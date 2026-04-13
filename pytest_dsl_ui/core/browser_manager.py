"""浏览器管理器

负责管理 Playwright 浏览器实例的生命周期。
所有 Playwright 同步 API 调用都会被转发到同一个工作线程，
避免远程关键字在不同请求线程之间切换时触发 greenlet/thread 错误。
"""

from __future__ import annotations

import atexit
import logging
import queue
import threading
from concurrent.futures import Future
from typing import Any, Callable, Dict, Optional

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)

logger = logging.getLogger(__name__)


class _WorkerThread:
    """串行执行 Playwright 调用的专用线程。"""

    def __init__(self):
        self._queue: "queue.Queue[Any]" = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._thread_id: Optional[int] = None
        self._stop_sentinel = object()
        self._lock = threading.Lock()

    def _ensure_started(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                return

            self._thread = threading.Thread(
                target=self._run_loop,
                name="pytest-dsl-ui-playwright-worker",
                daemon=True,
            )
            self._thread.start()

    def _run_loop(self):
        self._thread_id = threading.get_ident()

        while True:
            item = self._queue.get()
            if item is self._stop_sentinel:
                break

            future, func, args, kwargs = item
            try:
                future.set_result(func(*args, **kwargs))
            except BaseException as exc:
                future.set_exception(exc)

    def run(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        self._ensure_started()

        if threading.get_ident() == self._thread_id:
            return func(*args, **kwargs)

        future: Future[Any] = Future()
        self._queue.put((future, func, args, kwargs))
        return future.result()

    def shutdown(self):
        with self._lock:
            if not self._thread or not self._thread.is_alive():
                self._thread = None
                self._thread_id = None
                return

            self._queue.put(self._stop_sentinel)
            self._thread.join(timeout=2)
            self._thread = None
            self._thread_id = None


class _PlaywrightMethodProxy:
    """将对象方法调用转发到工作线程。"""

    def __init__(self, manager: "BrowserManager", object_id: str, method_name: str):
        self._manager = manager
        self._object_id = object_id
        self._method_name = method_name

    def __call__(self, *args, **kwargs):
        return self._manager._call_object_method(
            self._object_id, self._method_name, *args, **kwargs
        )

    def __repr__(self) -> str:
        return f"<_PlaywrightMethodProxy {self._method_name}>"


class _PlaywrightObjectProxy:
    """Playwright 同步对象的跨线程代理。"""

    def __init__(self, manager: "BrowserManager", object_id: str):
        object.__setattr__(self, "_manager", manager)
        object.__setattr__(self, "_object_id", object_id)

    def __getattr__(self, name: str):
        if self._manager._is_callable_attribute(self._object_id, name):
            return _PlaywrightMethodProxy(self._manager, self._object_id, name)
        return self._manager._get_object_attribute(self._object_id, name)

    def __enter__(self):
        return self._manager._call_object_method(self._object_id, "__enter__")

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._manager._call_object_method(
            self._object_id, "__exit__", exc_type, exc_val, exc_tb
        )

    def __repr__(self) -> str:
        try:
            return self._manager._call_object_method(self._object_id, "__repr__")
        except Exception:
            return f"<_PlaywrightObjectProxy {self._object_id}>"


class BrowserManager:
    """浏览器管理器

    管理 Playwright 浏览器实例，支持多浏览器、多上下文和多页面。
    """

    def __init__(self):
        self.playwright: Optional[_PlaywrightObjectProxy] = None
        self.browsers: Dict[str, Any] = {}
        self.contexts: Dict[str, Any] = {}
        self.pages: Dict[str, Any] = {}
        self.current_browser: Optional[str] = None
        self.current_context: Optional[str] = None
        self.current_page: Optional[str] = None

        self._worker = _WorkerThread()
        self._objects: Dict[str, Any] = {}
        self._identity_to_object_id: Dict[int, str] = {}
        self._registry_lock = threading.Lock()
        atexit.register(self.shutdown_worker)

    def _ensure_playwright(self):
        """确保 Playwright 实例已在工作线程中启动。"""
        if self.playwright is None:
            playwright = self._worker.run(lambda: sync_playwright().start())
            self.playwright = self._wrap_result(playwright)

    def _should_proxy(self, value: Any) -> bool:
        if isinstance(value, BaseException):
            return False

        value_type = type(value)
        module_name = getattr(value_type, "__module__", "")
        return module_name.startswith("playwright.") or getattr(
            value_type, "__thread_proxy_target__", False
        )

    def _register_object(self, value: Any) -> str:
        object_identity = id(value)

        with self._registry_lock:
            existing_id = self._identity_to_object_id.get(object_identity)
            if existing_id and self._objects.get(existing_id) is value:
                return existing_id

            object_id = f"{type(value).__module__}:{type(value).__name__}:{object_identity}"
            self._objects[object_id] = value
            self._identity_to_object_id[object_identity] = object_id
            return object_id

    def _unregister_proxy(self, value: Any):
        if isinstance(value, _PlaywrightObjectProxy):
            with self._registry_lock:
                raw_object = self._objects.pop(value._object_id, None)
                if raw_object is not None:
                    self._identity_to_object_id.pop(id(raw_object), None)
            return

        if isinstance(value, dict):
            for item in value.values():
                self._unregister_proxy(item)
            return

        if isinstance(value, (list, tuple, set)):
            for item in value:
                self._unregister_proxy(item)

    def _wrap_result(self, value: Any) -> Any:
        if isinstance(value, _PlaywrightObjectProxy):
            return value

        if isinstance(value, list):
            return [self._wrap_result(item) for item in value]

        if isinstance(value, tuple):
            return tuple(self._wrap_result(item) for item in value)

        if isinstance(value, set):
            return {self._wrap_result(item) for item in value}

        if isinstance(value, dict):
            return {key: self._wrap_result(item) for key, item in value.items()}

        if self._should_proxy(value):
            return _PlaywrightObjectProxy(self, self._register_object(value))

        return value

    def _unwrap_value(self, value: Any) -> Any:
        if isinstance(value, _PlaywrightObjectProxy):
            with self._registry_lock:
                raw_object = self._objects.get(value._object_id)
            if raw_object is None:
                raise RuntimeError("Playwright 对象已失效或被释放")
            return raw_object

        if isinstance(value, list):
            return [self._unwrap_value(item) for item in value]

        if isinstance(value, tuple):
            return tuple(self._unwrap_value(item) for item in value)

        if isinstance(value, set):
            return {self._unwrap_value(item) for item in value}

        if isinstance(value, dict):
            return {key: self._unwrap_value(item) for key, item in value.items()}

        return value

    def _get_object(self, object_id: str) -> Any:
        with self._registry_lock:
            value = self._objects.get(object_id)

        if value is None:
            raise RuntimeError(f"Playwright 对象不存在或已失效: {object_id}")
        return value

    def _is_callable_attribute(self, object_id: str, attr_name: str) -> bool:
        def _check():
            return callable(getattr(self._get_object(object_id), attr_name))

        return self._worker.run(_check)

    def _get_object_attribute(self, object_id: str, attr_name: str) -> Any:
        def _get():
            return getattr(self._get_object(object_id), attr_name)

        return self._wrap_result(self._worker.run(_get))

    def _call_object_method(self, object_id: str, method_name: str, *args, **kwargs):
        unwrapped_args = self._unwrap_value(args)
        unwrapped_kwargs = self._unwrap_value(kwargs)

        def _call():
            method = getattr(self._get_object(object_id), method_name)
            return method(*unwrapped_args, **unwrapped_kwargs)

        return self._wrap_result(self._worker.run(_call))

    def run_in_worker(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """在 Playwright 工作线程中执行任意调用并返回结果。"""
        unwrapped_args = self._unwrap_value(args)
        unwrapped_kwargs = self._unwrap_value(kwargs)
        return self._wrap_result(
            self._worker.run(lambda: func(*unwrapped_args, **unwrapped_kwargs))
        )

    def expect(self, target: Any):
        """在工作线程中创建 Playwright expect 断言对象。"""
        from playwright.sync_api import expect as playwright_expect

        unwrapped_target = self._unwrap_value(target)
        return self._wrap_result(
            self._worker.run(lambda: playwright_expect(unwrapped_target))
        )

    def launch_browser(self, browser_type: str = "chromium", **config) -> str:
        """启动浏览器并返回浏览器 ID。"""
        self._ensure_playwright()

        if browser_type.lower() == "chromium":
            browser_launcher = self.playwright.chromium
        elif browser_type.lower() == "firefox":
            browser_launcher = self.playwright.firefox
        elif browser_type.lower() == "webkit":
            browser_launcher = self.playwright.webkit
        else:
            raise ValueError(f"不支持的浏览器类型: {browser_type}")

        launch_config = {
            "headless": config.get("headless", True),
            "slow_mo": config.get("slow_mo", 0),
        }

        if "args" in config:
            launch_config["args"] = config["args"]

        if "executable_path" in config:
            launch_config["executable_path"] = config["executable_path"]

        browser = browser_launcher.launch(**launch_config)
        browser_id = f"{browser_type}_{len(self.browsers)}"
        self.browsers[browser_id] = browser
        self.current_browser = browser_id

        logger.info(f"已启动浏览器: {browser_id}")
        return browser_id

    def create_context(self, browser_id: Optional[str] = None, **config) -> str:
        """创建浏览器上下文并返回上下文 ID。"""
        if browser_id is None:
            browser_id = self.current_browser

        if browser_id is None:
            raise ValueError("没有可用的浏览器实例")

        if browser_id not in self.browsers:
            raise ValueError(f"浏览器 {browser_id} 不存在")

        browser = self.browsers[browser_id]
        context_config: Dict[str, Any] = {}

        if "viewport" in config:
            context_config["viewport"] = config["viewport"]
        elif "width" in config and "height" in config:
            context_config["viewport"] = {
                "width": config["width"],
                "height": config["height"],
            }

        if "user_agent" in config:
            context_config["user_agent"] = config["user_agent"]

        if "geolocation" in config:
            context_config["geolocation"] = config["geolocation"]

        if "permissions" in config:
            context_config["permissions"] = config["permissions"]

        if config.get("ignore_https_errors", False):
            context_config["ignore_https_errors"] = True

        if "storage_state" in config:
            context_config["storage_state"] = config["storage_state"]
            logger.info("将使用认证状态创建浏览器上下文")

        context = browser.new_context(**context_config)
        context_id = f"{browser_id}_ctx_{len(self.contexts)}"
        self.contexts[context_id] = context
        self.current_context = context_id

        logger.info(f"已创建浏览器上下文: {context_id}")
        return context_id

    def create_page(self, context_id: Optional[str] = None) -> str:
        """创建页面并返回页面 ID。"""
        if context_id is None:
            context_id = self.current_context

        if context_id is None:
            raise ValueError("没有可用的浏览器上下文")

        if context_id not in self.contexts:
            raise ValueError(f"浏览器上下文 {context_id} 不存在")

        context = self.contexts[context_id]
        page = context.new_page()

        page_id = f"{context_id}_page_{len(self.pages)}"
        self.pages[page_id] = page
        self.current_page = page_id

        logger.info(f"已创建页面: {page_id}")
        return page_id

    def get_current_page(self) -> Page:
        """获取当前页面实例。"""
        if self.current_page is None or self.current_page not in self.pages:
            raise ValueError("没有可用的页面实例")
        return self.pages[self.current_page]

    def get_page(self, page_id: str) -> Page:
        """获取指定页面实例。"""
        if page_id not in self.pages:
            raise ValueError(f"页面 {page_id} 不存在")
        return self.pages[page_id]

    def get_current_context(self) -> Optional[BrowserContext]:
        """获取当前浏览器上下文实例。"""
        if self.current_context is None or self.current_context not in self.contexts:
            return None
        return self.contexts[self.current_context]

    def get_context(self, context_id: str) -> BrowserContext:
        """获取指定浏览器上下文实例。"""
        if context_id not in self.contexts:
            raise ValueError(f"浏览器上下文 {context_id} 不存在")
        return self.contexts[context_id]

    def switch_page(self, page_id: str):
        """切换到指定页面。"""
        if page_id not in self.pages:
            raise ValueError(f"页面 {page_id} 不存在")
        self.current_page = page_id
        logger.info(f"已切换到页面: {page_id}")

    def get_page_list(self) -> dict:
        """获取页面列表信息。"""
        return {
            "page_ids": list(self.pages.keys()),
            "current_page_id": self.current_page,
            "page_count": len(self.pages),
        }

    def get_current_page_id(self) -> Optional[str]:
        """获取当前页面 ID。"""
        return self.current_page

    def close_browser(self, browser_id: Optional[str] = None):
        """关闭浏览器。"""
        if browser_id is None:
            browser_id = self.current_browser

        if browser_id is None:
            logger.warning("没有可关闭的浏览器实例")
            return

        if browser_id not in self.browsers:
            return

        browser = self.browsers[browser_id]
        browser.close()
        self._unregister_proxy(browser)
        del self.browsers[browser_id]

        contexts_to_remove = [
            ctx_id for ctx_id in self.contexts.keys() if ctx_id.startswith(browser_id)
        ]
        for ctx_id in contexts_to_remove:
            self._unregister_proxy(self.contexts[ctx_id])
            del self.contexts[ctx_id]

        pages_to_remove = [
            page_id for page_id in self.pages.keys() if page_id.startswith(browser_id)
        ]
        for page_id in pages_to_remove:
            self._unregister_proxy(self.pages[page_id])
            del self.pages[page_id]

        if self.current_browser == browser_id:
            self.current_browser = None
            self.current_context = None
            self.current_page = None

        logger.info(f"已关闭浏览器: {browser_id}")

    def close_all(self):
        """关闭所有浏览器实例和 Playwright。"""
        for browser in list(self.browsers.values()):
            browser.close()
            self._unregister_proxy(browser)

        if self.playwright:
            self.playwright.stop()
            self._unregister_proxy(self.playwright)

        self.browsers.clear()
        self.contexts.clear()
        self.pages.clear()

        with self._registry_lock:
            self._objects.clear()
            self._identity_to_object_id.clear()

        self.playwright = None
        self.current_browser = None
        self.current_context = None
        self.current_page = None
        logger.info("已关闭所有浏览器实例")

    def shutdown_worker(self):
        """关闭工作线程。"""
        try:
            self.close_all()
        except Exception:
            logger.debug("关闭 Playwright 资源时发生异常", exc_info=True)
        finally:
            self._worker.shutdown()


# 全局浏览器管理器实例
browser_manager = BrowserManager()
