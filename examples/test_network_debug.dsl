@name: "网络关键字数据结构调试测试"
@description: "调试网络监听返回的数据结构，检查是否存在问题"
@author: "pytest-dsl-ui"

# 启动浏览器
[启动浏览器], 浏览器类型: "chromium", headless: False, 慢动作: 500

[打印], 内容: "🔍 开始网络数据结构调试..."

# 开始网络监听
[开始网络监听], 变量名: "monitoring_status"
[打印], 内容: "监听状态: ${monitoring_status}"

# 访问一个简单的页面
[打开页面], 地址: "https://httpbin.org/html"
[等待], 秒数: 3

# 获取所有网络请求和响应
[获取网络请求], 变量名: "all_requests"
[获取网络响应], 变量名: "all_responses"

# 打印所有请求和响应的详细信息
[打印], 内容: "=== 所有请求数据 ==="
[打印], 内容: "all_requests: ${all_requests}"
[打印], 内容: "=== 所有响应数据 ==="
[打印], 内容: "all_responses: ${all_responses}"

# 测试不同的URL模式
[打印], 内容: "=== 测试URL模式过滤 ==="

# 尝试不同的URL模式
[获取网络请求], URL模式: "httpbin", 变量名: "httpbin_requests_simple"
[打印], 内容: "httpbin模式请求: ${httpbin_requests_simple}"

[获取网络请求], URL模式: "httpbin.org", 变量名: "httpbin_requests_dot"
[打印], 内容: "httpbin.org模式请求: ${httpbin_requests_dot}"

[获取网络请求], URL模式: "html", 变量名: "html_requests"
[打印], 内容: "html模式请求: ${html_requests}"

[获取网络请求], URL模式: ".*", 变量名: "all_pattern_requests"
[打印], 内容: ".*模式请求: ${all_pattern_requests}"

# 测试响应过滤
[获取网络响应], URL模式: "httpbin", 变量名: "httpbin_responses_simple"
[打印], 内容: "httpbin模式响应: ${httpbin_responses_simple}"

[获取网络响应], URL模式: ".*", 变量名: "all_pattern_responses"
[打印], 内容: ".*模式响应: ${all_pattern_responses}"

# 访问另一个页面看看数据变化
[打印], 内容: "=== 访问JSON页面后的数据 ==="
[打开页面], 地址: "https://httpbin.org/json"
[等待], 秒数: 2

[获取网络请求], 变量名: "requests_after_json"
[获取网络响应], 变量名: "responses_after_json"

[打印], 内容: "JSON页面后的请求: ${requests_after_json}"
[打印], 内容: "JSON页面后的响应: ${responses_after_json}"

# 测试JSON页面的过滤
[获取网络请求], URL模式: "json", 变量名: "json_requests"
[获取网络响应], URL模式: "json", 变量名: "json_responses"

[打印], 内容: "json模式请求: ${json_requests}"
[打印], 内容: "json模式响应: ${json_responses}"

# 停止监听
[停止网络监听]

teardown do
    [打印], 内容: "🔍 网络数据结构调试完成"
    [关闭浏览器]
end 