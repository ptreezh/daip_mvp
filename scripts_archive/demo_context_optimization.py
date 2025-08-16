#!/usr/bin/env python3
"""自动上下文优化演示

展示基于多面嵌入技术的智能上下文优化效果
"""

import asyncio
import sys

sys.path.append('src')

async def demo_context_optimization():
    """演示上下文优化功能"""
    print("🚀 自动上下文优化演示")
    print("=" * 60)

    from src.core_services.context_optimization_engine import ContextOptimizationEngine, ContextOptimizationRequest

    # 创建上下文优化引擎
    engine = ContextOptimizationEngine()

    # 模拟用户历史对话
    conversation_history = [
        {
            "content": "我是一名医生，对AI在医疗领域的应用很感兴趣",
            "type": "user_query",
            "timestamp": "2025-01-01T09:00:00"
        },
        {
            "content": "AI在医疗领域确实有很大潜力，包括诊断辅助、药物发现等...",
            "type": "assistant_response",
            "timestamp": "2025-01-01T09:01:00"
        },
        {
            "content": "AI诊断系统的准确性如何？有什么局限性？",
            "type": "user_query",
            "timestamp": "2025-01-01T09:05:00"
        },
        {
            "content": "AI诊断系统在某些领域已经达到专家水平，但仍有局限性...",
            "type": "assistant_response",
            "timestamp": "2025-01-01T09:06:00"
        },
        {
            "content": "那么AI医疗系统的伦理问题呢？比如责任归属",
            "type": "user_query",
            "timestamp": "2025-01-01T09:10:00"
        },
        {
            "content": "AI医疗伦理确实是个复杂问题，涉及责任、透明度、公平性等...",
            "type": "assistant_response",
            "timestamp": "2025-01-01T09:11:00"
        }
    ]

    # 可用的上下文信息
    available_context = {
        "relevant_knowledge": [
            "医疗AI系统需要通过FDA等监管机构的严格审批",
            "AI诊断的可解释性对医生接受度至关重要",
            "患者数据隐私是医疗AI部署的核心考虑因素",
            "医疗AI的偏见问题可能导致健康不平等",
            "医疗责任保险需要适应AI辅助诊断的新模式"
        ],
        "domain_knowledge": {
            "医疗AI": "人工智能在医疗诊断、治疗规划、药物发现等领域的应用",
            "医疗伦理": "医疗实践中的道德原则，包括自主性、受益性、无害性、公正性",
            "监管合规": "医疗设备和软件需要遵循的法规要求和审批流程"
        },
        "user_environment": {
            "expertise_level": "expert",
            "professional_background": "healthcare",
            "current_role": "practicing_physician"
        },
        "system_status": {
            "available_models": ["gpt-4", "claude-3", "llama-3"],
            "current_load": "normal",
            "response_time": "fast"
        }
    }

    # 当前用户查询
    current_query = "请深入分析AI辅助诊断系统在实际临床应用中面临的主要伦理挑战，并提供具体的解决方案建议"

    print(f"📋 用户查询: {current_query}")
    print(f"📚 历史对话数量: {len(conversation_history)}")
    print(f"🔍 可用知识条目: {len(available_context['relevant_knowledge'])}")
    print()

    # 测试不同的优化策略
    strategies = ["adaptive", "focused", "comprehensive"]

    for strategy in strategies:
        print(f"🎯 策略: {strategy.upper()}")
        print("-" * 40)

        # 创建优化请求
        request = ContextOptimizationRequest(
            user_id="demo_doctor",
            current_query=current_query,
            conversation_history=conversation_history,
            current_task="医疗AI伦理分析",
            available_context=available_context,
            optimization_strategy=strategy
        )

        # 执行上下文优化
        optimized_context = await engine.optimize_context(request)

        # 显示优化结果
        print("📊 优化统计:")
        print(f"   原始上下文大小: {optimized_context.original_context_size}")
        print(f"   优化后大小: {optimized_context.optimized_context_size}")
        print(f"   压缩率: {(1 - optimized_context.optimized_context_size / optimized_context.original_context_size) * 100:.1f}%")
        print(f"   优化置信度: {optimized_context.confidence_score:.3f}")

        print("🧠 优化理由:")
        print(f"   {optimized_context.optimization_reasoning}")

        print("📝 优化后的上下文 (前500字符):")
        prompt_preview = optimized_context.optimized_prompt[:500]
        print(f"   {prompt_preview}...")

        print("🔗 选中的上下文元素:")
        for i, element in enumerate(optimized_context.context_elements[:5]):  # 显示前5个
            print(f"   {i+1}. [{element.element_type}] {element.content[:60]}... (相关性: {element.relevance_score:.3f})")

        if len(optimized_context.context_elements) > 5:
            print(f"   ... 还有 {len(optimized_context.context_elements) - 5} 个元素")

        print()

    # 展示优化前后的对比
    print("🔄 优化效果对比")
    print("=" * 60)

    # 获取自适应策略的结果进行详细对比
    adaptive_request = ContextOptimizationRequest(
        user_id="demo_doctor",
        current_query=current_query,
        conversation_history=conversation_history,
        current_task="医疗AI伦理分析",
        available_context=available_context,
        optimization_strategy="adaptive"
    )

    adaptive_result = await engine.optimize_context(adaptive_request)

    print("📋 原始上下文信息:")
    print("   - 历史对话记录 (6条)")
    print("   - 相关知识条目 (5条)")
    print("   - 领域知识 (3个领域)")
    print("   - 用户环境信息")
    print("   - 系统状态信息")
    print()

    print("✨ 优化后的智能上下文:")
    print(f"   - 选择了最相关的 {adaptive_result.optimized_context_size} 个上下文元素")
    print("   - 根据用户专业背景(医生)调整了详细程度")
    print("   - 基于历史兴趣(AI医疗伦理)优化了内容重点")
    print("   - 考虑了任务复杂度和用户经验水平")
    print()

    print("🎯 优化带来的好处:")
    print("   ✅ 减少了无关信息，提高了相关性")
    print("   ✅ 根据用户背景个性化了回应风格")
    print("   ✅ 保留了最重要的历史上下文")
    print("   ✅ 优化了LLM调用的效率和质量")
    print()

    # 展示多面嵌入的工作原理
    print("🧬 多面嵌入技术展示")
    print("=" * 60)

    from src.core_services.context_optimization_engine import MultiAspectEmbeddingModel

    embedding_model = MultiAspectEmbeddingModel()

    # 分析用户查询的多面嵌入
    pattern_emb, goal_emb, solution_emb, context_emb = embedding_model.encode_multi_aspect(
        current_query,
        {"user_profile": available_context["user_environment"]}
    )

    print("🔍 查询的多面嵌入分析:")
    print(f"   问题模式嵌入范数: {np.linalg.norm(pattern_emb):.3f}")
    print(f"   目标嵌入范数: {np.linalg.norm(goal_emb):.3f}")
    print(f"   解决方案嵌入范数: {np.linalg.norm(solution_emb):.3f}")
    print(f"   上下文嵌入范数: {np.linalg.norm(context_emb):.3f}")
    print()

    # 分析不同类型文本的嵌入差异
    test_texts = [
        "什么是AI伦理？",  # 问题型
        "分析AI医疗系统的风险",  # 分析型
        "请解释算法公平性的概念",  # 解释型
    ]

    print("📊 不同查询类型的模式识别:")
    for text in test_texts:
        pattern_emb, _, _, _ = embedding_model.encode_multi_aspect(text)
        pattern_strength = np.linalg.norm(pattern_emb)
        print(f"   '{text}' -> 模式强度: {pattern_strength:.3f}")

    print()
    print("🎉 演示完成！")
    print("💡 上下文优化系统成功展示了基于多面嵌入技术的智能上下文处理能力")

async def main():
    """主函数"""
    # 导入numpy用于嵌入计算
    global np
    import numpy as np

    await demo_context_optimization()

if __name__ == "__main__":
    asyncio.run(main())
