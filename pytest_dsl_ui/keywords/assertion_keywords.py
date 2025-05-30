"""UI断言关键字

提供UI元素存在性、可见性、文本内容等断言功能。
使用Playwright的expect API实现更可靠的断言。
"""

import asyncio
import logging
import allure
from typing import Optional

from pytest_dsl.core.keyword_manager import keyword_manager
from ..core.browser_manager import browser_manager
from ..core.element_locator import ElementLocator

# 导入Playwright的expect API
try:
    from playwright.sync_api import expect
except ImportError:
    # 如果同步API不可用，使用异步API
    from playwright.async_api import expect as async_expect
    expect = None

logger = logging.getLogger(__name__)


def _get_current_locator() -> ElementLocator:
    """获取当前页面的元素定位器"""
    page = browser_manager.get_current_page()
    return ElementLocator(page)


def _run_async_assertion(coro):
    """运行异步断言"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果循环正在运行，创建一个任务
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


@keyword_manager.register('断言元素可见_新', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_element_visible_new(**kwargs):
    """使用Playwright expect API断言元素可见

    Args:
        selector: 元素定位器
        timeout: 超时时间（秒）
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout', 5.0)  # 默认5秒超时
    message = kwargs.get('message', f'元素 {selector} 应该可见')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"断言元素可见(新): {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            # 使用Playwright的expect API进行断言
            async def _assert_visible():
                from playwright.async_api import expect as async_expect
                await async_expect(element).to_be_visible(timeout=int(timeout * 1000))

            _run_async_assertion(_assert_visible())

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="元素可见断言(新)",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素可见断言通过(新): {selector}")

            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "assertion": "element_visible_new",
                    "operation": "assert_element_visible_new"
                }
            }

        except Exception as e:
            logger.error(f"元素可见断言失败(新): {selector} - {str(e)}")
            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}\n"
                f"实际错误: {str(e)}",
                name="元素可见断言失败(新)",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"{message}: {str(e)}")


