# 多窗口和新窗口处理指南

本指南介绍如何使用pytest-dsl-ui处理多窗口、新标签页和弹窗场景。

## 核心概念

### 页面ID
- 每个页面都有唯一的ID，格式：`{浏览器ID}_ctx_{上下文ID}_page_{序号}`
- 例如：`chromium_0_ctx_0_page_0`、`chromium_0_ctx_0_page_1`

### 相关关键字

1. **`打开页面`** - 现在返回页面ID
2. **`新建页面`** - 手动创建新页面
3. **`获取页面列表`** - 获取所有页面信息
4. **`切换页面`** - 切换到指定页面
5. **`等待新页面`** - 等待新窗口出现
6. **`切换到最新页面`** - 切换到最新创建的页面

## 使用场景

### 1. 获取当前页面ID

```yaml
# 打开页面现在会返回页面ID
result = [打开页面], 地址: "https://example.com"
current_page_id = ${result['current_page_id']}

# 保存页面ID供后续使用
[设置全局变量], 变量名: "主页面ID", 值: ${current_page_id}
```

### 2. 手动创建新页面

```yaml
# 新建页面
new_page_result = [新建页面]
new_page_id = ${new_page_result['result']}

# 在新页面中打开网站
[打开页面], 地址: "https://another-site.com"
```

### 3. 处理点击链接打开的新窗口

```yaml
# 方法1: 点击后检查页面数量变化
initial_pages = [获取页面列表]
[点击元素], 定位器: "a[target='_blank']"
[等待], 时间: 2

updated_pages = [获取页面列表]
if updated_pages['page_count'] > initial_pages['page_count']:
    # 有新页面打开
    [切换到最新页面], 变量名: "新窗口ID"
    new_window_id = [获取全局变量], 变量名: "新窗口ID"

# 方法2: 使用等待新页面功能
# 注意：需要在点击前准备等待
[等待新页面], 超时时间: 10, 变量名: "弹窗页面ID"
# 在另一个操作中触发新窗口打开...
```

### 4. 多窗口之间切换

```yaml
# 获取所有页面信息
[获取页面列表], 变量名: "所有页面"
pages = [获取全局变量], 变量名: "所有页面"

# 显示页面信息
for page in ${pages['page_info']} do
    [打印], 内容: "页面ID: ${page['page_id']}"
    [打印], 内容: "标题: ${page['title']}"
    [打印], 内容: "URL: ${page['url']}"
end

# 切换到特定页面
[切换页面], 页面ID: "chromium_0_ctx_0_page_1"

# 切换到最新页面
[切换到最新页面], 变量名: "最新页面"
```

### 5. 处理JavaScript弹窗

```yaml
# 点击会触发window.open()的按钮
before_count = [获取页面列表]
[点击元素], 定位器: "#popup-button"
[等待], 时间: 3

after_count = [获取页面列表]
if after_count['page_count'] > before_count['page_count']:
    [切换到最新页面]
    # 在弹窗中操作...
```

## 完整示例

### 电商网站多窗口测试

```yaml
@name: "电商多窗口测试"

# 启动浏览器
[启动浏览器], 浏览器: "chromium", 无头模式: false

# 打开主页
main_result = [打开页面], 地址: "https://shop.example.com"
main_page_id = main_result['current_page_id']

# 在主页搜索商品
[填写输入框], 定位器: "#search", 内容: "手机"
[点击元素], 定位器: "#search-btn"

# 点击商品链接（在新窗口打开）
[点击元素], 定位器: ".product-link[target='_blank']"
[等待], 时间: 2

# 检查是否有新页面
[获取页面列表], 变量名: "商品页面"
product_pages = [获取全局变量], 变量名: "商品页面"

if product_pages['page_count'] > 1:
    # 切换到商品详情页
    [切换到最新页面], 变量名: "商品详情页"
    
    # 在商品页操作
    [点击元素], 定位器: "#add-to-cart"
    [等待元素], 定位器: ".cart-success"
    
    # 打开购物车（新窗口）
    [点击元素], 定位器: "#view-cart[target='_blank']"
    [等待], 时间: 2
    
    # 切换到购物车页面
    [切换到最新页面]
    
    # 在购物车页面操作
    [点击元素], 定位器: "#checkout"
    
    # 切换回主页继续购物
    [切换页面], 页面ID: main_page_id
    
    # 搜索其他商品...

[关闭浏览器]
```

### 银行网站多标签页测试

```yaml
@name: "银行多标签页测试"

[启动浏览器], 浏览器: "chromium", 无头模式: false

# 登录银行网站
login_result = [打开页面], 地址: "https://bank.example.com/login"
login_page_id = login_result['current_page_id']

[填写输入框], 定位器: "#username", 内容: "testuser"
[填写输入框], 定位器: "#password", 内容: "password"
[点击元素], 定位器: "#login-btn"

# 进入账户概览
[等待元素], 定位器: "#account-overview"

# 在新标签页打开转账页面
[点击元素], 定位器: "a[href='/transfer'][target='_blank']"
[等待], 时间: 2
[切换到最新页面], 变量名: "转账页面"

# 在转账页面操作
[填写输入框], 定位器: "#to-account", 内容: "1234567890"
[填写输入框], 定位器: "#amount", 内容: "100"

# 在新标签页打开历史记录
[点击元素], 定位器: "a[href='/history'][target='_blank']"
[等待], 时间: 2
[切换到最新页面], 变量名: "历史页面"

# 查看历史记录
[等待元素], 定位器: ".transaction-list"

# 切换回转账页面完成转账
transfer_page_id = [获取全局变量], 变量名: "转账页面"
[切换页面], 页面ID: transfer_page_id
[点击元素], 定位器: "#submit-transfer"

# 显示所有打开的页面
[获取页面列表], 变量名: "所有银行页面"
all_pages = [获取全局变量], 变量名: "所有银行页面"
[打印], 内容: f"共打开了 {all_pages['page_count']} 个银行页面"

[关闭浏览器]
```

## 最佳实践

### 1. 页面ID管理
- 始终保存重要页面的ID到全局变量
- 使用有意义的变量名，如"主页面ID"、"商品页面ID"

### 2. 新窗口检测
- 在点击可能打开新窗口的元素后，检查页面数量变化
- 使用适当的等待时间让新窗口完全加载

### 3. 错误处理
- 在切换页面前验证页面ID是否存在
- 使用try-catch处理可能的页面切换错误

### 4. 性能考虑
- 不要打开过多窗口，及时关闭不需要的页面
- 定期清理页面列表

## 故障排除

### 问题1: 新窗口没有被检测到
- **原因**: 页面加载时间不够
- **解决**: 增加等待时间或使用更精确的等待条件

### 问题2: 页面切换失败
- **原因**: 页面ID不存在或已关闭
- **解决**: 使用`获取页面列表`验证页面是否存在

### 问题3: 弹窗被阻止
- **原因**: 浏览器弹窗阻止设置
- **解决**: 在浏览器启动配置中禁用弹窗阻止

```yaml
[启动浏览器], 配置: '''
  args:
    - "--disable-popup-blocking"
    - "--disable-web-security"
'''
```

## 注意事项

1. **浏览器限制**: 某些浏览器可能阻止弹窗，需要适当配置
2. **时序问题**: 新窗口打开需要时间，确保有足够的等待
3. **内存使用**: 多窗口会增加内存使用，测试完成后及时关闭
4. **并发限制**: 不要同时打开过多窗口，可能影响性能

通过这些功能，你可以轻松处理各种多窗口测试场景！ 