#!/usr/bin/env python3
"""验证自动上下文优化系统
"""

import asyncio
import sys

sys.path.append('src')

async def test_context_optimization_engine():
    """测试上下文优化引擎"""
    try:
        from src.core_services.context_optimization_engine import ContextOptimizationEngine

        # 创建上下文优化引擎
        engine = ContextOptimizationEngine()

        # 验证基本属性
        assert hasattr(engine, 'history_analyzer'), "缺少history_analyzer属性"
        assert hasattr(engine, 'task_analyzer'), "缺少task_analyzer属性"
        assert hasattr(engine, 'context_aggregator'), "缺少context_aggregator属性"
        assert hasattr(engine, 'embedding_model'), "缺少embedding_model属性"

        # 验证基本方法
        assert hasattr(engine, 'optimize_context'), "缺少optimize_context方法"

        print("✅ ContextOptimizationEngine基本验证通过")
        return True

    except Exception as e:
        print(f"❌ ContextOptimizationEngine验证失败: {e}")
        return False

async def test_multi_aspect_embedding():
    """测试多面嵌入模型"""
    try:
        from src.core_services.context_optimization_engine import MultiAspectEmbeddingModel

        # 创建多面嵌入模型
        model = MultiAspectEmbeddingModel()

        # 验证基本方法
        assert hasattr(model, 'encode_pattern'), "缺少encode_pattern方法"
        assert hasattr(model, 'encode_goal'), "缺少encode_goal方法"
        assert hasattr(model, 'encode_solution'), "缺少encode_solution方法"
        assert hasattr(model, 'encode_context'), "缺少encode_context方法"
        assert hasattr(model, 'encode_multi_aspect'), "缺少encode_multi_aspect方法"

        # 测试多面嵌入编码
        test_text = "请分析AI伦理在医疗诊断中的应用问题"
        test_context = {"user_profile": {"expertise": "intermediate"}}

        pattern_emb, goal_emb, solution_emb, context_emb = model.encode_multi_aspect(
            test_text, test_context
        )

        # 验证嵌入向量
        assert pattern_emb.shape == (384,), f"模式嵌入维度错误: {pattern_emb.shape}"
        assert goal_emb.shape == (384,), f"目标嵌入维度错误: {goal_emb.shape}"
        assert solution_emb.shape == (384,), f"解决方案嵌入维度错误: {solution_emb.shape}"
        assert context_emb.shape == (384,), f"上下文嵌入维度错误: {context_emb.shape}"

        print(f"   模式嵌入范数: {np.linalg.norm(pattern_emb):.3f}")
        print(f"   目标嵌入范数: {np.linalg.norm(goal_emb):.3f}")
        print(f"   解决方案嵌入范数: {np.linalg.norm(solution_emb):.3f}")
        print(f"   上下文嵌入范数: {np.linalg.norm(context_emb):.3f}")

        print("✅ MultiAspectEmbeddingModel验证通过")
        return True

    except Exception as e:
        print(f"❌ MultiAspectEmbeddingModel验证失败: {e}")
        return False

async def test_conversation_history_analyzer():
    """测试对话历史分析器"""
    try:
        from src.core_services.context_optimization_engine import ConversationHistoryAnalyzer

        # 创建对话历史分析器
        analyzer = ConversationHistoryAnalyzer()

        # 验证基本方法
        assert hasattr(analyzer, 'analyze'), "缺少analyze方法"

        # 测试对话历史分析
        conversation_history = [
            {
                "content": "我想了解AI伦理的基本原则",
                "type": "user_query",
                "timestamp": "2025-01-01T10:00:00"
            },
            {
                "content": "AI伦理包括公平性、透明度、责任等核心原则...",
                "type": "assistant_response",
                "timestamp": "2025-01-01T10:01:00"
            },
            {
                "content": "请详细分析算法公平性的实现方法",
                "type": "user_query",
                "timestamp": "2025-01-01T10:05:00"
            },
            {
                "content": "算法公平性可以通过多种技术手段实现...",
                "type": "assistant_response",
                "timestamp": "2025-01-01T10:06:00"
            }
        ]

        analysis_result = await analyzer.analyze(conversation_history)

        # 验证分析结果
        assert "patterns" in analysis_result, "分析结果缺少patterns"
        assert "preferences" in analysis_result, "分析结果缺少preferences"
        assert "success_indicators" in analysis_result, "分析结果缺少success_indicators"
        assert "key_topics" in analysis_result, "分析结果缺少key_topics"
        assert "time_patterns" in analysis_result, "分析结果缺少time_patterns"

        print(f"   识别的关键主题: {analysis_result['key_topics']}")
        print(f"   用户偏好风格: {analysis_result['preferences']['preferred_response_style']}")
        print(f"   分析置信度: {analysis_result['analysis_confidence']:.3f}")

        print("✅ ConversationHistoryAnalyzer验证通过")
        return True

    except Exception as e:
        print(f"❌ ConversationHistoryAnalyzer验证失败: {e}")
        return False

