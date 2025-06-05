# 元素操作关键字测试DSL文件
@name: "元素操作关键字全面测试"
@description: "测试pytest-dsl-ui中的所有元素操作关键字功能"
@tags: [UI, 自动化, 元素操作, 测试]
@author: "assistant"

# 启动浏览器
[启动浏览器], 浏览器: "chromium", 无头模式: False

# 导航到测试页面
[打开页面], 地址: "file://./test_elements.html"

[打印], 内容: "开始测试所有元素操作关键字功能"

# 2. 测试基础点击操作
[打印], 内容: "测试基础点击操作..."
[点击元素], 定位器: "#single-click-btn"
[等待], 秒数: 1

click_result = [获取元素文本], 定位器: "#click-result"
[打印], 内容: "单击结果: ${click_result}"
[断言文本内容], 定位器: "#click-result", 期望文本: "单击操作成功", 匹配方式: contains

[双击元素], 定位器: "#double-click-btn"
[等待], 秒数: 1

dblclick_result = [获取元素文本], 定位器: "#click-result"
[打印], 内容: "双击结果: ${dblclick_result}"
[断言文本内容], 定位器: "#click-result", 期望文本: "双击操作成功", 匹配方式: contains

[右键点击元素], 定位器: "#right-click-btn"
[等待], 秒数: 1

rightclick_result = [获取元素文本], 定位器: "#click-result"
[打印], 内容: "右键点击结果: ${rightclick_result}"
[断言文本内容], 定位器: "#click-result", 期望文本: "右键点击成功", 匹配方式: contains

[悬停元素], 定位器: "#hover-btn"
[等待], 秒数: 1

hover_result = [获取元素文本], 定位器: "#click-result"
[打印], 内容: "悬停结果: ${hover_result}"
[断言文本内容], 定位器: "#click-result", 期望文本: "悬停操作触发", 匹配方式: contains

# 3. 测试文本输入操作
[打印], 内容: "测试文本输入操作..."
[输入文本], 定位器: "#text-input", 文本: "自动化测试文本", 清空输入框: True

text_value = [获取元素属性], 定位器: "#text-input", 属性: "value"
[打印], 内容: "输入的文本值: ${text_value}"
[断言输入值], 定位器: "#text-input", 期望值: "自动化测试文本"

[输入文本], 定位器: "#password-input", 文本: "testPassword123"
[输入文本], 定位器: "#email-input", 文本: "test@automation.com"
[输入文本], 定位器: "#textarea", 文本: "多行文本测试\\n第二行内容\\n第三行内容"

# 测试逐字符输入
[清空文本], 定位器: "#text-input"
[逐字符输入], 定位器: "#text-input", 文本: "逐字符输入测试", 延迟: 50

typed_text = [获取元素属性], 定位器: "#text-input", 属性: "value"
[打印], 内容: "逐字符输入结果: ${typed_text}"
[断言输入值], 定位器: "#text-input", 期望值: "逐字符输入测试"

# 4. 测试复选框操作
[打印], 内容: "测试复选框操作..."

# 先检查初始状态
reading_initial = [获取元素属性], 定位器: "#hobby-reading", 属性: "checked"
[打印], 内容: "阅读复选框初始状态: ${reading_initial}"

[勾选复选框], 定位器: "#hobby-reading"
[等待], 秒数: 1
[勾选复选框], 定位器: "#hobby-music"
[等待], 秒数: 1
[勾选复选框], 定位器: "#hobby-sports"
[等待], 秒数: 1

# 验证复选框是否被选中
reading_checked = [获取元素属性], 定位器: "#hobby-reading", 属性: "checked"
[打印], 内容: "阅读复选框状态: ${reading_checked}"
[断言复选框状态], 定位器: "#hobby-reading", 期望状态: True, 消息: "阅读复选框应该被选中"

# 取消勾选某个复选框
[取消勾选复选框], 定位器: "#hobby-music"
music_checked = [获取元素属性], 定位器: "#hobby-music", 属性: "checked"
[打印], 内容: "音乐复选框状态: ${music_checked}"
[断言复选框状态], 定位器: "#hobby-music", 期望状态: False, 消息: "音乐复选框应该被取消选中"

