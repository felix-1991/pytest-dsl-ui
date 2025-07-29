# pytest-dsl-ui

🎯 **基于Playwright的UI自动化测试框架** - 为pytest-dsl提供强大的Web UI测试能力

## ✨ 核心特性

- 🔍 **智能定位器** - 支持20+种元素定位策略，包括复合定位器
- ⚡ **零配置启动** - 开箱即用，无需复杂配置
- 🌐 **多浏览器支持** - Chrome、Firefox、Safari、Edge
- 🔧 **Playwright转换器** - 一键转换录制脚本为DSL格式

## 🚀 快速开始

### 安装
```bash
pip install pytest-dsl-ui
playwright install  # 安装浏览器
```

### 5分钟上手示例
```dsl
@name: "百度搜索测试"

[启动浏览器], 浏览器: "chromium"
[打开页面], 地址: "https://www.baidu.com"
[输入文本], 定位器: "input#kw", 文本: "pytest-dsl-ui"
[点击元素], 定位器: "input#su"
[断言文本存在], 文本: "pytest"
[截图], 文件名: "search_result.png"
[关闭浏览器]
```

运行：`pytest-dsl test.dsl`

## 🎯 定位器速查表

> **定位器是框架的核心**，支持简单到复杂的各种定位需求

### 基础定位器

| 定位器类型 | 语法格式 | 使用示例 | 说明 |
|-----------|---------|----------|------|
| **CSS选择器** | `selector` | `"button.submit"` | 最常用，支持所有CSS选择器 |
| **文本定位** | `text=文本` | `"text=登录"` | 根据元素文本内容定位 |
| **角色定位** | `role=角色` | `"role=button"` | 根据ARIA角色定位 |
| **标签定位** | `label=标签` | `"label=用户名"` | 根据关联的label定位 |
| **占位符定位** | `placeholder=文本` | `"placeholder=请输入"` | 根据placeholder属性定位 |
| **测试ID定位** | `testid=ID` | `"testid=submit-btn"` | 根据test-id属性定位 |
| **XPath定位** | `//xpath` | `"//button[@type='submit']"` | 使用XPath表达式定位 |

### 精确匹配定位器

| 定位器类型 | 语法格式 | 使用示例 | 说明 |
|-----------|---------|----------|------|
| **精确文本** | `text=文本,exact=true` | `"text=登录,exact=true"` | 精确匹配文本，不包含子串 |
| **精确标签** | `label=标签,exact=true` | `"label=用户名,exact=true"` | 精确匹配标签文本 |
| **角色+名称** | `role=角色:名称` | `"role=button:提交"` | 角色和名称的组合定位 |

### 复合定位器 ⭐

| 功能 | 语法格式 | 使用示例 | 说明 |
|------|---------|----------|------|
| **子元素定位** | `基础定位器&locator=子选择器` | `"role=cell:外到内&locator=label"` | 在基础元素中查找子元素 |
| **文本过滤** | `基础定位器&has_text=文本` | `"div&has_text=重要"` | 包含特定文本的元素 |
| **选择第一个** | `基础定位器&first=true` | `"button&first=true"` | 选择第一个匹配的元素 |
| **选择最后一个** | `基础定位器&last=true` | `"li&last=true"` | 选择最后一个匹配的元素 |
| **选择第N个** | `基础定位器&nth=索引` | `"option&nth=2"` | 选择第N个元素（从0开始） |
| **组合条件** | `定位器&条件1&条件2` | `"role=cell:外到内&locator=label&first=true"` | 多个条件组合使用 |

### 智能定位器

| 定位器类型 | 语法格式 | 使用示例 | 说明 |
|-----------|---------|----------|------|
| **可点击元素** | `clickable=文本` | `"clickable=提交"` | 智能查找可点击的元素 |
| **元素类型** | `标签名=文本` | `"span=状态"` | 根据HTML标签和文本定位 |
| **CSS类定位** | `class=类名:文本` | `"class=btn:确认"` | 根据CSS类名和文本定位 |

## 🛠️ 常用操作关键字

### 浏览器控制
```dsl
[启动浏览器], 浏览器: "chromium", 无头模式: false
[打开页面], 地址: "https://example.com"
[刷新页面]
[关闭浏览器]
```

### 元素操作
```dsl
[点击元素], 定位器: "button#submit"
[双击元素], 定位器: "text=编辑"
[输入文本], 定位器: "input[name='username']", 文本: "admin"
[清空文本], 定位器: "textarea"
[选择选项], 定位器: "select", 值: "选项1"
[上传文件], 定位器: "input[type='file']", 文件路径: "test.jpg"
```

