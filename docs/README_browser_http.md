# 基于浏览器的HTTP API测试关键字

本项目提供了基于浏览器上下文的HTTP API测试关键字，设计上与pytest-dsl的HTTP关键字保持一致，但利用Playwright浏览器的会话状态和认证信息。

## 设计理念

### 与pytest-dsl的一致性

1. **相同的YAML配置格式**：支持与pytest-dsl完全相同的配置语法
2. **统一的返回格式**：返回结果包含captures、session_state、response等字段
3. **兼容的断言系统**：支持相同的断言类型和重试机制
4. **一致的变量捕获**：支持JSONPath、正则表达式、响应头等提取方式

### 浏览器上下文的优势

1. **自动会话管理**：继承浏览器的Cookie、认证状态
2. **真实环境测试**：使用与UI测试相同的浏览器环境
3. **跨域支持**：利用浏览器处理CORS等问题
4. **状态保持**：在UI操作和API测试间保持状态一致性

## 核心组件

### 1. BrowserHTTPClient (browser_http_client.py)

基于Playwright APIRequestContext的HTTP客户端实现：

```python
class BrowserHTTPClient:
    """基于浏览器上下文的HTTP客户端类"""
    
    def __init__(self, browser_context, base_url="", headers={}, timeout=30):
        # 利用浏览器上下文创建API请求上下文
        self._api_request_context = browser_context.request
```

**特点：**
- 继承浏览器的Cookie和认证状态
- 支持与requests.Response兼容的响应接口
- 自动处理HTTPS证书验证
- 内置Allure报告支持

### 2. BrowserHTTPRequest (browser_http_request.py)

HTTP请求处理类，复用pytest-dsl的核心逻辑：

```python
class BrowserHTTPRequest:
    """基于浏览器的HTTP请求处理类"""
    
    def process_captures(self) -> Dict[str, Any]:
        # 复用pytest-dsl的捕获逻辑
    
    def process_asserts(self) -> Tuple[List[Dict], List[Dict]]:
        # 复用pytest-dsl的断言和重试逻辑
```

**特点：**
- 完全兼容pytest-dsl的断言语法
- 支持断言重试机制
- 提供详细的错误信息和Allure报告

### 3. BrowserHTTPKeywords (browser_http_keywords.py)

关键字实现，提供与pytest-dsl一致的接口：

```python
@keyword_manager.register('浏览器HTTP请求', [...])
def browser_http_request(context, **kwargs):
    """执行基于浏览器的HTTP请求"""
```

## 使用示例

### 基本HTTP请求

```yaml
# 配置浏览器HTTP客户端
browser_http_clients:
  api_server:
    base_url: "https://api.example.com"
    timeout: 30
    headers:
      Content-Type: "application/json"
      User-Agent: "pytest-dsl-ui/1.0"
```

```python
# 发送GET请求
[浏览器HTTP请求], 客户端: "api_server", 配置: '''
    method: GET
    url: /users/1
    captures:
        user_id: ["jsonpath", "$.id"]
        user_name: ["jsonpath", "$.name"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.id", "eq", 1]
'''
```

### 带认证的请求序列

```python
# 1. 先在浏览器中登录（获取认证状态）
[打开页面], 地址: "https://example.com/login"
[输入文本], 选择器: "#username", 文本: "admin"
[输入文本], 选择器: "#password", 文本: "password"
[点击元素], 选择器: "#login-btn"

# 2. 使用浏览器的认证状态发送API请求
[浏览器HTTP请求], 客户端: "api_server", 配置: '''
    method: GET
    url: /profile
    captures:
        profile_data: ["jsonpath", "$"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.authenticated", "eq", true]
'''
```

### 复杂断言和重试

```python
[浏览器HTTP请求], 客户端: "api_server", 配置: '''
    method: POST
    url: /orders
    request:
        json:
            product_id: ${product_id}
            quantity: 2
    captures:
        order_id: ["jsonpath", "$.id"]
        order_status: ["jsonpath", "$.status"]
    asserts:
        - ["status", "eq", 201]
        - ["jsonpath", "$.id", "exists"]
        - ["jsonpath", "$.status", "eq", "pending"]
        - ["jsonpath", "$.items", "length", "eq", 1]
    retry_assertions:
        all: true
        count: 3
        interval: 2
'''
```

### 使用模板

```yaml
# 定义请求模板
browser_http_templates:
  create_user:
    method: POST
    url: /users
    request:
        headers:
            Content-Type: "application/json"
        json:
            name: "${user_name}"
            email: "${user_email}"
    captures:
        new_user_id: ["jsonpath", "$.id"]
    asserts:
        - ["status", "eq", 201]
        - ["jsonpath", "$.id", "exists"]
```

```python
# 使用模板发送请求
user_name = "张三"
user_email = "zhangsan@example.com"

[浏览器HTTP请求], 模板: "create_user", 配置: '''
    # 可以在此处覆盖模板中的配置
    request:
        json:
            department: "技术部"
'''
```

## 配置格式

### 客户端配置

```yaml
browser_http_clients:
  default:
    base_url: "https://api.example.com"
    timeout: 30
    headers:
      Content-Type: "application/json"
      User-Agent: "pytest-dsl-ui/1.0"
    ignore_https_errors: false
    extra_http_headers:
      X-Request-ID: "test-${timestamp}"
  
  auth_server:
    base_url: "https://auth.example.com"
    timeout: 60
    headers:
      Content-Type: "application/json"
```

### 请求配置

