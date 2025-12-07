from module.automation import auto
from module.logger import log
from module.config import cfg
from tasks.daily.buildtarget import BuildTarget
from tasks.power.instance import Instance
from tasks.power.power import Power
from .activitytemplate import ActivityTemplate


class DoubleActivity(ActivityTemplate):
    instances_power = {
        "拟造花萼（金）": 10,
        "拟造花萼（赤）": 10,
        "凝滞虚影": 30,
        "侵蚀隧洞": 40,
        "历战余响": 30,
        "饰品提取": 40,
    }

    challenges_count_max = {
        "拟造花萼（金）": 24,
        "拟造花萼（赤）": 24,
        "凝滞虚影": 8,
        "侵蚀隧洞": 6,
        "历战余响": 3,
    }

    def __init__(self, name, enabled, instance_type):
        super().__init__(name, enabled)
        self.instance_type = instance_type
        self.instance_name = cfg.instance_names[self.instance_type]
        self.expect_challenge_count = cfg.instance_names_challenge_count[self.instance_type]
        self.instance_power_cost = self.instances_power[instance_type]

    def _get_reward_count(self):
        auto.find_element("奖励剩余次数", "text", max_retries=10, crop=(960.0 / 1920, 125.0 / 1080, 940.0 / 1920, 846.0 / 1080), include=True)
        for box in auto.ocr_result:
            text = box[1][0]
            if "/" in text:
                if text.split("/")[0].isdigit():
                    return int(text.split("/")[0])
        return 0

    def _calculate_instance_run_plan(self, reward_cap) -> list[(int, int)]:
        plan = []
        power = Power.get()

        power_based_total_challenges = power // self.instance_power_cost
        total_challenges = min(reward_cap, power_based_total_challenges)

        if total_challenges > 0:
            effective_batch_size = min(self.expect_challenge_count, self.challenges_count_max[self.instance_type])
            full_runs = total_challenges // effective_batch_size
            partial_run = total_challenges % effective_batch_size

            if full_runs > 0:
                plan.append((effective_batch_size * self.instance_power_cost, full_runs))
            if partial_run > 0:
                plan.append((partial_run * self.instance_power_cost, 1))

            log.info(
                f"双倍活动: 体力={power}, 每次消耗={self.instance_power_cost}, "
                f"体力可支持挑战次数={power_based_total_challenges}, 奖励上限={reward_cap}, "
                f"实际执行挑战次数={total_challenges}, 期望挑战次数={effective_batch_size}, "
                f"完整批次={full_runs}, 收尾批次挑战次数={partial_run}"
            )

        return plan

    def _run_instances(self, reward_cap):
        if plan := self._calculate_instance_run_plan(reward_cap):
            if not cfg.activity_ignore_buildtarget and (build_target_instance := BuildTarget.get_instance(include=[self.instance_type])):
                self.instance_name = build_target_instance[1]

            total_challenges = sum(power_need // self.instance_power_cost * runs for power_need, runs in plan)
            log.info(f"双倍活动-开始执行 {self.instance_type} - {self.instance_name}，总计{total_challenges}个挑战，分为{len(plan)}轮")

            for power_need, runs in plan:
                result = Instance.run(self.instance_type, self.instance_name, power_need, runs)
                if result == "Failed":
                    return False
        else:
            log.info(f"双倍活动-跳过 {self.instance_type} - {self.instance_name}，奖励次数或体力耗尽")

        return True

    def run(self):
        reward_count = self._get_reward_count()
        if reward_count == 0:
            return True

        log.info(f"{self.name}剩余次数：{reward_count}")
        return self._run_instances(reward_count)
