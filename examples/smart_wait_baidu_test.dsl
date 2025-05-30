@name: "智能等待百度搜索测试"
@description: "利用Playwright智能等待机制的百度搜索测试"
@tags: [UI, 自动化, 百度, 智能等待]
@author: "pytest-dsl-ui"

# 启动浏览器
[启动浏览器], 浏览器: "chromium", 无头模式: False, 视口宽度: 1920, 视口高度: 1080

# 打开百度首页
[打开页面], 地址: "https://www.baidu.com"

# 获取页面标题
title = [获取页面标题]
[打印], 内容: "页面标题: ${title}"

# 直接点击搜索框（Playwright会自动等待元素可交互）
[点击元素], 定位器: "role=textbox"

# 输入搜索内容
[输入文本], 定位器: "role=textbox", 文本: "pytest自动化测试框架"

# 截图保存输入后的状态
[截图], 文件名: "smart_wait_input.png"

# 点击搜索按钮 - 使用改进的角色定位器
[点击元素], 定位器: "role=button:百度一下"

# 截图保存搜索结果（Playwright会等待页面稳定）
[截图], 文件名: "smart_wait_results.png"

# 获取当前URL
current_url = [获取当前地址]
[打印], 内容: "搜索结果页URL: ${current_url}"

# 关闭浏览器
[关闭浏览器]
