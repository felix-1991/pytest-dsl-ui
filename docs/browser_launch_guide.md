# 浏览器启动功能指南

## 概述

pytest-dsl-ui 提供了强大的浏览器启动和管理功能，支持多种浏览器类型、灵活的配置选项和完整的生命周期管理。本文档详细介绍如何使用`[启动浏览器]`关键字及其相关功能。

## 基础用法

### 最简单的启动方式

```yaml
[启动浏览器]
```

这将使用默认配置启动Chromium浏览器：
- 浏览器类型：chromium
- 模式：headless (无界面)
- 慢动作：0ms (正常速度)

### 指定浏览器类型

```yaml
[启动浏览器], 浏览器类型: "firefox"
[启动浏览器], 浏览器类型: "webkit"
[启动浏览器], 浏览器类型: "chromium"
```

支持的浏览器类型：
- **chromium**: Google Chrome/Chromium (推荐)
- **firefox**: Mozilla Firefox
- **webkit**: Safari WebKit

## 关键参数详解

### 1. headless - 无头模式控制

```yaml
# 有界面模式 - 可视化调试
[启动浏览器], headless: False

# 无界面模式 - CI/CD环境
[启动浏览器], headless: True
```

**用途说明：**
- `False`: 显示浏览器窗口，适合开发调试
- `True`: 后台运行，适合自动化测试和CI/CD

### 2. 慢动作模式

```yaml
# 慢动作模式，便于观察测试过程
[启动浏览器], 慢动作: 1000  # 每个操作间隔1秒

# 超慢模式，详细观察
[启动浏览器], 慢动作: 2000  # 每个操作间隔2秒
```

**用途说明：**
- 0: 正常速度执行
- 500-1000: 适中的观察速度
- 1000+: 详细观察每个步骤

### 3. 视口尺寸设置

```yaml
# 设置浏览器窗口大小
[启动浏览器], 视口宽度: 1920, 视口高度: 1080

# 移动设备模拟
[启动浏览器], 视口宽度: 375, 视口高度: 667  # iPhone SE
```

**常用尺寸：**
- 桌面：1920x1080, 1366x768, 1440x900
- 平板：768x1024, 1024x768
- 手机：375x667, 414x896, 360x640

### 4. HTTPS证书处理

```yaml
# 忽略SSL证书错误（适用于测试环境）
[启动浏览器], 忽略证书错误: True

# 严格证书验证（适用于生产环境）
[启动浏览器], 忽略证书错误: False
```

## 高级配置

### YAML配置方式

```yaml
[启动浏览器], 配置: '''
  headless: false
  slow_mo: 1000
  viewport:
    width: 1920
    height: 1080
  args:
    - "--start-maximized"
    - "--disable-web-security"
    - "--allow-running-insecure-content"
  user_agent: "Custom-Agent/1.0"
  geolocation:
    latitude: 40.7128
    longitude: -74.0060
  permissions:
    - "geolocation"
    - "notifications"
'''
```

### 启动参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `headless` | boolean | True | 是否无头模式 |
| `slow_mo` | number | 0 | 操作间隔(毫秒) |
| `viewport.width` | number | 1280 | 视口宽度 |
| `viewport.height` | number | 720 | 视口高度 |
| `args` | array | [] | 浏览器启动参数 |
| `user_agent` | string | 默认 | 用户代理字符串 |
| `geolocation` | object | null | 地理位置 |
| `permissions` | array | [] | 权限列表 |

## 实际使用示例

### 开发调试模式

```yaml
@name: "开发调试浏览器设置"

# 启动可视化浏览器，便于调试
[启动浏览器], 
  浏览器类型: "chromium",
  headless: False,
  慢动作: 1000,
  视口宽度: 1920,
  视口高度: 1080,
  忽略证书错误: True

[打开页面], 地址: "https://example.com"
[等待], 时间: 2
[截图], 文件名: "debug_screenshot.png"
```

### CI/CD自动化模式

```yaml
@name: "CI环境浏览器设置"

# 启动无界面浏览器，适合自动化
[启动浏览器],
  浏览器类型: "chromium",
  headless: True,
  视口宽度: 1366,
  视口高度: 768

[打开页面], 地址: "https://api.example.com"
[断言页面标题], 预期标题: "API Documentation"
```

### 移动端测试模式

```yaml
@name: "移动端浏览器模拟"

[启动浏览器], 配置: '''
  headless: false
  slow_mo: 500
  viewport:
    width: 375
    height: 667
  user_agent: "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
  args:
    - "--user-agent=iPhone"
'''

[打开页面], 地址: "https://m.example.com"
[断言元素存在], 选择器: ".mobile-menu"
```

### 地理位置测试

```yaml
@name: "地理位置功能测试"

[启动浏览器], 配置: '''
  headless: false
  geolocation:
    latitude: 37.7749
    longitude: -122.4194
  permissions:
    - "geolocation"
'''

[打开页面], 地址: "https://maps.example.com"
[点击元素], 选择器: "#get-location"
[等待元素], 选择器: ".location-result"
```

## 浏览器管理功能

### 多浏览器支持

```yaml
# 启动第一个浏览器
[启动浏览器], 浏览器类型: "chromium"
[打开页面], 地址: "https://app1.example.com"

# 启动第二个浏览器
[启动浏览器], 浏览器类型: "firefox"
[打开页面], 地址: "https://app2.example.com"

# 两个浏览器可以并行操作
```

