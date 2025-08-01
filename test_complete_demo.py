#!/usr/bin/env python3

import sys
import asyncio
sys.path.append('.')

from src.real_demo_system.interactive_demo_flow import InteractiveDemoFlow
from src.real_demo_system.demo_types import DemoScenarioType


async def run_complete_demo():
    """运行完整的演示测试"""
    print("🚀 开始完整的交互式演示流程测试")
    print("=" * 60)
    
    # 创建演示流程管理器
    demo_flow = InteractiveDemoFlow()
    print("✅ 创建演示流程管理器成功")
    
    # 获取可用场景
    scenarios = demo_flow.get_available_scenarios()
    print(f"📋 可用场景数量: {len(scenarios)}")
    for scenario_type, info in scenarios.items():
        print(f"  - {info['name']} ({scenario_type})")
    
    # 启动演示
    print("\n🎬 启动多角色辩论演示")
    start_result = await demo_flow.start_demo(
        DemoScenarioType.MULTI_ROLE_DEBATE.value,
        {"topic": "AI在医疗诊断中的应用"}
    )
    
    if "error" in start_result:
        print(f"❌ 启动失败: {start_result['error']}")
        return False
    
    print(f"✅ 演示启动成功")
    print(f"   演示ID: {start_result['demo_id']}")
    print(f"   场景: {start_result['scenario_name']}")
    print(f"   总步骤: {start_result['total_steps']}")
    
    # 执行演示步骤
    print("\n⚡ 执行演示步骤")
    step_count = 0
    max_steps = 4  # 执行前4步进行测试
    
    while step_count < max_steps:
        # 获取当前状态
        status = demo_flow.get_current_demo_status()
        if status:
            print(f"📊 当前进度: {status['progress_percentage']:.1f}% ({status['current_step']}/{status['total_steps']})")
        
        # 执行下一步
        step_result = await demo_flow.execute_next_step({
            "user_input": f"用户输入 - 步骤 {step_count + 1}",
            "custom_data": f"测试数据 {step_count + 1}"
        })
        
        if "error" in step_result:
            print(f"❌ 步骤 {step_count + 1} 执行失败: {step_result['error']}")
            break
        
        if step_result.get("status") == "demo_completed":
            print("🎉 演示完成!")
            print(f"   总时长: {step_result['total_duration']:.1f}秒")
            print(f"   完成步骤: {step_result['completed_steps']}")
            print(f"   摘要: {step_result['summary']}")
            
            # 显示分析报告摘要
            if "analysis_report" in step_result:
                report = step_result["analysis_report"]
                print(f"   质量分数: {report.get('quality_assessment', {}).get('overall_quality_score', 0):.2f}")
                print(f"   成功率: {report.get('execution_statistics', {}).get('success_rate', 0):.2f}")
            break
        else:
            step_count += 1
            print(f"✅ 步骤 {step_count} 完成: {step_result['step_completed']}")
            print(f"   动作: {step_result['result']['action']}")
            print(f"   描述: {step_result['result']['description']}")
            print(f"   进度: {step_result['progress']['percentage']:.1f}%")
            
            if step_result.get("next_step"):
                print(f"   下一步: {step_result['next_step']['step_name']}")
            
            # 模拟用户思考时间
            await asyncio.sleep(0.5)
    
    # 检查演示历史
    print("\n📚 检查演示历史")
    history = demo_flow.get_demo_history()
    print(f"✅ 历史记录数量: {len(history)}")
    
    for i, record in enumerate(history, 1):
        print(f"   {i}. {record['scenario_name']}")
        print(f"      状态: {record['status']}")
        print(f"      时长: {record['duration']:.1f}秒")
        print(f"      质量分数: {record['quality_score']:.2f}")
    
    print("\n🎉 完整演示测试成功完成!")
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(run_complete_demo())
        print(f"\n测试结果: {'✅ 成功' if success else '❌ 失败'}")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()