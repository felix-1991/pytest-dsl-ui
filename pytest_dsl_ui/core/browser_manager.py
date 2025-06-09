"""浏览器管理器

负责管理Playwright浏览器实例的生命周期，包括启动、关闭和配置。
支持多浏览器、多页面的管理。
"""

import logging
from typing import Dict, Optional
from playwright.sync_api import (
    sync_playwright, Browser, BrowserContext, Page, Playwright
)

logger = logging.getLogger(__name__)


class BrowserManager:
    """浏览器管理器

    管理Playwright浏览器实例，支持多浏览器类型和多页面。
    """

    def __init__(self):
        """初始化浏览器管理器"""
        self.playwright: Optional[Playwright] = None
        self.browsers: Dict[str, Browser] = {}
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}
        self.current_browser: Optional[str] = None
        self.current_context: Optional[str] = None
        self.current_page: Optional[str] = None

    def _ensure_playwright(self):
        """确保Playwright实例已启动"""
        if self.playwright is None:
            self.playwright = sync_playwright().start()

    def launch_browser(self, browser_type: str = "chromium", **config) -> str:
        """启动浏览器

        Args:
            browser_type: 浏览器类型 (chromium, firefox, webkit)
            **config: 浏览器启动配置

        Returns:
            str: 浏览器ID
        """
        self._ensure_playwright()

        # 获取浏览器类型
        if browser_type.lower() == "chromium":
            browser_launcher = self.playwright.chromium
        elif browser_type.lower() == "firefox":
            browser_launcher = self.playwright.firefox
        elif browser_type.lower() == "webkit":
            browser_launcher = self.playwright.webkit
        else:
            raise ValueError(f"不支持的浏览器类型: {browser_type}")

        # 处理配置参数
        launch_config = {
            "headless": config.get("headless", True),
            "slow_mo": config.get("slow_mo", 0),
        }

        # 添加启动参数
        if "args" in config:
            launch_config["args"] = config["args"]

        # 添加可执行文件路径
        if "executable_path" in config:
            launch_config["executable_path"] = config["executable_path"]

        # 启动浏览器
        browser = browser_launcher.launch(**launch_config)

        # 生成浏览器ID
        browser_id = f"{browser_type}_{len(self.browsers)}"
        self.browsers[browser_id] = browser
        self.current_browser = browser_id

        logger.info(f"已启动浏览器: {browser_id}")
        return browser_id

    def create_context(self, browser_id: Optional[str] = None, **config) -> str:
        """创建浏览器上下文

        Args:
            browser_id: 浏览器ID，如果为None则使用当前浏览器
            **config: 上下文配置，支持storage_state参数加载认证状态

        Returns:
            str: 上下文ID
        """
        if browser_id is None:
            browser_id = self.current_browser

        if browser_id is None:
            raise ValueError("没有可用的浏览器实例")

        if browser_id not in self.browsers:
            raise ValueError(f"浏览器 {browser_id} 不存在")

        browser = self.browsers[browser_id]

        # 处理配置参数
        context_config = {}

        # 视口配置
        if "viewport" in config:
            context_config["viewport"] = config["viewport"]
        elif "width" in config and "height" in config:
            context_config["viewport"] = {
                "width": config["width"],
                "height": config["height"]
            }

        # 用户代理
        if "user_agent" in config:
            context_config["user_agent"] = config["user_agent"]

        # 地理位置
        if "geolocation" in config:
            context_config["geolocation"] = config["geolocation"]

        # 权限
        if "permissions" in config:
            context_config["permissions"] = config["permissions"]

        # SSL证书忽略配置
        ignore_https_errors = config.get("ignore_https_errors", False)
        if ignore_https_errors:
            context_config["ignore_https_errors"] = True

        # 认证状态配置
        if "storage_state" in config:
            context_config["storage_state"] = config["storage_state"]
            logger.info("将使用认证状态创建浏览器上下文")

        context = browser.new_context(**context_config)

        # 生成上下文ID
        context_id = f"{browser_id}_ctx_{len(self.contexts)}"
        self.contexts[context_id] = context
        self.current_context = context_id

        # 标记上下文是否支持HTTPS证书错误忽略
        if context_config.get('ignore_https_errors', False):
            setattr(context, '_ignore_https_errors', True)

        logger.info(f"已创建浏览器上下文: {context_id}")
        return context_id

    def create_page(self, context_id: Optional[str] = None) -> str:
        """创建页面

        Args:
            context_id: 上下文ID，如果为None则使用当前上下文

        Returns:
            str: 页面ID
        """
        if context_id is None:
            context_id = self.current_context

        if context_id is None:
            raise ValueError("没有可用的浏览器上下文")

        if context_id not in self.contexts:
            raise ValueError(f"浏览器上下文 {context_id} 不存在")

        context = self.contexts[context_id]
        page = context.new_page()

        # 生成页面ID
        page_id = f"{context_id}_page_{len(self.pages)}"
        self.pages[page_id] = page
        self.current_page = page_id

        logger.info(f"已创建页面: {page_id}")
        return page_id

    def get_current_page(self) -> Page:
        """获取当前页面实例"""
        if self.current_page is None or self.current_page not in self.pages:
            raise ValueError("没有可用的页面实例")
        return self.pages[self.current_page]

    def get_page(self, page_id: str) -> Page:
        """获取指定页面实例"""
        if page_id not in self.pages:
            raise ValueError(f"页面 {page_id} 不存在")
        return self.pages[page_id]

    def get_current_context(self) -> Optional[BrowserContext]:
        """获取当前浏览器上下文实例"""
        if self.current_context is None or self.current_context not in self.contexts:
            return None
        return self.contexts[self.current_context]

    def get_context(self, context_id: str) -> BrowserContext:
        """获取指定浏览器上下文实例"""
        if context_id not in self.contexts:
            raise ValueError(f"浏览器上下文 {context_id} 不存在")
        return self.contexts[context_id]

    def switch_page(self, page_id: str):
        """切换到指定页面"""
        if page_id not in self.pages:
            raise ValueError(f"页面 {page_id} 不存在")
        self.current_page = page_id
        logger.info(f"已切换到页面: {page_id}")

    def get_page_list(self) -> dict:
        """获取页面列表信息
        
        Returns:
            dict: 包含页面ID列表和当前页面信息的字典
        """
        return {
            'page_ids': list(self.pages.keys()),
            'current_page_id': self.current_page,
            'page_count': len(self.pages)
        }

    def get_current_page_id(self) -> Optional[str]:
        """获取当前页面ID
        
        Returns:
            Optional[str]: 当前页面ID，如果没有页面则返回None
        """
        return self.current_page

    def close_browser(self, browser_id: Optional[str] = None):
        """关闭浏览器

        Args:
            browser_id: 浏览器ID，如果为None则关闭当前浏览器
        """
        if browser_id is None:
            browser_id = self.current_browser

        if browser_id is None:
            logger.warning("没有可关闭的浏览器实例")
            return

        if browser_id in self.browsers:
            browser = self.browsers[browser_id]
            browser.close()
            del self.browsers[browser_id]

            # 清理相关的上下文和页面
            contexts_to_remove = [
                ctx_id for ctx_id in self.contexts.keys()
                if ctx_id.startswith(browser_id)
            ]
            for ctx_id in contexts_to_remove:
                del self.contexts[ctx_id]

            pages_to_remove = [
                page_id for page_id in self.pages.keys()
                if page_id.startswith(browser_id)
            ]
            for page_id in pages_to_remove:
                del self.pages[page_id]

            # 更新当前引用
            if self.current_browser == browser_id:
                self.current_browser = None
                self.current_context = None
                self.current_page = None

            logger.info(f"已关闭浏览器: {browser_id}")

    def close_all(self):
        """关闭所有浏览器实例"""
        for browser in self.browsers.values():
            browser.close()

        if self.playwright:
            self.playwright.stop()

        self.browsers.clear()
        self.contexts.clear()
        self.pages.clear()
        self.playwright = None
        self.current_browser = None
        self.current_context = None
        self.current_page = None
        logger.info("已关闭所有浏览器实例")


# 全局浏览器管理器实例
browser_manager = BrowserManager()
