import json
import logging
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin
import allure

logger = logging.getLogger(__name__)


class BrowserHTTPClient:
    """基于浏览器上下文的HTTP客户端类

    通过Playwright的APIRequestContext实现API测试，
    可以继承浏览器的认证状态、Cookie等会话信息
    """

    def __init__(self,
                 name: str = "default",
                 browser_context=None,
                 base_url: str = "",
                 headers: Dict[str, str] = None,
                 timeout: int = 30,
                 ignore_https_errors: bool = False,
                 extra_http_headers: Dict[str, str] = None):
        """初始化浏览器HTTP客户端

        Args:
            name: 客户端名称
            browser_context: Playwright浏览器上下文
            base_url: 基础URL
            headers: 默认请求头
            timeout: 默认超时时间(秒)
            ignore_https_errors: 是否忽略HTTPS错误
            extra_http_headers: 额外的HTTP头
        """
        self.name = name
        self.browser_context = browser_context
        self.base_url = base_url
        self.default_headers = headers or {}
        self.timeout = timeout * 1000  # Playwright使用毫秒
        self.ignore_https_errors = ignore_https_errors
        self.extra_http_headers = extra_http_headers or {}

        # 获取API请求上下文
        self._api_request_context = None
        self._init_api_request_context()

    def _init_api_request_context(self):
        """初始化API请求上下文"""
        if self.browser_context:
            # 使用浏览器上下文的request对象，这样可以继承浏览器的会话状态
            self._api_request_context = self.browser_context.request
        else:
            raise ValueError("需要提供有效的浏览器上下文")

    def make_request(self, method: str, url: str, **request_kwargs) -> 'BrowserResponse':
        """发送HTTP请求

        Args:
            method: HTTP方法
            url: 请求URL
            **request_kwargs: 请求参数

        Returns:
            BrowserResponse: 包装的响应对象
        """
        # 构建完整URL
        if not url.startswith(('http://', 'https://')):
            url = urljoin(self.base_url, url.lstrip('/'))

        # 合并请求头
        headers = {}
        headers.update(self.default_headers)
        headers.update(self.extra_http_headers)
        if 'headers' in request_kwargs:
            headers.update(request_kwargs['headers'])

        # 构建Playwright请求参数
        playwright_kwargs = {
            'timeout': request_kwargs.get('timeout', self.timeout),
            'ignore_https_errors': request_kwargs.get('ignore_https_errors', self.ignore_https_errors)
        }

        # 添加请求头
        if headers:
            playwright_kwargs['headers'] = headers

        # 处理查询参数
        if 'params' in request_kwargs and request_kwargs['params']:
            playwright_kwargs['params'] = request_kwargs['params']

        # 处理请求体
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            if 'json' in request_kwargs:
                playwright_kwargs['data'] = request_kwargs['json']
                if 'Content-Type' not in headers:
                    headers['Content-Type'] = 'application/json'
            elif 'data' in request_kwargs:
                if isinstance(request_kwargs['data'], dict):
                    # 表单数据
                    playwright_kwargs['form'] = request_kwargs['data']
                else:
                    # 原始数据
                    playwright_kwargs['data'] = request_kwargs['data']

        # 处理文件上传
        if 'files' in request_kwargs:
            # Playwright处理文件上传的方式
            playwright_kwargs['multipart'] = request_kwargs['files']

        # 记录请求详情
        self._log_request_to_allure(method, url, playwright_kwargs)

        try:
            # 发送请求
            if method.upper() == 'GET':
                response = self._api_request_context.get(
                    url, **playwright_kwargs)
            elif method.upper() == 'POST':
                response = self._api_request_context.post(
                    url, **playwright_kwargs)
            elif method.upper() == 'PUT':
                response = self._api_request_context.put(
                    url, **playwright_kwargs)
            elif method.upper() == 'DELETE':
                response = self._api_request_context.delete(
                    url, **playwright_kwargs)
            elif method.upper() == 'PATCH':
                response = self._api_request_context.patch(
                    url, **playwright_kwargs)
            elif method.upper() == 'HEAD':
                response = self._api_request_context.head(
                    url, **playwright_kwargs)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            # 包装响应对象
            browser_response = BrowserResponse(response)

            # 记录响应详情
            self._log_response_to_allure(browser_response)

            return browser_response

        except Exception as e:
            # 记录请求异常
            error_message = f"请求异常: {str(e)}"
            allure.attach(
                error_message,
                name=f"浏览器HTTP请求失败: {method} {url}",
                attachment_type=allure.attachment_type.TEXT
            )
            raise ValueError(f"浏览器HTTP请求失败: {str(e)}") from e

    def _log_request_to_allure(self, method: str, url: str, request_kwargs: Dict[str, Any]) -> None:
        """使用Allure记录请求信息"""
        request_summary = f"{method} {url}"
        request_details = [f"Method: {method}", f"URL: {url}"]

        # 添加请求头
        if "headers" in request_kwargs and request_kwargs["headers"]:
            safe_headers = {}
            for key, value in request_kwargs["headers"].items():
                if key.lower() in ["authorization", "x-api-key", "token", "api-key"]:
                    safe_headers[key] = "***REDACTED***"
                else:
                    safe_headers[key] = value
            request_details.append("Headers:")
            for key, value in safe_headers.items():
                request_details.append(f"  {key}: {value}")

        # 添加查询参数
        if "params" in request_kwargs and request_kwargs["params"]:
            request_details.append("Query Parameters:")
            for key, value in request_kwargs["params"].items():
                request_details.append(f"  {key}: {value}")

        # 添加请求体
        if "data" in request_kwargs and request_kwargs["data"]:
            request_details.append("JSON Body:")
            try:
                if isinstance(request_kwargs["data"], (dict, list)):
                    request_details.append(json.dumps(
                        request_kwargs["data"], indent=2, ensure_ascii=False))
                else:
                    request_details.append(str(request_kwargs["data"]))
            except:
                request_details.append(str(request_kwargs["data"]))

        # 添加表单数据
        if "form" in request_kwargs and request_kwargs["form"]:
            request_details.append("Form Data:")
            for key, value in request_kwargs["form"].items():
                request_details.append(f"  {key}: {value}")

        # 记录到Allure
        allure.attach(
            "\n".join(request_details),
            name=f"浏览器HTTP请求: {request_summary}",
            attachment_type=allure.attachment_type.TEXT
        )

    def _log_response_to_allure(self, response: 'BrowserResponse') -> None:
        """使用Allure记录响应信息"""
        response_summary = f"{response.status_code} ({response.elapsed_ms:.2f}ms)"
        response_details = [
            f"Status: {response.status_code} {response.status_text}",
            f"Response Time: {response.elapsed_ms:.2f}ms"
        ]

        # 添加响应头
        response_details.append("Headers:")
        for key, value in response.headers.items():
            response_details.append(f"  {key}: {value}")

        # 添加响应体
        response_details.append("Body:")
        try:
            body_text = response.text
            if response.is_json():
                response_details.append(json.dumps(
                    response.json(), indent=2, ensure_ascii=False))
            elif len(body_text) < 10240:  # 限制大小
                response_details.append(body_text)
            else:
                response_details.append(f"<{len(body_text)} 字符>")
        except Exception as e:
            response_details.append(f"<解析响应体错误: {str(e)}>")

        # 记录到Allure
        allure.attach(
            "\n".join(response_details),
            name=f"浏览器HTTP响应: {response_summary}",
            attachment_type=allure.attachment_type.TEXT
        )

    def close(self) -> None:
        """关闭客户端"""
        # Playwright的APIRequestContext会随浏览器上下文一起关闭
        pass


