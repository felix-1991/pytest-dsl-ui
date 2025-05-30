"""元素操作关键字

提供元素点击、输入、选择等交互操作关键字。
"""

import asyncio
import logging
import allure
from typing import Optional, List, Union

from pytest_dsl.core.keyword_manager import keyword_manager
from ..core.browser_manager import browser_manager
from ..core.element_locator import ElementLocator

logger = logging.getLogger(__name__)


def _get_current_locator() -> ElementLocator:
    """获取当前页面的元素定位器"""
    page = browser_manager.get_current_page()
    return ElementLocator(page)


@keyword_manager.register('点击元素', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '强制点击', 'mapping': 'force', 'description': '是否强制点击（忽略元素状态检查）'},
])
def click_element(**kwargs):
    """点击元素

    Args:
        selector: 元素定位器
        timeout: 超时时间
        force: 是否强制点击

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout')
    force = kwargs.get('force', False)

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"点击元素: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            # Playwright会自动等待元素可交互，无需显式等待
            # 使用优化的异步执行方式
            async def _click_async():
                timeout_ms = int(timeout * 1000) if timeout else 30000  # 默认30秒超时
                await element.click(force=force, timeout=timeout_ms)

            locator._run_async(_click_async())

            allure.attach(
                f"定位器: {selector}\n"
                f"强制点击: {force}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="元素点击信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素点击成功: {selector}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "operation": "click_element"
                }
            }

        except Exception as e:
            logger.error(f"元素点击失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="元素点击失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('双击元素', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
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

            # Playwright会自动等待元素可交互，无需显式等待
            # 使用优化的异步执行方式
            async def _double_click_async():
                timeout_ms = int(timeout * 1000) if timeout else 30000  # 默认30秒超时
                await element.dblclick(timeout=timeout_ms)

            locator._run_async(_double_click_async())

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="元素双击信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素双击成功: {selector}")

            # 统一返回格式 - 支持远程关键字模式
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
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
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

            # Playwright会自动等待元素可交互，无需显式等待
            # 使用优化的异步执行方式
            async def _right_click_async():
                timeout_ms = int(timeout * 1000) if timeout else 30000  # 默认30秒超时
                await element.click(button="right", timeout=timeout_ms)

            locator._run_async(_right_click_async())

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="元素右键点击信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素右键点击成功: {selector}")

            # 统一返回格式 - 支持远程关键字模式
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
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '文本', 'mapping': 'text', 'description': '要输入的文本内容'},
    {'name': '清空输入框', 'mapping': 'clear', 'description': '输入前是否清空输入框，默认为true'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
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

            # Playwright会自动等待元素可交互，无需显式等待
            # 使用优化的异步执行方式 - 模拟Playwright录制脚本的行为
            async def _input_async():
                timeout_ms = int(timeout * 1000) if timeout else 30000  # 默认30秒超时

                if clear:
                    # 使用fill方法，它会自动清空并填入内容（类似录制脚本）
                    await element.fill(text, timeout=timeout_ms)
                else:
                    # 不清空的情况下，先点击获得焦点，然后输入
                    await element.click(timeout=timeout_ms)
                    await element.type(text, delay=50, timeout=timeout_ms)

            locator._run_async(_input_async())

            allure.attach(
                f"定位器: {selector}\n"
                f"输入文本: {text}\n"
                f"清空输入框: {clear}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="文本输入信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"文本输入成功: {selector} -> {text}")

            # 统一返回格式 - 支持远程关键字模式
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
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器（CSS选择器、XPath、文本等）'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
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

            # Playwright会自动等待元素可交互，无需显式等待
            # 使用优化的异步执行方式
            async def _clear_async():
                timeout_ms = int(timeout * 1000) if timeout else 30000  # 默认30秒超时
                await element.clear(timeout=timeout_ms)

            locator._run_async(_clear_async())

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="文本清空信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"文本清空成功: {selector}")

            # 统一返回格式 - 支持远程关键字模式
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
