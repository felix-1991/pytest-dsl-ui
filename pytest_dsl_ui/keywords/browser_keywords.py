"""浏览器操作关键字

提供浏览器启动、关闭、页面切换等基础功能。
"""

import logging
import yaml
import allure
import time as time_module
import urllib.parse

from pytest_dsl.core.keyword_manager import keyword_manager
from ..core.browser_manager import browser_manager

logger = logging.getLogger(__name__)


@keyword_manager.register('启动浏览器', [
    {'name': '浏览器', 'mapping': 'browser_type',
        'description': '浏览器类型：chromium, firefox, webkit', 'default': 'chromium'},
    {'name': '无头模式', 'mapping': 'headless',
     'description': '是否以无头模式运行', 'default': False},
    {'name': '慢动作', 'mapping': 'slow_mo',
     'description': '操作间隔时间（毫秒），用于调试', 'default': 0},
    {'name': '配置', 'mapping': 'config',
     'description': '浏览器启动配置（YAML格式）', 'default': '{}'},
    {'name': '视口宽度', 'mapping': 'width', 'description': '浏览器视口宽度'},
    {'name': '视口高度', 'mapping': 'height', 'description': '浏览器视口高度'},
    {'name': '忽略证书错误', 'mapping': 'ignore_https_errors',
     'description': '是否忽略HTTPS证书错误', 'default': True},
], category='UI/浏览器', tags=['启动', '配置'])
def launch_browser(**kwargs):
    """启动浏览器

    Args:
        browser_type: 浏览器类型
        headless: 是否无头模式
        slow_mo: 慢动作间隔
        config: 配置字符串
        width: 视口宽度
        height: 视口高度
        ignore_https_errors: 是否忽略HTTPS证书错误

    Returns:
        dict: 包含浏览器ID和相关信息的字典
    """
    browser_type = kwargs.get('browser_type', 'chromium')
    headless = kwargs.get('headless', True)
    slow_mo = kwargs.get('slow_mo', 0)
    config_str = kwargs.get('config', '{}')
    width = kwargs.get('width')
    height = kwargs.get('height')
    ignore_https_errors = kwargs.get('ignore_https_errors', True)
    context = kwargs.get('context')

    with allure.step(f"启动浏览器: {browser_type}"):
        try:
            # 解析配置
            if isinstance(config_str, str):
                try:
                    config = yaml.safe_load(
                        config_str) if config_str.strip() else {}
                except yaml.YAMLError:
                    # 尝试作为JSON解析
                    import json
                    config = json.loads(
                        config_str) if config_str.strip() else {}
            else:
                config = config_str or {}

            # 设置基本配置
            launch_config = {
                'headless': headless,
                'slow_mo': slow_mo,
                **config
            }

            # 启动浏览器
            browser_id = browser_manager.launch_browser(
                browser_type, **launch_config)

            # 创建默认上下文
            context_config = {}
            if width and height:
                context_config['viewport'] = {
                    'width': int(width), 'height': int(height)}
            elif 'viewport' in config:
                context_config['viewport'] = config['viewport']

            # 添加忽略HTTPS证书错误的配置
            if ignore_https_errors:
                context_config['ignore_https_errors'] = True

            context_id = browser_manager.create_context(
                browser_id, **context_config)

            # 创建默认页面
            page_id = browser_manager.create_page(context_id)

            result = {
                'browser_id': browser_id,
                'context_id': context_id,
                'page_id': page_id
            }

            # 在测试上下文中保存浏览器信息
            if context:
                context.set('current_browser_id', browser_id)
                context.set('current_context_id', context_id)
                context.set('current_page_id', page_id)

            allure.attach(
                f"浏览器类型: {browser_type}\n"
                f"浏览器ID: {browser_id}\n"
                f"上下文ID: {context_id}\n"
                f"页面ID: {page_id}\n"
                f"无头模式: {headless}\n"
                f"忽略HTTPS证书错误: {ignore_https_errors}",
                name="浏览器启动信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"浏览器启动成功: {browser_type} (ID: {browser_id})")

            # 保存重要信息到上下文
            if context:
                context.set('current_browser_id', browser_id)
                context.set('current_context_id', context_id)
                context.set('current_page_id', page_id)

            # 直接返回浏览器信息
            return {
                "browser_id": browser_id,
                "context_id": context_id,
                "page_id": page_id
            }

        except Exception as e:
            logger.error(f"启动浏览器失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="浏览器启动失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('关闭浏览器', [
    {'name': '浏览器ID', 'mapping': 'browser_id',
        'description': '要关闭的浏览器ID，如果不指定则关闭当前浏览器'},
], category='UI/浏览器', tags=['关闭'])
def close_browser(**kwargs):
    """关闭浏览器

    Args:
        browser_id: 浏览器ID

    Returns:
        dict: 操作结果
    """
    browser_id = kwargs.get('browser_id')
    context = kwargs.get('context')

    with allure.step("关闭浏览器"):
        try:
            # 如果没有指定浏览器ID，从上下文获取
            if not browser_id and context:
                browser_id = context.get('current_browser_id')

            browser_manager.close_browser(browser_id)

            # 清理上下文中的浏览器信息
            if context:
                context.set('current_browser_id', None)
                context.set('current_context_id', None)
                context.set('current_page_id', None)

            allure.attach(
                f"已关闭浏览器: {browser_id or '当前浏览器'}",
                name="浏览器关闭信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"浏览器关闭成功: {browser_id or '当前浏览器'}")

            # 直接返回成功状态
            return True

        except Exception as e:
            logger.error(f"关闭浏览器失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="浏览器关闭失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('新建页面', [
    {'name': '上下文ID', 'mapping': 'context_id',
        'description': '浏览器上下文ID，如果不指定则使用当前上下文'},
], category='UI/浏览器', tags=['页面', '新建'])
def new_page(**kwargs):
    """新建页面

    Args:
        context_id: 上下文ID

    Returns:
        dict: 包含新页面ID的字典
    """
    context_id = kwargs.get('context_id')
    test_context = kwargs.get('context')

    with allure.step("新建页面"):
        try:
            # 如果没有指定上下文ID，从测试上下文获取
            if not context_id and test_context:
                context_id = test_context.get('current_context_id')

            page_id = browser_manager.create_page(context_id)

            # 更新测试上下文中的当前页面
            if test_context:
                test_context.set('current_page_id', page_id)

            allure.attach(
                f"新页面ID: {page_id}\n上下文ID: {context_id}",
                name="新建页面信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"新建页面成功: {page_id}")

            # 保存页面ID到上下文
            if test_context:
                test_context.set('current_page_id', page_id)

            # 直接返回页面ID
            return page_id

        except Exception as e:
            logger.error(f"新建页面失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="新建页面失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('切换页面', [
    {'name': '页面ID', 'mapping': 'page_id', 'description': '要切换到的页面ID'},
], category='UI/浏览器', tags=['页面', '切换'])
def switch_page(**kwargs):
    """切换页面

    Args:
        page_id: 页面ID

    Returns:
        dict: 操作结果
    """
    page_id = kwargs.get('page_id')
    context = kwargs.get('context')

    with allure.step(f"切换页面: {page_id}"):
        try:
            browser_manager.switch_page(page_id)

            # 更新测试上下文中的当前页面
            if context:
                context.set('current_page_id', page_id)

            allure.attach(
                f"已切换到页面: {page_id}",
                name="页面切换信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"页面切换成功: {page_id}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": True,
                "captures": {
                    'current_page_id': page_id
                },
                "session_state": {},
                "metadata": {
                    "page_id": page_id,
                    "operation": "switch_page"
                }
            }

        except Exception as e:
            logger.error(f"切换页面失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="页面切换失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('设置等待超时', [
    {'name': '超时时间', 'mapping': 'timeout', 'description': '默认等待超时时间（秒）', 'default': 30},
], category='UI/浏览器', tags=['配置', '超时'])
def set_default_timeout(**kwargs):
    """设置默认等待超时时间

    Args:
        timeout: 超时时间（秒）

    Returns:
        dict: 操作结果
    """
    timeout = float(kwargs.get('timeout', 30))

    with allure.step(f"设置等待超时: {timeout}秒"):
        try:
            # 获取当前页面并设置超时
            page = browser_manager.get_current_page()
            from ..core.element_locator import ElementLocator
            locator = ElementLocator(page)
            locator.set_default_timeout(timeout)

            allure.attach(
                f"默认超时时间已设置为: {timeout}秒",
                name="超时设置信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"默认超时时间设置成功: {timeout}秒")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": timeout,
                "captures": {},
                "session_state": {},
                "metadata": {
                    "timeout": timeout,
                    "operation": "set_default_timeout"
                }
            }

        except Exception as e:
            logger.error(f"设置超时时间失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="超时设置失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('获取页面列表', [
    {'name': '变量名', 'mapping': 'variable',
     'description': '保存页面列表的变量名'},
], category='UI/浏览器', tags=['页面', '查询'])
def get_page_list(**kwargs):
    """获取页面列表

    Args:
        variable: 变量名

    Returns:
        dict: 包含页面列表的字典
    """
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    with allure.step("获取页面列表"):
        try:
            # 获取所有页面ID
            page_ids = list(browser_manager.pages.keys())
            current_page_id = browser_manager.current_page

            page_info = []
            for page_id in page_ids:
                page = browser_manager.pages[page_id]
                try:
                    title = page.title()
                    url = page.url
                except:
                    title = "无法获取"
                    url = "无法获取"
                
                page_info.append({
                    'page_id': page_id,
                    'title': title,
                    'url': url,
                    'is_current': page_id == current_page_id
                })

            # 保存到变量
            result = {
                'page_ids': page_ids,
                'current_page_id': current_page_id,
                'page_info': page_info
            }

            if variable and context:
                context.set(variable, result)

            allure.attach(
                f"总页面数: {len(page_ids)}\n"
                f"当前页面: {current_page_id}\n"
                f"页面列表: {', '.join(page_ids)}",
                name="页面列表信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"获取页面列表成功，共{len(page_ids)}个页面")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": result,
                "captures": {
                    variable: result
                } if variable else {},
                "session_state": {},
                "metadata": {
                    "page_count": len(page_ids),
                    "current_page_id": current_page_id,
                    "operation": "get_page_list"
                }
            }

        except Exception as e:
            logger.error(f"获取页面列表失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="获取页面列表失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('等待新页面', [
    {'name': '超时时间', 'mapping': 'timeout', 'description': '等待超时时间（秒）', 'default': 30},
    {'name': '变量名', 'mapping': 'variable', 'description': '保存新页面ID的变量名'},
], category='UI/浏览器', tags=['页面', '等待'])
def wait_for_new_page(**kwargs):
    """等待新页面出现（用于处理新窗口/标签页）

    Args:
        timeout: 超时时间
        variable: 变量名

    Returns:
        dict: 包含新页面ID的字典
    """
    timeout = kwargs.get('timeout', 30.0)
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    with allure.step("等待新页面"):
        try:
            # 记录当前页面数量
            initial_page_count = len(browser_manager.pages)
            
            # 获取当前上下文
            current_context = browser_manager.get_current_context()
            if not current_context:
                raise ValueError("没有可用的浏览器上下文")

            # 等待新页面出现
            timeout_ms = int(timeout * 1000)
            
            # 使用Playwright的等待新页面功能
            with current_context.expect_page(timeout=timeout_ms) as page_info:
                pass
            
            new_page = page_info.value
            
            # 为新页面生成ID并注册
            page_id = f"{browser_manager.current_context}_page_{len(browser_manager.pages)}"
            browser_manager.pages[page_id] = new_page
            
            # 切换到新页面
            browser_manager.switch_page(page_id)
            
            # 更新测试上下文
            if context:
                context.set('current_page_id', page_id)

            # 保存到变量
            if variable and context:
                context.set(variable, page_id)

            allure.attach(
                f"新页面ID: {page_id}\n"
                f"页面URL: {new_page.url}\n"
                f"超时时间: {timeout}秒",
                name="等待新页面信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"等待新页面成功: {page_id}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": page_id,
                "captures": {
                    variable: page_id
                } if variable else {
                    'new_page_id': page_id
                },
                "session_state": {},
                "metadata": {
                    "page_id": page_id,
                    "page_url": new_page.url,
                    "timeout": timeout,
                    "operation": "wait_for_new_page"
                }
            }

        except Exception as e:
            logger.error(f"等待新页面失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="等待新页面失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('切换到最新页面', [
    {'name': '变量名', 'mapping': 'variable', 'description': '保存最新页面ID的变量名'},
], category='UI/浏览器', tags=['页面', '切换'])
def switch_to_latest_page(**kwargs):
    """切换到最新创建的页面

    Args:
        variable: 变量名

    Returns:
        dict: 包含最新页面ID的字典
    """
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    with allure.step("切换到最新页面"):
        try:
            if not browser_manager.pages:
                raise ValueError("没有可用的页面")

            # 获取所有页面ID，按创建顺序排序（页面ID包含序号）
            page_ids = list(browser_manager.pages.keys())
            if not page_ids:
                raise ValueError("没有可用的页面")

            # 获取最新的页面ID（序号最大的）
            latest_page_id = max(page_ids, key=lambda pid: int(pid.split('_page_')[-1]))
            
            # 切换到最新页面
            browser_manager.switch_page(latest_page_id)
            
            # 更新测试上下文
            if context:
                context.set('current_page_id', latest_page_id)

            # 保存到变量
            if variable and context:
                context.set(variable, latest_page_id)

            # 获取页面信息
            page = browser_manager.get_page(latest_page_id)
            page_url = page.url
            page_title = page.title()

            allure.attach(
                f"最新页面ID: {latest_page_id}\n"
                f"页面URL: {page_url}\n"
                f"页面标题: {page_title}",
                name="切换到最新页面信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"切换到最新页面成功: {latest_page_id}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": latest_page_id,
                "captures": {
                    variable: latest_page_id
                } if variable else {
                    'latest_page_id': latest_page_id
                },
                "session_state": {},
                "metadata": {
                    "page_id": latest_page_id,
                    "page_url": page_url,
                    "page_title": page_title,
                    "operation": "switch_to_latest_page"
                }
            }

        except Exception as e:
            logger.error(f"切换到最新页面失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="切换到最新页面失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('根据标题查找页面', [
    {'name': '标题', 'mapping': 'title', 'description': '页面标题（支持部分匹配）'},
    {'name': '精确匹配', 'mapping': 'exact_match', 'description': '是否精确匹配标题', 'default': False},
    {'name': '变量名', 'mapping': 'variable', 'description': '保存找到的页面ID的变量名'},
], category='UI/浏览器', tags=['页面', '查找'])
def find_page_by_title(**kwargs):
    """根据页面标题查找页面ID

    Args:
        title: 要查找的页面标题
        exact_match: 是否精确匹配
        variable: 变量名

    Returns:
        dict: 包含找到的页面ID的字典
    """
    title = kwargs.get('title')
    exact_match = kwargs.get('exact_match', False)
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    if not title:
        raise ValueError("标题参数不能为空")

    with allure.step(f"根据标题查找页面: {title}"):
        try:
            # 获取所有页面
            page_ids = list(browser_manager.pages.keys())
            found_pages = []

            # 将搜索标题转换为多种格式用于匹配
            search_title_lower = title.lower()
            search_title_encoded = urllib.parse.quote(title, safe='')
            
            for page_id in page_ids:
                page = browser_manager.pages[page_id]
                try:
                    page_title = page.title()
                    
                    # 处理空标题的情况
                    if not page_title:
                        continue
                    
                    # 尝试多种方式解码标题（处理被编码的中文）
                    decoded_title = page_title
                    
                    # 方法1：从URL中提取正确编码的标题
                    try:
                        page_url = page.url
                        if 'title>' in page_url and '%' in page_url:
                            # 从URL中提取title标签的内容
                            start = page_url.find('<title>') + 7
                            end = page_url.find('</title>')
                            if start > 6 and end > start:
                                url_title = page_url[start:end]
                                decoded_title = urllib.parse.unquote(url_title)
                    except:
                        pass
                    
                    # 方法2：尝试URL解码
                    try:
                        if '%' in page_title:
                            decoded_title = urllib.parse.unquote(page_title)
                    except:
                        pass
                    
                    # 方法3：尝试处理UTF-8编码问题
                    try:
                        if isinstance(page_title, str):
                            # 尝试将错误编码的字符串正确解码
                            decoded_title = page_title.encode('latin1').decode('utf-8')
                    except:
                        pass
                    
                    # 根据匹配模式判断
                    if exact_match:
                        # 精确匹配：检查原标题、解码标题
                        if (page_title == title or 
                            decoded_title == title):
                            found_pages.append({
                                'page_id': page_id,
                                'title': page_title,
                                'decoded_title': decoded_title,
                                'url': page.url
                            })
                    else:
                        # 部分匹配：检查原标题、解码标题（不区分大小写）
                        page_title_lower = page_title.lower()
                        decoded_title_lower = decoded_title.lower()
                        
                        if (search_title_lower in page_title_lower or 
                            search_title_lower in decoded_title_lower or
                            search_title_encoded in page_title):
                            found_pages.append({
                                'page_id': page_id,
                                'title': page_title,
                                'decoded_title': decoded_title,
                                'url': page.url
                            })
                except Exception as e:
                    # 忽略无法获取标题的页面
                    logger.debug(f"无法获取页面 {page_id} 的标题: {str(e)}")
                    continue

            if not found_pages:
                raise ValueError(f"未找到标题包含 '{title}' 的页面")

            # 如果找到多个页面，返回第一个
            result = found_pages[0]['page_id'] if found_pages else None
            
            # 保存到变量
            if variable and context and result:
                context.set(variable, result)

            allure.attach(
                f"查找标题: {title}\n"
                f"编码后: {search_title_encoded}\n"
                f"匹配模式: {'精确匹配' if exact_match else '部分匹配'}\n"
                f"找到页面数: {len(found_pages)}\n"
                f"返回页面ID: {result}\n"
                f"所有匹配页面: {found_pages}",
                name="根据标题查找页面信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"根据标题 '{title}' 找到 {len(found_pages)} 个页面，返回: {result}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": result,
                "captures": {
                    variable: result
                } if variable and result else {
                    'found_page_id': result,
                    'all_matches': found_pages
                },
                "session_state": {},
                "metadata": {
                    "search_title": title,
                    "search_title_encoded": search_title_encoded,
                    "exact_match": exact_match,
                    "found_count": len(found_pages),
                    "found_page_id": result,
                    "all_matches": found_pages,
                    "operation": "find_page_by_title"
                }
            }

        except Exception as e:
            logger.error(f"根据标题查找页面失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="根据标题查找页面失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise


@keyword_manager.register('根据URL查找页面', [
    {'name': 'URL', 'mapping': 'url', 'description': '页面URL（支持部分匹配）'},
    {'name': '精确匹配', 'mapping': 'exact_match', 'description': '是否精确匹配URL', 'default': False},
    {'name': '变量名', 'mapping': 'variable', 'description': '保存找到的页面ID的变量名'},
], category='UI/浏览器', tags=['页面', '查找'])
def find_page_by_url(**kwargs):
    """根据页面URL查找页面ID

    Args:
        url: 要查找的页面URL
        exact_match: 是否精确匹配
        variable: 变量名

    Returns:
        dict: 包含找到的页面ID的字典
    """
    url = kwargs.get('url')
    exact_match = kwargs.get('exact_match', False)
    variable = kwargs.get('variable')
    context = kwargs.get('context')

    if not url:
        raise ValueError("URL参数不能为空")

    with allure.step(f"根据URL查找页面: {url}"):
        try:
            # 获取所有页面
            page_ids = list(browser_manager.pages.keys())
            found_pages = []

            for page_id in page_ids:
                page = browser_manager.pages[page_id]
                try:
                    page_url = page.url
                    
                    # 根据匹配模式判断
                    if exact_match:
                        if page_url == url:
                            found_pages.append({
                                'page_id': page_id,
                                'title': page.title(),
                                'url': page_url
                            })
                    else:
                        if url.lower() in page_url.lower():
                            found_pages.append({
                                'page_id': page_id,
                                'title': page.title(),
                                'url': page_url
                            })
                except:
                    # 忽略无法获取URL的页面
                    continue

            if not found_pages:
                raise ValueError(f"未找到URL包含 '{url}' 的页面")

            # 如果找到多个页面，返回第一个
            result = found_pages[0]['page_id'] if found_pages else None
            
            # 保存到变量
            if variable and context and result:
                context.set(variable, result)

            allure.attach(
                f"查找URL: {url}\n"
                f"匹配模式: {'精确匹配' if exact_match else '部分匹配'}\n"
                f"找到页面数: {len(found_pages)}\n"
                f"返回页面ID: {result}\n"
                f"所有匹配页面: {found_pages}",
                name="根据URL查找页面信息",
                attachment_type=allure.attachment_type.TEXT
            )

            logger.info(f"根据URL '{url}' 找到 {len(found_pages)} 个页面，返回: {result}")

            # 统一返回格式 - 支持远程关键字模式
            return {
                "result": result,
                "captures": {
                    variable: result
                } if variable and result else {
                    'found_page_id': result,
                    'all_matches': found_pages
                },
                "session_state": {},
                "metadata": {
                    "search_url": url,
                    "exact_match": exact_match,
                    "found_count": len(found_pages),
                    "found_page_id": result,
                    "all_matches": found_pages,
                    "operation": "find_page_by_url"
                }
            }

        except Exception as e:
            logger.error(f"根据URL查找页面失败: {str(e)}")
            allure.attach(
                f"错误信息: {str(e)}",
                name="根据URL查找页面失败",
                attachment_type=allure.attachment_type.TEXT
            )
            raise
