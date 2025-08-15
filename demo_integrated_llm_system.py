#!/usr/bin/env python3
"""集成LLM系统演示

展示所有虚拟角色都使用智能上下文优化的完整系统
"""

import asyncio
import sys

sys.path.append('src')

async def demo_integrated_llm_system():
    """演示集成LLM系统"""
    print("🚀 集成LLM智能优化系统演示")
    print("=" * 70)
    print("💡 所有虚拟角色的LLM调用都将使用智能上下文优化")
    print()
    
    from src.core_services.integrated_llm_manager import IntegratedLLMManager
    
    # 初始化集成LLM管理器
    llm_manager = IntegratedLLMManager()
    
    try:
        print("🔧 初始化集成LLM管理器...")
        await llm_manager.initialize()
        print("✅ 初始化完成")
        print()
        
        # 模拟AI伦理决策分析场景
        print("📋 场景：AI伦理决策分析")
        print("-" * 50)
        
        ethical_dilemma = "医院想部署AI辅助诊断系统，但担心算法偏见可能影响少数族裔患者的诊断准确性"
        
        # 定义参与的虚拟角色
        participating_roles = [
            "ethics_expert",      # 伦理专家
            "ai_researcher",      # AI研究员  
            "medical_doctor",     # 医生
            "policy_maker",       # 政策制定者
            "patient_advocate"    # 患者权益代表
        ]
        
        print(f"🎭 参与角色: {', '.join(participating_roles)}")
        print(f"🔍 伦理议题: {ethical_dilemma}")
        print()
        
        # 第一轮：每个角色独立分析
        print("🔄 第一轮：角色独立分析")
        print("-" * 30)
        
        individual_analyses = {}
        
        for role_id in participating_roles:
            print(f"   🤖 {role_id} 分析中...")
            
            analysis_input = f"请从你的专业角度分析以下AI伦理问题：{ethical_dilemma}"
            
            result = await llm_manager.call_llm_for_role(
                role_id=role_id,
                user_input=analysis_input,
                task_context="AI伦理决策分析",
                additional_context={
                    "analysis_type": "individual",
                    "ethical_dilemma": ethical_dilemma,
                    "required_depth": "detailed"
                }
            )
            
            individual_analyses[role_id] = result
            
            # 显示优化效果
            if result.get("optimization_applied"):
                metrics = result["optimization_metrics"]
                print(f"      ✨ 优化效果: 改进{metrics['improvement_score']:.3f}, 节省{metrics['tokens_saved']}Token")
            
            # 显示回应预览
            response_preview = result["response"][:100] + "..." if len(result["response"]) > 100 else result["response"]
            print(f"      💬 回应预览: {response_preview}")
            print()
        
        # 第二轮：多角色辩论
        print("🔄 第二轮：多角色辩论")
        print("-" * 30)
        
        debate_context = {
            "history": [
                {
                    "round": 1,
                    "type": "individual_analysis",
                    "results": {role_id: result["response"] for role_id, result in individual_analyses.items()}
                }
            ],
            "positions": {
                role_id: "基于第一轮分析的立场" for role_id in participating_roles
            },
            "rules": [
                "基于专业背景提出观点",
                "尊重其他角色的专业意见",
                "寻求平衡和可行的解决方案"
            ]
        }
        
        debate_results = await llm_manager.call_llm_for_multi_role_debate(
            participating_roles=participating_roles,
            debate_topic=ethical_dilemma,
            debate_context=debate_context,
            round_number=2
        )
        
        print("🎯 辩论结果:")
        for role_id, result in debate_results["role_responses"].items():
            if "error" not in result:
                print(f"   🤖 {result['role_name']}:")
                
                if result.get("optimization_applied"):
                    metrics = result["optimization_metrics"]
                    print(f"      ✨ 优化: 改进{metrics['improvement_score']:.3f}, 节省{metrics['tokens_saved']}Token")
                
                response_preview = result["response"][:150] + "..." if len(result["response"]) > 150 else result["response"]
                print(f"      💬 观点: {response_preview}")
                print()
        
        # 显示辩论优化摘要
        optimization_summary = debate_results["optimization_summary"]
        print("📊 辩论优化摘要:")
        print(f"   参与角色: {optimization_summary['participating_roles']}")
        print(f"   成功优化: {optimization_summary['successful_optimizations']}")
        print(f"   优化成功率: {optimization_summary['optimization_success_rate']*100:.1f}%")
        print(f"   总Token节省: {optimization_summary['total_tokens_saved']}")
        print(f"   总时间节省: {optimization_summary['total_time_saved']:.3f}s")
        print(f"   平均改进分数: {optimization_summary['average_improvement']:.3f}")
        print(f"   优化效果: {optimization_summary['debate_optimization_effectiveness']}")
        print()
        
        # 第三轮：共识形成
        print("🔄 第三轮：共识形成")
        print("-" * 30)
        
        consensus_input = f"基于前两轮的分析和辩论，请提出关于'{ethical_dilemma}'的具体解决方案和实施建议"
        
        consensus_results = {}
        
        for role_id in participating_roles:
            print(f"   🤖 {role_id} 提出解决方案...")
            
            result = await llm_manager.call_llm_for_role(
                role_id=role_id,
                user_input=consensus_input,
                task_context="AI伦理共识形成",
                additional_context={
                    "previous_analyses": individual_analyses,
                    "debate_results": debate_results,
                    "consensus_stage": True,
                    "solution_focus": True
                }
            )
            
            consensus_results[role_id] = result
            
            if result.get("optimization_applied"):
                metrics = result["optimization_metrics"]
                print(f"      ✨ 优化: 改进{metrics['improvement_score']:.3f}, 节省{metrics['tokens_saved']}Token")
        
        print()
        
        # 系统级性能分析
        print("📈 系统级性能分析")
        print("-" * 30)
        
        system_analytics = await llm_manager.get_system_wide_analytics()
        
        summary = system_analytics["system_summary"]
        print(f"   总调用次数: {summary['total_calls']}")
        print(f"   活跃角色数: {summary['active_roles']}")
        print(f"   总Token节省: {summary['total_tokens_saved']}")
        print(f"   总时间节省: {summary['total_time_saved']:.3f}s")
        print(f"   平均改进分数: {summary['average_improvement']:.3f}")
        print(f"   优化成功率: {summary['optimization_success_rate']*100:.1f}%")
        print(f"   系统效果评估: {system_analytics['optimization_effectiveness']}")
        print()
        
        # 角色表现排名
        print("🏆 角色优化表现排名:")
        for i, (role_id, improvement_score) in enumerate(system_analytics["top_performing_roles"], 1):
            role_perf = system_analytics["role_performance"][role_id]
            print(f"   {i}. {role_id}: 改进{improvement_score:.3f}, 调用{role_perf['call_count']}次, 节省{role_perf['tokens_saved']}Token")
        
        print()
        
        # 详细角色分析（选择表现最好的角色）
        if system_analytics["top_performing_roles"]:
            top_role = system_analytics["top_performing_roles"][0][0]
            print(f"🔍 详细分析：{top_role}")
            print("-" * 30)
            
            role_analytics = await llm_manager.get_role_performance_analytics(top_role)
            
            perf_summary = role_analytics["performance_summary"]
            print(f"   总调用: {perf_summary['total_calls']}")
            print(f"   Token节省: {perf_summary['total_tokens_saved']}")
            print(f"   时间节省: {perf_summary['total_time_saved']:.3f}s")
            print(f"   平均改进: {perf_summary['average_improvement']:.3f}")
            print(f"   优化成功率: {perf_summary['optimization_success_rate']*100:.1f}%")
            
            context_stats = role_analytics["context_optimization_stats"]
            print(f"   平均上下文压缩: {context_stats['avg_context_compression']*100:.1f}%")
            print(f"   平均Token/调用: {context_stats['avg_tokens_per_call']:.0f}")
            print(f"   平均响应时间: {context_stats['avg_response_time']:.3f}s")
            
            trend = role_analytics["recent_trend"]
            print(f"   最近趋势: {trend['trend_direction']}")
        
        print()
        
    except Exception as e:
        print(f"❌ 演示过程出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await llm_manager.close()
    
    print("🎯 集成系统核心优势:")
    print("=" * 70)
    print("✅ 所有虚拟角色统一使用智能上下文优化")
    print("✅ 基于角色历史记忆和对话主题的个性化优化")
    print("✅ 针对不同任务类型的自适应上下文调整")
    print("✅ 实时性能监控和优化效果分析")
    print("✅ 多角色辩论场景的协同优化")
    print("✅ 系统级和角色级的详细分析报告")
    print()
    print("💡 这就是真正集成到项目中的智能LLM优化系统！")
    print("🚀 每个虚拟角色的每次LLM调用都经过智能优化！")

async def main():
    """主函数"""
    await demo_integrated_llm_system()

if __name__ == "__main__":
    asyncio.run(main())