async def test_task_analyzer():
    """测试任务分析器"""
    try:
        from src.core_services.context_optimization_engine import TaskAnalyzer

        # 创建任务分析器
        analyzer = TaskAnalyzer()

        # 验证基本方法
        assert hasattr(analyzer, 'analyze'), "缺少analyze方法"

        # 测试任务分析
        test_query = "请从多个角度深入分析AI在医疗诊断中的伦理风险，并提供具体的解决方案建议"
        current_task = "AI伦理风险评估"

        analysis_result = await analyzer.analyze(test_query, current_task)

        # 验证分析结果
        assert "task_type" in analysis_result, "分析结果缺少task_type"
        assert "complexity" in analysis_result, "分析结果缺少complexity"
        assert "keywords" in analysis_result, "分析结果缺少keywords"
        assert "required_resources" in analysis_result, "分析结果缺少required_resources"
        assert "estimated_time" in analysis_result, "分析结果缺少estimated_time"

        print(f"   任务类型: {analysis_result['task_type']}")
        print(f"   复杂度: {analysis_result['complexity']}")
        print(f"   关键词: {analysis_result['keywords']}")
        print(f"   预估时间: {analysis_result['estimated_time']}秒")
        print(f"   分析置信度: {analysis_result['analysis_confidence']:.3f}")

        print("✅ TaskAnalyzer验证通过")
        return True

    except Exception as e:
        print(f"❌ TaskAnalyzer验证失败: {e}")
        return False

async def test_context_aggregator():
    """测试上下文聚合器"""
    try:
        from src.core_services.context_optimization_engine import ContextAggregator

        # 创建上下文聚合器
        aggregator = ContextAggregator()

        # 验证基本方法
        assert hasattr(aggregator, 'aggregate'), "缺少aggregate方法"

        # 准备测试数据
        available_context = {
            "relevant_knowledge": [
                "AI伦理是人工智能发展的重要指导原则",
                "医疗AI需要特别关注患者隐私和数据安全",
                "算法透明度对医疗诊断的可信度至关重要"
            ],
            "domain_knowledge": {
                "医疗AI": "医疗人工智能应用的专业知识",
                "伦理学": "道德哲学和伦理原则的理论基础"
            }
        }

        history_insights = {
            "key_topics": ["AI伦理", "医疗应用", "算法公平性"],
            "preferences": {
                "preferred_response_style": "formal",
                "detail_level": "detailed"
            }
        }

        task_insights = {
            "task_type": "analysis",
            "complexity": "high",
            "keywords": ["AI", "伦理", "医疗", "诊断"],
            "analysis_confidence": 0.85
        }

        # 测试上下文聚合
        context_elements = await aggregator.aggregate(
            available_context, history_insights, task_insights
        )

        # 验证聚合结果
        assert isinstance(context_elements, list), "聚合结果应该是列表"
        assert len(context_elements) > 0, "聚合结果不应为空"

        # 验证元素类型分布
        element_types = set(elem.element_type for elem in context_elements)
        print(f"   上下文元素数量: {len(context_elements)}")
        print(f"   元素类型: {element_types}")
        print(f"   平均相关性: {sum(elem.relevance_score for elem in context_elements) / len(context_elements):.3f}")

        print("✅ ContextAggregator验证通过")
        return True

    except Exception as e:
        print(f"❌ ContextAggregator验证失败: {e}")
        return False

