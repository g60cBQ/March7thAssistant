from typing import Optional
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from qfluentwidgets import ScrollArea, ExpandGroupSettingCard, MessageBox, BodyLabel, TransparentToolButton, FluentIcon, SwitchButton, StrongBodyLabel, LineEdit, TextEdit, ToolButton, CaptionLabel
from module.config import cfg
from module.notification import get_notify_rules, set_notify_rules, TEMPLATE_GROUPS
from module.notification.types import NotifyLevel


class NotifyRuleItem(QWidget):
    checked_changed = pyqtSignal(str, bool)  # (full_id, enabled)
    edit_requested = pyqtSignal(str)  # (full_id)

    def __init__(self, full_id: str, label: str, description: str, level: NotifyLevel, enabled: bool, parent=None):
        super().__init__(parent)

        self.full_id = full_id
        self.level = level

        # 布局
        self.horizontalContainer = QHBoxLayout(self)
        self.horizontalContainer.setContentsMargins(20, 8, 8, 8)
        self.horizontalContainer.setSpacing(16)

        # 通知级别标签
        self.levelLabel = StrongBodyLabel(self._get_level_text(), self)
        self.levelLabel.setFixedWidth(60)
        self._set_level_color()

        # 名称
        self.nameLabel = BodyLabel(label, self)
        self.descriptionLabel = BodyLabel(description, self)

        # 编辑按钮
        self.editButton = TransparentToolButton(FluentIcon.EDIT, self)
        self.editButton.setCursor(Qt.CursorShape.PointingHandCursor)

        # 开关
        self.switchButton = SwitchButton(self)
        self.switchButton.setOffText("")
        self.switchButton.setOnText("")
        self.switchButton.setChecked(enabled)

        self.horizontalContainer.addWidget(self.levelLabel)
        self.horizontalContainer.addWidget(self.nameLabel)
        self.horizontalContainer.addWidget(self.descriptionLabel)
        self.horizontalContainer.addStretch(1)
        self.horizontalContainer.addWidget(self.editButton)
        self.horizontalContainer.addWidget(self.switchButton)

        self.switchButton.checkedChanged.connect(self._onCheckedChanged)
        self.editButton.clicked.connect(self._onEditClicked)

    def _get_level_text(self) -> str:
        match self.level:
            case NotifyLevel.NORMAL:
                return "普通"
            case NotifyLevel.IMPORTANT:
                return "重要"
            case NotifyLevel.ERROR:
                return "错误"
            case _:
                return "未知"

    def _set_level_color(self):
        match self.level:
            case NotifyLevel.ERROR:
                self.levelLabel.setTextColor(QColor("#ff6b6b"), QColor("#ff6b6b"))
            case NotifyLevel.IMPORTANT:
                self.levelLabel.setTextColor(QColor("#ff9500"), QColor("#ff9500"))
            case _:
                self.levelLabel.setTextColor(QColor("#999999"), QColor("#999999"))

    def _onEditClicked(self):
        self.edit_requested.emit(self.full_id)

    def _onCheckedChanged(self, isChecked: bool):
        self.checked_changed.emit(self.full_id, isChecked)


class NotifyRuleEditorDialog(MessageBox):
    rule_update_requested = pyqtSignal(str, str, str)  # (full_id, title, template)

    def __init__(self, full_id: str, dialog_title: str = "", title: str = "", template: str = "", parent=None):
        super().__init__(dialog_title, "", parent)

        self.full_id = full_id

        try:
            self.textLayout.removeWidget(self.contentLabel)
            self.contentLabel.clear()
        except Exception:
            pass

        self.yesButton.setText("保存")
        self.cancelButton.setText("取消")

        self.buttonGroup.setMinimumWidth(500)

        # 通知标题
        self.titleLabel = StrongBodyLabel("自定义标题", self)
        self.textLayout.addWidget(self.titleLabel)

        self.editTitle = LineEdit(self)
        self.editTitle.setText(title)
        self.editTitle.setPlaceholderText("留空则使用默认标题")
        self.editTitle.setClearButtonEnabled(True)
        self.textLayout.addWidget(self.editTitle)

        # 通知模板
        self.textLayout.addSpacing(12)
        self.lblTemplate = StrongBodyLabel("自定义模板", self)
        self.textLayout.addWidget(self.lblTemplate)

        self.editTemplate = TextEdit(self)
        self.editTemplate.setText(template)
        self.editTemplate.setPlaceholderText("留空则使用默认模板\n支持使用 {variable} 占位符,在发送时会自动替换")
        self.editTemplate.setFixedHeight(120)
        self.textLayout.addWidget(self.editTemplate)

        # 说明
        self.textLayout.addSpacing(8)
        self.infoLayout = QHBoxLayout()
        self.infoLabel = CaptionLabel("提示：留空表示使用默认值", self)
        self.infoLabel.setTextColor(QColor("#999999"), QColor("#999999"))
        self.infoLayout.addWidget(self.infoLabel)

        self.infoLayout.addStretch(1)
        self.clearButton = ToolButton(FluentIcon.DELETE, self)
        self.clearButton.setToolTip("清空输入")
        self.clearButton.clicked.connect(self._onClearAllClicked)
        self.infoLayout.addWidget(self.clearButton)

        self.textLayout.addLayout(self.infoLayout)

        self.cancelButton.clicked.disconnect()
        self.cancelButton.clicked.connect(self.reject)

        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(self._onSaveClicked)

    def _onClearAllClicked(self):
        self.editTitle.clear()
        self.editTemplate.clear()

    def _onSaveClicked(self):
        title = self.editTitle.text().strip()
        template = self.editTemplate.toPlainText().strip()
        self.rule_update_requested.emit(self.full_id, title, template)
        self.accept()


