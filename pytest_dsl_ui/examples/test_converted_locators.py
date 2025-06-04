#!/usr/bin/env python3
"""
转换后定位器测试

测试从Playwright转换后的定位器是否能正确工作
"""

from playwright.sync_api import sync_playwright
from pytest_dsl_ui.core.element_locator import ElementLocator


def test_converted_locators():
    """测试转换后的定位器"""
    
    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        # 创建更接近实际情况的HTML页面
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>转换后定位器测试</title>
        </head>
        <body>
            <!-- 模拟表格cell结构 -->
            <table>
                <tr>
                    <td role="cell" aria-label="外到内">
                        <label>选择外到内</label>
                        <span>外到内</span>
                    </td>
                    <td role="cell" aria-label="内到外">
                        <label>选择内到外</label>
                        <span>内到外</span>
                    </td>
                </tr>
            </table>
            
            <!-- 模拟日志检索结构 -->
            <div aria-label="日志检索">
                <div>日志检索</div>
                <span>其他内容</span>
            </div>
            
            <!-- 模拟专家模式 -->
            <button>专家模式</button>
        </body>
        </html>
        """
        
        page.set_content(html_content)
        
        # 创建ElementLocator实例
        locator = ElementLocator(page)
        
        print("=== 测试转换后的定位器 ===\n")
        
        # 测试1: 转换后的复杂定位器
        print("测试1: role=cell:外到内&locator=label&first=true")
        try:
            # 这是转换器生成的定位器格式
            converted_locator = locator.locate("role=cell:外到内&locator=label&first=true")
            if converted_locator.count() > 0:
                text = converted_locator.text_content()
                print(f"✅ 成功找到元素，文本: '{text}'")
            else:
                print("❌ 未找到匹配的元素")
        except Exception as e:
            print(f"❌ 测试1失败: {e}")
        
        # 测试2: 精确匹配的文本定位器
        print("\n测试2: text=专家模式,exact=true")
        try:
            text_locator = locator.locate("text=专家模式,exact=true")
            if text_locator.count() > 0:
                text = text_locator.text_content()
                print(f"✅ 成功找到元素，文本: '{text}'")
            else:
                print("❌ 未找到匹配的元素")
        except Exception as e:
            print(f"❌ 测试2失败: {e}")
        
        # 测试3: 标签定位器加过滤
        print("\n测试3: label=日志检索,exact=true&locator=div&has_text=日志检索")
        try:
            label_locator = locator.locate("label=日志检索,exact=true&locator=div&has_text=日志检索")
            if label_locator.count() > 0:
                text = label_locator.text_content()
                print(f"✅ 成功找到元素，文本: '{text}'")
            else:
                print("❌ 未找到匹配的元素")
        except Exception as e:
            print(f"❌ 测试3失败: {e}")
        
        # 测试4: 对比原始Playwright方法
        print("\n测试4: 对比原始Playwright方法")
        try:
            # 原始方法
            original = page.get_by_role("cell", name="外到内").locator("label").first
            original_text = original.text_content() if original.count() > 0 else "未找到"
            
            # 转换后的方法
            converted = locator.locate("role=cell:外到内&locator=label&first=true")
            converted_text = converted.text_content() if converted.count() > 0 else "未找到"
            
            print(f"原始方法结果: '{original_text}'")
            print(f"转换方法结果: '{converted_text}'")
            
            if original_text == converted_text:
                print("✅ 两种方法结果一致！")
            else:
                print("❌ 两种方法结果不一致")
                
        except Exception as e:
            print(f"❌ 测试4失败: {e}")
        
        # 清理
        browser.close()


if __name__ == "__main__":
    test_converted_locators() 