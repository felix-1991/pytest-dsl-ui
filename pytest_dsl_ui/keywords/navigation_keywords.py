"""页面导航关键字

提供页面导航、刷新、前进后退等关键字。
"""

import logging
import allure
from typing import Optional

from pytest_dsl.core.keyword_manager import keyword_manager
from ..core.browser_manager import browser_manager
from ..core.page_context import PageContext

logger = logging.getLogger(__name__)


@keyword_manager.register('打开页面', [
    {'name': '地址', 'mapping': 'url', 'description': '要打开的页面URL'},
    {'name': '等待条件', 'mapping': 'wait_until', 'description': '等待条件：load, domcontentloaded, networkidle'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
])
def open_page(**kwargs):
    """打开页面
    
    Args:
        url: 页面URL
        wait_until: 等待条件
        timeout: 超时时间
        
    Returns:
        dict: 操作结果
    """
    url = kwargs.get('url')
    wait_until = kwargs.get('wait_until', 'load')
    timeout = kwargs.get('timeout')
    
    if not url:
        raise ValueError("URL参数不能为空")
    
    with allure.step(f"打开页面: {url}"):
        try:
            page = browser_manager.get_current_page()
            page_context = PageContext(page)
            
            page_context.navigate(url, wait_until, timeout)
            
            allure.attach(
                f"URL: {url}\n"
                f"等待条件: {wait_until}\n"
                f"超时时间: {timeout or '默认'}秒",
                name="页面导航信息",
                attachment_type=allure.attachment_type.TEXT
            )
            
            logger.info(f"页面打开成功: {url}")
            
            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": url,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "url": url,
                    "wait_until": wait_until,
                    "operation": "open_page"
                }
            }
            
        except Exception as e:
            logger.error(f"打开页面失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="页面导航失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('刷新页面', [
    {'name': '等待条件', 'mapping': 'wait_until', 'description': '等待条件：load, domcontentloaded, networkidle'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
])
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
            
            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "wait_until": wait_until,
                    "operation": "refresh_page"
                }
            }
            
        except Exception as e:
            logger.error(f"刷新页面失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="页面刷新失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('后退', [
    {'name': '等待条件', 'mapping': 'wait_until', 'description': '等待条件：load, domcontentloaded, networkidle'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
])
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
            
            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "wait_until": wait_until,
                    "operation": "go_back"
                }
            }
            
        except Exception as e:
            logger.error(f"浏览器后退失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="浏览器后退失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('前进', [
    {'name': '等待条件', 'mapping': 'wait_until', 'description': '等待条件：load, domcontentloaded, networkidle'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
])
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
            
            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "wait_until": wait_until,
                    "operation": "go_forward"
                }
            }
            
        except Exception as e:
            logger.error(f"浏览器前进失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="浏览器前进失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('获取页面标题', [])
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
            
            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": title,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "title": title,
                    "operation": "get_page_title"
                }
            }
            
        except Exception as e:
            logger.error(f"获取页面标题失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="获取页面标题失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('获取当前地址', [])
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
            
            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": url,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "url": url,
                    "operation": "get_current_url"
                }
            }
            
        except Exception as e:
            logger.error(f"获取当前地址失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="获取当前地址失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
