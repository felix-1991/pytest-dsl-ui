"""远程 pytest-dsl 验证时加载 pytest-dsl-ui 关键字。"""

from __future__ import annotations

import sys
import types


def _ensure_pyperclip_stub():
    """当前验证环境缺少 pyperclip，给远程服务补一个最小 stub。"""
    if "pyperclip" in sys.modules:
        return

    pyperclip_stub = types.ModuleType("pyperclip")
    _clipboard = {"text": ""}

    def copy(text: str):
        _clipboard["text"] = text or ""

    def paste() -> str:
        return _clipboard["text"]

    pyperclip_stub.copy = copy
    pyperclip_stub.paste = paste
    sys.modules["pyperclip"] = pyperclip_stub


_ensure_pyperclip_stub()

from pytest_dsl_ui import register_keywords  # noqa: E402

register_keywords()