class BrowserResponse:
    """浏览器响应包装类

    提供与requests.Response兼容的接口
    """

    def __init__(self, playwright_response):
        """初始化响应包装器

        Args:
            playwright_response: Playwright的APIResponse对象
        """
        self._response = playwright_response
        self._text = None
        self._json = None

    @property
    def status_code(self) -> int:
        """获取状态码"""
        return self._response.status

    @property
    def status_text(self) -> str:
        """获取状态文本"""
        return self._response.status_text

    @property
    def headers(self) -> Dict[str, str]:
        """获取响应头"""
        return dict(self._response.headers)

    @property
    def url(self) -> str:
        """获取请求URL"""
        return self._response.url

    @property
    def text(self) -> str:
        """获取响应文本"""
        if self._text is None:
            try:
                self._text = self._response.text()
            except Exception as e:
                logger.warning(f"获取响应文本失败: {str(e)}")
                self._text = ""
        return self._text

    @property
    def elapsed_ms(self) -> float:
        """获取响应时间（毫秒）"""
        # 如果有设置响应时间属性，返回它；否则返回0
        return getattr(self, '_elapsed_ms', 0.0)

    def json(self) -> Any:
        """解析JSON响应"""
        if self._json is None:
            try:
                self._json = self._response.json()
            except Exception as e:
                raise ValueError(f"响应不是有效的JSON格式: {str(e)}")
        return self._json

    def is_json(self) -> bool:
        """判断响应是否是JSON格式"""
        content_type = self.headers.get('content-type', '')
        return 'application/json' in content_type.lower()

    @property
    def ok(self) -> bool:
        """判断请求是否成功"""
        return 200 <= self.status_code < 300


