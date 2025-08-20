"""剪贴板操作关键字

提供系统剪贴板的读取、写入和比较功能。
基于pyperclip库实现跨平台剪贴板操作。
"""

import logging
import allure
import pyperclip

from pytest_dsl.core.keyword_manager import keyword_manager

logger = logging.getLogger(__name__)


@keyword_manager.register('获取剪贴板文本', [
    {'name': '变量名', 'mapping': 'variable',
     'description': '保存剪贴板文本的变量名'},
], category='系统/剪贴板')
def get_clipboard_text(**kwargs):
    """获取系统剪贴板中的文本内容

    Args:
        variable: 变量名

    Returns:
        str: 剪贴板中的文本内容
    """
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    with allure.step("获取剪贴板文本"):
        try:
            # 获取剪贴板文本
            clipboard_text = pyperclip.paste()

            # 保存到变量
            if variable and context:
                context.set(variable, clipboard_text)

            # 记录日志和报告
            allure.attach(
                f"剪贴板文本: {clipboard_text}\n"
                f"文本长度: {len(clipboard_text)}\n"
                f"保存变量: {variable or '无'}",
                name="剪贴板文本信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"获取剪贴板文本成功: {clipboard_text[:50]}{'...' if len(clipboard_text) > 50 else ''}")

            # 直接返回剪贴板文本
            return clipboard_text

        except Exception as e:
            logger.error(f"获取剪贴板文本失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="获取剪贴板文本失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('设置剪贴板文本', [
    {'name': '文本', 'mapping': 'text', 'description': '要设置到剪贴板的文本内容'},
], category='系统/剪贴板')
def set_clipboard_text(**kwargs):
    """设置系统剪贴板的文本内容

    Args:
        text: 要设置的文本内容

    Returns:
        bool: 操作是否成功
    """
    text = kwargs.get('text', '')

    if text is None:
        text = ''

    with allure.step("设置剪贴板文本"):
        try:
            # 设置剪贴板文本
            pyperclip.copy(text)

            # 记录日志和报告
            allure.attach(
                f"设置文本: {text}\n"
                f"文本长度: {len(text)}",
                name="剪贴板设置信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"设置剪贴板文本成功: {text[:50]}{'...' if len(text) > 50 else ''}")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"设置剪贴板文本失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="设置剪贴板文本失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('比较剪贴板文本', [
    {'name': '期望文本', 'mapping': 'expected_text', 'description': '期望的文本内容'},
    {'name': '匹配方式', 'mapping': 'match_type',
     'description': '匹配方式 - exact(完全匹配) 或 contains(包含匹配)', 'default': 'exact'},
    {'name': '忽略大小写', 'mapping': 'ignore_case', 'description': '是否忽略大小写', 'default': False},
    {'name': '忽略空白字符', 'mapping': 'ignore_whitespace', 'description': '是否忽略首尾空白字符', 'default': False},
], category='系统/剪贴板')
def compare_clipboard_text(**kwargs):
    """比较剪贴板文本与期望文本

    Args:
        expected_text: 期望的文本内容
        match_type: 匹配方式 - exact(完全匹配) 或 contains(包含匹配)
        ignore_case: 是否忽略大小写
        ignore_whitespace: 是否忽略首尾空白字符

    Returns:
        bool: 比较结果
    """
    expected_text = kwargs.get('expected_text')
    match_type = kwargs.get('match_type', 'exact')
    ignore_case = kwargs.get('ignore_case', False)
    ignore_whitespace = kwargs.get('ignore_whitespace', False)

    if expected_text is None:
        raise ValueError("期望文本参数不能为空")

    with allure.step("比较剪贴板文本"):
        try:
            # 获取剪贴板文本
            clipboard_text = pyperclip.paste()

            # 处理文本
            actual_text = clipboard_text
            expected_text_processed = expected_text

            if ignore_whitespace:
                actual_text = actual_text.strip()
                expected_text_processed = expected_text_processed.strip()

            if ignore_case:
                actual_text = actual_text.lower()
                expected_text_processed = expected_text_processed.lower()

            # 执行比较
            if match_type == 'exact':
                result = actual_text == expected_text_processed
            elif match_type == 'contains':
                result = expected_text_processed in actual_text
            else:
                raise ValueError(f"不支持的匹配方式: {match_type}")

            # 记录日志和报告
            allure.attach(
                f"剪贴板文本: {clipboard_text}\n"
                f"期望文本: {expected_text}\n"
                f"匹配方式: {match_type}\n"
                f"忽略大小写: {ignore_case}\n"
                f"忽略空白字符: {ignore_whitespace}\n"
                f"比较结果: {'匹配' if result else '不匹配'}",
                name="剪贴板文本比较信息",
                attachment_type=allure.attachment_type.TEXT
            )

            if result:
                logger.info(f"剪贴板文本比较成功: 文本匹配")
            else:
                logger.warning(f"剪贴板文本比较失败: 文本不匹配")

            # 直接返回比较结果
            return result

        except Exception as e:
            logger.error(f"剪贴板文本比较失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="剪贴板文本比较失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('断言剪贴板文本', [
    {'name': '期望文本', 'mapping': 'expected_text', 'description': '期望的文本内容'},
    {'name': '匹配方式', 'mapping': 'match_type',
     'description': '匹配方式 - exact(完全匹配) 或 contains(包含匹配)', 'default': 'exact'},
    {'name': '忽略大小写', 'mapping': 'ignore_case', 'description': '是否忽略大小写', 'default': False},
    {'name': '忽略空白字符', 'mapping': 'ignore_whitespace', 'description': '是否忽略首尾空白字符', 'default': False},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
], category='系统/剪贴板')
def assert_clipboard_text(**kwargs):
    """断言剪贴板文本内容

    Args:
        expected_text: 期望的文本内容
        match_type: 匹配方式 - exact(完全匹配) 或 contains(包含匹配)
        ignore_case: 是否忽略大小写
        ignore_whitespace: 是否忽略首尾空白字符
        message: 自定义错误消息

    Returns:
        bool: 断言结果
    """
    expected_text = kwargs.get('expected_text')
    match_type = kwargs.get('match_type', 'exact')
    ignore_case = kwargs.get('ignore_case', False)
    ignore_whitespace = kwargs.get('ignore_whitespace', False)
    message = kwargs.get('message')

    if expected_text is None:
        raise ValueError("期望文本参数不能为空")

    default_message = (
        f'剪贴板文本应该{"完全匹配" if match_type == "exact" else "包含"} '
        f'"{expected_text}"'
    )
    message = message or default_message

    with allure.step("断言剪贴板文本"):
        try:
            # 使用比较函数
            result = compare_clipboard_text(
                expected_text=expected_text,
                match_type=match_type,
                ignore_case=ignore_case,
                ignore_whitespace=ignore_whitespace
            )

            if not result:
                # 获取实际文本用于错误信息
                clipboard_text = pyperclip.paste()
                error_msg = f"{message}。实际文本: '{clipboard_text}'"
                
                allure.attach(
                    error_msg,
                    name="剪贴板文本断言失败",
                    attachment_type=allure.attachment_type.TEXT
                )
                
                raise AssertionError(error_msg)

            logger.info(f"剪贴板文本断言成功")
            return True

        except AssertionError:
            raise
        except Exception as e:
            logger.error(f"剪贴板文本断言失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="剪贴板文本断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
