#!/usr/bin/env python3
"""
Test 2: Module Import Validation
验证模块导入
"""

import sys
import os

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_tui_import():
    """测试TUI模块导入"""
    print("1. 测试TUI模块导入...")
    try:
        from daip_live.tui import DAIP_TUI
        print("   ✅ TUI模块导入成功")
        return True
    except Exception as e:
        print(f"   ❌ TUI模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_import():
    """测试CLI模块导入"""
    print("2. 测试CLI模块导入...")
    try:
        from daip_live.cli import app
        print("   ✅ CLI模块导入成功")
        return True
    except Exception as e:
        print(f"   ❌ CLI模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_core_modules_import():
    """测试核心模块导入"""
    print("3. 测试核心模块导入...")
    core_modules = [
        'daip_live.agent_engine.executor.AgentExecutor',
        'daip_live.memory.session_manager.SessionManager',
        'daip_live.p4_role_manager_tools.role_manager.RoleManager',
        'daip_live.model_provider.provider.LiteLLMProvider',
        'daip_live.persistence.database.DatabaseManager'
    ]
    
    failed_modules = []
    for module_path in core_modules:
        try:
            module_parts = module_path.split('.')
            module_name = '.'.join(module_parts[:-1])
            class_name = module_parts[-1]
            
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
        except Exception as e:
            failed_modules.append((module_path, str(e)))
    
    if failed_modules:
        print(f"   ❌ 以下模块导入失败:")
        for module_path, error in failed_modules:
            print(f"      - {module_path}: {error}")
        return False
    else:
        print("   ✅ 所有核心模块导入成功")
        return True

def test_container_import():
    """测试容器导入"""
    print("4. 测试容器导入...")
    try:
        from daip_live.container import Container
        print("   ✅ 容器模块导入成功")
        return True
    except Exception as e:
        print(f"   ❌ 容器模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_import():
    """测试配置模块导入"""
    print("5. 测试配置模块导入...")
    try:
        from daip_live.config import config_manager, create_config_yaml_if_not_exists
        print("   ✅ 配置模块导入成功")
        return True
    except Exception as e:
        print(f"   ❌ 配置模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("测试2: 模块导入验证")
    print("=" * 60)
    
    tests = [
        test_tui_import,
        test_cli_import,
        test_core_modules_import,
        test_container_import,
        test_config_import
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ 测试 {test.__name__} 执行失败: {e}")
            results.append(False)
        print()
    
    print("=" * 60)
    if all(results):
        print("✅ 所有模块导入测试通过!")
        return 0
    else:
        failed_count = len([r for r in results if not r])
        print(f"❌ {failed_count} 个测试失败!")
        return 1

if __name__ == "__main__":
    sys.exit(main())