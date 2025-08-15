#!/usr/bin/env python3
"""
增强的用户干预机制验证 - 基于真实架构和构造函数分析
"""

import sys
import os
import asyncio
sys.path.append('src')

def test_interactivecontroller():
    """测试InteractiveController"""
    try:
        from src.user_interface.interactive_controller import InteractiveController
        from rich.console import Console
        
        # 创建实例
        instance = InteractiveController(console=Console(), config_dir=".kiro/config")
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'register_intervention_point'), "缺少register_intervention_point方法"
        assert hasattr(instance, 'create_workflow_steering_menu'), "缺少create_workflow_steering_menu方法"
        assert hasattr(instance, 'display_workflow_options'), "缺少display_workflow_options方法"
        
        print("✅ InteractiveController验证通过")
        return True
        
    except Exception as e:
        print(f"❌ InteractiveController验证失败: {e}")
        return False

def test_parameterdefinition():
    """测试ParameterDefinition"""
    try:
        from src.user_interface.parameter_manager import ParameterDefinition
        
        
        # 创建实例
        instance = ParameterDefinition()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        
        print("✅ ParameterDefinition验证通过")
        return True
        
    except Exception as e:
        print(f"❌ ParameterDefinition验证失败: {e}")
        return False

def test_parametererror():
    """测试ParameterError"""
    try:
        from src.core.exceptions import ParameterError
        
        
        # 创建实例
        instance = ParameterError()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        
        print("✅ ParameterError验证通过")
        return True
        
    except Exception as e:
        print(f"❌ ParameterError验证失败: {e}")
        return False

def test_parametermanager():
    """测试ParameterManager"""
    try:
        from src.user_interface.parameter_manager import ParameterManager
        from rich.console import Console
        
        # 创建实例
        instance = ParameterManager(console=Console())
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'create_parameter_preset'), "缺少create_parameter_preset方法"
        assert hasattr(instance, 'load_parameter_preset'), "缺少load_parameter_preset方法"
        assert hasattr(instance, 'list_parameter_presets'), "缺少list_parameter_presets方法"
        
        print("✅ ParameterManager验证通过")
        return True
        
    except Exception as e:
        print(f"❌ ParameterManager验证失败: {e}")
        return False

def test_parametertype():
    """测试ParameterType"""
    try:
        from src.user_interface.parameter_manager import ParameterType
        
        
        # 创建实例
        instance = ParameterType()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'STRING'), "缺少STRING属性"
        assert hasattr(instance, 'INTEGER'), "缺少INTEGER属性"
        assert hasattr(instance, 'FLOAT'), "缺少FLOAT属性"
        
        print("✅ ParameterType验证通过")
        return True
        
    except Exception as e:
        print(f"❌ ParameterType验证失败: {e}")
        return False

def test_scenarioparameter():
    """测试ScenarioParameter"""
    try:
        from src.real_demo_system.scenario_manager import ScenarioParameter
        
        
        # 创建实例
        instance = ScenarioParameter()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'to_dict'), "缺少to_dict方法"
        
        print("✅ ScenarioParameter验证通过")
        return True
        
    except Exception as e:
        print(f"❌ ScenarioParameter验证失败: {e}")
        return False

def test_steeringaction():
    """测试SteeringAction"""
    try:
        from src.user_interface.workflow_steering import SteeringAction
        
        
        # 创建实例
        instance = SteeringAction()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'CONTINUE'), "缺少CONTINUE属性"
        assert hasattr(instance, 'PAUSE'), "缺少PAUSE属性"
        assert hasattr(instance, 'MODIFY_PARAMETERS'), "缺少MODIFY_PARAMETERS属性"
        
        print("✅ SteeringAction验证通过")
        return True
        
    except Exception as e:
        print(f"❌ SteeringAction验证失败: {e}")
        return False

def test_steeringcommand():
    """测试SteeringCommand"""
    try:
        from src.user_interface.workflow_steering import SteeringCommand
        
        
        # 创建实例
        instance = SteeringCommand()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        
        print("✅ SteeringCommand验证通过")
        return True
        
    except Exception as e:
        print(f"❌ SteeringCommand验证失败: {e}")
        return False

def test_steeringpoint():
    """测试SteeringPoint"""
    try:
        from src.user_interface.workflow_steering import SteeringPoint
        
        
        # 创建实例
        instance = SteeringPoint()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        
        print("✅ SteeringPoint验证通过")
        return True
        
    except Exception as e:
        print(f"❌ SteeringPoint验证失败: {e}")
        return False

