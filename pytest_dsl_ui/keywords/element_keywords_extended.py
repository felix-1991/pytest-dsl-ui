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
], category='UI/交互')
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

    if not any([value, label, index is not None], category='UI/元素'):
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
], category='UI/交互')
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
    {'name': '状态', 'mapping': 'state',
     'description': '等待状态：visible, hidden, attached, detached'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '失败时抛异常', 'mapping': 'raise_on_timeout',
     'description': '等待超时时是否抛出异常，默认为false'},
], category='UI/交互')
def wait_for_element(**kwargs):
    """等待元素出现或达到指定状态

    Args:
        selector: 元素定位器
        state: 等待状态
        timeout: 超时时间
        raise_on_timeout: 超时时是否抛出异常

    Returns:
        dict: 操作结果
    """
    selector = kwargs.get('selector')
    state = kwargs.get('state', 'visible')
    timeout = kwargs.get('timeout')
    raise_on_timeout = kwargs.get('raise_on_timeout', False)

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
                f"等待结果: {'成功' if result else '超时'}\n"
                f"失败时抛异常: {raise_on_timeout}",
                name="元素等待信息",
                attachment_type=allure.attachment_type.TEXT
            )

            if result:
                logger.info(f"元素等待成功: {selector} ({state})")
            else:
                logger.warning(f"元素等待超时: {selector} ({state})")

                # 如果设置了失败时抛异常，则抛出异常
                if raise_on_timeout:
                    raise TimeoutError(
                        f"等待元素超时: {selector} (状态: {state}, "
                        f"超时时间: {timeout or '默认'}秒)"
                    )

            # 直接返回等待结果
            return result

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
    {'name': '失败时抛异常', 'mapping': 'raise_on_timeout',
     'description': '等待超时时是否抛出异常，默认为false'},
], category='UI/交互')
def wait_for_text(**kwargs):
    """等待文本在页面中出现

    Args:
        text: 要等待的文本
        timeout: 超时时间
        raise_on_timeout: 超时时是否抛出异常

    Returns:
        dict: 操作结果
    """
    text = kwargs.get('text')
    timeout = kwargs.get('timeout')
    raise_on_timeout = kwargs.get('raise_on_timeout', False)

    if not text:
        raise ValueError("文本参数不能为空")

    with allure.step(f"等待文本出现: {text}"):
        try:
            locator = _get_current_locator()
            result = locator.wait_for_text(text, timeout)

            allure.attach(
                f"等待文本: {text}\n"
                f"超时时间: {timeout or '默认'}秒\n"
                f"等待结果: {'成功' if result else '超时'}\n"
                f"失败时抛异常: {raise_on_timeout}",
                name="文本等待信息",
                attachment_type=allure.attachment_type.TEXT
            )

            if result:
                logger.info(f"文本等待成功: {text}")
            else:
                logger.warning(f"文本等待超时: {text}")

                # 如果设置了失败时抛异常，则抛出异常
                if raise_on_timeout:
                    raise TimeoutError(
                        f"等待文本超时: {text} "
                        f"(超时时间: {timeout or '默认'}秒)"
                    )

            # 直接返回等待结果
            return result

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
], category='UI/交互')
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

            # 保存到变量
            if variable and context:
                context.set(variable, text)

            # 直接返回元素文本
            return text

        except Exception as e:
            logger.error(f"获取元素文本失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="获取元素文本失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('获取元素属性', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
    {'name': '属性', 'mapping': 'attribute', 'description': '要获取的属性名称'},
    {'name': '变量名', 'mapping': 'variable', 'description': '保存属性值的变量名'},
    {'name': '默认值', 'mapping': 'default_value',
        'description': '当属性不存在或为None时的默认值'},
], category='UI/交互')
def get_element_attribute(**kwargs):
    """获取元素属性值

    Args:
        selector: 元素定位器
        attribute: 属性名称
        variable: 变量名
        default_value: 当属性不存在或为None时的默认值

    Returns:
        dict: 包含属性值的字典
    """
    selector = kwargs.get('selector')
    attribute = kwargs.get('attribute')
    variable = kwargs.get('variable')
    default_value = kwargs.get('default_value')
    context = kwargs.get('context')

    if not selector:
        raise ValueError("定位器参数不能为空")
    if not attribute:
        raise ValueError("属性参数不能为空")

    with allure.step(f"获取元素属性: {selector}.{attribute}"):
        try:
            locator = _get_current_locator()
            attribute_value = locator.get_element_attribute(
                selector, attribute)

            # 处理None值和特殊属性
            if attribute_value is None:
                if default_value is not None:
                    attribute_value = default_value
                elif attribute.lower() in ['checked', 'selected', 'disabled']:
                    # 对于布尔属性，None表示false
                    attribute_value = False
                else:
                    # 对于其他属性，转换为字符串表示
                    attribute_value = "null"

            # 对于布尔属性的特殊处理
            elif attribute.lower() in ['checked', 'selected', 'disabled']:
                # 将字符串转换为布尔值
                if isinstance(attribute_value, str):
                    attribute_value = attribute_value.lower(
                    ) in ['true', 'checked', 'selected', 'disabled', '']
                else:
                    attribute_value = bool(attribute_value)

            # 对于checked属性，使用is_checked方法更可靠
            if attribute.lower() == 'checked':
                try:
                    attribute_value = locator.is_element_checked(selector)
                except Exception:
                    # 如果is_checked方法失败，回退到原来的逻辑
                    pass

            # 对于value属性，使用get_element_value方法更可靠
            if attribute.lower() == 'value':
                try:
                    attribute_value = locator.get_element_value(selector)
                except Exception:
                    # 如果get_element_value方法失败，回退到原来的逻辑
                    pass

            # 保存到变量
            captures = {}
            if variable and context:
                context.set(variable, attribute_value)
                captures[variable] = attribute_value

            allure.attach(
                f"定位器: {selector}\n"
                f"属性名: {attribute}\n"
                f"原始属性值: {locator.get_element_attribute(selector, attribute)}\n"
                f"处理后属性值: {attribute_value}\n"
                f"默认值: {default_value or '无'}\n"
                f"保存变量: {variable or '无'}",
                name="元素属性信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(
                f"获取元素属性成功: {selector}.{attribute} -> {attribute_value}")

            # 保存到变量
            if variable and context:
                context.set(variable, attribute_value)

            # 直接返回属性值
            return attribute_value

        except Exception as e:
            logger.error(f"获取元素属性失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="获取元素属性失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('检查元素是否选中', [
    {'name': '定位器', 'mapping': 'selector', 'description': '元素定位器'},
], category='UI/断言')
def check_element_checked(**kwargs):
    """检查元素是否选中（复选框或单选框）

    Args:
        selector: 元素定位器

    Returns:
        dict: 包含布尔值结果的字典
    """
    selector = kwargs.get('selector')

    if not selector:
        raise ValueError("定位器参数不能为空")

    with allure.step(f"检查元素是否选中: {selector}"):
        try:
            locator = _get_current_locator()
            is_checked = locator.is_element_checked(selector)

            allure.attach(
                f"定位器: {selector}\n"
                f"选中状态: {is_checked}",
                name="元素选中状态检查",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"元素选中状态检查完成: {selector} -> {is_checked}")

            return {
                "result": is_checked,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "selector": selector,
                    "checked": is_checked,
                    "operation": "check_element_checked"
                }
            }

        except Exception as e:
            logger.error(f"检查元素选中状态失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="元素选中状态检查失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
