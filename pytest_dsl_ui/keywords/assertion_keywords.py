"""UI断言关键字

提供UI元素存在性、可见性、文本内容等断言功能。
使用Playwright的expect API实现更可靠的断言。
"""

import asyncio
import logging
import allure

from pytest_dsl.core.keyword_manager import keyword_manager
from ..core.browser_manager import browser_manager
from ..core.element_locator import ElementLocator

# 导入Playwright的expect API
try:
    from playwright.sync_api import expect
    from playwright.async_api import expect as async_expect
except ImportError:
    expect = None
    async_expect = None

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


@keyword_manager.register('断言元素可见', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_element_visible(**kwargs):
    """断言元素可见

    Args:
        selector: 元素定位器
        timeout: 超时时间（秒）
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout', 5.0)
    message = kwargs.get('message', f'元素 {selector} 应该可见')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"断言元素可见: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            # 使用Playwright的expect API进行断言
            async def _assert_visible():
                await async_expect(element).to_be_visible(
                    timeout=int(timeout * 1000)
                )

            _run_async_assertion(_assert_visible())

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="元素可见断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素可见断言通过: {selector}")

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

        except Exception as e:
            logger.error(f"元素可见断言失败: {selector} - {str(e)}")
            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}\n"
                f"实际错误: {str(e)}",
                name="元素可见断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"{message}: {str(e)}")


@keyword_manager.register('断言元素隐藏', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_element_hidden(**kwargs):
    """断言元素隐藏

    Args:
        selector: 元素定位器
        timeout: 超时时间（秒）
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout', 5.0)
    message = kwargs.get('message', f'元素 {selector} 应该隐藏')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"断言元素隐藏: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            async def _assert_hidden():
                await async_expect(element).to_be_hidden(
                    timeout=int(timeout * 1000)
                )

            _run_async_assertion(_assert_hidden())

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="元素隐藏断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素隐藏断言通过: {selector}")

            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "assertion": "element_hidden",
                    "operation": "assert_element_hidden"
                }
            }

        except Exception as e:
            logger.error(f"元素隐藏断言失败: {selector} - {str(e)}")
            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}\n"
                f"实际错误: {str(e)}",
                name="元素隐藏断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"{message}: {str(e)}")


@keyword_manager.register('断言元素存在', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_element_exists(**kwargs):
    """断言元素存在（附加到DOM）

    Args:
        selector: 元素定位器
        timeout: 超时时间（秒）
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout', 5.0)
    message = kwargs.get('message', f'元素 {selector} 应该存在')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"断言元素存在: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            async def _assert_attached():
                await async_expect(element).to_be_attached(
                    timeout=int(timeout * 1000)
                )

            _run_async_assertion(_assert_attached())

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="元素存在断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素存在断言通过: {selector}")

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

        except Exception as e:
            logger.error(f"元素存在断言失败: {selector} - {str(e)}")
            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}\n"
                f"实际错误: {str(e)}",
                name="元素存在断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"{message}: {str(e)}")


@keyword_manager.register('断言元素启用', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_element_enabled(**kwargs):
    """断言元素启用

    Args:
        selector: 元素定位器
        timeout: 超时时间（秒）
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout', 5.0)
    message = kwargs.get('message', f'元素 {selector} 应该启用')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"断言元素启用: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            async def _assert_enabled():
                await async_expect(element).to_be_enabled(
                    timeout=int(timeout * 1000)
                )

            _run_async_assertion(_assert_enabled())

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="元素启用断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素启用断言通过: {selector}")

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

        except Exception as e:
            logger.error(f"元素启用断言失败: {selector} - {str(e)}")
            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}\n"
                f"实际错误: {str(e)}",
                name="元素启用断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"{message}: {str(e)}")


