"""网络监听关键字

提供网络请求监听、响应内容获取、URL变化等待等功能。
这些关键字可以用于登录验证、API调用监控等场景。
"""

import logging
import re
import time
import allure
from typing import Optional, Dict, Any, List

from pytest_dsl.core.keyword_manager import keyword_manager
from ..core.browser_manager import browser_manager

logger = logging.getLogger(__name__)


class NetworkMonitor:
    """网络监控器

    用于监听和记录网络请求和响应
    """

    def __init__(self, page):
        self.page = page
        self.requests: List[Dict[str, Any]] = []
        self.responses: List[Dict[str, Any]] = []
        self.is_monitoring = False
        self._request_handler = None
        self._response_handler = None

    def start_monitoring(self):
        """开始监听网络请求"""
        if self.is_monitoring:
            return

        self.requests.clear()
        self.responses.clear()

        def on_request(request):
            request_data = {
                'url': request.url,
                'method': request.method,
                'headers': dict(request.headers),
                'post_data': request.post_data,
                'timestamp': self._get_timestamp()
            }
            self.requests.append(request_data)
            logger.debug(f"捕获请求: {request.method} {request.url}")

        def on_response(response):
            response_data = {
                'url': response.url,
                'status': response.status,
                'status_text': response.status_text,
                'headers': dict(response.headers),
                'timestamp': self._get_timestamp()
            }
            # 尝试获取响应内容
            try:
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    response_data['json'] = response.json()
                response_data['text'] = response.text()
            except Exception as e:
                logger.debug(f"无法获取响应内容: {str(e)}")
                response_data['text'] = None
                response_data['json'] = None

            self.responses.append(response_data)
            logger.debug(f"捕获响应: {response.status} {response.url}")

        self._request_handler = on_request
        self._response_handler = on_response

        self.page.on('request', self._request_handler)
        self.page.on('response', self._response_handler)
        self.is_monitoring = True
        logger.info("网络监听已开始")

    def stop_monitoring(self):
        """停止监听网络请求"""
        if not self.is_monitoring:
            return

        if self._request_handler:
            self.page.remove_listener('request', self._request_handler)
        if self._response_handler:
            self.page.remove_listener('response', self._response_handler)

        self.is_monitoring = False
        logger.info("网络监听已停止")

    def get_requests(
        self, url_pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取捕获的请求

        Args:
            url_pattern: URL匹配模式（正则表达式）

        Returns:
            List[Dict[str, Any]]: 匹配的请求列表
        """
        if not url_pattern:
            return self.requests.copy()

        pattern = re.compile(url_pattern)
        return [req for req in self.requests if pattern.search(req['url'], category='UI/网络')]

    def get_responses(
        self, url_pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取捕获的响应

        Args:
            url_pattern: URL匹配模式（正则表达式）

        Returns:
            List[Dict[str, Any]]: 匹配的响应列表
        """
        if not url_pattern:
            return self.responses.copy()

        pattern = re.compile(url_pattern)
        return [resp for resp in self.responses if pattern.search(resp['url'], category='UI/网络')]

    def _get_timestamp(self):
        """获取当前时间戳"""
        return time.time()


# 全局网络监控器实例
_network_monitors: Dict[str, NetworkMonitor] = {}


def _get_network_monitor() -> NetworkMonitor:
    """获取当前页面的网络监控器"""
    page = browser_manager.get_current_page()
    page_id = id(page)

    if page_id not in _network_monitors:
        _network_monitors[page_id] = NetworkMonitor(page)

    return _network_monitors[page_id]


@keyword_manager.register('开始网络监听', [
    {'name': '变量名', 'mapping': 'variable',
     'description': '保存监听器状态的变量名'},
], category='UI/网络')
def start_network_monitoring(**kwargs):
    """开始监听网络请求和响应

    Args:
        variable: 变量名

    Returns:
        dict: 操作结果
    """
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    with allure.step("开始网络监听"):
        try:
            monitor = _get_network_monitor()
            monitor.start_monitoring()

            # 保存到变量
            captures = {}
            if variable and context:
                context.set(variable, True)
                captures[variable] = True

            allure.attach(
                f"网络监听已开始\n"
                f"保存变量: {variable or '无'}",
                name="网络监听信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info("网络监听开始成功")

            # 保存到变量
            if variable and context:
                context.set(variable, True)

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"开始网络监听失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="网络监听失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('停止网络监听', [], category='UI/网络')
def stop_network_monitoring(**kwargs):
    """停止监听网络请求和响应

    Returns:
        dict: 操作结果
    """
    with allure.step("停止网络监听"):
        try:
            monitor = _get_network_monitor()
            monitor.stop_monitoring()

            allure.attach(
                "网络监听已停止",
                name="网络监听信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info("网络监听停止成功")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"停止网络监听失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="停止网络监听失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('获取网络请求', [
    {'name': 'URL模式', 'mapping': 'url_pattern',
     'description': '匹配URL的正则表达式模式'},
    {'name': '变量名', 'mapping': 'variable',
     'description': '保存请求列表的变量名'},
], category='UI/网络')
def get_network_requests(**kwargs):
    """获取捕获的网络请求

    Args:
        url_pattern: URL匹配模式（正则表达式）
        variable: 变量名

    Returns:
        dict: 包含请求列表的字典
    """
    url_pattern = kwargs.get('url_pattern')
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    with allure.step("获取网络请求"):
        try:
            monitor = _get_network_monitor()
            requests = monitor.get_requests(url_pattern)

            # 保存到变量
            captures = {}
            if variable and context:
                context.set(variable, requests)
                captures[variable] = requests

            # 输出数量信息到日志
            logger.info(f"获取到 {len(requests)} 个网络请求")

            allure.attach(
                f"URL模式: {url_pattern or '全部'}\n"
                f"请求数量: {len(requests)}\n"
                f"保存变量: {variable or '无'}\n"
                f"匹配的请求数量: {len(requests)} 个",
                name="网络请求统计信息",
                attachment_type=allure.attachment_type.TEXT
            )

            # 详细记录请求信息
            if requests:
                request_details = []
                for i, req in enumerate(requests):
                    request_details.append(
                        f"请求 {i+1}:\n"
                        f"  URL: {req['url']}\n"
                        f"  方法: {req['method']}\n"
                        f"  时间戳: {req['timestamp']}"
                    )

                allure.attach(
                    "\n\n".join(request_details),
                    name="请求详情",
                    attachment_type=allure.attachment_type.TEXT
                )

            logger.info(f"获取网络请求成功: {len(requests)} 个")

            # 保存到变量
            if variable and context:
                context.set(variable, requests)

            # 直接返回请求列表
            return requests

        except Exception as e:
            logger.error(f"获取网络请求失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="获取网络请求失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('获取网络响应', [
    {'name': 'URL模式', 'mapping': 'url_pattern',
     'description': '匹配URL的正则表达式模式'},
    {'name': '变量名', 'mapping': 'variable',
     'description': '保存响应列表的变量名'},
], category='UI/网络')
def get_network_responses(**kwargs):
    """获取捕获的网络响应

    Args:
        url_pattern: URL匹配模式（正则表达式）
        variable: 变量名

    Returns:
        dict: 包含响应列表的字典
    """
    url_pattern = kwargs.get('url_pattern')
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    with allure.step("获取网络响应"):
        try:
            monitor = _get_network_monitor()
            responses = monitor.get_responses(url_pattern)

            # 保存到变量
            captures = {}
            if variable and context:
                context.set(variable, responses)
                captures[variable] = responses

            # 输出数量信息到日志
            logger.info(f"获取到 {len(responses)} 个网络响应")

            allure.attach(
                f"URL模式: {url_pattern or '全部'}\n"
                f"响应数量: {len(responses)}\n"
                f"保存变量: {variable or '无'}\n"
                f"匹配的响应数量: {len(responses)} 个",
                name="网络响应统计信息",
                attachment_type=allure.attachment_type.TEXT
            )

            # 详细记录响应信息
            if responses:
                response_details = []
                for i, resp in enumerate(responses):
                    response_details.append(
                        f"响应 {i+1}:\n"
                        f"  URL: {resp['url']}\n"
                        f"  状态: {resp['status']} {resp['status_text']}\n"
                        f"  时间戳: {resp['timestamp']}"
                    )

                allure.attach(
                    "\n\n".join(response_details),
                    name="响应详情",
                    attachment_type=allure.attachment_type.TEXT
                )

            logger.info(f"获取网络响应成功: {len(responses)} 个")

            # 保存到变量
            if variable and context:
                context.set(variable, responses)

            # 直接返回响应列表
            return responses

        except Exception as e:
            logger.error(f"获取网络响应失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="获取网络响应失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('等待网络请求', [
    {'name': 'URL模式', 'mapping': 'url_pattern',
     'description': '匹配URL的正则表达式模式'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '变量名', 'mapping': 'variable',
     'description': '保存匹配请求的变量名'},
], category='UI/网络')
def wait_for_network_request(**kwargs):
    """等待特定的网络请求

    Args:
        url_pattern: URL匹配模式（正则表达式）
        timeout: 超时时间（秒）
        variable: 变量名

    Returns:
        dict: 包含匹配请求的字典
    """
    url_pattern = kwargs.get('url_pattern')
    timeout = kwargs.get('timeout', 30.0)
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    if not url_pattern:
        raise ValueError("URL模式参数不能为空")

    with allure.step(f"等待网络请求: {url_pattern}"):
        try:
            page = browser_manager.get_current_page()

            # 使用Playwright的expect_request方法
            timeout_ms = int(timeout * 1000)
            with page.expect_request(
                lambda req: re.search(url_pattern, req.url),
                timeout=timeout_ms
            ) as request_info:
                # 等待请求
                pass

            request = request_info.value

            # 构建请求数据
            request_data = {
                'url': request.url,
                'method': request.method,
                'headers': dict(request.headers),
                'post_data': request.post_data,
                'timestamp': time.time()
            }

            # 保存到变量
            captures = {}
            if variable and context:
                context.set(variable, request_data)
                captures[variable] = request_data

            allure.attach(
                f"URL模式: {url_pattern}\n"
                f"匹配URL: {request.url}\n"
                f"请求方法: {request.method}\n"
                f"超时时间: {timeout}秒\n"
                f"保存变量: {variable or '无'}",
                name="等待网络请求信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"等待网络请求成功: {request.url}")

            # 保存到变量
            if variable and context:
                context.set(variable, request_data)

            # 直接返回请求数据
            return request_data

        except Exception as e:
            logger.error(f"等待网络请求失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}\n"
                f"URL模式: {url_pattern}",
                name="等待网络请求失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('等待网络响应', [
    {'name': 'URL模式', 'mapping': 'url_pattern',
     'description': '匹配URL的正则表达式模式'},
    {'name': '状态码', 'mapping': 'status_code', 'description': '期望的HTTP状态码'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '变量名', 'mapping': 'variable',
     'description': '保存匹配响应的变量名'},
], category='UI/网络')
def wait_for_network_response(**kwargs):
    """等待特定的网络响应

    Args:
        url_pattern: URL匹配模式（正则表达式）
        status_code: 期望的HTTP状态码
        timeout: 超时时间（秒）
        variable: 变量名

    Returns:
        dict: 包含匹配响应的字典
    """
    url_pattern = kwargs.get('url_pattern')
    status_code = kwargs.get('status_code')
    timeout = kwargs.get('timeout', 30.0)
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    if not url_pattern:
        raise ValueError("URL模式参数不能为空")

    with allure.step(f"等待网络响应: {url_pattern}"):
        try:
            page = browser_manager.get_current_page()

            # 构建匹配条件
            def match_response(response):
                url_match = re.search(url_pattern, response.url)
                if not url_match:
                    return False

                if status_code is not None:
                    return response.status == int(status_code)

                return True

            # 使用Playwright的expect_response方法
            timeout_ms = int(timeout * 1000)
            with page.expect_response(
                match_response, timeout=timeout_ms
            ) as response_info:
                # 等待响应
                pass

            response = response_info.value

            # 构建响应数据
            response_data = {
                'url': response.url,
                'status': response.status,
                'status_text': response.status_text,
                'headers': dict(response.headers),
                'timestamp': time.time()
            }

            # 尝试获取响应内容
            try:
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    response_data['json'] = response.json()
                response_data['text'] = response.text()
            except Exception as e:
                logger.debug(f"无法获取响应内容: {str(e)}")
                response_data['text'] = None
                response_data['json'] = None

            # 保存到变量
            captures = {}
            if variable and context:
                context.set(variable, response_data)
                captures[variable] = response_data

            allure.attach(
                f"URL模式: {url_pattern}\n"
                f"匹配URL: {response.url}\n"
                f"响应状态: {response.status} {response.status_text}\n"
                f"期望状态码: {status_code or '任意'}\n"
                f"超时时间: {timeout}秒\n"
                f"保存变量: {variable or '无'}",
                name="等待网络响应信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"等待网络响应成功: {response.url}")

            # 保存到变量
            if variable and context:
                context.set(variable, response_data)

            # 直接返回响应数据
            return response_data

        except Exception as e:
            logger.error(f"等待网络响应失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}\n"
                f"URL模式: {url_pattern}\n"
                f"期望状态码: {status_code or '任意'}",
                name="等待网络响应失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('等待URL变化', [
    {'name': 'URL模式', 'mapping': 'url_pattern',
     'description': '期望的URL模式（正则表达式）'},
    {'name': '超时时间', 'mapping': 'timeout', 'description': '超时时间（秒）'},
    {'name': '变量名', 'mapping': 'variable', 'description': '保存新URL的变量名'},
], category='UI/网络')
def wait_for_url_change(**kwargs):
    """等待页面URL变化到指定模式

    Args:
        url_pattern: 期望的URL模式（正则表达式）
        timeout: 超时时间（秒）
        variable: 变量名

    Returns:
        dict: 包含新URL的字典
    """
    url_pattern = kwargs.get('url_pattern')
    timeout = kwargs.get('timeout', 30.0)
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    if not url_pattern:
        raise ValueError("URL模式参数不能为空")

    with allure.step(f"等待URL变化: {url_pattern}"):
        try:
            page = browser_manager.get_current_page()
            current_url = page.url

            # 使用Playwright的wait_for_url方法
            timeout_ms = int(timeout * 1000)
            page.wait_for_url(url_pattern, timeout=timeout_ms)

            new_url = page.url

            # 保存到变量
            captures = {}
            if variable and context:
                context.set(variable, new_url)
                captures[variable] = new_url

            allure.attach(
                f"URL模式: {url_pattern}\n"
                f"原始URL: {current_url}\n"
                f"新URL: {new_url}\n"
                f"超时时间: {timeout}秒\n"
                f"保存变量: {variable or '无'}",
                name="URL变化信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"URL变化等待成功: {current_url} -> {new_url}")

            # 保存到变量
            if variable and context:
                context.set(variable, new_url)

            # 直接返回新URL
            return new_url

        except Exception as e:
            logger.error(f"等待URL变化失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}\n"
                f"URL模式: {url_pattern}",
                name="等待URL变化失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('断言响应内容', [
    {'name': '响应数据', 'mapping': 'response_data',
     'description': '响应数据（变量名或字典）'},
    {'name': '断言类型', 'mapping': 'assertion_type',
     'description': '断言类型：status_code, json_path, text_contains'},
    {'name': '期望值', 'mapping': 'expected_value', 'description': '期望的值'},
    {'name': 'JSON路径', 'mapping': 'json_path',
     'description': 'JSON路径（用于json_path断言）'},
    {'name': '消息', 'mapping': 'message', 'description': '断言失败时的错误消息'},
], category='UI/网络')
def assert_response_content(**kwargs):
    """断言响应内容

    Args:
        response_data: 响应数据
        assertion_type: 断言类型
        expected_value: 期望值
        json_path: JSON路径
        message: 自定义错误消息

    Returns:
        dict: 操作结果
    """
    response_data = kwargs.get('response_data')
    assertion_type = kwargs.get('assertion_type')
    expected_value = kwargs.get('expected_value')
    json_path = kwargs.get('json_path')
    message = kwargs.get('message')
    context = kwargs.get('context')

    if not response_data or not assertion_type:
        raise ValueError("响应数据和断言类型参数不能为空")

    # 如果response_data是变量名，从上下文获取
    if isinstance(response_data, str) and context:
        response_data = context.get(response_data)

    if not isinstance(response_data, dict):
        raise ValueError("响应数据必须是字典格式")

    with allure.step(f"断言响应内容: {assertion_type}"):
        try:
            result = False
            actual_value = None

            if assertion_type == 'status_code':
                actual_value = response_data.get('status')
                result = actual_value == int(expected_value)

            elif assertion_type == 'json_path':
                if not json_path:
                    raise ValueError("JSON路径断言需要指定json_path参数")

                json_data = response_data.get('json')
                if json_data is None:
                    raise ValueError("响应数据中没有JSON内容")

                # 简单的JSON路径解析（支持点号分隔的路径）
                actual_value = json_data
                for key in json_path.split('.'):
                    if isinstance(actual_value, dict):
                        actual_value = actual_value.get(key)
                    else:
                        actual_value = None
                        break

                result = actual_value == expected_value

            elif assertion_type == 'text_contains':
                text_content = response_data.get('text', '')
                actual_value = text_content
                result = str(expected_value) in text_content

            else:
                raise ValueError(f"不支持的断言类型: {assertion_type}")

            if not result:
                error_msg = (
                    message or
                    f"响应内容断言失败: 期望 {expected_value}, "
                    f"实际 {actual_value}"
                )
                raise AssertionError(error_msg)

            allure.attach(
                f"断言类型: {assertion_type}\n"
                f"期望值: {expected_value}\n"
                f"实际值: {actual_value}\n"
                f"JSON路径: {json_path or '无'}\n"
                f"断言结果: 通过",
                name="响应内容断言",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"响应内容断言通过: {assertion_type}")

            # 直接返回断言结果
            return True

        except Exception as e:
            logger.error(f"响应内容断言失败: {str(e)}")
            allure.attach(
                f"断言类型: {assertion_type}\n"
                f"期望值: {expected_value}\n"
                f"实际值: {actual_value}\n"
                f"错误信息: {str(e)}",
                name="响应内容断言失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
