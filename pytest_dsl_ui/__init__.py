"""pytest-dsl-ui: Playwright-based UI automation keywords for pytest-dsl

这个包为pytest-dsl框架提供基于Playwright的UI自动化测试关键字。
通过entry_points机制自动集成到pytest-dsl中。
"""

__version__ = "0.1.0"
__author__ = "Chen Shuanglin"

from pytest_dsl.core.keyword_manager import keyword_manager


def register_keywords(keyword_manager_instance=None):
    """注册所有UI关键字到关键字管理器
    
    这个函数会被pytest-dsl的插件发现机制自动调用。
    
    Args:
        keyword_manager_instance: 关键字管理器实例，如果为None则使用全局实例
    """
    if keyword_manager_instance is None:
        keyword_manager_instance = keyword_manager
    
    # 导入所有关键字模块，触发关键字注册
    try:
        from . import keywords
        print("pytest-dsl-ui: 已成功加载UI自动化关键字")
    except ImportError as e:
        print(f"pytest-dsl-ui: 加载关键字时出错: {e}")
        raise


# 当模块被直接导入时，自动注册关键字
# 这确保了即使没有调用register_keywords函数，关键字也会被注册
try:
    from . import keywords
except ImportError:
    # 在某些情况下（如安装时），可能无法导入依赖
    pass
