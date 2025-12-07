from tasks.power.power import Power
from .doubleactivity import DoubleActivity
from module.screen import screen
from module.automation import auto
from module.logger import log
from tasks.weekly.universe import Universe
import time


class PlanarFissure(DoubleActivity):
    def __init__(self, name, enabled):
        super().__init__(name, enabled, "饰品提取")

    def _get_immersifier_count(self):
        screen.change_to("guide3")
        instance_type_crop = (262.0 / 1920, 289.0 / 1080, 422.0 / 1920, 624.0 / 1080)

        auto.click_element(self.instance_type, "text", crop=instance_type_crop)
        # 等待界面完全停止
        time.sleep(1)

        # 需要判断是否有可用存档
        if auto.find_element("无可用存档", "text", crop=(688.0 / 1920, 289.0 / 1080, 972.0 / 1920, 369.0 / 1080), include=True):
            # 刷差分宇宙存档
            if Universe.start(nums=1, save=False, category="divergent"):
                # 验证存档
                screen.change_to("guide3")
                auto.click_element(self.instance_type, "text", crop=instance_type_crop)
                # 等待界面完全停止
                time.sleep(1)
                if auto.find_element("无可用存档", "text", crop=(688.0 / 1920, 289.0 / 1080, 972.0 / 1920, 369.0 / 1080), include=True):
                    log.error("暂无可用存档")
                    return False
            else:
                return False

        screen.change_to("guide3")

        immersifier_crop = (1623.0 / 1920, 40.0 / 1080, 162.0 / 1920, 52.0 / 1080)
        text = auto.get_single_line_text(crop=immersifier_crop, blacklist=["+", "米"], max_retries=3)
        if "/12" not in text:
            log.error("沉浸器数量识别失败")
            return False

        self.immersifier_count = int(text.split("/")[0])
        log.info(f"🟣沉浸器: {self.immersifier_count}/12")

        return True

    def _calculate_instance_run_plan(self, reward_cap):
        power = Power.get()

        if not self._get_immersifier_count():
            return []

        immersifier_count = self.immersifier_count
        power_based_runs = power // self.instance_power_cost
        total_runs = power_based_runs + immersifier_count
        total_challenges = min(reward_cap, total_runs)

        log.info(
            f"双倍活动: 体力={power}, 每次消耗={self.instance_power_cost}, "
            f"体力可支持挑战次数={power_based_runs}, 沉浸器={immersifier_count}, "
            f"总可挑战次数={total_runs}, 奖励上限={reward_cap}, "
            f"实际执行挑战次数={total_challenges}"
        )

        if total_challenges > 0:
            return [(40, total_challenges)]

        return []
