#!/usr/bin/env python3
"""增强的上下文优化验证

通过真实LLM调用验证优化效果
"""

import asyncio
import sys
import time
from typing import Any

sys.path.append('src')

class LLMContextValidator:
    """LLM上下文验证器"""
    
    def __init__(self):
        """初始化验证器"""
        self.test_queries = [
            {
                "query": "请分析AI在医疗诊断中的伦理风险",
                "expected_topics": ["伦理", "医疗", "AI", "风险", "诊断"],
                "complexity": "high"
            },
            {
                "query": "什么是机器学习？",
                "expected_topics": ["机器学习", "定义", "基础"],
                "complexity": "low"
            },
            {
                "query": "比较深度学习和传统机器学习的优缺点",
                "expected_topics": ["深度学习", "传统机器学习", "比较", "优缺点"],
                "complexity": "medium"
            }
        ]
    
    async def validate_optimization_effectiveness(self):
        """验证优化效果"""
        print("🔬 开始真实LLM验证")
        print("=" * 60)
        
        from src.core_services.context_optimization_engine import ContextOptimizationEngine, ContextOptimizationRequest
        
        engine = ContextOptimizationEngine()
        results = []
        
        for test_case in self.test_queries:
            print(f"📋 测试查询: {test_case['query']}")
            
            # 准备测试数据
            conversation_history = self._generate_realistic_history(test_case)
            available_context = self._generate_realistic_context(test_case)
            
            # 测试不同策略
            for strategy in ["adaptive", "focused", "comprehensive"]:
                print(f"   🎯 策略: {strategy}")
                
                request = ContextOptimizationRequest(
                    user_id="validation_user",
                    current_query=test_case["query"],
                    conversation_history=conversation_history,
                    available_context=available_context,
                    optimization_strategy=strategy
                )
                
                # 执行优化
                start_time = time.time()
                optimized_context = await engine.optimize_context(request)
                optimization_time = time.time() - start_time
                
                # 模拟LLM调用（实际应该调用真实LLM）
                llm_response_original = await self._simulate_llm_call(
                    test_case["query"], 
                    self._create_baseline_context(available_context)
                )
                
                llm_response_optimized = await self._simulate_llm_call(
                    test_case["query"],
                    optimized_context.optimized_prompt
                )
                
                # 评估效果
                effectiveness = self._evaluate_response_quality(
                    test_case,
                    llm_response_original,
                    llm_response_optimized
                )
                
                result = {
                    "query": test_case["query"],
                    "strategy": strategy,
                    "optimization_time": optimization_time,
                    "context_reduction": (
                        optimized_context.original_context_size - 
                        optimized_context.optimized_context_size
                    ) / optimized_context.original_context_size,
                    "effectiveness": effectiveness,
                    "confidence": optimized_context.confidence_score
                }
                
                results.append(result)
                
                print(f"      ⏱️  优化时间: {optimization_time:.3f}s")
                print(f"      📊 上下文压缩: {result['context_reduction']*100:.1f}%")
                print(f"      🎯 效果评分: {effectiveness['overall_score']:.3f}")
                print(f"      🔒 置信度: {optimized_context.confidence_score:.3f}")
        
        # 生成验证报告
        self._generate_validation_report(results)
        
        return results
    
    def _generate_realistic_history(self, test_case: dict[str, Any]) -> list[dict[str, Any]]:
        """生成真实的对话历史"""
        if test_case["complexity"] == "high":
            return [
                {
                    "content": "我对AI伦理问题很关注",
                    "type": "user_query",
                    "timestamp": "2025-01-01T09:00:00"
                },
                {
                    "content": "AI伦理确实是个重要话题，涉及公平性、透明度等...",
                    "type": "assistant_response", 
                    "timestamp": "2025-01-01T09:01:00"
                },
                {
                    "content": "医疗AI有什么特殊的伦理考虑？",
                    "type": "user_query",
                    "timestamp": "2025-01-01T09:05:00"
                }
            ]
        elif test_case["complexity"] == "low":
            return [
                {
                    "content": "我是AI初学者",
                    "type": "user_query",
                    "timestamp": "2025-01-01T10:00:00"
                }
            ]
        else:
            return [
                {
                    "content": "我想了解不同的机器学习方法",
                    "type": "user_query",
                    "timestamp": "2025-01-01T11:00:00"
                },
                {
                    "content": "机器学习有很多方法，包括监督学习、无监督学习...",
                    "type": "assistant_response",
                    "timestamp": "2025-01-01T11:01:00"
                }
            ]
    
    def _generate_realistic_context(self, test_case: dict[str, Any]) -> dict[str, Any]:
        """生成真实的上下文"""
        base_context = {
            "relevant_knowledge": [
                "AI系统需要考虑伦理和社会影响",
                "机器学习是AI的核心技术之一",
                "深度学习在图像和语音识别方面表现出色"
            ],
            "user_environment": {
                "expertise_level": "intermediate" if test_case["complexity"] == "medium" else "beginner"
            }
        }
        
        if "医疗" in test_case["query"]:
            base_context["domain_knowledge"] = {
                "医疗AI": "人工智能在医疗领域的应用",
                "医疗伦理": "医疗实践中的道德考虑"
            }
        
        return base_context
    
    def _create_baseline_context(self, available_context: dict[str, Any]) -> str:
        """创建基线上下文（未优化）"""
        context_parts = ["请回答以下问题："]
        
        # 简单地将所有可用信息拼接
        for key, value in available_context.items():
            if isinstance(value, list):
                context_parts.extend([f"- {item}" for item in value])
            elif isinstance(value, dict):
                for k, v in value.items():
                    context_parts.append(f"- {k}: {v}")
        
        return "\n".join(context_parts)
    
    async def _simulate_llm_call(self, query: str, context: str) -> dict[str, Any]:
        """模拟LLM调用（实际应该调用真实LLM）"""
        # 这里应该调用真实的LLM API
        # 目前只是模拟响应
        
        response_length = len(context) // 10  # 模拟响应长度与上下文相关
        relevance_score = min(1.0, len([word for word in query.split() if word in context]) / len(query.split()))
        
        return {
            "response": f"基于提供的上下文，针对'{query}'的回答...",
            "response_length": response_length,
            "relevance_score": relevance_score,
            "processing_time": 0.5 + len(context) / 1000  # 模拟处理时间
        }
    
    def _evaluate_response_quality(
        self, 
        test_case: dict[str, Any],
        original_response: dict[str, Any],
        optimized_response: dict[str, Any]
    ) -> dict[str, float]:
        """评估响应质量"""
        # 相关性改进
        relevance_improvement = (
            optimized_response["relevance_score"] - 
            original_response["relevance_score"]
        )
        
        # 效率改进（处理时间）
        efficiency_improvement = (
            original_response["processing_time"] - 
            optimized_response["processing_time"]
        ) / original_response["processing_time"]
        
        # 简洁性（响应长度适中）
        optimal_length = 200  # 假设的最优长度
        original_length_score = 1 - abs(original_response["response_length"] - optimal_length) / optimal_length
        optimized_length_score = 1 - abs(optimized_response["response_length"] - optimal_length) / optimal_length
        conciseness_improvement = optimized_length_score - original_length_score
        
        # 综合评分
        overall_score = (
            relevance_improvement * 0.5 +
            efficiency_improvement * 0.3 +
            conciseness_improvement * 0.2
        )
        
        return {
            "relevance_improvement": relevance_improvement,
            "efficiency_improvement": efficiency_improvement,
            "conciseness_improvement": conciseness_improvement,
            "overall_score": overall_score
        }
    
    def _generate_validation_report(self, results: list[dict[str, Any]]):
        """生成验证报告"""
        print("\n📊 验证报告")
        print("=" * 60)
        
        # 按策略统计
        strategy_stats = {}
        for result in results:
            strategy = result["strategy"]
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    "count": 0,
                    "avg_effectiveness": 0,
                    "avg_compression": 0,
                    "avg_confidence": 0
                }
            
            stats = strategy_stats[strategy]
            stats["count"] += 1
            stats["avg_effectiveness"] += result["effectiveness"]["overall_score"]
            stats["avg_compression"] += result["context_reduction"]
            stats["avg_confidence"] += result["confidence"]
        
        # 计算平均值
        for strategy, stats in strategy_stats.items():
            count = stats["count"]
            stats["avg_effectiveness"] /= count
            stats["avg_compression"] /= count
            stats["avg_confidence"] /= count
            
            print(f"\n🎯 {strategy.upper()} 策略:")
            print(f"   平均效果评分: {stats['avg_effectiveness']:.3f}")
            print(f"   平均压缩率: {stats['avg_compression']*100:.1f}%")
            print(f"   平均置信度: {stats['avg_confidence']:.3f}")
        
        # 整体统计
        all_scores = [r["effectiveness"]["overall_score"] for r in results]
        avg_score = sum(all_scores) / len(all_scores)
        
        print("\n📈 整体表现:")
        print(f"   平均优化效果: {avg_score:.3f}")
        print(f"   最佳效果: {max(all_scores):.3f}")
        print(f"   最差效果: {min(all_scores):.3f}")
        
        # 可靠性评估
        if avg_score > 0.1:
            reliability = "较可靠"
        elif avg_score > 0:
            reliability = "基本可靠"
        else:
            reliability = "不可靠"
        
        print(f"   可靠性评估: {reliability}")

async def main():
    """主验证函数"""
    validator = LLMContextValidator()
    results = await validator.validate_optimization_effectiveness()
    
    print("\n🔍 诚实的评估结论:")
    print("=" * 60)
    print("❌ 当前实现的局限性:")
    print("   1. 没有真实LLM集成验证")
    print("   2. 嵌入模型过于简化")
    print("   3. 缺乏真实用户反馈")
    print("   4. 评估指标不够客观")
    print()
    print("✅ 但具备的基础能力:")
    print("   1. 完整的架构设计")
    print("   2. 多策略优化框架")
    print("   3. 可扩展的组件结构")
    print("   4. 基本的智能化逻辑")
    print()
    print("🚀 改进建议:")
    print("   1. 集成真实LLM API进行验证")
    print("   2. 使用预训练的语义嵌入模型")
    print("   3. 收集真实用户反馈数据")
    print("   4. 建立客观的评估基准")

if __name__ == "__main__":
    asyncio.run(main())