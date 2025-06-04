#!/usr/bin/env python3
"""
便捷的Playwright到DSL转换脚本

用法:
    python playwright2dsl.py input.py [output.dsl]
    python playwright2dsl.py input.py --output output.dsl
"""

import sys
import subprocess
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from pytest_dsl_ui.utils.playwright_converter import main
except ImportError:
    # 如果无法导入，尝试直接运行
    print("警告: 无法导入playwright_converter模块，尝试直接运行...")
    script_path = (Path(__file__).parent / "pytest_dsl_ui" / "utils" /
                   "playwright_converter.py")
    sys.exit(subprocess.call([sys.executable, str(script_path)] +
                             sys.argv[1:]))


def show_help():
    """显示帮助信息"""
    help_text = """
Playwright Python脚本转DSL语法工具

用法:
    python playwright2dsl.py <input_file> [output_file]
    
参数:
    input_file   - 输入的Playwright Python脚本文件
    output_file  - (可选) 输出的DSL文件路径
    
选项:
    -h, --help   - 显示此帮助信息
    -o, --output - 指定输出文件路径
    
示例:
    # 转换并输出到控制台
    python playwright2dsl.py recorded_script.py
    
    # 转换并保存到文件
    python playwright2dsl.py recorded_script.py test_case.dsl
    python playwright2dsl.py recorded_script.py -o test_case.dsl
    
说明:
    该工具可以将playwright codegen录制的Python脚本转换为
    pytest-dsl-ui的DSL语法格式，支持以下转换:
    
    - 浏览器启动和配置
    - 页面导航 (goto)
    - 元素定位 (get_by_*)
    - 点击操作 (click, dblclick)
    - 文本输入 (fill)
    - 键盘操作 (press)
    - 复选框操作 (check, uncheck)
    - 下拉选择 (select_option)
    - 截图操作 (screenshot)
    - 等待操作 (wait_for_*)
    - 断言操作 (expect)
    """
    print(help_text.strip())


def quick_convert():
    """快速转换入口"""
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        show_help()
        return 0
    
    # 重新组织参数以符合main函数的期望
    new_args = ['playwright2dsl.py']  # 脚本名
    
    input_file = None
    output_file = None
    i = 1
    
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg in ['-o', '--output']:
            if i + 1 < len(sys.argv):
                output_file = sys.argv[i + 1]
                i += 2
            else:
                print("错误: -o/--output 需要指定文件路径")
                return 1
        elif not input_file:
            input_file = arg
            i += 1
        elif not output_file:
            output_file = arg
            i += 1
        else:
            print(f"错误: 未知参数 {arg}")
            return 1
    
    if not input_file:
        print("错误: 请指定输入文件")
        show_help()
        return 1
    
    # 构建参数列表
    new_args.append(input_file)
    if output_file:
        new_args.extend(['-o', output_file])
    
    # 替换sys.argv
    original_argv = sys.argv[:]
    sys.argv = new_args
    
    try:
        return main()
    finally:
        sys.argv = original_argv


if __name__ == '__main__':
    sys.exit(quick_convert()) 