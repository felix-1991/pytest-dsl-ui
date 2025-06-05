#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest-dsl-ui 默认值使用示例

展示了如何利用关键字的默认值功能简化DSL脚本编写。
"""

from pytest_dsl.core.keyword_manager import keyword_manager

# 示例：发送邮件关键字（参考您提供的样例）
@keyword_manager.register('发送邮件', [
    {'name': '收件人', 'mapping': 'to_email', 'description': '收件人邮箱'},
    {'name': '主题', 'mapping': 'subject', 'description': '邮件主题', 'default': '测试邮件'},
    {'name': '内容', 'mapping': 'content', 'description': '邮件内容', 'default': '这是一封测试邮件'},
    {'name': '优先级', 'mapping': 'priority', 'description': '邮件优先级', 'default': 'normal'}
])
def send_email(**kwargs):
    """发送邮件通知"""
    to_email = kwargs.get('to_email')
    subject = kwargs.get('subject', '测试邮件')
    content = kwargs.get('content', '这是一封测试邮件')
    priority = kwargs.get('priority', 'normal')

    # 实现邮件发送逻辑
    print(f"发送邮件到 {to_email}: {subject} (优先级: {priority})")
    return True

"""
DSL脚本使用示例：

## 基础用法（所有参数都显式指定）
发送邮件:
  收件人: user@example.com
  主题: 登录测试通知
  内容: 测试已完成，请查看结果
  优先级: high

## 使用默认值（只指定必需参数）
发送邮件:
  收件人: admin@example.com
  # 主题将使用默认值：测试邮件
  # 内容将使用默认值：这是一封测试邮件
  # 优先级将使用默认值：normal

## 部分使用默认值
发送邮件:
  收件人: dev@example.com
  主题: 自动化测试报告
  # 内容和优先级使用默认值

## 浏览器操作使用默认值示例

# 启动浏览器（使用默认值）
启动浏览器:
  # 浏览器类型默认：chromium
  # 无头模式默认：True
  # 慢动作默认：0
  # 配置默认：{}
  # 忽略证书错误默认：True

# 打开页面（使用默认值）
打开页面:
  地址: https://example.com
  # 等待条件默认：load
  # 超时时间默认：30
  # 忽略证书错误默认：True

# 点击元素（使用默认值）
点击元素:
  定位器: button[type="submit"]
  # 超时时间默认：30
  # 强制点击默认：False
  # 可见性默认：False

# 输入文本（使用默认值）
输入文本:
  定位器: input[name="username"]
  文本: admin
  # 清空输入框默认：True
  # 超时时间默认：30

# 断言元素可见（使用默认值）
断言元素可见:
  定位器: .success-message
  # 超时时间默认：5.0

# 截图（使用默认值）
截图:
  文件名: test_result.png
  # 全页面默认：False

# 加载认证状态（使用默认值）
加载认证状态:
  状态名称: admin_login
  # 创建新上下文默认：True
  # 验证登录默认：True

## 优势说明：

1. **简化DSL脚本**：不需要为每个参数都指定值
2. **减少错误**：使用经过验证的默认值
3. **提高可读性**：只显示关键配置，突出重点
4. **向后兼容**：现有脚本仍然正常工作
5. **灵活性**：可以选择性覆盖默认值

## 注意事项：

1. 必需参数（如定位器、地址等）仍然需要显式指定
2. 默认值在关键字注册时定义，确保一致性
3. 可以通过函数内的kwargs.get()访问默认值
4. 框架会自动处理默认值的应用
"""

if __name__ == "__main__":
    print("这是pytest-dsl-ui默认值功能的示例文件")
    print("请查看文件内容了解如何使用默认值功能") 