class NotifyPolicyManagerDialog(MessageBox):
    def __init__(self, parent=None):
        super().__init__("通知管理", "", parent)

        _rules = get_notify_rules()
        _default_title = cfg.notify_title

        self.default_title = _default_title if isinstance(_default_title, str) else ""
        self.notify_rules = _rules if isinstance(_rules, dict) else {}

        self.vm_rules = {}

        try:
            self.textLayout.removeWidget(self.contentLabel)
            self.contentLabel.clear()
        except Exception:
            pass

        self.yesButton.hide()
        self.cancelButton.setText("关闭")
        self.buttonGroup.setMinimumWidth(480)

        # 容器
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        self.contentContainer = QWidget()
        self.contentContainer.setObjectName("scrollWidget")
        self.contentLayout = QVBoxLayout(self.contentContainer)

        self.scrollArea.setWidget(self.contentContainer)
        self.scrollArea.setMinimumWidth(800)
        self.scrollArea.setMinimumHeight(400)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.textLayout.addWidget(self.scrollArea)

        self.createGroups()

        self.contentLayout.addStretch(1)

    def createGroups(self):
        for group in TEMPLATE_GROUPS:
            group_card = ExpandGroupSettingCard(FluentIcon.FOLDER, group.label, "", self)

            for item in group.get_templates():
                override_rule = self.notify_rules.get(item.full_id, {})
                enabled = override_rule.get("enabled", True)

                model = {
                    "path": item.full_id,
                    "label": item.label,
                    "description": item.description,
                    "title": override_rule.get("title", self.default_title),
                    "template": override_rule.get("template", item.content_template),
                    "_default_template": item.content_template,
                }

                self.vm_rules[item.full_id] = model

                item = NotifyRuleItem(full_id=item.full_id, label=item.label, description=item.description, level=item.level, enabled=enabled)
                item.checked_changed.connect(lambda ek, checked: self._onRuleChanged(ek, is_enabled=checked))
                item.edit_requested.connect(self._showEditDialog)

                group_card.addGroupWidget(item)

            self.contentLayout.addWidget(group_card)

    def _showEditDialog(self, full_id: str):
        model = self.vm_rules.get(full_id)

        if not model:
            return

        dialog = NotifyRuleEditorDialog(
            full_id=full_id,
            dialog_title=model["label"],
            title=model["title"],
            template=model["template"],
            parent=self,
        )

        dialog.rule_update_requested.connect(lambda full_id, title, template: self._onRuleChanged(full_id, title=title, template=template))

        dialog.exec()

    def _onRuleChanged(self, full_id: str, is_enabled: Optional[bool] = None, title: Optional[str] = None, template: Optional[str] = None):
        if full_id not in self.notify_rules:
            self.notify_rules[full_id] = {}

        # 启用/禁用
        if is_enabled is not None:
            if is_enabled:
                del self.notify_rules[full_id]["enabled"]
            else:
                self.notify_rules[full_id]["enabled"] = is_enabled

        # 标题
        if title is not None:
            if title:
                self.notify_rules[full_id]["title"] = title
            elif "title" in self.notify_rules[full_id]:
                del self.notify_rules[full_id]["title"]

        # 模板
        if template is not None:
            if template:
                self.notify_rules[full_id]["template"] = template
            elif "template" in self.notify_rules[full_id]:
                del self.notify_rules[full_id]["template"]

        # 按需清空整个条目
        if not self.notify_rules[full_id]:
            del self.notify_rules[full_id]

        # 同步更新 map
        if full_id in self.vm_rules:
            override_rule = self.notify_rules.get(full_id, {})
            self.vm_rules[full_id]["title"] = override_rule.get("title", self.default_title)
            self.vm_rules[full_id]["template"] = override_rule.get("template", self.vm_rules[full_id].get("_default_template", ""))

        # 更新配置
        set_notify_rules(rules=self.notify_rules)
