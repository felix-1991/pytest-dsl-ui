"""浏览器操作关键字

提供浏览器启动、关闭、页面切换等基础功能。
"""

import logging
import yaml
import allure
import time as time_module

from pytest_dsl.core.keyword_manager import keyword_manager
from ..core.browser_manager import browser_manager

logger = logging.getLogger(__name__)


@keyword_manager.register('启动浏览器', [
    {'name': '浏览器', 'mapping': 'browser_type',
        'description': '浏览器类型：chromium, firefox, webkit', 'default': 'chromium'},
    {'name': '无头模式', 'mapping': 'headless',
     'description': '是否以无头模式运行', 'default': False},
    {'name': '慢动作', 'mapping': 'slow_mo',
     'description': '操作间隔时间（毫秒），用于调试', 'default': 0},
    {'name': '配置', 'mapping': 'config',
     'description': '浏览器启动配置（YAML格式）', 'default': '{}'},
    {'name': '视口宽度', 'mapping': 'width', 'description': '浏览器视口宽度'},
    {'name': '视口高度', 'mapping': 'height', 'description': '浏览器视口高度'},
    {'name': '忽略证书错误', 'mapping': 'ignore_https_errors',
     'description': '是否忽略HTTPS证书错误', 'default': True},
])
def launch_browser(**kwargs):
    """启动浏览器

    Args:
        browser_type: 浏览器类型
        headless: 是否无头模式
        slow_mo: 慢动作间隔
        config: 配置字符串
        width: 视口宽度
        height: 视口高度
        ignore_https_errors: 是否忽略HTTPS证书错误

    Returns:
        dict: 包含浏览器ID和相关信息的字典
    """
    browser_type = kwargs.get('browser_type', 'chromium')
    headless = kwargs.get('headless', True)
    slow_mo = kwargs.get('slow_mo', 0)
    config_str = kwargs.get('config', '{}')
    width = kwargs.get('width')
    height = kwargs.get('height')
    ignore_https_errors = kwargs.get('ignore_https_errors', True)
    context = kwargs.get('context')

    with allure.step(f"启动浏览器: {browser_type}"):
        try:
            # 解析配置
            if isinstance(config_str, str):
                try:
                    config = yaml.safe_load(
                        config_str) if config_str.strip() else {}
                except yaml.YAMLError:
                    # 尝试作为JSON解析
                    import json
                    config = json.loads(
                        config_str) if config_str.strip() else {}
            else:
                config = config_str or {}

            # 设置基本配置
            launch_config = {
                'headless': headless,
                'slow_mo': slow_mo,
                **config
            }

            # 启动浏览器
            browser_id = browser_manager.launch_browser(
                browser_type, **launch_config)

            # 创建默认上下文
            context_config = {}
            if width and height:
                context_config['viewport'] = {
                    'width': int(width), 'height': int(height)}
            elif 'viewport' in config:
                context_config['viewport'] = config['viewport']

            # 添加忽略HTTPS证书错误的配置
            if ignore_https_errors:
                context_config['ignore_https_errors'] = True

            context_id = browser_manager.create_context(
                browser_id, **context_config)

            # 创建默认页面
            page_id = browser_manager.create_page(context_id)

            result = {
                'browser_id': browser_id,
                'context_id': context_id,
                'page_id': page_id
            }

            # 在测试上下文中保存浏览器信息
            if context:
                context.set('current_browser_id', browser_id)
                context.set('current_context_id', context_id)
                context.set('current_page_id', page_id)

            allure.attach(
                f"浏览器类型: {browser_type}\n"
                f"浏览器ID: {browser_id}\n"
                f"上下文ID: {context_id}\n"
                f"页面ID: {page_id}\n"
                f"无头模式: {headless}\n"
                f"忽略HTTPS证书错误: {ignore_https_errors}",
                name="浏览器启动信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"浏览器启动成功: {browser_type} (ID: {browser_id})")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": result,
                "captures": {
                    'current_browser_id': browser_id,
                    'current_context_id': context_id,
                    'current_page_id': page_id
                },
                "session_state": {},
                "metadata": {
                    "browser_type": browser_type,
                    "browser_id": browser_id,
                    "ignore_https_errors": ignore_https_errors,
                    "operation": "launch_browser"
                }
            }

        except Exception as e:
            logger.error(f"启动浏览器失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="浏览器启动失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('关闭浏览器', [
    {'name': '浏览器ID', 'mapping': 'browser_id',
        'description': '要关闭的浏览器ID，如果不指定则关闭当前浏览器'},
])
def close_browser(**kwargs):
    """关闭浏览器

    Args:
        browser_id: 浏览器ID

    Returns:
        dict: 操作结果
    """
    browser_id = kwargs.get('browser_id')
    context = kwargs.get('context')

    with allure.step("关闭浏览器"):
        try:
            # 如果没有指定浏览器ID，从上下文获取
            if not browser_id and context:
                browser_id = context.get('current_browser_id')

            browser_manager.close_browser(browser_id)

            # 清理上下文中的浏览器信息
            if context:
                context.set('current_browser_id', None)
                context.set('current_context_id', None)
                context.set('current_page_id', None)

            allure.attach(
                f"已关闭浏览器: {browser_id or '当前浏览器'}",
                name="浏览器关闭信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"浏览器关闭成功: {browser_id or '当前浏览器'}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "browser_id": browser_id,
                    "operation": "close_browser"
                }
            }

        except Exception as e:
            logger.error(f"关闭浏览器失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="浏览器关闭失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('新建页面', [
    {'name': '上下文ID', 'mapping': 'context_id',
        'description': '浏览器上下文ID，如果不指定则使用当前上下文'},
])
def new_page(**kwargs):
    """新建页面

    Args:
        context_id: 上下文ID

    Returns:
        dict: 包含新页面ID的字典
    """
    context_id = kwargs.get('context_id')
    test_context = kwargs.get('context')

    with allure.step("新建页面"):
        try:
            # 如果没有指定上下文ID，从测试上下文获取
            if not context_id and test_context:
                context_id = test_context.get('current_context_id')

            page_id = browser_manager.create_page(context_id)

            # 更新测试上下文中的当前页面
            if test_context:
                test_context.set('current_page_id', page_id)

            allure.attach(
                f"新页面ID: {page_id}\n上下文ID: {context_id}",
                name="新建页面信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"新建页面成功: {page_id}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": page_id,
                "captures": {
                    'current_page_id': page_id
                },
                "session_state": {},
                "metadata": {
                    "page_id": page_id,
                    "context_id": context_id,
                    "operation": "new_page"
                }
            }

        except Exception as e:
            logger.error(f"新建页面失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="新建页面失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('切换页面', [
    {'name': '页面ID', 'mapping': 'page_id', 'description': '要切换到的页面ID'},
])
def switch_page(**kwargs):
    """切换页面

    Args:
        page_id: 页面ID

    Returns:
        dict: 操作结果
    """
    page_id = kwargs.get('page_id')
    context = kwargs.get('context')

    with allure.step(f"切换页面: {page_id}"):
        try:
            browser_manager.switch_page(page_id)

            # 更新测试上下文中的当前页面
            if context:
                context.set('current_page_id', page_id)

            allure.attach(
                f"已切换到页面: {page_id}",
                name="页面切换信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"页面切换成功: {page_id}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": True,
                "captures": {
                    'current_page_id': page_id
                },
                "session_state": {},
                "metadata": {
                    "page_id": page_id,
                    "operation": "switch_page"
                }
            }

        except Exception as e:
            logger.error(f"切换页面失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="页面切换失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('设置等待超时', [
    {'name': '超时时间', 'mapping': 'timeout', 'description': '默认等待超时时间（秒）', 'default': 30},
])
def set_default_timeout(**kwargs):
    """设置默认等待超时时间

    Args:
        timeout: 超时时间（秒）

    Returns:
        dict: 操作结果
    """
    timeout = float(kwargs.get('timeout', 30))

    with allure.step(f"设置等待超时: {timeout}秒"):
        try:
            # 获取当前页面并设置超时
            page = browser_manager.get_current_page()
            from ..core.element_locator import ElementLocator
            locator = ElementLocator(page)
            locator.set_default_timeout(timeout)

            allure.attach(
                f"默认超时时间已设置为: {timeout}秒",
                name="超时设置信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"默认超时时间设置成功: {timeout}秒")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": timeout,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "timeout": timeout,
                    "operation": "set_default_timeout"
                }
            }

        except Exception as e:
            logger.error(f"设置超时时间失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="超时设置失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('等待', [
    {'name': '时间', 'mapping': 'time', 'description': '等待时间（秒）'},
])
def wait(**kwargs):
    """等待指定时间
    
    Args:
        time: 等待时间（秒）
        
    Returns:
        dict: 操作结果
    """
    wait_time = float(kwargs.get('time', 1))
    
    with allure.step(f"等待 {wait_time} 秒"):
        try:
            allure.attach(
                f"等待时间: {wait_time}秒",
                name="等待信息",
                attachment_type=allure.attachment_type.TEXT
            )
            
            time_module.sleep(wait_time)
            logger.info(f"等待完成: {wait_time}秒")
            
            return {
                "result": True,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "wait_time": wait_time,
                    "operation": "wait"
                }
            }
            
        except Exception as e:
            logger.error(f"等待失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="等待失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
