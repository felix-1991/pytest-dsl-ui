# 简单重试逻辑测试

# 启动浏览器
[启动浏览器], 浏览器: "chromium", 配置: '''
    headless: true
    viewport:
        width: 1280
        height: 720
'''

[打印], 内容: "🚀 开始测试重试逻辑..."

# 测试1: 成功的断言（不会重试）
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts/1
    retry_assertions:
        all: true
        count: 2
        interval: 1
    captures:
        title: ["jsonpath", "$.title"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.id", "eq", 1]
        - ["jsonpath", "$.title", "exists"]
''', 步骤名称: "测试成功断言（不重试）"

[打印], 内容: "✅ 成功断言测试完成: ${title}"

# 测试2: 失败的断言（会重试）
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts/2
    retry_assertions:
        specific:
            "1": 
                count: 2
                interval: 0.5
    captures:
        post_id: ["jsonpath", "$.id"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.fake_field", "eq", "fake_value"]  # 这个会失败并重试2次
        - ["jsonpath", "$.id", "eq", 2]
''', 步骤名称: "测试失败断言重试"

[打印], 内容: "❌ 重试测试完成，Post ID: ${post_id}"

[关闭浏览器] 