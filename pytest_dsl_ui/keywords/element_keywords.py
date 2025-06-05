"""元素操作关键字

提供元素点击、输入、选择等交互操作关键字。
充分利用Playwright的智能等待机制。
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


@keyword_manager.register('点击元素', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 30},
    {'name': '强制点击', 'mapping': 'force', 
     'description': '是否强制点击（忽略元素状态检查）', 'default': False},
    {'name': '索引', 'mapping': 'index', 
     'description': '元素索引（当有多个匹配元素时）'},
    {'name': '可见性', 'mapping': 'visible_only', 
     'description': '是否只点击可见元素', 'default': False},
])
def click_element(**kwargs):
    """点击元素

    Args:
        selector: 元素定位器
        timeout: 超时时间
        force: 是否强制点击
        index: 元素索引（当有多个匹配元素时）
        visible_only: 是否只点击可见元素

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout')
    force = kwargs.get('force', False)
    index = kwargs.get('index')
    visible_only = kwargs.get('visible_only', False)

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"点击元素: {selector}"):
        try:
            locator = _get_current_locator()

            # 根据参数选择合适的定位方式
            if visible_only:
                element = locator.locate_by_visible(selector)
            else:
                element = locator.locate(selector)

            # 如果指定了索引，使用nth定位
            if index is not None:
                element = element.nth(index)

            # 使用Playwright的智能等待机制
            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.click(force=force, timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"强制点击: {force}\n"
                f"索引: {index if index is not None else '无'}\n"
                f"仅可见元素: {visible_only}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="元素点击信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(
                f"元素点击成功: {selector} "
                f"(索引: {index}, 可见性: {visible_only})"
            )

            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "index": index,
                    "visible_only": visible_only,
                    "operation": "click_element"
                }
            }

        except Exception as e:
            error_msg = f"元素点击失败: {str(e)}"
            if "timeout" in str(e).lower():
                error_msg += (f"\n可能原因: 1) 元素不存在或不可见 "
                             f"2) 页面加载缓慢 3) 定位器 '{selector}' 不正确")
            elif "detached" in str(e).lower():
                error_msg += "\n可能原因: 页面结构发生变化，元素已被移除"
            
            logger.error(error_msg)
            allure.attach(
                f"错误信息: {error_msg}",
                name="元素点击失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise Exception(error_msg)


@keyword_manager.register('双击元素', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 30},
])
def double_click_element(**kwargs):
    """双击元素

    Args:
        selector: 元素定位器
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"双击元素: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.dblclick(timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="元素双击信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素双击成功: {selector}")

            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "operation": "double_click_element"
                }
            }

        except Exception as e:
            logger.error(f"元素双击失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="元素双击失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('右键点击元素', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 30},
])
def right_click_element(**kwargs):
    """右键点击元素

    Args:
        selector: 元素定位器
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"右键点击元素: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.click(button="right", timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="元素右键点击信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素右键点击成功: {selector}")

            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "operation": "right_click_element"
                }
            }

        except Exception as e:
            logger.error(f"元素右键点击失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="元素右键点击失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('输入文本', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '文本', 'mapping': 'text', 'description': '要输入的文本内容'},
    {'name': '清空输入框', 'mapping': 'clear', 
     'description': '输入前是否清空输入框', 'default': True},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 30},
])
def input_text(**kwargs):
    """输入文本

    Args:
        selector: 元素定位器
        text: 要输入的文本
        clear: 是否清空输入框
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    text = kwargs.get('text', '')
    clear = kwargs.get('clear', True)
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"输入文本: {selector} -> {text}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000

            if clear:
                # 使用fill方法，它会自动清空并填入内容
                element.fill(text, timeout=timeout_ms)
            else:
                # 不清空的情况下，先点击获得焦点，然后输入
                element.click(timeout=timeout_ms)
                element.type(text, delay=50, timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"输入文本: {text}\n"
                f"清空输入框: {clear}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="文本输入信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"文本输入成功: {selector} -> {text}")

            return {
                "result": text,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "text": text,
                    "operation": "input_text"
                }
            }

        except Exception as e:
            logger.error(f"文本输入失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="文本输入失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('清空文本', [
    {'name': '定位器', 'mapping': 'selector', 
     'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 30},
])
def clear_text(**kwargs):
    """清空文本

    Args:
        selector: 元素定位器
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"清空文本: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            timeout_ms = int(timeout * 1000) if timeout else 30000
            element.clear(timeout=timeout_ms)

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="文本清空信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"文本清空成功: {selector}")

            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "operation": "clear_text"
                }
            }

        except Exception as e:
            logger.error(f"文本清空失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="文本清空失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
