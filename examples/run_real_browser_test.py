#!/usr/bin/env python3
"""真实浏览器API测试运行器

使用非headless模式运行浏览器API测试，验证浏览器HTTP功能
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent.parent
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
    
    # 复制配置文件到config目录
    config_source = project_root / "examples" / "test_config_real.yaml"
    config_target = project_root / "config" / "test_config_real.yaml"
    
    if config_source.exists():
        import shutil
        shutil.copy2(config_source, config_target)
        print(f"📋 复制配置文件到: config/test_config_real.yaml")

def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")
    
    required_packages = [
        "pytest",
        "pytest-dsl", 
        "playwright",
        "jsonpath-ng",
        "pyyaml",
        "requests"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "pyyaml":
                __import__("yaml")
            elif package == "jsonpath-ng":
                __import__("jsonpath_ng")
            else:
                __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} (缺失)")
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install " + " ".join(missing_packages))
        return False
    
    return True

def run_browser_test():
    """运行浏览器测试"""
    print("\n🚀 启动浏览器API测试...")
    print("=" * 60)
    
    # DSL文件路径
    dsl_file = project_root / "examples" / "test_browser_api_real.dsl"
    
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
        # 使用pytest-dsl运行DSL文件
        cmd = [
            sys.executable, "-m", "pytest",
            str(dsl_file),
            "-v", "-s",
            "--tb=short",
            "--config-dir", str(project_root / "config"),
            "--var-file", "test_config_real.yaml"
        ]
        
        print(f"🔧 执行命令: {' '.join(cmd)}")
        print("🌐 即将打开浏览器窗口，请注意观察...")
        print("⏱️  测试过程中浏览器会自动执行各种操作")
        print()
        
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
            
            # 检查生成的文件
            check_generated_files()
            
            return True
        else:
            print(f"\n❌ 测试失败，退出码: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n💥 运行测试时出错: {str(e)}")
        return False

def check_generated_files():
    """检查生成的文件"""
    print("\n📂 检查生成的文件...")
    
    files_to_check = [
        "screenshots/browser_api_test_completed.png",
        "videos/",
        "downloads/"
    ]
    
    for file_path in files_to_check:
        full_path = project_root / file_path
        if full_path.exists():
            if full_path.is_file():
                size = full_path.stat().st_size
                print(f"✅ {file_path} ({size:,} bytes)")
            else:
                count = len(list(full_path.iterdir()))
                print(f"✅ {file_path} ({count} 个文件)")
        else:
            print(f"⚠️  {file_path} (未生成)")

def main():
    """主函数"""
    print("=" * 60)
    print("🌐 pytest-dsl-ui 真实浏览器API测试")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 设置环境
    setup_environment()
    
    print("\n📖 测试说明:")
    print("  1. 将启动非headless模式的Chromium浏览器")
    print("  2. 浏览器会自动访问JSONPlaceholder API")
    print("  3. 执行一系列HTTP请求测试(GET/POST/PUT/PATCH/DELETE)")
    print("  4. 验证响应数据和断言")
    print("  5. 捕获变量并在后续请求中使用")
    print("  6. 最后会截图保存测试结果")
    
    input("\n按回车键开始测试...")
    
    # 运行测试
    success = run_browser_test()
    
    if success:
        print("\n✨ 恭喜！浏览器API测试验证成功")
        print("🔍 您可以查看以下内容:")
        print("  - screenshots/ 目录中的截图")
        print("  - videos/ 目录中的录屏(如果启用)")
        print("  - 控制台输出的详细测试日志")
    else:
        print("\n⚠️  测试过程中遇到问题，请检查错误信息")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 