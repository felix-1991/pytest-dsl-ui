"""页面导航关键字

提供页面导航、刷新、前进后退等关键字。
"""

import logging
import allure

from pytest_dsl.core.keyword_manager import keyword_manager
from ..core.browser_manager import browser_manager
from ..core.page_context import PageContext

logger = logging.getLogger(__name__)


@keyword_manager.register('打开页面', [
    {'name': '地址', 'mapping': 'url', 'description': '要打开的页面URL'},
    {'name': '等待条件', 'mapping': 'wait_until',
     'description': '等待条件：load, domcontentloaded, networkidle', 'default': 'load'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 30},
    {'name': '忽略证书错误', 'mapping': 'ignore_https_errors',
     'description': '是否忽略HTTPS证书错误', 'default': True},
], category='UI/导航', tags=['打开', '跳转'])
def open_page(**kwargs):
    """打开页面

    Args:
        url: 页面URL
        wait_until: 等待条件
        timeout: 超时时间
        ignore_https_errors: 是否忽略HTTPS证书错误

    Returns:
        dict: 操作结果
    """
    url = kwargs.get('url')
    wait_until = kwargs.get('wait_until', 'load')
    timeout = kwargs.get('timeout')
    ignore_https_errors = kwargs.get('ignore_https_errors', True)

    if not url:
        raise ValueError("URL参数不能为空")

    with allure.step(f"打开页面: {url}"):
        try:
            # 如果需要忽略HTTPS证书错误，且当前上下文不支持，需要创建新上下文
            if ignore_https_errors and url.startswith('https://'):
                # 检查当前上下文是否支持忽略HTTPS错误
                current_page = browser_manager.get_current_page()
                current_context = current_page.context

                # 如果当前上下文没有设置ignore_https_errors，创建新上下文
                if not getattr(current_context, '_ignore_https_errors', False):
                    # 创建支持忽略HTTPS错误的新上下文
                    browser_id = browser_manager.current_browser
                    if browser_id:
                        context_id = browser_manager.create_context(
                            browser_id,
                            ignore_https_errors=True
                        )
                        page_id = browser_manager.create_page(context_id)
                        browser_manager.switch_page(page_id)

            page = browser_manager.get_current_page()
            page_context = PageContext(page)

            page_context.navigate(url, wait_until, timeout)

            allure.attach(
                f"URL: {url}\n"
                f"等待条件: {wait_until}\n"
                f"超时时间: {timeout or '默认'}秒\n"
                f"忽略HTTPS证书错误: {ignore_https_errors}",
                name="页面导航信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"页面打开成功: {url}")

            # 直接返回访问的URL
            return url

        except Exception as e:
            logger.error(f"打开页面失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="页面导航失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('刷新页面', [
    {'name': '等待条件', 'mapping': 'wait_until',
     'description': '等待条件：load, domcontentloaded, networkidle', 'default': 'load'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 30},
], category='UI/导航', tags=['刷新'])
def refresh_page(**kwargs):
    """刷新页面

    Args:
        wait_until: 等待条件
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    wait_until = kwargs.get('wait_until', 'load')
    timeout = kwargs.get('timeout')

    with allure.step("刷新页面"):
        try:
            page = browser_manager.get_current_page()
            page_context = PageContext(page)

            page_context.reload(wait_until, timeout)

            allure.attach(
                f"等待条件: {wait_until}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="页面刷新信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info("页面刷新成功")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"刷新页面失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="页面刷新失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('后退', [
    {'name': '等待条件', 'mapping': 'wait_until',
     'description': '等待条件：load, domcontentloaded, networkidle', 'default': 'load'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 30},
], category='UI/导航', tags=['后退', '历史'])
def go_back(**kwargs):
    """浏览器后退

    Args:
        wait_until: 等待条件
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    wait_until = kwargs.get('wait_until', 'load')
    timeout = kwargs.get('timeout')

    with allure.step("浏览器后退"):
        try:
            page = browser_manager.get_current_page()
            page_context = PageContext(page)

            page_context.go_back(wait_until, timeout)

            allure.attach(
                f"等待条件: {wait_until}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="浏览器后退信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info("浏览器后退成功")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"浏览器后退失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="浏览器后退失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('前进', [
    {'name': '等待条件', 'mapping': 'wait_until',
     'description': '等待条件：load, domcontentloaded, networkidle', 'default': 'load'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）', 'default': 30},
], category='UI/导航', tags=['前进', '历史'])
def go_forward(**kwargs):
    """浏览器前进

    Args:
        wait_until: 等待条件
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    wait_until = kwargs.get('wait_until', 'load')
    timeout = kwargs.get('timeout')

    with allure.step("浏览器前进"):
        try:
            page = browser_manager.get_current_page()
            page_context = PageContext(page)

            page_context.go_forward(wait_until, timeout)

            allure.attach(
                f"等待条件: {wait_until}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="浏览器前进信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info("浏览器前进成功")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"浏览器前进失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="浏览器前进失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('获取页面标题', [], category='UI/导航', tags=['获取', '标题'])
def get_page_title(**kwargs):
    """获取页面标题

    Returns:
        dict: 包含页面标题的字典
    """
    with allure.step("获取页面标题"):
        try:
            page = browser_manager.get_current_page()
            page_context = PageContext(page)

            title = page_context.get_title()

            allure.attach(
                f"页面标题: {title}",
                name="页面标题信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"获取页面标题成功: {title}")

            # 直接返回页面标题
            return title

        except Exception as e:
            logger.error(f"获取页面标题失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="获取页面标题失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('获取当前地址', [], category='UI/导航', tags=['获取', 'URL'])
def get_current_url(**kwargs):
    """获取当前页面URL

    Returns:
        dict: 包含当前URL的字典
    """
    with allure.step("获取当前地址"):
        try:
            page = browser_manager.get_current_page()
            page_context = PageContext(page)

            url = page_context.get_url()

            allure.attach(
                f"当前URL: {url}",
                name="当前地址信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"获取当前地址成功: {url}")

            # 直接返回当前URL
            return url

        except Exception as e:
            logger.error(f"获取当前地址失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="获取当前地址失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
