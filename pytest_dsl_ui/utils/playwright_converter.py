"""
Playwright Python脚本到DSL语法转换工具

支持将playwright codegen生成的Python脚本转换为pytest-dsl-ui的DSL语法

最近更新:
- 修复了关键字映射错误，将注释的操作改为正确的DSL关键字
- 添加了对按键操作、悬停元素、聚焦元素、滚动元素到视野的支持
- 修正了复选框操作（勾选、取消勾选、设置状态）的映射
- 改进了下拉选择操作，支持按值、标签、索引选择
- 扩展了断言支持，包括文本包含、元素状态、输入值、URL、标题等
- 添加了页面级别操作：刷新、后退、前进
"""

import re
import argparse
import sys
from typing import Optional, Dict, Any
from pathlib import Path


class PlaywrightToDSLConverter:
    """Playwright Python脚本到DSL语法转换器"""

    def __init__(self):
        # DSL输出缓冲区
        self.dsl_lines = []
        self.browser_type = "chromium"
        self.headless = False
        self.viewport_width = 1920
        self.viewport_height = 1080

    def convert_script(self, script_content: str) -> str:
        """转换整个脚本为DSL格式"""
        # 直接使用正则表达式方法，更可靠
        return self._regex_conversion(script_content)

    def _add_dsl_header(self):
        """添加DSL文件头部"""
        self.dsl_lines.extend([
            '@name: "从Playwright录制转换的测试"',
            '@description: "由playwright codegen录制并自动转换为DSL格式"',
            '@tags: [UI, 自动化, 转换]',
            '@author: "playwright-to-dsl-converter"',
            ''
        ])

    def _regex_conversion(self, script_content: str) -> str:
        """使用正则表达式进行转换"""
        lines = script_content.split('\n')
        dsl_lines = []

        # 添加头部
        dsl_lines.extend([
            '@name: "从Playwright录制转换的测试"',
            '@description: "由playwright codegen录制并自动转换为DSL格式"',
            '@tags: [UI, 自动化, 转换]',
            '@author: "playwright-to-dsl-converter"',
            ''
        ])

        browser_started = False
        i = 0

        while i < len(lines):
            line = lines[i]
            line = line.strip()

            # 跳过导入、函数定义和注释，但不跳过下载相关的with语句
            skip_patterns = [
                'import ', 'from ', 'def ', '#', '"""', "'''"]
            if (any(line.startswith(pattern) for pattern in skip_patterns) or
                    not line or line == 'pass' or line.startswith('return')):
                i += 1
                continue

            # 跳过非下载相关的with语句
            if line.startswith('with ') and 'expect_download' not in line:
                i += 1
                continue

            # 启动浏览器
            if '.launch(' in line and not browser_started:
                headless_val = 'False' if 'headless=False' in line else 'True'

                browser_type = "chromium"
                if 'firefox' in line:
                    browser_type = "firefox"
                elif 'webkit' in line:
                    browser_type = "webkit"

                dsl_lines.append("# 启动浏览器")
                browser_line = (f'[启动浏览器], 浏览器: "{browser_type}", '
                                f'无头模式: {headless_val}')
                dsl_lines.append(browser_line)
                browser_started = True
                i += 1
                continue

            # 跳过context创建，但不跳过new_page赋值
            if (('.new_context()' in line and '=' not in line) or
                    '.close()' in line):
                i += 1
                continue

            # 打开页面
            if '.goto(' in line:
                url_match = re.search(r'\.goto\(["\']([^"\']+)["\']', line)
                if url_match:
                    url = url_match.group(1)
                    dsl_lines.append("\n# 打开页面")
                    dsl_lines.append(f'[打开页面], 地址: "{url}"')
                i += 1
                continue

            # 处理等待操作 - 移到前面处理
            if '.wait_for_' in line:
                self._convert_wait_operation(line, dsl_lines)
                i += 1
                continue

            # 处理复杂的链式调用（优先处理）
            dsl_line = self._convert_complex_chained_call(line)
            if dsl_line:
                dsl_lines.append(dsl_line)
                i += 1
                continue

            # 处理get_by系列方法的链式调用
            dsl_line = self._convert_chained_call(line)
            if dsl_line:
                dsl_lines.append(dsl_line)
                i += 1
                continue

            # 处理普通的点击操作
            if '.click(' in line and 'get_by_' not in line:
                selector_match = re.search(
                    r'\.click\(["\']([^"\']+)["\']', line)
                if selector_match:
                    selector = selector_match.group(1)
                    dsl_lines.append(f'[点击元素], 定位器: "{selector}"')
                i += 1
                continue

            # 处理截图
            if '.screenshot(' in line:
                filename_match = re.search(r'path=["\']([^"\']+)["\']', line)
                if filename_match:
                    filename = filename_match.group(1)
                else:
                    filename = "screenshot.png"
                dsl_lines.append(f'[截图], 文件名: "{filename}"')
                i += 1
                continue

            # 处理页面级别的操作
            if '.reload(' in line:
                dsl_lines.append("[刷新页面]")
                i += 1
                continue

            if '.go_back(' in line:
                dsl_lines.append("[后退]")
                i += 1
                continue

            if '.go_forward(' in line:
                dsl_lines.append("[前进]")
                i += 1
                continue

            # 处理新窗口/页面操作
            if 'context.new_page()' in line or '.new_page(' in line:
                dsl_lines.append("[新建页面]")
                i += 1
                continue

            # 处理页面导航到新窗口（避免与new_page冲突）
            if ('new_page' in line and 'context' in line and
                    '.new_page(' not in line and
                    'context.new_page()' not in line):
                dsl_lines.append("# 检测到新页面创建")
                dsl_lines.append("[等待新页面], 变量名: \"new_page_id\"")
                i += 1
                continue

            # 处理视口设置
            if '.set_viewport_size(' in line:
                viewport_match = re.search(
                    r'\.set_viewport_size\(\s*{[^}]*width[^}]*:\s*(\d+)'
                    r'[^}]*height[^}]*:\s*(\d+)', line)
                if viewport_match:
                    width = viewport_match.group(1)
                    height = viewport_match.group(2)
                    dsl_lines.append(
                        f'[设置视口大小], 宽度: {width}, 高度: {height}')
                i += 1
                continue

            # 处理JavaScript执行
            if '.evaluate(' in line:
                # 检查是否是多行JavaScript（以三引号开始）
                if '"""' in line or "'''" in line:
                    # 处理多行JavaScript
                    dsl_lines.append("[执行JavaScript], 脚本: \"<多行代码>\"")
                    dsl_lines.append(f'# 原代码开始: {line}')
                    i += 1
                    # 跳过多行JavaScript内容直到结束
                    while i < len(lines):
                        current_line = lines[i].strip()
                        dsl_lines.append(f'# {current_line}')
                        if '"""' in current_line or "'''" in current_line:
                            break
                        i += 1
                    dsl_lines.append('# 原代码结束')
                    i += 1
                    continue
                else:
                    # 提取单行JavaScript代码
                    js_match = re.search(r'\.evaluate\(["\']([^"\']*(?:\\.[^"\']*)*)["\']', line)
                    if js_match:
                        js_code = js_match.group(1)
                        # 转义内部的双引号
                        js_code = js_code.replace('"', '\\"')
                        dsl_lines.append(f'[执行JavaScript], 脚本: "{js_code}"')
                    else:
                        # 处理复杂的JavaScript代码
                        dsl_lines.append("[执行JavaScript], 脚本: \"<复杂代码>\"")
                        dsl_lines.append(f'# 原代码: {line}')
                i += 1
                continue

            # 处理网络监听
            if 'page.route(' in line or '.route(' in line:
                dsl_lines.append("[开始网络监听]")
                dsl_lines.append("# 网络路由设置 - 需要手动配置")
                i += 1
                continue

            # 处理获取文本/属性操作
            if '.inner_text()' in line or '.text_content()' in line:
                # 通常与变量赋值一起使用
                locator = self._extract_locator_from_assignment(line)
                if not locator:
                    # 尝试直接从行中提取定位器
                    locator = self._extract_locator(line)

                if locator:
                    # 尝试提取变量名
                    var_name = self._extract_variable_name(line)
                    if var_name:
                        dsl_lines.append(f'{var_name} = [获取元素文本], 定位器: "{locator}"')
                    else:
                        dsl_lines.append(f'[获取元素文本], 定位器: "{locator}"')
                else:
                    dsl_lines.append("# 获取文本 - 需要手动转换")
                i += 1
                continue

            if '.get_attribute(' in line:
                locator = self._extract_locator_from_assignment(line)
                attr_match = re.search(
                    r'\.get_attribute\(["\']([^"\']+)["\']', line)
                if not locator:
                    # 尝试直接从行中提取定位器
                    locator = self._extract_locator(line)

                if locator and attr_match:
                    attr = attr_match.group(1)
                    # 尝试提取变量名
                    var_name = self._extract_variable_name(line)
                    if var_name:
                        dsl_lines.append(f'{var_name} = [获取元素属性], 定位器: "{locator}", 属性: "{attr}"')
                    else:
                        dsl_lines.append(f'[获取元素属性], 定位器: "{locator}", 属性: "{attr}"')
                else:
                    dsl_lines.append("# 获取属性 - 需要手动转换")
                i += 1
                continue

            # 处理下载操作
            if 'with page.expect_download()' in line:
                # 使用专门的下载转换方法
                download_dsl, new_index = self._convert_download_operation(
                    '\n'.join(lines), i)
                dsl_lines.extend(download_dsl)
                i = new_index
                continue

            if '.expect_download(' in line or 'expect_download()' in line:
                # 简单的expect_download调用
                dsl_lines.append("# 等待下载 - 需要手动转换为[等待下载]关键字")
                i += 1
                continue

            if '.save_as(' in line:
                # 保存下载文件
                path_match = re.search(r'\.save_as\(["\']([^"\']+)["\']', line)
                if path_match:
                    save_path = path_match.group(1)
                    dsl_lines.append(f'# 保存下载文件到: {save_path} - 需要手动处理')
                i += 1
                continue

            # 处理页面断言 - 移到更早的位置处理
            if 'expect(' in line:
                self._convert_assertion(line, dsl_lines)
                i += 1
                continue

            # 增加循环索引
            i += 1

        # 添加关闭浏览器
        dsl_lines.append("\n# 关闭浏览器")
        dsl_lines.append("[关闭浏览器]")

        return '\n'.join(dsl_lines)

    def _convert_complex_chained_call(self, line: str) -> Optional[str]:
        """转换复杂的链式调用，包括filter、locator、first等"""

        # 处理复杂的链式调用，如：
        # page.get_by_label("日志检索", exact=True).locator("div")
        #   .filter(has_text="日志检索").click()
        # page.get_by_role("cell", name="外到内").locator("label").first.click()
        # page.get_by_role("table").locator("tbody").get_by_role("row").first.get_by_role("cell").nth(1).click()

        # 检查是否包含复杂链式调用
        has_complex_chain = (
            'get_by_' in line and (
                ('filter(' in line) or
                ('locator(' in line) or
                ('.first' in line) or
                ('.last' in line) or
                ('.nth(' in line) or
                (line.count('get_by_') > 1)  # 多个get_by_调用
            )
        )

        if not has_complex_chain:
            return None

        # 对于多重嵌套的get_by_调用，需要特殊处理
        if line.count('get_by_') > 1:
            return self._convert_nested_get_by_calls(line)

        # 提取基础定位器
        base_locator = self._extract_base_locator_with_params(line)
        if not base_locator:
            return None

        # 分析链式操作
        chain_info = self._analyze_chain_operations(line)

        # 构建最终的定位器字符串
        final_locator = self._build_final_locator(base_locator, chain_info)

        # 检查最终操作类型
        if '.click()' in line:
            return f'[点击元素], 定位器: "{final_locator}"'
        elif '.dblclick()' in line:
            return f'[双击元素], 定位器: "{final_locator}"'
        elif '.fill(' in line:
            text_match = re.search(r'\.fill\(["\']([^"\']*)["\']', line)
            text = text_match.group(1) if text_match else ""
            if text:
                return f'[输入文本], 定位器: "{final_locator}", 文本: "{text}"'
            else:
                return f'[清空文本], 定位器: "{final_locator}"'
        elif '.check()' in line:
            return f'[勾选复选框], 定位器: "{final_locator}"'
        elif '.uncheck()' in line:
            return f'[取消勾选复选框], 定位器: "{final_locator}"'
        elif '.press(' in line:
            key_match = re.search(r'\.press\(["\']([^"\']+)["\']', line)
            if key_match:
                key = key_match.group(1)
                return f'[按键操作], 定位器: "{final_locator}", 按键: "{key}"'

        return None

    def _convert_nested_get_by_calls(self, line: str) -> Optional[str]:
        """处理嵌套的get_by_调用，如：
        page.get_by_role("table").locator("tbody").get_by_role("row").first.get_by_role("cell").nth(1).click()
        """
        # 将复杂的嵌套调用转换为简化的定位器表示
        # 这种情况下，我们构建一个描述性的定位器字符串

        # 提取所有的get_by_调用
        get_by_matches = re.findall(r'get_by_(\w+)\([^)]+\)', line)

        if len(get_by_matches) < 2:
            return None

        # 构建描述性定位器
        locator_parts = []

        # 分析整个调用链
        parts = re.split(r'\.(?=get_by_|locator|first|last|nth)', line)

        for part in parts:
            if 'get_by_role(' in part:
                role_match = re.search(r'get_by_role\(["\']([^"\']+)["\'](?:,\s*name=["\']([^"\']*)["\'])?\)', part)
                if role_match:
                    role = role_match.group(1)
                    name = role_match.group(2) or ""
                    if name:
                        locator_parts.append(f"role={role}:{name}")
                    else:
                        locator_parts.append(f"role={role}")
            elif 'locator(' in part:
                locator_match = re.search(r'locator\(["\']([^"\']+)["\']', part)
                if locator_match:
                    selector = locator_match.group(1)
                    locator_parts.append(f"locator={selector}")
            elif 'first' in part:
                locator_parts.append("first=true")
            elif 'last' in part:
                locator_parts.append("last=true")
            elif 'nth(' in part:
                nth_match = re.search(r'nth\((\d+)\)', part)
                if nth_match:
                    index = nth_match.group(1)
                    locator_parts.append(f"nth={index}")

        # 组合所有部分
        final_locator = "&".join(locator_parts)

        # 检查最终操作类型
        if '.click()' in line:
            return f'[点击元素], 定位器: "{final_locator}"'
        elif '.fill(' in line:
            text_match = re.search(r'\.fill\(["\']([^"\']*)["\']', line)
            text = text_match.group(1) if text_match else ""
            if text:
                return f'[输入文本], 定位器: "{final_locator}", 文本: "{text}"'
            else:
                return f'[清空文本], 定位器: "{final_locator}"'

        return None

    def _extract_base_locator_with_params(self, line: str) -> \
            Optional[Dict[str, Any]]:
        """提取带参数的基础定位器"""

        # get_by_role with name parameter
        role_pattern = (r'get_by_role\(["\']([^"\']+)["\']'
                        r'(?:,\s*name=["\']([^"\']*)["\'])?\)')
        role_match = re.search(role_pattern, line)
        if role_match:
            role = role_match.group(1)
            name = role_match.group(2) or ""
            return {
                'type': 'role',
                'role': role,
                'name': name
            }

        # get_by_label with exact parameter
        label_pattern = (r'get_by_label\(["\']([^"\']+)["\']'
                         r'(?:,\s*exact=([^,\)]+))?\)')
        label_match = re.search(label_pattern, line)
        if label_match:
            label = label_match.group(1)
            exact = (label_match.group(2) == 'True'
                     if label_match.group(2) else False)
            return {
                'type': 'label',
                'label': label,
                'exact': exact
            }

        # get_by_text with exact parameter
        text_pattern = (r'get_by_text\(["\']([^"\']+)["\']'
                        r'(?:,\s*exact=([^,\)]+))?\)')
        text_match = re.search(text_pattern, line)
        if text_match:
            text = text_match.group(1)
            exact = (text_match.group(2) == 'True'
                     if text_match.group(2) else False)
            return {
                'type': 'text',
                'text': text,
                'exact': exact
            }

        # 其他基础定位器
        for method, pattern in [
            ('placeholder', r'get_by_placeholder\(["\']([^"\']+)["\']'),
            ('testid', r'get_by_test_id\(["\']([^"\']+)["\']'),
            ('title', r'get_by_title\(["\']([^"\']+)["\']'),
            ('alt', r'get_by_alt_text\(["\']([^"\']+)["\']'),
        ]:
            match = re.search(pattern, line)
            if match:
                return {
                    'type': method,
                    method: match.group(1)
                }

        return None

    def _analyze_chain_operations(self, line: str) -> Dict[str, Any]:
        """分析链式操作"""
        chain_info = {
            'has_locator': False,
            'locator_selector': None,
            'has_filter': False,
            'filter_has_text': None,
            'has_first': False,
            'has_last': False,
            'has_nth': False,
            'nth_index': None
        }

        # 检查 .locator()
        locator_match = re.search(r'\.locator\(["\']([^"\']+)["\']', line)
        if locator_match:
            chain_info['has_locator'] = True
            chain_info['locator_selector'] = locator_match.group(1)

        # 检查 .filter()
        filter_match = re.search(
            r'\.filter\(has_text=["\']([^"\']+)["\']', line)
        if filter_match:
            chain_info['has_filter'] = True
            chain_info['filter_has_text'] = filter_match.group(1)

        # 检查选择器
        if '.first' in line:
            chain_info['has_first'] = True
        elif '.last' in line:
            chain_info['has_last'] = True
        elif '.nth(' in line:
            nth_match = re.search(r'\.nth\((\d+)\)', line)
            if nth_match:
                chain_info['has_nth'] = True
                chain_info['nth_index'] = int(nth_match.group(1))

        return chain_info

    def _build_final_locator(self, base_locator: Dict[str, Any],
                             chain_info: Dict[str, Any]) -> str:
        """构建最终的定位器字符串"""

        # 构建基础定位器字符串
        if base_locator['type'] == 'role':
            if base_locator['name']:
                locator_str = (f"role={base_locator['role']}:"
                               f"{base_locator['name']}")
            else:
                locator_str = f"role={base_locator['role']}"
        elif base_locator['type'] == 'label':
            locator_str = f"label={base_locator['label']}"
            if base_locator.get('exact'):
                locator_str += ",exact=true"
        elif base_locator['type'] == 'text':
            locator_str = f"text={base_locator['text']}"
            if base_locator.get('exact'):
                locator_str += ",exact=true"
        else:
            # 其他类型
            key = base_locator['type']
            value = base_locator[key]
            locator_str = f"{key}={value}"

        # 处理链式操作
        modifiers = []

        # 如果有locator子选择器
        if chain_info['has_locator']:
            selector = chain_info['locator_selector']
            modifiers.append(f"locator={selector}")

        # 如果有filter
        if chain_info['has_filter']:
            filter_text = chain_info['filter_has_text']
            modifiers.append(f"has_text={filter_text}")

        # 如果有选择器（修复布尔值格式）
        if chain_info['has_first']:
            modifiers.append("first=true")
        elif chain_info['has_last']:
            modifiers.append("last=true")
        elif chain_info['has_nth']:
            index = chain_info['nth_index']
            modifiers.append(f"nth={index}")

        # 组合所有修饰符
        if modifiers:
            locator_str += "&" + "&".join(modifiers)

        return locator_str

    def _convert_chained_call(self, line: str) -> Optional[str]:
        """转换简单的链式调用"""
        # 对于 inner_text() 和 get_attribute() 调用，使用更智能的定位器提取
        if '.inner_text()' in line or '.get_attribute(' in line:
            locator = self._extract_locator_from_assignment(line)
            if not locator:
                # 回退到简单提取
                locator = self._extract_locator(line)
        else:
            # 对于其他操作，使用简单提取
            locator = self._extract_locator(line)

        if not locator:
            return None

        # 检查最终操作
        if '.click()' in line:
            return f'[点击元素], 定位器: "{locator}"'
        elif '.dblclick()' in line:
            return f'[双击元素], 定位器: "{locator}"'
        elif '.context_click()' in line:  # 右键点击
            return f'[右键点击元素], 定位器: "{locator}"'
        elif '.fill(' in line:
            # 改进文本提取，支持包含特殊字符的文本
            text_match = re.search(r'\.fill\(["\']([^"\']*(?:\\.[^"\']*)*)["\']', line)
            if not text_match:
                # 尝试匹配包含转义字符的文本
                text_match = re.search(r'\.fill\((["\'])([^"\']*(?:\\.[^"\']*)*)\1', line)
                if text_match:
                    text = text_match.group(2)
                else:
                    text = ""
            else:
                text = text_match.group(1)

            if text:  # 只有非空文本才输出
                # 处理文本中的特殊字符
                text = text.replace('\\"', '"').replace("\\'", "'")
                return f'[输入文本], 定位器: "{locator}", 文本: "{text}"'
            else:
                return f'[清空文本], 定位器: "{locator}"'
        elif '.type(' in line:  # 逐字符输入
            text_match = re.search(r'\.type\(["\']([^"\']+)["\']', line)
            if text_match:
                text = text_match.group(1)
                return f'[逐字符输入], 定位器: "{locator}", 文本: "{text}"'
        elif '.press(' in line:
            key_match = re.search(r'\.press\(["\']([^"\']+)["\']', line)
            if key_match:
                key = key_match.group(1)
                return f'[按键操作], 定位器: "{locator}", 按键: "{key}"'
        elif '.check()' in line:
            return f'[勾选复选框], 定位器: "{locator}"'
        elif '.uncheck()' in line:
            return f'[取消勾选复选框], 定位器: "{locator}"'
        elif '.set_checked(' in line:
            # 处理set_checked操作
            checked_match = re.search(r'\.set_checked\((True|False)\)', line)
            if checked_match:
                checked = checked_match.group(1) == 'True'
                return (f'[设置复选框状态], 定位器: "{locator}", '
                        f'选中状态: {checked}')
        elif '.select_option(' in line:
            # 支持多种选择方式：value, label, index
            value_match = re.search(
                r'\.select_option\(["\']([^"\']*)["\']', line)
            if value_match:
                option = value_match.group(1)
                return (f'[选择下拉选项], 定位器: "{locator}", '
                        f'选项值: "{option}"')
            # 检查是否是通过label选择
            label_match = re.search(
                r'\.select_option\(label=["\']([^"\']+)["\']', line)
            if label_match:
                label = label_match.group(1)
                return (f'[选择下拉选项], 定位器: "{locator}", '
                        f'选项标签: "{label}"')
            # 检查是否是通过index选择
            index_match = re.search(r'\.select_option\(index=(\d+)', line)
            if index_match:
                index = index_match.group(1)
                return (f'[选择下拉选项], 定位器: "{locator}", '
                        f'选项索引: {index}')
        elif '.hover()' in line:
            return f'[悬停元素], 定位器: "{locator}"'
        elif '.focus()' in line:
            return f'[聚焦元素], 定位器: "{locator}"'
        elif '.scroll_into_view_if_needed()' in line:
            return f'[滚动元素到视野], 定位器: "{locator}"'
        elif '.set_input_files(' in line:  # 文件上传
            file_match = re.search(
                r'\.set_input_files\(["\']([^"\']+)["\']', line)
            if file_match:
                file_path = file_match.group(1)
                return (f'[上传文件], 定位器: "{locator}", '
                        f'文件路径: "{file_path}"')
        elif '.inner_text()' in line:
            # 获取文本内容，转换为DSL格式
            # 尝试提取变量名
            var_name = self._extract_variable_name(line)
            if var_name:
                return f'{var_name} = [获取元素文本], 定位器: "{locator}"'
            else:
                return f'[获取元素文本], 定位器: "{locator}"'
        elif '.get_attribute(' in line:
            attr_match = re.search(
                r'\.get_attribute\(["\']([^"\']+)["\']', line)
            if attr_match:
                attr = attr_match.group(1)
                # 尝试提取变量名
                var_name = self._extract_variable_name(line)
                if var_name:
                    return f'{var_name} = [获取元素属性], 定位器: "{locator}", 属性: "{attr}"'
                else:
                    return f'[获取元素属性], 定位器: "{locator}", 属性: "{attr}"'

        return None

    def _extract_locator(self, line: str) -> Optional[str]:
        """从行中提取定位器"""
        # 处理 get_by_role
        role_pattern = (r'get_by_role\(["\']([^"\']+)["\']'
                        r'(?:,\s*name=["\']([^"\']*)["\'])?\)')
        role_match = re.search(role_pattern, line)
        if role_match:
            role = role_match.group(1)
            name = role_match.group(2) or ""
            if name:
                return f"role={role}:{name}"
            else:
                return f"role={role}"

        # 处理 get_by_text（支持exact参数）
        text_pattern = (r'get_by_text\(["\']([^"\']+)["\']'
                        r'(?:,\s*exact=([^,\)]+))?\)')
        text_match = re.search(text_pattern, line)
        if text_match:
            text = text_match.group(1)
            exact = (text_match.group(2) == 'True'
                     if text_match.group(2) else False)
            if exact:
                return f"text={text},exact=true"
            else:
                return f"text={text}"

        # 处理 get_by_label（支持exact参数）
        label_pattern = (r'get_by_label\(["\']([^"\']+)["\']'
                         r'(?:,\s*exact=([^,\)]+))?\)')
        label_match = re.search(label_pattern, line)
        if label_match:
            label = label_match.group(1)
            exact = (label_match.group(2) == 'True'
                     if label_match.group(2) else False)
            if exact:
                return f"label={label},exact=true"
            else:
                return f"label={label}"

        # 处理 get_by_placeholder
        placeholder_pattern = r'get_by_placeholder\(["\']([^"\']+)["\']'
        placeholder_match = re.search(placeholder_pattern, line)
        if placeholder_match:
            placeholder = placeholder_match.group(1)
            return f"placeholder={placeholder}"

        # 处理 get_by_test_id
        testid_pattern = r'get_by_test_id\(["\']([^"\']+)["\']'
        testid_match = re.search(testid_pattern, line)
        if testid_match:
            testid = testid_match.group(1)
            return f"testid={testid}"

        # 处理 get_by_title
        title_pattern = r'get_by_title\(["\']([^"\']+)["\']'
        title_match = re.search(title_pattern, line)
        if title_match:
            title = title_match.group(1)
            return f"title={title}"

        # 处理 get_by_alt_text
        alt_pattern = r'get_by_alt_text\(["\']([^"\']+)["\']'
        alt_match = re.search(alt_pattern, line)
        if alt_match:
            alt = alt_match.group(1)
            return f"alt={alt}"

        # 处理 get_by_id
        id_pattern = r'get_by_id\(["\']([^"\']+)["\']'
        id_match = re.search(id_pattern, line)
        if id_match:
            element_id = id_match.group(1)
            return f"#{element_id}"

        # 处理 get_by_tag
        tag_pattern = r'get_by_tag\(["\']([^"\']+)["\']'
        tag_match = re.search(tag_pattern, line)
        if tag_match:
            tag = tag_match.group(1)
            return tag

        # 处理 locator - 改进对复杂选择器的处理，包括包含引号的XPath
        # 先尝试匹配双引号包围的内容
        locator_pattern_double = r'locator\("([^"]*(?:\\.[^"]*)*)"\)'
        locator_match = re.search(locator_pattern_double, line)

        if not locator_match:
            # 再尝试匹配单引号包围的内容
            locator_pattern_single = r"locator\('([^']*(?:\\.[^']*)*)'\)"
            locator_match = re.search(locator_pattern_single, line)

        if locator_match:
            selector = locator_match.group(1)
            # 处理特殊的CSS和XPath前缀
            if selector.startswith('css='):
                return selector[4:]  # 去掉css=前缀
            elif selector.startswith('xpath='):
                return selector  # 保留xpath=前缀
            else:
                return selector

        return None

    def _convert_wait_operation(self, line: str, dsl_lines: list):
        """转换等待操作"""
        if '.wait_for_selector(' in line:
            selector_match = re.search(
                r'\.wait_for_selector\(["\']([^"\']+)["\']', line)
            if selector_match:
                selector = selector_match.group(1)
                dsl_lines.append(f'[等待元素出现], 定位器: "{selector}", 状态: "visible"')
        elif '.wait_for_load_state(' in line:
            state_match = re.search(
                r'\.wait_for_load_state\(["\']([^"\']+)["\']', line)
            if state_match:
                state = state_match.group(1)
                # 根据keywords.json，没有找到对应的等待页面状态关键字，使用注释
                dsl_lines.append(f'# 等待页面状态: {state} (需要手动处理)')
        elif '.wait_for_timeout(' in line:
            timeout_match = re.search(r'\.wait_for_timeout\((\d+)\)', line)
            if timeout_match:
                timeout = int(timeout_match.group(1)) / 1000  # 转换为秒
                dsl_lines.append(f'[等待], 秒数: {timeout}')
        elif '.wait_for_event(' in line and 'download' in line:
            # 处理等待下载事件 - 转换为监听下载关键字
            dsl_lines.append("[监听下载], 监听时间: 30, 变量名: \"download_events\"")
            dsl_lines.append("# 原代码: " + line)
        elif '.wait_for_event(' in line:
            # 处理其他事件等待
            event_match = re.search(
                r'\.wait_for_event\(["\']([^"\']+)["\']', line)
            if event_match:
                event = event_match.group(1)
                dsl_lines.append(f'# 等待{event}事件 (需要手动处理)')
            else:
                # 如果没有匹配到具体事件，也要处理这行
                dsl_lines.append(f'# 等待事件: {line} (需要手动处理)')

    def _convert_download_operation(self, script_content: str,
                                    current_line_index: int):
        """转换下载操作块"""
        lines = script_content.split('\n')
        dsl_lines = []
        i = current_line_index

        # 检查是否是expect_download模式
        current_line = lines[i].strip()

        if 'with page.expect_download()' in current_line:
            # 处理with expect_download模式
            dsl_lines.append("# 等待下载操作开始")
            i += 1

            # 查找触发下载的操作（通常是下一行的点击）
            trigger_found = False
            while i < len(lines) and not trigger_found:
                next_line = lines[i].strip()

                # 跳过空行和注释
                if not next_line or next_line.startswith('#'):
                    i += 1
                    continue

                # 找到触发操作
                if '.click(' in next_line or '.get_by_' in next_line:
                    # 尝试提取触发元素
                    locator = self._extract_locator(next_line)
                    if locator:
                        dsl_lines.append(
                            f'[等待下载], 触发元素: "{locator}", '
                            f'变量名: "download_path"')
                        trigger_found = True
                        i += 1
                        break
                    else:
                        # 如果无法提取定位器，直接转换为注释
                        dsl_lines.append(f'# 触发下载: {next_line}')
                        trigger_found = True
                        i += 1
                        break

                # 如果遇到其他操作，也停止查找
                if any(op in next_line for op in
                       ['.value', 'download =', 'download_info']):
                    i += 1
                    continue

                i += 1

            # 查找save_as操作和其他下载相关操作
            while i < len(lines):
                line = lines[i].strip()

                if not line or line.startswith('#'):
                    i += 1
                    continue

                if '.save_as(' in line:
                    path_match = re.search(
                        r'\.save_as\(["\']([^"\']+)["\']', line)
                    if path_match:
                        save_path = path_match.group(1)
                        dsl_lines.append(f'# 保存文件到: {save_path}')
                        dsl_lines.append('[验证下载文件], '
                                         '文件路径: "${download_path}"')
                    i += 1
                    continue

                # 处理wait_for_event下载事件
                if '.wait_for_event(' in line and 'download' in line:
                    dsl_lines.append("[监听下载], 监听时间: 30, "
                                     "变量名: \"download_events\"")
                    dsl_lines.append("# 原代码: " + line)
                    i += 1
                    continue

                # 遇到非下载相关的代码，停止处理
                if not any(keyword in line for keyword in
                           ['download', '.value', 'save_as',
                            'expect_download']):
                    break

                i += 1

        return dsl_lines, i

    def _convert_assertion(self, line: str, dsl_lines: list):
        """转换断言操作"""
        # 处理各种断言类型
        if 'to_have_text(' in line:
            text_match = re.search(r'to_have_text\(["\']([^"\']+)["\']', line)
            if text_match:
                text = text_match.group(1)
                locator = self._extract_locator_from_expect(line)
                if locator:
                    dsl_lines.append(f'[断言文本内容], 定位器: "{locator}", 期望文本: "{text}"')
                else:
                    dsl_lines.append(f'# 断言文本内容: {text} (需要手动处理定位器)')
        elif 'to_contain_text(' in line:
            text_match = re.search(r'to_contain_text\(["\']([^"\']+)["\']', line)
            if text_match:
                text = text_match.group(1)
                locator = self._extract_locator_from_expect(line)
                if locator:
                    dsl_lines.append(f'[断言文本内容], 定位器: "{locator}", 期望文本: "{text}", 匹配方式: "contains"')
                else:
                    dsl_lines.append(f'# 断言文本包含: {text} (需要手动处理定位器)')
        elif 'to_be_visible()' in line:
            locator = self._extract_locator_from_expect(line)
            if locator:
                dsl_lines.append(f'[断言元素可见], 定位器: "{locator}"')
            else:
                dsl_lines.append('# 断言元素可见 (需要手动处理定位器)')
        elif 'to_be_hidden()' in line:
            locator = self._extract_locator_from_expect(line)
            if locator:
                dsl_lines.append(f'[断言元素隐藏], 定位器: "{locator}"')
            else:
                dsl_lines.append('# 断言元素隐藏 (需要手动处理定位器)')
        elif 'to_be_enabled()' in line:
            locator = self._extract_locator_from_expect(line)
            if locator:
                dsl_lines.append(f'[断言元素启用], 定位器: "{locator}"')
            else:
                dsl_lines.append('# 断言元素启用 (需要手动处理定位器)')
        elif 'to_be_disabled()' in line:
            locator = self._extract_locator_from_expect(line)
            if locator:
                dsl_lines.append(f'[断言元素禁用], 定位器: "{locator}"')
            else:
                dsl_lines.append('# 断言元素禁用 (需要手动处理定位器)')
        elif 'to_be_checked()' in line:
            locator = self._extract_locator_from_expect(line)
            if locator:
                dsl_lines.append(f'[断言复选框状态], 定位器: "{locator}", 期望状态: True')
            else:
                dsl_lines.append('# 断言复选框选中 (需要手动处理定位器)')
        elif 'to_have_value(' in line:
            value_match = re.search(r'to_have_value\(["\']([^"\']+)["\']', line)
            if value_match:
                value = value_match.group(1)
                locator = self._extract_locator_from_expect(line)
                if locator:
                    dsl_lines.append(f'[断言输入值], 定位器: "{locator}", 期望值: "{value}"')
                else:
                    dsl_lines.append(f'# 断言输入值: {value} (需要手动处理定位器)')
        elif 'to_have_url(' in line:
            url_match = re.search(r'to_have_url\(["\']([^"\']+)["\']', line)
            if url_match:
                url = url_match.group(1)
                dsl_lines.append(f'[断言页面URL], 期望URL: "{url}"')
            else:
                dsl_lines.append('# 断言页面URL (需要手动处理)')
        elif 'to_have_title(' in line:
            title_match = re.search(r'to_have_title\(["\']([^"\']+)["\']', line)
            if title_match:
                title = title_match.group(1)
                dsl_lines.append(f'[断言页面标题], 期望标题: "{title}"')
            else:
                dsl_lines.append('# 断言页面标题 (需要手动处理)')
        elif 'to_have_class(' in line:
            class_match = re.search(r'to_have_class\(["\']([^"\']+)["\']', line)
            if class_match:
                class_name = class_match.group(1)
                locator = self._extract_locator_from_expect(line)
                if locator:
                    # 使用获取元素属性关键字来检查class
                    dsl_lines.append(f'# 断言元素class: {class_name} - 建议使用[获取元素属性]关键字检查')
                    dsl_lines.append(f'[获取元素属性], 定位器: "{locator}", 属性: "class", 变量名: "element_class"')
                else:
                    dsl_lines.append(f'# 断言元素class: {class_name} (需要手动处理定位器)')
        elif 'to_have_attribute(' in line:
            attr_match = re.search(r'to_have_attribute\(["\']([^"\']+)["\'](?:,\s*["\']([^"\']*)["\'])?\)', line)
            if attr_match:
                attr_name = attr_match.group(1)
                attr_value = attr_match.group(2) or ""
                locator = self._extract_locator_from_expect(line)
                if locator:
                    # 使用获取元素属性关键字
                    if attr_value:
                        dsl_lines.append(f'# 断言元素属性: {attr_name}="{attr_value}" - 建议使用[获取元素属性]关键字检查')
                        dsl_lines.append(f'[获取元素属性], 定位器: "{locator}", 属性: "{attr_name}", 变量名: "element_attr", 默认值: ""')
                    else:
                        dsl_lines.append(f'# 断言元素属性存在: {attr_name} - 建议使用[获取元素属性]关键字检查')
                        dsl_lines.append(f'[获取元素属性], 定位器: "{locator}", 属性: "{attr_name}", 变量名: "element_attr"')
                else:
                    dsl_lines.append(f'# 断言元素属性: {attr_name} (需要手动处理定位器)')
        else:
            # 处理其他未识别的断言
            dsl_lines.append(f'# 断言操作: {line.strip()} (需要手动转换)')

    def _extract_locator_from_expect(self, line: str) -> Optional[str]:
        """从expect语句中提取定位器"""
        # 从expect(page.get_by_xxx(...))中提取定位器
        # 处理复杂的expect语句，包括链式调用
        expect_match = re.search(r'expect\(page\.(.+?)\)\.to_', line)
        if expect_match:
            locator_part = expect_match.group(1)
            # 如果包含复杂的链式调用，需要特殊处理
            if 'get_by_' in locator_part and ('locator(' in locator_part or 'filter(' in locator_part):
                return self._extract_complex_locator_from_expect(locator_part)
            else:
                return self._extract_locator(locator_part)
        return None

    def _extract_complex_locator_from_expect(self, locator_part: str) -> Optional[str]:
        """从复杂的expect语句中提取定位器"""
        # 模拟完整的行来使用现有的复杂定位器提取逻辑
        mock_line = f"page.{locator_part}.click()"

        # 尝试使用复杂链式调用的提取逻辑
        if 'get_by_' in mock_line and ('filter(' in mock_line or 'locator(' in mock_line):
            base_locator = self._extract_base_locator_with_params(mock_line)
            if base_locator:
                chain_info = self._analyze_chain_operations(mock_line)
                return self._build_final_locator(base_locator, chain_info)

        # 如果复杂提取失败，尝试简单提取
        return self._extract_locator(locator_part)

    def _extract_locator_from_assignment(self, line: str) -> Optional[str]:
        """从赋值语句中提取定位器"""
        # 匹配如：text = page.get_by_xxx(...).nth(1).inner_text()
        # 或：attr = page.get_by_xxx(...).nth(0).get_attribute(...)

        # 更精确的正则表达式，匹配从page.到方法调用之前的所有内容
        assignment_match = re.search(
            r'=\s*page\.(.+?)\.(inner_text|text_content|get_attribute)\([^)]*\)', line)
        if assignment_match:
            locator_part = assignment_match.group(1)
            return self._parse_complex_locator_chain(locator_part)

        # 匹配简单的定位器调用：page.get_by_xxx(...).method()
        page_match = re.search(
            r'page\.(.+?)\.(inner_text|text_content|get_attribute)\([^)]*\)', line)
        if page_match:
            locator_part = page_match.group(1)
            return self._parse_complex_locator_chain(locator_part)

        return None

    def _parse_complex_locator_chain(self, locator_part: str) -> Optional[str]:
        """解析复杂的定位器链，支持 nth(), first, last 等"""
        # 直接分析定位器链并构建DSL格式
        if 'get_by_' in locator_part:
            # 提取基础定位器
            base_locator = self._extract_locator(locator_part)
            if not base_locator:
                return None

            # 分析链式操作
            chain_info = self._analyze_chain_operations(f"page.{locator_part}.click()")

            # 构建完整的定位器字符串
            modifiers = []

            # 如果有locator子选择器
            if chain_info['has_locator']:
                selector = chain_info['locator_selector']
                modifiers.append(f"locator={selector}")

            # 如果有filter
            if chain_info['has_filter']:
                filter_text = chain_info['filter_has_text']
                modifiers.append(f"has_text={filter_text}")

            # 如果有选择器
            if chain_info['has_first']:
                modifiers.append("first=true")
            elif chain_info['has_last']:
                modifiers.append("last=true")
            elif chain_info['has_nth']:
                index = chain_info['nth_index']
                modifiers.append(f"nth={index}")

            # 组合所有修饰符
            if modifiers:
                return base_locator + "&" + "&".join(modifiers)
            else:
                return base_locator

        # 如果不是get_by_调用，使用简单提取
        return self._extract_locator(locator_part)

    def _extract_variable_name(self, line: str) -> Optional[str]:
        """从赋值语句中提取变量名"""
        # 匹配如：var_name = page.get_by_xxx(...).inner_text()
        # 或：attr = page.get_by_xxx(...).get_attribute(...)
        var_match = re.search(r'^\s*(\w+)\s*=\s*page\.', line.strip())
        if var_match:
            return var_match.group(1)
        return None


def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(
        description='将Playwright Python脚本转换为DSL语法')
    parser.add_argument('input_file', help='输入的Python脚本文件路径')
    parser.add_argument('-o', '--output', help='输出的DSL文件路径（可选）')

    args = parser.parse_args()

    # 读取输入文件
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"错误: 输入文件 {input_path} 不存在")
        return 1

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
    except Exception as e:
        print(f"错误: 无法读取输入文件: {e}")
        return 1

    # 转换脚本
    converter = PlaywrightToDSLConverter()
    dsl_content = converter.convert_script(script_content)

    # 输出结果
    if args.output:
        output_path = Path(args.output)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(dsl_content)
            print(f"转换完成! DSL文件已保存到: {output_path}")
        except Exception as e:
            print(f"错误: 无法写入输出文件: {e}")
            return 1
    else:
        print("转换结果:")
        print("=" * 50)
        print(dsl_content)

    return 0


if __name__ == '__main__':
    sys.exit(main())
