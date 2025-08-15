#!/usr/bin/env python3
"""增强工作流选择器测试

测试新的增强工作流选择器，验证是否达到V0.2.1任务要求：
- 意图识别准确率≥90%
- 工作流选择正确率≥95%
- 支持三大场景智能识别
"""

import sys
from typing import Any

from src.core_services.enhanced_workflow_selector import EnhancedWorkflowSelector, ScenarioType, WorkflowType


class EnhancedWorkflowTester:
    """增强工作流选择器测试器"""
    
    def __init__(self):
        self.selector = EnhancedWorkflowSelector()
        self.test_cases = [
            # 学术研究场景 - 应该选择多视角工作流
            {
                "input": "分析人工智能在医疗领域的应用前景和发展趋势",
                "expected_scenario": ScenarioType.ACADEMIC_RESEARCH,
                "expected_workflow": WorkflowType.MULTI_PERSPECTIVE,
                "category": "学术研究"
            },
            {
                "input": "研究区块链技术对金融行业的影响因素",
                "expected_scenario": ScenarioType.ACADEMIC_RESEARCH,
                "expected_workflow": WorkflowType.MULTI_PERSPECTIVE,
                "category": "学术研究"
            },
            {
                "input": "探讨量子计算在密码学领域的理论应用",
                "expected_scenario": ScenarioType.ACADEMIC_RESEARCH,
                "expected_workflow": WorkflowType.MULTI_PERSPECTIVE,
                "category": "学术研究"
            },
            
            # 专家咨询场景 - 应该选择批判性审查工作流
            {
                "input": "我的创业公司应该选择什么技术栈？请给出专业建议",
                "expected_scenario": ScenarioType.EXPERT_CONSULTATION,
                "expected_workflow": WorkflowType.CRITICAL_REVIEW,
                "category": "专家咨询"
            },
            {
                "input": "如何制定有效的市场营销策略？需要注意哪些风险？",
                "expected_scenario": ScenarioType.EXPERT_CONSULTATION,
                "expected_workflow": WorkflowType.CRITICAL_REVIEW,
                "category": "专家咨询"
            },
            {
                "input": "投资股市需要分析哪些风险因素？",
                "expected_scenario": ScenarioType.EXPERT_CONSULTATION,
                "expected_workflow": WorkflowType.CRITICAL_REVIEW,
                "category": "专家咨询"
            },
            
            # 轻松讨论场景 - 应该选择多视角工作流
            {
                "input": "大家来聊聊最近看的好电影，分享一下观后感",
                "expected_scenario": ScenarioType.CASUAL_DISCUSSION,
                "expected_workflow": WorkflowType.MULTI_PERSPECTIVE,
                "category": "轻松讨论"
            },
            {
                "input": "谈谈你们的旅行经历，有什么有趣的故事？",
                "expected_scenario": ScenarioType.CASUAL_DISCUSSION,
                "expected_workflow": WorkflowType.MULTI_PERSPECTIVE,
                "category": "轻松讨论"
            },
            {
                "input": "推荐一些好听的音乐，大家一起交流音乐心得",
                "expected_scenario": ScenarioType.CASUAL_DISCUSSION,
                "expected_workflow": WorkflowType.MULTI_PERSPECTIVE,
                "category": "轻松讨论"
            },
            
            # 批判性审查场景 - 明确要求审查分析
            {
                "input": "请审查这个技术方案的可行性，分析潜在风险",
                "expected_scenario": ScenarioType.EXPERT_CONSULTATION,
                "expected_workflow": WorkflowType.CRITICAL_REVIEW,
                "category": "技术审查"
            },
            {
                "input": "检查这份商业计划书是否有逻辑漏洞",
                "expected_scenario": ScenarioType.EXPERT_CONSULTATION,
                "expected_workflow": WorkflowType.CRITICAL_REVIEW,
                "category": "文档审查"
            },
            {
                "input": "评估这个研究结论的准确性和可靠性",
                "expected_scenario": ScenarioType.ACADEMIC_RESEARCH,
                "expected_workflow": WorkflowType.CRITICAL_REVIEW,
                "category": "研究评估"
            },
            
            # 多视角综合场景 - 明确要求多角度讨论
            {
                "input": "从不同角度讨论远程工作的利弊",
                "expected_scenario": ScenarioType.CASUAL_DISCUSSION,
                "expected_workflow": WorkflowType.MULTI_PERSPECTIVE,
                "category": "多角度讨论"
            },
            {
                "input": "听听各方观点关于教育改革的看法",
                "expected_scenario": ScenarioType.ACADEMIC_RESEARCH,
                "expected_workflow": WorkflowType.MULTI_PERSPECTIVE,
                "category": "观点收集"
            },
            {
                "input": "综合考虑各种因素，分析城市发展策略",
                "expected_scenario": ScenarioType.ACADEMIC_RESEARCH,
                "expected_workflow": WorkflowType.MULTI_PERSPECTIVE,
                "category": "综合分析"
            }
        ]
    
    def test_accuracy(self) -> dict[str, Any]:
        """测试准确性"""
        print("🧪 测试增强工作流选择器准确性...")
        
        results = []
        scenario_correct = 0
        workflow_correct = 0
        total_tests = len(self.test_cases)
        
        category_stats = {}
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n测试用例 {i}: {test_case['category']}")
            print(f"输入: {test_case['input']}")
            
            try:
                # 执行增强选择
                result = self.selector.select_workflow(test_case["input"])
                
                predicted_scenario = result.scenario_type
                predicted_workflow = result.workflow_type
                expected_scenario = test_case["expected_scenario"]
                expected_workflow = test_case["expected_workflow"]
                
                scenario_match = predicted_scenario == expected_scenario
                workflow_match = predicted_workflow == expected_workflow
                
                if scenario_match:
                    scenario_correct += 1
                if workflow_match:
                    workflow_correct += 1
                
                print(f"预测场景: {predicted_scenario.value} {'✅' if scenario_match else '❌'}")
                print(f"预测工作流: {predicted_workflow.value} {'✅' if workflow_match else '❌'}")
                print(f"综合置信度: {result.confidence:.2f}")
                print(f"场景置信度: {result.scenario_confidence:.2f}")
                print(f"推理: {result.reasoning}")
                
                # 统计分类结果
                category = test_case['category']
                if category not in category_stats:
                    category_stats[category] = {'total': 0, 'scenario_correct': 0, 'workflow_correct': 0}
                
                category_stats[category]['total'] += 1
                if scenario_match:
                    category_stats[category]['scenario_correct'] += 1
                if workflow_match:
                    category_stats[category]['workflow_correct'] += 1
                
                test_result = {
                    "test_case": i,
                    "category": test_case["category"],
                    "input": test_case["input"],
                    "expected_scenario": expected_scenario.value,
                    "predicted_scenario": predicted_scenario.value,
                    "expected_workflow": expected_workflow.value,
                    "predicted_workflow": predicted_workflow.value,
                    "scenario_correct": scenario_match,
                    "workflow_correct": workflow_match,
                    "confidence": result.confidence,
                    "scenario_confidence": result.scenario_confidence,
                    "reasoning": result.reasoning,
                    "keywords": result.keywords_matched
                }
                
                results.append(test_result)
                
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                results.append({
                    "test_case": i,
                    "category": test_case["category"],
                    "error": str(e),
                    "scenario_correct": False,
                    "workflow_correct": False
                })
        
        # 计算准确率
        scenario_accuracy = (scenario_correct / total_tests * 100) if total_tests > 0 else 0
        workflow_accuracy = (workflow_correct / total_tests * 100) if total_tests > 0 else 0
        
        print("\n📊 测试总结:")
        print(f"总测试用例: {total_tests}")
        print(f"场景识别准确率: {scenario_accuracy:.1f}% ({scenario_correct}/{total_tests})")
        print(f"工作流选择准确率: {workflow_accuracy:.1f}% ({workflow_correct}/{total_tests})")
        
        # 分类统计
        print("\n📋 分类统计:")
        for category, stats in category_stats.items():
            scenario_acc = (stats['scenario_correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            workflow_acc = (stats['workflow_correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"{category}: 场景{scenario_acc:.1f}%, 工作流{workflow_acc:.1f}% ({stats['total']}个用例)")
        
        return {
            "total_tests": total_tests,
            "scenario_correct": scenario_correct,
            "workflow_correct": workflow_correct,
            "scenario_accuracy": scenario_accuracy,
            "workflow_accuracy": workflow_accuracy,
            "category_stats": category_stats,
            "results": results
        }
    
    def test_performance(self) -> dict[str, Any]:
        """测试性能"""
        print("\n⚡ 测试性能...")
        
        import time
        
        performance_results = []
        
        # 测试前5个用例的性能
        for test_case in self.test_cases[:5]:
            start_time = time.time()
            
            try:
                result = self.selector.select_workflow(test_case["input"])
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # 转换为毫秒
                
                performance_results.append({
                    "category": test_case["category"],
                    "response_time_ms": response_time,
                    "confidence": result.confidence
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

def main():
    """主测试函数"""
    print("🚀 开始增强工作流选择器测试...")
    
    tester = EnhancedWorkflowTester()
    
    # 1. 测试准确性
    accuracy_results = tester.test_accuracy()
    
    # 2. 测试性能
    performance_results = tester.test_performance()
    
    # 生成测试报告
    print("\n" + "="*60)
    print("📋 V0.2.1 增强工作流选择器测试报告")
    print("="*60)
    
    print(f"\n✅ 场景识别准确率: {accuracy_results['scenario_accuracy']:.1f}%")
    print(f"✅ 工作流选择准确率: {accuracy_results['workflow_accuracy']:.1f}%")
    print(f"✅ 平均响应时间: {performance_results['average_response_time_ms']:.1f}ms")
    
    # 评估是否达到V0.2.1任务要求
    scenario_target = 90.0  # 场景识别准确率≥90%
    workflow_target = 95.0  # 工作流选择准确率≥95%
    performance_target = 5000.0  # 响应时间<5秒
    
    scenario_met = accuracy_results['scenario_accuracy'] >= scenario_target
    workflow_met = accuracy_results['workflow_accuracy'] >= workflow_target
    performance_met = performance_results['average_response_time_ms'] < performance_target
    
    print("\n🎯 V0.2.1任务目标达成情况:")
    print(f"场景识别准确率≥90%: {'✅ 达成' if scenario_met else '❌ 未达成'}")
    print(f"工作流选择准确率≥95%: {'✅ 达成' if workflow_met else '❌ 未达成'}")
    print(f"响应时间<5秒: {'✅ 达成' if performance_met else '❌ 未达成'}")
    
    # 三大场景支持验证
    scenarios_supported = len(set(result['predicted_scenario'] for result in accuracy_results['results']))
    print(f"支持场景类型: {scenarios_supported}/3 ({'✅ 完整支持' if scenarios_supported >= 3 else '❌ 支持不完整'})")
    
    if scenario_met and workflow_met and performance_met and scenarios_supported >= 3:
        print("\n🎉 V0.2.1任务验证通过！增强工作流选择器满足所有要求。")
        return True
    else:
        print("\n⚠️ 部分指标未达标，需要进一步优化。")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)