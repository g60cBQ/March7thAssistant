from .types import NotifyLevel, NotifyTemplateGroup

# 通知模板定义


class SystemNotifyGroup(NotifyTemplateGroup):
    def __init__(self):
        super().__init__("system", "系统")
        self.NEW_VERSION = self.add_template("new_version", "发现新版本 {version}", NotifyLevel.IMPORTANT, "发现新版本")
        self.CONTINUE_TIME = self.add_template("continue_time", "将在{time}继续运行", NotifyLevel.IMPORTANT, "下次运行时间")
        self.FULL_POWER_TIME = self.add_template("full_power_time", "开拓力剩余{power}/300\n预计{time}回满", NotifyLevel.IMPORTANT, "体力回满预计时间")
        self.ERROR_OCCURRED = self.add_template("error_occurred", "发生错误 {error}", NotifyLevel.ERROR, "发生致命错误")


class RewardNotifyGroup(NotifyTemplateGroup):
    def __init__(self):
        super().__init__("reward", "奖励")
        self.QUEST_COMPLETED = self.add_template("quest_completed", "每日实训已完成", NotifyLevel.NORMAL, "每日实训完成")
        self.QUEST_INCOMPLETE = self.add_template("quest_incomplete", "每日实训未完成", NotifyLevel.IMPORTANT, "每日实训未完成")
        self.REDEMPTION_SUCCESS = self.add_template("redemption_success", "成功使用了{count}个兑换码: {codes}", NotifyLevel.NORMAL, "兑换码使用成功")
        self.MAIL_CLAIMED = self.add_template("mail_claimed", "邮件奖励已领取", NotifyLevel.NORMAL, "已领取邮件奖励")


class BuildTargetNotifyGroup(NotifyTemplateGroup):
    def __init__(self):
        super().__init__("daily", "培养目标")
        self.LIST = self.add_template("list", "培养目标{name}的待刷副本:\n{instances}", NotifyLevel.NORMAL, "待刷副本列表")
        self.RETURN_WITH_ERROR = self.add_template("return_with_error", "获取培养目标副本时出错，已提前返回当前已获取列表。\n详细情况请检查日志。", NotifyLevel.IMPORTANT, "获取培养目标时出错")
        self.NO_TARGET = self.add_template("no_target", "未能获取到任何培养目标副本信息，回退至默认的设置", NotifyLevel.IMPORTANT, "未能获取到任何待刷副本信息")


class FhoeNotifyGroup(NotifyTemplateGroup):
    def __init__(self):
        super().__init__("fhoe", "锄大地")
        self.COMPLETED = self.add_template("completed", "锄大地已完成", NotifyLevel.NORMAL, "锄大地已完成")
        self.INCOMPLETE = self.add_template("incomplete", "锄大地未完成", NotifyLevel.IMPORTANT, "锄大地未完成")


class PowerNotifyGroup(NotifyTemplateGroup):
    def __init__(self):
        super().__init__("power", "体力刷本")
        self.INSTANCE_INCOMPLETE = self.add_template("instance_incomplete", "清体力未完成 {error}", NotifyLevel.ERROR, "体力刷本未完成")


class UniverseNotifyGroup(NotifyTemplateGroup):
    def __init__(self):
        super().__init__("universe", "模拟宇宙")
        self.COMPLETED = self.add_template("completed", "模拟宇宙已完成", NotifyLevel.NORMAL, "模拟宇宙已完成")
        self.REWARD_CLAIMED = self.add_template("reward_claimed", "模拟宇宙奖励已领取", NotifyLevel.NORMAL, "模拟宇宙奖励领取成功")
        self.NOT_COMPLETED = self.add_template("not_completed", "模拟宇宙未完成", NotifyLevel.IMPORTANT, "模拟宇宙未完成")


class ChallengeNotifyGroup(NotifyTemplateGroup):
    def __init__(self):
        super().__init__("challenge", "混沌回忆/虚无/虚构叙事")
        self.LEVEL_CLEARED = self.add_template("level_cleared", "{name}已通关{level}层", NotifyLevel.NORMAL, "逐层通关播报")
        self.LEVEL_CLEARED_WITH_ISSUE = self.add_template("level_cleared_with_issue", "{name}已通关{level}层\n领取星琼失败", NotifyLevel.IMPORTANT, "通关异常")


SYSTEM_NOTIFS = SystemNotifyGroup()
REWARD_NOTIFS = RewardNotifyGroup()
POWER_NOTIFS = PowerNotifyGroup()
BUILD_TARGET_NOTIFS = BuildTargetNotifyGroup()
UNIVERSE_NOTIFS = UniverseNotifyGroup()
CHALLENGE_NOTIFS = ChallengeNotifyGroup()
FHOE_NOTIFS = FhoeNotifyGroup()

TEMPLATE_GROUPS: list[NotifyTemplateGroup] = [
    SYSTEM_NOTIFS,
    REWARD_NOTIFS,
    POWER_NOTIFS,
    BUILD_TARGET_NOTIFS,
    UNIVERSE_NOTIFS,
    CHALLENGE_NOTIFS,
    FHOE_NOTIFS,
]
