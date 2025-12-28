from module.automation import auto
from .rewardtemplate import RewardTemplate
import time
from tasks.base.base import Base
from module.notification import REWARD_NOTIFS


class Mail(RewardTemplate):
    def run(self):
        if auto.click_element("./assets/images/zh_CN/reward/mail/receive_all.png", "image", 0.8):
            time.sleep(2)
            Base.notify_with_screenshot(REWARD_NOTIFS.MAIL_CLAIMED)
            auto.click_element("./assets/images/zh_CN/base/click_close.png", "image", 0.8, max_retries=10)
