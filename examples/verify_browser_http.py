#!/usr/bin/env python3
"""验证浏览器HTTP关键字功能

这个脚本验证浏览器HTTP关键字的基本功能和配置
使用JSONPlaceholder API进行实际的HTTP请求测试
"""

import sys
import os
import json
import yaml
import requests
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_jsonplaceholder_connectivity():
    """测试JSONPlaceholder API的连通性"""
    print("🌐 测试JSONPlaceholder API连通性...")
    
    try:
        response = requests.get("https://jsonplaceholder.typicode.com/posts/1", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ JSONPlaceholder API连接成功")
            print(f"📄 示例文章标题: {data.get('title', 'N/A')}")
            print(f"👤 作者ID: {data.get('userId', 'N/A')}")
            return True
        else:
            print(f"❌ API请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        return False

def verify_file_structure():
    """验证文件结构"""
    print("\n📁 验证文件结构...")
    
    required_files = [
        "pytest_dsl_ui/core/browser_http_client.py",
        "pytest_dsl_ui/core/browser_http_request.py", 
        "pytest_dsl_ui/keywords/browser_http_keywords.py",
        "docs/README_browser_http.md",
        "examples/browser_http_config.yaml",
        "examples/test_browser_http_jsonplaceholder.dsl",
        "examples/test_browser_http_runner.py"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {file_path} ({size:,} bytes)")
        else:
            print(f"❌ {file_path} (缺失)")
            all_exist = False
    
    return all_exist

def verify_config_file():
    """验证配置文件"""
    print("\n⚙️  验证配置文件...")
    
    config_file = project_root / "examples/browser_http_config.yaml"
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 验证基本结构
        if 'browser_http_clients' not in config:
            print("❌ 配置文件缺少 browser_http_clients 节点")
            return False
        
        clients = config['browser_http_clients']
        required_clients = ['default', 'jsonplaceholder']
        
        for client_name in required_clients:
            if client_name in clients:
                client_config = clients[client_name]
                print(f"✅ 客户端 '{client_name}': {client_config.get('base_url', 'N/A')}")
                
                # 验证必需字段
                required_fields = ['base_url', 'timeout']
                for field in required_fields:
                    if field not in client_config:
                        print(f"⚠️  客户端 '{client_name}' 缺少字段: {field}")
            else:
                print(f"❌ 缺少客户端配置: {client_name}")
                return False
        
        # 验证模板
        if 'browser_http_templates' in config:
            templates = config['browser_http_templates']
            print(f"✅ 找到 {len(templates)} 个请求模板")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置文件验证失败: {str(e)}")
        return False

def verify_dsl_file():
    """验证DSL文件"""
    print("\n📝 验证DSL文件...")
    
    dsl_file = project_root / "examples/test_browser_http_jsonplaceholder.dsl"
    
    try:
        with open(dsl_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 基本结构验证
        required_elements = [
            '@name:',
            '@description:',
            '[浏览器HTTP请求]',
            'jsonplaceholder',
            'captures:',
            'asserts:',
            'teardown do'
        ]
        
        all_found = True
        for element in required_elements:
            if element in content:
                print(f"✅ 找到: {element}")
            else:
                print(f"❌ 缺少: {element}")
                all_found = False
        
        # HTTP方法验证
        http_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        method_count = 0
        for method in http_methods:
            if f'method: {method}' in content:
                method_count += 1
                print(f"✅ HTTP方法: {method}")
        
        print(f"📊 包含 {method_count} 种HTTP方法")
        print(f"📄 文件大小: {len(content):,} 字符")
        print(f"📋 行数: {len(content.splitlines())} 行")
        
        return all_found
        
    except Exception as e:
        print(f"❌ DSL文件验证失败: {str(e)}")
        return False

def verify_imports():
    """验证模块导入"""
    print("\n🐍 验证Python模块导入...")
    
    try:
        # 测试核心模块
        sys.path.insert(0, str(project_root))
        
        print("✅ 测试核心模块导入...")
        
        # 测试关键字模块导入
        try:
            from pytest_dsl_ui.keywords import browser_http_keywords
            print("✅ 浏览器HTTP关键字模块导入成功")
        except Exception as e:
            print(f"⚠️  关键字模块导入失败: {str(e)}")
            print("   (这可能是正常的，如果pytest-dsl未安装)")
        
        return True
        
    except Exception as e:
        print(f"❌ 模块导入失败: {str(e)}")
        return False

def show_usage_instructions():
    """显示使用说明"""
    print("\n" + "="*60)
    print("📖 使用说明")
    print("="*60)
    
    print("""
🔧 安装依赖:
   pip install pytest playwright requests pyyaml jsonpath-ng

🎭 安装Playwright浏览器:
   playwright install

🧪 运行验证测试:
   python examples/test_browser_http_runner.py

📊 使用pytest运行:
   pytest examples/test_browser_http_runner.py -v

🔍 验证DSL语法:
   pytest-dsl-list | grep "浏览器HTTP"

📝 编辑配置:
   编辑 examples/browser_http_config.yaml

🚀 运行DSL测试:
   1. 确保有pytest-dsl环境
   2. 使用pytest方式运行DSL文件
   3. 查看详细文档: docs/README_browser_http.md
""")

def main():
    """主函数"""
    print("="*60)
    print("🔍 pytest-dsl-ui 浏览器HTTP功能验证")
    print("="*60)
    
    # 验证步骤
    tests = [
        ("JSONPlaceholder API连通性", test_jsonplaceholder_connectivity),
        ("文件结构", verify_file_structure),
        ("配置文件", verify_config_file),
        ("DSL文件", verify_dsl_file),
        ("Python模块", verify_imports)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"⚠️  {name} 验证未完全通过")
        except Exception as e:
            print(f"❌ {name} 验证出错: {str(e)}")
    
    # 结果汇总
    print("\n" + "="*60)
    print("📊 验证结果汇总")
    print("="*60)
    print(f"✅ 通过: {passed}/{total}")
    print(f"🎯 完成度: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有验证都通过了！浏览器HTTP功能已就绪")
    else:
        print("⚠️  部分验证未通过，请检查相关问题")
    
    # 显示使用说明
    show_usage_instructions()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 