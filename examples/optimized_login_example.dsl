@name: "优化的认证状态管理示例"
@description: "展示如何使用认证状态管理实现登录复用，登录逻辑自定义实现"
@tags: [UI, 自动化, 认证, 状态管理]
@author: "陈双麟"

# 启动浏览器
[启动浏览器], 浏览器: "chromium", 无头模式: False

# 定义登录状态名称
$login_state_name = "admin_login_state"

# 检查是否已有认证状态
has_auth = [检查认证状态], 状态名称: "${login_state_name}"

# 如果没有认证状态，则执行登录并保存状态
if has_auth == False do
    [打印], 内容: "没有找到认证状态，开始执行登录流程"
    
    # 打开登录页面
    [打开页面], 地址: "https://10.65.173.36/login#/"
    
    # 定义自定义登录关键字（适应具体系统的登录方式）
    function 执行系统登录() do
        [打印], 内容: "开始尝试登录系统"
        [点击元素], 定位器: "role=textbox:请输入您的用户名"
        [输入文本], 定位器: "role=textbox:请输入您的用户名", 文本: "admin"
        [输入文本], 定位器: "role=textbox:请输入您的密码", 文本: "admin"
        [点击元素], 定位器: "role=checkbox:我已阅读并同意"
        
        # 验证码重试逻辑
        for i in range(1, 5) do
            [打印], 内容: "第${i}次登录尝试"
            captcha_text = [识别文字验证码], 图片源: ".uedc-ppkg-login_captcha", 源类型: "element", 变量名: "验证码文本"
            [打印], 内容: "识别到验证码: ${captcha_text}"
            
            [输入文本], 定位器: "role=textbox:请按右图输入验证码", 文本: "${captcha_text}"
            [点击元素], 定位器: "role=button:立即登录"
            [等待], 秒数: 3
            
            # 检查登录是否成功
            login_button = [检查元素是否可见], 定位器: "role=button:立即登录", 超时时间: 10
            
            if login_button == False do
                [打印], 内容: "登录成功！"
                return True
            else
                [打印], 内容: "第${i}次登录失败，准备重试"
            end
        end
        
        [断言], 条件: False, 消息: "登录失败"   
    end
    
    # 执行登录
    [执行系统登录]
    
    # 登录成功后保存认证状态
    [保存认证状态], 状态名称: "${login_state_name}", 用户名: "admin", 描述: "管理员登录状态"
    [打印], 内容: "认证状态已保存: ${login_state_name}"
    
else
    [打印], 内容: "找到已保存的认证状态，直接加载"
    
    # 加载认证状态
    [加载认证状态], 状态名称: "${login_state_name}", 创建新上下文: True
    [打印], 内容: "认证状态加载成功"
    
    # 导航到主页面（因为加载状态后需要手动导航）
    [打开页面], 地址: "https://10.65.173.36/login#/"
end

# 执行业务操作（无论是新登录还是加载状态，都会执行这些操作）
[点击元素], 定位器: "role=button:以后再说"
[点击元素], 定位器: "clickable=日志检索"
[点击元素], 定位器: "role=button:简易模式 down"
[点击元素], 定位器: "text=专家模式,exact=true"
[点击元素], 定位器: "role=textbox:请选择访问方向"
[点击元素], 定位器: "text=外到内"
[点击元素], 定位器: "role=cell:外到内&locator=label&first=true"

# 查看当前所有认证状态
[列出认证状态], 变量名: "all_states"
[打印], 内容: "当前保存的认证状态: ${all_states}"

# 如果需要清除认证状态（可选，用于调试或重置）
# [清除认证状态], 状态名称: "${login_state_name}"
# [清除所有认证状态], 确认清除: True

# 关闭浏览器
[关闭浏览器] 