### 浏览器上下文管理

```yaml
# 启动浏览器会自动创建：
# - 浏览器实例 (Browser)
# - 浏览器上下文 (BrowserContext)  
# - 默认页面 (Page)

[启动浏览器], headless: False

# 新建页面（在同一上下文中）
[新建页面]
[打开页面], 地址: "https://page2.example.com"

# 在不同页面间切换
[切换页面], 页面ID: "page_1"
```

### 认证状态管理

```yaml
# 先登录获取认证状态
[启动浏览器], headless: False
[打开页面], 地址: "https://app.example.com/login"
[填写输入框], 选择器: "#username", 内容: "testuser"
[填写输入框], 选择器: "#password", 内容: "password"
[点击元素], 选择器: "#login-btn"

# 保存认证状态
[保存认证状态], 状态名称: "logged_in"

# 在新上下文中加载认证状态
[加载认证状态], 状态名称: "logged_in"
[打开页面], 地址: "https://app.example.com/dashboard"
```

## 与API测试集成

### 浏览器HTTP请求

```yaml
# 启动浏览器
[启动浏览器], headless: False

# 在浏览器上下文中进行API测试
[浏览器HTTP请求], 客户端: "api", 配置: '''
  method: GET
  url: https://api.example.com/users/me
  captures:
    user_id: ["jsonpath", "$.id"]
    user_name: ["jsonpath", "$.name"]
  asserts:
    - ["status", "eq", 200]
'''

# API和UI操作无缝结合
[打开页面], 地址: "https://app.example.com/profile"
[断言文本内容], 选择器: ".username", 预期文本: "${user_name}"
```

## 性能优化建议

### 1. 选择合适的浏览器

```yaml
# 性能优先
[启动浏览器], 浏览器类型: "chromium"  # 最快

# 兼容性优先  
[启动浏览器], 浏览器类型: "firefox"   # 中等

# Safari测试
[启动浏览器], 浏览器类型: "webkit"    # WebKit引擎
```

### 2. headless模式选择

```yaml
# 开发阶段 - 可视化调试
[启动浏览器], headless: False

# 自动化测试 - 更快执行
[启动浏览器], headless: True
```

### 3. 资源优化

```yaml
[启动浏览器], 配置: '''
  headless: true
  args:
    - "--no-sandbox"
    - "--disable-dev-shm-usage"
    - "--disable-images"          # 禁用图片加载
    - "--disable-javascript"      # 禁用JS（谨慎使用）
    - "--disable-plugins"         # 禁用插件
'''
```

## 错误处理和调试

### 常见问题解决

```yaml
# 问题1: 浏览器启动超时
[启动浏览器], 配置: '''
  timeout: 60000  # 增加超时时间
  args:
    - "--no-sandbox"
    - "--disable-dev-shm-usage"
'''

# 问题2: 证书错误
[启动浏览器], 忽略证书错误: True

# 问题3: 权限问题
[启动浏览器], 配置: '''
  args:
    - "--disable-web-security"
    - "--allow-running-insecure-content"
'''
```

### 调试模式

```yaml
# 启用详细日志
[启动浏览器], 配置: '''
  headless: false
  slow_mo: 1000
  args:
    - "--enable-logging"
    - "--log-level=0"
    - "--disable-background-timer-throttling"
'''

# 开发者工具
[启动浏览器], 配置: '''
  headless: false
  args:
    - "--auto-open-devtools-for-tabs"
'''
```

## 清理和资源管理

### 显式关闭

```yaml
# 手动关闭浏览器
[关闭浏览器]

# 关闭指定浏览器
[关闭浏览器], 浏览器ID: "chromium_0"
```

### 自动清理

```yaml
# teardown块会自动清理资源
teardown do
    [关闭浏览器]
    [打印], 内容: "浏览器已清理"
end
```

## 最佳实践

### 1. 环境适配

```yaml
# 开发环境
@if: "${ENV}" == "dev"
[启动浏览器], headless: False, 慢动作: 1000

# 测试环境  
@if: "${ENV}" == "test"
[启动浏览器], headless: True, 慢动作: 0

# 生产环境
@if: "${ENV}" == "prod"
[启动浏览器], headless: True, 忽略证书错误: False
```

### 2. 配置管理

```yaml
# 使用配置文件
# config/browser_settings.yaml
browser_configs:
  debug:
    headless: false
    slow_mo: 1000
    viewport: {width: 1920, height: 1080}
  
  ci:
    headless: true
    slow_mo: 0
    viewport: {width: 1366, height: 768}

# DSL文件中引用
[启动浏览器], 配置: "${browser_configs.debug}"
```

### 3. 错误恢复

```yaml
@try:
  [启动浏览器], headless: False
@except:
  [打印], 内容: "图形界面启动失败，切换到headless模式"
  [启动浏览器], headless: True
```

## 总结

浏览器启动功能是pytest-dsl-ui的核心组件，提供了：

- **多浏览器支持**: Chromium、Firefox、WebKit
- **灵活配置**: headless模式、视口尺寸、启动参数
- **调试友好**: 慢动作模式、可视化界面
- **自动化优化**: 无头模式、性能调优
- **完整管理**: 生命周期管理、资源清理
- **无缝集成**: UI测试、API测试、认证状态

通过合理配置和使用这些功能，可以构建robust、高效的自动化测试流程。 