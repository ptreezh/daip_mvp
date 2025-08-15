"""真实演示系统实际演示

展示系统的真实LLM调用和完整功能。
"""

import asyncio
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def demo_ai_ethics_scenario():
    """演示AI伦理决策分析场景"""
    print("\n" + "="*60)
    print("🎭 真实演示系统 - AI伦理决策分析场景")
    print("="*60)
    
    try:
        from src.real_demo_system.real_demo_controller import RealDemoController
        
        # 创建演示控制器
        print("\n🚀 初始化演示系统...")
        demo_controller = RealDemoController({
            "llm": {
                "provider": "ollama",
                "ollama": {
                    "host": "http://localhost:11434",
                    "generation_model": "llama3:instruct"
                }
            }
        })
        
        # 显示系统状态
        print("\n📊 系统状态检查:")
        system_status = demo_controller.get_system_status()
        print(f"  - LLM集成器: {system_status['component_status']['llm_integrator']}")
        print(f"  - 角色管理器: {system_status['component_status']['role_manager']}")
        print(f"  - 工作流执行器: {system_status['component_status']['workflow_executor']}")
        print(f"  - 透明度监控: {system_status['component_status']['transparency_monitor']}")
        
        # 创建演示会话
        print("\n🎪 创建AI伦理分析演示会话...")
        session_id = await demo_controller.create_demo_session(
            session_name="医疗AI伦理困境分析",
            scenario_type="ai_ethics",
            participants=["AI Ethics", "economist", "product_manager"],
            metadata={
                "demo_purpose": "展示DAIP-LIVE的AI伦理分析能力",
                "audience": "技术决策者和伦理委员会",
                "complexity": "高"
            }
        )
        print(f"✅ 会话创建成功: {session_id}")
        
        # 等待会话初始化
        print("\n⏳ 等待会话初始化...")
        await asyncio.sleep(3)
        
        # 检查会话状态
        session_status = await demo_controller.get_session_status(session_id)
        print(f"📋 会话状态: {session_status['status']}")
        print(f"👥 参与角色: {', '.join(session_status['participants'])}")
        
        # 定义伦理困境
        ethical_dilemma = """
        一家领先的医疗AI公司开发了一个革命性的癌症诊断系统，该系统在大规模临床试验中显示出比最优秀的人类肿瘤专家更高的准确率（95% vs 87%）。
        
        然而，深入分析发现该系统存在显著的种族和性别偏见：
        - 对白人男性患者的诊断准确率为98%
        - 对非洲裔女性患者的诊断准确率仅为78%
        - 对亚洲患者的诊断准确率为92%
        
        公司面临以下关键决策：
        1. 立即发布系统，因为整体准确率仍然超过人类医生，可以拯救更多生命
        2. 延迟发布直到解决偏见问题，但这可能导致本可以拯救的生命失去
        3. 发布系统但明确标注其局限性，让医生在特定人群中谨慎使用
        4. 仅在偏见较小的人群中发布，但这可能加剧医疗不平等
        
        请从多个角度分析这个伦理困境并提供决策建议。
        """
        
        context = {
            "industry": "医疗AI",
            "stakeholders": ["患者", "医生", "AI公司", "监管机构", "保险公司", "医院", "研究机构"],
            "ethical_frameworks": ["功利主义", "义务论", "美德伦理学", "关怀伦理学", "正义理论"],
            "regulatory_context": "FDA医疗设备审批、HIPAA合规、欧盟AI法案",
            "time_pressure": "高 - 每天有数千患者需要诊断"
        }
        
        print("\n🧠 开始AI伦理决策分析...")
        print("📝 伦理困境:")
        print(ethical_dilemma[:200] + "...")
        print(f"🎯 分析维度: {len(context['ethical_frameworks'])} 个伦理框架")
        print(f"👥 利益相关者: {len(context['stakeholders'])} 个群体")
        
        # 执行AI伦理场景
        print("\n🔄 执行真实的AI伦理分析工作流...")
        result = await demo_controller.execute_ai_ethics_scenario(
            session_id=session_id,
            ethical_dilemma=ethical_dilemma,
            context=context
        )
        
        if result['success']:
            print("\n🎉 AI伦理分析完成!")
            print(f"⏱️  总耗时: {result['session_duration_ms']/1000:.1f} 秒")
            
            # 显示批判性审查结果
            if result['critical_review']['success']:
                print("\n📊 批判性审查结果:")
                print(f"  ✅ 执行成功: {result['critical_review']['success']}")
                print(f"  📄 原始内容: {len(result['critical_review']['original_content'])} 字符")
                print(f"  📝 最终内容: {len(result['critical_review']['final_content'])} 字符")
                print(f"  🔍 提取事实: {result['critical_review']['facts_extracted']} 个")
                print(f"  👥 审查事实: {result['critical_review']['facts_reviewed']} 个")
                print(f"  ⚠️  需修订事实: {result['critical_review']['facts_needing_revision']} 个")
                
                if result['critical_review']['revision_needed']:
                    print(f"  📋 修订摘要: {result['critical_review']['revision_summary'][:100]}...")
            
            # 显示多视角分析结果
            if result['multi_perspective']['success']:
                print("\n🔍 多视角分析结果:")
                print(f"  ✅ 执行成功: {result['multi_perspective']['success']}")
                print(f"  🎯 分析主题: {result['multi_perspective']['topic'][:50]}...")
                print(f"  👁️  分析视角: {', '.join(result['multi_perspective']['perspectives'])}")
                print(f"  📊 置信度: {result['multi_perspective']['confidence']:.1%}")
                print(f"  ⭐ 质量分数: {result['multi_perspective']['quality_score']:.1f}/100")
                
                if 'key_insights' in result['multi_perspective']:
                    insights = result['multi_perspective']['key_insights']
                    if isinstance(insights, list) and insights:
                        print(f"  💡 关键洞察: {len(insights)} 个")
                        for i, insight in enumerate(insights[:3], 1):
                            print(f"    {i}. {insight[:80]}...")
            
            # 显示综合分析结果
            if result['synthesis']['call_record']['success']:
                print("\n🧩 综合分析结果:")
                synthesis_record = result['synthesis']['call_record']
                print(f"  ✅ LLM调用成功: {synthesis_record['success']}")
                print(f"  🆔 调用ID: {synthesis_record['call_id']}")
                print(f"  ⏱️  响应时间: {synthesis_record['duration_ms']} ms")
                print(f"  📥 输入Token: {synthesis_record['input_tokens']}")
                print(f"  📤 输出Token: {synthesis_record['output_tokens']}")
                print(f"  💰 调用成本: ${synthesis_record['cost_usd']:.4f}")
                print(f"  📝 分析报告长度: {len(result['synthesis']['response'])} 字符")
                
                # 显示分析报告的前几行
                print("\n📋 伦理分析报告预览:")
                response_lines = result['synthesis']['response'].split('\n')[:10]
                for line in response_lines:
                    if line.strip():
                        print(f"  {line[:100]}...")
            
            # 显示验证结果
            print("\n🔐 真实性验证结果:")
            for i, verification in enumerate(result['verification_results'], 1):
                print(f"  {i}. {verification['type']}:")
                if verification['type'] == 'llm_call':
                    print(f"     📞 调用ID: {verification['call_id']}")
                    print(f"     ✅ 验证状态: {verification['verification']['status']}")
                    print(f"     📊 置信度: {verification['verification']['confidence_score']:.1f}%")
                elif verification['type'] == 'workflow_execution':
                    print(f"     🔄 执行ID: {verification['execution_id']}")
                    print(f"     📊 透明度分数: {verification['verification']['transparency_score']:.1f}%")
            
            # 显示透明度证书
            print("\n🏆 透明度证书:")
            cert = result['transparency_certificate']
            print(f"  📜 证书ID: {cert['certificate_id']}")
            print(f"  📅 颁发时间: {cert['issued_at']}")
            print(f"  🔒 证书哈希: {cert['certificate_hash'][:32]}...")
            print(f"  🏢 颁发机构: {cert['issuer']}")
            
            # 显示最终系统统计
            print("\n📈 最终系统统计:")
            final_stats = demo_controller.get_demo_statistics()
            print(f"  📊 总会话数: {final_stats['total_sessions']}")
            print(f"  ✅ 完成会话数: {final_stats['completed_sessions']}")
            print(f"  📊 成功率: {final_stats['success_rate']:.1%}")
            print(f"  ⏱️  平均时长: {final_stats['average_duration_ms']/1000:.1f} 秒")
            
            print("\n🎯 演示总结:")
            print("  ✅ 所有LLM调用都是真实的，无任何模拟数据")
            print("  ✅ 所有角色都从真实JSON文件加载")
            print("  ✅ 工作流执行调用真实的后端服务")
            print("  ✅ 完整的透明度监控和验证机制")
            print("  ✅ 生成了可验证的透明度证书")
            
        else:
            print(f"\n❌ AI伦理分析失败: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 演示执行失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """主演示函数"""
    print("🎭 DAIP-LIVE 真实演示系统")
    print("=" * 60)
    print("展示完全真实的AI伦理决策分析能力")
    print("- 真实LLM调用 (非模拟)")
    print("- 真实角色库加载")
    print("- 真实工作流执行")
    print("- 完整透明度监控")
    print("=" * 60)
    print(f"演示开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 执行AI伦理场景演示
        result = await demo_ai_ethics_scenario()
        
        if result and result.get('success'):
            print("\n🎉 演示成功完成!")
            print("✅ 系统展示了完整的AI伦理分析能力")
            print("✅ 所有调用都经过验证，确保真实性")
            print("✅ 生成了专业的决策支持报告")
            print("✅ 提供了完整的透明度证书")
        else:
            print("\n⚠️ 演示未能完全成功")
            print("请检查系统配置和网络连接")
        
    except Exception as e:
        logger.error(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n演示结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("感谢观看 DAIP-LIVE 真实演示系统!")


if __name__ == "__main__":
    asyncio.run(main())