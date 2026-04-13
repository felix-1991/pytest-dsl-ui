"""浏览器管理器线程代理测试。"""

import threading

from pytest_dsl_ui.core.browser_manager import BrowserManager


class FakePlaywrightObject:
    """模拟需要固定在线程中执行的 Playwright 对象。"""

    __module__ = "playwright.fake"

    def __init__(self, label: str):
        self.label = label
        self.owner_thread = threading.get_ident()

    def thread_id(self):
        self._assert_owner_thread()
        return self.owner_thread

    def make_child(self, label: str):
        self._assert_owner_thread()
        return FakePlaywrightObject(label)

    def same_thread_as(self, other):
        self._assert_owner_thread()
        other._assert_owner_thread()
        return self.owner_thread == other.owner_thread

    def make_context_manager(self):
        self._assert_owner_thread()
        return FakeContextManager(self.label)

    def _assert_owner_thread(self):
        current = threading.get_ident()
        if current != self.owner_thread:
            raise RuntimeError(
                f"thread mismatch: expected {self.owner_thread}, got {current}"
            )


class FakeContextManager:
    """模拟 Playwright 的事件上下文管理器。"""

    __module__ = "playwright.fake"

    def __init__(self, label: str):
        self.label = label
        self.owner_thread = threading.get_ident()
        self.value = FakePlaywrightObject(f"{label}-value")

    def __enter__(self):
        self._assert_owner_thread()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._assert_owner_thread()
        return False

    def _assert_owner_thread(self):
        current = threading.get_ident()
        if current != self.owner_thread:
            raise RuntimeError(
                f"thread mismatch: expected {self.owner_thread}, got {current}"
            )


def test_worker_proxy_runs_methods_on_same_thread():
    manager = BrowserManager()

    try:
        page = manager.run_in_worker(FakePlaywrightObject, "root")
        worker_thread_id = page.thread_id()

        assert worker_thread_id != threading.get_ident()
        assert page.label == "root"

        child = page.make_child("child")
        assert child.label == "child"
        assert child.thread_id() == worker_thread_id
        assert page.same_thread_as(child) is True
    finally:
        manager.shutdown_worker()


def test_worker_proxy_supports_context_manager_protocol():
    manager = BrowserManager()

    try:
        page = manager.run_in_worker(FakePlaywrightObject, "root")

        with page.make_context_manager() as event_info:
            assert event_info.label == "root"

        assert event_info.value.label == "root-value"
        assert event_info.value.thread_id() == page.thread_id()
    finally:
        manager.shutdown_worker()
