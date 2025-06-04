"""扩展元素操作关键字

提供更多元素操作功能，如选择、上传、等待、获取属性等。
"""

import logging
import allure

from pytest_dsl.core.keyword_manager import keyword_manager
from ..core.browser_manager import browser_manager
from ..core.element_locator import ElementLocator

logger = logging.getLogger(__name__)


def _get_current_locator() -> ElementLocator:
    """获取当前页面的元素定位器"""
    page = browser_manager.get_current_page()
    return ElementLocator(page)


@keyword_manager.register('选择选项', [
    {'name': '定位器', 'mapping': 'selector', 'description': '下拉框元素定位器'},
    {'name': '值', 'mapping': 'value', 'description': '要选择的选项值'},
    {'name': '标签', 'mapping': 'label', 'description': '要选择的选项标签文本'},
    {'name': '索引', 'mapping': 'index', 'description': '要选择的选项索引（从0开始）'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
])
def select_option(**kwargs):
    """选择下拉框选项

    Args:
        selector: 下拉框定位器
        value: 选项值
        label: 选项标签
        index: 选项索引
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    value = kwargs.get('value')
    label = kwargs.get('label')
    index = kwargs.get('index')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    if not any([value, label, index is not None]):
        raise ValueError("必须指定值、标签或索引中的一个")

    with allure.step(f"选择选项: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            # 使用Playwright的智能等待机制
            timeout_ms = int(timeout * 1000) if timeout else 30000
            if value is not None:
                element.select_option(value=value, timeout=timeout_ms)
            elif label is not None:
                element.select_option(label=label, timeout=timeout_ms)
            elif index is not None:
                element.select_option(
                    index=int(index), timeout=timeout_ms
                )

            selection_info = (
                f"值: {value}" if value 
                else f"标签: {label}" if label 
                else f"索引: {index}"
            )

            allure.attach(
                f"定位器: {selector}\n"
                f"选择: {selection_info}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="选项选择信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"选项选择成功: {selector} -> {selection_info}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "value": value,
                    "label": label,
                    "index": index,
                    "operation": "select_option"
                }
            }

        except Exception as e:
            logger.error(f"选项选择失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="选项选择失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('上传文件', [
    {'name': '定位器', 'mapping': 'selector', 'description': '文件输入框元素定位器'},
    {'name': '文件路径', 'mapping': 'file_path', 'description': '要上传的文件路径'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
])
def upload_file(**kwargs):
    """上传文件

    Args:
        selector: 文件输入框定位器
        file_path: 文件路径
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    file_path = kwargs.get('file_path')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")
    if not file_path:
        raise ValueError("文件路径参数不能为空")

    with allure.step(f"上传文件: {selector} -> {file_path}"):
        try:
            import os
            if not os.path.exists(file_path):
                raise ValueError(f"文件不存在: {file_path}")

            locator = _get_current_locator()
            element = locator.locate(selector)

            # 使用Playwright的智能等待机制
            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.set_input_files(
                file_path, timeout=timeout_ms
            )

            allure.attach(
                f"定位器: {selector}\n"
                f"文件路径: {file_path}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="文件上传信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"文件上传成功: {selector} -> {file_path}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": file_path,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "file_path": file_path,
                    "operation": "upload_file"
                }
            }

        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="文件上传失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('等待元素出现', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '状态', 'mapping': 'state', 'description': '等待状态：visible, hidden, attached, detached'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
])
def wait_for_element(**kwargs):
    """等待元素出现或达到指定状态

    Args:
        selector: 元素定位器
        state: 等待状态
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    state = kwargs.get('state', 'visible')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"等待元素{state}: {selector}"):
        try:
            locator = _get_current_locator()
            result = locator.wait_for_element(selector, state, timeout)

            allure.attach(
                f"定位器: {selector}\n"
                f"等待状态: {state}\n"
                f"超时时间: {timeout or '默认'}秒\n"
                f"等待结果: {'成功' if result else '超时'}",
                name="元素等待信息",
                attachment_type=allure.attachment_type.TEXT
            )

            if result:
                logger.info(f"元素等待成功: {selector} ({state})")
            else:
                logger.warning(f"元素等待超时: {selector} ({state})")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": result,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "state": state,
                    "timeout": timeout,
                    "operation": "wait_for_element"
                }
            }

        except Exception as e:
            logger.error(f"元素等待失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="元素等待失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('等待文本出现', [
    {'name': '文本', 'mapping': 'text', 'description': '要等待的文本内容'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
])
def wait_for_text(**kwargs):
    """等待文本在页面中出现

    Args:
        text: 要等待的文本
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    text = kwargs.get('text')
    timeout = kwargs.get('timeout')

    if not text:
        raise ValueError("文本参数不能为空")

    with allure.step(f"等待文本出现: {text}"):
        try:
            locator = _get_current_locator()
            result = locator.wait_for_text(text, timeout)

            allure.attach(
                f"等待文本: {text}\n"
                f"超时时间: {timeout or '默认'}秒\n"
                f"等待结果: {'成功' if result else '超时'}",
                name="文本等待信息",
                attachment_type=allure.attachment_type.TEXT
            )

            if result:
                logger.info(f"文本等待成功: {text}")
            else:
                logger.warning(f"文本等待超时: {text}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": result,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "text": text,
                    "timeout": timeout,
                    "operation": "wait_for_text"
                }
            }

        except Exception as e:
            logger.error(f"文本等待失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="文本等待失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('获取元素文本', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '变量名', 'mapping': 'variable', 'description': '保存文本内容的变量名'},
])
def get_element_text(**kwargs):
    """获取元素文本内容

    Args:
        selector: 元素定位器
        variable: 变量名

    Returns:
        dict: 包含文本内容的字典
    """
    selector = kwargs.get('selector')
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"获取元素文本: {selector}"):
        try:
            locator = _get_current_locator()
            text = locator.get_element_text(selector)

            # 保存到变量
            captures = {}
            if variable and context:
                context.set(variable, text)
                captures[variable] = text

            allure.attach(
                f"定位器: {selector}\n"
                f"文本内容: {text}\n"
                f"保存变量: {variable or '无'}",
                name="元素文本信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"获取元素文本成功: {selector} -> {text}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": text,
                "captures": captures,
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "text": text,
                    "variable": variable,
                    "operation": "get_element_text"
                }
            }

        except Exception as e:
            logger.error(f"获取元素文本失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="获取元素文本失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
