import json
import logging
import re
import time
from typing import Dict, List, Any, Tuple, Optional
import allure

from .browser_http_client import browser_http_client_manager, BrowserResponse

logger = logging.getLogger(__name__)

# 从pytest-dsl复用的常量定义
COMPARISON_OPERATORS = {
    "eq", "neq", "lt", "lte", "gt", "gte", "in", "not_in", "matches",
    "contains", "not_contains", "startswith", "endswith"
}

ASSERTION_TYPES = {
    "exists", "not_exists", "contains", "not_contains", "startswith",
    "endswith", "matches", "type", "length", "schema", "value"
}

DUAL_PURPOSE = {
    "contains", "not_contains", "matches", "in", "not_in", "startswith",
    "endswith"
}


class BrowserHTTPRequest:
    """基于浏览器的HTTP请求处理类

    负责处理基于浏览器上下文的HTTP请求、响应捕获和断言
    设计上与pytest-dsl的HTTPRequest保持一致
    """

    def __init__(self, config: Dict[str, Any], client_name: str = "default",
                 browser_context=None, session_name: str = None):
        """初始化浏览器HTTP请求

        Args:
            config: 请求配置
            client_name: 客户端名称
            browser_context: 浏览器上下文
            session_name: 会话名称（保持兼容性，实际由浏览器上下文管理）
        """
        self.config = config
        self.client_name = client_name
        self.browser_context = browser_context
        self.session_name = session_name
        self.response = None
        self.captured_values = {}
        self._start_time = None

    def execute(self, disable_auth: bool = False) -> BrowserResponse:
        """执行HTTP请求

        Args:
            disable_auth: 是否禁用认证（对浏览器上下文的影响有限）

        Returns:
            BrowserResponse对象
        """
        # 获取浏览器HTTP客户端
        client_config = self.config.get('client_config', {})
        client = browser_http_client_manager.get_client(
            name=self.client_name,
            browser_context=self.browser_context,
            config=client_config
        )

        if client is None:
            error_message = f"无法获取浏览器HTTP客户端: {self.client_name}"
            allure.attach(
                error_message,
                name="浏览器HTTP客户端错误",
                attachment_type=allure.attachment_type.TEXT
            )
            raise ValueError(error_message)

        # 提取请求参数
        method = self.config.get('method', 'GET').upper()
        url = self.config.get('url', '')

        request_config = self.config.get('request', {})

        # 构建请求参数
        request_kwargs = {
            'params': request_config.get('params'),
            'headers': request_config.get('headers'),
            'json': request_config.get('json'),
            'data': request_config.get('data'),
            'files': request_config.get('files'),
            'timeout': request_config.get('timeout'),
            'ignore_https_errors': request_config.get('ignore_https_errors')
        }

        # 过滤掉None值
        request_kwargs = {k: v for k,
                          v in request_kwargs.items() if v is not None}

        try:
            # 记录开始时间
            self._start_time = time.time()

            # 发送请求
            self.response = client.make_request(method, url, **request_kwargs)

            # 计算响应时间
            if self._start_time:
                elapsed_ms = (time.time() - self._start_time) * 1000
                # 为响应对象添加响应时间属性
                self.response._elapsed_ms = elapsed_ms

            # 处理捕获
            try:
                self.process_captures()
            except Exception as capture_error:
                if (not hasattr(self, 'captured_values') or
                        self.captured_values is None):
                    self.captured_values = {}
                logger.warning(f"变量捕获处理失败: {str(capture_error)}")
                allure.attach(
                    f"变量捕获处理失败: {str(capture_error)}",
                    name="变量捕获警告",
                    attachment_type=allure.attachment_type.TEXT
                )

            return self.response

        except Exception as e:
            error_message = f"浏览器HTTP请求执行错误: {str(e)}"
            allure.attach(
                error_message,
                name=f"浏览器HTTP请求失败: {method} {url}",
                attachment_type=allure.attachment_type.TEXT
            )
            raise ValueError(error_message) from e

    def process_captures(self) -> Dict[str, Any]:
        """处理响应捕获

        复用pytest-dsl的捕获逻辑，适配浏览器响应格式

        Returns:
            捕获的值字典
        """
        if self.response is None:
            raise ValueError("需要先执行请求才能捕获响应")

        captures_config = self.config.get('captures', {})

        for var_name, capture_spec in captures_config.items():
            if not isinstance(capture_spec, list):
                raise ValueError(f"无效的捕获规格: {var_name}: {capture_spec}")

            try:
                extractor_type = capture_spec[0]
                extraction_path = capture_spec[1] if len(
                    capture_spec) > 1 else None

                # 检查是否有length参数
                is_length_capture = False
                if len(capture_spec) > 2 and capture_spec[2] == "length":
                    is_length_capture = True
                    default_value = capture_spec[3] if len(
                        capture_spec) > 3 else None
                else:
                    default_value = capture_spec[2] if len(
                        capture_spec) > 2 else None

                # 提取值
                captured_value = self._extract_value(
                    extractor_type, extraction_path, default_value)

                # 特殊处理length
                if is_length_capture:
                    try:
                        original_value = captured_value
                        captured_value = len(captured_value)

                        allure.attach(
                            f"变量名: {var_name}\n提取器: {extractor_type}\n路径: {extraction_path}\n原始值: {str(original_value)}\n长度: {captured_value}",
                            name=f"捕获长度: {var_name}",
                            attachment_type=allure.attachment_type.TEXT
                        )
                    except Exception as e:
                        error_msg = (
                            f"无法计算长度: {type(e).__name__}: {str(e)}\n"
                            f"类型: {type(original_value).__name__}\n"
                            f"值: {original_value}"
                        )
                        allure.attach(
                            error_msg,
                            name=f"长度计算失败: {extractor_type} {extraction_path}",
                            attachment_type=allure.attachment_type.TEXT
                        )
                        raise ValueError(
                            f"断言类型'length'无法应用于值 '{original_value}': {str(e)}")
                else:
                    allure.attach(
                        f"变量名: {var_name}\n提取器: {extractor_type}\n路径: {extraction_path}\n提取值: {str(captured_value)}",
                        name=f"捕获变量: {var_name}",
                        attachment_type=allure.attachment_type.TEXT
                    )

                self.captured_values[var_name] = captured_value

            except Exception as e:
                error_msg = (
                    f"变量捕获失败: {var_name}\n"
                    f"捕获规格: {capture_spec}\n"
                    f"错误: {type(e).__name__}: {str(e)}"
                )
                allure.attach(
                    error_msg,
                    name=f"变量捕获失败: {var_name}",
                    attachment_type=allure.attachment_type.TEXT
                )
                self.captured_values[var_name] = None

        return self.captured_values

    def process_asserts(self, specific_asserts=None, index_mapping=None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """处理响应断言

        复用pytest-dsl的断言逻辑，适配浏览器响应格式

        Args:
            specific_asserts: 指定要处理的断言列表
            index_mapping: 索引映射字典

        Returns:
            断言结果列表和失败需重试的断言列表
        """
        if self.response is None:
            raise ValueError("需要先执行请求才能进行断言")

        asserts_config = self.config.get('asserts', [])
        assert_results = []
        failed_retryable_assertions = []
        failed_assertions = []

        # 处理断言重试配置（复用pytest-dsl逻辑）
        retry_assertions_config = self.config.get('retry_assertions', {})
        retry_config = self.config.get('retry', {})
        global_retry_enabled = bool(retry_config)

        global_retry_count = retry_assertions_config.get(
            'count', retry_config.get('count', 3))
        global_retry_interval = retry_assertions_config.get(
            'interval', retry_config.get('interval', 1))

        retry_all_assertions = retry_assertions_config.get(
            'all', global_retry_enabled)
        retry_assertion_indices = retry_assertions_config.get('indices', [])
        specific_assertion_configs = retry_assertions_config.get(
            'specific', {})

        process_asserts = specific_asserts if specific_asserts is not None else asserts_config

        for assertion_idx, assertion in enumerate(process_asserts):
            if not isinstance(assertion, list) or len(assertion) < 2:
                raise ValueError(f"无效的断言配置: {assertion}")

            # 提取断言参数
            extractor_type = assertion[0]
            original_idx = index_mapping.get(
                assertion_idx, assertion_idx) if index_mapping else assertion_idx

            # 判断该断言是否应该重试
            is_retryable = False
            assertion_retry_count = global_retry_count
            assertion_retry_interval = global_retry_interval

            original_idx_str = str(original_idx)
            if original_idx_str in specific_assertion_configs or original_idx in specific_assertion_configs:
                spec_config = specific_assertion_configs.get(
                    original_idx_str) or specific_assertion_configs.get(original_idx)
                is_retryable = True
                if isinstance(spec_config, dict):
                    if 'count' in spec_config:
                        assertion_retry_count = spec_config['count']
                    if 'interval' in spec_config:
                        assertion_retry_interval = spec_config['interval']
            elif original_idx in retry_assertion_indices:
                is_retryable = True
            elif retry_all_assertions:
                is_retryable = True

            # 解析断言参数（直接内联，与pytest-dsl保持完全一致）
            if len(assertion) == 2:  # 简单存在性断言 ["header", "Location"]
                extraction_path = assertion[1]
                assertion_type = "exists"
                expected_value = None
                compare_operator = "eq"  # 默认比较操作符
            elif len(assertion) == 3:  # 简单断言 ["status", "eq", 200]
                # 检查第二个元素是否是操作符或二者兼用的断言类型
                if assertion[1] in COMPARISON_OPERATORS or assertion[1] in DUAL_PURPOSE:
                    # 这是操作符格式的断言 ["status", "eq", 200]
                    extraction_path = None if extractor_type in [
                        "status", "body", "response_time"] else assertion[1]

                    # 特殊处理二者兼用的断言类型
                    if assertion[1] in DUAL_PURPOSE:
                        if extractor_type in ["jsonpath", "body", "header"]:
                            # 当提取器是jsonpath/body/header时，将contains当作断言类型处理
                            assertion_type = assertion[1]
                            compare_operator = assertion[1]  # 匹配操作符和断言类型
                        else:
                            # 否则当作操作符处理
                            assertion_type = "value"
                            compare_operator = assertion[1]
                    else:
                        assertion_type = "value"  # 标记为值比较
                        compare_operator = assertion[1]

                    expected_value = assertion[2]  # 预期值
                else:
                    # 这可能是断言类型格式 ["jsonpath", "$.id", "exists"] 或者是简化的长度断言 ["body", "length", 10]
                    extraction_path = assertion[1]
                    potential_assertion_type = assertion[2]

                    # 特殊处理：如果第二个参数是"length"，第三个参数是数字，这是简化的长度断言
                    if extraction_path == "length" and isinstance(potential_assertion_type, (int, float)):
                        # 这是 ["body", "length", 10] 格式的长度断言
                        extraction_path = None  # body提取器不需要路径
                        assertion_type = "length"
                        compare_operator = "eq"
                        expected_value = potential_assertion_type
                    else:
                        # 这是标准的断言类型格式 ["jsonpath", "$.id", "exists"]
                        assertion_type = potential_assertion_type

                        # 特殊处理schema断言，因为schema值可能是字典
                        if assertion_type == "schema" or isinstance(assertion_type, dict):
                            if isinstance(assertion_type, dict):
                                # 这是 ["body", "schema", {schema_dict}] 格式
                                assertion_type = "schema"
                                expected_value = potential_assertion_type
                                compare_operator = "schema"
                                extraction_path = None  # body提取器不需要路径
                            else:
                                # 这是 ["jsonpath", "$.data", "schema"] 格式，需要在4参数中处理
                                expected_value = None
                                compare_operator = assertion_type
                        else:
                            # 检查断言类型是否有效
                            if assertion_type not in ASSERTION_TYPES:
                                raise ValueError(
                                    f"不支持的断言类型: {assertion_type} 在 {assertion}")

                            # 检查此断言类型是否需要预期值
                            if assertion_type not in ["exists", "not_exists"]:
                                # 特殊处理类型断言，它确实需要一个值但在这种格式中没有提供
                                if assertion_type == "type":
                                    raise ValueError(
                                        f"断言类型 'type' 需要预期值(string/number/boolean/array/object/null)，但未提供: {assertion}")
                                # 断言类型作为操作符
                                expected_value = None
                                compare_operator = assertion_type  # 使用断言类型作为操作符
                            else:
                                expected_value = None
                                compare_operator = assertion_type  # 存在性断言的操作符就是断言类型本身
            # 带操作符的断言 ["jsonpath", "$.id", "eq", 1] 或特殊断言 ["jsonpath", "$.type", "type", "string"] 或长度断言 ["body", "length", "gt", 50]
            elif len(assertion) == 4:
                extraction_path = assertion[1]

                # 特殊处理长度断言：["body", "length", "gt", 50]
                if extraction_path == "length" and assertion[2] in COMPARISON_OPERATORS:
                    # 这是4参数的长度断言格式
                    extraction_path = None  # body提取器不需要路径
                    assertion_type = "length"
                    compare_operator = assertion[2]  # 比较操作符
                    expected_value = assertion[3]  # 预期长度值
                # 检查第三个元素是否是操作符
                elif assertion[2] in COMPARISON_OPERATORS or assertion[2] in DUAL_PURPOSE:
                    # 这是操作符形式的断言
                    assertion_type = "value"  # 标记为值比较
                    compare_operator = assertion[2]  # 比较操作符
                    expected_value = assertion[3]  # 预期值
                else:
                    # 检查断言类型是否有效
                    if assertion[2] not in ASSERTION_TYPES:
                        raise ValueError(
                            f"不支持的断言类型: {assertion[2]} 在 {assertion}")

                    # 其他类型的断言，比如特殊断言
                    assertion_type = assertion[2]

                    # 根据断言类型决定如何处理操作符和期望值
                    if assertion_type == "length":
                        # 对于4参数的长度断言，第4个参数是期望值，默认使用eq比较
                        compare_operator = "eq"  # 默认使用相等比较
                        expected_value = assertion[3]  # 预期长度值
                    else:
                        # 对于其他特殊断言，使用第四个元素作为期望值
                        compare_operator = assertion_type  # 使用断言类型作为操作符
                        expected_value = assertion[3]
            else:  # 5个参数，例如 ["jsonpath", "$", "length", "eq", 10]
                extraction_path = assertion[1]
                assertion_type = assertion[2]

                # 检查断言类型是否有效
                if assertion_type not in ASSERTION_TYPES:
                    raise ValueError(
                        f"不支持的断言类型: {assertion_type} 在 {assertion}")

                # 特殊处理长度断言
                if assertion_type == "length":
                    # 验证第四个元素是有效的比较操作符
                    if assertion[3] not in COMPARISON_OPERATORS:
                        raise ValueError(
                            f"长度断言的比较操作符必须是 {', '.join(COMPARISON_OPERATORS)} 之一: {assertion}")

                    # 验证第五个元素是有效的长度值
                    try:
                        # 尝试将预期长度转换为整数
                        expected_length = int(assertion[4])
                        if expected_length < 0:
                            raise ValueError(f"长度断言的预期值必须是非负整数: {assertion}")
                    except (ValueError, TypeError):
                        raise ValueError(f"长度断言的预期值必须是有效的整数: {assertion}")

                compare_operator = assertion[3]
                expected_value = assertion[4]

            # 提取实际值
            actual_value = self._extract_value(extractor_type, extraction_path)

            # 处理length断言类型
            original_actual_value = actual_value
            if assertion_type == "length":
                if extractor_type not in ["response_time", "status"]:
                    try:
                        allure.attach(
                            f"提取器: {extractor_type}\n路径: {extraction_path}\n原始值: {original_actual_value}\n类型: {type(original_actual_value).__name__}",
                            name=f"长度断言原始值: {extractor_type}",
                            attachment_type=allure.attachment_type.TEXT
                        )
                        actual_value = len(actual_value)
                        allure.attach(
                            f"提取器: {extractor_type}\n路径: {extraction_path}\n长度: {actual_value}",
                            name=f"长度断言计算结果: {extractor_type}",
                            attachment_type=allure.attachment_type.TEXT
                        )
                    except Exception as e:
                        error_msg = (
                            f"无法计算长度: {type(e).__name__}: {str(e)}\n"
                            f"类型: {type(original_actual_value).__name__}\n"
                            f"值: {original_actual_value}"
                        )
                        allure.attach(
                            error_msg,
                            name=f"长度计算失败: {extractor_type} {extraction_path}",
                            attachment_type=allure.attachment_type.TEXT
                        )
                        raise ValueError(
                            f"断言类型'length'无法应用于值 '{original_actual_value}': {str(e)}")

            # 执行断言
            assertion_result = {
                'type': extractor_type,
                'path': extraction_path,
                'assertion_type': assertion_type,
                'operator': compare_operator,
                'actual_value': actual_value,
                'expected_value': expected_value,
                'original_value': original_actual_value if assertion_type == "length" else None,
                'retryable': is_retryable,
                'retry_count': assertion_retry_count,
                'retry_interval': assertion_retry_interval,
                'index': original_idx
            }

            try:
                # 执行断言验证（复用pytest-dsl逻辑）
                result = self._perform_assertion(
                    assertion_type, compare_operator, actual_value, expected_value)
                assertion_result['result'] = result

                if result:
                    assertion_result['passed'] = True
                    allure.attach(
                        self._format_assertion_details(assertion_result),
                        name=f"断言成功: {extractor_type}",
                        attachment_type=allure.attachment_type.TEXT
                    )
                else:
                    assertion_result['passed'] = False
                    assertion_result['error'] = "断言失败"

                    allure.attach(
                        self._format_assertion_details(
                            assertion_result) + "\n\n错误: 断言结果为False",
                        name=f"断言失败: {extractor_type}",
                        attachment_type=allure.attachment_type.TEXT
                    )

                    if is_retryable:
                        failed_retryable_assertions.append(assertion_result)

                    formatted_error = self._format_error_details(
                        extractor_type=extractor_type,
                        extraction_path=extraction_path,
                        assertion_type=assertion_type,
                        compare_operator=compare_operator,
                        actual_value=actual_value,
                        expected_value=expected_value,
                        original_actual_value=original_actual_value
                    )
                    failed_assertions.append((assertion_idx, formatted_error))

            except Exception as e:
                assertion_result['result'] = False
                assertion_result['passed'] = False
                assertion_result['error'] = str(e)

                if "\n" in str(e):
                    formatted_error = str(e)
                else:
                    formatted_error = self._format_error_details(
                        extractor_type=extractor_type,
                        extraction_path=extraction_path,
                        assertion_type=assertion_type,
                        compare_operator=compare_operator,
                        actual_value=actual_value,
                        expected_value=expected_value,
                        original_actual_value=original_actual_value,
                        error_message=str(e)
                    )

                allure.attach(
                    self._format_assertion_details(
                        assertion_result) + f"\n\n错误: {str(e)}",
                    name=f"断言失败: {extractor_type}",
                    attachment_type=allure.attachment_type.TEXT
                )

                if is_retryable:
                    failed_retryable_assertions.append(assertion_result)

                failed_assertions.append((assertion_idx, formatted_error))

            assert_results.append(assertion_result)

        # 处理断言失败
        if failed_assertions:
            collect_only = self.config.get(
                '_collect_failed_assertions_only', False)

            if not collect_only:
                if len(failed_assertions) == 1:
                    raise AssertionError(failed_assertions[0][1])
                else:
                    error_summary = f"多个断言失败 ({len(failed_assertions)}/{len(process_asserts)}):\n"
                    for idx, (assertion_idx, error_msg) in enumerate(failed_assertions, 1):
                        if "[" in error_msg and "]" in error_msg:
                            extractor_type = error_msg.split(
                                "[", 1)[1].split("]")[0]
                        else:
                            extractor_type = "未知"

                        assertion_title = f"断言 #{assertion_idx+1} [{extractor_type}]"
                        error_summary += f"\n{'-' * 30}\n{idx}. {assertion_title}:\n{'-' * 30}\n{error_msg}"

                    error_summary += f"\n{'-' * 50}"
                    raise AssertionError(error_summary)

        return assert_results, failed_retryable_assertions

    def _extract_value(self, extractor_type: str, extraction_path: str = None, default_value: Any = None) -> Any:
        """从浏览器响应提取值"""
        if self.response is None:
            return default_value

        try:
            if extractor_type == "jsonpath":
                return self._extract_jsonpath(extraction_path, default_value)
            elif extractor_type == "xpath":
                # 浏览器响应通常不支持XPath，可以考虑解析HTML
                return self._extract_xpath(extraction_path, default_value)
            elif extractor_type == "regex":
                return self._extract_regex(extraction_path, default_value)
            elif extractor_type == "header":
                return self._extract_header(extraction_path, default_value)
            elif extractor_type == "status":
                return self.response.status_code
            elif extractor_type == "body":
                return self.response.text
            elif extractor_type == "response_time":
                return getattr(self.response, '_elapsed_ms', 0.0)
            else:
                raise ValueError(f"不支持的提取器类型: {extractor_type}")
        except Exception as e:
            error_message = f"提取值失败({extractor_type}, {extraction_path}): {type(e).__name__}: {str(e)}"
            allure.attach(
                error_message,
                name=f"提取错误: {extractor_type}",
                attachment_type=allure.attachment_type.TEXT
            )
            if default_value is not None:
                return default_value
            raise ValueError(error_message)

    def _extract_jsonpath(self, path: str, default_value: Any = None) -> Any:
        """使用JSONPath从JSON响应提取值（与pytest-dsl完全一致）"""
        try:
            # 直接使用response.json()，与pytest-dsl保持完全一致
            json_data = self.response.json()

            # 使用jsonpath_ng库进行解析（与pytest-dsl保持一致）
            import jsonpath_ng.ext as jsonpath
            jsonpath_expr = jsonpath.parse(path)
            matches = [match.value for match in jsonpath_expr.find(json_data)]

            if not matches:
                return default_value
            elif len(matches) == 1:
                return matches[0]
            else:
                return matches
        except Exception as e:
            if default_value is not None:
                return default_value
            raise ValueError(f"JSONPath提取失败: {str(e)}")

    def _extract_xpath(self, path: str, default_value: Any = None) -> Any:
        """使用XPath从HTML响应提取值"""
        # 简化实现，实际应该使用lxml解析
        try:
            import lxml.etree as etree
            parser = etree.HTMLParser()
            tree = etree.fromstring(self.response.text.encode(), parser)
            result = tree.xpath(path)

            if not result:
                return default_value
            elif len(result) == 1:
                return result[0]
            else:
                return result
        except Exception as e:
            if default_value is not None:
                return default_value
            raise ValueError(f"XPath提取失败: {str(e)}")

    def _extract_regex(self, pattern: str, default_value: Any = None) -> Any:
        """使用正则表达式从响应提取值"""
        try:
            # 如果响应是JSON格式，先转换为字符串（与pytest-dsl保持一致）
            if self.response.is_json():
                text = json.dumps(self.response.json())
            else:
                text = self.response.text

            # 检查正则表达式是否包含捕获组
            compiled_pattern = re.compile(pattern)
            has_groups = compiled_pattern.groups > 0

            if has_groups:
                # 如果有捕获组，只返回第一个匹配的捕获组内容
                first_match = re.search(pattern, text)
                if not first_match:
                    return default_value

                # 获取第一个匹配的捕获组
                if compiled_pattern.groups == 1:
                    # 只有一个捕获组，返回字符串
                    return first_match.group(1)
                else:
                    # 多个捕获组，返回元组
                    return first_match.groups()
            else:
                # 如果没有捕获组，使用findall获取所有完整匹配
                matches = re.findall(pattern, text)

                if not matches:
                    return default_value
                elif len(matches) == 1:
                    return matches[0]
                else:
                    return matches
        except Exception as e:
            if default_value is not None:
                return default_value
            raise ValueError(f"正则表达式提取失败: {str(e)}")

    def _extract_header(self, header_name: str, default_value: Any = None) -> Any:
        """从响应头提取值"""
        header_value = self.response.headers.get(header_name)
        return header_value if header_value is not None else default_value

    def _perform_assertion(self, assertion_type: str, operator: str, actual_value: Any, expected_value: Any = None) -> bool:
        """执行断言（复用pytest-dsl逻辑）"""
        # 类型转换增强（完全复用pytest-dsl逻辑）
        if operator in ["eq", "neq", "lt", "lte", "gt", "gte"] and expected_value is not None:
            try:
                # 将预期值转换为适当的类型
                if isinstance(expected_value, str):
                    # 去除空白字符和换行符
                    clean_expected = expected_value.strip()

                    # 判断是否是整数
                    if clean_expected.isdigit() or (clean_expected.startswith('-') and clean_expected[1:].isdigit()):
                        expected_value = int(clean_expected)
                    # 判断是否是浮点数（包括科学记数法）
                    elif (
                        # 标准小数
                        (clean_expected.replace('.', '', 1).isdigit()) or
                        # 负小数
                        (clean_expected.startswith('-') and clean_expected[1:].replace('.', '', 1).isdigit()) or
                        # 科学记数法 - 正
                        (('e' in clean_expected or 'E' in clean_expected) and
                         clean_expected.replace('e', '').replace('E', '').replace('+', '', 1).replace('-', '', 1).replace('.', '', 1).isdigit()) or
                        # 科学记数法 - 负
                        (clean_expected.startswith('-') and ('e' in clean_expected or 'E' in clean_expected) and
                         clean_expected[1:].replace('e', '').replace('E', '').replace('+', '', 1).replace('-', '', 1).replace('.', '', 1).isdigit())
                    ):
                        expected_value = float(clean_expected)

                # 将实际值转换为适当的类型
                if isinstance(actual_value, str):
                    # 去除空白字符和换行符
                    clean_actual = actual_value.strip()

                    # 判断是否是整数
                    if clean_actual.isdigit() or (clean_actual.startswith('-') and clean_actual[1:].isdigit()):
                        actual_value = int(clean_actual)
                    # 判断是否是浮点数（包括科学记数法）
                    elif (
                        # 标准小数
                        (clean_actual.replace('.', '', 1).isdigit()) or
                        # 负小数
                        (clean_actual.startswith('-') and clean_actual[1:].replace('.', '', 1).isdigit()) or
                        # 科学记数法 - 正
                        (('e' in clean_actual or 'E' in clean_actual) and
                         clean_actual.replace('e', '').replace('E', '').replace('+', '', 1).replace('-', '', 1).replace('.', '', 1).isdigit()) or
                        # 科学记数法 - 负
                        (clean_actual.startswith('-') and ('e' in clean_actual or 'E' in clean_actual) and
                         clean_actual[1:].replace('e', '').replace('E', '').replace('+', '', 1).replace('-', '', 1).replace('.', '', 1).isdigit())
                    ):
                        actual_value = float(clean_actual)
            except (ValueError, TypeError) as e:
                # 转换失败时记录日志但不抛出异常，保持原值进行比较
                allure.attach(
                    f"类型转换失败: {str(e)}\n实际值: {actual_value} ({type(actual_value).__name__})\n预期值: {expected_value} ({type(expected_value).__name__})",
                    name="断言类型转换警告",
                    attachment_type=allure.attachment_type.TEXT
                )

        # 记录断言参数
        allure.attach(
            f"断言类型: {assertion_type}\n"
            f"比较操作符: {operator}\n"
            f"实际值: {actual_value} ({type(actual_value).__name__})\n"
            f"期望值: {expected_value} ({type(expected_value).__name__ if expected_value is not None else 'None'})",
            name="断言参数",
            attachment_type=allure.attachment_type.TEXT
        )

        # 执行断言逻辑（复用pytest-dsl的实现）
        if assertion_type == "value":
            return self._compare_values(actual_value, expected_value, operator)
        elif assertion_type in ["contains", "not_contains", "startswith", "endswith", "matches", "schema"]:
            if assertion_type == "contains":
                if isinstance(actual_value, str):
                    return str(expected_value) in actual_value
                elif isinstance(actual_value, (list, tuple, dict)):
                    return expected_value in actual_value
                return False
            elif assertion_type == "not_contains":
                if isinstance(actual_value, str):
                    return str(expected_value) not in actual_value
                elif isinstance(actual_value, (list, tuple, dict)):
                    return expected_value not in actual_value
                return True
            elif assertion_type == "startswith":
                return isinstance(actual_value, str) and actual_value.startswith(str(expected_value))
            elif assertion_type == "endswith":
                return isinstance(actual_value, str) and actual_value.endswith(str(expected_value))
            elif assertion_type == "matches":
                if not isinstance(actual_value, str):
                    actual_value = str(
                        actual_value) if actual_value is not None else ""
                try:
                    pattern = str(expected_value)
                    match_result = bool(re.search(pattern, actual_value))
                    # 记录匹配结果
                    allure.attach(
                        f"正则表达式匹配结果: {'成功' if match_result else '失败'}\n"
                        f"模式: {pattern}\n"
                        f"目标字符串: {actual_value}",
                        name="正则表达式匹配",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    return match_result
                except Exception as e:
                    # 记录正则表达式匹配错误
                    allure.attach(
                        f"正则表达式匹配失败: {type(e).__name__}: {str(e)}\n"
                        f"模式: {expected_value}\n"
                        f"目标字符串: {actual_value}",
                        name="正则表达式错误",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    return False
            elif assertion_type == "schema":
                try:
                    from jsonschema import validate
                    validate(instance=actual_value, schema=expected_value)
                    return True
                except Exception as e:
                    # 记录JSON Schema验证错误
                    allure.attach(
                        f"JSON Schema验证失败: {type(e).__name__}: {str(e)}\n"
                        f"Schema: {expected_value}\n"
                        f"实例: {actual_value}",
                        name="Schema验证错误",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    return False
        elif assertion_type == "length":
            effective_operator = "eq" if operator == "length" else operator
            return self._compare_values(actual_value, expected_value, effective_operator)
        elif assertion_type == "exists":
            return actual_value is not None
        elif assertion_type == "not_exists":
            return actual_value is None
        elif assertion_type == "type":
            if expected_value == "string":
                return isinstance(actual_value, str)
            elif expected_value == "number":
                return isinstance(actual_value, (int, float))
            elif expected_value == "boolean":
                return isinstance(actual_value, bool)
            elif expected_value == "array":
                return isinstance(actual_value, list)
            elif expected_value == "object":
                return isinstance(actual_value, dict)
            elif expected_value == "null":
                return actual_value is None
            return False
        else:
            raise ValueError(f"不支持的断言类型: {assertion_type}")

    def _compare_values(self, actual_value: Any, expected_value: Any, operator: str) -> bool:
        """比较两个值（复用pytest-dsl逻辑）"""
        # 类型转换逻辑（复用pytest-dsl的实现）
        if operator in ["eq", "neq", "lt", "lte", "gt", "gte"] and expected_value is not None:
            try:
                # 将预期值转换为适当的类型
                if isinstance(expected_value, str):
                    clean_expected = expected_value.strip()
                    if clean_expected.isdigit() or (clean_expected.startswith('-') and clean_expected[1:].isdigit()):
                        expected_value = int(clean_expected)
                    elif (clean_expected.replace('.', '', 1).isdigit()) or \
                         (clean_expected.startswith('-') and clean_expected[1:].replace('.', '', 1).isdigit()) or \
                         (('e' in clean_expected or 'E' in clean_expected) and 
                          clean_expected.replace('e', '').replace('E', '').replace('+', '', 1).replace('-', '', 1).replace('.', '', 1).isdigit()):
                        expected_value = float(clean_expected)

                # 将实际值转换为适当的类型
                if isinstance(actual_value, str):
                    clean_actual = actual_value.strip()
                    if clean_actual.isdigit() or (clean_actual.startswith('-') and clean_actual[1:].isdigit()):
                        actual_value = int(clean_actual)
                    elif (clean_actual.replace('.', '', 1).isdigit()) or \
                         (clean_actual.startswith('-') and clean_actual[1:].replace('.', '', 1).isdigit()) or \
                         (('e' in clean_actual or 'E' in clean_actual) and 
                          clean_actual.replace('e', '').replace('E', '').replace('+', '', 1).replace('-', '', 1).replace('.', '', 1).isdigit()):
                        actual_value = float(clean_actual)
            except (ValueError, TypeError):
                # 转换失败时保持原值进行比较
                pass

        if operator == "eq":
            return actual_value == expected_value
        elif operator == "neq":
            return actual_value != expected_value
        elif operator == "lt":
            return actual_value < expected_value
        elif operator == "lte":
            return actual_value <= expected_value
        elif operator == "gt":
            return actual_value > expected_value
        elif operator == "gte":
            return actual_value >= expected_value
        elif operator == "in":
            return actual_value in expected_value
        elif operator == "not_in":
            return actual_value not in expected_value
        elif operator == "contains":
            if isinstance(actual_value, str):
                return str(expected_value) in actual_value
            elif isinstance(actual_value, (list, tuple, dict)):
                return expected_value in actual_value
            return False
        elif operator == "not_contains":
            if isinstance(actual_value, str):
                return str(expected_value) not in actual_value
            elif isinstance(actual_value, (list, tuple, dict)):
                return expected_value not in actual_value
            return True
        elif operator == "startswith":
            if not isinstance(actual_value, str):
                actual_value = str(
                    actual_value) if actual_value is not None else ""
            return actual_value.startswith(str(expected_value))
        elif operator == "endswith":
            if not isinstance(actual_value, str):
                actual_value = str(
                    actual_value) if actual_value is not None else ""
            return actual_value.endswith(str(expected_value))
        elif operator == "matches":
            if not isinstance(actual_value, str):
                actual_value = str(
                    actual_value) if actual_value is not None else ""
            try:
                pattern = str(expected_value)
                match_result = bool(re.search(pattern, actual_value))
                # 记录匹配结果
                allure.attach(
                    f"正则表达式匹配结果: {'成功' if match_result else '失败'}\n"
                    f"模式: {pattern}\n"
                    f"目标字符串: {actual_value}",
                    name="正则表达式匹配",
                    attachment_type=allure.attachment_type.TEXT
                )
                return match_result
            except Exception as e:
                # 记录正则表达式匹配错误
                allure.attach(
                    f"正则表达式匹配失败: {type(e).__name__}: {str(e)}\n"
                    f"模式: {expected_value}\n"
                    f"目标字符串: {actual_value}",
                    name="正则表达式错误",
                    attachment_type=allure.attachment_type.TEXT
                )
                return False
        else:
            raise ValueError(f"不支持的比较操作符: {operator}")

    def _format_assertion_details(self, assertion_result: Dict[str, Any]) -> str:
        """格式化断言详情"""
        details = f"类型: {assertion_result['type']}\n"
        if assertion_result['path']:
            details += f"路径: {assertion_result['path']}\n"

        if assertion_result['assertion_type'] == 'length':
            details += f"原始值: {assertion_result['original_value']}\n"
            details += f"长度: {assertion_result['actual_value']}\n"
        else:
            details += f"实际值: {assertion_result['actual_value']}\n"

        details += f"操作符: {assertion_result['operator']}\n"

        if assertion_result['expected_value'] is not None:
            details += f"预期值: {assertion_result['expected_value']}\n"

        details += f"结果: {'通过' if assertion_result['passed'] else '失败'}"
        return details

    def _format_error_details(self, extractor_type: str, extraction_path: str,
                              assertion_type: str, compare_operator: str,
                              actual_value: Any, expected_value: Any,
                              original_actual_value: Any = None,
                              error_message: str = None,
                              additional_context: str = None) -> str:
        """格式化断言错误详情"""
        error_details = []

        prefix = "断言执行错误" if additional_context else "断言失败"
        error_details.append(f"{prefix} [{extractor_type}]")

        if additional_context:
            error_details.append(f"异常类型: {additional_context}")

        if extraction_path:
            error_details.append(f"路径: {extraction_path}")

        if assertion_type == "length":
            error_details.append("断言类型: 长度比较")
            if original_actual_value is not None:
                error_details.append(f"原始值: {original_actual_value}")
            error_details.append(f"实际长度: {actual_value}")
        else:
            error_details.append(f"断言类型: {assertion_type}")
            error_details.append(f"实际值: {actual_value}")

        if compare_operator:
            error_details.append(f"比较操作符: {compare_operator}")

        if expected_value is not None:
            error_details.append(f"预期值: {expected_value}")

        error_details.append(f"实际类型: {type(actual_value).__name__}")
        if expected_value is not None:
            error_details.append(f"预期类型: {type(expected_value).__name__}")

        if error_message:
            error_details.append(f"错误信息: {error_message}")

        return "\n".join(error_details)
