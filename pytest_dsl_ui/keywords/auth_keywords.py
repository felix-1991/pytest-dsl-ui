"""认证相关关键字

提供认证状态保存、加载、检查和清除等功能。
基于Playwright的storage_state机制实现认证状态重用。
登录逻辑由DSL脚本自定义实现，以适应不同系统的登录方式。
"""

import logging
import allure

from pytest_dsl.core.keyword_manager import keyword_manager
from ..core.browser_manager import browser_manager
from ..core.auth_manager import auth_manager

logger = logging.getLogger(__name__)


@keyword_manager.register('加载认证状态', [
    {'name': '状态名称', 'mapping': 'state_name', 'description': '要加载的认证状态名称'},
    {'name': '创建新上下文', 'mapping': 'new_context',
     'description': '是否创建新的浏览器上下文', 'default': True},
    {'name': '创建新页面', 'mapping': 'create_new_page',
     'description': '是否创建新页面（仅在创建新上下文时有效）', 'default': False},
    {'name': '验证登录', 'mapping': 'verify_login',
     'description': '是否验证登录状态', 'default': True},
], category='UI/认证', tags=['加载', '状态'])
def load_auth_state(**kwargs):
    """加载保存的认证状态

    Args:
        state_name: 认证状态名称
        new_context: 是否创建新的浏览器上下文
        create_new_page: 是否创建新页面（仅在创建新上下文时有效）
        verify_login: 是否验证登录状态

    Returns:
        dict: 操作结果
    """
    state_name = kwargs.get('state_name')
    new_context = kwargs.get('new_context', True)
    create_new_page = kwargs.get('create_new_page', False)
    verify_login = kwargs.get('verify_login', True)
    context = kwargs.get('context')

    if not state_name:
        raise ValueError("状态名称参数不能为空")

    with allure.step(f"加载认证状态: {state_name}"):
        try:
            # 检查认证状态是否存在
            if not auth_manager.has_auth_state(state_name):
                raise ValueError(f"认证状态不存在: {state_name}")

            # 加载认证状态
            storage_state = auth_manager.load_auth_state(state_name)
            if not storage_state:
                raise ValueError(f"无法加载认证状态: {state_name}")

            # 验证storage_state结构
            if not isinstance(storage_state, dict):
                raise ValueError(f"认证状态格式无效: {state_name}")

            # 确保必要的字段存在
            if 'cookies' not in storage_state:
                storage_state['cookies'] = []
            if 'origins' not in storage_state:
                storage_state['origins'] = []

            # 获取当前浏览器ID
            current_browser_id = browser_manager.current_browser
            if not current_browser_id:
                raise ValueError("没有可用的浏览器实例")

            # 创建新的浏览器上下文（包含认证状态）
            if new_context:
                # 准备上下文配置 - 增加更多选项支持
                context_config = {
                    "storage_state": storage_state,
                    "ignore_https_errors": True,  # 默认支持HTTPS证书忽略，避免后续打开页面时重新创建上下文
                    # 考虑是否包含其他浏览器配置
                }

                # 如果storage_state包含viewport信息，也可以设置
                if 'viewport' in storage_state:
                    context_config['viewport'] = storage_state['viewport']

                # 创建新上下文
                context_id = browser_manager.create_context(
                    current_browser_id, **context_config
                )

                # 智能页面管理：检查是否需要创建新页面
                page_id = None
                if create_new_page:
                    # 用户明确要求创建新页面
                    page_id = browser_manager.create_page(context_id)
                    logger.info(f"已创建新页面: {page_id}")
                else:
                    # 检查新上下文是否已有页面
                    new_context_obj = browser_manager.get_context(context_id)
                    existing_pages = new_context_obj.pages

                    if existing_pages:
                        # 使用上下文中的第一个页面
                        existing_page = existing_pages[0]
                        # 为现有页面生成ID并注册到browser_manager
                        page_id = f"{context_id}_page_existing"
                        browser_manager.pages[page_id] = existing_page
                        logger.info(f"复用上下文中的现有页面: {page_id}")
                    else:
                        # 上下文中没有页面，创建一个
                        page_id = browser_manager.create_page(context_id)
                        logger.info(f"上下文中无页面，已创建新页面: {page_id}")

                # 切换到目标页面
                browser_manager.switch_page(page_id)

                # 更新测试上下文
                if context:
                    context.set('current_context_id', context_id)
                    context.set('current_page_id', page_id)

                # 可选：验证登录状态
                if verify_login:
                    try:
                        page = browser_manager.get_current_page()
                        # 等待页面加载完成
                        page.wait_for_load_state(
                            'domcontentloaded', timeout=10000)

                        # 检查是否有有效的认证状态（通过检查cookies）
                        current_cookies = page.context.cookies()
                        if not current_cookies:
                            logger.warning(
                                f"加载认证状态后未发现任何cookies: {state_name}")
                        else:
                            logger.info(
                                f"认证状态验证成功，发现 {len(current_cookies)} 个cookies")

                    except Exception as verify_error:
                        logger.warning(f"验证登录状态时出现警告: {str(verify_error)}")
                        # 验证失败不应该阻止整个流程

                logger.info(f"已创建新上下文并加载认证状态: {state_name} (页面策略: {'新建' if create_new_page else '智能复用'})")
            else:
                logger.warning("当前不支持在现有上下文中加载认证状态")

            # 获取元数据 - 改进元数据获取逻辑
            metadata = storage_state.get("metadata", {})

            # 如果metadata为空，尝试从其他地方获取信息
            if not metadata:
                # 尝试从cookies中推断一些信息
                cookies = storage_state.get("cookies", [])
                if cookies:
                    # 获取第一个cookie的域名作为参考
                    first_cookie = cookies[0] if cookies else {}
                    metadata = {
                        "domain": first_cookie.get("domain", "未知"),
                        "cookies_count": len(cookies),
                        "loaded_at": "刚刚"
                    }

            allure.attach(
                f"状态名称: {state_name}\n"
                f"用户名: {metadata.get('username', '未知')}\n"
                f"保存时间: {metadata.get('saved_at', '未知')}\n"
                f"保存URL: {metadata.get('url', '未知')}\n"
                f"Cookies数量: {len(storage_state.get('cookies', []))}\n"
                f"Origins数量: {len(storage_state.get('origins', []))}\n"
                f"创建新上下文: {new_context}\n"
                f"页面管理策略: {'强制创建新页面' if create_new_page else '智能复用现有页面'}\n"
                f"验证登录: {verify_login}",
                name="认证状态加载信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"认证状态加载成功: {state_name}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": True,
                "captures": {
                    "auth_loaded": True,
                    "state_name": state_name,
                    "metadata": metadata,
                    "cookies_count": len(storage_state.get('cookies', [])),
                    "origins_count": len(storage_state.get('origins', []))
                },
                "session_state": {},
                "metadata": {
                    "state_name": state_name,
                    "metadata": metadata,
                    "storage_info": {
                        "cookies_count": len(storage_state.get('cookies', [])),
                        "origins_count": len(storage_state.get('origins', []))
                    },
                    "operation": "load_auth_state"
                }
            }

        except Exception as e:
            logger.error(f"加载认证状态失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}\n"
                f"状态名称: {state_name}",
                name="认证状态加载失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('保存认证状态', [
    {'name': '状态名称', 'mapping': 'state_name', 'description': '认证状态名称'},
    {'name': '用户名', 'mapping': 'username', 'description': '用户名（元数据）'},
    {'name': '描述', 'mapping': 'description', 'description': '状态描述（元数据）'},
    {'name': '包含IndexedDB', 'mapping': 'include_indexed_db',
     'description': '是否包含IndexedDB数据', 'default': True},
], category='UI/认证', tags=['保存', '状态'])
def save_auth_state(**kwargs):
    """保存当前的认证状态

    Args:
        state_name: 认证状态名称
        username: 用户名
        description: 状态描述
        include_indexed_db: 是否包含IndexedDB数据

    Returns:
        dict: 操作结果
    """
    state_name = kwargs.get('state_name')
    username = kwargs.get('username')
    description = kwargs.get('description')
    include_indexed_db = kwargs.get('include_indexed_db', True)

    if not state_name:
        raise ValueError("状态名称参数不能为空")

    with allure.step(f"保存认证状态: {state_name}"):
        try:
            page = browser_manager.get_current_page()
            browser_context = page.context

            # 准备元数据 - 增强元数据收集
            import datetime
            current_time = datetime.datetime.now().isoformat()

            metadata = {
                "url": page.url,
                "description": description,
                "saved_at": current_time,
                "user_agent": page.evaluate("navigator.userAgent"),
                "viewport": page.viewport_size,
                "include_indexed_db": include_indexed_db
            }

            if username:
                metadata["username"] = username

            # 获取当前页面的基本信息
            try:
                title = page.title()
                metadata["page_title"] = title
            except Exception:
                metadata["page_title"] = "未知"

            # 保存认证状态 - 根据Playwright最佳实践
            # 注意：这里需要确保auth_manager支持indexed_db参数
            try:
                # 尝试使用IndexedDB支持（如果可用）
                state_path = auth_manager.save_auth_state(
                    browser_context, state_name, metadata,
                    include_indexed_db=include_indexed_db
                )
            except TypeError:
                # 如果auth_manager不支持include_indexed_db参数，使用原有方式
                logger.warning("auth_manager不支持IndexedDB参数，使用标准方式保存")
                state_path = auth_manager.save_auth_state(
                    browser_context, state_name, metadata
                )

            # 验证保存的状态
            if auth_manager.has_auth_state(state_name):
                # 获取保存后的状态信息进行验证
                saved_state = auth_manager.load_auth_state(state_name)
                if saved_state:
                    cookies_count = len(saved_state.get('cookies', []))
                    origins_count = len(saved_state.get('origins', []))
                    logger.info(
                        f"认证状态保存验证成功: cookies={cookies_count}, "
                        f"origins={origins_count}")

                    # 更新metadata中的统计信息
                    metadata.update({
                        "cookies_count": cookies_count,
                        "origins_count": origins_count
                    })
                else:
                    logger.warning("保存后无法读取认证状态，可能存在问题")
            else:
                logger.warning("保存后认证状态验证失败")

            allure.attach(
                f"状态名称: {state_name}\n"
                f"用户名: {username or '未提供'}\n"
                f"描述: {description or '无'}\n"
                f"当前URL: {page.url}\n"
                f"页面标题: {metadata.get('page_title', '未知')}\n"
                f"保存时间: {current_time}\n"
                f"包含IndexedDB: {include_indexed_db}\n"
                f"Cookies数量: {metadata.get('cookies_count', '未知')}\n"
                f"Origins数量: {metadata.get('origins_count', '未知')}\n"
                f"保存路径: {state_path}",
                name="认证状态保存信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"认证状态保存成功: {state_name}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": state_path,
                "captures": {
                    "state_saved": True,
                    "state_name": state_name,
                    "state_path": state_path,
                    "metadata": metadata
                },
                "session_state": {},
                "metadata": {
                    "state_name": state_name,
                    "state_path": state_path,
                    "metadata": metadata,
                    "include_indexed_db": include_indexed_db,
                    "operation": "save_auth_state"
                }
            }

        except Exception as e:
            logger.error(f"保存认证状态失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}\n"
                f"状态名称: {state_name}\n"
                f"当前URL: {page.url if 'page' in locals() else '未知'}",
                name="认证状态保存失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('检查认证状态', [
    {'name': '状态名称', 'mapping': 'state_name', 'description': '要检查的认证状态名称'},
], category='UI/认证', tags=['检查', '状态'])
def check_auth_state(**kwargs):
    """检查认证状态是否存在

    Args:
        state_name: 认证状态名称

    Returns:
        dict: 包含检查结果的字典
    """
    state_name = kwargs.get('state_name')

    if not state_name:
        raise ValueError("状态名称参数不能为空")

    with allure.step(f"检查认证状态: {state_name}"):
        try:
            exists = auth_manager.has_auth_state(state_name)

            # 如果存在，获取更多信息
            metadata = {}
            if exists:
                storage_state = auth_manager.load_auth_state(state_name)
                if storage_state:
                    metadata = storage_state.get("metadata", {})

            allure.attach(
                f"状态名称: {state_name}\n"
                f"存在状态: {exists}\n"
                f"用户名: {metadata.get('username', '未知')}\n"
                f"保存时间: {metadata.get('saved_at', '未知')}\n"
                f"URL: {metadata.get('url', '未知')}",
                name="认证状态检查信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"认证状态检查完成: {state_name} -> {exists}")

            # 直接返回检查结果
            return exists

        except Exception as e:
            logger.error(f"检查认证状态失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="认证状态检查失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('删除认证状态', [
    {'name': '状态名称', 'mapping': 'state_name', 'description': '要删除的认证状态名称'},
], category='UI/认证', tags=['删除', '状态'])
def delete_auth_state(**kwargs):
    """删除认证状态

    Args:
        state_name: 认证状态名称

    Returns:
        dict: 操作结果
    """
    state_name = kwargs.get('state_name')

    if not state_name:
        raise ValueError("状态名称参数不能为空")

    with allure.step(f"删除认证状态: {state_name}"):
        try:
            success = auth_manager.delete_auth_state(state_name)

            allure.attach(
                f"状态名称: {state_name}\n"
                f"删除结果: {'成功' if success else '失败（状态不存在）'}",
                name="认证状态删除信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"认证状态删除{'成功' if success else '失败'}: {state_name}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": success,
                "captures": {
                    "delete_success": success,
                    "state_name": state_name
                },
                "session_state": {},
                "metadata": {
                    "state_name": state_name,
                    "success": success,
                    "operation": "delete_auth_state"
                }
            }

        except Exception as e:
            logger.error(f"删除认证状态失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="认证状态删除失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('列出认证状态', [
    {'name': '变量名', 'mapping': 'variable', 'description': '保存状态列表的变量名'},
], category='UI/认证', tags=['列表', '状态'])
def list_auth_states(**kwargs):
    """列出所有认证状态

    Args:
        variable: 变量名

    Returns:
        dict: 包含状态列表的字典
    """
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    with allure.step("列出认证状态"):
        try:
            states = auth_manager.list_auth_states()

            # 保存到变量
            captures = {}
            if variable and context:
                context.set(variable, states)
                captures[variable] = states

            # 准备显示信息
            states_info = []
            for state_name, metadata in states.items():
                states_info.append(
                    f"- {state_name}: {metadata.get('username', '未知')} "
                    f"({metadata.get('saved_at', '未知时间')})"
                )

            allure.attach(
                f"认证状态数量: {len(states)}\n"
                f"状态列表:\n" + (
                    "\n".join(states_info) if states_info else "无认证状态"
                ) + "\n"
                f"保存变量: {variable or '无'}",
                name="认证状态列表",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"列出认证状态完成，共 {len(states)} 个状态")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": states,
                "captures": captures,
                "session_state": {},
                "metadata": {
                    "states_count": len(states),
                    "operation": "list_auth_states"
                }
            }

        except Exception as e:
            logger.error(f"列出认证状态失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="列出认证状态失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('清除认证状态', [
    {'name': '状态名称', 'mapping': 'state_name', 'description': '要清除的认证状态名称'},
], category='UI/认证', tags=['清除', '状态'])
def clear_auth_state(**kwargs):
    """清除指定的认证状态

    Args:
        state_name: 认证状态名称

    Returns:
        dict: 操作结果
    """
    state_name = kwargs.get('state_name')

    if not state_name:
        raise ValueError("状态名称参数不能为空")

    with allure.step(f"清除认证状态: {state_name}"):
        try:
            # 检查状态是否存在
            exists = auth_manager.has_auth_state(state_name)

            if not exists:
                logger.warning(f"认证状态不存在: {state_name}")

            # 删除认证状态
            success = auth_manager.delete_auth_state(state_name)

            allure.attach(
                f"状态名称: {state_name}\n"
                f"原始存在状态: {exists}\n"
                f"清除结果: {'成功' if success else '失败（状态不存在）'}",
                name="认证状态清除信息",
                attachment_type=allure.attachment_type.TEXT
            )

            if success:
                logger.info(f"认证状态已清除: {state_name}")
            else:
                logger.warning(f"认证状态清除失败: {state_name}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": success,
                "captures": {
                    "clear_success": success,
                    "state_name": state_name,
                    "was_exists": exists
                },
                "session_state": {},
                "metadata": {
                    "state_name": state_name,
                    "success": success,
                    "was_exists": exists,
                    "operation": "clear_auth_state"
                }
            }

        except Exception as e:
            logger.error(f"清除认证状态失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="认证状态清除失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('清除所有认证状态', [
    {'name': '确认清除', 'mapping': 'confirm_clear',
        'description': '确认清除所有状态', 'default': False},
], category='UI/认证', tags=['清除', '全部'])
def clear_all_auth_states(**kwargs):
    """清除所有认证状态

    Args:
        confirm_clear: 确认清除所有状态，防止误操作

    Returns:
        dict: 操作结果
    """
    confirm_clear = kwargs.get('confirm_clear', False)

    if not confirm_clear:
        raise ValueError("请设置 '确认清除: True' 来确认清除所有认证状态")

    with allure.step("清除所有认证状态"):
        try:
            # 先获取所有状态
            states = auth_manager.list_auth_states()
            states_count = len(states)

            if states_count == 0:
                logger.info("没有认证状态需要清除")

                allure.attach(
                    "没有认证状态需要清除",
                    name="认证状态清除信息",
                    attachment_type=allure.attachment_type.TEXT
                )

                return {
                    "result": True,
                    "captures": {
                        "cleared_count": 0,
                        "total_count": 0
                    },
                    "session_state": {},
                    "metadata": {
                        "cleared_count": 0,
                        "total_count": 0,
                        "operation": "clear_all_auth_states"
                    }
                }

            # 清除所有状态
            cleared_count = 0
            failed_states = []

            for state_name in states.keys():
                try:
                    success = auth_manager.delete_auth_state(state_name)
                    if success:
                        cleared_count += 1
                        logger.info(f"已清除认证状态: {state_name}")
                    else:
                        failed_states.append(state_name)
                        logger.warning(f"清除认证状态失败: {state_name}")
                except Exception as e:
                    failed_states.append(state_name)
                    logger.error(f"清除认证状态 {state_name} 时发生错误: {str(e)}")

            # 准备结果信息
            failed_count = len(failed_states)
            success_overall = failed_count == 0

            result_info = [
                f"总共状态数: {states_count}",
                f"成功清除: {cleared_count}",
                f"清除失败: {failed_count}"
            ]

            if failed_states:
                result_info.append(f"失败的状态: {', '.join(failed_states)}")

            allure.attach(
                "\n".join(result_info),
                name="所有认证状态清除结果",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"认证状态清除完成: 成功 {cleared_count}/{states_count}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": success_overall,
                "captures": {
                    "cleared_count": cleared_count,
                    "failed_count": failed_count,
                    "total_count": states_count,
                    "failed_states": failed_states,
                    "success_overall": success_overall
                },
                "session_state": {},
                "metadata": {
                    "cleared_count": cleared_count,
                    "failed_count": failed_count,
                    "total_count": states_count,
                    "failed_states": failed_states,
                    "operation": "clear_all_auth_states"
                }
            }

        except Exception as e:
            logger.error(f"清除所有认证状态失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="清除所有认证状态失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
