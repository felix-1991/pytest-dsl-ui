#!/usr/bin/env python3
"""测试Playwright下载操作转换"""

from pytest_dsl_ui.utils.playwright_converter import PlaywrightToDSLConverter

# 测试下载操作的Playwright脚本
playwright_download_script = '''
from playwright.sync_api import Playwright, sync_playwright

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://example.com/download")
    
    # 下载文件
    with page.expect_download() as download_info:
        page.get_by_text("Download PDF").click()
    download = download_info.value
    download.save_as("./downloads/example.pdf")
    
    # 简单的下载等待
    page.wait_for_event('download')
    page.get_by_role("button", name="Download").click()
    
    # 截图
    page.screenshot(path="./screenshots/download_page.png")
    
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
'''

def test_download_conversion():
    """测试下载操作转换"""
    converter = PlaywrightToDSLConverter()
    result = converter.convert_script(playwright_download_script)
    
    print("原始Playwright脚本:")
    print("=" * 50)
    print(playwright_download_script)
    print("\n转换后的DSL:")
    print("=" * 50)
    print(result)
    
    # 调试：显示转换后DSL的每一行
    print("\n" + "=" * 50)
    print("转换后DSL逐行分析:")
    print("=" * 50)
    lines = result.split('\n')
    for i, line in enumerate(lines, 1):
        if 'wait_for_event' in line.lower() or 'monitor' in line.lower() or '监听' in line:
            print(f"🔍 Line {i}: {line}")
        elif '[监听下载]' in line:
            print(f"✅ Line {i}: {line}")
        elif line.strip() and not line.startswith('@') and not line.startswith('#'):
            print(f"   Line {i}: {line}")
    
    # 检查关键的转换结果
    expected_features = [
        ("[启动浏览器]", "浏览器启动"),
        ("[打开页面]", "页面导航"), 
        ("[等待下载]", "下载等待关键字"),
        ("触发元素", "下载触发器"),
        ("变量名", "变量处理"),
        ("[验证下载文件]", "下载验证"),
        ("wait_for_event", "事件等待处理"),
        ("[截图]", "截图功能"),
        ("[关闭浏览器]", "浏览器关闭")
    ]
    
    print("\n" + "=" * 50)
    print("转换检查结果:")
    print("=" * 50)
    
    for feature, description in expected_features:
        if feature in result:
            print(f"✅ {description}: 找到 '{feature}'")
        else:
            print(f"❌ {description}: 缺少 '{feature}'")
    
    # 检查是否正确处理了复杂的下载逻辑
    complex_checks = [
        ("download_path =", "下载路径变量赋值"),
        ("保存文件到:", "文件保存处理"),
        ("[监听下载]", "下载事件等待转换"),
        ("原代码: page.wait_for_event", "原wait_for_event代码注释")
    ]
    
    print("\n特殊下载功能检查:")
    print("-" * 30)
    for check, description in complex_checks:
        if check in result:
            print(f"✅ {description}: 正确处理")
        else:
            print(f"❌ {description}: 未处理")

if __name__ == "__main__":
    test_download_conversion() 