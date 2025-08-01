#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流选择准确性测试

测试现有PersonalAssistant的工作流选择机制，验证意图识别准确率和工作流选择正确率
"""

import asyncio
import sys
from typing import List, Dict, Any
from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService, WorkflowType

class WorkflowSelectionTester:
    """工作流选择测试器"""
    
    def __init__(self):
        self.assistant = PersonalAssistantService()
        self.test_cases = [
            # 批判性审查场景
            {
                "input": "请分析这个技术方案的可行性和风险",
                "expected": WorkflowType.CRITICAL_REVIEW,
                "scenario": "技术评估"
            },
            {
                "input": "帮我审查这份商业计划书的逻辑漏洞",
                "expected": WorkflowType.CRITICAL_REVIEW,
                "scenario": "文档审查"
            },
            {
                "input": "检查这个研究结论是否有问题",
                "expected": WorkflowType.CRITICAL_REVIEW,
                "scenario": "研究验证"
            },
            
            # 多视角综合场景
            {
                "input": "大家来讨论一下AI对教育的影响",
                "expected": WorkflowType.MULTI_PERSPECTIVE,
                "scenario": "多角度讨论"
            },
            {
                "input": "从不同角度分析气候变化的解决方案",
                "expected": WorkflowType.MULTI_PERSPECTIVE,
                "scenario": "综合分析"
            },
            {
                "input": "我想听听各种观点关于远程工作的利弊",
                "expected": WorkflowType.MULTI_PERSPECTIVE,
                "scenario": "观点收集"
            },
            
            # 边界情况
            {
                "input": "你好，我想了解一下这个系统",
                "expected": None,  # 可以是任意工作流
                "scenario": "一般询问"
            },
            {
                "input": "帮我写一份报告",
                "expected": None,  # 可以是任意工作流
                "scenario": "任务请求"
            }
        ]
    
    async def test_intent_analysis_accuracy(self) -> Dict[str, Any]:
        """测试意图分析准确性"""
        print("🧪 测试意图分析准确性...")
        
        results = []
        correct_predictions = 0
        total_predictions = 0
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n测试用例 {i}: {test_case['scenario']}")
            print(f"输入: {test_case['input']}")
            
            try:
                # 执行意图分析
                intent_result = await self.assistant.analyze_intent(
                    test_case["input"],
                    context={"user_id": "test_user", "message_history": []}
                )
                
                predicted_workflow = intent_result.workflowType
                expected_workflow = test_case["expected"]
                
                print(f"预测工作流: {predicted_workflow.value}")
                print(f"置信度: {intent_result.confidence:.2f}")
                print(f"推理: {intent_result.reasoning}")
                
                # 评估准确性
                is_correct = (expected_workflow is None or 
                            predicted_workflow == expected_workflow)
                
                if expected_workflow is not None:
                    total_predictions += 1
                    if is_correct:
                        correct_predictions += 1
                
                result = {
                    "test_case": i,
                    "scenario": test_case["scenario"],
                    "input": test_case["input"],
                    "expected": expected_workflow.value if expected_workflow else "任意",
                    "predicted": predicted_workflow.value,
                    "confidence": intent_result.confidence,
                    "reasoning": intent_result.reasoning,
                    "correct": is_correct
                }
                
                results.append(result)
                print(f"结果: {'✅ 正确' if is_correct else '❌ 错误'}")
                
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                results.append({
                    "test_case": i,
                    "scenario": test_case["scenario"],
                    "error": str(e),
                    "correct": False
                })
        
        # 计算准确率
        accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
        
        summary = {
            "total_tests": len(self.test_cases),
            "total_predictions": total_predictions,
            "correct_predictions": correct_predictions,
            "accuracy": accuracy,
            "results": results
        }
        
        print(f"\n📊 测试总结:")
        print(f"总测试用例: {len(self.test_cases)}")
        print(f"有效预测: {total_predictions}")
        print(f"正确预测: {correct_predictions}")
        print(f"准确率: {accuracy:.1f}%")
        
        return summary
    
    async def test_workflow_selection_performance(self) -> Dict[str, Any]:
        """测试工作流选择性能"""
        print("\n⚡ 测试工作流选择性能...")
        
        import time
        
        performance_results = []
        
        for test_case in self.test_cases[:3]:  # 测试前3个用例
            start_time = time.time()
            
            try:
                intent_result = await self.assistant.analyze_intent(
                    test_case["input"],
                    context={"user_id": "test_user", "message_history": []}
                )
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # 转换为毫秒
                
                performance_results.append({
                    "scenario": test_case["scenario"],
                    "response_time_ms": response_time,
                    "confidence": intent_result.confidence
                })
                
                print(f"{test_case['scenario']}: {response_time:.1f}ms")
                
            except Exception as e:
                print(f"❌ 性能测试失败: {e}")
        
        avg_response_time = sum(r["response_time_ms"] for r in performance_results) / len(performance_results)
        
        print(f"\n平均响应时间: {avg_response_time:.1f}ms")
        
        return {
            "average_response_time_ms": avg_response_time,
            "results": performance_results
        }
    
    async def test_scenario_adaptation(self) -> Dict[str, Any]:
        """测试场景适配逻辑"""
        print("\n🎯 测试场景适配逻辑...")
        
        # 定义三大场景的测试用例
        scenario_tests = {
            "学术研究": [
                "分析人工智能在医疗领域的应用前景",
                "研究区块链技术的发展趋势",
                "探讨量子计算对密码学的影响"
            ],
            "专家咨询": [
                "我的创业公司应该选择什么技术栈？",
                "如何制定有效的市场营销策略？",
                "投资股市需要注意哪些风险？"
            ],
            "轻松讨论": [
                "大家觉得最近的电影怎么样？",
                "聊聊你们的旅行经历吧",
                "推荐一些好听的音乐"
            ]
        }
        
        scenario_results = {}
        
        for scenario_name, test_inputs in scenario_tests.items():
            print(f"\n测试场景: {scenario_name}")
            scenario_results[scenario_name] = []
            
            for test_input in test_inputs:
                try:
                    intent_result = await self.assistant.analyze_intent(
                        test_input,
                        context={"user_id": "test_user", "message_history": []}
                    )
                    
                    result = {
                        "input": test_input,
                        "workflow": intent_result.workflowType.value,
                        "confidence": intent_result.confidence,
                        "reasoning": intent_result.reasoning
                    }
                    
                    scenario_results[scenario_name].append(result)
                    print(f"  输入: {test_input}")
                    print(f"  工作流: {intent_result.workflowType.value}")
                    print(f"  置信度: {intent_result.confidence:.2f}")
                    
                except Exception as e:
                    print(f"  ❌ 测试失败: {e}")
        
        return scenario_results

async def main():
    """主测试函数"""
    print("🚀 开始工作流选择机制测试...")
    
    tester = WorkflowSelectionTester()
    
    # 1. 测试意图分析准确性
    accuracy_results = await tester.test_intent_analysis_accuracy()
    
    # 2. 测试性能
    performance_results = await tester.test_workflow_selection_performance()
    
    # 3. 测试场景适配
    scenario_results = await tester.test_scenario_adaptation()
    
    # 生成测试报告
    print("\n" + "="*50)
    print("📋 V0.2.1 工作流选择机制测试报告")
    print("="*50)
    
    print(f"\n✅ 意图识别准确率: {accuracy_results['accuracy']:.1f}%")
    print(f"✅ 平均响应时间: {performance_results['average_response_time_ms']:.1f}ms")
    print(f"✅ 支持工作流类型: {len([wf for wf in WorkflowType])}")
    
    # 评估是否达到V0.2.1任务要求
    accuracy_target = 90.0  # 目标准确率≥90%
    performance_target = 5000.0  # 目标响应时间<5秒
    
    accuracy_met = accuracy_results['accuracy'] >= accuracy_target
    performance_met = performance_results['average_response_time_ms'] < performance_target
    
    print(f"\n🎯 V0.2.1任务目标达成情况:")
    print(f"意图识别准确率≥90%: {'✅ 达成' if accuracy_met else '❌ 未达成'}")
    print(f"响应时间<5秒: {'✅ 达成' if performance_met else '❌ 未达成'}")
    
    if accuracy_met and performance_met:
        print("\n🎉 V0.2.1任务验证通过！现有工作流选择机制满足要求。")
        return True
    else:
        print("\n⚠️ 需要优化现有工作流选择机制。")
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
        sys.exit(1)