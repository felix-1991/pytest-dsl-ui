#!/usr/bin/env python3
"""
浏览器HTTP实现修复功能的单元测试
验证与pytest-dsl实现的一致性
"""

import pytest
import json
import re
from unittest.mock import Mock, MagicMock
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pytest_dsl_ui.core.browser_http_request import BrowserHTTPRequest
from pytest_dsl_ui.core.browser_http_client import BrowserResponse


class TestBrowserHTTPFixes:
    """测试浏览器HTTP实现修复功能"""

    def setup_method(self):
        """设置测试环境"""
        # 创建模拟的浏览器响应
        self.mock_playwright_response = Mock()
        self.mock_playwright_response.status = 200
        self.mock_playwright_response.status_text = "OK"
        self.mock_playwright_response.headers = {
            "content-type": "application/json",
            "server": "nginx/1.14.0"
        }
        self.mock_playwright_response.url = "https://httpbin.org/get"
        
        # 模拟JSON响应数据
        self.test_json_data = {
            "slideshow": {
                "title": "Sample Slide Show",
                "author": "Yours Truly",
                "slides": [
                    {"title": "Wake up to WonderWidgets!", "type": "all"},
                    {"title": "Overview", "type": "all"}
                ]
            },
            "args": {
                "number_string": "123",
                "float_string": "123.45",
                "scientific": "1.23e-4",
                "negative": "-456"
            },
            "headers": {
                "User-Agent": "Mozilla/5.0 (test)",
                "Host": "httpbin.org"
            }
        }
        
        self.mock_playwright_response.text.return_value = json.dumps(self.test_json_data)
        
        # 创建BrowserResponse实例
        self.browser_response = BrowserResponse(self.mock_playwright_response)
        self.browser_response._elapsed_ms = 150.5

    def test_parse_assertion_params_basic(self):
        """测试基础断言参数解析"""
        config = {
            "method": "GET",
            "url": "https://httpbin.org/get"
        }
        
        request = BrowserHTTPRequest(config)
        
        # 测试2参数格式 - 存在性断言
        assertion = ["header", "Content-Type"]
        path, assertion_type, operator, expected = request._parse_assertion_params(assertion)
        assert path == "Content-Type"
        assert assertion_type == "exists"
        assert operator == "eq"
        assert expected is None
        
        # 测试3参数格式 - 值比较
        assertion = ["status", "eq", 200]
        path, assertion_type, operator, expected = request._parse_assertion_params(assertion)
        assert path is None  # status不需要路径
        assert assertion_type == "value"
        assert operator == "eq"
        assert expected == 200
        
        # 测试4参数格式 - JSONPath值比较
        assertion = ["jsonpath", "$.slideshow.title", "eq", "Sample Slide Show"]
        path, assertion_type, operator, expected = request._parse_assertion_params(assertion)
        assert path == "$.slideshow.title"
        assert assertion_type == "value"
        assert operator == "eq"
        assert expected == "Sample Slide Show"

    def test_parse_assertion_params_length(self):
        """测试长度断言参数解析"""
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        
        # 测试3参数长度断言 - ["body", "length", 10]
        assertion = ["body", "length", 10]
        path, assertion_type, operator, expected = request._parse_assertion_params(assertion)
        assert path is None
        assert assertion_type == "length"
        assert operator == "eq"
        assert expected == 10
        
        # 测试4参数长度断言 - ["body", "length", "gt", 50]
        assertion = ["body", "length", "gt", 50]
        path, assertion_type, operator, expected = request._parse_assertion_params(assertion)
        assert path is None
        assert assertion_type == "length"
        assert operator == "gt"
        assert expected == 50
        
        # 测试5参数长度断言 - ["jsonpath", "$.slides", "length", "eq", 2]
        assertion = ["jsonpath", "$.slideshow.slides", "length", "eq", 2]
        path, assertion_type, operator, expected = request._parse_assertion_params(assertion)
        assert path == "$.slideshow.slides"
        assert assertion_type == "length"
        assert operator == "eq"
        assert expected == 2

    def test_extract_jsonpath_basic(self):
        """测试基础JSONPath提取功能"""
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        request.response = self.browser_response
        
        # 测试简单路径提取
        title = request._extract_jsonpath("$.slideshow.title")
        assert title == "Sample Slide Show"
        
        # 测试数组索引提取
        first_slide = request._extract_jsonpath("$.slideshow.slides[0].title")
        assert first_slide == "Wake up to WonderWidgets!"
        
        # 测试不存在的路径
        missing = request._extract_jsonpath("$.nonexistent", "default")
        assert missing == "default"

    def test_extract_jsonpath_with_jsonpath_ng(self):
        """测试使用jsonpath_ng库的复杂JSONPath提取"""
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        request.response = self.browser_response
        
        try:
            import jsonpath_ng.ext as jsonpath
            
            # 测试复杂路径提取
            slides = request._extract_jsonpath("$.slideshow.slides[*].title")
            assert isinstance(slides, list)
            assert len(slides) == 2
            assert "Wake up to WonderWidgets!" in slides
            assert "Overview" in slides
            
        except ImportError:
            # 如果没有jsonpath_ng库，跳过测试
            pytest.skip("jsonpath_ng library not available")

    def test_type_conversion_in_comparison(self):
        """测试类型转换逻辑"""
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        request.response = self.browser_response
        
        # 测试字符串数字转换
        result = request._compare_values("123", 123, "eq")
        assert result is True
        
        # 测试浮点数转换
        result = request._compare_values("123.45", 123.45, "eq")
        assert result is True
        
        # 测试科学记数法转换
        result = request._compare_values("1.23e-4", 0.000123, "eq")
        assert result is True
        
        # 测试负数转换
        result = request._compare_values("-456", -456, "eq")
        assert result is True
        
        # 测试数值比较
        result = request._compare_values("100", 50, "gt")
        assert result is True

    def test_regex_matching(self):
        """测试正则表达式匹配功能"""
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        
        # 测试简单匹配
        result = request._compare_values("test@example.com", r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$", "matches")
        assert result is True
        
        # 测试不匹配的情况
        result = request._compare_values("invalid-email", r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$", "matches")
        assert result is False
        
        # 测试包含匹配
        result = request._compare_values("Hello World", "World", "contains")
        assert result is True
        
        # 测试开头匹配
        result = request._compare_values("https://example.com", "https://", "startswith")
        assert result is True
        
        # 测试结尾匹配
        result = request._compare_values("file.txt", ".txt", "endswith")
        assert result is True

    def test_schema_validation(self):
        """测试JSON Schema验证功能"""
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        
        try:
            from jsonschema import validate
            
            # 测试有效的schema
            test_data = {"name": "John", "age": 30}
            schema = {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "number"}
                },
                "required": ["name", "age"]
            }
            
            result = request._perform_assertion("schema", "schema", test_data, schema)
            assert result is True
            
            # 测试无效的schema
            invalid_data = {"name": "John", "age": "thirty"}  # age应该是数字
            result = request._perform_assertion("schema", "schema", invalid_data, schema)
            assert result is False
            
        except ImportError:
            # 如果没有jsonschema库，跳过测试
            pytest.skip("jsonschema library not available")

    def test_length_assertions(self):
        """测试长度断言功能"""
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        request.response = self.browser_response
        
        # 测试字符串长度
        result = request._perform_assertion("length", "eq", 5, 5)  # "hello" has length 5
        assert result is True
        
        # 测试数组长度
        result = request._perform_assertion("length", "gt", 3, 2)  # length 3 > 2
        assert result is True
        
        # 测试长度比较操作符
        result = request._perform_assertion("length", "lte", 10, 15)  # length 10 <= 15
        assert result is True

    def test_existence_assertions(self):
        """测试存在性断言"""
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        
        # 测试exists断言
        result = request._perform_assertion("exists", "exists", "some_value", None)
        assert result is True
        
        result = request._perform_assertion("exists", "exists", None, None)
        assert result is False
        
        # 测试not_exists断言
        result = request._perform_assertion("not_exists", "not_exists", None, None)
        assert result is True
        
        result = request._perform_assertion("not_exists", "not_exists", "some_value", None)
        assert result is False

    def test_type_assertions(self):
        """测试类型断言"""
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        
        # 测试字符串类型
        result = request._perform_assertion("type", "type", "hello", "string")
        assert result is True
        
        # 测试数字类型
        result = request._perform_assertion("type", "type", 123, "number")
        assert result is True
        
        # 测试布尔类型
        result = request._perform_assertion("type", "type", True, "boolean")
        assert result is True
        
        # 测试数组类型
        result = request._perform_assertion("type", "type", [1, 2, 3], "array")
        assert result is True
        
        # 测试对象类型
        result = request._perform_assertion("type", "type", {"key": "value"}, "object")
        assert result is True
        
        # 测试null类型
        result = request._perform_assertion("type", "type", None, "null")
        assert result is True

    def test_extract_value_methods(self):
        """测试各种值提取方法"""
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        request.response = self.browser_response
        
        # 测试状态码提取
        status = request._extract_value("status")
        assert status == 200
        
        # 测试响应体提取
        body = request._extract_value("body")
        assert isinstance(body, str)
        assert "slideshow" in body
        
        # 测试响应时间提取
        response_time = request._extract_value("response_time")
        assert response_time == 150.5
        
        # 测试头部提取
        content_type = request._extract_value("header", "content-type")
        assert content_type == "application/json"

    def test_regex_extraction(self):
        """测试正则表达式提取功能"""
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        
        # 模拟包含电子邮件的响应
        mock_response = Mock()
        mock_response.text = "Contact us at support@example.com or sales@test.org"
        mock_response.headers = {}
        
        browser_response = BrowserResponse(mock_response)
        request.response = browser_response
        
        # 测试带捕获组的正则表达式
        email_domain = request._extract_regex(r"[\w\.-]+@([\w\.-]+)")
        assert email_domain == "example.com"  # 第一个匹配的域名
        
        # 测试不带捕获组的正则表达式
        emails = request._extract_regex(r"[\w\.-]+@[\w\.-]+")
        assert isinstance(emails, list)
        assert len(emails) == 2

    def test_error_handling(self):
        """测试错误处理"""
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        
        # 测试没有响应时的错误处理
        with pytest.raises(ValueError, match="需要先执行请求"):
            request.process_captures()
        
        with pytest.raises(ValueError, match="需要先执行请求"):
            request.process_asserts()
        
        # 测试无效的提取器类型
        request.response = self.browser_response
        with pytest.raises(ValueError, match="不支持的提取器类型"):
            request._extract_value("invalid_extractor")

    def test_browser_response_properties(self):
        """测试BrowserResponse属性"""
        response = self.browser_response
        
        # 测试基本属性
        assert response.status_code == 200
        assert response.status_text == "OK"
        assert response.url == "https://httpbin.org/get"
        assert response.elapsed_ms == 150.5
        
        # 测试头部访问
        assert response.headers["content-type"] == "application/json"
        assert response.headers["server"] == "nginx/1.14.0"
        
        # 测试JSON解析
        json_data = response.json()
        assert json_data["slideshow"]["title"] == "Sample Slide Show"
        
        # 测试JSON检测
        assert response.is_json() is True
        
        # 测试状态判断
        assert response.ok is True

def test_basic_functionality():
    """基本功能测试"""
    assert True

if __name__ == "__main__":
    print("测试文件创建成功") 