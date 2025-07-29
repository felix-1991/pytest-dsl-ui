"""基于浏览器的HTTP请求关键字模块

该模块提供了基于浏览器上下文的HTTP请求、捕获响应和断言的关键字。
设计上与pytest-dsl的HTTP关键字保持一致，但利用浏览器的会话状态和认证信息。
"""

import allure
import re
import yaml
import json
import os
import time
import logging
from typing import Dict, Any, Union

# 假设这些模块存在于当前项目中
try:
    from pytest_dsl.core.keyword_manager import keyword_manager
    from pytest_dsl.core.yaml_vars import yaml_vars
    from pytest_dsl.core.context import TestContext
except ImportError:
    # 如果pytest-dsl模块不存在，创建简单的替代实现
    class keyword_manager:
        @staticmethod
        def register(name, params):
            def decorator(func):
                return func
            return decorator
    
    class yaml_vars:
        @staticmethod
        def get_variable(key):
            return {}
    
    class TestContext:
        def __init__(self):
            self._vars = {}
        
        def set(self, key, value):
            self._vars[key] = value
        
        def get(self, key):
            return self._vars.get(key)

from ..core.browser_http_request import BrowserHTTPRequest

# 配置日志
logger = logging.getLogger(__name__)

# 获取浏览器管理器（假设存在）
try:
    from pytest_dsl_ui.core.browser_manager import browser_manager
except ImportError:
    # 创建简单的浏览器管理器替代实现
    class BrowserManager:
        def get_current_context(self):
            return None
    browser_manager = BrowserManager()


def _process_file_reference(reference: Union[str, Dict[str, Any]],
                            allow_vars: bool = True,
                            test_context: TestContext = None) -> Any:
    """处理文件引用，加载外部文件内容
    
    复用pytest-dsl的文件引用处理逻辑
    """
    # 处理简单语法
    if isinstance(reference, str):
        file_ref_pattern = r'^@file(?:_template)?:(.+)$'
        match = re.match(file_ref_pattern, reference.strip())

        if match:
            file_path = match.group(1).strip()
            is_template = '_template' in reference[:15]
            return _load_file_content(file_path, is_template, 'auto', 'utf-8', test_context)

    # 处理详细语法
    elif isinstance(reference, dict) and 'file_ref' in reference:
        file_ref = reference['file_ref']

        if isinstance(file_ref, str):
            return _load_file_content(file_ref, allow_vars, 'auto', 'utf-8', test_context)
        elif isinstance(file_ref, dict):
            file_path = file_ref.get('path')
            if not file_path:
                raise ValueError("file_ref必须包含path字段")

            template = file_ref.get('template', allow_vars)
            file_type = file_ref.get('type', 'auto')
            encoding = file_ref.get('encoding', 'utf-8')

            return _load_file_content(file_path, template, file_type, encoding, test_context)

    return reference


