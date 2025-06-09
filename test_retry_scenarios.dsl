# 重试场景详细测试

[启动浏览器], 浏览器: "chromium", 配置: '''
    headless: true
'''

[打印], 内容: "🧪 开始测试各种重试场景..."

# 场景1: 无重试配置 - 正常成功
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts/1
    captures:
        normal_title: ["jsonpath", "$.title"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.id", "eq", 1]
''', 步骤名称: "无重试配置-成功案例"

[打印], 内容: "✅ 场景1完成: ${normal_title}"

# 场景2: 测试索引重试 - 只重试指定索引的断言
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts/2
    retry_assertions:
        indices: [0]  # 只重试第0个断言
        count: 1
        interval: 0.3
    captures:
        index_title: ["jsonpath", "$.title"]
    asserts:
        - ["jsonpath", "$.nonexistent1", "exists"]  # 索引0 - 会重试1次
        - ["jsonpath", "$.nonexistent2", "exists"]  # 索引1 - 不会重试
''', 步骤名称: "索引重试测试"

[打印], 内容: "⚠️ 场景2应该失败: ${index_title}"

[关闭浏览器]

[打印], 内容: "🎯 重试场景测试完成！" 