#!/usr/bin/env python3
"""DSL测试运行器

用于直接运行DSL文件进行测试
"""

import sys
import yaml
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def load_config(config_file_path):
    """加载配置文件"""
    with open(config_file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def run_dsl_test(dsl_file_path, config_file_path):
    """运行DSL测试"""
    print(f"📄 运行DSL文件: {dsl_file_path}")
    print(f"⚙️  配置文件: {config_file_path}")
    
    # 加载配置
    config = load_config(config_file_path)
    print(f"✅ 配置加载成功")
    
    # 导入必要的模块
    from pytest_dsl_ui.core.yaml_vars import yaml_vars
    from pytest_dsl_ui.core.dsl_executor import DSLExecutor
    from pytest_dsl_ui.core.context import TestContext
    
    # 设置配置到yaml_vars
    for key, value in config.items():
        yaml_vars.set_variable(key, value)
    
    print(f"🔧 配置已设置到yaml_vars")
    
    # 创建测试上下文
    context = TestContext()
    
    # 创建并运行DSL执行器
    executor = DSLExecutor(context)
    
    try:
        # 执行DSL文件
        print(f"🚀 开始执行DSL测试...")
        executor.execute_file(dsl_file_path)
        print(f"✅ DSL测试执行完成")
        return True
    except Exception as e:
        print(f"❌ DSL测试执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    if len(sys.argv) != 3:
        print("用法: python run_dsl_test.py <dsl_file> <config_file>")
        sys.exit(1)
    
    dsl_file = sys.argv[1]
    config_file = sys.argv[2]
    
    # 检查文件是否存在
    if not Path(dsl_file).exists():
        print(f"❌ DSL文件不存在: {dsl_file}")
        sys.exit(1)
    
    if not Path(config_file).exists():
        print(f"❌ 配置文件不存在: {config_file}")
        sys.exit(1)
    
    # 运行测试
    success = run_dsl_test(dsl_file, config_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 