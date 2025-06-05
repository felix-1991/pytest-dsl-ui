#!/usr/bin/env python3
"""专门测试wait_for_event行"""

from pytest_dsl_ui.utils.playwright_converter import PlaywrightToDSLConverter

# 只包含wait_for_event的行
just_wait_script = '''page.wait_for_event('download')'''

# 含完整函数的脚本
function_script = '''
def test():
    page.wait_for_event('download')
'''

def test_specific_wait():
    """测试特定的wait_for_event行"""
    converter = PlaywrightToDSLConverter()
    
    print("=== 测试1: 只有wait_for_event行 ===")
    result1 = converter.convert_script(just_wait_script)
    print("转换结果:")
    print(result1)
    print(f"包含监听下载: {'[监听下载]' in result1}")
    print(f"包含原代码: {'原代码:' in result1}")
    
    print("\n=== 测试2: 带函数定义的脚本 ===")
    result2 = converter.convert_script(function_script)
    print("转换结果:")
    print(result2)
    print(f"包含监听下载: {'[监听下载]' in result2}")
    print(f"包含原代码: {'原代码:' in result2}")

if __name__ == "__main__":
    test_specific_wait() 