from dataclasses import dataclass
from enum import StrEnum
from typing import Dict


class NotifyLevel(StrEnum):
    """通知级别枚举类

    用于区分通知的重要程度。

    Attributes:
        NORMAL: 普通，一般信息提示
        IMPORTANT: 重要，可能需要注意的问题
        ERROR: 异常，必须得知的消息
    """

    NORMAL = "normal"
    IMPORTANT = "important"
    ERROR = "error"

    @property
    def priority(self) -> int:
        match self:
            case self.NORMAL:
                return 1
            case self.IMPORTANT:
                return 2
            case self.ERROR:
                return 3
            case _:
                return 0

    def __lt__(self, other: "NotifyLevel") -> bool:
        if not isinstance(other, NotifyLevel):
            return NotImplemented
        return self.priority < other.priority

    def __le__(self, other: "NotifyLevel") -> bool:
        if not isinstance(other, NotifyLevel):
            return NotImplemented
        return self.priority <= other.priority

    def __gt__(self, other: "NotifyLevel") -> bool:
        if not isinstance(other, NotifyLevel):
            return NotImplemented
        return self.priority > other.priority

    def __ge__(self, other: "NotifyLevel") -> bool:
        if not isinstance(other, NotifyLevel):
            return NotImplemented
        return self.priority >= other.priority


@dataclass
class NotifyTemplate:
    """通知模板数据类

    定义系统中通知消息的结构和元数据，用于作为发送通知时的规范。

    Attributes:
        group_id: 模板所属的分组ID，用于对通知进行归类。
        id: 模板在分组内的唯一标识符。
        content_template: 消息正文的模板字符串（支持参数化替换）。
        level: 通知级别，决定该类通知的重要程度。
        label: 可选的展示名称，用于在 UI 中友好地显示该通知类型。
        description: 可选的描述信息，说明该通知触发的场景或用途。

    Properties:
        full_id: 模板的完整路径ID，格式为 "group_id.template_id"，用于全局引用。
    """

    group_id: str
    id: str
    content_template: str
    level: NotifyLevel
    label: str = ""
    description: str = ""

    @property
    def full_id(self) -> str:
        """获取通知模板的完整路径ID"""
        return f"{self.group_id}.{self.id}"


class NotifyTemplateGroup:
    """通知模板分组辅助类

    用于简化通知模板的批量定义、收集和管理，无特定业务逻辑。
    """

    def __init__(self, id: str, label: str = ""):
        """
        初始化模板分组。

        :param id: 分组的唯一标识符。
        :param label: 可选的分组显示标签，默认使用 id。
        """
        self.id = id
        self.label = label or self.id
        self._templates: Dict[str, NotifyTemplate] = {}

    def add_template(self, template_id: str, content_template: str, level: NotifyLevel = NotifyLevel.NORMAL, label: str = "", description: str = "") -> NotifyTemplate:
        """
        在当前分组中定义一个新的通知模板。

        :param template_id: 模板在组内的唯一标识符。
        :param template: 通知消息的正文模板。
        :param level: 通知级别，默认为 NORMAL。
        :param label: 可选的显示标签，默认使用 template_id。
        :param description: 可选的模板描述。
        :return: 创建的 NotifyTemplate 实例。
        """
        item = NotifyTemplate(self.id, template_id, content_template, level, label or template_id, description)
        self._templates[template_id] = item
        return item

    def get_templates(self) -> list[NotifyTemplate]:
        """
        获取分组中定义的所有通知模板列表。

        :return: 包含所有 NotifyTemplate 实例的列表。
        """
        return list(self._templates.values())
