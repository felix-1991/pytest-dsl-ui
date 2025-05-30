#!/usr/bin/env python3
"""开发环境设置脚本

自动设置pytest-dsl-ui开发环境，包括依赖安装、浏览器安装等。
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, check=True, shell=False):
    """运行命令并处理输出"""
    print(f"执行命令: {command}")
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=check, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stdout:
            print(f"标准输出: {e.stdout}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"错误: 需要Python 3.9+，当前版本: {version.major}.{version.minor}")
        sys.exit(1)
    print(f"Python版本检查通过: {version.major}.{version.minor}.{version.micro}")


def setup_virtual_environment():
    """设置虚拟环境"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("虚拟环境已存在，跳过创建")
        return
    
    print("创建虚拟环境...")
    run_command("python -m venv venv")
    
    # 激活虚拟环境的说明
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate"
    
    print(f"虚拟环境创建完成！")
    print(f"请手动激活虚拟环境: {activate_cmd}")


def install_dependencies(dev=True):
    """安装依赖"""
    print("安装Python依赖...")
    
    # 升级pip
    run_command("python -m pip install --upgrade pip")
    
    # 安装项目依赖
    if dev:
        run_command("pip install -e .[dev]")
    else:
        run_command("pip install -e .")


def install_playwright_browsers(browsers=None):
    """安装Playwright浏览器"""
    print("安装Playwright浏览器...")
    
    if browsers is None:
        browsers = ["chromium"]  # 默认只安装chromium
    
    for browser in browsers:
        print(f"安装 {browser}...")
        run_command(f"playwright install {browser}")
    
    # 安装系统依赖（Linux）
    if sys.platform.startswith('linux'):
        print("安装系统依赖...")
        run_command("playwright install-deps", check=False)


def create_example_files():
    """创建示例文件"""
    print("创建示例文件...")
    
    # 创建测试目录
    test_dir = Path("my_tests")
    test_dir.mkdir(exist_ok=True)
    
    # 创建简单示例
    simple_test = test_dir / "simple_ui_test.dsl"
    if not simple_test.exists():
        simple_test.write_text('''@name: "我的第一个UI测试"
@description: "使用pytest-dsl-ui进行UI自动化测试"

# 启动浏览器
[启动浏览器], 浏览器: "chromium", 无头模式: false

# 打开测试页面
[打开页面], 地址: "https://example.com"

# 等待页面加载
[等待元素出现], 定位器: "h1"

# 获取页面标题
title = [获取页面标题]
[打印], 内容: "页面标题: ${title}"

# 断言页面内容
[断言文本内容], 定位器: "h1", 预期文本: "Example Domain"

# 截图
[截图], 文件名: "example_page.png"

# 关闭浏览器
[关闭浏览器]
''')
        print(f"创建示例文件: {simple_test}")
    
    # 创建配置文件示例
    config_file = Path("config.yaml")
    if not config_file.exists():
        config_file.write_text('''# pytest-dsl-ui 配置文件示例

ui_config:
  default_browser: "chromium"
  default_headless: false
  default_timeout: 30
  screenshot_dir: "screenshots"
  video_dir: "videos"
  viewport:
    width: 1920
    height: 1080

# 测试数据
test_data:
  base_url: "https://example.com"
  username: "testuser"
  password: "testpass"
''')
        print(f"创建配置文件: {config_file}")


def run_verification_test():
    """运行验证测试"""
    print("运行验证测试...")
    
    # 检查是否有示例文件
    test_file = Path("my_tests/simple_ui_test.dsl")
    if test_file.exists():
        print("运行示例测试...")
        result = run_command(f"pytest-dsl {test_file}", check=False)
        if result.returncode == 0:
            print("✅ 验证测试通过！pytest-dsl-ui安装成功！")
        else:
            print("❌ 验证测试失败，请检查安装")
    else:
        print("跳过验证测试（没有找到测试文件）")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="pytest-dsl-ui开发环境设置")
    parser.add_argument("--no-venv", action="store_true", help="跳过虚拟环境创建")
    parser.add_argument("--no-browsers", action="store_true", help="跳过浏览器安装")
    parser.add_argument("--browsers", nargs="+", default=["chromium"], 
                       help="要安装的浏览器 (chromium, firefox, webkit)")
    parser.add_argument("--no-examples", action="store_true", help="跳过示例文件创建")
    parser.add_argument("--no-test", action="store_true", help="跳过验证测试")
    parser.add_argument("--production", action="store_true", help="生产环境安装（不安装开发依赖）")
    
    args = parser.parse_args()
    
    print("🚀 开始设置pytest-dsl-ui开发环境...")
    print("=" * 50)
    
    # 检查Python版本
    check_python_version()
    
    # 设置虚拟环境
    if not args.no_venv:
        setup_virtual_environment()
    
    # 安装依赖
    install_dependencies(dev=not args.production)
    
    # 安装浏览器
    if not args.no_browsers:
        install_playwright_browsers(args.browsers)
    
    # 创建示例文件
    if not args.no_examples:
        create_example_files()
    
    # 运行验证测试
    if not args.no_test:
        run_verification_test()
    
    print("=" * 50)
    print("🎉 pytest-dsl-ui开发环境设置完成！")
    print()
    print("下一步:")
    if not args.no_venv:
        if os.name == 'nt':
            print("1. 激活虚拟环境: venv\\Scripts\\activate")
        else:
            print("1. 激活虚拟环境: source venv/bin/activate")
    print("2. 运行示例测试: pytest-dsl my_tests/simple_ui_test.dsl")
    print("3. 查看文档: README.md")
    print("4. 开始编写你的UI测试！")


if __name__ == "__main__":
    main()
