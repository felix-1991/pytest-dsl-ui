#!/usr/bin/env python3
"""
pytest-dsl-ui 包的主入口点

支持通过 python -m pytest_dsl_ui 运行
"""

import sys
import argparse
from pathlib import Path


def show_help():
    """显示帮助信息"""
    help_text = """
pytest-dsl-ui 工具集

用法:
    python -m pytest_dsl_ui <command> [options]
    
命令:
    convert      - 转换Playwright脚本为DSL格式
    help         - 显示帮助信息
    
示例:
    # 转换Playwright脚本
    python -m pytest_dsl_ui convert script.py output.dsl
    
    # 显示帮助
    python -m pytest_dsl_ui help
    """
    print(help_text.strip())


def convert_command(args):
    """处理转换命令"""
    if len(args) < 1:
        print("错误: convert命令需要输入文件")
        print("用法: python -m pytest_dsl_ui convert <input_file> [output_file]")
        return 1
    
    # 导入转换器
    try:
        from .utils.playwright_converter import PlaywrightToDSLConverter
    except ImportError:
        print("错误: 无法导入playwright_converter模块")
        return 1
    
    input_file = args[0]
    output_file = args[1] if len(args) > 1 else None
    
    # 检查输入文件
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"错误: 输入文件 {input_path} 不存在")
        return 1
    
    try:
        # 读取文件
        with open(input_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # 转换
        converter = PlaywrightToDSLConverter()
        dsl_content = converter.convert_script(script_content)
        
        # 输出结果
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(dsl_content)
            print(f"转换完成! DSL文件已保存到: {output_path}")
        else:
            print("转换结果:")
            print("=" * 50)
            print(dsl_content)
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}")
        return 1


def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return 0
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    if command == 'convert':
        return convert_command(args)
    elif command == 'help':
        show_help()
        return 0
    else:
        print(f"错误: 未知命令 '{command}'")
        show_help()
        return 1


if __name__ == '__main__':
    sys.exit(main()) 