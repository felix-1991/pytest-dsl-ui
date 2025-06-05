# 下载关键字测试DSL文件
@name: "下载关键字功能测试"
@description: "测试pytest-dsl-ui中的文件下载关键字功能"
@tags: [UI, 自动化, 下载, 测试]
@author: "assistant"

# 启动浏览器
[启动浏览器], 浏览器: "chromium", 无头模式: False

# 导航到测试页面
[打开页面], 地址: "file://./test_elements.html"

[打印], 内容: "开始测试下载关键字功能"

# 滚动到下载测试区域
[滚动元素到视野], 定位器: "h2:has-text('文件下载测试')"
[等待], 秒数: 1

# 1. 测试基本文件下载功能
[打印], 内容: "1. 测试基本文件下载功能..."

# 测试文本文件下载
download_path_txt = [等待下载], 触发元素: "#download-txt", 变量名: "txt_file_path"
[打印], 内容: "文本文件下载路径: ${download_path_txt}"
# 验证下载的文本文件
[验证下载文件], 文件路径: "${txt_file_path}", 最小文件大小: 100, 文件扩展名: ".txt"
[打印], 内容: "✅ 文本文件下载验证成功"

# 测试JSON文件下载
download_path_json = [等待下载], 触发元素: "#download-json", 变量名: "json_file_path"
[打印], 内容: "JSON文件下载路径: ${download_path_json}"

# 验证下载的JSON文件
[验证下载文件], 文件路径: "${json_file_path}", 最小文件大小: 100, 最大文件大小: 1000, 文件扩展名: ".json"
[打印], 内容: "✅ JSON文件下载验证成功"

# 2. 测试动态生成文件下载
[打印], 内容: "2. 测试动态生成文件下载..."

# 动态生成文本文件下载
dynamic_txt_path = [等待下载], 触发元素: "#download-dynamic-txt", 变量名: "dynamic_txt_path"
[打印], 内容: "动态文本文件路径: ${dynamic_txt_path}"

# 验证动态生成的文本文件
[验证下载文件], 文件路径: "${dynamic_txt_path}", 最小文件大小: 200, 文件扩展名: ".txt"
[打印], 内容: "✅ 动态文本文件验证成功"

# 动态生成CSV文件下载
dynamic_csv_path = [等待下载], 触发元素: "#download-dynamic-csv", 变量名: "dynamic_csv_path"
[打印], 内容: "动态CSV文件路径: ${dynamic_csv_path}"

# 验证动态生成的CSV文件
[验证下载文件], 文件路径: "${dynamic_csv_path}", 最小文件大小: 100, 文件扩展名: ".csv"
[打印], 内容: "✅ 动态CSV文件验证成功"

# 3. 测试不同大小文件下载
[打印], 内容: "3. 测试不同大小文件下载..."

# 小文件下载
small_file_path = [等待下载], 触发元素: "#download-small-file", 变量名: "small_file_path"
[验证下载文件], 文件路径: "${small_file_path}", 最小文件大小: 10, 最大文件大小: 1000
[打印], 内容: "✅ 小文件下载验证成功"

# 中等文件下载
medium_file_path = [等待下载], 触发元素: "#download-medium-file", 变量名: "medium_file_path"
[验证下载文件], 文件路径: "${medium_file_path}", 最小文件大小: 5000, 最大文件大小: 20000
[打印], 内容: "✅ 中等文件下载验证成功"

# 大文件下载
large_file_path = [等待下载], 触发元素: "#download-large-content", 变量名: "large_file_path"
[验证下载文件], 文件路径: "${large_file_path}", 最小文件大小: 50000, 最大文件大小: 200000
[打印], 内容: "✅ 大文件下载验证成功"

# 4. 测试特殊文件名下载
[打印], 内容: "4. 测试特殊文件名下载..."