def test_templateparameter():
    """测试TemplateParameter"""
    try:
        from src.institutional_primitives.workflow_templates import TemplateParameter
        
        
        # 创建实例
        instance = TemplateParameter()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'validate_default'), "缺少validate_default方法"
        
        print("✅ TemplateParameter验证通过")
        return True
        
    except Exception as e:
        print(f"❌ TemplateParameter验证失败: {e}")
        return False

def test_templateparametervalues():
    """测试TemplateParameterValues"""
    try:
        from src.institutional_primitives.workflow_templates import TemplateParameterValues
        
        
        # 创建实例
        instance = TemplateParameterValues()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'get'), "缺少get方法"
        assert hasattr(instance, 'set'), "缺少set方法"
        
        print("✅ TemplateParameterValues验证通过")
        return True
        
    except Exception as e:
        print(f"❌ TemplateParameterValues验证失败: {e}")
        return False

def test_testinteractivecontroller():
    """测试TestInteractiveController"""
    try:
        from src.user_interface.test_user_intervention import TestInteractiveController
        
        
        # 创建实例
        instance = TestInteractiveController()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'setup_method'), "缺少setup_method方法"
        assert hasattr(instance, 'test_controller_initialization'), "缺少test_controller_initialization方法"
        assert hasattr(instance, 'test_steering_point_setup'), "缺少test_steering_point_setup方法"
        
        print("✅ TestInteractiveController验证通过")
        return True
        
    except Exception as e:
        print(f"❌ TestInteractiveController验证失败: {e}")
        return False

def test_testparametermanager():
    """测试TestParameterManager"""
    try:
        from src.user_interface.test_user_intervention import TestParameterManager
        
        
        # 创建实例
        instance = TestParameterManager()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'setup_method'), "缺少setup_method方法"
        assert hasattr(instance, 'test_parameter_definition_creation'), "缺少test_parameter_definition_creation方法"
        assert hasattr(instance, 'test_parameter_validation'), "缺少test_parameter_validation方法"
        
        print("✅ TestParameterManager验证通过")
        return True
        
    except Exception as e:
        print(f"❌ TestParameterManager验证失败: {e}")
        return False

def test_testworkflowsteering():
    """测试TestWorkflowSteering"""
    try:
        from src.user_interface.test_user_intervention import TestWorkflowSteering
        
        
        # 创建实例
        instance = TestWorkflowSteering()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'setup_method'), "缺少setup_method方法"
        assert hasattr(instance, 'test_steering_point_registration'), "缺少test_steering_point_registration方法"
        assert hasattr(instance, 'test_command_callback_registration'), "缺少test_command_callback_registration方法"
        
        print("✅ TestWorkflowSteering验证通过")
        return True
        
    except Exception as e:
        print(f"❌ TestWorkflowSteering验证失败: {e}")
        return False

def test_transparencycontroller():
    """测试TransparencyController"""
    try:
        from src.user_interface.transparency_controller import TransparencyController
        
        
        # 创建实例
        instance = TransparencyController()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'present_workflow_result'), "缺少present_workflow_result方法"
        assert hasattr(instance, 'present_with_traceability'), "缺少present_with_traceability方法"
        assert hasattr(instance, 'validate_result_quality'), "缺少validate_result_quality方法"
        
        print("✅ TransparencyController验证通过")
        return True
        
    except Exception as e:
        print(f"❌ TransparencyController验证失败: {e}")
        return False

def test_transparencyevent():
    """测试TransparencyEvent"""
    try:
        from src.real_demo_system.transparency_monitor import TransparencyEvent
        
        
        # 创建实例
        instance = TransparencyEvent()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'to_dict'), "缺少to_dict方法"
        
        print("✅ TransparencyEvent验证通过")
        return True
        
    except Exception as e:
        print(f"❌ TransparencyEvent验证失败: {e}")
        return False

def test_transparencylevel():
    """测试TransparencyLevel"""
    try:
        from src.virtual_role_chat.models import TransparencyLevel
        
        
        # 创建实例
        instance = TransparencyLevel()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'MINIMAL'), "缺少MINIMAL属性"
        assert hasattr(instance, 'MODERATE'), "缺少MODERATE属性"
        assert hasattr(instance, 'DETAILED'), "缺少DETAILED属性"
        
        print("✅ TransparencyLevel验证通过")
        return True
        
    except Exception as e:
        print(f"❌ TransparencyLevel验证失败: {e}")
        return False