@keyword_manager.register('断言文本内容_新', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '期望文本', 'mapping': 'expected_text', 'description': '期望的文本内容'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_text_content_new(**kwargs):
    """使用Playwright expect API断言文本内容

    Args:
        selector: 元素定位器
        expected_text: 期望的文本内容
        timeout: 超时时间（秒）
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    expected_text = kwargs.get('expected_text')
    timeout = kwargs.get('timeout', 5.0)  # 默认5秒超时
    message = kwargs.get('message', f'元素 {selector} 应该包含文本 {expected_text}')

    if not selector:
        raise ValueError("定位器参数不能为空")
    if expected_text is None:
        raise ValueError("期望文本参数不能为空")

    with allure.step(f"断言文本内容(新): {selector} -> {expected_text}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            # 使用Playwright的expect API进行断言
            async def _assert_text():
                from playwright.async_api import expect as async_expect
                await async_expect(element).to_contain_text(expected_text, timeout=int(timeout * 1000))

            _run_async_assertion(_assert_text())

            allure.attach(
                f"定位器: {selector}\n"
                f"期望文本: {expected_text}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="文本内容断言(新)",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"文本内容断言通过(新): {selector} -> {expected_text}")

            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "expected_text": expected_text,
                    "assertion": "text_content_new",
                    "operation": "assert_text_content_new"
                }
            }

        except Exception as e:
            logger.error(f"文本内容断言失败(新): {selector} -> {expected_text} - {str(e)}")
            allure.attach(
                f"定位器: {selector}\n"
                f"期望文本: {expected_text}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}\n"
                f"实际错误: {str(e)}",
                name="文本内容断言失败(新)",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"{message}: {str(e)}")


@keyword_manager.register('断言元素存在', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_element_exists(**kwargs):
    """断言元素存在

    Args:
        selector: 元素定位器
        timeout: 超时时间
        message: 错误消息

    Returns:
        dict: 断言结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout', 10)
    message = kwargs.get('message', f'元素不存在: {selector}')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"断言元素存在: {selector}"):
        try:
            locator = _get_current_locator()

            # 等待元素出现
            exists = locator.wait_for_element(selector, "attached", timeout)

            if not exists:
                raise AssertionError(message)

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="元素存在断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素存在断言通过: {selector}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "assertion": "element_exists",
                    "operation": "assert_element_exists"
                }
            }

        except AssertionError:
            logger.error(f"元素存在断言失败: {selector}")
            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}",
                name="元素存在断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        except Exception as e:
            logger.error(f"元素存在断言出错: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="元素存在断言出错",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('断言元素不存在', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_element_not_exists(**kwargs):
    """断言元素不存在

    Args:
        selector: 元素定位器
        timeout: 超时时间
        message: 错误消息

    Returns:
        dict: 断言结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout', 10)
    message = kwargs.get('message', f'元素仍然存在: {selector}')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"断言元素不存在: {selector}"):
        try:
            locator = _get_current_locator()

            # 等待元素消失
            not_exists = locator.wait_for_element(selector, "detached", timeout)

            if not not_exists:
                # 检查元素是否仍然存在
                count = locator.get_element_count(selector)
                if count > 0:
                    raise AssertionError(message)

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="元素不存在断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素不存在断言通过: {selector}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "assertion": "element_not_exists",
                    "operation": "assert_element_not_exists"
                }
            }

        except AssertionError:
            logger.error(f"元素不存在断言失败: {selector}")
            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}",
                name="元素不存在断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        except Exception as e:
            logger.error(f"元素不存在断言出错: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="元素不存在断言出错",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('断言元素可见', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_element_visible(**kwargs):
    """断言元素可见

    Args:
        selector: 元素定位器
        timeout: 超时时间
        message: 错误消息

    Returns:
        dict: 断言结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout', 10)
    message = kwargs.get('message', f'元素不可见: {selector}')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"断言元素可见: {selector}"):
        try:
            locator = _get_current_locator()

            # 等待元素可见
            visible = locator.wait_for_element(selector, "visible", timeout)

            if not visible:
                raise AssertionError(message)

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="元素可见断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素可见断言通过: {selector}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "assertion": "element_visible",
                    "operation": "assert_element_visible"
                }
            }

        except AssertionError:
            logger.error(f"元素可见断言失败: {selector}")
            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}",
                name="元素可见断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        except Exception as e:
            logger.error(f"元素可见断言出错: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="元素可见断言出错",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('断言元素启用', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_element_enabled(**kwargs):
    """断言元素启用

    Args:
        selector: 元素定位器
        message: 错误消息

    Returns:
        dict: 断言结果
    """
    selector = kwargs.get('selector')
    message = kwargs.get('message', f'元素未启用: {selector}')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"断言元素启用: {selector}"):
        try:
            locator = _get_current_locator()

            # 检查元素是否启用
            enabled = locator.is_element_enabled(selector)

            if not enabled:
                raise AssertionError(message)

            allure.attach(
                f"定位器: {selector}\n"
                f"断言结果: 通过",
                name="元素启用断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素启用断言通过: {selector}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "assertion": "element_enabled",
                    "operation": "assert_element_enabled"
                }
            }

        except AssertionError:
            logger.error(f"元素启用断言失败: {selector}")
            allure.attach(
                f"定位器: {selector}\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}",
                name="元素启用断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        except Exception as e:
            logger.error(f"元素启用断言出错: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="元素启用断言出错",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('断言文本内容', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '预期文本', 'mapping': 'expected_text', 'description': '预期的文本内容'},
    {'name': '匹配方式', 'mapping': 'match_type', 'description': '匹配方式：exact(完全匹配), contains(包含), starts_with(开头), ends_with(结尾)'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_text_content(**kwargs):
    """断言文本内容

    Args:
        selector: 元素定位器
        expected_text: 预期文本
        match_type: 匹配方式
        message: 错误消息

    Returns:
        dict: 断言结果
    """
    selector = kwargs.get('selector')
    expected_text = kwargs.get('expected_text')
    match_type = kwargs.get('match_type', 'exact')
    message = kwargs.get('message')

    if not selector:
        raise ValueError("定位器参数不能为空")
    if expected_text is None:
        raise ValueError("预期文本参数不能为空")

    with allure.step(f"断言文本内容: {selector}"):
        try:
            locator = _get_current_locator()

            # 获取实际文本
            actual_text = locator.get_element_text(selector)

            # 根据匹配方式进行比较
            match_result = False
            if match_type == 'exact':
                match_result = actual_text == expected_text
                default_message = f'文本不匹配。预期: "{expected_text}", 实际: "{actual_text}"'
            elif match_type == 'contains':
                match_result = expected_text in actual_text
                default_message = f'文本不包含预期内容。预期包含: "{expected_text}", 实际: "{actual_text}"'
            elif match_type == 'starts_with':
                match_result = actual_text.startswith(expected_text)
                default_message = f'文本开头不匹配。预期开头: "{expected_text}", 实际: "{actual_text}"'
            elif match_type == 'ends_with':
                match_result = actual_text.endswith(expected_text)
                default_message = f'文本结尾不匹配。预期结尾: "{expected_text}", 实际: "{actual_text}"'
            else:
                raise ValueError(f"不支持的匹配方式: {match_type}")

            if not match_result:
                raise AssertionError(message or default_message)

            allure.attach(
                f"定位器: {selector}\n"
                f"预期文本: {expected_text}\n"
                f"实际文本: {actual_text}\n"
                f"匹配方式: {match_type}\n"
                f"断言结果: 通过",
                name="文本内容断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"文本内容断言通过: {selector} -> {expected_text}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "expected_text": expected_text,
                    "actual_text": actual_text,
                    "match_type": match_type,
                    "assertion": "text_content",
                    "operation": "assert_text_content"
                }
            }

        except AssertionError:
            logger.error(f"文本内容断言失败: {selector}")
            allure.attach(
                f"定位器: {selector}\n"
                f"预期文本: {expected_text}\n"
                f"实际文本: {actual_text}\n"
                f"匹配方式: {match_type}\n"
                f"断言结果: 失败\n"
                f"错误消息: {message or default_message}",
                name="文本内容断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
        except Exception as e:
            logger.error(f"文本内容断言出错: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="文本内容断言出错",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
