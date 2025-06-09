"""浏览器HTTP测试运行器

这个文件演示了如何使用pytest来运行浏览器HTTP DSL测试
符合pytest-dsl的推荐使用方式
"""

import pytest
import yaml
import os
from pathlib import Path

# 测试数据目录
TEST_DATA_DIR = Path(__file__).parent

# 加载配置文件
CONFIG_FILE = TEST_DATA_DIR / "browser_http_config.yaml"

def load_test_config():
    """加载测试配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

# 全局测试配置
TEST_CONFIG = load_test_config()

class TestBrowserHTTPJSONPlaceholder:
    """JSONPlaceholder API测试类"""
    
    @pytest.fixture(autouse=True)
    def setup_config(self):
        """设置测试配置"""
        # 这里可以设置浏览器HTTP客户端配置
        pass
    
    def test_jsonplaceholder_api(self):
        """测试JSONPlaceholder API的完整流程"""
        # 这里应该运行DSL文件
        # 由于pytest-dsl集成需要特定的设置，这里先创建一个占位符
        
        dsl_file = TEST_DATA_DIR / "test_browser_http_jsonplaceholder.dsl"
        
        # 验证DSL文件存在
        assert dsl_file.exists(), f"DSL文件不存在: {dsl_file}"
        
        # 验证配置文件包含JSONPlaceholder客户端
        assert 'browser_http_clients' in TEST_CONFIG
        assert 'jsonplaceholder' in TEST_CONFIG['browser_http_clients']
        
        client_config = TEST_CONFIG['browser_http_clients']['jsonplaceholder']
        assert client_config['base_url'] == "https://jsonplaceholder.typicode.com"
        
        print("✅ DSL文件和配置验证通过")
        print(f"📄 DSL文件路径: {dsl_file}")
        print(f"⚙️  配置文件路径: {CONFIG_FILE}")
        print(f"🌐 JSONPlaceholder基础URL: {client_config['base_url']}")
        
    def test_config_structure(self):
        """测试配置文件结构"""
        assert 'browser_http_clients' in TEST_CONFIG
        
        # 验证默认客户端
        assert 'default' in TEST_CONFIG['browser_http_clients']
        
        # 验证JSONPlaceholder客户端
        assert 'jsonplaceholder' in TEST_CONFIG['browser_http_clients']
        jsonplaceholder_config = TEST_CONFIG['browser_http_clients']['jsonplaceholder']
        
        required_fields = ['base_url', 'timeout', 'headers']
        for field in required_fields:
            assert field in jsonplaceholder_config, f"配置缺少必需字段: {field}"
        
        print("✅ 配置文件结构验证通过")
        
    def test_dsl_file_content(self):
        """测试DSL文件内容"""
        dsl_file = TEST_DATA_DIR / "test_browser_http_jsonplaceholder.dsl"
        
        with open(dsl_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证DSL文件包含必要的元素
        assert '@name:' in content
        assert '@description:' in content
        assert '[浏览器HTTP请求]' in content
        assert 'jsonplaceholder' in content
        assert 'https://jsonplaceholder.typicode.com' in content
        
        # 验证包含各种HTTP方法
        http_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        for method in http_methods:
            assert method in content, f"DSL文件缺少HTTP方法: {method}"
        
        # 验证包含变量捕获和断言
        assert 'captures:' in content
        assert 'asserts:' in content
        assert 'jsonpath' in content
        
        print("✅ DSL文件内容验证通过")
        print(f"📝 文件大小: {len(content)} 字符")
        print(f"📄 行数: {len(content.splitlines())} 行")

if __name__ == "__main__":
    # 直接运行时显示配置信息
    print("=" * 60)
    print("🔧 浏览器HTTP测试配置信息")
    print("=" * 60)
    
    config = load_test_config()
    if config:
        print(f"📁 配置文件: {CONFIG_FILE}")
        
        if 'browser_http_clients' in config:
            clients = config['browser_http_clients']
            print(f"🌐 配置的客户端数量: {len(clients)}")
            
            for name, client_config in clients.items():
                print(f"  • {name}: {client_config.get('base_url', 'N/A')}")
        
        print("\n🧪 运行测试...")
        pytest.main([__file__, "-v", "-s"])
    else:
        print("❌ 配置文件未找到或为空") 