### 等待与断言
```dsl
[等待元素出现], 定位器: ".loading"
[等待元素消失], 定位器: ".spinner"
[等待文本出现], 文本: "加载完成"
[断言元素存在], 定位器: ".success"
[断言文本内容], 定位器: "h1", 期望文本: "欢迎"
[断言元素可见], 定位器: "button"
[断言元素隐藏], 定位器: ".modal"
[断言输入值], 定位器: "input[name='email']", 期望值: "test@example.com"
[断言复选框状态], 定位器: "role=checkbox:同意条款", 期望状态: true
```

### 复选框和表单操作
```dsl
[勾选复选框], 定位器: "role=checkbox:接受协议"
[取消勾选复选框], 定位器: "role=checkbox:订阅邮件"
[设置复选框状态], 定位器: "role=checkbox:记住密码", 选中状态: true
[选择下拉选项], 定位器: "select[name='country']", 选项值: "CN"
[选择下拉选项], 定位器: "role=combobox:语言", 选项标签: "中文"
[选择下拉选项], 定位器: "role=listbox", 选项索引: 0
```

### 获取元素信息
```dsl
[获取元素文本], 定位器: "h1", 变量名: "page_title"
[获取元素属性], 定位器: "img", 属性: "src", 变量名: "image_url"
```

## 🔄 Playwright脚本转换

将Playwright录制的脚本一键转换为DSL格式：

```bash
# 使用pw2dsl命令转换（推荐）
pw2dsl input.py -o output.dsl

# 或使用完整路径
python -m pytest_dsl_ui.utils.playwright_converter input.py -o output.dsl

# 直接输出到控制台
pw2dsl input.py
```

> **✨ 最新改进**：转换器已经过全面优化，确保输出的DSL语法与框架实现完全一致，支持复杂的元素定位和断言操作。

**转换前（Playwright）：**
```python
# 复杂的链式调用
page.get_by_role("cell", name="外到内").locator("label").first.click()
page.get_by_text("专家模式", exact=True).click()

# 复选框操作
page.get_by_role("checkbox", name="同意条款").check()
page.get_by_role("checkbox", name="记住密码").set_checked(True)

# 断言操作
expect(page.get_by_role("heading", name="欢迎")).to_be_visible()
expect(page.get_by_text("成功")).to_contain_text("成功")
expect(page.get_by_role("textbox", name="邮箱")).to_have_value("test@example.com")
```

**转换后（DSL）：**
```dsl
# 复杂的链式调用
[点击元素], 定位器: "role=cell:外到内&locator=label&first=true"
[点击元素], 定位器: "text=专家模式,exact=true"

# 复选框操作
[勾选复选框], 定位器: "role=checkbox:同意条款"
[设置复选框状态], 定位器: "role=checkbox:记住密码", 选中状态: True

# 断言操作
[断言元素可见], 定位器: "role=heading:欢迎"
[断言文本内容], 定位器: "text=成功", 期望文本: "成功", 匹配方式: "contains"
[断言输入值], 定位器: "role=textbox:邮箱", 期望值: "test@example.com"
```

## 📝 实战示例

### 登录测试
```dsl
@name: "用户登录测试"

[启动浏览器], 浏览器: "chromium"
[打开页面], 地址: "https://example.com/login"

# 输入用户名密码
[输入文本], 定位器: "label=用户名", 文本: "admin"
[输入文本], 定位器: "placeholder=请输入密码", 文本: "123456"

# 点击登录按钮
[点击元素], 定位器: "role=button:登录"

# 验证登录成功
[等待文本出现], 文本: "欢迎"
[断言元素存在], 定位器: "text=退出"
[截图], 文件名: "login_success.png"

[关闭浏览器]
```

### 表单操作
```dsl
@name: "复杂表单测试"

[启动浏览器]
[打开页面], 地址: "https://example.com/form"

# 复合定位器示例
[点击元素], 定位器: "role=cell:配置项&locator=button&first=true"
[选择选项], 定位器: "label=类型&locator=select", 值: "高级"
[输入文本], 定位器: "class=input-group:备注&locator=textarea", 文本: "测试数据"

# 提交表单
[点击元素], 定位器: "clickable=提交"
[等待文本出现], 文本: "保存成功"

[关闭浏览器]
```

## 🔧 高级配置

### 设置默认超时
```dsl
[设置等待超时], 超时时间: 30  # 30秒
```

### 浏览器选项
```dsl
[启动浏览器], 浏览器: "firefox", 无头模式: true, 视口宽度: 1920, 视口高度: 1080
```

## 📚 更多资源

- 📖 [完整文档](https://github.com/your-repo/pytest-dsl-ui/docs)
- 🐛 [问题反馈](https://github.com/your-repo/pytest-dsl-ui/issues)
- 💡 [示例集合](https://github.com/your-repo/pytest-dsl-ui/examples)

---

**💡 提示**：定位器是框架的核心，熟练掌握各种定位器的使用是提高测试效率的关键！