# 使用设置复选框状态
[设置复选框状态], 定位器: "#hobby-travel", 选中状态: True
travel_checked = [获取元素属性], 定位器: "#hobby-travel", 属性: "checked"
[打印], 内容: "旅行复选框状态: ${travel_checked}"

[设置复选框状态], 定位器: "#hobby-travel", 选中状态: False
travel_unchecked = [获取元素属性], 定位器: "#hobby-travel", 属性: "checked"
[打印], 内容: "旅行复选框取消状态: ${travel_unchecked}"

# 5. 测试单选框操作
[打印], 内容: "测试单选框操作..."
[选择单选框], 定位器: "#gender-male"
male_selected = [获取元素属性], 定位器: "#gender-male", 属性: "checked"
[打印], 内容: "男性单选框状态: ${male_selected}"

[选择单选框], 定位器: "#gender-female"
female_selected = [获取元素属性], 定位器: "#gender-female", 属性: "checked"
[打印], 内容: "女性单选框状态: ${female_selected}"

# 验证之前的单选框应该被取消选择
male_unselected = [获取元素属性], 定位器: "#gender-male", 属性: "checked"
[打印], 内容: "男性单选框更新状态: ${male_unselected}"

# 6. 测试下拉选择操作
[打印], 内容: "测试下拉选择操作..."

# 通过值选择
[选择下拉选项], 定位器: "#city-select", 选项值: "shanghai"
selected_city = [获取元素属性], 定位器: "#city-select", 属性: "value"
[打印], 内容: "通过值选择的城市: ${selected_city}"
[断言输入值], 定位器: "#city-select", 期望值: "shanghai"

# 通过标签选择
[选择下拉选项], 定位器: "#city-select", 选项标签: "北京"
selected_city_by_label = [获取元素属性], 定位器: "#city-select", 属性: "value"
[打印], 内容: "通过标签选择的城市: ${selected_city_by_label}"
[断言输入值], 定位器: "#city-select", 期望值: "beijing"

# 通过索引选择
[选择下拉选项], 定位器: "#city-select", 选项索引: 3
selected_city_by_index = [获取元素属性], 定位器: "#city-select", 属性: "value"
[打印], 内容: "通过索引选择的城市: ${selected_city_by_index}"
[断言输入值], 定位器: "#city-select", 期望值: "guangzhou"

# 多选下拉框
[选择下拉选项], 定位器: "#skills-select", 选项值: "javascript,python,java", 多选: True

# 7. 测试按键操作
[打印], 内容: "测试按键操作..."
[聚焦元素], 定位器: "#text-input"
[按键操作], 定位器: "#text-input", 按键: "Meta+a"
[按键操作], 定位器: "#text-input", 按键: "Delete"

cleared_text = [获取元素属性], 定位器: "#text-input", 属性: "value"
[打印], 内容: "清空后的文本: '${cleared_text}'"
[断言输入值], 定位器: "#text-input", 期望值: ""

[按键操作], 定位器: "#text-input", 按键: "T"
[按键操作], 定位器: "#text-input", 按键: "e"
[按键操作], 定位器: "#text-input", 按键: "s"
[按键操作], 定位器: "#text-input", 按键: "t"

typed_keys = [获取元素属性], 定位器: "#text-input", 属性: "value"
[打印], 内容: "按键输入的文本: ${typed_keys}"
[断言输入值], 定位器: "#text-input", 期望值: "Test"

# 8. 测试聚焦操作
[打印], 内容: "测试聚焦操作..."
[聚焦元素], 定位器: "#focus-input-1"
[等待], 秒数: 0.5
[聚焦元素], 定位器: "#focus-input-2"
[等待], 秒数: 0.5
[聚焦元素], 定位器: "#focus-input-3"
[等待], 秒数: 0.5

