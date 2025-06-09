"""
基于浏览器的HTTP API测试示例

本示例展示如何使用浏览器HTTP关键字进行API测试，
结合UI操作和API测试的优势。
"""

import pytest


def test_browser_http_basic_request():
    """基本的浏览器HTTP请求示例"""
    
    # 设置浏览器HTTP客户端
    [设置浏览器HTTP客户端], 客户端名称: "jsonplaceholder", 基础URL: "https://jsonplaceholder.typicode.com", 默认头: '''
    {
        "Content-Type": "application/json",
        "User-Agent": "pytest-dsl-ui/1.0"
    }
    '''
    
    # 发送GET请求获取用户信息
    [浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
        method: GET
        url: /users/1
        captures:
            user_id: ["jsonpath", "$.id"]
            user_name: ["jsonpath", "$.name"]
            user_email: ["jsonpath", "$.email"]
            user_username: ["jsonpath", "$.username"]
        asserts:
            - ["status", "eq", 200]
            - ["jsonpath", "$.id", "eq", 1]
            - ["jsonpath", "$.name", "exists"]
            - ["jsonpath", "$.email", "contains", "@"]
    '''
    
    # 验证捕获的变量
    print(f"用户ID: {user_id}")
    print(f"用户名: {user_name}")
    print(f"邮箱: {user_email}")


def test_browser_http_with_ui_login():
    """结合UI登录和API测试的示例"""
    
    # 1. 通过UI进行登录（模拟获取认证状态）
    [打开页面], 地址: "https://example.com/demo-login"
    
    # 模拟登录过程
    [输入文本], 选择器: "#username", 文本: "demo"
    [输入文本], 选择器: "#password", 文本: "demo123"
    [点击元素], 选择器: "#login-button"
    [等待元素], 选择器: ".welcome-message", 超时时间: 5
    
    # 2. 使用浏览器的认证状态发送API请求
    [浏览器HTTP请求], 客户端: "api", 配置: '''
        method: GET
        url: /api/profile
        captures:
            profile_data: ["jsonpath", "$"]
            authenticated: ["jsonpath", "$.authenticated"]
        asserts:
            - ["status", "eq", 200]
            - ["jsonpath", "$.authenticated", "eq", true]
            - ["jsonpath", "$.user", "exists"]
    '''
    
    # 3. 验证API返回的数据与UI一致
    assert authenticated == True, "用户应该已通过认证"


def test_browser_http_post_request():
    """POST请求和复杂断言示例"""
    
    [浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
        method: POST
        url: /posts
        request:
            json:
                title: "测试文章标题"
                body: "这是一篇测试文章的内容"
                userId: 1
        captures:
            post_id: ["jsonpath", "$.id"]
            post_title: ["jsonpath", "$.title"]
            post_user_id: ["jsonpath", "$.userId"]
        asserts:
            - ["status", "eq", 201]
            - ["jsonpath", "$.id", "exists"]
            - ["jsonpath", "$.title", "eq", "测试文章标题"]
            - ["jsonpath", "$.body", "contains", "测试文章"]
            - ["jsonpath", "$.userId", "eq", 1]
            - ["response_time", "lt", 5000]
    '''
    
    print(f"创建的文章ID: {post_id}")
    print(f"文章标题: {post_title}")


def test_browser_http_with_retry():
    """带重试的断言示例"""
    
    [浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
        method: GET
        url: /posts
        captures:
            posts_count: ["jsonpath", "$", "length"]
            first_post_id: ["jsonpath", "$[0].id"]
        asserts:
            - ["status", "eq", 200]
            - ["jsonpath", "$", "type", "array"]
            - ["jsonpath", "$", "length", "gt", 0]
            - ["jsonpath", "$[0].id", "exists"]
        retry_assertions:
            indices: [2, 3]  # 只重试第3和第4个断言
            count: 3
            interval: 1
    '''
    
    print(f"文章总数: {posts_count}")
    print(f"第一篇文章ID: {first_post_id}")


def test_browser_http_complex_workflow():
    """复杂的API工作流示例"""
    
    # 设置API客户端
    [设置浏览器HTTP客户端], 客户端名称: "api", 基础URL: "https://jsonplaceholder.typicode.com"
    
    # 1. 获取所有用户
    [浏览器HTTP请求], 客户端: "api", 配置: '''
        method: GET
        url: /users
        captures:
            users: ["jsonpath", "$"]
            user_count: ["jsonpath", "$", "length"]
            first_user_id: ["jsonpath", "$[0].id"]
        asserts:
            - ["status", "eq", 200]
            - ["jsonpath", "$", "type", "array"]
            - ["jsonpath", "$", "length", "gt", 5]
    '''
    
    # 2. 获取第一个用户的详细信息
    [浏览器HTTP请求], 客户端: "api", 配置: '''
        method: GET
        url: /users/${first_user_id}
        captures:
            user_name: ["jsonpath", "$.name"]
            user_company: ["jsonpath", "$.company.name"]
        asserts:
            - ["status", "eq", 200]
            - ["jsonpath", "$.id", "eq", ${first_user_id}]
            - ["jsonpath", "$.name", "exists"]
    '''
    
    # 3. 获取该用户的所有文章
    [浏览器HTTP请求], 客户端: "api", 配置: '''
        method: GET
        url: /posts
        request:
            params:
                userId: ${first_user_id}
        captures:
            user_posts: ["jsonpath", "$"]
            posts_count: ["jsonpath", "$", "length"]
        asserts:
            - ["status", "eq", 200]
            - ["jsonpath", "$", "type", "array"]
            - ["jsonpath", "$[0].userId", "eq", ${first_user_id}]
    '''
    
    # 4. 为该用户创建新文章
    [浏览器HTTP请求], 客户端: "api", 配置: '''
        method: POST
        url: /posts
        request:
            json:
                title: "来自${user_name}的新文章"
                body: "这是${user_name}在${user_company}工作时写的文章"
                userId: ${first_user_id}
        captures:
            new_post_id: ["jsonpath", "$.id"]
        asserts:
            - ["status", "eq", 201]
            - ["jsonpath", "$.userId", "eq", ${first_user_id}]
            - ["jsonpath", "$.title", "contains", "${user_name}"]
    '''
    
    print(f"工作流完成:")
    print(f"  用户总数: {user_count}")
    print(f"  选择用户: {user_name} (ID: {first_user_id})")
    print(f"  用户公司: {user_company}")
    print(f"  用户现有文章数: {posts_count}")
    print(f"  新创建文章ID: {new_post_id}")


def test_browser_http_error_handling():
    """错误处理和调试示例"""
    
    # 测试404错误
    try:
        [浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
            method: GET
            url: /users/999999  # 不存在的用户
            asserts:
                - ["status", "eq", 404]
        '''
        print("✓ 404错误处理正确")
    except AssertionError as e:
        print(f"✗ 404错误处理失败: {e}")
    
    # 保存响应进行调试
    [浏览器HTTP请求], 客户端: "jsonplaceholder", 保存响应: "debug_response", 配置: '''
        method: GET
        url: /users/1
        captures:
            debug_data: ["jsonpath", "$"]
    '''
    
    # 打印调试信息
    print("调试响应数据:")
    print(f"  状态码: {debug_response['status_code']}")
    print(f"  响应时间: {debug_response['elapsed_ms']}ms")
    print(f"  用户数据: {debug_data}")


def test_browser_http_file_upload_simulation():
    """模拟文件上传的示例"""
    
    # 模拟多媒体内容上传
    [浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
        method: POST
        url: /posts
        request:
            json:
                title: "包含图片的文章"
                body: "这篇文章包含图片内容"
                userId: 1
                media:
                    type: "image"
                    filename: "test-image.jpg"
                    size: 1024
        captures:
            media_post_id: ["jsonpath", "$.id"]
        asserts:
            - ["status", "eq", 201]
            - ["jsonpath", "$.media.type", "eq", "image"]
            - ["jsonpath", "$.media.filename", "contains", "test-image"]
    '''
    
    print(f"多媒体文章创建成功，ID: {media_post_id}")


if __name__ == "__main__":
    # 运行示例测试
    test_browser_http_basic_request()
    test_browser_http_post_request()
    test_browser_http_with_retry()
    test_browser_http_complex_workflow()
    test_browser_http_error_handling()
    test_browser_http_file_upload_simulation()
    
    print("所有浏览器HTTP示例测试完成！") 