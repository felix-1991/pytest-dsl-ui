"""UI关键字模块

导入所有UI关键字，确保它们被注册到关键字管理器中。
"""

# 导入所有关键字模块，触发关键字注册
from . import browser_keywords
from . import navigation_keywords
from . import element_keywords
from . import element_keywords_extended
from . import assertion_keywords
from . import capture_keywords
from . import captcha_keywords
from . import network_keywords
from . import auth_keywords
from . import download_keywords
from . import browser_http_keywords

__all__ = [
    'browser_keywords',
    'navigation_keywords',
    'element_keywords',
    'element_keywords_extended',
    'assertion_keywords',
    'capture_keywords',
    'captcha_keywords',
    'network_keywords',
    'auth_keywords',
    'download_keywords',
    'browser_http_keywords'
]
