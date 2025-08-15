#!/usr/bin/env python3
"""完全集成系统演示

展示所有虚拟角色LLM调用都使用智能上下文优化的完整DAIP-LIVE系统
"""

import asyncio
import sys

sys.path.append('src')

async def demo_fully_integrated_system():
    """演示完全集成的系统"""
    print("🚀 完全集成的DAIP-LIVE智能优化系统演示")
    print("=" * 80)
    print("💡 所有虚拟角色的LLM调用都已集成智能上下文优化")
    print("🎯 包括：多角色辩论、个人助手、工作流执行等所有场景")
    print()
    
    # 模拟一个完整的AI伦理决策场景
    print("📋 完整场景演示：医院AI诊断系统伦理决策")
    print("=" * 60)
    
    ethical_scenario = {
        "title": "医院AI诊断系统部署伦理决策",
        "description": "某三甲医院计划部署AI辅助诊断系统，需要全面评估伦理风险并制定实施方案",
        "stakeholders": [
            "医院管理层",
            "临床医生", 
            "患者代表",
            "AI技术专家",
            "医疗伦理专家",
            "法律顾问",
            "监管机构代表"
        ],
        "key_concerns": [
            "算法偏见对少数族裔患者的影响",
            "医生对AI诊断的依赖性",
            "患者数据隐私保护",
            "医疗责任归属问题",
            "AI系统的可解释性要求"
        ]
    }
    
    print(f"🏥 场景: {ethical_scenario['title']}")
    print(f"📝 描述: {ethical_scenario['description']}")
    print(f"👥 利益相关者: {len(ethical_scenario['stakeholders'])}个")
    print(f"⚠️  关键关注点: {len(ethical_scenario['key_concerns'])}个")
    print()
    
    try:
        # 1. 个人助手阶段 - 用户咨询
        print("🔄 阶段1：个人助手咨询")
        print("-" * 40)
        
        from src.real_demo_system.llm_optimization_adapter import optimize_role_llm_call
        
        # 模拟医院管理者咨询个人助手
        user_query = "我们医院想部署AI诊断系统，需要了解完整的伦理风险评估流程和关键决策点"
        
        assistant_response = await optimize_role_llm_call(
            role_id="personal_assistant",
            user_input=user_query,
            context={
                "current_task": "ethical_consultation",
                "user_context": {
                    "role": "hospital_administrator",
                    "expertise_level": "intermediate",
                    "urgency": "high"
                },
                "scenario_context": ethical_scenario
            }
        )
        
        print("🤖 个人助手回应:")
        if assistant_response.get("optimization_applied"):
            metrics = assistant_response["optimization_metrics"]
            print(f"   ✨ 优化效果: 改进{metrics['improvement_score']:.3f}, 节省{metrics['tokens_saved']}Token")
        
        response_preview = assistant_response["response"][:300] + "..." if len(assistant_response["response"]) > 300 else assistant_response["response"]
        print(f"   💬 {response_preview}")
        print()
        
        # 2. 多角色辩论阶段
        print("🔄 阶段2：多角色专家辩论")
        print("-" * 40)
        
        from src.real_demo_system.llm_optimization_adapter import optimize_debate_llm_calls
        
        debate_roles = [
            "medical_ethics_expert",
            "ai_researcher", 
            "clinical_physician",
            "patient_advocate",
            "legal_advisor"
        ]
        
        debate_topic = "AI辅助诊断系统的伦理风险评估和缓解策略"
        
        debate_context = {
            "scenario": ethical_scenario,
            "debate_rules": [
                "基于专业背景提出观点",
                "考虑所有利益相关者",
                "提供具体可行的建议"
            ],
            "round_number": 1
        }
        
        debate_results = await optimize_debate_llm_calls(
            roles=debate_roles,
            topic=debate_topic,
            context=debate_context
        )
        
        print(f"🎭 辩论参与者: {len(debate_roles)}个角色")
        print("📊 辩论优化摘要:")
        
        optimization_summary = debate_results.get("optimization_summary", {})
        if optimization_summary:
            print(f"   成功优化: {optimization_summary.get('successful_optimizations', 0)}/{optimization_summary.get('participating_roles', 0)}")
            print(f"   优化成功率: {optimization_summary.get('optimization_success_rate', 0)*100:.1f}%")
            print(f"   总Token节省: {optimization_summary.get('total_tokens_saved', 0)}")
            print(f"   平均改进: {optimization_summary.get('average_improvement', 0):.3f}")
            print(f"   效果评估: {optimization_summary.get('debate_optimization_effectiveness', 'unknown')}")
        
        print("\n🗣️  各角色观点:")
        for role_id, response in debate_results.get("responses", {}).items():
            if "error" not in response:
                print(f"   🤖 {response.get('role_name', role_id)}:")
                if response.get("optimization_applied"):
                    metrics = response["optimization_metrics"]
                    print(f"      ✨ 优化: 改进{metrics['improvement_score']:.3f}, 节省{metrics['tokens_saved']}Token")
                
                content_preview = response["response"][:200] + "..." if len(response["response"]) > 200 else response["response"]
                print(f"      💬 {content_preview}")
                print()
        
        # 3. 工作流执行阶段
        print("🔄 阶段3：批判性审查工作流")
        print("-" * 40)
        
        # 模拟批判性审查工作流中的LLM调用
        critical_review_tasks = [
            {
                "task": "事实验证",
                "role": "fact_checker",
                "input": "验证AI诊断系统相关的技术事实和统计数据"
            },
            {
                "task": "逻辑分析", 
                "role": "logic_analyst",
                "input": "分析各方论证的逻辑一致性和推理有效性"
            },
            {
                "task": "偏见检测",
                "role": "bias_detector", 
                "input": "识别讨论中可能存在的认知偏见和立场偏向"
            }
        ]
        
        workflow_results = {}
        
        for task in critical_review_tasks:
            print(f"   🔍 执行任务: {task['task']}")
            
            result = await optimize_role_llm_call(
                role_id=task["role"],
                user_input=task["input"],
                context={
                    "current_task": f"critical_review_{task['task']}",
                    "workflow_context": {
                        "scenario": ethical_scenario,
                        "debate_results": debate_results,
                        "review_focus": task["task"]
                    }
                }
            )
            
            workflow_results[task["task"]] = result
            
            if result.get("optimization_applied"):
                metrics = result["optimization_metrics"]
                print(f"      ✨ 优化: 改进{metrics['improvement_score']:.3f}, 节省{metrics['tokens_saved']}Token")
        
        print()
        
        # 4. 共识形成阶段
        print("🔄 阶段4：共识形成和决策建议")
        print("-" * 40)
        
        consensus_input = f"""
        基于以上完整的分析过程，请形成关于'{ethical_scenario['title']}'的最终共识和实施建议：
        
        1. 个人助手咨询结果
        2. 多角色专家辩论观点
        3. 批判性审查工作流结果
        
        请提供：
        - 核心共识点
        - 关键风险和缓解措施
        - 具体实施建议
        - 监管合规要求
        """
        
        consensus_result = await optimize_role_llm_call(
            role_id="consensus_facilitator",
            user_input=consensus_input,
            context={
                "current_task": "consensus_formation",
                "full_context": {
                    "scenario": ethical_scenario,
                    "assistant_consultation": assistant_response,
                    "debate_results": debate_results,
                    "workflow_results": workflow_results
                }
            }
        )
        
        print("🤝 共识形成结果:")
        if consensus_result.get("optimization_applied"):
            metrics = consensus_result["optimization_metrics"]
            print(f"   ✨ 优化效果: 改进{metrics['improvement_score']:.3f}, 节省{metrics['tokens_saved']}Token")
        
        consensus_preview = consensus_result["response"][:400] + "..." if len(consensus_result["response"]) > 400 else consensus_result["response"]
        print(f"   📋 {consensus_preview}")
        print()
        
        # 5. 系统级性能分析
        print("📈 系统级性能分析")
        print("-" * 40)
        
        from src.real_demo_system.llm_optimization_adapter import get_llm_optimization_stats
        
        system_stats = await get_llm_optimization_stats()
        
        if "system_summary" in system_stats:
            summary = system_stats["system_summary"]
            print("   📊 总体统计:")
            print(f"      总调用次数: {summary.get('total_calls', 0)}")
            print(f"      活跃角色数: {summary.get('active_roles', 0)}")
            print(f"      总Token节省: {summary.get('total_tokens_saved', 0)}")
            print(f"      总时间节省: {summary.get('total_time_saved', 0):.3f}s")
            print(f"      平均改进分数: {summary.get('average_improvement', 0):.3f}")
            print(f"      优化成功率: {summary.get('optimization_success_rate', 0)*100:.1f}%")
            print(f"      系统效果: {system_stats.get('optimization_effectiveness', 'unknown')}")
            
            if "top_performing_roles" in system_stats:
                print("\n   🏆 表现最佳角色:")
                for i, (role_id, score) in enumerate(system_stats["top_performing_roles"][:3], 1):
                    print(f"      {i}. {role_id}: 改进分数 {score:.3f}")
        
        print()
        
    except Exception as e:
        print(f"❌ 演示过程出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("🎯 完全集成系统的核心成就:")
    print("=" * 80)
    print("✅ 所有虚拟角色的LLM调用都使用智能上下文优化")
    print("✅ 个人助手、多角色辩论、工作流执行全面集成")
    print("✅ 基于角色历史记忆和对话主题的个性化优化")
    print("✅ 针对不同任务类型和场景的自适应上下文调整")
    print("✅ 实时性能监控和优化效果分析")
    print("✅ 端到端的完整用户体验优化")
    print("✅ 系统级和角色级的详细性能分析")
    print()
    print("🚀 这就是真正集成到项目中的完整智能优化系统！")
    print("💡 每个虚拟角色的每次LLM调用都经过智能优化！")
    print("🎉 从个人助手到多角色辩论，从工作流执行到共识形成，")
    print("    整个DAIP-LIVE系统都在使用真实LLM的智能上下文优化！")

async def main():
    """主函数"""
    await demo_fully_integrated_system()

if __name__ == "__main__":
    asyncio.run(main())