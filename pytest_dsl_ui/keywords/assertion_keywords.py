"""UI断言关键字

提供UI元素存在性、可见性、文本内容等断言功能。
使用Playwright的expect API实现更可靠的断言。
"""

import logging
import allure

from pytest_dsl.core.keyword_manager import keyword_manager
from ..core.browser_manager import browser_manager
from ..core.element_locator import ElementLocator

# 导入Playwright的expect API
try:
    from playwright.sync_api import expect
except ImportError:
    expect = None

logger = logging.getLogger(__name__)


def _get_current_locator() -> ElementLocator:
    """获取当前页面的元素定位器"""
    page = browser_manager.get_current_page()
    return ElementLocator(page)


@keyword_manager.register('断言元素可见', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 5},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
], category='UI/断言')
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
    timeout = kwargs.get('timeout', 5)
    message = kwargs.get('message', f'元素 {selector} 应该可见')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"断言元素可见: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            # 使用Playwright的expect API进行断言
            expect(element).to_be_visible(timeout=int(timeout * 1000))

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="元素可见断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素可见断言通过: {selector}")

            # 直接返回断言结果
            return True

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
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 5},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
], category='UI/断言')
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
    timeout = kwargs.get('timeout', 5)
    message = kwargs.get('message', f'元素 {selector} 应该隐藏')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"断言元素隐藏: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            expect(element).to_be_hidden(timeout=int(timeout * 1000))

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
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 5},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
], category='UI/断言')
def assert_element_exists(**kwargs):
    """断言元素存在

    Args:
        selector: 元素定位器
        timeout: 超时时间（秒）
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout', 5)
    message = kwargs.get('message', f'元素 {selector} 应该存在')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"断言元素存在: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            expect(element).to_be_attached(timeout=int(timeout * 1000))

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
], category='UI/断言')
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
    timeout = kwargs.get('timeout', 5)
    message = kwargs.get('message', f'元素 {selector} 应该启用')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"断言元素启用: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            expect(element).to_be_enabled(timeout=int(timeout * 1000))

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
], category='UI/断言')
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
    timeout = kwargs.get('timeout', 5)
    message = kwargs.get('message', f'元素 {selector} 应该禁用')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"断言元素禁用: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            expect(element).to_be_disabled(timeout=int(timeout * 1000))

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
    {'name': '匹配方式', 'mapping': 'match_type',
        'description': '完全匹配或包含匹配，匹配方式 - exact(完全匹配) 或 contains(包含匹配)', 'default': 'exact'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 5},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
], category='UI/断言')
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
    timeout = kwargs.get('timeout', 5)
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

            # 根据匹配方式选择不同的断言方法
            if match_type == 'contains':
                expect(element).to_contain_text(
                    expected_text, timeout=int(timeout * 1000)
                )
            else:  # exact
                expect(element).to_have_text(
                    expected_text, timeout=int(timeout * 1000)
                )

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
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 5},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
], category='UI/断言')
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
    timeout = kwargs.get('timeout', 5)
    message = kwargs.get('message', f'输入元素 {selector} 值应该为 "{expected_value}"')

    if not selector:
        raise ValueError("定位器参数不能为空")
    if expected_value is None:
        raise ValueError("期望值参数不能为空")

    with allure.step(f"断言输入值: {selector} -> {expected_value}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            expect(element).to_have_value(
                expected_value, timeout=int(timeout * 1000)
            )

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
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 5},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
], category='UI/断言')
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
    timeout = kwargs.get('timeout', 5)
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

            expect(element).to_have_attribute(
                attribute_name, expected_value, timeout=int(timeout * 1000)
            )

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
], category='UI/断言')
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
    timeout = kwargs.get('timeout', 5)
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

            expect(element).to_have_count(
                expected_count, timeout=int(timeout * 1000)
            )

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
], category='UI/断言')
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
    timeout = kwargs.get('timeout', 5)
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

            # 根据匹配方式选择不同的断言方法
            if match_type == 'contains':
                # 使用正则表达式实现包含匹配
                import re
                title_pattern = re.compile(f".*{re.escape(expected_title)}.*")
                expect(page).to_have_title(
                    title_pattern, timeout=int(timeout * 1000)
                )
            else:  # exact
                expect(page).to_have_title(
                    expected_title, timeout=int(timeout * 1000)
                )

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
], category='UI/断言')
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
    timeout = kwargs.get('timeout', 5)
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

            # 根据匹配方式选择不同的断言方法
            if match_type == 'contains':
                # 使用正则表达式实现包含匹配
                import re
                url_pattern = re.compile(f".*{re.escape(expected_url)}.*")
                expect(page).to_have_url(
                    url_pattern, timeout=int(timeout * 1000)
                )
            else:  # exact
                expect(page).to_have_url(
                    expected_url, timeout=int(timeout * 1000)
                )

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


# ===== Bool类型的元素检查方法 =====
# 以下方法返回bool值，不会抛出异常，适合在条件判断中使用


@keyword_manager.register('检查元素是否可见', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
], category='UI/断言')
def check_element_visible(**kwargs):
    """检查元素是否可见

    Args:
        selector: 元素定位器
        timeout: 超时时间（秒）

    Returns:
        dict: 包含boolean结果的操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout', 3.0)

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"检查元素是否可见: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            # 使用is_visible()方法检查，不会抛出异常
            is_visible = element.is_visible()

            if is_visible:
                # 再次确认元素真的可见（有时需要等待）
                # 使用与断言相同的逻辑确保一致性
                try:
                    expect(element).to_be_visible(timeout=int(timeout * 1000))
                    result = True
                except Exception:
                    # 如果expect失败，但is_visible为True，说明元素可见但可能不稳定
                    # 使用is_element_visible方法再次检查（支持智能定位器）
                    result = locator.is_element_visible(selector)
            else:
                result = False

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"检查结果: {'可见' if result else '不可见'}",
                name="元素可见性检查",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素可见性检查: {selector} -> {'可见' if result else '不可见'}")

            # 直接返回检查结果
            return result

        except Exception as e:
            logger.error(f"元素可见性检查异常: {selector} - {str(e)}")
            # 对于检查类方法，异常时应该返回False而不是抛出异常
            # 但同时使用is_element_visible做最后尝试
            try:
                locator = _get_current_locator()
                result = locator.is_element_visible(selector)
                logger.info(
                    f"使用备用方法检查元素可见性: {selector} -> {'可见' if result else '不可见'}")
            except Exception:
                result = False

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"检查结果: {'可见' if result else '异常 - 不可见'}\n"
                f"异常信息: {str(e)}",
                name="元素可见性检查异常",
                attachment_type=allure.attachment_type.TEXT
            )

            return {
                "result": result,
                "captures": {"is_visible": result, "error": str(e)},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "check_type": "element_visible",
                    "operation": "check_element_visible"
                }
            }


