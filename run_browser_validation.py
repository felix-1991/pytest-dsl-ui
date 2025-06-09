#!/usr/bin/env python3
"""真实浏览器HTTP实现验证脚本

用于验证浏览器HTTP实现修复效果的完整测试
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_environment():
    """设置测试环境"""
    print("🔧 设置测试环境...")
    
    # 切换到项目根目录
    os.chdir(project_root)
    
    # 创建必要的目录
    directories = ["screenshots", "videos", "downloads", "config"]
    for dir_name in directories:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            dir_path.mkdir()
            print(f"📁 创建目录: {dir_name}")
    
    # 复制配置文件
    config_source = project_root / "examples" / "config" / "test_simple_config.yaml"
    config_target = project_root / "config" / "test_simple_config.yaml"
    
    if config_source.exists():
        import shutil
        shutil.copy2(config_source, config_target)
        print(f"📋 复制配置文件到: config/test_simple_config.yaml")

def check_playwright_installation():
    """检查Playwright浏览器是否安装"""
    print("🔍 检查Playwright浏览器安装状态...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--help"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Playwright已安装")
            
            # 尝试安装浏览器
            print("🔧 确保浏览器已安装...")
            install_result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                capture_output=True,
                text=True
            )
            
            if install_result.returncode == 0:
                print("✅ Chromium浏览器已安装")
                return True
            else:
                print(f"⚠️  浏览器安装警告: {install_result.stderr}")
                return True  # 继续尝试，可能已经安装了
        else:
            print("❌ Playwright未安装，请运行: pip install playwright")
            return False
            
    except Exception as e:
        print(f"⚠️  检查Playwright时出错: {str(e)}")
        return False

def run_browser_test():
    """运行浏览器测试"""
    print("\n🚀 启动真实浏览器HTTP测试...")
    print("=" * 60)
    
    # DSL文件路径
    dsl_file = project_root / "examples" / "test_browser_http_simple.dsl"
    
    if not dsl_file.exists():
        print(f"❌ DSL文件不存在: {dsl_file}")
        return False
    
    print(f"📄 DSL文件: {dsl_file}")
    print(f"📁 工作目录: {project_root}")
    
    # 设置环境变量
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    env["DSL_CONFIG_DIR"] = str(project_root / "config")
    
    try:
        # 使用pytest-dsl命令行工具运行DSL文件
        cmd = [
            "pytest-dsl",
            str(dsl_file),
            "--yaml-vars", str(project_root / "config" / "test_simple_config.yaml")
        ]
        
        print(f"🔧 执行命令: {' '.join(cmd)}")
        print("🌐 即将打开浏览器窗口，请注意观察...")
        print("⏱️  测试过程包含多个HTTP请求，请耐心等待...")
        print()
        
        # 倒计时
        for i in range(3, 0, -1):
            print(f"⏰ {i}秒后开始...")
            time.sleep(1)
        
        print("🏁 开始测试！")
        
        # 运行测试
        result = subprocess.run(
            cmd,
            cwd=project_root,
            env=env,
            capture_output=False,  # 允许实时输出
            text=True
        )
        
        if result.returncode == 0:
            print("\n🎉 测试成功完成！")
            return True
        else:
            print(f"\n❌ 测试失败，退出码: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n💥 运行测试时出错: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🌐 pytest-dsl-ui 浏览器HTTP实现验证")
    print("=" * 60)
    
    # 检查Playwright安装
    if not check_playwright_installation():
        print("\n❌ Playwright未正确安装，无法继续测试")
        return False
    
    # 设置环境
    setup_environment()
    
    print("\n📖 测试说明:")
    print("  1. 启动非headless模式的Chromium浏览器")
    print("  2. 浏览器会访问JSONPlaceholder API进行HTTP测试")
    print("  3. 测试各种HTTP方法: GET, POST, PUT, PATCH, DELETE")
    print("  4. 验证JSONPath提取、断言逻辑、变量捕获等功能")
    print("  5. 测试复杂断言参数解析和错误处理")
    print("  6. 最后会截图并显示测试结果")
    
    print("\n🎯 验证重点:")
    print("  - 断言参数解析的完整性")
    print("  - JSONPath提取器的正确性")
    print("  - 类型断言和长度断言")
    print("  - 错误格式化和异常处理")
    print("  - 变量捕获和传递")
    
    input("\n按回车键开始验证测试...")
    
    # 运行测试
    success = run_browser_test()
    
    if success:
        print("\n✨ 恭喜！浏览器HTTP实现验证成功")
        print("✅ 所有关键功能都已正确实现")
        print("🔧 修复效果验证通过")
    else:
        print("\n⚠️  验证过程中遇到问题")
        print("🔍 请检查控制台输出以获取详细错误信息")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 