# 带空格的文件名
spaces_file_path = [等待下载], 触发元素: "#download-with-spaces", 变量名: "spaces_file_path"
[验证下载文件], 文件路径: "${spaces_file_path}", 最小文件大小: 10
[打印], 内容: "✅ 带空格文件名下载验证成功"

# 中文文件名
chinese_file_path = [等待下载], 触发元素: "#download-chinese-name", 变量名: "chinese_file_path"
[验证下载文件], 文件路径: "${chinese_file_path}", 最小文件大小: 100
[打印], 内容: "✅ 中文文件名下载验证成功"

# 特殊字符文件名
special_file_path = [等待下载], 触发元素: "#download-special-chars", 变量名: "special_file_path"
[验证下载文件], 文件路径: "${special_file_path}", 最小文件大小: 10
[打印], 内容: "✅ 特殊字符文件名下载验证成功"

# 5. 测试下载监听功能
[打印], 内容: "5. 测试下载监听功能..."

# 开始监听下载
[监听下载], 监听时间: 5, 变量名: "monitored_downloads"

# 在监听期间触发一些下载
[点击元素], 定位器: "#download-small-file"
[等待], 秒数: 1
[点击元素], 定位器: "#download-dynamic-txt"
[等待], 秒数: 2

[打印], 内容: "监听到的下载: ${monitored_downloads}"

# 6. 测试批量下载场景
[打印], 内容: "6. 测试批量下载场景..."

# 快速连续触发多个下载
[等待下载], 触发元素: "#download-small-file", 变量名: "batch1"
[等待], 秒数: 0.5
[等待下载], 触发元素: "#download-dynamic-csv", 变量名: "batch2"
[等待], 秒数: 0.5
[等待下载], 触发元素: "#download-chinese-name", 变量名: "batch3"

# 验证批量下载的文件
[验证下载文件], 文件路径: "${batch1}"
[验证下载文件], 文件路径: "${batch2}"
[验证下载文件], 文件路径: "${batch3}"
[打印], 内容: "✅ 批量下载验证成功"

# 7. 测试下载超时场景
[打印], 内容: "7. 测试下载超时设置..."

# 使用较短的超时时间测试
timeout_file = [等待下载], 触发元素: "#download-medium-file", 超时时间: 10, 变量名: "timeout_test"
[验证下载文件], 文件路径: "${timeout_file}"
[打印], 内容: "✅ 下载超时设置验证成功"

# 8. 测试自定义保存路径
[打印], 内容: "8. 测试自定义保存路径..."

# 指定保存路径下载
custom_path_file = [等待下载], 触发元素: "#download-txt", 保存路径: "downloads/custom_test.txt", 变量名: "custom_path_file"
[验证下载文件], 文件路径: "${custom_path_file}"
[打印], 内容: "自定义路径下载文件: ${custom_path_file}"
[打印], 内容: "✅ 自定义保存路径验证成功"

# 9. 截图保存测试结果
[截图], 文件名: "download_test_result.png"

# 10. 清理下载文件
[打印], 内容: "10. 清理下载文件..."

# 清理测试生成的下载文件
cleanup_result = [清理下载文件], 下载目录: "downloads", 文件模式: "*.txt", 变量名: "cleanup_info"
[打印], 内容: "清理结果: ${cleanup_result}"

# 清理CSV文件
[清理下载文件], 下载目录: "downloads", 文件模式: "*.csv"
[打印], 内容: "✅ 下载文件清理完成"

# 11. 测试下载结果验证
[打印], 内容: "11. 验证下载功能测试结果..."

# 获取下载结果显示内容
download_result_text = [获取元素文本], 定位器: "#download-result"
[打印], 内容: "下载结果显示: ${download_result_text}"

# 验证页面标题
page_title = [获取页面标题]
[断言页面标题], 期望标题: "元素操作关键字测试页面", 匹配方式: exact

[打印], 内容: "所有下载关键字测试完成！"

# 12. 关闭浏览器
[关闭浏览器] 