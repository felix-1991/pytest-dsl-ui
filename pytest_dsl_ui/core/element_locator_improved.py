"""改进的元素定位器

基于Playwright官方最佳实践，提供更可靠、更高性能的元素定位策略。
修复了原实现中的问题并增加了新功能。
"""

import logging
import re
from typing import Optional, List, Union, Dict, Any
from playwright.sync_api import (
    Page,
    Locator,
    TimeoutError as PlaywrightTimeoutError
)

logger = logging.getLogger(__name__)


class ImprovedElementLocator:
    """改进的元素定位器
    
    基于Playwright官方最佳实践设计：
    1. 优先使用用户面向的属性（角色、文本、标签等）
    2. 避免脆弱的CSS和XPath选择器
    3. 提供智能的冲突解决机制
    4. 支持现代Web标准（ARIA、语义化HTML等）
    """

    def __init__(self, page: Page):
        """初始化元素定位器

        Args:
            page: Playwright页面实例
        """
        self.page = page
        self.default_timeout = 30000  # 默认超时30秒
        
        # 定位器策略优先级（从高到低）
        self.locator_priority = [
            'testid',      # 最可靠：测试ID
            'role',        # 推荐：ARIA角色
            'label',       # 推荐：标签关联
            'placeholder', # 推荐：占位符
            'text',        # 可接受：文本内容
            'alt',         # 可接受：Alt文本
            'title',       # 较少使用：标题属性
            'css',         # 需谨慎：CSS选择器
            'xpath'        # 最后选择：XPath
        ]

    def set_default_timeout(self, timeout: float):
        """设置默认超时时间

        Args:
            timeout: 超时时间（秒）
        """
        self.default_timeout = int(timeout * 1000)
        logger.info(f"设置默认超时时间: {timeout}秒")

    def locate(self, selector: str, **kwargs) -> Locator:
        """智能定位元素
        
        根据Playwright最佳实践，自动选择最合适的定位策略。
        
        Args:
            selector: 元素选择器，支持多种格式
            **kwargs: 额外的定位参数
            
        Returns:
            Locator: Playwright定位器对象
            
        Raises:
            ValueError: 无效的选择器格式
        """
        if not selector or not selector.strip():
            raise ValueError("选择器不能为空")
            
        selector = selector.strip()
        
        # 解析选择器类型和参数
        locator_type, locator_value, locator_options = self._parse_selector(selector)
        
        # 合并传入的kwargs
        locator_options.update(kwargs)
        
        # 根据类型创建定位器
        return self._create_locator(locator_type, locator_value, locator_options)

    def _parse_selector(self, selector: str) -> tuple[str, str, Dict[str, Any]]:
        """解析选择器字符串
        
        Args:
            selector: 选择器字符串
            
        Returns:
            tuple: (定位器类型, 定位器值, 选项字典)
        """
        # XPath选择器识别
        if selector.startswith(("//", "(//")):
            return "xpath", selector, {}
            
        # 前缀式选择器识别
        if "=" in selector and not selector.startswith(("http://", "https://", "file://")):
            prefix, value = selector.split("=", 1)
            prefix = prefix.strip().lower()
            
            if prefix in ["text", "role", "label", "placeholder", "alt", "title", "testid", "clickable"]:
                return self._parse_prefixed_selector(prefix, value)
                
        # 默认为CSS选择器
        return "css", selector, {}

    def _parse_prefixed_selector(self, prefix: str, value: str) -> tuple[str, str, Dict[str, Any]]:
        """解析前缀式选择器
        
        Args:
            prefix: 选择器前缀
            value: 选择器值
            
        Returns:
            tuple: (定位器类型, 定位器值, 选项字典)
        """
        options = {}
        
        if prefix == "text":
            # 解析文本选择器：text=Hello,exact=true
            if "," in value:
                parts = [part.strip() for part in value.split(",")]
                text_value = parts[0]
                for part in parts[1:]:
                    if "=" in part:
                        key, val = part.split("=", 1)
                        key = key.strip()
                        val = val.strip()
                        if val.lower() in ("true", "false"):
                            options[key] = val.lower() == "true"
                        else:
                            options[key] = val
                return "text", text_value, options
            return "text", value, options
            
        elif prefix == "role":
            # 解析角色选择器：role=button:Submit 或 role=button,name=Submit
            if ":" in value and "," not in value:
                role, name = value.split(":", 1)
                return "role", role.strip(), {"name": name.strip()}
            elif "," in value:
                parts = [part.strip() for part in value.split(",")]
                role = parts[0]
                for part in parts[1:]:
                    if "=" in part:
                        key, val = part.split("=", 1)
                        key = key.strip()
                        val = val.strip()
                        if val.lower() in ("true", "false"):
                            options[key] = val.lower() == "true"
                        else:
                            options[key] = val
                return "role", role, options
            return "role", value, options
            
        elif prefix == "clickable":
            # 智能可点击元素定位
            return "clickable", value, options
            
        # 其他前缀直接返回
        return prefix, value, options

    def _create_locator(self, locator_type: str, value: str, options: Dict[str, Any]) -> Locator:
        """根据类型创建定位器
        
        Args:
            locator_type: 定位器类型
            value: 定位器值
            options: 定位器选项
            
        Returns:
            Locator: 创建的定位器
        """
        try:
            if locator_type == "role":
                return self.page.get_by_role(value, **options)
            elif locator_type == "text":
                return self.page.get_by_text(value, **options)
            elif locator_type == "label":
                return self.page.get_by_label(value, **options)
            elif locator_type == "placeholder":
                return self.page.get_by_placeholder(value, **options)
            elif locator_type == "alt":
                return self.page.get_by_alt_text(value, **options)
            elif locator_type == "title":
                return self.page.get_by_title(value, **options)
            elif locator_type == "testid":
                return self.page.get_by_test_id(value, **options)
            elif locator_type == "clickable":
                return self._locate_clickable_element(value, **options)
            elif locator_type == "xpath":
                return self.page.locator(f"xpath={value}", **options)
            elif locator_type == "css":
                return self.page.locator(value, **options)
            else:
                # 回退到CSS选择器
                logger.warning(f"未知的定位器类型: {locator_type}，回退到CSS选择器")
                return self.page.locator(value, **options)
                
        except Exception as e:
            logger.error(f"创建定位器失败: {locator_type}={value}, 错误: {e}")
            # 尝试回退到基本的CSS定位器
            return self.page.locator(value)

    def _locate_clickable_element(self, text: str, **options) -> Locator:
        """智能定位可点击元素
        
        按优先级查找可点击元素：
        1. 明确的按钮角色
        2. 链接角色
        3. 其他交互角色
        4. 具有点击事件的元素
        
        Args:
            text: 元素文本
            **options: 额外选项
            
        Returns:
            Locator: 最适合的可点击元素定位器
        """
        # 优先级顺序的角色列表
        clickable_roles = [
            "button",
            "link", 
            "menuitem",
            "tab",
            "option"
        ]
        
        # 尝试按角色查找
        for role in clickable_roles:
            try:
                locator = self.page.get_by_role(role, name=text)
                if locator.count() > 0:
                    return locator.first
            except Exception:
                continue
        
        # 尝试通过元素类型和文本查找
        clickable_selectors = [
            f"button:has-text('{text}')",
            f"a:has-text('{text}')",
            f"[role='button']:has-text('{text}')",
            f"[onclick]:has-text('{text}')",
            f"span:has-text('{text}')",
            f"div:has-text('{text}')"
        ]
        
        for selector in clickable_selectors:
            try:
                locator = self.page.locator(selector)
                if locator.count() > 0:
                    return locator.first
            except Exception:
                continue
                
        # 最后回退到文本定位
        return self.page.get_by_text(text).first

    def locate_by_best_practice(self, 
                               text: Optional[str] = None,
                               role: Optional[str] = None,
                               label: Optional[str] = None,
                               placeholder: Optional[str] = None,
                               test_id: Optional[str] = None,
                               fallback_css: Optional[str] = None) -> Locator:
        """使用最佳实践定位元素
        
        按照Playwright推荐的优先级顺序查找元素。
        
        Args:
            text: 文本内容
            role: ARIA角色
            label: 标签文本
            placeholder: 占位符文本
            test_id: 测试ID
            fallback_css: 回退CSS选择器
            
        Returns:
            Locator: 找到的定位器
            
        Raises:
            ValueError: 未提供任何定位参数
        """
        if not any([text, role, label, placeholder, test_id, fallback_css]):
            raise ValueError("必须提供至少一个定位参数")
        
        # 按最佳实践优先级尝试定位
        if test_id:
            locator = self.page.get_by_test_id(test_id)
            if locator.count() > 0:
                return locator
                
        if role:
            if text:
                locator = self.page.get_by_role(role, name=text)
            else:
                locator = self.page.get_by_role(role)
            if locator.count() > 0:
                return locator
                
        if label:
            locator = self.page.get_by_label(label)
            if locator.count() > 0:
                return locator
                
        if placeholder:
            locator = self.page.get_by_placeholder(placeholder)
            if locator.count() > 0:
                return locator
                
        if text:
            locator = self.page.get_by_text(text)
            if locator.count() > 0:
                return locator
                
        if fallback_css:
            locator = self.page.locator(fallback_css)
            if locator.count() > 0:
                return locator
                
        # 如果都没找到，返回空定位器
        return self.page.locator("non-existent-element-12345")

    def wait_for_element(self, selector: str, state: str = "visible", 
                         timeout: Optional[float] = None) -> bool:
        """等待元素达到指定状态

        Args:
            selector: 元素选择器
            state: 等待状态 (visible, hidden, attached, detached)
            timeout: 超时时间（秒）

        Returns:
            bool: 是否在超时时间内达到指定状态
        """
        timeout_ms = int((timeout * 1000) if timeout else self.default_timeout)

        try:
            # 特殊处理clickable定位器，确保与click操作行为一致
            if selector.startswith("clickable="):
                text = selector[10:]  # 移除"clickable="前缀
                
                # 对于clickable定位器，我们需要确保元素不仅存在，还要可点击
                # 这与_locate_clickable_element的逻辑保持一致
                clickable_selectors = [
                    f"button:has-text('{text}')",
                    f"a:has-text('{text}')", 
                    f"[role='button']:has-text('{text}')",
                    f"[role='link']:has-text('{text}')",
                    f"[role='menuitem']:has-text('{text}')"
                ]
                
                # 首先尝试明确的可点击元素
                for css_selector in clickable_selectors:
                    locator = self.page.locator(css_selector)
                    if locator.count() > 0:
                        locator.first.wait_for(state=state, timeout=timeout_ms)
                        return True
                
                # 如果没有找到明确的可点击元素，尝试文本匹配
                text_locator = self.page.get_by_text(text, exact=True)
                if text_locator.count() > 0:
                    # 对于多个匹配，优先选择span或div元素
                    if text_locator.count() > 1:
                        span_locator = self.page.locator(
                            f"span:has-text('{text}')")
                        if span_locator.count() > 0:
                            span_locator.first.wait_for(
                                state=state, timeout=timeout_ms)
                            return True
                        
                        div_locator = self.page.locator(
                            f"div:has-text('{text}')")
                        if div_locator.count() > 0:
                            div_locator.first.wait_for(
                                state=state, timeout=timeout_ms)
                            return True
                    
                    # 使用第一个匹配的元素
                    text_locator.first.wait_for(
                        state=state, timeout=timeout_ms)
                    return True
                else:
                    # 尝试模糊匹配
                    fuzzy_locator = self.page.get_by_text(text)
                    if fuzzy_locator.count() > 0:
                        fuzzy_locator.first.wait_for(
                            state=state, timeout=timeout_ms)
                        return True
                    
                return False
            else:
                # 对于其他类型的定位器，使用标准等待逻辑
                locator = self.locate(selector)
                locator.wait_for(state=state, timeout=timeout_ms)
                return True
                
        except PlaywrightTimeoutError:
            logger.warning(
                f"等待元素超时: {selector}, 状态: {state}, "
                f"超时: {timeout_ms}ms"
            )
            return False
        except Exception as e:
            # 记录其他异常信息，但仍然返回False而不是抛出异常
            logger.warning(
                f"等待元素时发生异常: {selector}, 错误: {str(e)}"
            )
            return False

    def is_element_visible(self, selector: str) -> bool:
        """检查元素是否可见"""
        try:
            # 特殊处理clickable定位器，确保与其他操作行为一致
            if selector.startswith("clickable="):
                # 使用_locate_clickable_element方法获取智能定位的元素
                locator = self._locate_clickable_element(selector[10:])
                return locator.is_visible() if locator.count() > 0 else False
            else:
                locator = self.locate(selector)
                return (locator.first.is_visible() 
                       if locator.count() > 0 else False)
        except Exception as e:
            logger.debug(f"检查元素可见性失败: {selector}, 错误: {e}")
            return False

    def is_element_enabled(self, selector: str) -> bool:
        """检查元素是否启用"""
        try:
            # 特殊处理clickable定位器，确保与其他操作行为一致
            if selector.startswith("clickable="):
                # 使用_locate_clickable_element方法获取智能定位的元素
                locator = self._locate_clickable_element(selector[10:])
                return locator.is_enabled() if locator.count() > 0 else False
            else:
                locator = self.locate(selector)
                return (locator.first.is_enabled() 
                       if locator.count() > 0 else False)
        except Exception as e:
            logger.debug(f"检查元素启用状态失败: {selector}, 错误: {e}")
            return False

    def get_element_count(self, selector: str) -> int:
        """获取匹配选择器的元素数量"""
        try:
            locator = self.locate(selector)
            return locator.count()
        except Exception as e:
            logger.debug(f"获取元素数量失败: {selector}, 错误: {e}")
            return 0

    def get_element_text(self, selector: str) -> str:
        """获取元素文本内容"""
        try:
            locator = self.locate(selector)
            if locator.count() == 0:
                return ""
            return locator.first.text_content() or ""
        except Exception as e:
            logger.debug(f"获取元素文本失败: {selector}, 错误: {e}")
            return ""

    def get_element_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """获取元素属性值"""
        try:
            locator = self.locate(selector)
            if locator.count() == 0:
                return None
            return locator.first.get_attribute(attribute)
        except Exception as e:
            logger.debug(f"获取元素属性失败: {selector}.{attribute}, 错误: {e}")
            return None

    def filter_by_text(self, base_selector: str, text: str, exact: bool = False) -> Locator:
        """通过文本过滤元素"""
        base_locator = self.locate(base_selector)
        if exact:
            return base_locator.filter(has_text=re.compile(f"^{re.escape(text)}$"))
        else:
            return base_locator.filter(has_text=text)

    def filter_by_visible(self, base_selector: str) -> Locator:
        """过滤可见元素"""
        base_locator = self.locate(base_selector)
        return base_locator.filter(visible=True)

    def locate_nth(self, selector: str, index: int) -> Locator:
        """定位第N个元素（从0开始）"""
        base_locator = self.locate(selector)
        return base_locator.nth(index)

    def locate_first(self, selector: str) -> Locator:
        """定位第一个元素"""
        return self.locate_nth(selector, 0)

    def locate_last(self, selector: str) -> Locator:
        """定位最后一个元素"""
        base_locator = self.locate(selector)
        return base_locator.last

    def resolve_multiple_matches(self, 
                                 selector: str,
                                 preferred_text: Optional[str] = None,
                                 prefer_visible: bool = True,
                                 index: Optional[int] = None) -> Locator:
        """解决多元素匹配问题
        
        当选择器匹配多个元素时的智能解决策略。
        
        Args:
            selector: 基础选择器
            preferred_text: 首选文本内容
            prefer_visible: 是否优先选择可见元素
            index: 指定索引（优先级最高）
            
        Returns:
            Locator: 解决冲突后的定位器
        """
        base_locator = self.locate(selector)
        
        # 如果只有一个匹配，直接返回
        if base_locator.count() <= 1:
            return base_locator
            
        logger.info(f"发现多个匹配元素({base_locator.count()})，正在解决冲突: {selector}")
        
        # 优先级1: 指定索引
        if index is not None:
            return base_locator.nth(index)
            
        # 优先级2: 按首选文本过滤
        if preferred_text:
            text_filtered = base_locator.filter(has_text=preferred_text)
            if text_filtered.count() == 1:
                return text_filtered
            elif text_filtered.count() > 1:
                base_locator = text_filtered
                
        # 优先级3: 按可见性过滤
        if prefer_visible:
            visible_filtered = base_locator.filter(visible=True)
            if visible_filtered.count() >= 1:
                return visible_filtered.first
                
        # 最后返回第一个元素
        return base_locator.first

    def validate_locator_strategy(self, selector: str) -> Dict[str, Any]:
        """验证定位器策略
        
        分析给定选择器的可靠性和性能特征。
        
        Args:
            selector: 要验证的选择器
            
        Returns:
            Dict: 包含验证结果的字典
        """
        result = {
            "selector": selector,
            "strategy": "unknown",
            "reliability": "unknown",
            "performance": "unknown",
            "recommendations": []
        }
        
        locator_type, _, _ = self._parse_selector(selector)
        result["strategy"] = locator_type
        
        # 可靠性评估
        reliability_scores = {
            "testid": "excellent",
            "role": "good", 
            "label": "good",
            "placeholder": "good",
            "text": "fair",
            "alt": "fair",
            "title": "poor",
            "css": "poor",
            "xpath": "very_poor"
        }
        result["reliability"] = reliability_scores.get(locator_type, "unknown")
        
        # 性能评估
        performance_scores = {
            "testid": "excellent",
            "role": "good",
            "label": "good", 
            "placeholder": "good",
            "text": "good",
            "alt": "good",
            "title": "fair",
            "css": "fair",
            "xpath": "poor"
        }
        result["performance"] = performance_scores.get(locator_type, "unknown")
        
        # 生成建议
        if locator_type in ["xpath", "css"]:
            result["recommendations"].append("考虑使用更稳定的定位策略，如role、label或testid")
            
        if locator_type == "text":
            result["recommendations"].append("考虑使用role或label定位器以提高可靠性")
            
        if result["reliability"] in ["poor", "very_poor"]:
            result["recommendations"].append("当前策略可靠性较低，建议重新设计定位策略")
            
        return result


# 为了向后兼容，提供别名
ElementLocator = ImprovedElementLocator 