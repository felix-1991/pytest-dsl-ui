@name: "简单浏览器API测试"
@description: "简单验证浏览器HTTP功能"
@author: "pytest-dsl-ui"

# 启动浏览器（非headless模式）
[启动浏览器], 浏览器类型: "chromium", headless: False, 慢动作: 1000

# 测试1: 直接进行API请求，无需先打开页面
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts/1
    captures:
        post_title: ["jsonpath", "$.title"]
        post_id: ["jsonpath", "$.id"]
        post_user_id: ["jsonpath", "$.userId"]
    asserts:
        - ["status", "eq", 200]
        - ["header", "content-type", "contains", "application/json"]
        - ["jsonpath", "$.id", "eq", 1]
        - ["jsonpath", "$.title", "exists"]
        - ["jsonpath", "$.userId", "type", "number"]
''', 步骤名称: "获取文章详情"

[打印], 内容: "✅ 成功获取文章: ${post_title}"
[打印], 内容: "👤 作者ID: ${post_user_id}"

# 测试2: 根据捕获的用户ID获取用户信息
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/users/${post_user_id}
    captures:
        user_name: ["jsonpath", "$.name"]
        user_email: ["jsonpath", "$.email"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.id", "eq", ${post_user_id}]
        - ["jsonpath", "$.name", "exists"]
        - ["jsonpath", "$.email", "exists"]
''', 步骤名称: "获取用户信息"

[打印], 内容: "👨‍💼 用户姓名: ${user_name}"
[打印], 内容: "📧 用户邮箱: ${user_email}"

# 测试3: 创建新文章
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: POST
    url: https://jsonplaceholder.typicode.com/posts
    request:
        headers:
            Content-Type: application/json
        json:
            title: "浏览器HTTP测试文章"
            body: "这是通过浏览器HTTP功能创建的文章"
            userId: ${post_user_id}
    captures:
        new_post_id: ["jsonpath", "$.id"]
        new_post_title: ["jsonpath", "$.title"]
    asserts:
        - ["status", "eq", 201]
        - ["jsonpath", "$.title", "eq", "浏览器HTTP测试文章"]
        - ["jsonpath", "$.userId", "eq", ${post_user_id}]
        - ["jsonpath", "$.id", "exists"]
''', 步骤名称: "创建新文章"

[打印], 内容: "✅ 成功创建文章，ID: ${new_post_id}"

# 现在打开一个简单页面显示测试完成
[打开页面], 地址: "https://httpbin.org/html"
[等待], 时间: 2

# 截图保存测试结果  
[截图], 文件名: "simple_browser_api_test.png"
[打印], 内容: "📸 测试结果截图已保存"

teardown do
    [打印], 内容: "🎉 简单浏览器API测试完成！"
    [等待], 时间: 3
    [关闭浏览器]
end 