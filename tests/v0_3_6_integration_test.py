"""@Time    : 2025-08-04 12:30:00
@Author  : DAIP-LIVE Team
@File    : test_v0_3_6_integration.py
@Description:
    Integration test for V0.3.6 Multi-perspective Synthesis Workflow intelligence.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

from src.subagents.dynamic_weight import DynamicWeightAdjuster, PerformanceMonitor
from src.subagents.intelligent_synthesis import EnhancedQualityEvaluator, IntelligentSynthesisAgent
from src.subagents.visualization import MultiPerspectiveVisualizer, VisualizationType


# Mock LLM interface for testing
class MockLLMInterface:
    """Mock LLM interface for testing."""
    
    def __init__(self):
        self.config = {"model": "mock-model"}
    
    async def generate(self, messages: list[dict[str, Any]], participant_id: str = None) -> dict[str, Any]:
        """Generate mock response."""
        return {
            "content": "这是一个综合分析的模拟响应。基于多位专家的观点，我们可以得出以下结论：\n\n1. 深度分析：该问题涉及多个层面的复杂因素，需要从根本机制进行分析。\n2. 多维度整合：经济、社会、技术三个维度相互影响，形成复杂系统。\n3. 冲突解决：通过平衡不同视角，可以找到建设性的解决方案。\n4. 洞察生成：关键在于系统性思维和长期视角的建立。\n\n综上所述，建议采取综合性策略，兼顾各方利益，实现可持续发展。",
            "token_usage": {"total_tokens": 250}
        }

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_intelligent_synthesis():
    """Test intelligent synthesis functionality."""
    logger.info("=== Testing Intelligent Synthesis Agent ===")
    
    # Initialize agent
    llm_interface = MockLLMInterface()
    synthesis_agent = IntelligentSynthesisAgent(llm_interface)
    
    # Test data
    topic = "人工智能对社会就业的影响"
    viewpoints = [
        {
            "expert_name": "经济学家",
            "perspective": "经济",
            "viewpoint": "AI将提高生产效率，创造新的就业机会，但短期内可能导致结构性失业。需要政策干预来平滑过渡期。",
            "supporting_evidence": ["历史技术革命数据", "生产力提升研究"],
            "confidence": 0.8
        },
        {
            "expert_name": "社会学家",
            "perspective": "社会",
            "viewpoint": "AI将重塑社会结构，改变工作性质，需要重新思考教育体系和社会保障网络。",
            "supporting_evidence": ["社会变迁理论", "劳动力市场研究"],
            "confidence": 0.75
        },
        {
            "expert_name": "技术专家",
            "perspective": "技术",
            "viewpoint": "AI技术发展速度超过预期，需要加强人机协作研究，发展新的技能培训体系。",
            "supporting_evidence": ["技术发展趋势", "人机交互研究"],
            "confidence": 0.85
        }
    ]
    
    conflicts = [
        {
            "description": "短期影响vs长期影响的权衡",
            "conflict_score": 0.6,
            "involved_perspectives": [0, 1]
        }
    ]
    
    consensus_areas = [
        "需要教育和培训体系的改革",
        "政策干预的必要性",
        "人机协作的重要性"
    ]
    
    # Test synthesis
    result = await synthesis_agent.synthesize_intelligently(
        topic=topic,
        viewpoints=viewpoints,
        conflicts=conflicts,
        consensus_areas=consensus_areas
    )
    
    logger.info(f"Synthesis success: {result['success']}")
    logger.info(f"Synthesis strategy: {result['synthesis_strategy']}")
    logger.info(f"Overall confidence: {result['confidence']:.3f}")
    logger.info(f"Quality assessment: {result['quality_assessment']['overall_quality']:.3f}")
    
    return result

async def test_enhanced_quality_evaluation():
    """Test enhanced quality evaluation."""
    logger.info("=== Testing Enhanced Quality Evaluation ===")
    
    # Initialize evaluator
    quality_evaluator = EnhancedQualityEvaluator()
    
    # Test data
    synthesis_result = {
        "synthesis": """
这是一个关于人工智能对社会就业影响的综合分析。

从经济角度看，AI技术将显著提升生产效率，历史上每次技术革命最终都创造了更多的就业机会。然而，在转型期间，确实存在结构性失业的风险。因此，需要制定针对性的政策来帮助受影响的工人转型。

从社会维度分析，AI正在深刻改变工作性质和社会结构。传统的职业定义正在被重新审视，教育体系需要适应这种变化。社会保障网络也需要相应调整，以支持人们在职业生涯中的多次转型。

技术发展方面，AI的进步速度超出了许多人的预期。关键在于发展人机协作模式，而不是简单的人机替代。这需要新的技能培训体系和思维模式的转变。