def _load_file_content(file_path: str, is_template: bool = False,
                       file_type: str = 'auto', encoding: str = 'utf-8',
                       test_context: TestContext = None) -> Any:
    """加载文件内容"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到引用的文件: {file_path}")

    with open(file_path, 'r', encoding=encoding) as f:
        content = f.read()

    if is_template:
        # 简单的变量替换实现
        try:
            from pytest_dsl.core.variable_utils import VariableReplacer
            replacer = VariableReplacer(test_context=test_context)
            content = replacer.replace_in_string(content)
        except ImportError:
            # 如果没有VariableReplacer，进行简单的字符串替换
            if test_context:
                for key, value in test_context._vars.items():
                    content = content.replace(f"${{{key}}}", str(value))

    if file_type == 'auto':
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext in ['.json']:
            file_type = 'json'
        elif file_ext in ['.yaml', '.yml']:
            file_type = 'yaml'
        else:
            file_type = 'text'

    if file_type == 'json':
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"无效的JSON文件 {file_path}: {str(e)}")
    elif file_type == 'yaml':
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"无效的YAML文件 {file_path}: {str(e)}")
    else:
        return content


def _process_request_config(config: Dict[str, Any], test_context: TestContext = None) -> Dict[str, Any]:
    """处理请求配置，检查并处理文件引用"""
    if not isinstance(config, dict):
        return config

    if 'request' in config and isinstance(config['request'], dict):
        request = config['request']

        if 'json' in request:
            request['json'] = _process_file_reference(request['json'], test_context=test_context)

        if 'data' in request:
            request['data'] = _process_file_reference(request['data'], test_context=test_context)

        if 'headers' in request:
            request['headers'] = _process_file_reference(request['headers'], test_context=test_context)

    return config


def _normalize_retry_config(config, assert_retry_count=None, assert_retry_interval=None):
    """标准化断言重试配置（复用pytest-dsl逻辑）"""
    standard_retry_config = {
        'enabled': False,
        'count': 3,
        'interval': 1.0,
        'all': False,
        'indices': [],
        'specific': {}
    }

    if assert_retry_count and int(assert_retry_count) > 0:
        standard_retry_config['enabled'] = True
        standard_retry_config['count'] = int(assert_retry_count)
        standard_retry_config['all'] = True
        if assert_retry_interval:
            standard_retry_config['interval'] = float(assert_retry_interval)

    if 'retry_assertions' in config and config['retry_assertions']:
        retry_assertions = config['retry_assertions']
        standard_retry_config['enabled'] = True

        if 'count' in retry_assertions:
            standard_retry_config['count'] = retry_assertions['count']
        if 'interval' in retry_assertions:
            standard_retry_config['interval'] = retry_assertions['interval']
        if 'all' in retry_assertions:
            standard_retry_config['all'] = retry_assertions['all']
        if 'indices' in retry_assertions:
            standard_retry_config['indices'] = retry_assertions['indices']
        if 'specific' in retry_assertions:
            specific_config = {}
            for key, value in retry_assertions['specific'].items():
                specific_config[str(key)] = value
                if isinstance(key, int):
                    specific_config[key] = value
            standard_retry_config['specific'] = specific_config

    elif 'retry' in config and config['retry']:
        retry_config = config['retry']
        if 'count' in retry_config and retry_config['count'] > 0:
            standard_retry_config['enabled'] = True
            standard_retry_config['count'] = retry_config['count']
            standard_retry_config['all'] = True
            if 'interval' in retry_config:
                standard_retry_config['interval'] = retry_config['interval']

    return standard_retry_config


@keyword_manager.register('浏览器HTTP请求', [
    {'name': '客户端', 'mapping': 'client',
     'description': '客户端名称，对应YAML变量文件中的客户端配置',
     'default': 'default'},
    {'name': '配置', 'mapping': 'config',
     'description': '包含请求、捕获和断言的YAML配置'},
    {'name': '会话', 'mapping': 'session',
     'description': '会话名称，用于在多个请求间保持会话状态（浏览器上下文自动管理）'},
    {'name': '保存响应', 'mapping': 'save_response',
     'description': '将完整响应保存到指定变量名中'},
    {'name': '禁用授权', 'mapping': 'disable_auth',
     'description': '禁用客户端配置中的授权机制', 'default': False},
    {'name': '模板', 'mapping': 'template',
     'description': '使用YAML变量文件中定义的请求模板'},
    {'name': '断言重试次数', 'mapping': 'assert_retry_count',
     'description': '断言失败时的重试次数', 'default': 0},
    {'name': '断言重试间隔', 'mapping': 'assert_retry_interval',
     'description': '断言重试间隔时间（秒）', 'default': 1}
], category='UI/接口测试', tags=['接口', '请求'])
def browser_http_request(context, **kwargs):
    """执行基于浏览器的HTTP请求

    根据YAML配置发送HTTP请求，利用浏览器的会话状态和认证信息，
    支持客户端配置、响应捕获和断言。

    Args:
        context: 测试上下文
        client: 客户端名称
        config: YAML配置
        session: 会话名称（浏览器上下文自动管理）
        save_response: 保存响应的变量名
        disable_auth: 禁用客户端配置中的授权机制
        template: 模板名称
        assert_retry_count: 断言失败时的重试次数
        assert_retry_interval: 断言重试间隔时间（秒）

    Returns:
        捕获的变量字典或响应对象
    """
    client_name = kwargs.get('client', 'default')
    config = kwargs.get('config', '{}')
    session_name = kwargs.get('session')
    save_response = kwargs.get('save_response')
    disable_auth = kwargs.get('disable_auth', False)
    template_name = kwargs.get('template')
    assert_retry_count = kwargs.get('assert_retry_count')
    assert_retry_interval = kwargs.get('assert_retry_interval')

    # 获取当前浏览器上下文
    browser_context = browser_manager.get_current_context()
    if not browser_context:
        raise ValueError("需要先创建浏览器上下文才能使用浏览器HTTP请求")

    print(f"🌐 浏览器HTTP请求 - 客户端: {client_name}")

    # 检查浏览器HTTP客户端配置
    browser_http_clients_config = yaml_vars.get_variable("browser_http_clients")
    if browser_http_clients_config:
        print(f"✓ 找到browser_http_clients配置，包含 {len(browser_http_clients_config)} 个客户端")
        if client_name in browser_http_clients_config:
            print(f"✓ 找到浏览器HTTP客户端 '{client_name}' 的配置")
            client_config = browser_http_clients_config[client_name]
            print(f"  - base_url: {client_config.get('base_url', 'N/A')}")
            print(f"  - timeout: {client_config.get('timeout', 'N/A')}")
        else:
            print(f"⚠️ 未找到浏览器HTTP客户端 '{client_name}' 的配置")
            print(f"  可用客户端: {list(browser_http_clients_config.keys())}")
    else:
        print("⚠️ 未找到browser_http_clients配置，使用默认配置")

    with allure.step(f"发送浏览器HTTP请求 (客户端: {client_name}"
                     f"{', 会话: ' + session_name if session_name else ''})"):
        # 处理模板
        if template_name:
            browser_http_templates = yaml_vars.get_variable("browser_http_templates") or {}
            template = browser_http_templates.get(template_name)

            if not template:
                raise ValueError(f"未找到名为 '{template_name}' 的浏览器HTTP请求模板")

            if isinstance(config, str):
                try:
                    from pytest_dsl.core.variable_utils import VariableReplacer
                    replacer = VariableReplacer(test_context=context)
                    config = replacer.replace_in_string(config)
                except ImportError:
                    # 简单的变量替换
                    if hasattr(context, '_vars'):
                        for key, value in context._vars.items():
                            config = config.replace(f"${{{key}}}", str(value))

                try:
                    user_config = yaml.safe_load(config) if config else {}
                    merged_config = _deep_merge(template.copy(), user_config)
                    config = merged_config
                except yaml.YAMLError as e:
                    raise ValueError(f"无效的YAML配置: {str(e)}")
        else:
            if isinstance(config, str):
                try:
                    from pytest_dsl.core.variable_utils import VariableReplacer
                    replacer = VariableReplacer(test_context=context)
                    config = replacer.replace_in_string(config)
                except ImportError:
                    # 简单的变量替换
                    if hasattr(context, '_vars'):
                        for key, value in context._vars.items():
                            config = config.replace(f"${{{key}}}", str(value))

        # 解析YAML配置
        if isinstance(config, str):
            try:
                config = yaml.safe_load(config)
            except yaml.YAMLError as e:
                raise ValueError(f"无效的YAML配置: {str(e)}")

        # 统一处理重试配置
        retry_config = _normalize_retry_config(config, assert_retry_count, assert_retry_interval)

        # 为了兼容性，将标准化后的重试配置写回到配置中
        if retry_config['enabled']:
            config['retry_assertions'] = {
                'count': retry_config['count'],
                'interval': retry_config['interval'],
                'all': retry_config['all'],
                'indices': retry_config['indices'],
                'specific': retry_config['specific']
            }

        # 获取客户端配置
        browser_http_clients_config = yaml_vars.get_variable("browser_http_clients") or {}
        client_config = browser_http_clients_config.get(client_name, {})
        config['client_config'] = client_config

        config = _process_request_config(config, test_context=context)

        # 创建浏览器HTTP请求对象
        browser_http_req = BrowserHTTPRequest(
            config, client_name, browser_context, session_name)

        # 执行请求
        response = browser_http_req.execute(disable_auth=disable_auth)

        # 统一处理断言逻辑
        with allure.step("执行断言验证"):
            if retry_config['enabled']:
                _process_assertions_with_unified_retry(
                    browser_http_req, retry_config, disable_auth)
            else:
                browser_http_req.process_asserts()

        # 在断言完成后获取最终的捕获值
        captured_values = browser_http_req.captured_values

        # 将捕获的变量注册到上下文
        for var_name, value in captured_values.items():
            context.set(var_name, value)

        # 保存完整响应（如果需要）
        if save_response:
            context.set(save_response, response)

        # 获取浏览器会话状态
        session_state = None
        if browser_context:
            try:
                # 获取浏览器的cookies和存储状态
                cookies = browser_context.cookies()
                # 转换为字典格式
                cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
                
                session_state = {
                    "cookies": cookie_dict,
                    "context_id": id(browser_context)
                }
            except Exception as e:
                logger.warning(f"获取浏览器会话状态失败: {str(e)}")

        # 准备响应数据（如果需要保存响应）
        response_data = None
        if save_response:
            try:
                response_data = {
                    "status_code": response.status_code,
                    "status_text": response.status_text,
                    "headers": response.headers,
                    "text": response.text,
                    "url": response.url,
                    "elapsed_ms": getattr(response, '_elapsed_ms', 0.0)
                }
                if response.is_json():
                    try:
                        response_data["json"] = response.json()
                    except:
                        response_data["json"] = None
            except Exception as e:
                logger.warning(f"准备响应数据失败: {str(e)}")
                response_data = {"error": str(e)}

        # 保存捕获的变量到上下文
        if context:
            for key, value in captured_values.items():
                context.set(key, value)

        # 直接返回捕获的变量（如果有的话），否则返回True
        if captured_values:
            return captured_values
        else:
            return True


def _deep_merge(dict1, dict2):
    """深度合并两个字典"""
    for key in dict2:
        if (key in dict1 and isinstance(dict1[key], dict) and
                isinstance(dict2[key], dict)):
            _deep_merge(dict1[key], dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1


def _process_assertions_with_unified_retry(browser_http_req, retry_config, disable_auth=False):
    """使用统一的重试配置处理断言"""
    # 初始尝试执行所有断言
    try:
        results, failed_retryable_assertions = browser_http_req.process_asserts()
        return results
    except AssertionError as e:
        # 记录初始断言失败的详细错误信息
        allure.attach(
            str(e),
            name="断言验证失败详情",
            attachment_type=allure.attachment_type.TEXT
        )

        # 收集失败的断言
        original_config = (browser_http_req.config.copy()
                           if isinstance(browser_http_req.config, dict) else {})

        temp_config = original_config.copy()
        temp_config['_collect_failed_assertions_only'] = True

        try:
            browser_http_req.config = temp_config
            if not browser_http_req.response:
                browser_http_req.execute(disable_auth=disable_auth)

            _, failed_retryable_assertions = browser_http_req.process_asserts()
        except Exception as collect_err:
            allure.attach(
                f"收集失败断言时出错: {type(collect_err).__name__}: {str(collect_err)}",
                name="断言收集错误",
                attachment_type=allure.attachment_type.TEXT
            )
            failed_retryable_assertions = []
        finally:
            browser_http_req.config = original_config

        if not failed_retryable_assertions:
            raise

        # 过滤需要重试的断言
        retryable_assertions = []
        for failed_assertion in failed_retryable_assertions:
            assertion_idx = failed_assertion['index']
            should_retry = False
            specific_retry_count = retry_config['count']
            specific_retry_interval = retry_config['interval']

            if str(assertion_idx) in retry_config['specific']:
                should_retry = True
                spec_config = retry_config['specific'][str(assertion_idx)]
                if isinstance(spec_config, dict):
                    if 'count' in spec_config:
                        specific_retry_count = spec_config['count']
                    if 'interval' in spec_config:
                        specific_retry_interval = spec_config['interval']
            elif assertion_idx in retry_config['indices']:
                should_retry = True
            elif retry_config['all']:
                should_retry = True

            if should_retry:
                failed_assertion['retry_count'] = specific_retry_count
                failed_assertion['retry_interval'] = specific_retry_interval
                retryable_assertions.append(failed_assertion)

        if not retryable_assertions:
            raise

        retry_info = "\n".join([
            f"{i+1}. {a['type']} " +
            (f"[{a['path']}]" if a['path'] else "") +
            f": 重试 {a['retry_count']} 次，间隔 {a['retry_interval']} 秒"
            for i, a in enumerate(retryable_assertions)
        ])

        allure.attach(
            f"找到 {len(retryable_assertions)} 个可重试的断言:\n\n{retry_info}",
            name="重试断言列表",
            attachment_type=allure.attachment_type.TEXT
        )

        # 开始重试循环
        max_retry_count = retry_config['count']
        for retryable_assertion in retryable_assertions:
            max_retry_count = max(max_retry_count,
                                  retryable_assertion.get('retry_count', 3))

        # 进行断言重试
        for attempt in range(1, max_retry_count + 1):
            with allure.step(f"断言重试 (尝试 {attempt}/{max_retry_count})"):
                retry_interval = retry_config['interval']
                for assertion in retryable_assertions:
                    retry_interval = max(retry_interval,
                                         assertion.get('retry_interval', 1.0))

                allure.attach(
                    f"重试 {len(retryable_assertions)} 个断言\n"
                    f"等待间隔: {retry_interval}秒",
                    name="断言重试信息",
                    attachment_type=allure.attachment_type.TEXT
                )

                time.sleep(retry_interval)

                # 重新发送请求
                try:
                    browser_http_req.execute(disable_auth=disable_auth)
                except Exception as exec_error:
                    allure.attach(
                        f"重试执行请求失败: {type(exec_error).__name__}: {str(exec_error)}",
                        name=f"重试请求执行失败 #{attempt}",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    continue

                # 过滤出仍在重试范围内的断言
                still_retryable_assertions = []
                for assertion in retryable_assertions:
                    assertion_retry_count = assertion.get('retry_count', 3)
                    if attempt < assertion_retry_count:
                        still_retryable_assertions.append(assertion)

                if not still_retryable_assertions:
                    break

                # 只重试那些仍在重试范围内的断言
                try:
                    retry_assertion_indexes = [
                        a['index'] for a in still_retryable_assertions]
                    retry_assertions = [
                        browser_http_req.config.get('asserts', [])[idx]
                        for idx in retry_assertion_indexes]

                    index_mapping = {
                        new_idx: orig_idx for new_idx, orig_idx in
                        enumerate(retry_assertion_indexes)}

                    results, new_failed_assertions = browser_http_req.process_asserts(
                        specific_asserts=retry_assertions,
                        index_mapping=index_mapping)

                    if not new_failed_assertions:
                        try:
                            results, _ = browser_http_req.process_asserts()
                            allure.attach(
                                "所有断言重试后验证通过",
                                name="重试成功",
                                attachment_type=allure.attachment_type.TEXT
                            )
                            return results
                        except AssertionError as final_err:
                            allure.attach(
                                f"重试后的完整断言验证仍有失败: {str(final_err)}",
                                name="完整断言仍失败",
                                attachment_type=allure.attachment_type.TEXT
                            )
                            continue

                    retryable_assertions = new_failed_assertions

                except AssertionError as retry_err:
                    allure.attach(
                        f"第 {attempt} 次重试断言失败: {str(retry_err)}",
                        name=f"重试断言失败 #{attempt}",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    continue

        # 重试次数用完，执行一次完整的断言以获取最终结果和错误
        allure.attach(
            "所有重试次数已用完，执行最终断言验证",
            name="重试完成",
            attachment_type=allure.attachment_type.TEXT
        )

        try:
            browser_http_req.execute(disable_auth=disable_auth)
            results, _ = browser_http_req.process_asserts()
            return results
        except AssertionError as final_err:
            enhanced_error = (
                f"断言验证失败 (已重试 {max_retry_count} 次):\n\n"
                f"{str(final_err)}"
            )
            allure.attach(
                enhanced_error,
                name="重试后仍失败的断言",
                attachment_type=allure.attachment_type.TEXT
            )
            raise AssertionError(enhanced_error) from final_err


# 额外的便利关键字

@keyword_manager.register('设置浏览器HTTP客户端', [
    {'name': '客户端名称', 'mapping': 'client_name',
     'description': '客户端名称', 'default': 'default'},
    {'name': '基础URL', 'mapping': 'base_url',
     'description': 'API的基础URL地址'},
    {'name': '默认头', 'mapping': 'headers',
     'description': '默认请求头（JSON格式）'},
    {'name': '超时时间', 'mapping': 'timeout',
     'description': '默认超时时间（秒）', 'default': 30},
], category='UI/接口测试', tags=['接口', '请求'])
def set_browser_http_client(context, **kwargs):
    """设置浏览器HTTP客户端配置

    Args:
        context: 测试上下文
        client_name: 客户端名称
        base_url: 基础URL
        headers: 默认请求头
        timeout: 超时时间

    Returns:
        dict: 操作结果
    """
    client_name = kwargs.get('client_name', 'default')
    base_url = kwargs.get('base_url', '')
    headers = kwargs.get('headers', {})
    timeout = kwargs.get('timeout', 30)

    # 处理headers参数
    if isinstance(headers, str):
        try:
            headers = json.loads(headers)
        except json.JSONDecodeError:
            raise ValueError("无效的JSON格式headers")

    with allure.step(f"设置浏览器HTTP客户端: {client_name}"):
        # 构建客户端配置
        client_config = {
            'base_url': base_url,
            'headers': headers,
            'timeout': timeout
        }

        # 保存到上下文变量
        browser_http_clients = context.get('browser_http_clients') or {}
        browser_http_clients[client_name] = client_config
        context.set('browser_http_clients', browser_http_clients)

        allure.attach(
            f"客户端名称: {client_name}\n"
            f"基础URL: {base_url}\n"
            f"默认头: {json.dumps(headers, indent=2, ensure_ascii=False)}\n"
            f"超时时间: {timeout}秒",
            name="浏览器HTTP客户端配置",
            attachment_type=allure.attachment_type.TEXT
        )

        # 直接返回成功状态
        return True