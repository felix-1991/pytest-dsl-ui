"""测试 UI 断言关键字中的布尔检查委托行为。"""

from contextlib import contextmanager
import re

import pytest

from pytest_dsl_ui.keywords import assertion_keywords
from pytest_dsl_ui.keywords import element_keywords_extended


class _FakeElement:
    def __init__(self, *, text="", attributes=None):
        self.text = text
        self.attributes = attributes or {}
        self.text_calls = []
        self.attribute_calls = []

    def text_content(self, timeout=None):
        self.text_calls.append(timeout)
        return self.text

    def get_attribute(self, name, timeout=None):
        self.attribute_calls.append({"name": name, "timeout": timeout})
        return self.attributes.get(name)


class _FakeLocator:
    def __init__(
        self,
        *,
        wait_result=True,
        count=0,
        visible=False,
        element=None,
    ):
        self.wait_result = wait_result
        self.count = count
        self.visible = visible
        self.element = element or _FakeElement()
        self.wait_calls = []
        self.count_calls = []
        self.visible_calls = []
        self.locate_calls = []
        self.checked = False

    def wait_for_element(self, selector, state="visible", timeout=None):
        self.wait_calls.append(
            {"selector": selector, "state": state, "timeout": timeout}
        )
        return self.wait_result

    def get_element_count(self, selector):
        self.count_calls.append(selector)
        return self.count

    def is_element_visible(self, selector):
        self.visible_calls.append(selector)
        return self.visible

    def locate(self, selector):
        self.locate_calls.append(selector)
        return self.element

    def is_element_checked(self, selector):
        return self.checked


class _FakePage:
    def __init__(self, *, url="", title=""):
        self.url = url
        self._title = title
        self.title_calls = 0

    def title(self):
        self.title_calls += 1
        return self._title


class _FakeExpect:
    def __init__(self, failing_methods=None):
        self.failing_methods = set(failing_methods or [])
        self.calls = []

    def __call__(self, target):
        parent = self

        class _AssertionProxy:
            def __getattr__(self, name):
                def _call(*args, **kwargs):
                    parent.calls.append(
                        {
                            "target": target,
                            "method": name,
                            "args": args,
                            "kwargs": kwargs,
                        }
                    )
                    if name in parent.failing_methods:
                        raise AssertionError(f"{name} failed")

                return _call

        return _AssertionProxy()


@contextmanager
def _noop_step(_title):
    yield


