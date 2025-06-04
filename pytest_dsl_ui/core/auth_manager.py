"""认证状态管理器

基于Playwright的storage_state功能，提供登录状态的保存和重用机制。
参考: https://playwright.net.cn/python/docs/auth
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.sync_api import BrowserContext

logger = logging.getLogger(__name__)


class AuthManager:
    """认证状态管理器

    提供登录状态的保存、加载和重用功能。
    """

    def __init__(self, auth_dir: str = "playwright/.auth"):
        """初始化认证管理器

        Args:
            auth_dir: 认证状态文件存储目录
        """
        self.auth_dir = Path(auth_dir)
        self.auth_dir.mkdir(parents=True, exist_ok=True)

        # 确保.gitignore包含认证目录
        self._ensure_gitignore()

    def _ensure_gitignore(self):
        """确保.gitignore包含认证目录"""
        gitignore_path = Path(".gitignore")
        auth_pattern = str(self.auth_dir)

        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if auth_pattern not in content:
                with open(gitignore_path, 'a', encoding='utf-8') as f:
                    f.write(f"\n# Playwright认证状态文件\n{auth_pattern}\n")
                logger.info(f"已将 {auth_pattern} 添加到 .gitignore")
        else:
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(f"# Playwright认证状态文件\n{auth_pattern}\n")
            logger.info(f"已创建 .gitignore 并添加 {auth_pattern}")

    def save_auth_state(self, context: BrowserContext,
                        state_name: str,
                        metadata: Optional[Dict[str, Any]] = None,
                        include_indexed_db: bool = True) -> str:
        """保存认证状态

        Args:
            context: 已认证的浏览器上下文
            state_name: 状态名称（用于标识不同的认证状态）
            metadata: 元数据（如用户名、网站信息等）
            include_indexed_db: 是否包含IndexedDB数据（Playwright 1.20+支持）

        Returns:
            str: 状态文件路径
        """
        try:
            # 生成状态文件路径
            state_file = self.auth_dir / f"{state_name}.json"

            # 保存存储状态 - 根据Playwright版本支持IndexedDB
            try:
                if include_indexed_db:
                    # 尝试使用IndexedDB选项（需要Playwright 1.20+）
                    storage_state = context.storage_state(indexed_db=True)
                    logger.info("使用IndexedDB支持保存认证状态")
                else:
                    storage_state = context.storage_state()
                    logger.info("使用标准方式保存认证状态")
            except TypeError as te:
                # 旧版本Playwright不支持indexed_db参数
                logger.warning(f"当前Playwright版本不支持IndexedDB选项: {str(te)}")
                storage_state = context.storage_state()
            except Exception as e:
                logger.error(f"获取存储状态失败: {str(e)}")
                raise

            # 添加元数据
            if metadata:
                storage_state["metadata"] = metadata
            
            # 确保保存时间戳
            storage_state["saved_at"] = self._get_timestamp()
            
            # 添加IndexedDB标识
            storage_state["include_indexed_db"] = include_indexed_db

            # 添加统计信息到元数据
            stats = {
                "cookies_count": len(storage_state.get("cookies", [])),
                "origins_count": len(storage_state.get("origins", [])),
                "file_path": str(state_file)
            }
            
            if "metadata" not in storage_state:
                storage_state["metadata"] = {}
            storage_state["metadata"].update(stats)

            # 写入文件
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(storage_state, f, indent=2, ensure_ascii=False)

            logger.info(f"认证状态已保存: {state_file} (cookies: {stats['cookies_count']}, origins: {stats['origins_count']})")
            return str(state_file)

        except Exception as e:
            logger.error(f"保存认证状态失败: {str(e)}")
            raise

    def load_auth_state(self, state_name: str) -> Optional[Dict[str, Any]]:
        """加载认证状态

        Args:
            state_name: 状态名称

        Returns:
            Optional[Dict[str, Any]]: 认证状态数据，如果不存在则返回None
        """
        try:
            state_file = self.auth_dir / f"{state_name}.json"

            if not state_file.exists():
                logger.warning(f"认证状态文件不存在: {state_file}")
                return None

            with open(state_file, 'r', encoding='utf-8') as f:
                storage_state = json.load(f)

            logger.info(f"认证状态已加载: {state_file}")
            return storage_state

        except Exception as e:
            logger.error(f"加载认证状态失败: {str(e)}")
            return None

    def has_auth_state(self, state_name: str) -> bool:
        """检查认证状态是否存在

        Args:
            state_name: 状态名称

        Returns:
            bool: 是否存在
        """
        state_file = self.auth_dir / f"{state_name}.json"
        return state_file.exists()

    def delete_auth_state(self, state_name: str) -> bool:
        """删除认证状态

        Args:
            state_name: 状态名称

        Returns:
            bool: 删除是否成功
        """
        try:
            state_file = self.auth_dir / f"{state_name}.json"

            if state_file.exists():
                state_file.unlink()
                logger.info(f"认证状态已删除: {state_file}")
                return True
            else:
                logger.warning(f"认证状态文件不存在: {state_file}")
                return False

        except Exception as e:
            logger.error(f"删除认证状态失败: {str(e)}")
            return False

    def list_auth_states(self) -> Dict[str, Dict[str, Any]]:
        """列出所有认证状态

        Returns:
            Dict[str, Dict[str, Any]]: 状态名称到元数据的映射
        """
        states = {}

        try:
            for state_file in self.auth_dir.glob("*.json"):
                state_name = state_file.stem

                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    metadata = data.get("metadata", {})
                    metadata["file_path"] = str(state_file)
                    metadata["file_size"] = state_file.stat().st_size

                    states[state_name] = metadata

                except Exception as e:
                    logger.warning(f"无法读取状态文件 {state_file}: {str(e)}")

        except Exception as e:
            logger.error(f"列出认证状态失败: {str(e)}")

        return states

    def cleanup_expired_states(self, max_age_days: int = 30):
        """清理过期的认证状态

        Args:
            max_age_days: 最大保存天数
        """
        import time

        try:
            current_time = time.time()
            cutoff_time = current_time - (max_age_days * 24 * 60 * 60)

            deleted_count = 0
            for state_file in self.auth_dir.glob("*.json"):
                file_mtime = state_file.stat().st_mtime

                if file_mtime < cutoff_time:
                    state_file.unlink()
                    deleted_count += 1
                    logger.info(f"已删除过期认证状态: {state_file}")

            if deleted_count > 0:
                logger.info(f"清理完成，删除了 {deleted_count} 个过期认证状态")
            else:
                logger.info("没有过期的认证状态需要清理")

        except Exception as e:
            logger.error(f"清理过期认证状态失败: {str(e)}")

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()


# 全局认证管理器实例
auth_manager = AuthManager()
