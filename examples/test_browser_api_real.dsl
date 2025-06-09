@name: "真实浏览器API测试"
@description: "在非headless浏览器模式下测试API功能"
@author: "pytest-dsl-ui"

# 启动浏览器（非headless模式）
[启动浏览器], 浏览器类型: "chromium", headless: False, 慢动作: 1000

# 首先打开一个页面建立浏览器上下文
[打开页面], 地址: "https://jsonplaceholder.typicode.com"
[等待], 时间: 2

# 测试1: 基础GET请求 - 获取文章详情
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts/1
    captures:
        post_title: ["jsonpath", "$.title"]
        post_body: ["jsonpath", "$.body"]
        post_user_id: ["jsonpath", "$.userId"]
    asserts:
        - ["status", "eq", 200]
        - ["header", "content-type", "contains", "application/json"]
        - ["jsonpath", "$.id", "eq", 1]
        - ["jsonpath", "$.title", "exists"]
        - ["jsonpath", "$.body", "exists"]
        - ["jsonpath", "$.userId", "type", "number"]
''', 步骤名称: "获取文章1的详情"

[打印], 内容: "✅ 成功获取文章: ${post_title}"
[打印], 内容: "👤 作者ID: ${post_user_id}"

# 测试2: 根据捕获的用户ID获取用户信息
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/users/${post_user_id}
    captures:
        user_name: ["jsonpath", "$.name"]
        user_email: ["jsonpath", "$.email"]
        user_company: ["jsonpath", "$.company.name"]
        user_website: ["jsonpath", "$.website"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.id", "eq", ${post_user_id}]
        - ["jsonpath", "$.name", "exists"]
        - ["jsonpath", "$.email", "regex", "^[\\w\\.-]+@[\\w\\.-]+\\.[a-zA-Z]{2,}$"]
        - ["jsonpath", "$.company.name", "exists"]
''', 步骤名称: "获取作者信息"

[打印], 内容: "👨‍💼 作者姓名: ${user_name}"
[打印], 内容: "📧 作者邮箱: ${user_email}"
[打印], 内容: "🏢 作者公司: ${user_company}"
[打印], 内容: "🌐 作者网站: ${user_website}"

