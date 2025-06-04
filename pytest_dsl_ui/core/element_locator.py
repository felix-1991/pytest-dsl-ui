"""元素定位器

提供多种元素定位策略，充分利用Playwright的智能等待机制。
"""

import logging
from typing import Optional, List
from playwright.sync_api import (
    Page,
    Locator,
    TimeoutError as PlaywrightTimeoutError
)

logger = logging.getLogger(__name__)


class ElementLocator:
    """元素定位器

    提供统一的元素定位接口，充分利用Playwright的智能等待。
    """

    def __init__(self, page: Page):
        """初始化元素定位器

        Args:
            page: Playwright页面实例
        """
        self.page = page
        self.default_timeout = 30000  # 默认超时30秒

    def set_default_timeout(self, timeout: float):
        """设置默认超时时间

        Args:
            timeout: 超时时间（秒）
        """
        self.default_timeout = int(timeout * 1000)  # 转换为毫秒
        logger.info(f"设置默认超时时间: {timeout}秒")

    def locate(self, selector: str) -> Locator:
        """定位元素

        Args:
            selector: 元素选择器，支持多种格式：
                     - CSS选择器: "button.submit"
                     - XPath: "//button[@type='submit']"
                     - 文本定位: "text=提交" 或 "text=提交,exact=true"
                     - 角色定位: "role=button" 或 "role=button:提交"
                     - 标签定位: "label=用户名"
                     - 占位符定位: "placeholder=请输入用户名"
                     - 测试ID定位: "testid=submit-btn"
                     - 标题定位: "title=关闭"
                     - Alt文本定位: "alt=logo"
                     - 智能点击定位: "clickable=日志检索"
                     - 元素类型定位: "span=日志检索" 或 "div=日志检索"
                     - CSS类定位: "class=highlight-item-container:日志检索"
                     - 复合定位器: "role=cell:外到内&locator=label&first=true"

        Returns:
            Locator: Playwright定位器对象
        """
        # 检查是否是复合定位器（包含&符号）
        if "&" in selector and not selector.startswith(("http", "ftp")):
            return self._parse_compound_locator(selector)
        
        # 根据选择器类型选择合适的定位方法
        if selector.startswith("//") or selector.startswith("(//"):
            # XPath选择器
            return self.page.locator(f"xpath={selector}")
        elif selector.startswith("text="):
            # 文本定位
            return self._parse_text_locator(selector)
        elif selector.startswith("role="):
            # 角色定位
            return self._parse_role_locator(selector)
        elif selector.startswith("clickable="):
            # 智能可点击元素定位
            text = selector[10:]  # 移除"clickable="前缀
            return self.locate_clickable_element(text)
        elif selector.startswith("class="):
            # CSS类和文本组合定位 class=类名:文本
            class_part = selector[6:]  # 移除"class="前缀
            if ":" in class_part:
                css_class, text = class_part.split(":", 1)
                return self.locate_by_css_class(
                    text.strip(), css_class.strip())
            else:
                # 只有类名，没有文本
                return self.page.locator(f".{class_part}")
        elif "=" in selector and not selector.startswith(("http", "/")):
            # 检查是否是元素类型定位 (span=, div=, button=等)
            element_type, text = selector.split("=", 1)
            allowed_types = [
                "span", "div", "button", "a", "input", 
                "p", "h1", "h2", "h3", "h4", "h5", "h6"
            ]
            if element_type in allowed_types:
                return self.locate_by_element_type(text, element_type)
        
        # 处理其他标准定位器
        if selector.startswith("placeholder="):
            # 占位符定位
            placeholder = selector[12:]  # 移除"placeholder="前缀
            return self.page.get_by_placeholder(placeholder)
        elif selector.startswith("label="):
            # 标签定位
            label = selector[6:]  # 移除"label="前缀
            return self.page.get_by_label(label)
        elif selector.startswith("title="):
            # 标题定位
            title = selector[6:]  # 移除"title="前缀
            return self.page.get_by_title(title)
        elif selector.startswith("alt="):
            # Alt文本定位
            alt = selector[4:]  # 移除"alt="前缀
            return self.page.get_by_alt_text(alt)
        elif selector.startswith("testid="):
            # 测试ID定位
            testid = selector[7:]  # 移除"testid="前缀
            return self.page.get_by_test_id(testid)
        else:
            # 默认使用CSS选择器
            return self.page.locator(selector)

    def _parse_text_locator(self, selector: str) -> Locator:
        """解析文本定位器，支持精确匹配等选项"""
        text_part = selector[5:]  # 移除"text="前缀

        if "," in text_part:
            # 解析带参数的格式：text=Welcome,exact=true
            parts = text_part.split(",")
            text = parts[0].strip()
            kwargs = {}

            for part in parts[1:]:
                if "=" in part:
                    key, value = part.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # 转换布尔值
                    if value.lower() in ('true', 'false'):
                        kwargs[key] = value.lower() == 'true'
                    else:
                        kwargs[key] = value

            return self.page.get_by_text(text, **kwargs)
        else:
            return self.page.get_by_text(text_part)

    def _parse_role_locator(self, selector: str) -> Locator:
        """解析角色定位器，支持过滤、组合等高级功能"""
        role_part = selector[5:]  # 移除"role="前缀

        # 支持冒号分隔的简化格式：role=button:百度一下
        if ":" in role_part and "," not in role_part:
            role, name = role_part.split(":", 1)
            return self.page.get_by_role(role.strip(), name=name.strip())
        elif "," in role_part:
            # 解析带参数的格式：role=button,name=百度一下
            parts = role_part.split(",")
            role = parts[0].strip()
            kwargs = {}

            for part in parts[1:]:
                if "=" in part:
                    key, value = part.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # 转换布尔值
                    if value.lower() in ('true', 'false'):
                        kwargs[key] = value.lower() == 'true'
                    else:
                        kwargs[key] = value

            return self.page.get_by_role(role, **kwargs)
        else:
            # 简单角色定位
            return self.page.get_by_role(role_part)

    def _parse_compound_locator(self, selector: str) -> Locator:
        """解析复合定位器
        
        格式示例: "role=cell:外到内&locator=label&first=true"
        
        Args:
            selector: 复合定位器字符串
            
        Returns:
            Locator: 解析后的定位器
        """
        # 分解基础定位器和修饰符
        parts = selector.split("&")
        base_part = parts[0]
        modifiers = parts[1:] if len(parts) > 1 else []
        
        # 解析基础定位器
        base_locator = self.locate(base_part)
        
        # 应用修饰符
        current_locator = base_locator
        
        for modifier in modifiers:
            if "=" not in modifier:
                continue
                
            key, value = modifier.split("=", 1)
            key = key.strip()
            value = value.strip()
            
            if key == "locator":
                # 子定位器
                current_locator = current_locator.locator(value)
            elif key == "has_text":
                # 文本过滤
                current_locator = current_locator.filter(has_text=value)
            elif key == "has_not_text":
                # 排除文本过滤
                current_locator = current_locator.filter(has_not_text=value)
            elif key == "first" and value.lower() == "true":
                # 第一个元素
                current_locator = current_locator.first
            elif key == "last" and value.lower() == "true":
                # 最后一个元素
                current_locator = current_locator.last
            elif key == "nth":
                # 第N个元素
                try:
                    index = int(value)
                    current_locator = current_locator.nth(index)
                except ValueError:
                    logger.warning(f"无效的nth索引: {value}")
            elif key == "visible" and value.lower() == "true":
                # 只选择可见元素
                current_locator = current_locator.filter(visible=True)
            elif key == "exact":
                # exact参数已在基础定位器中处理
                pass
            else:
                logger.warning(f"未知的修饰符: {key}={value}")
        
        return current_locator

    def wait_for_element(self, selector: str, state: str = "visible", 
                         timeout: Optional[float] = None) -> bool:
        """等待元素达到指定状态

        Args:
            selector: 元素选择器
            state: 等待状态 (visible, hidden, attached, detached)
            timeout: 超时时间（秒），如果为None则使用默认超时

        Returns:
            bool: 是否在超时时间内达到指定状态
        """
        timeout_ms = int((timeout * 1000) if timeout else self.default_timeout)

        try:
            # 特殊处理clickable定位器，确保与locate_clickable_element行为完全一致
            if selector.startswith("clickable="):
                text = selector[10:]  # 移除"clickable="前缀
                
                # 直接使用locate_clickable_element方法获取定位器
                # 这样确保逻辑完全一致
                clickable_locator = self.locate_clickable_element(text)
                
                # 检查定位器是否找到了元素
                if clickable_locator.count() > 0:
                    clickable_locator.wait_for(state=state, timeout=timeout_ms)
                    return True
                else:
                    # 如果没找到元素，返回False
                    logger.debug(f"clickable定位器未找到元素: {text}")
                    return False
            else:
                # 对于其他类型的定位器，使用标准等待逻辑
                locator = self.locate(selector)
                locator.wait_for(state=state, timeout=timeout_ms)
                return True
                
        except PlaywrightTimeoutError:
            logger.debug(f"等待元素超时: {selector}, 状态: {state}, 超时: {timeout_ms}ms")
            return False
        except Exception as e:
            # 记录其他异常信息，但仍然返回False而不是抛出异常
            logger.warning(f"等待元素时发生异常: {selector}, 错误: {str(e)}")
            return False

    def wait_for_text(self, text: str, 
                      timeout: Optional[float] = None) -> bool:
        """等待文本在页面中出现

        Args:
            text: 要等待的文本
            timeout: 超时时间（秒），如果为None则使用默认超时

        Returns:
            bool: 是否在超时时间内找到文本
        """
        timeout_ms = int((timeout * 1000) if timeout else self.default_timeout)
        try:
            locator = self.page.get_by_text(text)
            locator.wait_for(state="visible", timeout=timeout_ms)
            return True
        except PlaywrightTimeoutError:
            return False

    def is_element_visible(self, selector: str) -> bool:
        """检查元素是否可见

        Args:
            selector: 元素选择器

        Returns:
            bool: 元素是否可见
        """
        try:
            # 特殊处理clickable定位器，确保与locate_clickable_element行为一致
            if selector.startswith("clickable="):
                text = selector[10:]  # 移除"clickable="前缀
                clickable_locator = self.locate_clickable_element(text)
                return (clickable_locator.count() > 0 and 
                       clickable_locator.first.is_visible() if clickable_locator.count() > 0 else False)
            else:
                locator = self.locate(selector)
                return locator.is_visible()
        except Exception as e:
            logger.debug(f"检查元素可见性失败: {selector}, 错误: {e}")
            return False

    def is_element_enabled(self, selector: str) -> bool:
        """检查元素是否启用

        Args:
            selector: 元素选择器

        Returns:
            bool: 元素是否启用
        """
        try:
            # 特殊处理clickable定位器，确保与locate_clickable_element行为一致
            if selector.startswith("clickable="):
                text = selector[10:]  # 移除"clickable="前缀
                clickable_locator = self.locate_clickable_element(text)
                return (clickable_locator.count() > 0 and 
                       clickable_locator.first.is_enabled() if clickable_locator.count() > 0 else False)
            else:
                locator = self.locate(selector)
                return locator.is_enabled()
        except Exception as e:
            logger.debug(f"检查元素启用状态失败: {selector}, 错误: {e}")
            return False

    def is_element_checked(self, selector: str) -> bool:
        """检查元素是否被选中（适用于复选框和单选按钮）

        Args:
            selector: 元素选择器

        Returns:
            bool: 元素是否被选中
        """
        try:
            locator = self.locate(selector)
            return locator.is_checked()
        except Exception:
            return False

    def get_element_count(self, selector: str) -> int:
        """获取匹配选择器的元素数量

        Args:
            selector: 元素选择器

        Returns:
            int: 元素数量
        """
        try:
            locator = self.locate(selector)
            return locator.count()
        except Exception:
            return 0

    def get_element_text(self, selector: str) -> str:
        """获取元素文本内容

        Args:
            selector: 元素选择器

        Returns:
            str: 元素文本内容
        """
        try:
            locator = self.locate(selector)
            # 先检查元素是否存在，避免超时
            if locator.count() == 0:
                return ""
            return locator.text_content() or ""
        except Exception:
            return ""

    def get_element_attribute(self, selector: str, 
                              attribute: str) -> Optional[str]:
        """获取元素属性值

        Args:
            selector: 元素选择器
            attribute: 属性名

        Returns:
            Optional[str]: 属性值，如果属性不存在则返回None
        """
        locator = self.locate(selector)
        return locator.get_attribute(attribute)

    def get_element_value(self, selector: str) -> str:
        """获取输入元素的值

        Args:
            selector: 元素选择器

        Returns:
            str: 输入元素的值
        """
        locator = self.locate(selector)
        return locator.input_value()

    def get_all_elements_text(self, selector: str) -> List[str]:
        """获取所有匹配元素的文本内容

        Args:
            selector: 元素选择器

        Returns:
            List[str]: 所有匹配元素的文本内容列表
        """
        locator = self.locate(selector)
        elements = locator.all()
        texts = []
        for element in elements:
            text = element.text_content()
            texts.append(text or "")
        return texts

    def locate_by_visible(self, selector: str) -> Locator:
        """定位可见元素（过滤掉不可见的元素）

        Args:
            selector: 基础选择器

        Returns:
            Locator: 过滤后只包含可见元素的定位器
        """
        base_locator = self.locate(selector)
        return base_locator.filter(visible=True)

    def locate_first(self, selector: str) -> Locator:
        """定位第一个匹配的元素

        Args:
            selector: 元素选择器

        Returns:
            Locator: 第一个匹配元素的定位器
        """
        base_locator = self.locate(selector)
        return base_locator.first

    def locate_last(self, selector: str) -> Locator:
        """定位最后一个匹配的元素

        Args:
            selector: 元素选择器

        Returns:
            Locator: 最后一个匹配元素的定位器
        """
        base_locator = self.locate(selector)
        return base_locator.last

    def locate_nth(self, selector: str, index: int) -> Locator:
        """定位第N个匹配的元素

        Args:
            selector: 元素选择器
            index: 元素索引（从0开始）

        Returns:
            Locator: 第N个匹配元素的定位器
        """
        base_locator = self.locate(selector)
        return base_locator.nth(index)

    def locate_with_filter(self, selector: str, has_text: Optional[str] = None,
                           has_not_text: Optional[str] = None,
                           has: Optional[str] = None,
                           has_not: Optional[str] = None) -> Locator:
        """使用过滤条件定位元素

        Args:
            selector: 基础选择器
            has_text: 必须包含的文本
            has_not_text: 不能包含的文本
            has: 必须包含的子元素选择器
            has_not: 不能包含的子元素选择器

        Returns:
            Locator: 过滤后的定位器
        """
        base_locator = self.locate(selector)
        filter_kwargs = {}

        if has_text:
            filter_kwargs["has_text"] = has_text
        if has_not_text:
            filter_kwargs["has_not_text"] = has_not_text
        if has:
            filter_kwargs["has"] = self.locate(has)
        if has_not:
            filter_kwargs["has_not"] = self.locate(has_not)

        return base_locator.filter(**filter_kwargs)

    def locate_and(self, selector1: str, selector2: str) -> Locator:
        """组合定位：同时匹配两个条件

        Args:
            selector1: 第一个选择器
            selector2: 第二个选择器

        Returns:
            Locator: 组合后的定位器
        """
        locator1 = self.locate(selector1)
        locator2 = self.locate(selector2)
        return locator1.and_(locator2)

    def locate_or(self, selector1: str, selector2: str) -> Locator:
        """或定位：匹配任一条件

        Args:
            selector1: 第一个选择器
            selector2: 第二个选择器

        Returns:
            Locator: 或定位器
        """
        locator1 = self.locate(selector1)
        locator2 = self.locate(selector2)
        return locator1.or_(locator2)

    def locate_unique_by_text(self, base_selector: str, 
                              text: str, exact: bool = True) -> Locator:
        """通过文本内容从多个匹配元素中选择唯一元素
        
        当基础选择器匹配多个元素时，通过文本内容进一步过滤。
        适用于解决严格模式冲突问题。

        Args:
            base_selector: 基础选择器（如 "title=日志检索"）
            text: 用于过滤的精确文本内容
            exact: 是否精确匹配文本

        Returns:
            Locator: 过滤后的唯一定位器
        """
        base_locator = self.locate(base_selector)
        if exact:
            return base_locator.filter(has_text=f"^{text}$")
        else:
            return base_locator.filter(has_text=text)

    def locate_by_text_content_only(self, text: str, 
                                    exact: bool = True) -> Locator:
        """仅通过文本内容定位元素，避免title属性冲突
        
        Args:
            text: 要匹配的文本内容
            exact: 是否精确匹配

        Returns:
            Locator: 文本定位器
        """
        if exact:
            return self.page.get_by_text(text, exact=True)
        else:
            return self.page.get_by_text(text)

    def resolve_strict_mode_conflict(self, selector: str, 
                                     preferred_text: Optional[str] = None,
                                     prefer_visible: bool = True,
                                     index: Optional[int] = None) -> Locator:
        """解决严格模式冲突
        
        当选择器匹配多个元素时，提供多种策略来选择唯一元素。

        Args:
            selector: 原始选择器
            preferred_text: 首选的文本内容（用于过滤）
            prefer_visible: 是否优先选择可见元素
            index: 如果指定，直接选择第N个元素

        Returns:
            Locator: 解决冲突后的定位器
        """
        base_locator = self.locate(selector)
        
        # 如果指定了索引，直接返回第N个元素
        if index is not None:
            return base_locator.nth(index)
        
        # 如果指定了首选文本，先按文本过滤
        if preferred_text:
            filtered_locator = base_locator.filter(has_text=preferred_text)
            # 检查过滤后是否还有多个元素
            if filtered_locator.count() == 1:
                return filtered_locator
            elif filtered_locator.count() > 1 and prefer_visible:
                return filtered_locator.filter(visible=True).first
            elif filtered_locator.count() > 1:
                return filtered_locator.first
        
        # 如果没有指定文本或过滤后仍有多个，按可见性过滤
        if prefer_visible:
            visible_locator = base_locator.filter(visible=True)
            if visible_locator.count() >= 1:
                return visible_locator.first
        
        # 最后选择第一个元素
        return base_locator.first

    def locate_clickable_element(self, text: str, 
                                 prefer_interactive: bool = True) -> Locator:
        """智能定位可点击元素
        
        当多个元素包含相同文本时，智能选择最合适的可点击元素。
        优先级：可见且启用的交互元素 > 可见的交互元素 > 其他元素
        
        Args:
            text: 要匹配的文本
            prefer_interactive: 是否优先选择交互性元素
            
        Returns:
            Locator: 最适合点击的元素定位器
        """
        logger.debug(f"智能定位可点击元素: '{text}'")
        
        # 首先尝试常见的可点击元素
        clickable_selectors = [
            f"button:has-text('{text}')",
            f"a:has-text('{text}')", 
            f"[role='button']:has-text('{text}')",
            f"[role='link']:has-text('{text}')",
            f"[role='menuitem']:has-text('{text}')"
        ]
        
        # 首先寻找可见且启用的元素
        for selector in clickable_selectors:
            locator = self.page.locator(selector)
            count = locator.count()
            if count > 0:
                logger.debug(f"检查选择器: {selector} (数量: {count})")
                
                # 优先选择可见且启用的元素
                for i in range(count):
                    element = locator.nth(i)
                    try:
                        is_visible = element.is_visible()
                        is_enabled = element.is_enabled()
                        logger.debug(f"  元素 {i}: 可见={is_visible}, 启用={is_enabled}")
                        
                        if is_visible and is_enabled:
                            logger.debug(f"选择可见且启用的元素: {selector} (索引: {i})")
                            return element
                    except Exception as e:
                        logger.debug(f"  检查元素 {i} 状态失败: {e}")
                        continue
        
        # 如果没找到可见且启用的交互元素，再次查找仅可见的交互元素
        for selector in clickable_selectors:
            locator = self.page.locator(selector)
            count = locator.count()
            if count > 0:
                for i in range(count):
                    element = locator.nth(i)
                    try:
                        is_visible = element.is_visible()
                        if is_visible:
                            logger.debug(f"选择可见元素: {selector} (索引: {i})")
                            return element
                    except Exception as e:
                        logger.debug(f"  检查元素 {i} 可见性失败: {e}")
                        continue
        
        # 如果没找到明确的可点击元素，尝试span和div
        text_locator = self.page.get_by_text(text, exact=True)
        count = text_locator.count()
        logger.debug(f"精确文本匹配: '{text}' (数量: {count})")
        
        if count == 1:
            return text_locator
        elif count > 1:
            # 优先选择可见且启用的span元素
            span_locator = self.page.locator(f"span:has-text('{text}')")
            span_count = span_locator.count()
            if span_count > 0:
                logger.debug(f"检查span元素: span:has-text('{text}') (数量: {span_count})")
                
                # 寻找可见且启用的span
                for i in range(span_count):
                    element = span_locator.nth(i)
                    try:
                        is_visible = element.is_visible()
                        is_enabled = element.is_enabled()
                        if is_visible and is_enabled:
                            logger.debug(f"选择可见且启用的span元素 (索引: {i})")
                            return element
                    except Exception:
                        continue
                
                # 如果没有可见且启用的，选择第一个可见的
                for i in range(span_count):
                    element = span_locator.nth(i)
                    try:
                        is_visible = element.is_visible()
                        if is_visible:
                            logger.debug(f"选择可见的span元素 (索引: {i})")
                            return element
                    except Exception:
                        continue
                
                # 最后选择第一个
                logger.debug("选择第一个span元素")
                return span_locator.first
            
            # 然后选择div元素（类似的逻辑）
            div_locator = self.page.locator(f"div:has-text('{text}')")
            div_count = div_locator.count()
            if div_count > 0:
                logger.debug(f"检查div元素: div:has-text('{text}') (数量: {div_count})")
                
                # 寻找可见且启用的div
                for i in range(div_count):
                    element = div_locator.nth(i)
                    try:
                        is_visible = element.is_visible()
                        is_enabled = element.is_enabled()
                        if is_visible and is_enabled:
                            logger.debug(f"选择可见且启用的div元素 (索引: {i})")
                            return element
                    except Exception:
                        continue
                
                # 如果没有可见且启用的，选择第一个可见的
                for i in range(div_count):
                    element = div_locator.nth(i)
                    try:
                        is_visible = element.is_visible()
                        if is_visible:
                            logger.debug(f"选择可见的div元素 (索引: {i})")
                            return element
                    except Exception:
                        continue
                
                # 最后选择第一个
                logger.debug("选择第一个div元素")
                return div_locator.first
            
            # 最后在所有文本匹配中选择可见且启用的元素
            for i in range(count):
                element = text_locator.nth(i)
                try:
                    is_visible = element.is_visible()
                    is_enabled = element.is_enabled()
                    if is_visible and is_enabled:
                        logger.debug(f"选择可见且启用的文本匹配元素 (索引: {i})")
                        return element
                except Exception:
                    continue
            
            # 选择第一个可见的
            for i in range(count):
                element = text_locator.nth(i)
                try:
                    is_visible = element.is_visible()
                    if is_visible:
                        logger.debug(f"选择可见的文本匹配元素 (索引: {i})")
                        return element
                except Exception:
                    continue
            
            # 最后返回第一个匹配的元素
            logger.debug("使用第一个文本匹配元素")
            return text_locator.first
        else:
            # 如果精确匹配失败，尝试模糊匹配
            fuzzy_locator = self.page.get_by_text(text)
            fuzzy_count = fuzzy_locator.count()
            logger.debug(f"模糊文本匹配: '{text}' (数量: {fuzzy_count})")
            if fuzzy_count > 0:
                # 同样优先选择可见且启用的元素
                for i in range(fuzzy_count):
                    element = fuzzy_locator.nth(i)
                    try:
                        is_visible = element.is_visible()
                        is_enabled = element.is_enabled()
                        if is_visible and is_enabled:
                            logger.debug(f"选择可见且启用的模糊匹配元素 (索引: {i})")
                            return element
                    except Exception:
                        continue
                
                return fuzzy_locator.first
            else:
                logger.warning(f"无法找到包含文本 '{text}' 的任何元素")
                return fuzzy_locator  # 返回空定位器

    def locate_by_element_type(self, text: str, 
                               element_type: str = "span") -> Locator:
        """根据元素类型和文本定位
        
        Args:
            text: 文本内容
            element_type: 元素类型 (span, div, button, a等)
            
        Returns:
            Locator: 指定类型的元素定位器
        """
        return self.page.locator(f"{element_type}:has-text('{text}')").first

    def locate_by_css_class(self, text: str, 
                            css_class: str) -> Locator:
        """根据CSS类名和文本定位
        
        Args:
            text: 文本内容  
            css_class: CSS类名
            
        Returns:
            Locator: 包含指定类名和文本的元素定位器
        """
        return self.page.locator(f".{css_class}:has-text('{text}')").first
