# 测试浏览器HTTP重试逻辑功能

# 首先启动浏览器
[启动浏览器], 浏览器: "chromium", 配置: '''
    headless: true
    viewport:
        width: 1280
        height: 720
'''

# 测试1: 全局重试配置测试
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts/1
    retry_assertions:
        all: true
        count: 3
        interval: 1
    captures:
        post_title: ["jsonpath", "$.title"]
        post_id: ["jsonpath", "$.id"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.id", "eq", 1]
        - ["jsonpath", "$.title", "exists"]
        - ["jsonpath", "$.nonexistent", "eq", "should_fail"]  # 这个会失败并重试
''', 步骤名称: "测试全局重试配置"

[打印], 内容: "🔄 全局重试测试完成: ${post_title}"

# 测试2: 特定断言重试配置测试
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts/2
    retry_assertions:
        specific:
            "1": 
                count: 2
                interval: 0.5
            "3":
                count: 3
                interval: 1
    captures:
        post_content: ["jsonpath", "$.body"]
        user_id: ["jsonpath", "$.userId"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.userId", "eq", 1]  # 索引1 - 会重试2次
        - ["jsonpath", "$.id", "eq", 2]
        - ["jsonpath", "$.fake_field", "exists"]  # 索引3 - 会重试3次
''', 步骤名称: "测试特定断言重试配置"

[打印], 内容: "🎯 特定重试测试完成: User ${user_id}"

# 测试3: 索引列表重试配置测试
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts/3
    retry_assertions:
        indices: [1, 2]
        count: 2
        interval: 0.8
    captures:
        title_content: ["jsonpath", "$.title"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.wrong_field", "eq", "fail"]  # 索引1 - 会重试
        - ["jsonpath", "$.another_wrong", "exists"]    # 索引2 - 会重试
        - ["jsonpath", "$.title", "exists"]           # 索引3 - 不会重试
''', 步骤名称: "测试索引列表重试配置"

[打印], 内容: "📋 索引重试测试完成: ${title_content}"

# 测试4: 混合重试配置测试（命令行参数）
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts/4
    captures:
        final_title: ["jsonpath", "$.title"]
        final_id: ["jsonpath", "$.id"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.id", "eq", 4]
        - ["jsonpath", "$.title", "exists"]
        - ["jsonpath", "$.missing_data", "eq", "will_fail"]  # 会根据命令行参数重试
''', 断言重试次数: 2, 断言重试间隔: 1, 步骤名称: "测试命令行重试参数"

[打印], 内容: "⚙️ 命令行重试测试完成: ${final_title}"

[打印], 内容: "🎉 所有重试逻辑测试完成！"

# 关闭浏览器
[关闭浏览器] 