综合来看，解决AI对就业影响的关键在于：
1. 教育体系的现代化改革
2. 灵活的社会保障政策
3. 促进人机协作的技术发展
4. 支持终身学习的文化氛围

通过多方面的协同努力，我们可以最大化AI的积极影响，同时最小化其负面影响。
        """,
        "confidence": 0.82
    }
    
    viewpoints = [
        {
            "expert_name": "经济学家",
            "perspective": "经济",
            "viewpoint": "AI将提高生产效率，创造新的就业机会，但短期内可能导致结构性失业。",
            "supporting_evidence": ["历史数据", "研究"],
            "quality_score": 0.8
        },
        {
            "expert_name": "社会学家", 
            "perspective": "社会",
            "viewpoint": "AI将重塑社会结构，需要重新思考教育体系。",
            "supporting_evidence": ["理论", "研究"],
            "quality_score": 0.75
        },
        {
            "expert_name": "技术专家",
            "perspective": "技术", 
            "viewpoint": "需要加强人机协作研究，发展新的技能培训。",
            "supporting_evidence": ["趋势", "研究"],
            "quality_score": 0.85
        }
    ]
    
    cognitive_analysis = {
        "diversity_score": 0.75,
        "convergence_score": 0.65,
        "bias_risk_score": 0.3
    }
    
    # Test evaluation
    result = await quality_evaluator.evaluate_enhanced_quality(
        synthesis_result=synthesis_result,
        viewpoints=viewpoints,
        cognitive_analysis=cognitive_analysis,
        conflicts=[]
    )
    
    logger.info(f"Quality evaluation success: {result.get('evaluation_id', 'N/A')}")
    logger.info(f"Overall quality score: {result['overall_score']:.3f}")
    logger.info(f"Quality grade: {result['quality_grade']}")
    logger.info(f"Recommendations count: {len(result['recommendations'])}")
    
    return result

async def test_dynamic_weight_adjustment():
    """Test dynamic weight adjustment."""
    logger.info("=== Testing Dynamic Weight Adjustment ===")
    
    # Initialize weight adjuster
    weight_adjuster = DynamicWeightAdjuster()
    
    # Test data
    quality_assessment = {
        "overall_score": 0.78,
        "dimensions": {
            "cognitive_depth": {"score": 0.85, "weight": 0.20},
            "insight_quality": {"score": 0.72, "weight": 0.18},
            "synthesis_coherence": {"score": 0.80, "weight": 0.15},
            "perspective_integration": {"score": 0.75, "weight": 0.12},
            "conflict_resolution": {"score": 0.70, "weight": 0.10},
            "evidence_utilization": {"score": 0.82, "weight": 0.10},
            "practical_value": {"score": 0.68, "weight": 0.08},
            "innovation_level": {"score": 0.75, "weight": 0.07}
        }
    }
    
    synthesis_result = {
        "synthesis": "Test synthesis content",
        "processing_time": 15.2
    }
    
    # Test weight adjustment
    result = await weight_adjuster.adjust_weights(
        quality_assessment=quality_assessment,
        synthesis_result=synthesis_result
    )
    
    logger.info(f"Weight adjustment success: {result['success']}")
    logger.info(f"Adjustment strategy: {result['adjustment_strategy']}")
    logger.info(f"Adjustment magnitude: {result['adjustment_magnitude']:.3f}")
    logger.info(f"Original weights sum: {sum(result['original_weights'].values()):.3f}")
    logger.info(f"Adjusted weights sum: {sum(result['adjusted_weights'].values()):.3f}")
    
    return result

async def test_performance_monitoring():
    """Test performance monitoring."""
    logger.info("=== Testing Performance Monitoring ===")
    
    # Initialize performance monitor
    performance_monitor = PerformanceMonitor()
    
    # Record some performance data
    from src.subagents.dynamic_weight.performance_monitor import PerformanceMetric
    
    metrics_to_record = [
        (PerformanceMetric.QUALITY_SCORE, 0.85),
        (PerformanceMetric.SYNTHESIS_SPEED, 12.5),
        (PerformanceMetric.TOKEN_EFFICIENCY, 0.82),
        (PerformanceMetric.CONVERGENCE_RATE, 0.78),
        (PerformanceMetric.ERROR_RATE, 0.05)
    ]
    
    for metric_type, value in metrics_to_record:
        result = await performance_monitor.record_performance(
            metric_type=metric_type,
            value=value,
            metadata={"test": True}
        )
        logger.info(f"Recorded {metric_type.value}: {result['success']}")
    
    # Get performance summary
    summary = await performance_monitor.get_performance_summary()
    
    logger.info(f"Performance summary generated: {summary.get('health_status', {}).get('status', 'N/A')}")
    logger.info(f"Overall health: {summary.get('health_status', {}).get('overall_health', 0.0):.3f}")
    logger.info(f"Data points recorded: {summary.get('monitoring_status', {}).get('data_points_count', 0)}")
    
    return summary

async def test_visualization():
    """Test visualization functionality."""
    logger.info("=== Testing Visualization ===")
    
    # Initialize visualizer
    visualizer = MultiPerspectiveVisualizer()
    
    # Test data
    test_data = {
        "perspectives": ["经济", "社会", "技术", "伦理", "环境"],
        "quality_scores": {
            "经济": 0.85,
            "社会": 0.78,
            "技术": 0.82,
            "伦理": 0.75,
            "环境": 0.80
        },
        "insights": [
            "AI将显著提高生产效率",
            "需要重新设计教育体系",
            "人机协作是关键发展方向",
            "政策干预必不可少",
            "长期影响需要综合考虑"
        ],
        "weights": {
            "cognitive_depth": 0.20,
            "insight_quality": 0.18,
            "synthesis_coherence": 0.15,
            "perspective_integration": 0.12,
            "conflict_resolution": 0.10,
            "evidence_utilization": 0.10,
            "practical_value": 0.08,
            "innovation_level": 0.07
        }
    }
    
    # Test different visualization types
    viz_types = [
        VisualizationType.PERSPECTIVE_RADAR,
        VisualizationType.WEIGHT_DISTRIBUTION,
        VisualizationType.INSIGHT_WORDCLOUD
    ]
    
    results = {}
    for viz_type in viz_types:
        try:
            result = await visualizer.create_visualization(viz_type, test_data)
            results[viz_type.value] = result
            logger.info(f"Created {viz_type.value}: {result['success']}")
        except Exception as e:
            logger.error(f"Failed to create {viz_type.value}: {e}")
            results[viz_type.value] = {"success": False, "error": str(e)}
    
    return results

async def run_integration_test():
    """Run complete integration test."""
    logger.info("Starting V0.3.6 Multi-perspective Synthesis Workflow Integration Test")
    logger.info("=" * 70)
    
    test_results = {}
    
    # Run all tests
    try:
        test_results["intelligent_synthesis"] = await test_intelligent_synthesis()
        logger.info("✓ Intelligent Synthesis Test Completed")
    except Exception as e:
        logger.error(f"✗ Intelligent Synthesis Test Failed: {e}")
        test_results["intelligent_synthesis"] = {"error": str(e)}
    
    try:
        test_results["quality_evaluation"] = await test_enhanced_quality_evaluation()
        logger.info("✓ Quality Evaluation Test Completed")
    except Exception as e:
        logger.error(f"✗ Quality Evaluation Test Failed: {e}")
        test_results["quality_evaluation"] = {"error": str(e)}
    
    try:
        test_results["weight_adjustment"] = await test_dynamic_weight_adjustment()
        logger.info("✓ Dynamic Weight Adjustment Test Completed")
    except Exception as e:
        logger.error(f"✗ Dynamic Weight Adjustment Test Failed: {e}")
        test_results["weight_adjustment"] = {"error": str(e)}
    
    try:
        test_results["performance_monitoring"] = await test_performance_monitoring()
        logger.info("✓ Performance Monitoring Test Completed")
    except Exception as e:
        logger.error(f"✗ Performance Monitoring Test Failed: {e}")
        test_results["performance_monitoring"] = {"error": str(e)}
    
    try:
        test_results["visualization"] = await test_visualization()
        logger.info("✓ Visualization Test Completed")
    except Exception as e:
        logger.error(f"✗ Visualization Test Failed: {e}")
        test_results["visualization"] = {"error": str(e)}
    
    # Generate summary report
    logger.info("=" * 70)
    logger.info("INTEGRATION TEST SUMMARY")
    logger.info("=" * 70)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        if "error" not in result and result.get("success", True):
            logger.info(f"✓ {test_name}: PASSED")
            passed_tests += 1
        else:
            logger.info(f"✗ {test_name}: FAILED")
    
    success_rate = (passed_tests / total_tests) * 100
    
    logger.info(f"\nTest Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        logger.info("🎉 V0.3.6 Integration Test: SUCCESS")
    else:
        logger.info("⚠️  V0.3.6 Integration Test: NEEDS ATTENTION")
    
    # Save test results
    test_report = {
        "test_version": "V0.3.6",
        "timestamp": datetime.now().isoformat(),
        "success_rate": success_rate,
        "passed_tests": passed_tests,
        "total_tests": total_tests,
        "test_results": test_results
    }
    
    # Save to file
    with open("v0_3_6_integration_test_report.json", "w", encoding="utf-8") as f:
        json.dump(test_report, f, ensure_ascii=False, indent=2)
    
    logger.info("Test report saved to: v0_3_6_integration_test_report.json")
    
    return test_report

if __name__ == "__main__":
    # Run integration test
    asyncio.run(run_integration_test())