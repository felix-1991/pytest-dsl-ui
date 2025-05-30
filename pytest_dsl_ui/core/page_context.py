"""页面上下文管理器

管理页面状态、截图、录制等功能。
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, Union
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class PageContext:
    """页面上下文管理器
    
    管理页面的状态、截图、录制等功能。
    """
    
    def __init__(self, page: Page):
        """初始化页面上下文
        
        Args:
            page: Playwright页面实例
        """
        self.page = page
        self.screenshots_dir = Path("screenshots")
        self.videos_dir = Path("videos")
        self.recording_path: Optional[str] = None
        
        # 确保目录存在
        self.screenshots_dir.mkdir(exist_ok=True)
        self.videos_dir.mkdir(exist_ok=True)
    
    def _run_async(self, coro):
        """运行异步协程"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果循环正在运行，创建一个任务
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
    
    async def _navigate_async(self, url: str, wait_until: str = "load", timeout: Optional[float] = None):
        """异步导航到指定URL"""
        timeout_ms = int(timeout * 1000) if timeout else 30000
        await self.page.goto(url, wait_until=wait_until, timeout=timeout_ms)
    
    def navigate(self, url: str, wait_until: str = "load", timeout: Optional[float] = None):
        """导航到指定URL
        
        Args:
            url: 目标URL
            wait_until: 等待条件 (load, domcontentloaded, networkidle)
            timeout: 超时时间（秒）
        """
        self._run_async(self._navigate_async(url, wait_until, timeout))
        logger.info(f"已导航到: {url}")
    
    async def _reload_async(self, wait_until: str = "load", timeout: Optional[float] = None):
        """异步重新加载页面"""
        timeout_ms = int(timeout * 1000) if timeout else 30000
        await self.page.reload(wait_until=wait_until, timeout=timeout_ms)
    
    def reload(self, wait_until: str = "load", timeout: Optional[float] = None):
        """重新加载页面
        
        Args:
            wait_until: 等待条件 (load, domcontentloaded, networkidle)
            timeout: 超时时间（秒）
        """
        self._run_async(self._reload_async(wait_until, timeout))
        logger.info("页面已重新加载")
    
    async def _go_back_async(self, wait_until: str = "load", timeout: Optional[float] = None):
        """异步后退"""
        timeout_ms = int(timeout * 1000) if timeout else 30000
        await self.page.go_back(wait_until=wait_until, timeout=timeout_ms)
    
    def go_back(self, wait_until: str = "load", timeout: Optional[float] = None):
        """浏览器后退
        
        Args:
            wait_until: 等待条件 (load, domcontentloaded, networkidle)
            timeout: 超时时间（秒）
        """
        self._run_async(self._go_back_async(wait_until, timeout))
        logger.info("浏览器已后退")
    
    async def _go_forward_async(self, wait_until: str = "load", timeout: Optional[float] = None):
        """异步前进"""
        timeout_ms = int(timeout * 1000) if timeout else 30000
        await self.page.go_forward(wait_until=wait_until, timeout=timeout_ms)
    
    def go_forward(self, wait_until: str = "load", timeout: Optional[float] = None):
        """浏览器前进
        
        Args:
            wait_until: 等待条件 (load, domcontentloaded, networkidle)
            timeout: 超时时间（秒）
        """
        self._run_async(self._go_forward_async(wait_until, timeout))
        logger.info("浏览器已前进")
    
    async def _get_title_async(self) -> str:
        """异步获取页面标题"""
        return await self.page.title()
    
    def get_title(self) -> str:
        """获取页面标题
        
        Returns:
            str: 页面标题
        """
        return self._run_async(self._get_title_async())
    
    def get_url(self) -> str:
        """获取当前页面URL
        
        Returns:
            str: 当前页面URL
        """
        return self.page.url
    
    async def _screenshot_async(self, path: Optional[str] = None, element_selector: Optional[str] = None, 
                               full_page: bool = False) -> str:
        """异步截图"""
        if path is None:
            # 生成默认文件名
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = str(self.screenshots_dir / f"screenshot_{timestamp}.png")
        else:
            # 确保路径是绝对路径
            if not os.path.isabs(path):
                path = str(self.screenshots_dir / path)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        if element_selector:
            # 截取指定元素
            from .element_locator import ElementLocator
            locator = ElementLocator(self.page)
            element = locator.locate(element_selector)
            await element.screenshot(path=path)
        else:
            # 截取整个页面
            await self.page.screenshot(path=path, full_page=full_page)
        
        return path
    
    def screenshot(self, path: Optional[str] = None, element_selector: Optional[str] = None, 
                  full_page: bool = False) -> str:
        """截图
        
        Args:
            path: 保存路径，如果为None则自动生成
            element_selector: 元素选择器，如果指定则只截取该元素
            full_page: 是否截取整个页面（包括滚动区域）
            
        Returns:
            str: 截图文件路径
        """
        screenshot_path = self._run_async(self._screenshot_async(path, element_selector, full_page))
        logger.info(f"截图已保存: {screenshot_path}")
        return screenshot_path
    
    def start_recording(self, path: Optional[str] = None) -> str:
        """开始录制视频
        
        Args:
            path: 视频保存路径，如果为None则自动生成
            
        Returns:
            str: 视频文件路径
        """
        if path is None:
            # 生成默认文件名
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = str(self.videos_dir / f"recording_{timestamp}.webm")
        else:
            # 确保路径是绝对路径
            if not os.path.isabs(path):
                path = str(self.videos_dir / path)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # 注意：Playwright的录制需要在创建上下文时启动
        # 这里只是记录路径，实际录制需要在浏览器上下文级别配置
        self.recording_path = path
        logger.info(f"录制已开始，将保存到: {path}")
        return path
    
    def stop_recording(self) -> Optional[str]:
        """停止录制视频
        
        Returns:
            Optional[str]: 视频文件路径，如果没有在录制则返回None
        """
        if self.recording_path:
            path = self.recording_path
            self.recording_path = None
            logger.info(f"录制已停止，视频保存在: {path}")
            return path
        else:
            logger.warning("没有正在进行的录制")
            return None
    
    async def _wait_for_load_state_async(self, state: str = "load", timeout: Optional[float] = None):
        """异步等待页面加载状态"""
        timeout_ms = int(timeout * 1000) if timeout else 30000
        await self.page.wait_for_load_state(state, timeout=timeout_ms)
    
    def wait_for_load_state(self, state: str = "load", timeout: Optional[float] = None):
        """等待页面加载状态
        
        Args:
            state: 加载状态 (load, domcontentloaded, networkidle)
            timeout: 超时时间（秒）
        """
        self._run_async(self._wait_for_load_state_async(state, timeout))
        logger.info(f"页面已达到加载状态: {state}")
    
    async def _evaluate_async(self, expression: str) -> Any:
        """异步执行JavaScript表达式"""
        return await self.page.evaluate(expression)
    
    def evaluate(self, expression: str) -> Any:
        """执行JavaScript表达式
        
        Args:
            expression: JavaScript表达式
            
        Returns:
            Any: 表达式执行结果
        """
        return self._run_async(self._evaluate_async(expression))
    
    async def _set_viewport_size_async(self, width: int, height: int):
        """异步设置视口大小"""
        await self.page.set_viewport_size({"width": width, "height": height})
    
    def set_viewport_size(self, width: int, height: int):
        """设置视口大小
        
        Args:
            width: 视口宽度
            height: 视口高度
        """
        self._run_async(self._set_viewport_size_async(width, height))
        logger.info(f"视口大小已设置为: {width}x{height}")
    
    def get_viewport_size(self) -> Dict[str, int]:
        """获取当前视口大小
        
        Returns:
            Dict[str, int]: 包含width和height的字典
        """
        viewport = self.page.viewport_size
        return {"width": viewport["width"], "height": viewport["height"]} if viewport else {"width": 0, "height": 0}