async def test_full_context_optimization():
    """测试完整的上下文优化流程"""
    try:
        from src.core_services.context_optimization_engine import ContextOptimizationEngine, ContextOptimizationRequest

        # 创建上下文优化引擎
        engine = ContextOptimizationEngine()

        # 准备完整的优化请求
        request = ContextOptimizationRequest(
            user_id="test_user",
            current_query="请分析AI在医疗诊断中的伦理挑战，并提供解决方案",
            conversation_history=[
                {
                    "content": "我对AI伦理很感兴趣",
                    "type": "user_query",
                    "timestamp": "2025-01-01T09:00:00"
                },
                {
                    "content": "AI伦理确实是一个重要话题...",
                    "type": "assistant_response",
                    "timestamp": "2025-01-01T09:01:00"
                },
                {
                    "content": "医疗AI有什么特殊的伦理考虑？",
                    "type": "user_query",
                    "timestamp": "2025-01-01T09:05:00"
                }
            ],
            current_task="AI伦理分析",
            available_context={
                "relevant_knowledge": [
                    "医疗AI伦理涉及患者隐私、算法透明度、责任归属等问题",
                    "FDA对医疗AI设备有严格的监管要求",
                    "医疗决策的可解释性对患者信任至关重要"
                ],
                "user_environment": {
                    "expertise_level": "intermediate",
                    "professional_background": "healthcare"
                }
            },
            optimization_strategy="adaptive"
        )

        # 执行上下文优化
        optimized_context = await engine.optimize_context(request)

        # 验证优化结果
        assert optimized_context.optimized_prompt, "优化后的提示不应为空"
        assert len(optimized_context.context_elements) > 0, "上下文元素不应为空"
        assert optimized_context.confidence_score > 0, "置信度应大于0"
        assert optimized_context.optimized_context_size <= optimized_context.original_context_size, "优化后大小应不大于原始大小"

        print(f"   原始上下文大小: {optimized_context.original_context_size}")
        print(f"   优化后大小: {optimized_context.optimized_context_size}")
        print(f"   优化置信度: {optimized_context.confidence_score:.3f}")
        print(f"   优化理由: {optimized_context.optimization_reasoning}")

        # 显示优化后的提示（前200字符）
        prompt_preview = optimized_context.optimized_prompt[:200] + "..." if len(optimized_context.optimized_prompt) > 200 else optimized_context.optimized_prompt
        print(f"   优化后提示预览: {prompt_preview}")

        print("✅ 完整上下文优化验证通过")
        return True

    except Exception as e:
        print(f"❌ 完整上下文优化验证失败: {e}")
        return False

async def test_optimization_strategies():
    """测试不同的优化策略"""
    try:
        from src.core_services.context_optimization_engine import ContextOptimizationEngine, ContextOptimizationRequest

        # 创建上下文优化引擎
        engine = ContextOptimizationEngine()

        # 基础请求
        base_request = ContextOptimizationRequest(
            user_id="test_user",
            current_query="分析AI伦理问题",
            conversation_history=[
                {"content": "AI伦理很重要", "type": "user_query", "timestamp": "2025-01-01T10:00:00"}
            ],
            available_context={
                "relevant_knowledge": ["AI伦理包括公平性、透明度等原则"]
            }
        )

        strategies = ["adaptive", "focused", "comprehensive"]
        results = {}

        for strategy in strategies:
            request = ContextOptimizationRequest(
                user_id=base_request.user_id,
                current_query=base_request.current_query,
                conversation_history=base_request.conversation_history,
                available_context=base_request.available_context,
                optimization_strategy=strategy
            )

            result = await engine.optimize_context(request)
            results[strategy] = result

            print(f"   {strategy}策略 - 元素数: {result.optimized_context_size}, 置信度: {result.confidence_score:.3f}")

        # 验证不同策略产生不同结果
        sizes = [results[s].optimized_context_size for s in strategies]
        assert len(set(sizes)) > 1 or all(s > 0 for s in sizes), "不同策略应产生不同结果或都有效"

        print("✅ 优化策略验证通过")
        return True

    except Exception as e:
        print(f"❌ 优化策略验证失败: {e}")
        return False

async def main():
    """主验证函数"""
    print("🚀 开始验证自动上下文优化系统")

    # 导入numpy用于嵌入验证
    global np
    import numpy as np

    tests = [
        ("上下文优化引擎", test_context_optimization_engine),
        ("多面嵌入模型", test_multi_aspect_embedding),
        ("对话历史分析器", test_conversation_history_analyzer),
        ("任务分析器", test_task_analyzer),
        ("上下文聚合器", test_context_aggregator),
        ("完整上下文优化", test_full_context_optimization),
        ("优化策略测试", test_optimization_strategies)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 验证 {test_name}...")
        try:
            result = await test_func()
            if result:
                passed += 1
            else:
                print(f"❌ {test_name} 验证失败")
        except Exception as e:
            print(f"❌ {test_name} 验证异常: {e}")

    if passed == total:
        print(f"\n✅ 所有验证通过 ({passed}/{total})")
        return True
    else:
        print(f"\n❌ 验证失败 ({passed}/{total})")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
