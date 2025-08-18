#!/usr/bin/env python3
"""验证用户干预机制 - 基于真实架构生成
"""

import asyncio
import sys

sys.path.append('src')

def test_userinterventionhandler():
    """测试UserInterventionHandler"""
    try:
        from src.cli.user_intervention import UserInterventionHandler

        # 创建实例
        instance = UserInterventionHandler()

        # 验证基本属性

        # 验证基本方法
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
        from src.user_interface.workflow_steering import WorkflowSteering

        # 创建实例
        instance = WorkflowSteering()

        # 验证基本属性

        # 验证基本方法
        assert hasattr(instance, 'register_steering_point'), "缺少register_steering_point方法"
        assert hasattr(instance, 'register_command_callback'), "缺少register_command_callback方法"
        assert hasattr(instance, 'get_steering_history'), "缺少get_steering_history方法"

        print("✅ WorkflowSteering验证通过")
        return True

    except Exception as e:
        print(f"❌ WorkflowSteering验证失败: {e}")
        return False

def test_parametermanager():
    """测试ParameterManager"""
    try:
        from src.user_interface.parameter_manager import ParameterManager

        # 创建实例
        instance = ParameterManager()

        # 验证基本属性

        # 验证基本方法

        print("✅ ParameterManager验证通过")
        return True

    except Exception as e:
        print(f"❌ ParameterManager验证失败: {e}")
        return False

def test_workflowcustomizer():
    """测试WorkflowCustomizer"""
    try:
        from src.user_interface.workflow_customizer import WorkflowCustomizer

        # 创建实例
        instance = WorkflowCustomizer()

        # 验证基本属性

        # 验证基本方法
        assert hasattr(instance, 'create_custom_config'), "缺少create_custom_config方法"
        assert hasattr(instance, 'load_config_from_file'), "缺少load_config_from_file方法"
        assert hasattr(instance, 'save_config_to_file'), "缺少save_config_to_file方法"

        print("✅ WorkflowCustomizer验证通过")
        return True

    except Exception as e:
        print(f"❌ WorkflowCustomizer验证失败: {e}")
        return False

def test_transparencycontroller():
    """测试TransparencyController"""
    try:
        from src.user_interface.transparency_controller import TransparencyController

        # 创建实例
        instance = TransparencyController()

        # 验证基本属性

        # 验证基本方法
        assert hasattr(instance, 'present_workflow_result'), "缺少present_workflow_result方法"
        assert hasattr(instance, 'present_with_traceability'), "缺少present_with_traceability方法"
        assert hasattr(instance, 'validate_result_quality'), "缺少validate_result_quality方法"
        assert hasattr(instance, 'export_result'), "缺少export_result方法"

        print("✅ TransparencyController验证通过")
        return True

    except Exception as e:
        print(f"❌ TransparencyController验证失败: {e}")
        return False

def test_interactivecontroller():
    """测试InteractiveController"""
    try:
        from src.user_interface.interactive_controller import InteractiveController

        # 创建实例
        instance = InteractiveController()

        # 验证基本属性

        # 验证基本方法
        assert hasattr(instance, 'register_intervention_point'), "缺少register_intervention_point方法"
        assert hasattr(instance, 'create_workflow_steering_menu'), "缺少create_workflow_steering_menu方法"
        assert hasattr(instance, 'display_workflow_options'), "缺少display_workflow_options方法"
        assert hasattr(instance, 'load_workflow_configuration'), "缺少load_workflow_configuration方法"

        print("✅ InteractiveController验证通过")
        return True

    except Exception as e:
        print(f"❌ InteractiveController验证失败: {e}")
        return False

async def main():
    """主验证函数"""
    print("🚀 开始验证用户干预机制")

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
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()

        if result:
            passed += 1
        else:
            print(f"❌ {test_name} 验证失败，停止后续测试")
            break

    if passed == total:
        print(f"\n✅ 所有验证通过 ({passed}/{total})")
        return True
    else:
        print(f"\n❌ 验证失败 ({passed}/{total})")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
