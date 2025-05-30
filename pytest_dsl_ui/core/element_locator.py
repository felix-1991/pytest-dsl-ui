"""元素定位器

提供多种元素定位策略和智能等待机制。
"""

import asyncio
import logging
from typing import Optional, Union, List, Dict, Any
from playwright.async_api import Page, Locator, TimeoutError as PlaywrightTimeoutError

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
                     - 文本定位: "text=提交"
                     - 角色定位: "role=button" 或 "role=button,name=提交"
                     - 标签定位: "label=用户名"
                     - 占位符定位: "placeholder=请输入用户名"
                     - 测试ID定位: "testid=submit-btn"
                     - 标题定位: "title=关闭"
                     - Alt文本定位: "alt=logo"

        Returns:
            Locator: Playwright定位器对象
        """
        # 根据选择器类型选择合适的定位方法
        if selector.startswith("//") or selector.startswith("(//"):
            # XPath选择器
            return self.page.locator(f"xpath={selector}")
        elif selector.startswith("text="):
            # 文本定位 - 支持精确匹配和正则表达式
            text = selector[5:]  # 移除"text="前缀
            return self.page.get_by_text(text)
        elif selector.startswith("role="):
            # 角色定位 - 按照Playwright最佳实践优化
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
                        kwargs[key.strip()] = value.strip()

                return self.page.get_by_role(role, **kwargs)
            else:
                # 简单角色定位
                return self.page.get_by_role(role_part)
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

    def _run_async(self, coro):
        """运行异步协程 - 优化的事件循环管理"""
        try:
            # 首先尝试获取当前事件循环
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果循环正在运行，使用线程池执行
                import concurrent.futures
                import threading

                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(coro)
                    finally:
                        new_loop.close()

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # 创建新的事件循环
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()

    async def _wait_for_element_async(self, selector: str, state: str = "visible", timeout: Optional[float] = None) -> bool:
        """异步等待元素状态"""
        locator = self.locate(selector)
        timeout_ms = int((timeout * 1000) if timeout else self.default_timeout)

        try:
            if state == "visible":
                await locator.wait_for(state="visible", timeout=timeout_ms)
            elif state == "hidden":
                await locator.wait_for(state="hidden", timeout=timeout_ms)
            elif state == "attached":
                await locator.wait_for(state="attached", timeout=timeout_ms)
            elif state == "detached":
                await locator.wait_for(state="detached", timeout=timeout_ms)
            else:
                raise ValueError(f"不支持的等待状态: {state}")
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

    async def _wait_for_text_async(self, text: str, timeout: Optional[float] = None) -> bool:
        """异步等待文本出现"""
        timeout_ms = int((timeout * 1000) if timeout else self.default_timeout)

        try:
            locator = self.page.get_by_text(text)
            await locator.wait_for(state="visible", timeout=timeout_ms)
            return True
        except PlaywrightTimeoutError:
            return False

    def wait_for_text(self, text: str, timeout: Optional[float] = None) -> bool:
        """等待文本在页面中出现

        Args:
            text: 要等待的文本
            timeout: 超时时间（秒），如果为None则使用默认超时

        Returns:
            bool: 是否在超时时间内找到文本
        """
        return self._run_async(self._wait_for_text_async(text, timeout))

    def is_element_visible(self, selector: str) -> bool:
        """检查元素是否可见

        Args:
            selector: 元素选择器

        Returns:
            bool: 元素是否可见
        """
        try:
            locator = self.locate(selector)
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

    async def _get_element_text_async(self, selector: str) -> str:
        """异步获取元素文本"""
        locator = self.locate(selector)
        return await locator.text_content() or ""

    def get_element_text(self, selector: str) -> str:
        """获取元素文本内容

        Args:
            selector: 元素选择器

        Returns:
            str: 元素文本内容
        """
        return self._run_async(self._get_element_text_async(selector))

    async def _get_element_attribute_async(self, selector: str, attribute: str) -> Optional[str]:
        """异步获取元素属性"""
        locator = self.locate(selector)
        return await locator.get_attribute(attribute)

    def get_element_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """获取元素属性值

        Args:
            selector: 元素选择器
            attribute: 属性名

        Returns:
            Optional[str]: 属性值，如果属性不存在则返回None
        """
        return self._run_async(self._get_element_attribute_async(selector, attribute))

    async def _get_element_value_async(self, selector: str) -> str:
        """异步获取输入元素的值"""
        locator = self.locate(selector)
        return await locator.input_value()

    def get_element_value(self, selector: str) -> str:
        """获取输入元素的值

        Args:
            selector: 元素选择器

        Returns:
            str: 输入元素的值
        """
        return self._run_async(self._get_element_value_async(selector))

    def get_all_elements_text(self, selector: str) -> List[str]:
        """获取所有匹配元素的文本内容

        Args:
            selector: 元素选择器

        Returns:
            List[str]: 所有匹配元素的文本内容列表
        """
        async def _get_all_text():
            locator = self.locate(selector)
            elements = await locator.all()
            texts = []
            for element in elements:
                text = await element.text_content()
                texts.append(text or "")
            return texts

        return self._run_async(_get_all_text())
