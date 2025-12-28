import io
from PIL import Image
from typing import Optional
from utils.logger.logger import Logger
from utils.singleton import SingletonMeta
from .notifier import Notifier
from .types import NotifyLevel, NotifyTemplate


class Notification(metaclass=SingletonMeta):
    """
    通知管理类，负责管理和发送不同类型的通知。
    """

    def __init__(self, logger: Logger, default_title: str, minimum_level: NotifyLevel, overrides: dict):
        """
        初始化通知管理类。

        :param logger: 用于记录日志的Logger对象。
        :param default_title: 默认的通知标题。
        :param minimum_level: 最小通知级别，低于此级别的通知将被过滤。
        :param overrides: 通知模板配置覆盖字典，用于覆盖程序中的固定模板配置。
        """
        self.logger = logger
        self.default_title = default_title

        self.minimum_level = minimum_level
        self.overrides = overrides

        self.notifiers = {}  # 存储不同类型的通知发送者实例

    def set_notifier(self, notifier_name: str, notifier: Notifier):
        """
        设置或更新一个通知发送者实例。

        :param notifier_name: 通知发送者的名称。
        :param notifier: 通知发送者的实例，应当实现Notifier接口。
        """
        self.notifiers[notifier_name] = notifier

    def send_template(self, template: NotifyTemplate, image: Optional[io.BytesIO | str | Image.Image] = None, **args):
        """
        使用预定义的模板发送通知。

        :param template: 指定的通知模板对象（NotifyTemplate 实例）。
        :param image: 可选的图片附件，支持 io.BytesIO | str | Image.Image。
        :param kwargs: 模板格式化参数，用于替换模板字符串中的 {key} 占位符。
        """
        override = self.overrides.get(template.full_id, {})

        content_template = override.get("template", template.content_template)
        title = override.get("title", self.default_title)
        enabled = override.get("enabled", True)

        content = content_template.format_map(args)

        if enabled:
            self.send(content, title=title, image=image, level=template.level)
        else:
            self._log_by_level(content, template.level)
            self.logger.debug(f"通知跳过：'{template.label}' (在配置中已禁用)")

    def send(self, content: str, title: Optional[str] = None, image: Optional[io.BytesIO | str | Image.Image] = None, level: Optional[NotifyLevel] = None):
        """
        发送通知。

        :param content: 通知的正文内容。
        :param title: 通知标题。若为 None，则使用全局默认标题。
        :param image: 可选的图片附件，支持 io.BytesIO | str | Image.Image。
        :param level: 通知级别。
            - 若提供 level: 则受系统最小通知级别配置过滤。
            - 若为 None: 则视为强制通知，无视级别过滤。
        """
        self._log_by_level(content, level)

        if level and self.minimum_level > level:
            self.logger.debug(f"通知跳过：低于配置级别 (当前: {level}, 配置: {self.minimum_level})")
            return

        processed_image = self._process_image(image)

        for notifier_name, notifier in self.notifiers.items():
            try:
                if processed_image and notifier.supports_image:
                    notifier.send(title or self.default_title, content, processed_image)
                else:
                    notifier.send(title or self.default_title, content)
                if self.logger:
                    self.logger.info(f"{notifier_name} 通知发送完成")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"{notifier_name} 通知发送失败: {e}")

    def _process_image(self, image: Optional[io.BytesIO | str | Image.Image], max_size: tuple = (1920, 1080), quality: int = 85) -> Optional[io.BytesIO]:
        """
        根据image的类型处理图片，并进行压缩优化，确保它是io.BytesIO对象。

        :param image: 可以是io.BytesIO对象、文件路径字符串或PIL.Image对象，可选。
        :param max_size: 图片最大尺寸(宽, 高)，默认1920x1080。
        :param quality: JPEG压缩质量，范围1-95，默认85。
        :return: io.BytesIO对象或None（如果image为None或处理失败）。
        """
        pil_image = None

        # 第一步：将所有类型转换为PIL.Image对象
        if isinstance(image, str):
            try:
                pil_image = Image.open(image)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"图片读取失败: {e}")
                return None
        elif isinstance(image, io.BytesIO):
            try:
                image.seek(0)
                pil_image = Image.open(image)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"图片解析失败: {e}")
                return None
        elif isinstance(image, Image.Image):
            pil_image = image
        else:
            return None

        # 第二步：压缩处理
        try:
            # 转换为RGB模式（JPEG不支持透明通道）
            if pil_image.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', pil_image.size, (255, 255, 255))
                if pil_image.mode == 'P':
                    pil_image = pil_image.convert('RGBA')
                background.paste(pil_image, mask=pil_image.split()[-1] if pil_image.mode in ('RGBA', 'LA') else None)
                pil_image = background
            elif pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            # 调整图片尺寸（如果超过最大尺寸）
            if pil_image.width > max_size[0] or pil_image.height > max_size[1]:
                pil_image.thumbnail(max_size, Image.Resampling.LANCZOS)
                if self.logger:
                    self.logger.debug(f"图片已调整大小至: {pil_image.size}")

            # 保存为压缩后的JPEG格式
            img_byte_arr = io.BytesIO()
            pil_image.save(img_byte_arr, format='JPEG', quality=quality, optimize=True)
            img_byte_arr.seek(0)

            # 记录压缩后的大小
            compressed_size = img_byte_arr.getbuffer().nbytes
            if self.logger:
                self.logger.debug(f"图片压缩完成，大小: {compressed_size / 1024:.2f} KB")

            return img_byte_arr
        except Exception as e:
            if self.logger:
                self.logger.error(f"图片压缩失败: {e}")
            return None

    def _log_by_level(self, content: str, level: Optional[NotifyLevel]):
        level = level or NotifyLevel.NORMAL

        if level == NotifyLevel.ERROR:
            log = self.logger.error
        else:
            log = self.logger.info

        for item in content.split("\n"):
            log(item)
