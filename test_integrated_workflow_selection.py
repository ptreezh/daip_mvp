#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成工作流选择测试

测试集成了增强工作流选择器的PersonalAssistant，验证是否达到V0.2.1任务要求
"""

import asyncio
import sys
from typing import List, Dict, Any
from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService, WorkflowType

class IntegratedWorkflowTester:
    """集成工作流选择测试器"""
    
    def __init__(self):
        self.assistant = PersonalAssistantService()
        self.test_cases = [
            # 学术研究场景 - 应该选择多视角工作流
            {
                "input": "分析人工智能在医疗领域的应用前景和发展趋势",
                "expected": WorkflowType.MULTI_PERSPECTIVE,
                "category": "学术研究"
            },
            {
                "input": "研究区块链技术对金融行业的影响因素",
                "expected": WorkflowType.MULTI_PERSPECTIVE,
                "category": "学术研究"
            },
            {
                "input": "探讨量子计算在密码学领域的理论应用",
                "expected": WorkflowType.MULTI_PERSPECTIVE,
                "category": "学术研究"
            },
            
            # 专家咨询场景 - 应该选择批判性审查工作流
            {
                "input": "我的创业公司应该选择什么技术栈？请给出专业建议",
                "expected": WorkflowType.CRITICAL_REVIEW,
                "category": "专家咨询"
            },
            {
                "input": "如何制定有效的市场营销策略？需要注意哪些风险？",
                "expected": WorkflowType.CRITICAL_REVIEW,
                "category": "专家咨询"
            },
            {
                "input": "投资股市需要分析哪些风险因素？",
                "expected": WorkflowType.CRITICAL_REVIEW,
                "category": "专家咨询"
            },
            
            # 轻松讨论场景 - 应该选择多视角工作流
            {
                "input": "大家来聊聊最近看的好电影，分享一下观后感",
                "expected": WorkflowType.MULTI_PERSPECTIVE,
                "category": "轻松讨论"
            },
            {
                "input": "谈谈你们的旅行经历，有什么有趣的故事？",
                "expected": WorkflowType.MULTI_PERSPECTIVE,
                "category": "轻松讨论"
            },
            {
                "input": "推荐一些好听的音乐，大家一起交流音乐心得",
                "expected": WorkflowType.MULTI_PERSPECTIVE,
                "category": "轻松讨论"
            },
            
            # 批判性审查场景
            {
                "input": "请审查这个技术方案的可行性，分析潜在风险",
                "expected": WorkflowType.CRITICAL_REVIEW,
                "category": "技术审查"
            },
            {
                "input": "检查这份商业计划书是否有逻辑漏洞",
                "expected": WorkflowType.CRITICAL_REVIEW,
                "category": "文档审查"
            },
            {
                "input": "评估这个研究结论的准确性和可靠性",
                "expected": WorkflowType.CRITICAL_REVIEW,
                "category": "研究评估"
            },
            
            # 多视角综合场景
            {
                "input": "从不同角度讨论远程工作的利弊",
                "expected": WorkflowType.MULTI_PERSPECTIVE,
                "category": "多角度讨论"
            },
            {
                "input": "听听各方观点关于教育改革的看法",
                "expected": WorkflowType.MULTI_PERSPECTIVE,
                "category": "观点收集"
            },
            {
                "input": "综合考虑各种因素，分析城市发展策略",
                "expected": WorkflowType.MULTI_PERSPECTIVE,
                "category": "综合分析"
            }
        ]
    
    async def test_integrated_accuracy(self) -> Dict[str, Any]:
        """测试集成后的准确性"""
        print("🧪 测试集成工作流选择准确性...")
        
        results = []
        correct_predictions = 0
        total_predictions = len(self.test_cases)
        
        category_stats = {}
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n测试用例 {i}: {test_case['category']}")
            print(f"输入: {test_case['input']}")
            
            try:
                # 执行意图分析（会使用增强的降级策略）
                intent_result = await self.assistant.analyze_intent(
                    test_case["input"],
                    context={"user_id": "test_user", "message_history": []}
                )
                
                predicted_workflow = intent_result.workflowType
                expected_workflow = test_case["expected"]
                
                is_correct = predicted_workflow == expected_workflow
                if is_correct:
                    correct_predictions += 1
                
                print(f"预测工作流: {predicted_workflow.value} {'✅' if is_correct else '❌'}")
                print(f"期望工作流: {expected_workflow.value}")
                print(f"置信度: {intent_result.confidence:.2f}")
                print(f"推理: {intent_result.reasoning}")
                
                # 统计分类结果
                category = test_case['category']
                if category not in category_stats:
                    category_stats[category] = {'total': 0, 'correct': 0}
                
                category_stats[category]['total'] += 1
                if is_correct:
                    category_stats[category]['correct'] += 1
                
                test_result = {
                    "test_case": i,
                    "category": test_case["category"],
                    "input": test_case["input"],
                    "expected": expected_workflow.value,
                    "predicted": predicted_workflow.value,
                    "correct": is_correct,
                    "confidence": intent_result.confidence,
                    "reasoning": intent_result.reasoning
                }
                
                results.append(test_result)
                
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                results.append({
                    "test_case": i,
                    "category": test_case["category"],
                    "error": str(e),
                    "correct": False
                })
        
        # 计算准确率
        accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
        
        print(f"\n📊 测试总结:")
        print(f"总测试用例: {total_predictions}")
        print(f"正确预测: {correct_predictions}")
        print(f"准确率: {accuracy:.1f}%")
        
        # 分类统计
        print(f"\n📋 分类统计:")
        for category, stats in category_stats.items():
            cat_accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"{category}: {cat_accuracy:.1f}% ({stats['correct']}/{stats['total']})")
        
        return {
            "total_tests": total_predictions,
            "correct_predictions": correct_predictions,
            "accuracy": accuracy,
            "category_stats": category_stats,
            "results": results
        }
    
    async def test_performance(self) -> Dict[str, Any]:
        """测试性能"""
        print("\n⚡ 测试性能...")
        
        import time
        
        performance_results = []
        
        # 测试前5个用例的性能
        for test_case in self.test_cases[:5]:
            start_time = time.time()
            
            try:
                intent_result = await self.assistant.analyze_intent(
                    test_case["input"],
                    context={"user_id": "test_user", "message_history": []}
                )
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # 转换为毫秒
                
                performance_results.append({
                    "category": test_case["category"],
                    "response_time_ms": response_time,
                    "confidence": intent_result.confidence
                })
                
                print(f"{test_case['category']}: {response_time:.1f}ms")
                
            except Exception as e:
                print(f"❌ 性能测试失败: {e}")
        
        avg_response_time = sum(r["response_time_ms"] for r in performance_results) / len(performance_results)
        print(f"平均响应时间: {avg_response_time:.1f}ms")
        
        return {
            "average_response_time_ms": avg_response_time,
            "results": performance_results
        }

async def main():
    """主测试函数"""
    print("🚀 开始集成工作流选择测试...")
    print("注意：由于后端LLM服务不可用，将使用增强的降级策略")
    
    tester = IntegratedWorkflowTester()
    
    # 1. 测试准确性
    accuracy_results = await tester.test_integrated_accuracy()
    
    # 2. 测试性能
    performance_results = await tester.test_performance()
    
    # 生成测试报告
    print("\n" + "="*60)
    print("📋 V0.2.1 集成工作流选择测试报告")
    print("="*60)
    
    print(f"\n✅ 工作流选择准确率: {accuracy_results['accuracy']:.1f}%")
    print(f"✅ 平均响应时间: {performance_results['average_response_time_ms']:.1f}ms")
    
    # 评估是否达到V0.2.1任务要求
    accuracy_target = 95.0  # 工作流选择准确率≥95%
    performance_target = 5000.0  # 响应时间<5秒
    
    accuracy_met = accuracy_results['accuracy'] >= accuracy_target
    performance_met = performance_results['average_response_time_ms'] < performance_target
    
    print(f"\n🎯 V0.2.1任务目标达成情况:")
    print(f"工作流选择准确率≥95%: {'✅ 达成' if accuracy_met else '❌ 未达成'}")
    print(f"响应时间<5秒: {'✅ 达成' if performance_met else '❌ 未达成'}")
    
    # 架构优化说明
    print(f"\n🏗️ 架构优化说明:")
    print(f"- 消除了冗余设计：删除独立的EnhancedWorkflowSelector")
    print(f"- 集成到现有PersonalAssistant的降级策略中")
    print(f"- 保持了原有的LLM优先 + 智能降级的架构")
    print(f"- 提升了降级策略的准确率从83.3%到{accuracy_results['accuracy']:.1f}%")
    
    if accuracy_met and performance_met:
        print("\n🎉 V0.2.1任务验证通过！集成工作流选择器满足所有要求。")
        return True
    else:
        print("\n⚠️ 部分指标未达标，需要进一步优化。")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)