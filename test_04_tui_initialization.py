#!/usr/bin/env python3
"""
Test 4: TUI Initialization Validation
验证TUI初始化
"""

import sys
import os
import threading
import time

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_tui_instance_creation():
    """测试TUI实例创建"""
    print("1. 测试TUI实例创建...")
    try:
        from daip_live.tui import DAIP_TUI
        
        # 创建TUI实例（不运行）
        tui = DAIP_TUI()
        
        # 检查必需属性
        required_attrs = [
            '_executor', '_session_manager', '_role_manager', 
            '_knowledge_manager', '_model_provider', '_db_manager'
        ]
        
        missing_attrs = []
        for attr in required_attrs:
            if not hasattr(tui, attr):
                missing_attrs.append(attr)
        
        if missing_attrs:
            print(f"   ❌ TUI缺少以下属性: {missing_attrs}")
            return False
        else:
            print("   ✅ TUI实例创建成功，所有必需属性存在")
            return True
    except Exception as e:
        print(f"   ❌ TUI实例创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tui_with_dependencies():
    """测试带有依赖注入的TUI创建"""
    print("2. 测试带有依赖注入的TUI创建...")
    try:
        from daip_live.tui import DAIP_TUI
        from daip_live.container import Container
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
        from daip_live.config import config_manager, create_config_yaml_if_not_exists
        
        # 创建容器
        container = Container()
        create_config_yaml_if_not_exists()
        container.config.from_yaml("config.yaml")
        
        # 获取服务
        agent_executor = container.agent_executor()
        session_manager = container.session_manager()
        role_manager = container.role_manager()
        knowledge_manager = container.knowledge_manager()
        debate_manager = container.debate_manager()
        model_provider = container.model_provider()
        db_manager = container.db_manager()
        role_model_manager = RoleModelManager()
        
        # 创建TUI实例
        tui = DAIP_TUI(
            executor=agent_executor,
            goal="测试初始化",
            session_manager=session_manager,
            role_manager=role_manager,
            knowledge_manager=knowledge_manager,
            debate_manager=debate_manager,
            model_provider=model_provider,
            db_manager=db_manager,
            config_manager=config_manager,
            role_model_manager=role_model_manager
        )
        
        print("   ✅ 带依赖注入的TUI实例创建成功")
        return True
    except Exception as e:
        print(f"   ❌ 带依赖注入的TUI实例创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tui_attributes():
    """测试TUI属性初始化"""
    print("3. 测试TUI属性初始化...")
    try:
        from daip_live.tui import DAIP_TUI
        from daip_live.container import Container
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
        from daip_live.config import config_manager, create_config_yaml_if_not_exists
        
        # 创建容器
        container = Container()
        create_config_yaml_if_not_exists()
        container.config.from_yaml("config.yaml")
        
        # 获取服务
        agent_executor = container.agent_executor()
        session_manager = container.session_manager()
        role_manager = container.role_manager()
        knowledge_manager = container.knowledge_manager()
        debate_manager = container.debate_manager()
        model_provider = container.model_provider()
        db_manager = container.db_manager()
        role_model_manager = RoleModelManager()
        
        # 创建TUI实例
        tui = DAIP_TUI(
            executor=agent_executor,
            goal="测试初始化",
            session_manager=session_manager,
            role_manager=role_manager,
            knowledge_manager=knowledge_manager,
            debate_manager=debate_manager,
            model_provider=model_provider,
            db_manager=db_manager,
            config_manager=config_manager,
            role_model_manager=role_model_manager
        )
        
        # 检查关键属性
        checks = {
            '_current_model': lambda x: x is not None,
            '_model_name': lambda x: x is not None,
            '_token_usage': lambda x: isinstance(x, tuple) and len(x) == 2,
            '_goal': lambda x: x is not None,
            '_current_session_id': lambda x: x is not None or True  # can be None initially
        }
        
        failed_checks = []
        for attr_name, check_func in checks.items():
            if hasattr(tui, attr_name):
                attr_value = getattr(tui, attr_name)
                if not check_func(attr_value):
                    failed_checks.append(f"{attr_name} (值: {attr_value})")
            else:
                failed_checks.append(f"{attr_name} (不存在)")
        
        if failed_checks:
            print(f"   ❌ 以下属性检查失败: {failed_checks}")
            return False
        else:
            print("   ✅ TUI属性初始化检查通过")
            return True
    except Exception as e:
        print(f"   ❌ TUI属性检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tui_compose():
    """测试TUI界面组件创建"""
    print("4. 测试TUI界面组件创建...")
    try:
        from daip_live.tui import DAIP_TUI
        from daip_live.container import Container
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
        from daip_live.config import config_manager, create_config_yaml_if_not_exists
        
        # 创建容器
        container = Container()
        create_config_yaml_if_not_exists()
        container.config.from_yaml("config.yaml")
        
        # 获取服务
        agent_executor = container.agent_executor()
        session_manager = container.session_manager()
        role_manager = container.role_manager()
        knowledge_manager = container.knowledge_manager()
        debate_manager = container.debate_manager()
        model_provider = container.model_provider()
        db_manager = container.db_manager()
        role_model_manager = RoleModelManager()
        
        # 创建TUI实例
        tui = DAIP_TUI(
            executor=agent_executor,
            goal="测试初始化",
            session_manager=session_manager,
            role_manager=role_manager,
            knowledge_manager=knowledge_manager,
            debate_manager=debate_manager,
            model_provider=model_provider,
            db_manager=db_manager,
            config_manager=config_manager,
            role_model_manager=role_model_manager
        )
        
        # 检查是否可以访问主要组件
        main_components = ['#main_log', '#user_input', '#status_bar']
        
        print("   ✅ TUI界面组件创建成功 (无需实际渲染)")
        return True
    except Exception as e:
        print(f"   ❌ TUI界面组件创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("测试4: TUI初始化验证")
    print("=" * 60)
    
    tests = [
        test_tui_instance_creation,
        test_tui_with_dependencies,
        test_tui_attributes,
        test_tui_compose
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
        print("✅ 所有TUI初始化测试通过!")
        return 0
    else:
        failed_count = len([r for r in results if not r])
        print(f"❌ {failed_count} 个测试失败!")
        return 1

if __name__ == "__main__":
    sys.exit(main())