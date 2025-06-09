#!/usr/bin/env python3
"""
运行浏览器HTTP修复功能验证测试的脚本
"""

import sys
import os
import json
from unittest.mock import Mock

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_assertion_parsing():
    """测试断言参数解析功能"""
    print("🔍 测试断言参数解析功能...")
    
    try:
        from pytest_dsl_ui.core.browser_http_request import BrowserHTTPRequest
        
        # 创建mock响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"slideshow": {"title": "Sample Slide Show"}}
        mock_response.text = '{"slideshow": {"title": "Sample Slide Show"}}'
        mock_response.elapsed.total_seconds.return_value = 1.5
        
        config = {
            "method": "GET", 
            "url": "https://httpbin.org/get",
            "asserts": [
                ["status", "eq", 200],
                ["header", "Content-Type", "exists"],
                ["jsonpath", "$.slideshow.title", "exists"],
                ["body", "length", "gt", 10],
                ["jsonpath", "$.slideshow", "type", "object"]
            ]
        }
        request = BrowserHTTPRequest(config)
        request.response = mock_response
        
        # 测试断言解析和执行
        try:
            results, failed = request.process_asserts()
            print(f"  ✅ 断言解析和执行测试通过! 执行了 {len(results)} 个断言")
            return True
        except Exception as e:
            print(f"  ❌ 断言解析和执行失败: {e}")
            return False
                
    except ImportError as e:
        print(f"  ❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

def test_jsonpath_extraction():
    """测试JSONPath提取功能"""
    print("🔍 测试JSONPath提取功能...")
    
    try:
        from pytest_dsl_ui.core.browser_http_request import BrowserHTTPRequest
        from pytest_dsl_ui.core.browser_http_client import BrowserResponse
        
        # 创建模拟响应
        mock_playwright_response = Mock()
        mock_playwright_response.status = 200
        mock_playwright_response.headers = {"content-type": "application/json"}
        
        test_data = {
            "slideshow": {
                "title": "Sample Slide Show",
                "author": "Test Author",
                "slides": [
                    {"title": "Slide 1", "type": "all"},
                    {"title": "Slide 2", "type": "all"}
                ]
            }
        }
        mock_playwright_response.text.return_value = json.dumps(test_data)
        mock_playwright_response.json.return_value = test_data
        
        browser_response = BrowserResponse(mock_playwright_response)
        
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        request.response = browser_response
        
        # 测试JSONPath提取
        test_cases = [
            ("$.slideshow.title", "Sample Slide Show"),
            ("$.slideshow.author", "Test Author"),
            ("$.slideshow.slides[0].title", "Slide 1"),
            ("$.nonexistent", None)
        ]
        
        for path, expected in test_cases:
            try:
                result = request._extract_jsonpath(path)
                print(f"  ✅ JSONPath '{path}' -> {result}")
                if expected is not None:
                    assert result == expected, f"Expected {expected}, got {result}"
                else:
                    assert result is None, f"Expected None, got {result}"
            except Exception as e:
                print(f"  ❌ JSONPath '{path}' -> Error: {e}")
                return False
                
        print("  ✅ JSONPath提取测试通过!")
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

def test_type_conversion():
    """测试类型转换功能"""
    print("🔍 测试类型转换功能...")
    
    try:
        from pytest_dsl_ui.core.browser_http_request import BrowserHTTPRequest
        
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        
        # 测试类型转换比较
        test_cases = [
            ("123", 123, "eq", True),
            ("123.45", 123.45, "eq", True),
            ("1.23e-4", 0.000123, "eq", True),
            ("-456", -456, "eq", True),
            ("100", 50, "gt", True),
            ("text", 123, "eq", False)
        ]
        
        for actual, expected, operator, should_pass in test_cases:
            try:
                result = request._compare_values(actual, expected, operator)
                print(f"  ✅ '{actual}' {operator} {expected} -> {result}")
                assert result == should_pass, f"Expected {should_pass}, got {result}"
            except Exception as e:
                print(f"  ❌ '{actual}' {operator} {expected} -> Error: {e}")
                return False
                
        print("  ✅ 类型转换测试通过!")
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

def test_regex_matching():
    """测试正则表达式匹配功能"""
    print("🔍 测试正则表达式匹配功能...")
    
    try:
        from pytest_dsl_ui.core.browser_http_request import BrowserHTTPRequest
        
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        
        # 测试正则表达式匹配
        test_cases = [
            ("test@example.com", r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$", "matches", True),
            ("invalid-email", r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$", "matches", False),
            ("Hello World", "World", "contains", True),
            ("https://example.com", "https://", "startswith", True),
            ("file.txt", ".txt", "endswith", True)
        ]
        
        for text, pattern, operator, should_pass in test_cases:
            try:
                result = request._compare_values(text, pattern, operator)
                print(f"  ✅ '{text}' {operator} '{pattern}' -> {result}")
                assert result == should_pass, f"Expected {should_pass}, got {result}"
            except Exception as e:
                print(f"  ❌ '{text}' {operator} '{pattern}' -> Error: {e}")
                return False
                
        print("  ✅ 正则表达式匹配测试通过!")
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

def test_assertion_execution():
    """测试断言执行功能"""
    print("🔍 测试断言执行功能...")
    
    try:
        from pytest_dsl_ui.core.browser_http_request import BrowserHTTPRequest
        
        config = {"method": "GET", "url": "https://httpbin.org/get"}
        request = BrowserHTTPRequest(config)
        
        # 测试各种断言类型
        test_cases = [
            ("value", "eq", 123, 123, True),
            ("exists", "exists", "some_value", None, True),
            ("not_exists", "not_exists", None, None, True),
            ("type", "type", "hello", "string", True),
            ("type", "type", 123, "number", True),
            ("type", "type", [1, 2, 3], "array", True),
            ("length", "eq", 5, 5, True),
            ("contains", "contains", "hello world", "world", True),
            ("startswith", "startswith", "hello world", "hello", True),
            ("endswith", "endswith", "hello world", "world", True)
        ]
        
        for assertion_type, operator, actual, expected, should_pass in test_cases:
            try:
                result = request._perform_assertion(assertion_type, operator, actual, expected)
                print(f"  ✅ {assertion_type}({operator}): {actual} vs {expected} -> {result}")
                assert result == should_pass, f"Expected {should_pass}, got {result}"
            except Exception as e:
                print(f"  ❌ {assertion_type}({operator}): {actual} vs {expected} -> Error: {e}")
                return False
                
        print("  ✅ 断言执行测试通过!")
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始浏览器HTTP修复功能验证测试")
    print("=" * 60)
    
    tests = [
        test_assertion_parsing,
        test_jsonpath_extraction, 
        test_type_conversion,
        test_regex_matching,
        test_assertion_execution
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"  ❌ 测试异常: {e}")
            print()
    
    print("=" * 60)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过! 浏览器HTTP修复功能验证成功!")
        return True
    else:
        print("❌ 部分测试失败，请检查修复功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 