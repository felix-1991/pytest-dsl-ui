"""验证码识别关键字

提供文字验证码识别功能。
基于ddddocr库实现验证码识别。
"""

import os
import logging
import allure
from io import BytesIO
import base64

try:
    import ddddocr
except ImportError as e:
    raise ImportError(f"验证码识别功能需要安装依赖: {e}")

from pytest_dsl.core.keyword_manager import keyword_manager
from ..core.browser_manager import browser_manager
from ..core.page_context import PageContext

logger = logging.getLogger(__name__)


class CaptchaRecognizer:
    """验证码识别器"""

    def __init__(self):
        self._text_ocr = None

    @property
    def text_ocr(self):
        """文字验证码识别器"""
        if self._text_ocr is None:
            self._text_ocr = ddddocr.DdddOcr(show_ad=False)
        return self._text_ocr


# 全局验证码识别器实例
_captcha_recognizer = CaptchaRecognizer()


@keyword_manager.register('识别文字验证码', [
    {'name': '图片源', 'mapping': 'image_source',
     'description': '图片来源：文件路径、元素定位器、base64数据或变量名'},
    {'name': '源类型', 'mapping': 'source_type',
     'description': '源类型：file/element/base64/variable，默认auto自动判断'},
    {'name': '变量名', 'mapping': 'variable',
     'description': '保存识别结果的变量名'},
    {'name': '预处理', 'mapping': 'preprocess',
     'description': '是否进行图片预处理：去噪、二值化等'},
], category='UI/验证码')
def recognize_text_captcha(**kwargs):
    """识别文字验证码

    Args:
        image_source: 图片源
        source_type: 源类型 (file/element/base64/variable/auto)
        variable: 变量名
        preprocess: 是否预处理

    Returns:
        dict: 包含识别结果的字典
    """
    image_source = kwargs.get('image_source')
    source_type = kwargs.get('source_type', 'auto')
    variable = kwargs.get('variable')
    preprocess = kwargs.get('preprocess', False)
    context = kwargs.get('context')

    if not image_source:
        raise ValueError("图片源不能为空")

    with allure.step("识别文字验证码"):
        try:
            # 获取图片数据
            image_data = _get_image_data(image_source, source_type, context)

            # 预处理图片
            if preprocess:
                image_data = _preprocess_image(image_data)

            # 识别验证码
            result = _captcha_recognizer.text_ocr.classification(image_data)

            # 保存到变量
            if variable and context:
                context.set(variable, result)

            # 记录日志和报告
            allure.attach(
                image_data,
                name="验证码图片",
                attachment_type=allure.attachment_type.PNG
            )

            allure.attach(
                f"图片源: {image_source}\n"
                f"源类型: {source_type}\n"
                f"识别结果: {result}\n"
                f"预处理: {preprocess}\n"
                f"保存变量: {variable or '无'}",
                name="验证码识别信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"文字验证码识别成功: {result}")

            # 直接返回识别出的文本字符串
            return result

        except Exception as e:
            logger.error(f"文字验证码识别失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}\n"
                f"图片源: {image_source}",
                name="验证码识别失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


def _get_image_data(image_source: str, source_type: str, context) -> bytes:
    """获取图片数据

    Args:
        image_source: 图片源
        source_type: 源类型
        context: 上下文

    Returns:
        bytes: 图片数据
    """
    if source_type == 'auto':
        # 自动判断类型
        if os.path.isfile(image_source):
            source_type = 'file'
        elif image_source.startswith('data:image/'):
            source_type = 'base64'
        elif context and context.get(image_source) is not None:
            source_type = 'variable'
        else:
            source_type = 'element'

    if source_type == 'file':
        # 文件路径
        with open(image_source, 'rb') as f:
            return f.read()

    elif source_type == 'element':
        # 元素截图
        page = browser_manager.get_current_page()
        page_context = PageContext(page)
        screenshot_path = page_context.screenshot(
            element_selector=image_source)
        with open(screenshot_path, 'rb') as f:
            return f.read()

    elif source_type == 'base64':
        # base64数据
        if image_source.startswith('data:image/'):
            # 去掉data:image/png;base64,前缀
            image_source = image_source.split(',', 1)[1]
        return base64.b64decode(image_source)

    elif source_type == 'variable':
        # 变量
        if not context:
            raise ValueError("使用变量类型需要提供context")
        var_value = context.get(image_source)
        if var_value is None:
            raise ValueError(f"变量'{image_source}'不存在")
        if isinstance(var_value, str):
            if os.path.isfile(var_value):
                with open(var_value, 'rb') as f:
                    return f.read()
            else:
                return base64.b64decode(var_value)
        elif isinstance(var_value, bytes):
            return var_value
        else:
            raise ValueError(f"变量'{image_source}'的值类型不支持")

    else:
        raise ValueError(f"不支持的源类型: {source_type}")


def _preprocess_image(image_data: bytes) -> bytes:
    """预处理图片

    进行去噪、二值化等处理以提高识别率

    Args:
        image_data: 原始图片数据

    Returns:
        bytes: 处理后的图片数据
    """
    try:
        from PIL import Image, ImageEnhance, ImageFilter

        # 打开图片
        image = Image.open(BytesIO(image_data))

        # 转换为RGB模式
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # 提高对比度
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)

        # 提高锐度
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)

        # 去噪
        image = image.filter(ImageFilter.MedianFilter(size=3))

        # 转换为灰度图
        image = image.convert('L')

        # 二值化
        threshold = 128
        image = image.point(lambda x: 255 if x > threshold else 0, mode='1')

        # 保存处理后的图片
        output = BytesIO()
        image.save(output, format='PNG')
        return output.getvalue()

    except Exception as e:
        logger.warning(f"图片预处理失败，使用原图: {str(e)}")
        return image_data
