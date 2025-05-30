"""辅助工具函数

提供UI自动化测试中常用的辅助功能。
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)


def ensure_directory(path: Union[str, Path]) -> Path:
    """确保目录存在
    
    Args:
        path: 目录路径
        
    Returns:
        Path: 目录路径对象
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def generate_timestamp_filename(prefix: str = "", suffix: str = "", extension: str = "") -> str:
    """生成带时间戳的文件名
    
    Args:
        prefix: 文件名前缀
        suffix: 文件名后缀
        extension: 文件扩展名
        
    Returns:
        str: 生成的文件名
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    parts = []
    if prefix:
        parts.append(prefix)
    parts.append(timestamp)
    if suffix:
        parts.append(suffix)
    
    filename = "_".join(parts)
    
    if extension:
        if not extension.startswith("."):
            extension = "." + extension
        filename += extension
    
    return filename


def parse_selector(selector: str) -> Dict[str, str]:
    """解析选择器字符串
    
    Args:
        selector: 选择器字符串
        
    Returns:
        Dict[str, str]: 包含选择器类型和值的字典
    """
    selector = selector.strip()
    
    if selector.startswith("//") or selector.startswith("(//"):
        return {"type": "xpath", "value": selector}
    elif selector.startswith("text="):
        return {"type": "text", "value": selector[5:]}
    elif selector.startswith("role="):
        return {"type": "role", "value": selector[5:]}
    elif selector.startswith("placeholder="):
        return {"type": "placeholder", "value": selector[12:]}
    elif selector.startswith("label="):
        return {"type": "label", "value": selector[6:]}
    elif selector.startswith("title="):
        return {"type": "title", "value": selector[6:]}
    elif selector.startswith("alt="):
        return {"type": "alt", "value": selector[4:]}
    elif selector.startswith("testid="):
        return {"type": "testid", "value": selector[7:]}
    else:
        return {"type": "css", "value": selector}


def validate_browser_type(browser_type: str) -> str:
    """验证浏览器类型
    
    Args:
        browser_type: 浏览器类型
        
    Returns:
        str: 标准化的浏览器类型
        
    Raises:
        ValueError: 如果浏览器类型不支持
    """
    browser_type = browser_type.lower().strip()
    
    valid_browsers = ["chromium", "firefox", "webkit", "chrome", "edge"]
    
    # 处理别名
    if browser_type in ["chrome", "google-chrome"]:
        browser_type = "chromium"
    elif browser_type in ["edge", "microsoft-edge"]:
        browser_type = "chromium"
    elif browser_type in ["safari"]:
        browser_type = "webkit"
    
    if browser_type not in ["chromium", "firefox", "webkit"]:
        raise ValueError(f"不支持的浏览器类型: {browser_type}. 支持的类型: {valid_browsers}")
    
    return browser_type


def format_timeout(timeout: Optional[Union[int, float, str]]) -> Optional[int]:
    """格式化超时时间
    
    Args:
        timeout: 超时时间（秒）
        
    Returns:
        Optional[int]: 超时时间（毫秒），如果为None则返回None
    """
    if timeout is None:
        return None
    
    try:
        timeout_seconds = float(timeout)
        return int(timeout_seconds * 1000)  # 转换为毫秒
    except (ValueError, TypeError):
        logger.warning(f"无效的超时时间: {timeout}，使用默认值")
        return None


def safe_filename(filename: str) -> str:
    """生成安全的文件名
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 安全的文件名
    """
    # 移除或替换不安全的字符
    unsafe_chars = '<>:"/\\|?*'
    safe_name = filename
    
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, '_')
    
    # 移除多余的空格和点
    safe_name = safe_name.strip(' .')
    
    # 确保文件名不为空
    if not safe_name:
        safe_name = "unnamed"
    
    return safe_name


def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """合并配置字典
    
    Args:
        base_config: 基础配置
        override_config: 覆盖配置
        
    Returns:
        Dict[str, Any]: 合并后的配置
    """
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            # 递归合并嵌套字典
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged


def get_file_size(file_path: Union[str, Path]) -> int:
    """获取文件大小
    
    Args:
        file_path: 文件路径
        
    Returns:
        int: 文件大小（字节）
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化的文件大小
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def is_url(text: str) -> bool:
    """检查文本是否为URL
    
    Args:
        text: 要检查的文本
        
    Returns:
        bool: 是否为URL
    """
    text = text.strip().lower()
    return text.startswith(('http://', 'https://', 'file://', 'ftp://'))


def normalize_url(url: str) -> str:
    """标准化URL
    
    Args:
        url: 原始URL
        
    Returns:
        str: 标准化的URL
    """
    url = url.strip()
    
    # 如果没有协议，添加https://
    if not is_url(url):
        if url.startswith('localhost') or url.startswith('127.0.0.1'):
            url = 'http://' + url
        else:
            url = 'https://' + url
    
    return url


def wait_for_condition(condition_func, timeout: float = 30, interval: float = 0.5) -> bool:
    """等待条件满足
    
    Args:
        condition_func: 条件函数，返回True表示条件满足
        timeout: 超时时间（秒）
        interval: 检查间隔（秒）
        
    Returns:
        bool: 条件是否在超时时间内满足
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            if condition_func():
                return True
        except Exception as e:
            logger.debug(f"条件检查出错: {e}")
        
        time.sleep(interval)
    
    return False


def retry_on_exception(func, max_retries: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """重试装饰器
    
    Args:
        func: 要重试的函数
        max_retries: 最大重试次数
        delay: 重试间隔（秒）
        exceptions: 需要重试的异常类型
        
    Returns:
        装饰后的函数
    """
    def wrapper(*args, **kwargs):
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                if attempt < max_retries:
                    logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}，{delay}秒后重试")
                    time.sleep(delay)
                else:
                    logger.error(f"函数 {func.__name__} 重试 {max_retries} 次后仍然失败")
        
        raise last_exception
    
    return wrapper
