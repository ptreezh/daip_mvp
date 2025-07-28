#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实LLM上下文优化演示

展示使用真实LLM进行智能上下文优化的完整过程
"""

import sys
import asyncio
import json
sys.path.append('src')

async def demo_real_llm_optimization():
    """演示真实LLM上下文优化"""
    print("🚀 真实LLM智能上下文优化演示")
    print("=" * 70)
    
    from src.core_services.real_llm_context_optimizer import IntelligentContextOptimizer
    
    optimizer = IntelligentContextOptimizer()
    await optimizer.initialize()
    
    # 复杂的医疗AI伦理分析场景
    user_query = "作为医院管理者，我需要了解部署AI辅助诊断系统的完整伦理风险评估和具体的风险缓解策略"
    
    conversation_history = [
        {
            "type": "user_query",
            "content": "我们医院正在考虑引入AI辅助诊断系统"
        },
        {
            "type": "assistant_response", 
            "content": "AI辅助诊断系统确实能提高诊断效率和准确性，但需要考虑多个方面..."
        },
        {
            "type": "user_query",
            "content": "主要的技术挑战是什么？"
        },
        {
            "type": "assistant_response",
            "content": "主要技术挑战包括数据质量、模型可解释性、系统集成等..."
        },
        {
            "type": "user_query",
            "content": "那伦理方面呢？我们需要注意什么？"
        },
        {
            "type": "assistant_response",
            "content": "伦理方面需要考虑患者隐私、算法公平性、责任归属等重要问题..."
        }
    ]
    
    available_context = {
        "relevant_knowledge": [
            "FDA要求医疗AI设备必须通过510(k)预市场审查或PMA审批",
            "GDPR和HIPAA对医疗数据处理有严格的隐私保护要求",
            "AI诊断系统的可解释性直接影响医生的信任度和接受度",
            "算法偏见可能导致某些人群的诊断准确性下降",
            "医疗责任保险需要明确AI辅助诊断的责任分担机制",
            "患者知情同意需要包含AI系统使用的相关信息",
            "医疗AI系统需要持续监控和定期重新验证",
            "跨机构数据共享面临技术和法律双重挑战",
            "AI系统故障或错误诊断的应急处理预案必不可少",
            "医护人员需要接受AI系统使用的专业培训"
        ],
        "domain_knowledge": {
            "医疗AI监管": "FDA、CE标记、NMPA等监管机构对医疗AI产品的审批要求和流程",
            "医疗数据隐私": "HIPAA、GDPR等法规对医疗数据收集、存储、使用的规定",
            "医疗伦理原则": "自主性、受益性、无害性、公正性四大医疗伦理基本原则",
            "AI可解释性": "医疗AI决策过程的透明度和可理解性要求",
            "算法公平性": "确保AI系统对不同人群提供公平、无偏见的诊断服务"
        },
        "user_environment": {
            "expertise_level": "expert",
            "professional_background": "healthcare_management",
            "current_role": "hospital_administrator",
            "decision_authority": "high",
            "time_constraint": "urgent"
        },
        "system_status": {
            "available_models": ["llama3:instruct", "mistral:latest"],
            "current_load": "normal",
            "response_quality": "high"
        }
    }
    
    print(f"📋 用户查询:")
    print(f"   {user_query}")
    print()
    
    print(f"📚 上下文信息:")
    print(f"   对话历史: {len(conversation_history)} 轮")
    print(f"   相关知识: {len(available_context['relevant_knowledge'])} 条")
    print(f"   领域知识: {len(available_context['domain_knowledge'])} 个领域")
    print(f"   用户背景: {available_context['user_environment']['professional_background']}")
    print()
    
    print("🔄 开始智能优化过程...")
    print("-" * 50)
    
    try:
        result = await optimizer.optimize_context_with_llm(
            user_query=user_query,
            conversation_history=conversation_history,
            available_context=available_context,
            target_model="llama3:instruct"
        )
        
        print("✅ 优化完成！")
        print()
        
        # 显示原始上下文
        print("📄 原始上下文 (前500字符):")
        print("-" * 30)
        print(result.original_context[:500] + "...")
        print()
        
        # 显示优化后上下文
        print("✨ 优化后上下文 (前500字符):")
        print("-" * 30)
        print(result.optimized_context[:500] + "...")
        print()
        
        # 显示性能指标
        print("📊 优化效果指标:")
        print("-" * 30)
        print(f"   改进评分: {result.improvement_score:.3f} (范围: -1到1)")
        print(f"   上下文压缩率: {result.metrics['context_compression_ratio']*100:.1f}%")
        print(f"   Token节省: {result.metrics['token_efficiency']['token_savings']} 个")
        print(f"   响应时间差异: {result.metrics['response_time']['time_difference']:.3f}s")
        print()
        
        # 显示LLM评估理由
        print("🧠 LLM评估理由:")
        print("-" * 30)
        print(f"   {result.optimization_reasoning}")
        print()
        
        # 对比回答质量
        print("🔍 回答质量对比:")
        print("-" * 30)
        
        print("📝 原始回答:")
        print(f"   长度: {len(result.original_response.content)} 字符")
        print(f"   Token使用: {result.original_response.tokens_used}")
        print(f"   响应时间: {result.original_response.response_time:.3f}s")
        print(f"   内容预览: {result.original_response.content[:200]}...")
        print()
        
        print("✨ 优化后回答:")
        print(f"   长度: {len(result.optimized_response.content)} 字符")
        print(f"   Token使用: {result.optimized_response.tokens_used}")
        print(f"   响应时间: {result.optimized_response.response_time:.3f}s")
        print(f"   内容预览: {result.optimized_response.content[:200]}...")
        print()
        
        # 详细分析
        print("🔬 详细分析:")
        print("-" * 30)
        
        if result.improvement_score > 0.3:
            print("   🎉 显著改进！优化后的回答明显更好")
        elif result.improvement_score > 0.1:
            print("   ✅ 有效改进！优化产生了积极效果")
        elif result.improvement_score > 0:
            print("   📈 轻微改进！优化有一定效果")
        else:
            print("   ⚠️  改进有限！可能需要调整优化策略")
        
        compression = result.metrics['context_compression_ratio']
        if compression > 0.3:
            print("   🗜️  大幅压缩！显著减少了上下文长度")
        elif compression > 0.1:
            print("   📉 适度压缩！合理优化了上下文大小")
        elif compression > 0:
            print("   📏 轻微压缩！稍微减少了上下文")
        else:
            print("   📈 上下文扩展！可能添加了重要信息")
        
        token_savings = result.metrics['token_efficiency']['token_savings']
        if token_savings > 100:
            print("   💰 显著节省Token！大幅降低了调用成本")
        elif token_savings > 50:
            print("   💵 适度节省Token！有效控制了成本")
        elif token_savings > 0:
            print("   💸 轻微节省Token！稍微降低了成本")
        else:
            print("   💳 Token使用增加！可能为了提高质量")
        
    except Exception as e:
        print(f"❌ 优化过程出错: {e}")
    
    finally:
        await optimizer.close()
    
    print()
    print("🎯 真实LLM优化的核心优势:")
    print("=" * 70)
    print("✅ 使用真实LLM模型进行智能分析和优化")
    print("✅ 基于语义理解而非简单规则匹配")
    print("✅ 通过LLM评估提供客观的效果评价")
    print("✅ 实时适应不同类型的查询和上下文")
    print("✅ 提供可解释的优化决策理由")
    print("✅ 真实的性能指标和成本效益分析")
    print()
    print("💡 这就是真正智能的上下文优化！")

async def main():
    """主函数"""
    await demo_real_llm_optimization()

if __name__ == "__main__":
    asyncio.run(main())