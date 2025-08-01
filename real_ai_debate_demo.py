#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实AI辩论演示
展示真正的多角色AI辩论过程
"""

import sys
import asyncio
sys.path.append('.')

from src.real_demo_system.interactive_demo_flow import InteractiveDemoFlow
from src.real_demo_system.demo_types import DemoScenarioType


async def run_real_ai_debate():
    """运行真实AI辩论演示"""
    print("🎭 Personal Intelligence Hub - 真实AI多角色辩论演示")
    print("=" * 60)
    print("这是一个真实的AI协作决策演示")
    print("你将看到3个AI角色就复杂问题进行深度辩论")
    print()
    
    # 创建演示流程
    demo_flow = InteractiveDemoFlow()
    
    # 设置辩论话题
    topic = "提示词和上下文工程本质上是AI产品用户体验问题和商业模式不成熟问题，是面向AI产品设计和工程领域的，现在被迫让用户接受一个不成熟的、未被驯化的AI裸产品"
    
    print(f"🎯 辩论话题：{topic}")
    print()
    
    # 启动演示
    print("🚀 启动AI辩论演示...")
    start_result = await demo_flow.start_demo(
        DemoScenarioType.MULTI_ROLE_DEBATE.value,
        {"topic": topic}
    )
    
    if "error" in start_result:
        print(f"❌ 启动失败: {start_result['error']}")
        return
    
    print(f"✅ 演示启动成功 (ID: {start_result['demo_id']})")
    print(f"📊 总步骤数: {start_result['total_steps']}")
    print()
    
    # 执行所有演示步骤
    step_count = 0
    
    while True:
        # 显示进度
        status = demo_flow.get_current_demo_status()
        if status:
            print(f"📈 进度: {status['progress_percentage']:.1f}% ({status['current_step']}/{status['total_steps']})")
        
        # 执行下一步
        step_result = await demo_flow.execute_next_step({
            "automated_execution": True,
            "step_number": step_count + 1
        })
        
        if "error" in step_result:
            print(f"❌ 步骤执行失败: {step_result['error']}")
            break
        
        if step_result.get("status") == "demo_completed":
            print("\n🎉 AI辩论演示完成!")
            print(f"⏱️ 总时长: {step_result['total_duration']:.1f}秒")
            print(f"📝 摘要: {step_result['summary']}")
            
            # 显示分析报告
            if "analysis_report" in step_result:
                report = step_result["analysis_report"]
                print(f"\n📊 质量评估:")
                quality = report.get("quality_assessment", {})
                print(f"   • 总体质量分数: {quality.get('overall_quality_score', 0):.2f}")
                print(f"   • 教育价值: {quality.get('educational_value', 0):.2f}")
                print(f"   • 技术演示: {quality.get('technical_demonstration', 0):.2f}")
                
                print(f"\n💡 关键洞察:")
                for insight in report.get("insights", []):
                    print(f"   • {insight}")
                
                print(f"\n🔧 改进建议:")
                for rec in report.get("recommendations", []):
                    print(f"   • {rec}")
            
            break
        else:
            step_count += 1
            result = step_result["result"]
            
            print(f"\n✅ 步骤 {step_count}: {step_result['step_completed']}")
            print(f"🎯 动作: {result['action']}")
            print(f"📝 描述: {result['description']}")
            
            # 显示详细信息
            if "setup_info" in result:
                print("⚙️ 设置信息:")
                for key, value in result["setup_info"].items():
                    print(f"   • {key}: {value}")
            
            if "selected_roles" in result:
                print("👥 AI角色:")
                for role in result["selected_roles"]:
                    print(f"   • {role['name']}: {role['perspective']} ({role.get('stance', 'N/A')})")
                    if "system_prompt_length" in role:
                        print(f"     系统提示长度: {role['system_prompt_length']} 字符")
            
            if "initial_positions" in result:
                print("🎭 初始立场:")
                for pos in result["initial_positions"]:
                    print(f"   • {pos['role']}: {pos['initial_position']}")
            
            if "rounds" in result:
                print("🗣️ 辩论轮次:")
                for round_data in result["rounds"]:
                    print(f"   第{round_data['round_number']}轮: {round_data['theme']}")
                    for statement in round_data["statements"]:
                        print(f"   🎤 {statement['role']}: {statement['statement']}")
                        print(f"      关键点: {', '.join(statement['key_points'])}")
                    print(f"   📊 共识水平: {round_data['consensus_level']:.2f}")
                    print()
            
            if "consensus_result" in result:
                print("🤝 最终共识:")
                consensus = result["consensus_result"]
                print(f"   置信度: {consensus['confidence_score']:.2f}")
                print(f"   一致性: {consensus['agreement_level']}")
                print(f"   共识内容:")
                print(f"   {consensus['final_position']}")
            
            if "analysis_results" in result:
                print("📊 辩论质量分析:")
                analysis = result["analysis_results"]
                for key, value in analysis.items():
                    print(f"   • {key}: {value:.2f}")
            
            if "technical_details" in result:
                print("🔧 技术细节:")
                tech = result["technical_details"]
                for key, value in tech.items():
                    print(f"   • {key}: {value}")
            
            print(f"📈 当前进度: {step_result['progress']['percentage']:.1f}%")
            print("-" * 60)
            
            # 给用户一些时间阅读
            await asyncio.sleep(2)
    
    print(f"\n🎉 演示完成！这展示了AI多角色协作决策的真实能力。")


if __name__ == "__main__":
    try:
        asyncio.run(run_real_ai_debate())
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()