```yaml
method: POST
url: /api/endpoint
request:
    params:
        page: 1
        limit: 10
    headers:
        Authorization: "Bearer ${token}"
        X-Custom-Header: "value"
    json:
        name: "测试数据"
        value: 123
    timeout: 30
captures:
    response_id: ["jsonpath", "$.id"]
    response_message: ["jsonpath", "$.message"]
    status_code: ["status"]
    response_time: ["response_time"]
asserts:
    - ["status", "eq", 200]
    - ["jsonpath", "$.success", "eq", true]
    - ["response_time", "lt", 2000]
retry_assertions:
    all: false
    indices: [1, 2]  # 只重试第2和第3个断言
    count: 3
    interval: 1
    specific:
        1:  # 第2个断言的特殊配置
            count: 5
            interval: 2
```

## 支持的断言类型

### 提取器类型
- `jsonpath`: JSON路径提取
- `regex`: 正则表达式提取
- `header`: 响应头提取
- `status`: HTTP状态码
- `body`: 响应体文本
- `response_time`: 响应时间（毫秒）

### 断言类型
- `exists` / `not_exists`: 存在性断言
- `eq` / `neq`: 相等/不等断言
- `lt` / `lte` / `gt` / `gte`: 数值比较
- `contains` / `not_contains`: 包含断言
- `startswith` / `endswith`: 字符串开头/结尾断言
- `matches`: 正则表达式匹配
- `type`: 类型断言（string/number/boolean/array/object/null）
- `length`: 长度断言
- `schema`: JSON Schema验证

### 重试配置
- `all`: 是否重试所有断言
- `indices`: 要重试的断言索引列表
- `count`: 重试次数
- `interval`: 重试间隔（秒）
- `specific`: 特定断言的重试配置

## 与pytest-dsl HTTP关键字的对比

| 特性 | pytest-dsl HTTP | 浏览器HTTP | 说明 |
|------|----------------|-----------|------|
| 配置语法 | ✅ | ✅ | 完全兼容 |
| 断言系统 | ✅ | ✅ | 完全兼容 |
| 变量捕获 | ✅ | ✅ | 完全兼容 |
| 重试机制 | ✅ | ✅ | 完全兼容 |
| 会话管理 | requests.Session | 浏览器上下文 | 不同实现 |
| 认证方式 | 手动配置 | 浏览器自动 | 浏览器更便利 |
| CORS处理 | 需要服务器支持 | 浏览器自动处理 | 浏览器更强大 |
| 证书验证 | requests配置 | 浏览器策略 | 浏览器更灵活 |

## 最佳实践

### 1. 结合UI和API测试

```python
# 通过UI登录获取认证状态
[打开页面], 地址: "https://app.example.com/login"
[登录操作] # 自定义关键字

# 使用认证状态进行API测试
[浏览器HTTP请求], 配置: '''
    method: GET
    url: /api/user/profile
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.authenticated", "eq", true]
'''

# 通过API创建数据
[浏览器HTTP请求], 配置: '''
    method: POST
    url: /api/products
    request:
        json:
            name: "测试产品"
            price: 99.99
    captures:
        product_id: ["jsonpath", "$.id"]
'''

# 在UI中验证数据
[导航到页面], 地址: "/products/${product_id}"
[验证元素文本], 选择器: ".product-name", 期望文本: "测试产品"
```

### 2. 使用配置文件管理环境

```yaml
# config/test.yaml
browser_http_clients:
  api:
    base_url: "https://test-api.example.com"
    timeout: 30
    
# config/prod.yaml  
browser_http_clients:
  api:
    base_url: "https://api.example.com"
    timeout: 10
```

### 3. 模板化常用操作

```yaml
browser_http_templates:
  login_api:
    method: POST
    url: /auth/login
    request:
        json:
            username: "${username}"
            password: "${password}"
    captures:
        access_token: ["jsonpath", "$.access_token"]
        user_id: ["jsonpath", "$.user.id"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.access_token", "exists"]
        
  get_user_profile:
    method: GET
    url: /users/${user_id}
    request:
        headers:
            Authorization: "Bearer ${access_token}"
    captures:
        user_data: ["jsonpath", "$"]
    asserts:
        - ["status", "eq", 200]
        - ["jsonpath", "$.id", "eq", ${user_id}]
```

## 错误处理和调试

### Allure报告集成

- 自动记录请求和响应详情
- 支持断言失败的详细错误信息
- 重试过程的完整记录
- 敏感信息的自动隐藏

### 调试技巧

1. **使用保存响应功能**：
```python
[浏览器HTTP请求], 保存响应: "last_response", 配置: '''...'''
[打印变量], 变量名: "last_response"
```

2. **分步验证**：
```python
# 分别测试请求和断言
[浏览器HTTP请求], 配置: '''
    method: GET
    url: /api/data
    captures:
        all_data: ["jsonpath", "$"]
'''

# 单独验证捕获的数据
[打印变量], 变量名: "all_data"
```

3. **使用断言重试排查间歇性问题**：
```python
[浏览器HTTP请求], 配置: '''
    method: GET
    url: /api/status
    asserts:
        - ["jsonpath", "$.ready", "eq", true]
    retry_assertions:
        all: true
        count: 10
        interval: 3
'''
```

## 注意事项

1. **浏览器上下文依赖**：必须在有效的浏览器上下文中使用
2. **性能考虑**：浏览器HTTP请求可能比纯HTTP请求稍慢
3. **资源管理**：浏览器上下文会自动管理请求生命周期
4. **并发限制**：受浏览器并发连接限制

通过这些设计，浏览器HTTP关键字既保持了与pytest-dsl的完全兼容性，又充分利用了浏览器环境的优势，为API测试提供了更加便利和强大的工具。 