class BrowserHTTPClientManager:
    """浏览器HTTP客户端管理器

    管理多个浏览器HTTP客户端实例
    """

    def __init__(self):
        """初始化客户端管理器"""
        self._clients: Dict[str, BrowserHTTPClient] = {}

    def create_client(self, config: Dict[str, Any], browser_context=None) -> BrowserHTTPClient:
        """从配置创建客户端

        Args:
            config: 客户端配置
            browser_context: 浏览器上下文

        Returns:
            BrowserHTTPClient实例
        """
        name = config.get("name", "default")
        client = BrowserHTTPClient(
            name=name,
            browser_context=browser_context,
            base_url=config.get("base_url", ""),
            headers=config.get("headers", {}),
            timeout=config.get("timeout", 30),
            ignore_https_errors=config.get("ignore_https_errors", False),
            extra_http_headers=config.get("extra_http_headers", {})
        )
        return client

    def get_client(self, name: str = "default", browser_context=None, config: Dict[str, Any] = None) -> BrowserHTTPClient:
        """获取或创建客户端

        Args:
            name: 客户端名称
            browser_context: 浏览器上下文
            config: 客户端配置

        Returns:
            BrowserHTTPClient实例
        """
        # 生成客户端键名，包含浏览器上下文ID以确保唯一性
        context_id = id(browser_context) if browser_context else "default"
        client_key = f"{name}_{context_id}"

        # 如果客户端已存在，直接返回
        if client_key in self._clients:
            return self._clients[client_key]

        # 创建新客户端
        if not config:
            config = {"name": name}

        if not browser_context:
            raise ValueError("必须提供浏览器上下文")

        client = self.create_client(config, browser_context)
        self._clients[client_key] = client
        return client

    def close_client(self, name: str, browser_context=None) -> None:
        """关闭指定的客户端

        Args:
            name: 客户端名称
            browser_context: 浏览器上下文
        """
        context_id = id(browser_context) if browser_context else "default"
        client_key = f"{name}_{context_id}"

        if client_key in self._clients:
            self._clients[client_key].close()
            del self._clients[client_key]

    def close_all(self) -> None:
        """关闭所有客户端"""
        for client in self._clients.values():
            client.close()
        self._clients.clear()


# 创建全局浏览器HTTP客户端管理器实例
browser_http_client_manager = BrowserHTTPClientManager()