# 9. 测试滚动操作
[打印], 内容: "测试滚动操作..."
[滚动元素到视野], 定位器: "#scroll-item-10"
[等待], 秒数: 1
[滚动元素到视野], 定位器: "#scroll-item-1"
[等待], 秒数: 1
[滚动元素到视野], 定位器: "#scroll-item-5"
[等待], 秒数: 1

# 10. 测试拖拽操作
[打印], 内容: "测试拖拽操作..."
[拖拽元素], 源定位器: "#drag-item-1", 目标定位器: "#drop-zone"
[等待], 秒数: 1
[拖拽元素], 源定位器: "#drag-item-2", 目标定位器: "#drop-zone"
[等待], 秒数: 1

# 验证拖拽结果 - 检查元素是否在目标区域
is_element1_in_zone = [检查元素是否存在], 定位器: "#drop-zone #drag-item-1"
is_element2_in_zone = [检查元素是否存在], 定位器: "#drop-zone #drag-item-2"
[打印], 内容: "拖拽元素1在目标区域: ${is_element1_in_zone}"
[打印], 内容: "拖拽元素2在目标区域: ${is_element2_in_zone}"

# 重置拖拽项目
[点击元素], 定位器: "#reset-drag-items"
[等待], 秒数: 1

# 11. 测试动态元素操作
[打印], 内容: "测试动态元素操作..."
[点击元素], 定位器: "#add-element"
[等待], 秒数: 0.5

dynamic_element1_exists = [检查元素是否存在], 定位器: "#dynamic-element-1"
[打印], 内容: "动态元素1存在: ${dynamic_element1_exists}"

[点击元素], 定位器: "#add-element"
[等待], 秒数: 0.5

dynamic_element2_exists = [检查元素是否存在], 定位器: "#dynamic-element-2"
[打印], 内容: "动态元素2存在: ${dynamic_element2_exists}"

[点击元素], 定位器: "#remove-element"
[等待], 秒数: 0.5

dynamic_element2_removed = [检查元素是否存在], 定位器: "#dynamic-element-2"
[打印], 内容: "动态元素2移除后: ${dynamic_element2_removed}"

[点击元素], 定位器: "#toggle-element"
[等待], 秒数: 0.5

container_after_hide = [检查元素是否可见], 定位器: "#dynamic-container"
[打印], 内容: "容器切换隐藏后可见性: ${container_after_hide}"

[点击元素], 定位器: "#toggle-element"
[等待], 秒数: 0.5

container_after_show = [检查元素是否可见], 定位器: "#dynamic-container"
[打印], 内容: "容器切换显示后可见性: ${container_after_show}"

# 12. 测试表单综合操作
[打印], 内容: "测试表单综合操作..."
[输入文本], 定位器: "#form-name", 文本: "张三"
[输入文本], 定位器: "#form-email", 文本: "zhangsan@test.com"
[输入文本], 定位器: "#form-phone", 文本: "13800138000"
[勾选复选框], 定位器: "#form-agree"

# 提交表单
[点击元素], 定位器: "#submit-form"
[等待], 秒数: 1

form_result = [获取元素文本], 定位器: "#form-result"
[打印], 内容: "表单提交结果: ${form_result}"
[断言文本内容], 定位器: "#form-result", 期望文本: "表单提交成功", 匹配方式: contains

# 重置表单
[点击元素], 定位器: "#reset-form"
[等待], 秒数: 0.5

reset_name = [获取元素属性], 定位器: "#form-name", 属性: "value"
[打印], 内容: "重置后的姓名: '${reset_name}'"
[断言输入值], 定位器: "#form-name", 期望值: ""

# 13. 最终验证 - 测试页面标题
page_title = [获取页面标题]
[打印], 内容: "页面标题: ${page_title}"
[断言页面标题], 期望标题: "元素操作关键字测试页面", 匹配方式: exact

# 14. 截图保存测试结果
[截图], 文件名: "element_keywords_test_result.png"

[打印], 内容: "所有元素操作关键字测试完成！"

# 15. 关闭浏览器
[关闭浏览器] 