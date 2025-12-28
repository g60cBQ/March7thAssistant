import io
from PIL import Image
from typing import Optional
from module.automation import auto
from module.notification import notif, NotifyLevel, NotifyTemplate


class Base:
    @staticmethod
    def notify(template: NotifyTemplate, screenshot: Optional[io.BytesIO | str | Image.Image] = None, **args):
        """
        使用预定义的模板发送通知。

        :param template: 指定的通知模板对象（NotifyTemplate 实例）。
        :param screenshot: 可选的图片附件，支持 io.BytesIO | str | Image.Image。
        :param args: 模板格式化参数，用于替换模板字符串中的 {key} 占位符。
        """
        notif.send_template(template, screenshot, **args)

    @staticmethod
    def notify_with_screenshot(template: NotifyTemplate, screenshot: Optional[io.BytesIO | str | Image.Image] = None, **args):
        """
        自动截取当前画面作为图片附件并使用预定义的模板发送通知。

        :param template: 指定的通知模板对象（NotifyTemplate 实例）。
        :param screenshot: 可选的图片附件，支持 io.BytesIO | str | Image.Image。若为 None，则自动截取当前屏幕。
        :param args: 模板格式化参数，用于替换模板字符串中的 {key} 占位符。
        """
        if screenshot is None:
            screenshot, _, _ = auto.take_screenshot()
        notif.send_template(template, screenshot, **args)

    @staticmethod
    def custom_notify(content: str, title: Optional[str] = None, image: Optional[io.BytesIO | str | Image.Image] = None, level: Optional[NotifyLevel] = None):
        """
        发送通知。

        :param content: 通知的正文内容。
        :param title: 通知标题。若为 None，则使用全局默认标题。
        :param image: 可选的图片附件，支持 io.BytesIO | str | Image.Image。
        :param level: 通知级别。
            - 若提供 level: 则受系统最小通知级别配置过滤。
            - 若为 None: 则视为强制通知，无视级别过滤。
        """
        notif.send(content, title, image, level)

    @staticmethod
    def custom_notify_with_screenshot(content: str, title: Optional[str] = None, image: Optional[io.BytesIO | str | Image.Image] = None, level: Optional[NotifyLevel] = None):
        """
        自动截取当前画面作为图片附件并发送自定义通知。

        :param content: 通知的正文内容。
        :param title: 通知标题。若为 None，则使用全局默认标题。
        :param image: 可选的图片附件，支持 io.BytesIO | str | Image.Image。若为 None，则自动截取当前屏幕。
        :param level: 通知级别。
            - 若提供 level: 则受系统最小通知级别配置过滤。
            - 若为 None: 则视为强制通知，无视级别过滤。
        """
        if image is None:
            image, _, _ = auto.take_screenshot()
        notif.send(content, title, image, level)
