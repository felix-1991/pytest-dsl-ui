"""截图和录制关键字

提供页面截图、元素截图、视频录制等功能。
"""

import logging
import allure

from pytest_dsl.core.keyword_manager import keyword_manager
from ..core.browser_manager import browser_manager
from ..core.page_context import PageContext

logger = logging.getLogger(__name__)


@keyword_manager.register('截图', [
    {'name': '文件名', 'mapping': 'filename', 
     'description': '截图文件名，如果不指定则自动生成'},
    {'name': '元素定位器', 'mapping': 'element_selector', 
     'description': '如果指定则只截取该元素'},
    {'name': '全页面', 'mapping': 'full_page', 
     'description': '是否截取整个页面（包括滚动区域）', 'default': False},
    {'name': '变量名', 'mapping': 'variable', 
     'description': '保存截图路径的变量名'},
], category='UI/截图')
def take_screenshot(**kwargs):
    """截图

    Args:
        filename: 文件名
        element_selector: 元素定位器
        full_page: 是否全页面截图
        variable: 变量名

    Returns:
        dict: 包含截图路径的字典
    """
    filename = kwargs.get('filename')
    element_selector = kwargs.get('element_selector')
    full_page = kwargs.get('full_page', False)
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    with allure.step("页面截图"):
        try:
            page = browser_manager.get_current_page()
            page_context = PageContext(page)

            # 执行截图
            screenshot_path = page_context.screenshot(
                path=filename,
                element_selector=element_selector,
                full_page=full_page
            )

            # 保存到变量
            captures = {}
            if variable and context:
                context.set(variable, screenshot_path)
                captures[variable] = screenshot_path

            # 添加到Allure报告
            with open(screenshot_path, 'rb') as f:
                allure.attach(
                    f.read(),
                    name="页面截图",
                    attachment_type=allure.attachment_type.PNG
                )

            allure.attach(
                f"截图文件: {screenshot_path}\n"
                f"元素定位器: {element_selector or '整个页面'}\n"
                f"全页面: {full_page}\n"
                f"保存变量: {variable or '无'}",
                name="截图信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"截图成功: {screenshot_path}")

            # 保存到变量
            if variable and context:
                context.set(variable, screenshot_path)

            # 直接返回截图文件路径
            return screenshot_path

        except Exception as e:
            logger.error(f"截图失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="截图失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('开始录制', [
    {'name': '文件名', 'mapping': 'filename', 'description': '录制文件名，如果不指定则自动生成'},
    {'name': '变量名', 'mapping': 'variable', 'description': '保存录制路径的变量名'},
], category='UI/视频录制')
def start_recording(**kwargs):
    """开始录制视频

    Args:
        filename: 文件名
        variable: 变量名

    Returns:
        dict: 包含录制路径的字典
    """
    filename = kwargs.get('filename')
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    with allure.step("开始录制"):
        try:
            page = browser_manager.get_current_page()
            page_context = PageContext(page)

            # 开始录制
            recording_path = page_context.start_recording(filename)

            # 保存到变量
            captures = {}
            if variable and context:
                context.set(variable, recording_path)
                captures[variable] = recording_path

            allure.attach(
                f"录制文件: {recording_path}\n"
                f"保存变量: {variable or '无'}",
                name="录制开始信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"录制开始: {recording_path}")

            # 保存到变量
            if variable and context:
                context.set(variable, recording_path)

            # 直接返回录制文件路径
            return recording_path

        except Exception as e:
            logger.error(f"开始录制失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="开始录制失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('停止录制', [
    {'name': '变量名', 'mapping': 'variable', 'description': '保存录制路径的变量名'},
], category='UI/视频录制')
def stop_recording(**kwargs):
    """停止录制视频

    Args:
        variable: 变量名

    Returns:
        dict: 包含录制路径的字典
    """
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    with allure.step("停止录制"):
        try:
            page = browser_manager.get_current_page()
            page_context = PageContext(page)

            # 停止录制
            recording_path = page_context.stop_recording()

            # 保存到变量
            captures = {}
            if variable and context and recording_path:
                context.set(variable, recording_path)
                captures[variable] = recording_path

            if recording_path:
                # 添加到Allure报告
                try:
                    with open(recording_path, 'rb') as f:
                        allure.attach(
                            f.read(),
                            name="录制视频",
                            attachment_type=allure.attachment_type.WEBM
                        )
                except Exception as e:
                    logger.warning(f"无法添加录制视频到报告: {str(e)}")

                allure.attach(
                    f"录制文件: {recording_path}\n"
                    f"保存变量: {variable or '无'}",
                    name="录制停止信息",
                    attachment_type=allure.attachment_type.TEXT
                )

                logger.info(f"录制停止: {recording_path}")
            else:
                logger.warning("没有正在进行的录制")

            # 保存到变量
            if variable and context:
                context.set(variable, recording_path)

            # 直接返回录制文件路径
            return recording_path

        except Exception as e:
            logger.error(f"停止录制失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="停止录制失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('设置视口大小', [
    {'name': '宽度', 'mapping': 'width', 'description': '视口宽度'},
    {'name': '高度', 'mapping': 'height', 'description': '视口高度'},
], category='UI/浏览器')
def set_viewport_size(**kwargs):
    """设置视口大小

    Args:
        width: 视口宽度
        height: 视口高度

    Returns:
        dict: 操作结果
    """
    width = kwargs.get('width')
    height = kwargs.get('height')

    if not width or not height:
        raise ValueError("宽度和高度参数不能为空")

    with allure.step(f"设置视口大小: {width}x{height}"):
        try:
            page = browser_manager.get_current_page()
            page_context = PageContext(page)

            page_context.set_viewport_size(int(width), int(height))

            allure.attach(
                f"视口宽度: {width}\n"
                f"视口高度: {height}",
                name="视口大小设置",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"视口大小设置成功: {width}x{height}")

            # 直接返回设置的视口大小
            return {"width": int(width), "height": int(height)}

        except Exception as e:
            logger.error(f"设置视口大小失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="设置视口大小失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('获取视口大小', [
    {'name': '变量名', 'mapping': 'variable', 'description': '保存视口大小的变量名'},
], category='UI/浏览器')
def get_viewport_size(**kwargs):
    """获取视口大小

    Args:
        variable: 变量名

    Returns:
        dict: 包含视口大小的字典
    """
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    with allure.step("获取视口大小"):
        try:
            page = browser_manager.get_current_page()
            page_context = PageContext(page)

            viewport_size = page_context.get_viewport_size()

            # 保存到变量
            captures = {}
            if variable and context:
                context.set(variable, viewport_size)
                captures[variable] = viewport_size

            allure.attach(
                f"视口宽度: {viewport_size['width']}\n"
                f"视口高度: {viewport_size['height']}\n"
                f"保存变量: {variable or '无'}",
                name="视口大小信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"获取视口大小成功: {viewport_size}")

            # 保存到变量
            if variable and context:
                context.set(variable, viewport_size)

            # 直接返回视口大小
            return viewport_size

        except Exception as e:
            logger.error(f"获取视口大小失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="获取视口大小失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('执行JavaScript', [
    {'name': '脚本', 'mapping': 'script', 'description': 'JavaScript代码'},
    {'name': '变量名', 'mapping': 'variable', 'description': '保存执行结果的变量名'},
], category='UI/执行JavaScript')
def execute_javascript(**kwargs):
    """执行JavaScript代码

    Args:
        script: JavaScript代码
        variable: 变量名

    Returns:
        dict: 包含执行结果的字典
    """
    script = kwargs.get('script')
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    if not script:
        raise ValueError("脚本参数不能为空")

    with allure.step("执行JavaScript"):
        try:
            page = browser_manager.get_current_page()
            page_context = PageContext(page)

            result = page_context.evaluate(script)

            # 保存到变量
            if variable and context:
                context.set(variable, result)

            allure.attach(
                f"JavaScript代码:\n{script}\n\n"
                f"执行结果: {result}\n"
                f"保存变量: {variable or '无'}",
                name="JavaScript执行信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"JavaScript执行成功: {result}")

            # 直接返回执行结果
            return result

        except Exception as e:
            logger.error(f"JavaScript执行失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="JavaScript执行失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
