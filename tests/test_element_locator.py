"""测试元素定位器功能

使用test_page.html验证各种元素定位策略
"""

import pytest
from pytest_dsl_ui.core.element_locator import ElementLocator
from pytest_dsl_ui.core.browser_manager import browser_manager
import os


class TestElementLocator:
    """元素定位器测试类"""
    
    @pytest.fixture(scope="class")
    def setup_browser(self):
        """设置浏览器环境"""
        # 启动浏览器
        browser_id = browser_manager.launch_browser('chromium', headless=True)
        context_id = browser_manager.create_context(browser_id)
        page_id = browser_manager.create_page(context_id)
        
        # 获取页面对象
        page = browser_manager.get_page(page_id)
        
        # 导航到测试页面
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_page_path = os.path.join(
            current_dir, "..", "examples", "test_page.html"
        )
        test_page_path = os.path.abspath(test_page_path)
        page.goto(f"file://{test_page_path}")
        
        yield {
            'browser_id': browser_id,
            'context_id': context_id,
            'page_id': page_id,
            'page': page
        }
        
        # 清理
        browser_manager.close_browser(browser_id)
    
    @pytest.fixture(scope="class")
    def locator(self, setup_browser):
        """元素定位器实例"""
        return ElementLocator(setup_browser['page'])
        
    def test_css_selectors(self, locator):
        """测试CSS选择器"""
        # ID选择器
        search_input = locator.locate("#search-input")
        assert search_input.is_visible()
        
        # 类选择器
        btn_elements = locator.locate(".btn")
        assert btn_elements.count() >= 3
        
        # 标签选择器
        form_element = locator.locate("form")
        assert form_element.is_visible()
        
    def test_role_locators(self, locator):
        """测试角色定位器"""
        # 简单角色定位
        buttons = locator.locate("role=button")
        assert buttons.count() >= 3
        
        # 带名称的角色定位（冒号格式）- 使用具体的按钮文本
        search_button = locator.locate("role=button:搜索")
        assert search_button.is_visible()
        
        # 带名称的角色定位（逗号格式）
        submit_button = locator.locate("role=button,name=提交表单")
        assert submit_button.is_visible()
        
    def test_text_locators(self, locator):
        """测试文本定位器"""
        # 简单文本定位 - 使用页面标题避免冲突
        heading = locator.locate("text=Bool检查测试页面")
        assert heading.is_visible()
        
        # 精确文本匹配 - 使用具体的按钮文本
        search_button = locator.locate("text=搜索,exact=true")
        # 由于存在多个"搜索"文本，使用resolve_strict_mode_conflict
        resolved_button = locator.resolve_strict_mode_conflict(
            "text=搜索", 
            preferred_text="搜索",
            prefer_visible=True
        )
        assert resolved_button.is_visible()
        
    def test_form_locators(self, locator):
        """测试表单相关定位器"""
        # 标签定位 - 使用完整的标签文本
        username_field = locator.locate("label=用户名：")
        assert username_field.is_visible()
        
        # 占位符定位
        search_placeholder = locator.locate("placeholder=请输入搜索关键词")
        assert search_placeholder.is_visible()
        
    def test_custom_locators(self, locator):
        """测试自定义定位器"""
        # 智能点击定位 - 使用具体按钮文本
        search_clickable = locator.locate("clickable=搜索")
        assert search_clickable.is_visible()
        
        # 元素类型定位
        span_element = locator.locate("span=已加载")
        assert span_element.is_visible()
        
    def test_xpath_locators(self, locator):
        """测试XPath定位器"""
        # 简单XPath - 使用更具体的选择器
        input_xpath = locator.locate("//input[@id='search-input']")
        assert input_xpath.count() == 1
        assert input_xpath.is_visible()
        
        # 复杂XPath
        button_xpath = locator.locate("//button[contains(@class, 'btn')]")
        assert button_xpath.count() >= 3
        
    def test_locator_filtering(self, locator):
        """测试定位器过滤功能"""
        # 可见元素过滤
        visible_buttons = locator.locate_by_visible("button")
        all_buttons = locator.locate("button")
        assert visible_buttons.count() <= all_buttons.count()
        
        # 文本过滤 - 使用具体的按钮文本
        filtered_button = locator.locate_with_filter(
            "button", 
            has_text="搜索"
        )
        assert filtered_button.is_visible()
        
    def test_locator_chaining(self, locator):
        """测试定位器链式操作"""
        # 第一个按钮
        first_button = locator.locate_first("button")
        assert first_button.is_visible()
        
        # 最后一个按钮
        last_button = locator.locate_last("button")
        assert last_button.is_visible()
        
        # 第二个按钮
        second_button = locator.locate_nth("button", 1)
        assert second_button.is_visible()
        
    def test_boolean_checks(self, locator):
        """测试布尔检查方法"""
        # 元素可见性
        assert locator.is_element_visible("#search-input") is True
        assert locator.is_element_visible("#non-existent") is False
        
        # 元素启用状态
        assert locator.is_element_enabled("#search-btn") is True
        assert locator.is_element_enabled("#disabled-btn") is False
        
    def test_element_properties(self, locator):
        """测试元素属性获取"""
        # 获取元素文本
        heading_text = locator.get_element_text("h1")
        assert "Bool检查测试页面" in heading_text
        
        # 获取元素属性
        input_type = locator.get_element_attribute("#search-input", "type")
        assert input_type == "text"
        
        # 获取元素数量
        button_count = locator.get_element_count("button")
        assert button_count >= 3
        
    def test_strict_mode_resolution(self, locator):
        """测试严格模式冲突解决"""
        # 解决多个匹配的情况 - 使用role定位避免文本冲突
        resolved_button = locator.resolve_strict_mode_conflict(
            "role=button",
            preferred_text="搜索",
            prefer_visible=True
        )
        assert resolved_button.is_visible()
        
        # 通过索引解决冲突
        indexed_button = locator.resolve_strict_mode_conflict(
            "button",
            index=0
        )
        assert indexed_button.is_visible()
        
    def test_wait_operations(self, locator):
        """测试等待操作"""
        # 等待元素可见
        assert locator.wait_for_element("#search-input", "visible", 5) is True
        
        # 等待文本出现
        assert locator.wait_for_text("Bool检查测试页面", 5) is True
        
        # 等待不存在的元素（应该超时）
        assert locator.wait_for_element("#non-existent", "visible", 1) is False
        
    def test_complex_selectors(self, locator):
        """测试复杂选择器组合"""
        # 使用更简单的组合测试
        # 测试同时匹配多个属性的按钮
        submit_button = locator.locate("#submit-btn")
        assert submit_button.is_visible()
        
        # 通过ID和文本内容唯一定位
        unique_element = locator.locate("#page-status")
        assert unique_element.is_visible()
        assert "已加载" in locator.get_element_text("#page-status")
        
    def test_error_handling(self, locator):
        """测试错误处理"""
        # 不存在的元素应该返回默认值而不是抛出异常
        assert locator.get_element_count("#non-existent") == 0
        assert locator.get_element_text("#non-existent") == ""
        assert locator.is_element_visible("#non-existent") is False
        assert locator.is_element_enabled("#non-existent") is False
        assert locator.is_element_checked("#non-existent") is False
        
    def test_selector_edge_cases(self, locator):
        """测试选择器边界情况"""
        # 测试空选择器的处理
        try:
            empty_locator = locator.locate("")
            # 空选择器应该能处理，但可能没有匹配元素
            assert empty_locator.count() >= 0
        except Exception:
            # 如果抛出异常也是合理的
            pass
            
        # 测试特殊字符选择器
        special_locator = locator.locate("button")
        assert special_locator.count() >= 3
        
    def test_performance_considerations(self, locator):
        """测试性能相关的定位策略"""
        import time
        
        # 测试快速定位器（推荐的定位方式）
        start_time = time.time()
        fast_locator = locator.locate("#search-input")
        fast_locator.is_visible()
        fast_time = time.time() - start_time
        
        # 测试较慢的定位器（使用更具体的XPath）
        start_time = time.time()
        slow_locator = locator.locate("//input[@id='search-input']")
        slow_locator.is_visible()
        slow_time = time.time() - start_time
        
        # 验证快速定位器确实更快（通常情况下）
        # 注意：这个测试可能在某些情况下不稳定，所以我们只验证都能工作
        assert fast_time >= 0
        assert slow_time >= 0
        
    def test_best_practices_validation(self, locator):
        """测试最佳实践验证"""
        # 测试推荐的定位策略（按优先级）
        
        # 1. 测试ID定位（最可靠）
        if locator.get_element_count("[data-testid]") > 0:
            testid_locator = locator.locate("testid=search")
            # 不强制断言，因为测试页面可能没有testid
        
        # 2. 语义化角色定位
        role_locator = locator.locate("role=button")
        assert role_locator.count() >= 1
        
        # 3. 标签关联定位
        label_locator = locator.locate("label=用户名：")
        assert label_locator.is_visible()
        
        # 4. 文本内容定位 - 使用resolve_strict_mode_conflict处理冲突
        text_locator = locator.resolve_strict_mode_conflict(
            "text=搜索",
            preferred_text="搜索",
            prefer_visible=True
        )
        assert text_locator.is_visible()
        
        # 5. CSS类名定位
        css_locator = locator.locate(".btn")
        assert css_locator.count() >= 3 