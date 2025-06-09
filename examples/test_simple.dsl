@name: "简单测试"
@description: "测试页面ID获取"

# 启动浏览器
[启动浏览器], 浏览器: "chromium", 无头模式: False

# 打开页面并调试返回值
[打印], 内容: "开始打开页面..."
main_page_result = [打开页面], 地址: "https://www.baidu.com"
[打印], 内容: "页面打开结果:"
[打印], 内容: "${main_page_result}"

# 直接获取页面列表，不使用变量名参数
page_list_result = [获取页面列表]
[打印], 内容: "页面列表结果:"
[打印], 内容: "${page_list_result}"

[关闭浏览器] 