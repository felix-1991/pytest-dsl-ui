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
[断言文本内容], 定位器: "h1", 预期文本: "欢迎"
[断言元素可见], 定位器: "button"
```

## 🔄 Playwright脚本转换

将Playwright录制的脚本一键转换为DSL格式：

```bash
# 转换Playwright脚本
python -m pytest_dsl_ui.utils.playwright_converter input.py -o output.dsl
```

**转换前（Playwright）：**
```python
page.get_by_role("cell", name="外到内").locator("label").first.click()
page.get_by_text("专家模式", exact=True).click()
```

**转换后（DSL）：**
```dsl
[点击元素], 定位器: "role=cell:外到内&locator=label&first=true"
[点击元素], 定位器: "text=专家模式,exact=true"
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