def test_transparencymonitor():
    """测试TransparencyMonitor"""
    try:
        from src.real_demo_system.transparency_monitor import TransparencyMonitor
        
        
        # 创建实例
        instance = TransparencyMonitor(llm_integrator=None)
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'subscribe'), "缺少subscribe方法"
        assert hasattr(instance, 'unsubscribe'), "缺少unsubscribe方法"
        assert hasattr(instance, 'get_real_time_status'), "缺少get_real_time_status方法"
        
        print("✅ TransparencyMonitor验证通过")
        return True
        
    except Exception as e:
        print(f"❌ TransparencyMonitor验证失败: {e}")
        return False

def test_userinterventioncommand():
    """测试UserInterventionCommand"""
    try:
        from src.models import UserInterventionCommand
        
        
        # 创建实例
        instance = UserInterventionCommand()
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        
        print("✅ UserInterventionCommand验证通过")
        return True
        
    except Exception as e:
        print(f"❌ UserInterventionCommand验证失败: {e}")
        return False

def test_userinterventionhandler():
    """测试UserInterventionHandler"""
    try:
        from src.cli.user_intervention import UserInterventionHandler
        import asyncio
        
        # 创建实例
        instance = UserInterventionHandler(command_queue=asyncio.Queue())
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'start_listening'), "缺少start_listening方法"
        assert hasattr(instance, 'stop_listening'), "缺少stop_listening方法"
        
        print("✅ UserInterventionHandler验证通过")
        return True
        
    except Exception as e:
        print(f"❌ UserInterventionHandler验证失败: {e}")
        return False

def test_workflowcustomizer():
    """测试WorkflowCustomizer"""
    try:
        from src.user_interface.workflow_customizer import WorkflowCustomizer
        from rich.console import Console
        
        # 创建实例
        instance = WorkflowCustomizer(console=Console())
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'create_custom_config'), "缺少create_custom_config方法"
        assert hasattr(instance, 'load_config_from_file'), "缺少load_config_from_file方法"
        assert hasattr(instance, 'save_config_to_file'), "缺少save_config_to_file方法"
        
        print("✅ WorkflowCustomizer验证通过")
        return True
        
    except Exception as e:
        print(f"❌ WorkflowCustomizer验证失败: {e}")
        return False

def test_workflowsteering():
    """测试WorkflowSteering"""
    try:
        from src.user_interface.workflow_steering import WorkflowSteering
        from rich.console import Console
        
        # 创建实例
        instance = WorkflowSteering(console=Console())
        
        # 验证实例创建成功
        assert instance is not None, "实例创建失败"
        assert hasattr(instance, 'register_steering_point'), "缺少register_steering_point方法"
        assert hasattr(instance, 'register_command_callback'), "缺少register_command_callback方法"
        assert hasattr(instance, 'get_steering_history'), "缺少get_steering_history方法"
        
        print("✅ WorkflowSteering验证通过")
        return True
        
    except Exception as e:
        print(f"❌ WorkflowSteering验证失败: {e}")
        return False

async def main():
    """主验证函数"""
    print("🚀 开始验证用户干预机制 (增强版)")
    
    tests = [
        ("InteractiveController", test_interactivecontroller),
        ("ParameterDefinition", test_parameterdefinition),
        ("ParameterError", test_parametererror),
        ("ParameterManager", test_parametermanager),
        ("ParameterType", test_parametertype),
        ("ScenarioParameter", test_scenarioparameter),
        ("SteeringAction", test_steeringaction),
        ("SteeringCommand", test_steeringcommand),
        ("SteeringPoint", test_steeringpoint),
        ("TemplateParameter", test_templateparameter),
        ("TemplateParameterValues", test_templateparametervalues),
        ("TestInteractiveController", test_testinteractivecontroller),
        ("TestParameterManager", test_testparametermanager),
        ("TestWorkflowSteering", test_testworkflowsteering),
        ("TransparencyController", test_transparencycontroller),
        ("TransparencyEvent", test_transparencyevent),
        ("TransparencyLevel", test_transparencylevel),
        ("TransparencyMonitor", test_transparencymonitor),
        ("UserInterventionCommand", test_userinterventioncommand),
        ("UserInterventionHandler", test_userinterventionhandler),
        ("WorkflowCustomizer", test_workflowcustomizer),
        ("WorkflowSteering", test_workflowsteering),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"
📋 验证 {test_name}...")
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
    
    print(f"
📊 验证结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有验证通过")
        return True
    else:
        print("⚠️ 部分验证失败")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)