"""页面上下文管理器

管理页面状态、截图、录制等功能，使用Playwright同步API。
"""

import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, Union
from playwright.sync_api import Page

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

    def navigate(self, url: str, wait_until: str = "load", 
                timeout: Optional[float] = None):
        """导航到指定URL

        Args:
            url: 目标URL
            wait_until: 等待条件 (load, domcontentloaded, networkidle)
            timeout: 超时时间（秒）
        """
        timeout_ms = int(timeout * 1000) if timeout else 30000
        self.page.goto(url, wait_until=wait_until, timeout=timeout_ms)
        logger.info(f"已导航到: {url}")

    def reload(self, wait_until: str = "load", timeout: Optional[float] = None):
        """重新加载页面

        Args:
            wait_until: 等待条件 (load, domcontentloaded, networkidle)
            timeout: 超时时间（秒）
        """
        timeout_ms = int(timeout * 1000) if timeout else 30000
        self.page.reload(wait_until=wait_until, timeout=timeout_ms)
        logger.info("页面已重新加载")

    def go_back(self, wait_until: str = "load", timeout: Optional[float] = None):
        """浏览器后退

        Args:
            wait_until: 等待条件 (load, domcontentloaded, networkidle)
            timeout: 超时时间（秒）
        """
        timeout_ms = int(timeout * 1000) if timeout else 30000
        self.page.go_back(wait_until=wait_until, timeout=timeout_ms)
        logger.info("浏览器已后退")

    def go_forward(self, wait_until: str = "load", 
                  timeout: Optional[float] = None):
        """浏览器前进

        Args:
            wait_until: 等待条件 (load, domcontentloaded, networkidle)
            timeout: 超时时间（秒）
        """
        timeout_ms = int(timeout * 1000) if timeout else 30000
        self.page.go_forward(wait_until=wait_until, timeout=timeout_ms)
        logger.info("浏览器已前进")

    def get_title(self) -> str:
        """获取页面标题

        Returns:
            str: 页面标题
        """
        return self.page.title()

    def get_url(self) -> str:
        """获取当前页面URL

        Returns:
            str: 当前页面URL
        """
        return self.page.url

    def screenshot(self, path: Optional[str] = None, 
                  element_selector: Optional[str] = None,
                  full_page: bool = False) -> str:
        """截图

        Args:
            path: 截图保存路径
            element_selector: 要截图的元素选择器
            full_page: 是否截取整页

        Returns:
            str: 截图文件路径
        """
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
            element.screenshot(path=path)
        else:
            # 截取整个页面
            self.page.screenshot(path=path, full_page=full_page)

        return path

    def start_video_recording(self, path: Optional[str] = None) -> str:
        """开始录制视频

        Args:
            path: 录制文件保存路径

        Returns:
            str: 录制文件路径
        """
        if self.recording_path:
            logger.warning("已有录制在进行中")
            return self.recording_path

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

    def wait_for_load_state(self, state: str = "load", 
                           timeout: Optional[float] = None):
        """等待页面加载状态

        Args:
            state: 加载状态 (load, domcontentloaded, networkidle)
            timeout: 超时时间（秒）
        """
        timeout_ms = int(timeout * 1000) if timeout else 30000
        self.page.wait_for_load_state(state, timeout=timeout_ms)
        logger.info(f"页面已达到加载状态: {state}")

    def evaluate(self, expression: str) -> Any:
        """执行JavaScript表达式

        Args:
            expression: JavaScript表达式

        Returns:
            Any: 表达式执行结果
        """
        return self.page.evaluate(expression)

    def set_viewport_size(self, width: int, height: int):
        """设置视口大小

        Args:
            width: 视口宽度
            height: 视口高度
        """
        self.page.set_viewport_size({"width": width, "height": height})
        logger.info(f"视口大小已设置为: {width}x{height}")

    def get_viewport_size(self) -> Dict[str, int]:
        """获取当前视口大小

        Returns:
            Dict[str, int]: 包含width和height的字典
        """
        viewport = self.page.viewport_size
        if viewport:
            return {"width": viewport["width"], "height": viewport["height"]}
        else:
            return {"width": 0, "height": 0}
