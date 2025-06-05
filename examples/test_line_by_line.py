#!/usr/bin/env python3
"""逐行分析脚本转换过程"""

from pytest_dsl_ui.utils.playwright_converter import PlaywrightToDSLConverter

# 完整的测试脚本
full_script = '''
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

def test_line_by_line():
    """逐行分析转换过程"""
    
    # 首先找到wait_for_event行
    lines = full_script.split('\n')
    wait_line_number = None
    for i, line in enumerate(lines, 1):
        if 'wait_for_event' in line:
            wait_line_number = i
            print(f"找到wait_for_event在第{i}行: {repr(line.strip())}")
            break
    
    if not wait_line_number:
        print("❌ 没有找到wait_for_event行!")
        return
    
    # 转换并查看结果
    converter = PlaywrightToDSLConverter()
    result = converter.convert_script(full_script)
    
    print(f"\n完整转换结果:")
    print("=" * 50)
    print(result)
    
    # 检查结果中是否包含监听下载
    if '[监听下载]' in result:
        print(f"\n✅ 转换结果包含监听下载关键字")
        
        # 找到监听下载行
        result_lines = result.split('\n')
        for i, line in enumerate(result_lines, 1):
            if '[监听下载]' in line:
                print(f"   第{i}行: {line}")
            if '原代码:' in line and 'wait_for_event' in line:
                print(f"   第{i}行: {line}")
    else:
        print(f"\n❌ 转换结果不包含监听下载关键字!")
        
        # 查看是否有其他相关的处理
        if 'wait_for_event' in result:
            print("   但包含wait_for_event原文")
        else:
            print("   也不包含wait_for_event原文")
    
    # 检查其他关键特征
    checks = [
        ('[等待下载]', '等待下载关键字'),
        ('download_path', '下载路径变量'),
        ('[验证下载文件]', '验证下载文件'),
        ('[点击元素]', '点击元素关键字'),
        ('[截图]', '截图关键字')
    ]
    
    print(f"\n其他关键字检查:")
    for pattern, desc in checks:
        found = pattern in result
        status = "✅" if found else "❌"
        print(f"   {status} {desc}: {found}")

if __name__ == "__main__":
    test_line_by_line() 