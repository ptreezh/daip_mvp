#!/usr/bin/env python3
"""最终的用户干预机制验证 - 基于真实架构
"""

import asyncio
import sys

sys.path.append('src')

def test_userinterventionhandler():
    """测试UserInterventionHandler"""
    try:
        import asyncio

        from src.cli.user_intervention import UserInterventionHandler
        
        # 创建实例
        instance = UserInterventionHandler(command_queue=asyncio.Queue())
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'command_queue'), "缺少command_queue属性"
        assert hasattr(instance, 'running'), "缺少running属性"
        assert hasattr(instance, 'interactive_controller'), "缺少interactive_controller属性"
        assert hasattr(instance, 'start_listening'), "缺少start_listening方法"
        assert hasattr(instance, 'stop_listening'), "缺少stop_listening方法"
        
        print("✅ UserInterventionHandler验证通过")
        return True
        
    except Exception as e:
        print(f"❌ UserInterventionHandler验证失败: {e}")
        return False

def test_workflowsteering():
    """测试WorkflowSteering"""
    try:
        from rich.console import Console

        from src.user_interface.workflow_steering import WorkflowSteering
        
        # 创建实例
        instance = WorkflowSteering(console=Console())
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'steering_points'), "缺少steering_points属性"
        assert hasattr(instance, 'workflow_state'), "缺少workflow_state属性"
        assert hasattr(instance, 'steering_history'), "缺少steering_history属性"
        assert hasattr(instance, 'register_steering_point'), "缺少register_steering_point方法"
        assert hasattr(instance, 'get_available_checkpoints'), "缺少get_available_checkpoints方法"
        assert hasattr(instance, 'get_steering_history'), "缺少get_steering_history方法"
        
        print("✅ WorkflowSteering验证通过")
        return True
        
    except Exception as e:
        print(f"❌ WorkflowSteering验证失败: {e}")
        return False

def test_parametermanager():
    """测试ParameterManager"""
    try:
        from rich.console import Console

        from src.user_interface.parameter_manager import ParameterManager
        
        # 创建实例
        instance = ParameterManager(console=Console())
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'parameter_history'), "缺少parameter_history属性"
        assert hasattr(instance, 'validation_errors'), "缺少validation_errors属性"
        assert hasattr(instance, 'create_parameter_preset'), "缺少create_parameter_preset方法"
        assert hasattr(instance, 'load_parameter_preset'), "缺少load_parameter_preset方法"
        assert hasattr(instance, 'list_parameter_presets'), "缺少list_parameter_presets方法"
        
        print("✅ ParameterManager验证通过")
        return True
        
    except Exception as e:
        print(f"❌ ParameterManager验证失败: {e}")
        return False

def test_workflowcustomizer():
    """测试WorkflowCustomizer"""
    try:
        from rich.console import Console

        from src.user_interface.workflow_customizer import WorkflowCustomizer
        
        # 创建实例
        instance = WorkflowCustomizer(console=Console())
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'workflow_templates'), "缺少workflow_templates属性"
        assert hasattr(instance, 'customizations'), "缺少customizations属性"
        assert hasattr(instance, 'create_workflow_template'), "缺少create_workflow_template方法"
        assert hasattr(instance, 'apply_customization'), "缺少apply_customization方法"
        assert hasattr(instance, 'save_customization'), "缺少save_customization方法"
        
        print("✅ WorkflowCustomizer验证通过")
        return True
        
    except Exception as e:
        print(f"❌ WorkflowCustomizer验证失败: {e}")
        return False

def test_transparencycontroller():
    """测试TransparencyController"""
    try:
        from rich.console import Console

        from src.user_interface.transparency_controller import TransparencyController
        
        # 创建实例
        instance = TransparencyController(console=Console())
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'transparency_levels'), "缺少transparency_levels属性"
        assert hasattr(instance, 'current_level'), "缺少current_level属性"
        assert hasattr(instance, 'set_transparency_level'), "缺少set_transparency_level方法"
        assert hasattr(instance, 'get_transparency_info'), "缺少get_transparency_info方法"
        assert hasattr(instance, 'should_show_component'), "缺少should_show_component方法"
        
        print("✅ TransparencyController验证通过")
        return True
        
    except Exception as e:
        print(f"❌ TransparencyController验证失败: {e}")
        return False

def test_interactivecontroller():
    """测试InteractiveController"""
    try:
        from rich.console import Console

        from src.user_interface.interactive_controller import InteractiveController
        
        # 创建实例
        instance = InteractiveController(console=Console(), config_dir=".kiro/config")
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'intervention_callbacks'), "缺少intervention_callbacks属性"
        assert hasattr(instance, 'customization_options'), "缺少customization_options属性"
        assert hasattr(instance, 'parameter_manager'), "缺少parameter_manager属性"
        assert hasattr(instance, 'workflow_steering'), "缺少workflow_steering属性"
        assert hasattr(instance, 'configuration_manager'), "缺少configuration_manager属性"
        
        print("✅ InteractiveController验证通过")
        return True
        
    except Exception as e:
        print(f"❌ InteractiveController验证失败: {e}")
        return False

async def main():
    """主验证函数"""
    print("🚀 开始验证用户干预机制 (最终版)")
    
    tests = [
        ("UserInterventionHandler", test_userinterventionhandler),
        ("WorkflowSteering", test_workflowsteering),
        ("ParameterManager", test_parametermanager),
        ("WorkflowCustomizer", test_workflowcustomizer),
        ("TransparencyController", test_transparencycontroller),
        ("InteractiveController", test_interactivecontroller),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 验证 {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
                
            if result:
                passed += 1
            else:
                print(f"❌ {test_name} 验证失败")
        except Exception as e:
            print(f"❌ {test_name} 验证异常: {e}")
    
    print(f"\n📊 验证结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有验证通过")
        return True
    else:
        print("⚠️ 部分验证失败")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)