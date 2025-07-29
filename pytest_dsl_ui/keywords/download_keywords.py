"""文件下载关键字

提供文件下载、下载监听、下载验证等功能。
基于Playwright的下载API实现。
"""

import logging
import os
import time
import allure
from pathlib import Path
from typing import Optional, Dict, Any, List

from pytest_dsl.core.keyword_manager import keyword_manager
from ..core.browser_manager import browser_manager
from ..utils.helpers import generate_timestamp_filename, safe_filename

logger = logging.getLogger(__name__)


@keyword_manager.register('等待下载', [
    {'name': '触发元素', 'mapping': 'trigger_selector', 
     'description': '触发下载的元素定位器'},
    {'name': '保存路径', 'mapping': 'save_path', 
     'description': '文件保存路径，不指定则使用默认下载目录'},
    {'name': '超时时间', 'mapping': 'timeout', 
     'description': '等待下载超时时间（秒）', 'default': 30},
    {'name': '变量名', 'mapping': 'variable', 
     'description': '保存下载文件路径的变量名'},
], category='UI/下载')
def wait_for_download(**kwargs):
    """等待文件下载完成

    Args:
        trigger_selector: 触发下载的元素定位器
        save_path: 保存路径
        timeout: 超时时间
        variable: 变量名

    Returns:
        dict: 包含下载文件路径的字典
    """
    trigger_selector = kwargs.get('trigger_selector')
    save_path = kwargs.get('save_path')
    timeout = kwargs.get('timeout', 30)
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    if not trigger_selector:
        raise ValueError("触发元素定位器不能为空")

    with allure.step(f"等待下载: {trigger_selector}"):
        try:
            page = browser_manager.get_current_page()
            
            # 开始等待下载
            with page.expect_download(timeout=timeout * 1000) as download_info:
                # 点击触发下载的元素
                page.locator(trigger_selector).click()
            
            # 获取下载对象
            download = download_info.value
            
            # 确定保存路径
            if save_path:
                if not os.path.isabs(save_path):
                    # 相对路径，转换为绝对路径
                    downloads_dir = Path("downloads")
                    downloads_dir.mkdir(exist_ok=True)
                    final_path = downloads_dir / save_path
                else:
                    final_path = Path(save_path)
            else:
                # 使用建议的文件名和默认下载目录
                downloads_dir = Path("downloads")
                downloads_dir.mkdir(exist_ok=True)
                suggested_name = download.suggested_filename
                if suggested_name:
                    final_path = downloads_dir / safe_filename(suggested_name)
                else:
                    # 生成带时间戳的文件名
                    final_path = downloads_dir / generate_timestamp_filename("download", extension="bin")
            
            # 确保目录存在
            final_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            download.save_as(str(final_path))
            
            # 等待文件完全写入
            download_path = str(final_path.absolute())
            
            # 验证文件是否成功下载
            if not os.path.exists(download_path):
                raise RuntimeError(f"下载失败：文件不存在 {download_path}")
            
            file_size = os.path.getsize(download_path)
            if file_size == 0:
                raise RuntimeError(f"下载失败：文件为空 {download_path}")

            # 保存到变量
            captures = {}
            if variable and context:
                context.set(variable, download_path)
                captures[variable] = download_path

            allure.attach(
                f"触发元素: {trigger_selector}\n"
                f"下载文件: {download_path}\n"
                f"文件大小: {file_size} 字节\n"
                f"建议文件名: {download.suggested_filename}\n"
                f"保存变量: {variable or '无'}",
                name="文件下载信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"文件下载成功: {download_path} ({file_size} 字节)")

            # 保存到变量
            if variable and context:
                context.set(variable, download_path)

            # 直接返回下载文件路径
            return download_path

        except Exception as e:
            logger.error(f"文件下载失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="文件下载失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('监听下载', [
    {'name': '监听时间', 'mapping': 'listen_duration', 
     'description': '监听下载的时间（秒）', 'default': 10},
    {'name': '保存目录', 'mapping': 'save_directory', 
     'description': '下载文件保存目录，不指定则使用默认下载目录'},
    {'name': '变量名', 'mapping': 'variable', 
     'description': '保存下载文件列表的变量名'},
], category='UI/下载')
def monitor_downloads(**kwargs):
    """监听页面下载事件

    Args:
        listen_duration: 监听时间（秒）
        save_directory: 保存目录
        variable: 变量名

    Returns:
        dict: 包含下载文件列表的字典
    """
    listen_duration = kwargs.get('listen_duration', 10)
    save_directory = kwargs.get('save_directory')
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    with allure.step(f"监听下载 {listen_duration} 秒"):
        try:
            page = browser_manager.get_current_page()
            downloaded_files = []
            
            # 确定保存目录
            if save_directory:
                downloads_dir = Path(save_directory)
            else:
                downloads_dir = Path("downloads")
            downloads_dir.mkdir(exist_ok=True, parents=True)

            def handle_download(download):
                try:
                    # 生成文件名
                    suggested_name = download.suggested_filename
                    if suggested_name:
                        filename = safe_filename(suggested_name)
                    else:
                        filename = generate_timestamp_filename("download", extension="bin")
                    
                    file_path = downloads_dir / filename
                    
                    # 保存文件
                    download.save_as(str(file_path))
                    
                    file_info = {
                        "path": str(file_path.absolute()),
                        "filename": filename,
                        "suggested_filename": suggested_name,
                        "url": download.url,
                        "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                        "timestamp": time.time()
                    }
                    
                    downloaded_files.append(file_info)
                    logger.info(f"捕获下载: {filename} ({file_info['size']} 字节)")
                    
                except Exception as e:
                    logger.error(f"处理下载失败: {str(e)}")

            # 注册下载事件监听器
            page.on("download", handle_download)
            
            # 等待指定时间
            time.sleep(listen_duration)
            
            # 移除监听器
            page.remove_listener("download", handle_download)

            # 保存到变量
            captures = {}
            if variable and context:
                context.set(variable, downloaded_files)
                captures[variable] = downloaded_files

            allure.attach(
                f"监听时间: {listen_duration} 秒\n"
                f"保存目录: {downloads_dir}\n"
                f"下载文件数: {len(downloaded_files)}\n"
                f"文件列表: {[f['filename'] for f in downloaded_files]}\n"
                f"保存变量: {variable or '无'}",
                name="下载监听信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"下载监听完成: 捕获 {len(downloaded_files)} 个文件")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": downloaded_files,
                "captures": captures,
                "session_state": {},
                "metadata": {
                    "listen_duration": listen_duration,
                    "save_directory": str(downloads_dir),
                    "file_count": len(downloaded_files),
                    "operation": "monitor_downloads"
                }
            }

        except Exception as e:
            logger.error(f"下载监听失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="下载监听失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('验证下载文件', [
    {'name': '文件路径', 'mapping': 'file_path', 
     'description': '要验证的文件路径'},
    {'name': '最小文件大小', 'mapping': 'min_size', 
     'description': '最小文件大小（字节）', 'default': 0},
    {'name': '最大文件大小', 'mapping': 'max_size', 
     'description': '最大文件大小（字节）'},
    {'name': '文件扩展名', 'mapping': 'expected_extension', 
     'description': '期望的文件扩展名'},
], category='UI/下载')
def verify_downloaded_file(**kwargs):
    """验证下载的文件

    Args:
        file_path: 文件路径
        min_size: 最小文件大小
        max_size: 最大文件大小
        expected_extension: 期望的文件扩展名

    Returns:
        dict: 验证结果
    """
    file_path = kwargs.get('file_path')
    min_size = kwargs.get('min_size', 0)
    max_size = kwargs.get('max_size')
    expected_extension = kwargs.get('expected_extension')

    if not file_path:
        raise ValueError("文件路径不能为空")

    with allure.step(f"验证下载文件: {file_path}"):
        try:
            file_path = Path(file_path)
            
            # 检查文件是否存在
            if not file_path.exists():
                raise AssertionError(f"文件不存在: {file_path}")
            
            # 检查是否为文件
            if not file_path.is_file():
                raise AssertionError(f"路径不是文件: {file_path}")
            
            # 获取文件信息
            file_size = file_path.stat().st_size
            file_extension = file_path.suffix.lower()
            
            # 验证文件大小
            if file_size < min_size:
                raise AssertionError(
                    f"文件太小: {file_size} 字节 < {min_size} 字节"
                )
            
            if max_size and file_size > max_size:
                raise AssertionError(
                    f"文件太大: {file_size} 字节 > {max_size} 字节"
                )
            
            # 验证文件扩展名
            if expected_extension:
                if not expected_extension.startswith('.'):
                    expected_extension = '.' + expected_extension
                if file_extension != expected_extension.lower():
                    raise AssertionError(
                        f"文件扩展名不匹配: {file_extension} != {expected_extension}"
                    )

            file_info = {
                "path": str(file_path.absolute()),
                "size": file_size,
                "extension": file_extension,
                "exists": True,
                "valid": True
            }

            allure.attach(
                f"文件路径: {file_path}\n"
                f"文件大小: {file_size} 字节\n"
                f"文件扩展名: {file_extension}\n"
                f"验证结果: 通过",
                name="文件验证信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"文件验证成功: {file_path}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": file_info,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "file_path": str(file_path),
                    "validation_passed": True,
                    "operation": "verify_downloaded_file"
                }
            }

        except Exception as e:
            logger.error(f"文件验证失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="文件验证失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('清理下载文件', [
    {'name': '下载目录', 'mapping': 'download_directory', 
     'description': '要清理的下载目录', 'default': 'downloads'},
    {'name': '文件模式', 'mapping': 'file_pattern', 
     'description': '要删除的文件模式（如 *.pdf）'},
    {'name': '保留天数', 'mapping': 'keep_days', 
     'description': '保留最近几天的文件', 'default': 0},
], category='UI/下载')
def cleanup_downloads(**kwargs):
    """清理下载文件

    Args:
        download_directory: 下载目录
        file_pattern: 文件模式
        keep_days: 保留天数

    Returns:
        dict: 清理结果
    """
    download_directory = kwargs.get('download_directory', 'downloads')
    file_pattern = kwargs.get('file_pattern', '*')
    keep_days = kwargs.get('keep_days', 0)

    with allure.step(f"清理下载文件: {download_directory}"):
        try:
            downloads_dir = Path(download_directory)
            
            if not downloads_dir.exists():
                logger.warning(f"下载目录不存在: {downloads_dir}")
                return {
                    "result": {"deleted_count": 0, "total_size": 0},
                    "captures": {},
                    "session_state": {},
                    "metadata": {
                        "directory": str(downloads_dir),
                        "operation": "cleanup_downloads"
                    }
                }
            
            # 获取要删除的文件
            files_to_delete = list(downloads_dir.glob(file_pattern))
            
            # 按时间过滤
            if keep_days > 0:
                cutoff_time = time.time() - (keep_days * 24 * 3600)
                files_to_delete = [
                    f for f in files_to_delete 
                    if f.stat().st_mtime < cutoff_time
                ]
            
            # 只保留文件（不删除目录）
            files_to_delete = [f for f in files_to_delete if f.is_file()]
            
            deleted_count = 0
            total_size = 0
            
            for file_path in files_to_delete:
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_count += 1
                    total_size += file_size
                    logger.debug(f"删除文件: {file_path}")
                except Exception as e:
                    logger.warning(f"删除文件失败 {file_path}: {str(e)}")

            cleanup_result = {
                "deleted_count": deleted_count,
                "total_size": total_size,
                "directory": str(downloads_dir),
                "pattern": file_pattern,
                "keep_days": keep_days
            }

            allure.attach(
                f"下载目录: {downloads_dir}\n"
                f"文件模式: {file_pattern}\n"
                f"保留天数: {keep_days}\n"
                f"删除文件数: {deleted_count}\n"
                f"释放空间: {total_size} 字节",
                name="清理下载文件信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"清理下载文件完成: 删除 {deleted_count} 个文件，释放 {total_size} 字节")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": cleanup_result,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "directory": str(downloads_dir),
                    "deleted_count": deleted_count,
                    "operation": "cleanup_downloads"
                }
            }

        except Exception as e:
            logger.error(f"清理下载文件失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="清理下载文件失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise 