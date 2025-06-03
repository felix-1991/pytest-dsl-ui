# pytest-dsl-ui

基于Playwright的UI自动化测试关键字框架，为pytest-dsl提供强大的Web UI测试能力。

## 🚀 特性

- **无缝集成**：通过entry_points机制自动集成到pytest-dsl框架
- **Playwright驱动**：基于现代化的Playwright浏览器自动化引擎
- **丰富关键字**：提供完整的UI操作、断言和截图关键字
- **多浏览器支持**：支持Chrome、Firefox、Safari、Edge等主流浏览器
- **智能等待**：内置智能等待机制，提高测试稳定性
- **可视化调试**：支持截图、录制和可视化调试
- **远程执行**：支持pytest-dsl的远程关键字模式

## 📦 安装

```bash
# 安装pytest-dsl-ui（会自动安装pytest-dsl依赖）
pip install pytest-dsl-ui

# 安装Playwright浏览器
playwright install
```

## 🎯 快速入门

### 1. 创建测试文件

```dsl
@name: "UI自动化测试示例"
@description: "演示pytest-dsl-ui的基本功能"

# 启动浏览器并打开页面
[启动浏览器], 浏览器: "chromium", 无头模式: false
[打开页面], 地址: "https://www.example.com"

# 元素操作
[点击元素], 定位器: "button[type='submit']"
[输入文本], 定位器: "#username", 文本: "testuser"
[选择选项], 定位器: "select#country", 值: "China"

# 断言验证
[断言元素存在], 定位器: ".success-message"
[断言文本内容], 定位器: "h1", 预期文本: "欢迎"

# 截图保存
[截图], 文件名: "test_result.png"

# 关闭浏览器
[关闭浏览器]
```

### 2. 运行测试

```bash
pytest-dsl test_ui.dsl
```

## 🔍 元素定位详解

pytest-dsl-ui 提供了多种强大的元素定位策略，让您能够灵活地定位页面元素。

### 基础定位策略

1. **CSS选择器**
   ```dsl
   [点击元素], 定位器: "button.submit"
   [点击元素], 定位器: "#login-button"
   [点击元素], 定位器: "div.container > p.text"
   ```

2. **XPath**
   ```dsl
   [点击元素], 定位器: "//button[@type='submit']"
   [点击元素], 定位器: "//div[contains(@class, 'container')]//p"
   ```

3. **文本定位**
   ```dsl
   [点击元素], 定位器: "text=提交"
   [点击元素], 定位器: "text=提交,exact=true"  # 精确匹配
   ```

4. **角色定位**
   ```dsl
   [点击元素], 定位器: "role=button"
   [点击元素], 定位器: "role=button:提交"  # 带名称的角色定位
   [点击元素], 定位器: "role=button,name=提交"  # 完整格式
   ```

5. **其他定位方式**
   ```dsl
   # 标签定位
   [点击元素], 定位器: "label=用户名"
   
   # 占位符定位
   [点击元素], 定位器: "placeholder=请输入用户名"
   
   # 测试ID定位
   [点击元素], 定位器: "testid=submit-btn"
   
   # 标题定位
   [点击元素], 定位器: "title=关闭"
   
   # Alt文本定位
   [点击元素], 定位器: "alt=logo"
   ```

### 高级定位策略

1. **过滤定位**
   ```dsl
   # 文本过滤
   [点击元素], 定位器: "role=listitem,filter_text=Product 2"
   [点击元素], 定位器: "role=listitem,filter_not_text=Product 1"
   
   # 组合定位
   [点击元素], 定位器: "role=button,and_title=Subscribe"
   [点击元素], 定位器: "role=button,and_text=确认"
   ```

2. **元素索引**
   ```dsl
   # 定位第一个元素
   [点击元素], 定位器: "button >> nth=0"
   
   # 定位最后一个元素
   [点击元素], 定位器: "button >> nth=-1"
   
   # 定位特定索引的元素
   [点击元素], 定位器: "button >> nth=2"
   ```

3. **可见性过滤**
   ```dsl
   # 只定位可见元素
   [点击元素], 定位器: "button >> visible=true"
   ```

4. **组合条件**
   ```dsl
   # 同时满足多个条件
   [点击元素], 定位器: "button.submit >> has=span.icon >> has_text=提交"
   
   # 满足任一条件
   [点击元素], 定位器: "button.submit >> or=text=取消"
   ```

### 智能等待

框架内置智能等待机制，可以等待元素达到特定状态：

```dsl
# 等待元素可见
[等待元素出现], 定位器: ".loading", 超时时间: 10

# 等待元素消失
[等待元素消失], 定位器: ".loading"

# 等待文本出现
[等待文本出现], 文本: "加载完成"

# 设置全局等待超时
[设置等待超时], 超时时间: 30
```

## 📚 关键字参考

### 浏览器管理

- **启动浏览器**：启动指定类型的浏览器
- **关闭浏览器**：关闭当前浏览器实例
- **新建页面**：在当前浏览器中新建页面
- **切换页面**：切换到指定页面

### 页面导航

- **打开页面**：导航到指定URL
- **刷新页面**：刷新当前页面
- **后退**：浏览器后退
- **前进**：浏览器前进
- **获取页面标题**：获取当前页面标题
- **获取当前地址**：获取当前页面URL

### 元素操作

- **点击元素**：点击指定元素
- **双击元素**：双击指定元素
- **右键点击元素**：右键点击指定元素
- **输入文本**：在输入框中输入文本
- **清空文本**：清空输入框内容
- **选择选项**：在下拉框中选择选项
- **上传文件**：上传文件到文件输入框

### 元素查找与等待

- **等待元素出现**：等待元素在页面中出现
- **等待元素消失**：等待元素从页面中消失
- **等待文本出现**：等待指定文本在页面中出现
- **获取元素文本**：获取元素的文本内容
- **获取元素属性**：获取元素的指定属性值

### UI断言

- **断言元素存在**：断言元素在页面中存在
- **断言元素不存在**：断言元素在页面中不存在
- **断言文本内容**：断言元素包含指定文本
- **断言元素可见**：断言元素在页面中可见
- **断言元素启用**：断言元素处于启用状态

### 截图与录制

- **截图**：对当前页面或指定元素截图
- **开始录制**：开始录制浏览器操作
- **停止录制**：停止录制并保存视频

## 🔧 高级配置

### 浏览器配置

```dsl
# 自定义浏览器启动参数
[启动浏览器], 浏览器: "chromium", 配置: '''
    headless: false
    viewport:
        width: 1920
        height: 1080
    args:
        - "--disable-web-security"
        - "--disable-features=VizDisplayCompositor"
'''
```

## 🌐 远程执行支持

pytest-dsl-ui完全支持pytest-dsl的远程关键字模式：

```bash
# 启动远程关键字服务器
pytest-dsl-server --host 0.0.0.0 --port 8270

# 在DSL中使用远程UI关键字
[注册远程服务器], 别名: "ui_server", 地址: "http://remote-host:8270"
[ui_server|启动浏览器], 浏览器: "chromium"
[ui_server|打开页面], 地址: "https://www.example.com"
```

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## �� 许可证

MIT License
