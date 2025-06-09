@name: "JSONPlaceholder浏览器HTTP API测试"
@description: "验证浏览器HTTP功能使用JSONPlaceholder的免费API"
@author: "pytest-dsl-ui"

# 基础API测试
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
        - ["jsonpath", "$.userId", "type", "int"]
''', 步骤名称: "获取文章1的详情"

[打印], 内容: "文章标题: ${post_title}"
[打印], 内容: "作者ID: ${post_user_id}"

# 根据捕获的用户ID获取用户信息
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/users/${post_user_id}
    captures:
        user_name: ["jsonpath", "$.name"]
        user_email: ["jsonpath", "$.email"]
        user_company: ["jsonpath", "$.company.name"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.id", "eq", ${post_user_id}]
        - ["jsonpath", "$.name", "exists"]
        - ["jsonpath", "$.email", "regex", "^[\\w\\.-]+@[\\w\\.-]+\\.[a-zA-Z]{2,}$"]
''', 步骤名称: "获取作者信息"

[打印], 内容: "作者姓名: ${user_name}"
[打印], 内容: "作者邮箱: ${user_email}"
[打印], 内容: "作者公司: ${user_company}"

# 获取该用户的所有文章
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts
    request:
        params:
            userId: ${post_user_id}
    captures:
        posts_count: ["jsonpath", "$", "length"]
        first_post_title: ["jsonpath", "$[0].title"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$", "type", "array"]
        - ["jsonpath", "$", "length", "gt", 0]
        - ["jsonpath", "$[*].userId", "all", "eq", ${post_user_id}]
''', 步骤名称: "获取用户的所有文章"

[打印], 内容: "用户${user_name}共有${posts_count}篇文章"
[打印], 内容: "第一篇文章标题: ${first_post_title}"

# 创建新文章（POST请求）
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: POST
    url: https://jsonplaceholder.typicode.com/posts
    request:
        headers:
            Content-Type: application/json
        json:
            title: "通过浏览器HTTP创建的测试文章"
            body: "这是一篇通过pytest-dsl-ui浏览器HTTP功能创建的测试文章"
            userId: ${post_user_id}
    captures:
        new_post_id: ["jsonpath", "$.id"]
        new_post_title: ["jsonpath", "$.title"]
    asserts:
        - ["status", "eq", 201]
        - ["jsonpath", "$.title", "eq", "通过浏览器HTTP创建的测试文章"]
        - ["jsonpath", "$.userId", "eq", ${post_user_id}]
        - ["jsonpath", "$.id", "exists"]
''', 步骤名称: "创建新文章"

[打印], 内容: "成功创建文章，ID: ${new_post_id}"

# 更新文章（PUT请求）
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: PUT
    url: https://jsonplaceholder.typicode.com/posts/${new_post_id}
    request:
        headers:
            Content-Type: application/json
        json:
            id: ${new_post_id}
            title: "更新后的文章标题"
            body: "这是更新后的文章内容"
            userId: ${post_user_id}
    captures:
        updated_title: ["jsonpath", "$.title"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.title", "eq", "更新后的文章标题"]
        - ["jsonpath", "$.id", "eq", ${new_post_id}]
''', 步骤名称: "更新文章"

[打印], 内容: "文章更新成功，新标题: ${updated_title}"

# 部分更新文章（PATCH请求）
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: PATCH
    url: https://jsonplaceholder.typicode.com/posts/${new_post_id}
    request:
        headers:
            Content-Type: application/json
        json:
            title: "通过PATCH更新的标题"
    captures:
        patched_title: ["jsonpath", "$.title"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.title", "eq", "通过PATCH更新的标题"]
        - ["jsonpath", "$.id", "eq", ${new_post_id}]
''', 步骤名称: "部分更新文章"

[打印], 内容: "文章部分更新成功，标题: ${patched_title}"

# 删除文章（DELETE请求）
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: DELETE
    url: https://jsonplaceholder.typicode.com/posts/${new_post_id}
    asserts:
        - ["status", "eq", 200]
''', 步骤名称: "删除文章"

[打印], 内容: "文章${new_post_id}删除成功"

# 测试错误处理
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts/999999
    asserts:
        - ["status", "eq", 404]
        - ["jsonpath", "$", "eq", {}]
''', 步骤名称: "测试404错误处理"

[打印], 内容: "错误处理测试完成"

# 测试查询参数
[浏览器HTTP请求], 客户端: "jsonplaceholder", 配置: '''
    method: GET
    url: https://jsonplaceholder.typicode.com/posts
    request:
        params:
            _page: 1
            _limit: 5
    captures:
        limited_posts_count: ["jsonpath", "$", "length"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$", "length", "eq", 5]
        - ["header", "x-total-count", "exists"]
''', 步骤名称: "测试分页参数"

[打印], 内容: "分页测试完成，返回${limited_posts_count}条记录"

teardown do
    [打印], 内容: "JSONPlaceholder API测试全部完成！"
end 