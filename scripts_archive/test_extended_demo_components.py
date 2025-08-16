"""扩展演示系统组件测试

测试场景管理器和用户交互管理器等新增组件。
"""

import asyncio
import json
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_scenario_manager():
    """测试场景管理器"""
    print("\n" + "="*50)
    print("测试 ScenarioManager")
    print("="*50)

    try:
        from src.real_demo_system.scenario_manager import ScenarioManager

        # 创建场景管理器
        scenario_manager = ScenarioManager()

        # 获取可用场景
        print("\n1. 可用场景:")
        scenarios = scenario_manager.get_available_scenarios()
        print(f"总共 {len(scenarios)} 个场景")

        for scenario in scenarios:
            print(f"  - {scenario['name']} ({scenario['scenario_type']})")
            print(f"    描述: {scenario['description'][:100]}...")
            print(f"    参数数量: {len(scenario['parameters'])}")
            print(f"    必需角色: {scenario['required_roles']}")

        # 创建场景实例
        print("\n2. 创建AI伦理场景实例:")
        instance_id = scenario_manager.create_scenario_instance(
            scenario_id="ai_ethics_analysis",
            instance_name="医疗AI伦理分析测试",
            parameter_values={
                "ethical_dilemma": "一个医疗AI系统在诊断时对不同种族群体表现出不同的准确率，这引发了公平性和偏见的伦理问题。该系统在临床试验中显示出比人类医生更高的整体准确率，但在处理少数族裔患者数据时准确率明显下降。公司面临是否立即发布系统的决策困境。",
                "stakeholders": ["患者", "医生", "AI公司", "监管机构"],
                "ethical_frameworks": ["功利主义", "义务论", "关怀伦理学"],
                "industry_context": "医疗AI"
            }
        )
        print(f"实例创建成功: {instance_id}")

        # 获取实例状态
        print("\n3. 实例状态:")
        instance_status = scenario_manager.get_instance_status(instance_id)
        print(f"状态: {instance_status['status']}")
        print(f"参数值: {len(instance_status['parameter_values'])} 个参数")

        # 开始执行
        print("\n4. 开始场景执行:")
        started = scenario_manager.start_scenario_execution(instance_id)
        print(f"执行开始: {started}")

        # 模拟完成执行
        print("\n5. 完成场景执行:")
        completed = scenario_manager.complete_scenario_execution(
            instance_id,
            results={
                "analysis_report": "详细的伦理分析报告",
                "recommendations": ["建议1", "建议2", "建议3"],
                "risk_assessment": "中等风险"
            },
            success=True
        )
        print(f"执行完成: {completed}")

        # 获取统计信息
        print("\n6. 场景统计:")
        stats = scenario_manager.get_scenario_statistics()
        print(json.dumps(stats, indent=2, ensure_ascii=False))

        print("\n✅ ScenarioManager 测试通过")
        return True

    except Exception as e:
        print(f"\n❌ ScenarioManager 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_user_interaction_manager():
    """测试用户交互管理器"""
    print("\n" + "="*50)
    print("测试 UserInteractionManager")
    print("="*50)

    try:
        from src.real_demo_system.user_interaction_manager import UserInteractionManager

        # 创建用户交互管理器
        interaction_manager = UserInteractionManager()

        # 创建交互会话
        print("\n1. 创建交互会话:")
        session_id = interaction_manager.create_interaction_session(
            user_id="test_user",
            demo_session_id="demo_123",
            context={"demo_type": "ai_ethics", "user_level": "expert"}
        )
        print(f"会话创建成功: {session_id}")

        # 请求用户输入
        print("\n2. 请求用户输入:")
        input_request_id = await interaction_manager.request_user_input(
            session_id=session_id,
            title="请输入您的姓名",
            description="为了个性化演示体验，请输入您的姓名",
            input_type="text",
            validation_rules={"min_length": 2, "max_length": 50},
            required=True,
            timeout_seconds=60
        )
        print(f"输入请求创建: {input_request_id}")

        # 请求选择
        print("\n3. 请求选择:")
        choice_request_id = await interaction_manager.request_choice_selection(
            session_id=session_id,
            title="选择分析视角",
            description="请选择您希望重点关注的分析视角",
            choices=[
                {"id": "technical", "label": "技术视角", "description": "关注技术实现和算法"},
                {"id": "ethical", "label": "伦理视角", "description": "关注道德和伦理问题"},
                {"id": "business", "label": "商业视角", "description": "关注商业影响和价值"},
                {"id": "legal", "label": "法律视角", "description": "关注法律合规和风险"}
            ],
            allow_multiple=True,
            required=True,
            timeout_seconds=120
        )
        print(f"选择请求创建: {choice_request_id}")

        # 请求确认
        print("\n4. 请求确认:")
        confirm_request_id = await interaction_manager.request_confirmation(
            session_id=session_id,
            title="开始演示",
            description="是否准备开始AI伦理分析演示？",
            default_choice=True,
            timeout_seconds=30
        )
        print(f"确认请求创建: {confirm_request_id}")

        # 获取待处理请求
        print("\n5. 待处理请求:")
        pending_requests = interaction_manager.get_pending_requests(session_id)
        print(f"待处理请求数: {len(pending_requests)}")
        for req in pending_requests:
            print(f"  - {req['title']} ({req['interaction_type']})")

        # 模拟用户响应
        print("\n6. 模拟用户响应:")

        # 响应输入请求
        input_response = await interaction_manager.submit_response(
            request_id=input_request_id,
            response_data="张三",
            user_id="test_user"
        )
        print(f"输入响应提交: {input_response}")

        # 响应选择请求
        choice_response = await interaction_manager.submit_response(
            request_id=choice_request_id,
            response_data=["ethical", "technical"],
            user_id="test_user"
        )
        print(f"选择响应提交: {choice_response}")

        # 响应确认请求
        confirm_response = await interaction_manager.submit_response(
            request_id=confirm_request_id,
            response_data=True,
            user_id="test_user"
        )
        print(f"确认响应提交: {confirm_response}")

        # 获取会话状态
        print("\n7. 会话状态:")
        session_status = interaction_manager.get_session_status(session_id)
        print(f"活跃请求数: {len(session_status['active_requests'])}")
        print(f"已完成交互数: {len(session_status['completed_interactions'])}")

        # 获取交互统计
        print("\n8. 交互统计:")
        stats = interaction_manager.get_interaction_statistics()
        print(json.dumps(stats, indent=2, ensure_ascii=False))

        print("\n✅ UserInteractionManager 测试通过")
        return True

    except Exception as e:
        print(f"\n❌ UserInteractionManager 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_demo_controller_integration():
    """测试演示控制器集成"""
    print("\n" + "="*50)
    print("测试 RealDemoController 集成")
    print("="*50)

    try:
        from src.real_demo_system.real_demo_controller import RealDemoController

        # 创建演示控制器
        demo_controller = RealDemoController()

        # 获取系统状态
        print("\n1. 系统状态:")
        system_status = demo_controller.get_system_status()
        print(f"活跃会话数: {system_status['active_sessions']}")
        print(f"总会话数: {system_status['total_sessions']}")
        print("组件状态:")
        for component, status in system_status['component_status'].items():
            print(f"  - {component}: {status}")

        # 获取演示统计
        print("\n2. 演示统计:")
        demo_stats = demo_controller.get_demo_statistics()
        print(f"总会话数: {demo_stats['total_sessions']}")
        print(f"活跃会话数: {demo_stats['active_sessions']}")
        print(f"成功率: {demo_stats['success_rate']:.1%}")

        print("\n✅ RealDemoController 集成测试通过")
        return True

    except Exception as e:
        print(f"\n❌ RealDemoController 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("开始测试扩展演示系统组件...")
    print(f"测试时间: {datetime.now().isoformat()}")

    test_results = {}

    try:
        # 测试场景管理器
        test_results['scenario_manager'] = test_scenario_manager()

        # 测试用户交互管理器
        test_results['user_interaction_manager'] = await test_user_interaction_manager()

        # 测试演示控制器集成
        test_results['demo_controller_integration'] = await test_demo_controller_integration()

        print("\n" + "="*50)
        print("扩展组件测试结果摘要")
        print("="*50)

        for component, success in test_results.items():
            status = "✅ 通过" if success else "❌ 失败"
            print(f"{component}: {status}")

        total_tests = len(test_results)
        passed_tests = sum(test_results.values())

        print(f"\n总测试数: {total_tests}")
        print(f"通过测试数: {passed_tests}")
        print(f"成功率: {passed_tests/total_tests:.1%}")

        if passed_tests == total_tests:
            print("\n🎉 所有扩展组件测试通过！演示系统功能完整。")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} 个组件测试失败，请检查相关实现。")

    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
