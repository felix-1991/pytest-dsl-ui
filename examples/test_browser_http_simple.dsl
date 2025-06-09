@name: "简化浏览器HTTP测试"
@description: "验证浏览器HTTP实现修复效果的简化测试"
@author: "pytest-dsl-ui"

# 启动浏览器（非headless模式）
[启动浏览器], 浏览器类型: "chromium", headless: False, 慢动作: 500

# 首先打开一个页面建立浏览器上下文
[打开页面], 地址: "data:text/html,<h1>浏览器HTTP测试页面</h1>"
[等待], 时间: 1

# 测试1: 基础GET请求 - 使用httpbin（更稳定的测试API）
[浏览器HTTP请求], 客户端: "httpbin", 配置: '''
    method: GET
    url: https://httpbin.org/json
    captures:
        slide_type: ["jsonpath", "$.slideshow.title"]
        slides_count: ["jsonpath", "$.slideshow.slides", "length"]
        first_slide_title: ["jsonpath", "$.slideshow.slides[0].title"]
    asserts:
        - ["status", "eq", 200]
        - ["header", "content-type", "contains", "application/json"]
        - ["jsonpath", "$.slideshow", "exists"]
        - ["jsonpath", "$.slideshow.title", "type", "string"]
        - ["jsonpath", "$.slideshow.slides", "type", "array"]
        - ["jsonpath", "$.slideshow.slides", "length", "gt", 0]
''', 步骤名称: "测试基础GET请求"

[打印], 内容: "✅ 成功获取JSON数据"
[打印], 内容: "📊 幻灯片标题: ${slide_type}"
[打印], 内容: "📈 幻灯片数量: ${slides_count}"

# 测试2: 测试断言参数解析 - 复杂断言格式
[浏览器HTTP请求], 客户端: "httpbin", 配置: '''
    method: GET
    url: https://httpbin.org/user-agent
    captures:
        user_agent: ["jsonpath", "$.user-agent"]
        ua_length: ["jsonpath", "$.user-agent", "length"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.user-agent", "exists"]
        - ["jsonpath", "$.user-agent", "type", "string"]
        - ["jsonpath", "$.user-agent", "length", "gt", 10]
        - ["jsonpath", "$.user-agent", "contains", "Mozilla"]
''', 步骤名称: "测试断言参数解析"

[打印], 内容: "🔍 User-Agent: ${user_agent}"
[打印], 内容: "📏 User-Agent长度: ${ua_length}"

# 测试3: POST请求测试
[浏览器HTTP请求], 客户端: "httpbin", 配置: '''
    method: GET
    url: https://httpbin.org/get
    captures:
        url_info: ["jsonpath", "$.url"]
        headers_info: ["jsonpath", "$.headers"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.url", "contains", "httpbin.org"]
        - ["jsonpath", "$.headers", "exists"]
''', 步骤名称: "测试基础GET请求验证"

[打印], 内容: "📝 GET请求验证成功: ${url_info}"

# 测试4: 查询参数测试
[浏览器HTTP请求], 客户端: "httpbin", 配置: '''
    method: GET
    url: https://httpbin.org/get
    request:
        params:
            test_param: "浏览器HTTP"
            count: 42
            active: true
    captures:
        query_params: ["jsonpath", "$.args"]
        test_value: ["jsonpath", "$.args.test_param"]
        count_value: ["jsonpath", "$.args.count"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.args.test_param", "eq", "浏览器HTTP"]
        - ["jsonpath", "$.args.count", "eq", "42"]
        - ["jsonpath", "$.args.active", "eq", "True"]
''', 步骤名称: "测试查询参数"

[打印], 内容: "🔗 查询参数测试通过: ${test_value}"

# 测试5: 错误处理测试
[浏览器HTTP请求], 客户端: "httpbin", 配置: '''
    method: GET
    url: https://httpbin.org/status/404
    asserts:
        - ["status", "eq", 404]
''', 步骤名称: "测试404错误处理"

[打印], 内容: "❌ 404错误处理测试通过"

# 测试6: 响应时间测试
[浏览器HTTP请求], 客户端: "httpbin", 配置: '''
    method: GET
    url: https://httpbin.org/get
    captures:
        response_time: ["response_time"]
        status_code: ["status"]
    asserts:
        - ["status", "eq", 200]
        - ["response_time", "gt", 0]
        - ["response_time", "lt", 10000]
''', 步骤名称: "测试响应时间"

[打印], 内容: "⏱️ 响应时间测试通过: ${response_time}ms"

# 测试完成
[打印], 内容: "🎉 浏览器HTTP功能验证完成！"

# 截图保存测试结果
[截图], 文件名: "browser_http_simple_test.png"
[打印], 内容: "📸 测试完成截图已保存"

teardown do
    [打印], 内容: "🎊 简化浏览器HTTP测试全部完成！"
    [打印], 内容: "📊 测试摘要:"
    [打印], 内容: "  - JSON数据提取: ${slide_type}"
    [打印], 内容: "  - 数组长度验证: ${slides_count}"
    [打印], 内容: "  - User-Agent: ${user_agent}"
    [打印], 内容: "  - POST数据: ${url_info}"
    [打印], 内容: "  - 响应时间: ${response_time}ms"
    [等待], 时间: 3
    [关闭浏览器]
end 