@pytest.fixture
def patch_allure(monkeypatch):
    monkeypatch.setattr(assertion_keywords.allure, "attach", lambda *args, **kwargs: None)
    monkeypatch.setattr(assertion_keywords.allure, "step", _noop_step)
    monkeypatch.setattr(
        element_keywords_extended.allure,
        "attach",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(element_keywords_extended.allure, "step", _noop_step)


def test_check_element_exists_waits_for_attached_state(monkeypatch, patch_allure):
    locator = _FakeLocator(wait_result=True, count=1)

    monkeypatch.setattr(assertion_keywords, "_get_current_locator", lambda: locator)

    result = assertion_keywords.check_element_exists(
        selector="#delayed-element",
        timeout=2.5,
    )

    assert result is True
    assert locator.wait_calls == [
        {"selector": "#delayed-element", "state": "attached", "timeout": 2.5}
    ]
    assert locator.count_calls == ["#delayed-element"]


def test_check_element_exists_returns_false_after_wait_timeout(
    monkeypatch, patch_allure
):
    locator = _FakeLocator(wait_result=False, count=0)

    monkeypatch.setattr(assertion_keywords, "_get_current_locator", lambda: locator)

    result = assertion_keywords.check_element_exists(
        selector="#missing-element",
        timeout=0.25,
    )

    assert result is False
    assert locator.wait_calls == [
        {"selector": "#missing-element", "state": "attached", "timeout": 0.25}
    ]


def test_check_element_visible_waits_for_visible_state(monkeypatch, patch_allure):
    locator = _FakeLocator(wait_result=True)

    monkeypatch.setattr(assertion_keywords, "_get_current_locator", lambda: locator)

    result = assertion_keywords.check_element_visible(
        selector="#delayed-visible",
        timeout=1.5,
    )

    assert result is True
    assert locator.wait_calls == [
        {"selector": "#delayed-visible", "state": "visible", "timeout": 1.5}
    ]


def test_check_element_visible_returns_false_after_wait_timeout(
    monkeypatch, patch_allure
):
    locator = _FakeLocator(wait_result=False)

    monkeypatch.setattr(assertion_keywords, "_get_current_locator", lambda: locator)

    result = assertion_keywords.check_element_visible(
        selector="#always-hidden",
        timeout=0.25,
    )

    assert result is False
    assert locator.wait_calls == [
        {"selector": "#always-hidden", "state": "visible", "timeout": 0.25}
    ]


def test_check_element_enabled_uses_expect_timeout(monkeypatch, patch_allure):
    fake_expect = _FakeExpect()
    locator = _FakeLocator()

    monkeypatch.setattr(assertion_keywords, "expect", fake_expect)
    monkeypatch.setattr(assertion_keywords, "_get_current_locator", lambda: locator)

    result = assertion_keywords.check_element_enabled(
        selector="#submit",
        timeout=3,
    )

    assert result is True
    assert fake_expect.calls == [
        {
            "target": locator.element,
            "method": "to_be_enabled",
            "args": (),
            "kwargs": {"timeout": 3000},
        }
    ]


def test_check_text_contains_uses_expect_timeout(monkeypatch, patch_allure):
    fake_expect = _FakeExpect()
    element = _FakeElement(text="welcome back")
    locator = _FakeLocator(element=element)

    monkeypatch.setattr(assertion_keywords, "expect", fake_expect)
    monkeypatch.setattr(assertion_keywords, "_get_current_locator", lambda: locator)

    result = assertion_keywords.check_text_contains(
        selector=".message",
        expected_text="welcome",
        timeout=2,
    )

    assert result is True
    assert fake_expect.calls == [
        {
            "target": element,
            "method": "to_contain_text",
            "args": ("welcome",),
            "kwargs": {"timeout": 2000},
        }
    ]
    assert element.text_calls == [0]


def test_check_url_contains_uses_page_expect_timeout(monkeypatch, patch_allure):
    fake_expect = _FakeExpect()
    page = _FakePage(url="https://example.com/dashboard")

    monkeypatch.setattr(assertion_keywords, "expect", fake_expect)
    monkeypatch.setattr(
        assertion_keywords.browser_manager,
        "get_current_page",
        lambda: page,
    )

    result = assertion_keywords.check_url_contains(
        url_fragment="/dashboard",
        timeout=4,
    )

    assert result is True
    call = fake_expect.calls[0]
    assert call["target"] is page
    assert call["method"] == "to_have_url"
    assert call["kwargs"] == {"timeout": 4000}
    assert isinstance(call["args"][0], re.Pattern)
    assert call["args"][0].search(page.url)


def test_check_title_contains_uses_page_expect_timeout(monkeypatch, patch_allure):
    fake_expect = _FakeExpect()
    page = _FakePage(title="控制台首页")

    monkeypatch.setattr(assertion_keywords, "expect", fake_expect)
    monkeypatch.setattr(
        assertion_keywords.browser_manager,
        "get_current_page",
        lambda: page,
    )

    result = assertion_keywords.check_title_contains(
        title_fragment="首页",
        timeout=1.5,
    )

    assert result is True
    call = fake_expect.calls[0]
    assert call["target"] is page
    assert call["method"] == "to_have_title"
    assert call["kwargs"] == {"timeout": 1500}
    assert isinstance(call["args"][0], re.Pattern)
    assert call["args"][0].search(page.title())


def test_check_attribute_value_uses_expect_timeout(monkeypatch, patch_allure):
    fake_expect = _FakeExpect()
    element = _FakeElement(attributes={"data-state": "ready"})
    locator = _FakeLocator(element=element)

    monkeypatch.setattr(assertion_keywords, "expect", fake_expect)
    monkeypatch.setattr(assertion_keywords, "_get_current_locator", lambda: locator)

    result = assertion_keywords.check_attribute_value(
        selector="#status",
        attribute_name="data-state",
        expected_value="ready",
        timeout=2.5,
    )

    assert result is True
    assert fake_expect.calls == [
        {
            "target": element,
            "method": "to_have_attribute",
            "args": ("data-state", "ready"),
            "kwargs": {"timeout": 2500},
        }
    ]
    assert element.attribute_calls == [{"name": "data-state", "timeout": 0}]


def test_check_attribute_value_none_waits_for_attached(monkeypatch, patch_allure):
    element = _FakeElement(attributes={})
    locator = _FakeLocator(wait_result=True, element=element)

    monkeypatch.setattr(assertion_keywords, "_get_current_locator", lambda: locator)

    result = assertion_keywords.check_attribute_value(
        selector="#status",
        attribute_name="data-missing",
        expected_value=None,
        timeout=1.25,
    )

    assert result is True
    assert locator.wait_calls == [
        {"selector": "#status", "state": "attached", "timeout": 1.25}
    ]


def test_multiple_conditions_returns_bool(monkeypatch, patch_allure):
    monkeypatch.setattr(assertion_keywords, "check_element_visible", lambda **_: True)
    monkeypatch.setattr(assertion_keywords, "check_text_contains", lambda **_: False)

    result = assertion_keywords.check_multiple_conditions(
        conditions=[
            {"type": "element_visible", "selector": "#dialog"},
            {
                "type": "text_contains",
                "selector": ".status",
                "expected_text": "成功",
            },
        ],
        logic="OR",
    )

    assert result is True


def test_check_element_checked_returns_bool(monkeypatch, patch_allure):
    locator = _FakeLocator()
    locator.checked = True

    monkeypatch.setattr(
        element_keywords_extended,
        "_get_current_locator",
        lambda: locator,
    )

    result = element_keywords_extended.check_element_checked(selector="#agree")

    assert result is True
