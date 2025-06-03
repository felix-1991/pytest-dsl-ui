"""浏览器管理器

负责管理Playwright浏览器实例的生命周期，包括启动、关闭和配置。
支持多浏览器、多页面的管理。
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from playwright.async_api import (
    async_playwright, Browser, BrowserContext, Page, Playwright
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
        self._loop = None
        
    async def _ensure_playwright(self):
        """确保Playwright实例已启动"""
        if self.playwright is None:
            self.playwright = await async_playwright().start()
            
    def _get_event_loop(self):
        """获取或创建事件循环"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop
        
    def _run_async(self, coro):
        """运行异步协程"""
        loop = self._get_event_loop()
        if loop.is_running():
            # 如果循环正在运行，创建一个任务
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    
    async def _launch_browser_async(self, browser_type: str, config: Dict[str, Any]) -> str:
        """异步启动浏览器"""
        await self._ensure_playwright()
        
        # 获取浏览器类型
        if browser_type.lower() == "chromium":
            browser_launcher = self.playwright.chromium
        elif browser_type.lower() == "firefox":
            browser_launcher = self.playwright.firefox
        elif browser_type.lower() == "webkit":
            browser_launcher = self.playwright.webkit
        else:
            raise ValueError(f"不支持的浏览器类型: {browser_type}")
        
        # 启动浏览器
        browser = await browser_launcher.launch(**config)
        
        # 生成浏览器ID
        browser_id = f"{browser_type}_{len(self.browsers)}"
        self.browsers[browser_id] = browser
        self.current_browser = browser_id
        
        logger.info(f"已启动浏览器: {browser_id}")
        return browser_id
    
    def launch_browser(self, browser_type: str = "chromium", **config) -> str:
        """启动浏览器
        
        Args:
            browser_type: 浏览器类型 (chromium, firefox, webkit)
            **config: 浏览器启动配置
            
        Returns:
            str: 浏览器ID
        """
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
            
        return self._run_async(self._launch_browser_async(browser_type, launch_config))
    
    async def _create_context_async(self, browser_id: str, config: Dict[str, Any]) -> str:
        """异步创建浏览器上下文"""
        if browser_id not in self.browsers:
            raise ValueError(f"浏览器 {browser_id} 不存在")
            
        browser = self.browsers[browser_id]
        context = await browser.new_context(**config)
        
        # 生成上下文ID
        context_id = f"{browser_id}_ctx_{len(self.contexts)}"
        self.contexts[context_id] = context
        self.current_context = context_id
        
        logger.info(f"已创建浏览器上下文: {context_id}")
        return context_id
    
    def create_context(self, browser_id: Optional[str] = None, **config) -> str:
        """创建浏览器上下文
        
        Args:
            browser_id: 浏览器ID，如果为None则使用当前浏览器
            **config: 上下文配置
            
        Returns:
            str: 上下文ID
        """
        if browser_id is None:
            browser_id = self.current_browser
            
        if browser_id is None:
            raise ValueError("没有可用的浏览器实例")
        
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
            
        context_id = self._run_async(self._create_context_async(browser_id, context_config))
        
        # 在上下文对象上保存ignore_https_errors标志，方便后续检查
        if context_id in self.contexts:
            self.contexts[context_id]._ignore_https_errors = ignore_https_errors
            
        return context_id
    
    async def _create_page_async(self, context_id: str) -> str:
        """异步创建页面"""
        if context_id not in self.contexts:
            raise ValueError(f"浏览器上下文 {context_id} 不存在")
            
        context = self.contexts[context_id]
        page = await context.new_page()
        
        # 生成页面ID
        page_id = f"{context_id}_page_{len(self.pages)}"
        self.pages[page_id] = page
        self.current_page = page_id
        
        logger.info(f"已创建页面: {page_id}")
        return page_id
    
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
            
        return self._run_async(self._create_page_async(context_id))
    
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
    
    def switch_page(self, page_id: str):
        """切换到指定页面"""
        if page_id not in self.pages:
            raise ValueError(f"页面 {page_id} 不存在")
        self.current_page = page_id
        logger.info(f"已切换到页面: {page_id}")
    
    async def _close_browser_async(self, browser_id: str):
        """异步关闭浏览器"""
        if browser_id in self.browsers:
            browser = self.browsers[browser_id]
            await browser.close()
            del self.browsers[browser_id]
            
            # 清理相关的上下文和页面
            contexts_to_remove = [ctx_id for ctx_id in self.contexts.keys() if ctx_id.startswith(browser_id)]
            for ctx_id in contexts_to_remove:
                del self.contexts[ctx_id]
                
            pages_to_remove = [page_id for page_id in self.pages.keys() if page_id.startswith(browser_id)]
            for page_id in pages_to_remove:
                del self.pages[page_id]
            
            # 更新当前引用
            if self.current_browser == browser_id:
                self.current_browser = None
                self.current_context = None
                self.current_page = None
                
            logger.info(f"已关闭浏览器: {browser_id}")
    
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
            
        self._run_async(self._close_browser_async(browser_id))
    
    async def _close_all_async(self):
        """异步关闭所有浏览器"""
        for browser in self.browsers.values():
            await browser.close()
        
        if self.playwright:
            await self.playwright.stop()
            
        self.browsers.clear()
        self.contexts.clear()
        self.pages.clear()
        self.playwright = None
        self.current_browser = None
        self.current_context = None
        self.current_page = None
    
    def close_all(self):
        """关闭所有浏览器实例"""
        self._run_async(self._close_all_async())
        logger.info("已关闭所有浏览器实例")


# 全局浏览器管理器实例
browser_manager = BrowserManager()