@keyword_manager.register('断言元素禁用', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_element_disabled(**kwargs):
    """断言元素禁用

    Args:
        selector: 元素定位器
        timeout: 超时时间（秒）
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout', 5.0)
    message = kwargs.get('message', f'元素 {selector} 应该禁用')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"断言元素禁用: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            async def _assert_disabled():
                await async_expect(element).to_be_disabled(
                    timeout=int(timeout * 1000)
                )

            _run_async_assertion(_assert_disabled())

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="元素禁用断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素禁用断言通过: {selector}")

            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "assertion": "element_disabled",
                    "operation": "assert_element_disabled"
                }
            }

        except Exception as e:
            logger.error(f"元素禁用断言失败: {selector} - {str(e)}")
            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}\n"
                f"实际错误: {str(e)}",
                name="元素禁用断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"{message}: {str(e)}")


@keyword_manager.register('断言文本内容', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '期望文本', 'mapping': 'expected_text', 'description': '期望的文本内容'},
    {'name': '匹配方式', 'mapping': 'match_type', 'description': '完全匹配或包含匹配'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_text_content(**kwargs):
    """断言元素文本内容

    Args:
        selector: 元素定位器
        expected_text: 期望的文本内容
        match_type: 匹配方式 - exact(完全匹配) 或 contains(包含匹配)
        timeout: 超时时间（秒）
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    expected_text = kwargs.get('expected_text')
    match_type = kwargs.get('match_type', 'exact')
    timeout = kwargs.get('timeout', 5.0)
    message = kwargs.get('message')

    if not selector:
        raise ValueError("定位器参数不能为空")
    if expected_text is None:
        raise ValueError("期望文本参数不能为空")

    default_message = (
        f'元素 {selector} 文本应该{"完全匹配" if match_type == "exact" else "包含"} '
        f'"{expected_text}"'
    )
    message = message or default_message

    with allure.step(f"断言文本内容: {selector} -> {expected_text}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            async def _assert_text():
                if match_type == 'exact':
                    await async_expect(element).to_have_text(
                        expected_text, timeout=int(timeout * 1000)
                    )
                else:  # contains
                    await async_expect(element).to_contain_text(
                        expected_text, timeout=int(timeout * 1000)
                    )

            _run_async_assertion(_assert_text())

            allure.attach(
                f"定位器: {selector}\n"
                f"期望文本: {expected_text}\n"
                f"匹配方式: {match_type}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="文本内容断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"文本内容断言通过: {selector} -> {expected_text}")

            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "expected_text": expected_text,
                    "match_type": match_type,
                    "assertion": "text_content",
                    "operation": "assert_text_content"
                }
            }

        except Exception as e:
            logger.error(f"文本内容断言失败: {selector} -> {expected_text} - {str(e)}")
            allure.attach(
                f"定位器: {selector}\n"
                f"期望文本: {expected_text}\n"
                f"匹配方式: {match_type}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}\n"
                f"实际错误: {str(e)}",
                name="文本内容断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"{message}: {str(e)}")


@keyword_manager.register('断言输入值', [
    {'name': '定位器', 'mapping': 'selector', 'description': '输入元素定位器'},
    {'name': '期望值', 'mapping': 'expected_value', 'description': '期望的输入值'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_input_value(**kwargs):
    """断言输入元素的值

    Args:
        selector: 输入元素定位器
        expected_value: 期望的输入值
        timeout: 超时时间（秒）
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    expected_value = kwargs.get('expected_value')
    timeout = kwargs.get('timeout', 5.0)
    message = kwargs.get('message', f'输入元素 {selector} 值应该为 "{expected_value}"')

    if not selector:
        raise ValueError("定位器参数不能为空")
    if expected_value is None:
        raise ValueError("期望值参数不能为空")

    with allure.step(f"断言输入值: {selector} -> {expected_value}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            async def _assert_value():
                await async_expect(element).to_have_value(
                    expected_value, timeout=int(timeout * 1000)
                )

            _run_async_assertion(_assert_value())

            allure.attach(
                f"定位器: {selector}\n"
                f"期望值: {expected_value}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="输入值断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"输入值断言通过: {selector} -> {expected_value}")

            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "expected_value": expected_value,
                    "assertion": "input_value",
                    "operation": "assert_input_value"
                }
            }

        except Exception as e:
            logger.error(f"输入值断言失败: {selector} -> {expected_value} - {str(e)}")
            allure.attach(
                f"定位器: {selector}\n"
                f"期望值: {expected_value}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}\n"
                f"实际错误: {str(e)}",
                name="输入值断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"{message}: {str(e)}")


@keyword_manager.register('断言属性值', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '属性名', 'mapping': 'attribute_name', 'description': '属性名称'},
    {'name': '期望值', 'mapping': 'expected_value', 'description': '期望的属性值'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_attribute_value(**kwargs):
    """断言元素属性值

    Args:
        selector: 元素定位器
        attribute_name: 属性名称
        expected_value: 期望的属性值
        timeout: 超时时间（秒）
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    attribute_name = kwargs.get('attribute_name')
    expected_value = kwargs.get('expected_value')
    timeout = kwargs.get('timeout', 5.0)
    message = kwargs.get(
        'message',
        f'元素 {selector} 属性 {attribute_name} 应该为 "{expected_value}"'
    )

    if not selector:
        raise ValueError("定位器参数不能为空")
    if not attribute_name:
        raise ValueError("属性名参数不能为空")

    with allure.step(
        f"断言属性值: {selector}.{attribute_name} -> {expected_value}"
    ):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            async def _assert_attribute():
                await async_expect(element).to_have_attribute(
                    attribute_name, expected_value, timeout=int(timeout * 1000)
                )

            _run_async_assertion(_assert_attribute())

            allure.attach(
                f"定位器: {selector}\n"
                f"属性名: {attribute_name}\n"
                f"期望值: {expected_value}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="属性值断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(
                f"属性值断言通过: {selector}.{attribute_name} -> {expected_value}"
            )

            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "attribute_name": attribute_name,
                    "expected_value": expected_value,
                    "assertion": "attribute_value",
                    "operation": "assert_attribute_value"
                }
            }

        except Exception as e:
            error_msg = (
                f"{selector}.{attribute_name} -> {expected_value} - {str(e)}"
            )
            logger.error(f"属性值断言失败: {error_msg}")
            allure.attach(
                f"定位器: {selector}\n"
                f"属性名: {attribute_name}\n"
                f"期望值: {expected_value}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}\n"
                f"实际错误: {str(e)}",
                name="属性值断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"{message}: {str(e)}")


@keyword_manager.register('断言元素数量', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '期望数量', 'mapping': 'expected_count', 'description': '期望的元素数量'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_element_count(**kwargs):
    """断言元素数量

    Args:
        selector: 元素定位器
        expected_count: 期望的元素数量
        timeout: 超时时间（秒）
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    expected_count = kwargs.get('expected_count')
    timeout = kwargs.get('timeout', 5.0)
    message = kwargs.get('message', f'元素 {selector} 数量应该为 {expected_count}')

    if not selector:
        raise ValueError("定位器参数不能为空")
    if expected_count is None:
        raise ValueError("期望数量参数不能为空")

    try:
        expected_count = int(expected_count)
    except (ValueError, TypeError):
        raise ValueError("期望数量必须是数字")

    with allure.step(f"断言元素数量: {selector} -> {expected_count}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            async def _assert_count():
                await async_expect(element).to_have_count(
                    expected_count, timeout=int(timeout * 1000)
                )

            _run_async_assertion(_assert_count())

            allure.attach(
                f"定位器: {selector}\n"
                f"期望数量: {expected_count}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="元素数量断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素数量断言通过: {selector} -> {expected_count}")

            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "expected_count": expected_count,
                    "assertion": "element_count",
                    "operation": "assert_element_count"
                }
            }

        except Exception as e:
            logger.error(
                f"元素数量断言失败: {selector} -> {expected_count} - {str(e)}"
            )
            allure.attach(
                f"定位器: {selector}\n"
                f"期望数量: {expected_count}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}\n"
                f"实际错误: {str(e)}",
                name="元素数量断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"{message}: {str(e)}")


@keyword_manager.register('断言页面标题', [
    {'name': '期望标题', 'mapping': 'expected_title', 'description': '期望的页面标题'},
    {'name': '匹配方式', 'mapping': 'match_type', 'description': '完全匹配或包含匹配'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_page_title(**kwargs):
    """断言页面标题

    Args:
        expected_title: 期望的页面标题
        match_type: 匹配方式 - exact(完全匹配) 或 contains(包含匹配)
        timeout: 超时时间（秒）
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    expected_title = kwargs.get('expected_title')
    match_type = kwargs.get('match_type', 'exact')
    timeout = kwargs.get('timeout', 5.0)
    message = kwargs.get('message')

    if expected_title is None:
        raise ValueError("期望标题参数不能为空")

    default_message = (
        f'页面标题应该{"完全匹配" if match_type == "exact" else "包含"} '
        f'"{expected_title}"'
    )
    message = message or default_message

    with allure.step(f"断言页面标题: {expected_title}"):
        try:
            page = browser_manager.get_current_page()

            async def _assert_title():
                from playwright.async_api import expect as page_expect
                if match_type == 'exact':
                    await page_expect(page).to_have_title(
                        expected_title, timeout=int(timeout * 1000)
                    )
                else:  # contains
                    import re
                    pattern = re.compile(f".*{re.escape(expected_title)}.*")
                    await page_expect(page).to_have_title(
                        pattern, timeout=int(timeout * 1000)
                    )

            _run_async_assertion(_assert_title())

            allure.attach(
                f"期望标题: {expected_title}\n"
                f"匹配方式: {match_type}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="页面标题断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"页面标题断言通过: {expected_title}")

            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "expected_title": expected_title,
                    "match_type": match_type,
                    "assertion": "page_title",
                    "operation": "assert_page_title"
                }
            }

        except Exception as e:
            logger.error(f"页面标题断言失败: {expected_title} - {str(e)}")
            allure.attach(
                f"期望标题: {expected_title}\n"
                f"匹配方式: {match_type}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}\n"
                f"实际错误: {str(e)}",
                name="页面标题断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"{message}: {str(e)}")


@keyword_manager.register('断言页面URL', [
    {'name': '期望URL', 'mapping': 'expected_url', 'description': '期望的页面URL'},
    {'name': '匹配方式', 'mapping': 'match_type', 'description': '完全匹配或包含匹配'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
])
def assert_page_url(**kwargs):
    """断言页面URL

    Args:
        expected_url: 期望的页面URL
        match_type: 匹配方式 - exact(完全匹配) 或 contains(包含匹配)
        timeout: 超时时间（秒）
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    expected_url = kwargs.get('expected_url')
    match_type = kwargs.get('match_type', 'exact')
    timeout = kwargs.get('timeout', 5.0)
    message = kwargs.get('message')

    if expected_url is None:
        raise ValueError("期望URL参数不能为空")

    default_message = (
        f'页面URL应该{"完全匹配" if match_type == "exact" else "包含"} '
        f'"{expected_url}"'
    )
    message = message or default_message

    with allure.step(f"断言页面URL: {expected_url}"):
        try:
            page = browser_manager.get_current_page()

            async def _assert_url():
                from playwright.async_api import expect as page_expect
                if match_type == 'exact':
                    await page_expect(page).to_have_url(
                        expected_url, timeout=int(timeout * 1000)
                    )
                else:  # contains
                    import re
                    pattern = re.compile(f".*{re.escape(expected_url)}.*")
                    await page_expect(page).to_have_url(
                        pattern, timeout=int(timeout * 1000)
                    )

            _run_async_assertion(_assert_url())

            allure.attach(
                f"期望URL: {expected_url}\n"
                f"匹配方式: {match_type}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="页面URL断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"页面URL断言通过: {expected_url}")

            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "expected_url": expected_url,
                    "match_type": match_type,
                    "assertion": "page_url",
                    "operation": "assert_page_url"
                }
            }

        except Exception as e:
            logger.error(f"页面URL断言失败: {expected_url} - {str(e)}")
            allure.attach(
                f"期望URL: {expected_url}\n"
                f"匹配方式: {match_type}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}\n"
                f"实际错误: {str(e)}",
                name="页面URL断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"{message}: {str(e)}")