# 测试3: 获取该用户的所有文章
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts
    request:
        params:
            userId: ${post_user_id}
    captures:
        posts_count: ["jsonpath", "$", "length"]
        first_post_title: ["jsonpath", "$[0].title"]
        all_titles: ["jsonpath", "$[*].title"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$", "type", "array"]
        - ["jsonpath", "$", "length", "gt", 0]
        - ["jsonpath", "$[*].userId", "all", "eq", ${post_user_id}]
        - ["jsonpath", "$", "length", "lte", 20]
''', 步骤名称: "获取用户的所有文章"

[打印], 内容: "📚 用户${user_name}共有${posts_count}篇文章"
[打印], 内容: "📖 第一篇文章: ${first_post_title}"

# 测试4: 创建新文章（POST请求）
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: POST
    url: https://jsonplaceholder.typicode.com/posts
    request:
        headers:
            Content-Type: application/json
        json:
            title: "通过浏览器HTTP创建的测试文章"
            body: "这是一篇通过pytest-dsl-ui浏览器HTTP功能创建的测试文章，作者是${user_name}"
            userId: ${post_user_id}
    captures:
        new_post_id: ["jsonpath", "$.id"]
        new_post_title: ["jsonpath", "$.title"]
        created_body: ["jsonpath", "$.body"]
    asserts:
        - ["status", "eq", 201]
        - ["jsonpath", "$.title", "eq", "通过浏览器HTTP创建的测试文章"]
        - ["jsonpath", "$.userId", "eq", ${post_user_id}]
        - ["jsonpath", "$.id", "exists"]
        - ["jsonpath", "$.id", "type", "number"]
''', 步骤名称: "创建新文章"

[打印], 内容: "✅ 成功创建文章，ID: ${new_post_id}"
[打印], 内容: "📝 新文章标题: ${new_post_title}"

# 测试5: 更新文章（PUT请求）
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: PUT
    url: https://jsonplaceholder.typicode.com/posts/${new_post_id}
    request:
        headers:
            Content-Type: application/json
        json:
            id: ${new_post_id}
            title: "更新后的文章标题 - ${user_name}的作品"
            body: "这是更新后的文章内容，原作者是${user_name}，来自${user_company}公司"
            userId: ${post_user_id}
    captures:
        updated_title: ["jsonpath", "$.title"]
        updated_body: ["jsonpath", "$.body"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.title", "contains", ${user_name}]
        - ["jsonpath", "$.id", "eq", ${new_post_id}]
        - ["jsonpath", "$.body", "contains", ${user_company}]
''', 步骤名称: "更新文章"

[打印], 内容: "🔄 文章更新成功: ${updated_title}"

# 测试6: 部分更新文章（PATCH请求）
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: PATCH
    url: https://jsonplaceholder.typicode.com/posts/${new_post_id}
    request:
        headers:
            Content-Type: application/json
        json:
            title: "通过PATCH更新的标题 - 最终版本"
    captures:
        patched_title: ["jsonpath", "$.title"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.title", "eq", "通过PATCH更新的标题 - 最终版本"]
        - ["jsonpath", "$.id", "eq", ${new_post_id}]
''', 步骤名称: "部分更新文章"

[打印], 内容: "🔧 文章部分更新成功: ${patched_title}"

# 测试7: 获取文章评论
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/comments
    request:
        params:
            postId: 1
            _limit: 3
    captures:
        comments_count: ["jsonpath", "$", "length"]
        first_comment: ["jsonpath", "$[0].body"]
        comment_emails: ["jsonpath", "$[*].email"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$", "type", "array"]
        - ["jsonpath", "$", "length", "eq", 3]
        - ["jsonpath", "$[0].postId", "eq", 1]
        - ["jsonpath", "$[*].email", "all", "regex", "^[\\w\\.-]+@[\\w\\.-]+\\.[a-zA-Z]{2,}$"]
''', 步骤名称: "获取文章评论"

[打印], 内容: "💬 获取到${comments_count}条评论"
[打印], 内容: "📝 第一条评论: ${first_comment}"

# 测试8: 测试错误处理 - 404
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts/999999
    asserts:
        - ["status", "eq", 404]
        - ["jsonpath", "$", "eq", {}]
''', 步骤名称: "测试404错误处理"

[打印], 内容: "❌ 404错误处理测试通过"

# 测试9: 删除文章（DELETE请求）
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: DELETE
    url: https://jsonplaceholder.typicode.com/posts/${new_post_id}
    asserts:
        - ["status", "eq", 200]
''', 步骤名称: "删除文章"

[打印], 内容: "🗑️ 文章${new_post_id}删除成功"

# 测试10: 测试复杂查询参数
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts
    request:
        params:
            _page: 1
            _limit: 5
            _sort: id
            _order: desc
    captures:
        limited_posts_count: ["jsonpath", "$", "length"]
        first_post_id: ["jsonpath", "$[0].id"]
        last_post_id: ["jsonpath", "$[-1].id"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$", "length", "eq", 5]
        - ["header", "x-total-count", "exists"]
        - ["jsonpath", "$[0].id", "gt", "$[-1].id"]
''', 步骤名称: "测试复杂查询参数"

[打印], 内容: "📊 分页测试完成，返回${limited_posts_count}条记录"
[打印], 内容: "🔢 ID范围: ${first_post_id} 到 ${last_post_id}"

# 在浏览器中显示测试结果页面
[打开页面], 地址: "https://jsonplaceholder.typicode.com/guide"
[等待], 时间: 3
[打印], 内容: "📖 浏览器中已打开JSONPlaceholder指南页面"

# 截图保存测试结果
[截图], 文件名: "browser_api_test_completed.png"
[打印], 内容: "📸 测试完成截图已保存"

teardown do
    [打印], 内容: "🎉 浏览器API测试全部完成！"
    [打印], 内容: "📊 测试摘要:"
    [打印], 内容: "  - 获取用户信息: ${user_name} (${user_email})"
    [打印], 内容: "  - 用户文章数量: ${posts_count}"
    [打印], 内容: "  - 创建文章ID: ${new_post_id}"
    [打印], 内容: "  - 最终文章标题: ${patched_title}"
    [打印], 内容: "  - 评论数量: ${comments_count}"
    [等待], 时间: 5
    [关闭浏览器]
end 