@keyword_manager.register('检查元素是否存在', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
], category='UI/断言')
def check_element_exists(**kwargs):
    """检查元素是否存在

    Args:
        selector: 元素定位器
        timeout: 超时时间（秒）

    Returns:
        dict: 包含boolean结果的操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout', 3.0)

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"检查元素是否存在: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            # 使用count()方法检查元素数量
            count = element.count()
            result = count > 0

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"元素数量: {count}\n"
                f"检查结果: {'存在' if result else '不存在'}",
                name="元素存在性检查",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素存在性检查: {selector} -> {'存在' if result else '不存在'}")

            return {
                "result": result,
                "captures": {"exists": result, "count": count},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "check_type": "element_exists",
                    "operation": "check_element_exists"
                }
            }

        except Exception as e:
            logger.error(f"元素存在性检查异常: {selector} - {str(e)}")
            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"检查结果: 异常 - {str(e)}",
                name="元素存在性检查异常",
                attachment_type=allure.attachment_type.TEXT
            )

            return {
                "result": False,
                "captures": {"exists": False, "error": str(e)},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "check_type": "element_exists",
                    "operation": "check_element_exists"
                }
            }


@keyword_manager.register('检查元素是否启用', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
], category='UI/断言')
def check_element_enabled(**kwargs):
    """检查元素是否启用

    Args:
        selector: 元素定位器
        timeout: 超时时间（秒）

    Returns:
        dict: 包含boolean结果的操作结果
    """
    selector = kwargs.get('selector')
    timeout = kwargs.get('timeout', 3.0)

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"检查元素是否启用: {selector}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            # 使用is_enabled()方法检查
            result = element.is_enabled()

            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"检查结果: {'启用' if result else '禁用'}",
                name="元素启用状态检查",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素启用状态检查: {selector} -> {'启用' if result else '禁用'}")

            return {
                "result": result,
                "captures": {"is_enabled": result},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "check_type": "element_enabled",
                    "operation": "check_element_enabled"
                }
            }

        except Exception as e:
            logger.error(f"元素启用状态检查异常: {selector} - {str(e)}")
            allure.attach(
                f"定位器: {selector}\n"
                f"超时时间: {timeout}秒\n"
                f"检查结果: 异常 - {str(e)}",
                name="元素启用状态检查异常",
                attachment_type=allure.attachment_type.TEXT
            )

            return {
                "result": False,
                "captures": {"is_enabled": False, "error": str(e)},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "check_type": "element_enabled",
                    "operation": "check_element_enabled"
                }
            }


@keyword_manager.register('检查文本是否包含', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '期望文本', 'mapping': 'expected_text', 'description': '期望包含的文本'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
], category='UI/断言')
def check_text_contains(**kwargs):
    """检查元素文本是否包含指定内容

    Args:
        selector: 元素定位器
        expected_text: 期望包含的文本
        timeout: 超时时间（秒）

    Returns:
        dict: 包含boolean结果的操作结果
    """
    selector = kwargs.get('selector')
    expected_text = kwargs.get('expected_text')
    timeout = kwargs.get('timeout', 3.0)

    if not selector:
        raise ValueError("定位器参数不能为空")
    if expected_text is None:
        raise ValueError("期望文本参数不能为空")

    with allure.step(f"检查文本是否包含: {selector} -> {expected_text}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            # 获取元素文本内容
            actual_text = element.text_content()
            result = expected_text in (actual_text or "")

            allure.attach(
                f"定位器: {selector}\n"
                f"期望文本: {expected_text}\n"
                f"实际文本: {actual_text}\n"
                f"超时时间: {timeout}秒\n"
                f"检查结果: {'包含' if result else '不包含'}",
                name="文本包含检查",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"文本包含检查: {selector} -> {'包含' if result else '不包含'}")

            return {
                "result": result,
                "captures": {
                    "contains_text": result,
                    "actual_text": actual_text,
                    "expected_text": expected_text
                },
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "expected_text": expected_text,
                    "check_type": "text_contains",
                    "operation": "check_text_contains"
                }
            }

        except Exception as e:
            logger.error(f"文本包含检查异常: {selector} -> {expected_text} - {str(e)}")
            allure.attach(
                f"定位器: {selector}\n"
                f"期望文本: {expected_text}\n"
                f"超时时间: {timeout}秒\n"
                f"检查结果: 异常 - {str(e)}",
                name="文本包含检查异常",
                attachment_type=allure.attachment_type.TEXT
            )

            return {
                "result": False,
                "captures": {
                    "contains_text": False,
                    "expected_text": expected_text,
                    "error": str(e)
                },
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "expected_text": expected_text,
                    "check_type": "text_contains",
                    "operation": "check_text_contains"
                }
            }


@keyword_manager.register('检查页面URL是否包含', [
    {'name': '期望URL片段', 'mapping': 'url_fragment',
     'description': '期望包含的URL片段'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
], category='UI/断言')
def check_url_contains(**kwargs):
    """检查页面URL是否包含指定片段

    Args:
        url_fragment: 期望包含的URL片段
        timeout: 超时时间（秒）

    Returns:
        dict: 包含boolean结果的操作结果
    """
    url_fragment = kwargs.get('url_fragment')
    timeout = kwargs.get('timeout', 3.0)

    if url_fragment is None:
        raise ValueError("URL片段参数不能为空")

    with allure.step(f"检查页面URL是否包含: {url_fragment}"):
        try:
            page = browser_manager.get_current_page()
            current_url = page.url
            result = url_fragment in current_url

            allure.attach(
                f"期望URL片段: {url_fragment}\n"
                f"当前URL: {current_url}\n"
                f"超时时间: {timeout}秒\n"
                f"检查结果: {'包含' if result else '不包含'}",
                name="URL包含检查",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(
                f"URL包含检查: {url_fragment} -> "
                f"{'包含' if result else '不包含'}"
            )

            return {
                "result": result,
                "captures": {
                    "contains_url": result,
                    "current_url": current_url,
                    "url_fragment": url_fragment
                },
                "session_state": {},
                "metadata": {
                    "url_fragment": url_fragment,
                    "check_type": "url_contains",
                    "operation": "check_url_contains"
                }
            }

        except Exception as e:
            logger.error(f"URL包含检查异常: {url_fragment} - {str(e)}")
            allure.attach(
                f"期望URL片段: {url_fragment}\n"
                f"超时时间: {timeout}秒\n"
                f"检查结果: 异常 - {str(e)}",
                name="URL包含检查异常",
                attachment_type=allure.attachment_type.TEXT
            )

            return {
                "result": False,
                "captures": {
                    "contains_url": False,
                    "url_fragment": url_fragment,
                    "error": str(e)
                },
                "session_state": {},
                "metadata": {
                    "url_fragment": url_fragment,
                    "check_type": "url_contains",
                    "operation": "check_url_contains"
                }
            }


@keyword_manager.register('检查页面标题是否包含', [
    {'name': '期望标题片段', 'mapping': 'title_fragment',
     'description': '期望包含的标题片段'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
], category='UI/断言')
def check_title_contains(**kwargs):
    """检查页面标题是否包含指定片段

    Args:
        title_fragment: 期望包含的标题片段
        timeout: 超时时间（秒）

    Returns:
        dict: 包含boolean结果的操作结果
    """
    title_fragment = kwargs.get('title_fragment')
    timeout = kwargs.get('timeout', 3.0)

    if title_fragment is None:
        raise ValueError("标题片段参数不能为空")

    with allure.step(f"检查页面标题是否包含: {title_fragment}"):
        try:
            page = browser_manager.get_current_page()
            current_title = page.title()
            result = title_fragment in current_title

            allure.attach(
                f"期望标题片段: {title_fragment}\n"
                f"当前标题: {current_title}\n"
                f"超时时间: {timeout}秒\n"
                f"检查结果: {'包含' if result else '不包含'}",
                name="标题包含检查",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(
                f"标题包含检查: {title_fragment} -> "
                f"{'包含' if result else '不包含'}"
            )

            return {
                "result": result,
                "captures": {
                    "contains_title": result,
                    "current_title": current_title,
                    "title_fragment": title_fragment
                },
                "session_state": {},
                "metadata": {
                    "title_fragment": title_fragment,
                    "check_type": "title_contains",
                    "operation": "check_title_contains"
                }
            }

        except Exception as e:
            logger.error(f"标题包含检查异常: {title_fragment} - {str(e)}")
            allure.attach(
                f"期望标题片段: {title_fragment}\n"
                f"超时时间: {timeout}秒\n"
                f"检查结果: 异常 - {str(e)}",
                name="标题包含检查异常",
                attachment_type=allure.attachment_type.TEXT
            )

            return {
                "result": False,
                "captures": {
                    "contains_title": False,
                    "title_fragment": title_fragment,
                    "error": str(e)
                },
                "session_state": {},
                "metadata": {
                    "title_fragment": title_fragment,
                    "check_type": "title_contains",
                    "operation": "check_title_contains"
                }
            }


@keyword_manager.register('检查元素属性值', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '属性名', 'mapping': 'attribute_name', 'description': '属性名称'},
    {'name': '期望值', 'mapping': 'expected_value', 'description': '期望的属性值'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
], category='UI/断言')
def check_attribute_value(**kwargs):
    """检查元素属性值是否匹配

    Args:
        selector: 元素定位器
        attribute_name: 属性名称
        expected_value: 期望的属性值
        timeout: 超时时间（秒）

    Returns:
        dict: 包含boolean结果的操作结果
    """
    selector = kwargs.get('selector')
    attribute_name = kwargs.get('attribute_name')
    expected_value = kwargs.get('expected_value')
    timeout = kwargs.get('timeout', 3.0)

    if not selector:
        raise ValueError("定位器参数不能为空")
    if not attribute_name:
        raise ValueError("属性名参数不能为空")

    with allure.step(
        f"检查元素属性值: {selector}.{attribute_name} -> {expected_value}"
    ):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            # 获取属性值
            actual_value = element.get_attribute(attribute_name)
            result = (str(actual_value) == str(expected_value)
                      if actual_value is not None
                      else expected_value is None)

            allure.attach(
                f"定位器: {selector}\n"
                f"属性名: {attribute_name}\n"
                f"期望值: {expected_value}\n"
                f"实际值: {actual_value}\n"
                f"超时时间: {timeout}秒\n"
                f"检查结果: {'匹配' if result else '不匹配'}",
                name="属性值检查",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(
                f"属性值检查: {selector}.{attribute_name} -> "
                f"{'匹配' if result else '不匹配'}"
            )

            return {
                "result": result,
                "captures": {
                    "attribute_matches": result,
                    "actual_value": actual_value,
                    "expected_value": expected_value
                },
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "attribute_name": attribute_name,
                    "expected_value": expected_value,
                    "check_type": "attribute_value",
                    "operation": "check_attribute_value"
                }
            }

        except Exception as e:
            error_msg = (
                f"{selector}.{attribute_name} -> {expected_value} - {str(e)}"
            )
            logger.error(f"属性值检查异常: {error_msg}")
            allure.attach(
                f"定位器: {selector}\n"
                f"属性名: {attribute_name}\n"
                f"期望值: {expected_value}\n"
                f"超时时间: {timeout}秒\n"
                f"检查结果: 异常 - {str(e)}",
                name="属性值检查异常",
                attachment_type=allure.attachment_type.TEXT
            )

            return {
                "result": False,
                "captures": {
                    "attribute_matches": False,
                    "expected_value": expected_value,
                    "error": str(e)
                },
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "attribute_name": attribute_name,
                    "expected_value": expected_value,
                    "check_type": "attribute_value",
                    "operation": "check_attribute_value"
                }
            }


@keyword_manager.register('多条件检查', [
    {'name': '检查条件列表', 'mapping': 'conditions', 'description': '包含多个检查条件的列表'},
    {'name': '逻辑关系', 'mapping': 'logic', 'description': 'AND或OR逻辑关系'},
], category='UI/断言')
def check_multiple_conditions(**kwargs):
    """执行多个条件检查并根据逻辑关系返回结果

    Args:
        conditions: 检查条件列表，每个条件包含type和参数
        logic: 逻辑关系，'AND'或'OR'

    Returns:
        dict: 包含boolean结果的操作结果

    示例:
        conditions = [
            {"type": "element_visible", "selector": "#login-button"},
            {"type": "text_contains", "selector": "#message", 
             "expected_text": "欢迎"}
        ]
    """
    conditions = kwargs.get('conditions', [], category='UI/元素')
    logic = kwargs.get('logic', 'AND').upper()

    if not conditions:
        raise ValueError("检查条件列表不能为空")
    if logic not in ['AND', 'OR']:
        raise ValueError("逻辑关系必须是AND或OR")

    with allure.step(f"多条件检查 ({logic})"):
        results = []
        details = []

        for i, condition in enumerate(conditions):
            condition_type = condition.get('type')
            try:
                if condition_type == 'element_visible':
                    result = check_element_visible(**condition)
                elif condition_type == 'element_exists':
                    result = check_element_exists(**condition)
                elif condition_type == 'element_enabled':
                    result = check_element_enabled(**condition)
                elif condition_type == 'text_contains':
                    result = check_text_contains(**condition)
                elif condition_type == 'url_contains':
                    result = check_url_contains(**condition)
                elif condition_type == 'title_contains':
                    result = check_title_contains(**condition)
                elif condition_type == 'attribute_value':
                    result = check_attribute_value(**condition)
                else:
                    raise ValueError(f"不支持的检查类型: {condition_type}")

                condition_result = result.get('result', False)
                results.append(condition_result)
                details.append({
                    "condition": condition,
                    "result": condition_result,
                    "details": result.get('captures', {})
                })

            except Exception as e:
                logger.error(f"条件检查异常 {i}: {str(e)}")
                results.append(False)
                details.append({
                    "condition": condition,
                    "result": False,
                    "error": str(e)
                })

        # 根据逻辑关系计算最终结果
        if logic == 'AND':
            final_result = all(results)
        else:  # OR
            final_result = any(results)

        passed_count = sum(results)
        total_count = len(results)

        allure.attach(
            f"逻辑关系: {logic}\n"
            f"总条件数: {total_count}\n"
            f"通过条件数: {passed_count}\n"
            f"最终结果: {'通过' if final_result else '失败'}\n"
            f"详细结果: {details}",
            name="多条件检查",
            attachment_type=allure.attachment_type.TEXT
        )

        logger.info(
            f"多条件检查 ({logic}): {passed_count}/{total_count} -> "
            f"{'通过' if final_result else '失败'}"
        )

        return {
            "result": final_result,
            "captures": {
                "final_result": final_result,
                "passed_count": passed_count,
                "total_count": total_count,
                "details": details
            },
            "session_state": {},
            "metadata": {
                "logic": logic,
                "conditions_count": total_count,
                "check_type": "multiple_conditions",
                "operation": "check_multiple_conditions"
            }
        }


@keyword_manager.register('断言复选框状态', [
    {'name': '定位器', 'mapping': 'selector', 'description': '复选框定位器'},
    {'name': '期望状态', 'mapping': 'expected_checked', 'description': '期望的选中状态（True/False）'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 5},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
], category='UI/断言')
def assert_checkbox_state(**kwargs):
    """断言复选框状态

    Args:
        selector: 复选框定位器
        expected_checked: 期望的选中状态
        timeout: 超时时间（秒）
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    expected_checked = kwargs.get('expected_checked')
    timeout = kwargs.get('timeout', 5)
    message = kwargs.get('message', 
                       f'复选框 {selector} 应该{"被选中" if expected_checked else "未选中"}')

    if not selector:
        raise ValueError("定位器参数不能为空")
    if expected_checked is None:
        raise ValueError("期望状态参数不能为空")

    with allure.step(f"断言复选框状态: {selector} -> {expected_checked}"):
        try:
            locator = _get_current_locator()
            element = locator.locate(selector)

            if expected_checked:
                expect(element).to_be_checked(timeout=int(timeout * 1000))
            else:
                expect(element).not_to_be_checked(timeout=int(timeout * 1000))

            allure.attach(
                f"定位器: {selector}\n"
                f"期望状态: {'选中' if expected_checked else '未选中'}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 通过",
                name="复选框状态断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"复选框状态断言通过: {selector} -> {expected_checked}")

            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "expected_checked": expected_checked,
                    "assertion": "checkbox_state",
                    "operation": "assert_checkbox_state"
                }
            }

        except Exception as e:
            logger.error(f"复选框状态断言失败: {selector} -> {expected_checked} - {str(e)}")
            allure.attach(
                f"定位器: {selector}\n"
                f"期望状态: {'选中' if expected_checked else '未选中'}\n"
                f"超时时间: {timeout}秒\n"
                f"断言结果: 失败\n"
                f"错误消息: {message}\n"
                f"实际错误: {str(e)}",
                name="复选框状态断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(f"{message}: {str(e)}")
