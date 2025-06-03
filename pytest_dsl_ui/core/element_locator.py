"""元素定位器

提供多种元素定位策略和智能等待机制。
"""

import asyncio
import logging
from typing import Optional, List
from playwright.async_api import (
    Page, 
    Locator, 
    TimeoutError as PlaywrightTimeoutError
)

logger = logging.getLogger(__name__)


class ElementLocator:
    """元素定位器

    提供统一的元素定位和等待接口。
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
                     - 过滤定位: "role=listitem,filter_text=Product 2"
                     - 组合定位: "role=button,and_title=Subscribe"

        Returns:
            Locator: Playwright定位器对象
        """
        # 根据选择器类型选择合适的定位方法
        if selector.startswith("//") or selector.startswith("(//"):
            # XPath选择器
            return self.page.locator(f"xpath={selector}")
        elif selector.startswith("text="):
            # 文本定位 - 支持精确匹配和正则表达式
            return self._parse_text_locator(selector)
        elif selector.startswith("role="):
            # 角色定位 - 按照Playwright最佳实践优化
            return self._parse_role_locator(selector)
        elif selector.startswith("placeholder="):
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
            # 解析带参数的格式：role=button,name=百度一下,filter_text=Product 2
            parts = role_part.split(",")
            role = parts[0].strip()
            kwargs = {}
            filter_options = {}
            and_locator = None
            or_locator = None

            for part in parts[1:]:
                if "=" in part:
                    key, value = part.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # 处理过滤选项
                    if key == "filter_text":
                        filter_options["has_text"] = value
                    elif key == "filter_not_text":
                        filter_options["has_not_text"] = value
                    elif key == "filter_has":
                        # 这里可以扩展支持子元素过滤
                        pass
                    elif key == "and_title":
                        # 组合定位：同时匹配角色和标题
                        and_locator = self.page.get_by_title(value)
                    elif key == "and_text":
                        # 组合定位：同时匹配角色和文本
                        and_locator = self.page.get_by_text(value)
                    elif key == "or_text":
                        # 或定位：匹配角色或文本
                        or_locator = self.page.get_by_text(value)
                    else:
                        # 转换布尔值
                        if value.lower() in ('true', 'false'):
                            kwargs[key] = value.lower() == 'true'
                        else:
                            kwargs[key] = value

            # 创建基础定位器
            base_locator = self.page.get_by_role(role, **kwargs)

            # 应用过滤
            if filter_options:
                base_locator = base_locator.filter(**filter_options)

            # 应用组合定位
            if and_locator:
                base_locator = base_locator.and_(and_locator)

            if or_locator:
                base_locator = base_locator.or_(or_locator)

            return base_locator
        else:
            # 简单角色定位
            return self.page.get_by_role(role_part)

    def _run_async(self, coro):
        """运行异步协程 - 简化版本"""
        try:
            # 尝试获取当前事件循环
            asyncio.get_running_loop()
            # 如果循环正在运行，创建新线程
            import concurrent.futures
            
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                try:
                    return new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                return future.result()
        except RuntimeError:
            # 没有运行中的事件循环，直接运行
            return asyncio.run(coro)

    async def _wait_for_element_async(self, selector: str, state: str = "visible", timeout: Optional[float] = None) -> bool:
        """异步等待元素状态 - 利用 Playwright 智能等待"""
        locator = self.locate(selector)
        timeout_ms = int((timeout * 1000) if timeout else self.default_timeout)

        try:
            await locator.wait_for(state=state, timeout=timeout_ms)
            return True
        except PlaywrightTimeoutError:
            return False

    def wait_for_element(self, selector: str, state: str = "visible", timeout: Optional[float] = None) -> bool:
        """等待元素达到指定状态

        Args:
            selector: 元素选择器
            state: 等待状态 (visible, hidden, attached, detached)
            timeout: 超时时间（秒），如果为None则使用默认超时

        Returns:
            bool: 是否在超时时间内达到指定状态
        """
        return self._run_async(self._wait_for_element_async(selector, state, timeout))

    def wait_for_text(self, text: str, timeout: Optional[float] = None) -> bool:
        """等待文本在页面中出现 - 利用 Playwright 智能等待

        Args:
            text: 要等待的文本
            timeout: 超时时间（秒），如果为None则使用默认超时

        Returns:
            bool: 是否在超时时间内找到文本
        """
        async def _wait_for_text_async():
            timeout_ms = int((timeout * 1000) if timeout else self.default_timeout)
            try:
                locator = self.page.get_by_text(text)
                await locator.wait_for(state="visible", timeout=timeout_ms)
                return True
            except PlaywrightTimeoutError:
                return False
        
        return self._run_async(_wait_for_text_async())

    def is_element_visible(self, selector: str) -> bool:
        """检查元素是否可见 - 利用 Playwright 智能等待检查

        Args:
            selector: 元素选择器

        Returns:
            bool: 元素是否可见
        """
        try:
            locator = self.locate(selector)
            # 先等待元素存在，然后检查可见性
            return self._run_async(locator.is_visible())
        except Exception:
            return False

    def is_element_enabled(self, selector: str) -> bool:
        """检查元素是否启用

        Args:
            selector: 元素选择器

        Returns:
            bool: 元素是否启用
        """
        try:
            locator = self.locate(selector)
            return self._run_async(locator.is_enabled())
        except Exception:
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
            return self._run_async(locator.is_checked())
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
            return self._run_async(locator.count())
        except Exception:
            return 0

    def get_element_text(self, selector: str) -> str:
        """获取元素文本内容 - 利用 Playwright 智能等待

        Args:
            selector: 元素选择器

        Returns:
            str: 元素文本内容
        """
        async def _get_text_async():
            locator = self.locate(selector)
            # 等待元素可见后获取文本
            await locator.wait_for(state="visible", timeout=self.default_timeout)
            return await locator.text_content() or ""
        
        return self._run_async(_get_text_async())

    def get_element_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """获取元素属性值 - 利用 Playwright 智能等待

        Args:
            selector: 元素选择器
            attribute: 属性名

        Returns:
            Optional[str]: 属性值，如果属性不存在则返回None
        """
        async def _get_attribute_async():
            locator = self.locate(selector)
            # 等待元素存在后获取属性
            await locator.wait_for(state="attached", timeout=self.default_timeout)
            return await locator.get_attribute(attribute)
        
        return self._run_async(_get_attribute_async())

    def get_element_value(self, selector: str) -> str:
        """获取输入元素的值 - 利用 Playwright 智能等待

        Args:
            selector: 元素选择器

        Returns:
            str: 输入元素的值
        """
        async def _get_value_async():
            locator = self.locate(selector)
            # 等待元素可见后获取值
            await locator.wait_for(state="visible", timeout=self.default_timeout)
            return await locator.input_value()
        
        return self._run_async(_get_value_async())

    def get_all_elements_text(self, selector: str) -> List[str]:
        """获取所有匹配元素的文本内容

        Args:
            selector: 元素选择器

        Returns:
            List[str]: 所有匹配元素的文本内容列表
        """
        async def _get_all_text():
            locator = self.locate(selector)
            # 等待至少一个元素出现
            await locator.first.wait_for(state="visible", timeout=self.default_timeout)
            elements = await locator.all()
            texts = []
            for element in elements:
                text = await element.text_content()
                texts.append(text or "")
            return texts

        return self._run_async(_get_all_text())

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
