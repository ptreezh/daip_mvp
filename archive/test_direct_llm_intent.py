#!/usr/bin/env python3
"""直接测试LLM意图分析功能
绕过后端服务，直接调用LLM进行意图分析
"""

import asyncio
import json
import re
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.kernel.llm_interface import LLMConfig, LLMFactory


class DirectLLMIntentAnalyzer:
    """直接LLM意图分析器"""
    
    def __init__(self):
        """初始化LLM接口"""
        self.llm_config = LLMConfig(
            provider="ollama",
            model="qwen3:8b",  # 使用可用的模型
            base_url="http://localhost:11434",
            temperature=0.1,
            max_tokens=200
        )
        self.llm_interface = LLMFactory.create(self.llm_config)
    
    async def analyze_intent(self, user_input: str) -> dict:
        """使用LLM分析用户意图"""
        prompt = f"""分析用户输入，选择工作流类型。

用户输入："{user_input}"

工作流选择：
- critical_review：审查、评估、检查、验证、分析风险
- multi_perspective：讨论、观点、角度、多方面分析

场景分类：
- academic_research：研究、探讨、理论
- expert_consultation：建议、指导、咨询
- casual_discussion：聊天、分享、交流

直接返回JSON：
{{"workflow_type": "critical_review", "confidence": 0.9, "reasoning": "包含审查关键词", "scenario": "expert_consultation"}}"""

        try:
            # 调用LLM
            print(f"🤖 调用LLM分析: {user_input}")
            messages = [{"role": "user", "content": prompt}]
            response = await self.llm_interface.generate(messages=messages)
            llm_response = response.get("content", "")
            
            print(f"📝 LLM原始响应: {llm_response}")
            
            # 清理LLM响应，去掉常见的输出格式
            cleaned_response = llm_response
            # 去掉<think>标签及其内容
            cleaned_response = re.sub(r'<think>.*?</think>', '', cleaned_response, flags=re.DOTALL)
            # 去掉其他常见标签
            cleaned_response = re.sub(r'</?[^>]+>', '', cleaned_response)
            # 去掉多余的空白
            cleaned_response = cleaned_response.strip()
            
            print(f"📝 清理后响应: {cleaned_response}")
            
            # 解析JSON响应
            json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                # 验证和规范化结果
                workflow_type = result.get("workflow_type", "critical_review")
                if workflow_type not in ["critical_review", "multi_perspective"]:
                    workflow_type = "critical_review"
                
                confidence = float(result.get("confidence", 0.7))
                confidence = max(0.0, min(1.0, confidence))
                
                reasoning = result.get("reasoning", "基于LLM分析的结果")
                scenario = result.get("scenario", "unknown")
                
                return {
                    "workflow_type": workflow_type,
                    "confidence": confidence,
                    "reasoning": f"LLM分析: {reasoning}",
                    "scenario": scenario,
                    "raw_response": llm_response
                }
            else:
                raise ValueError(f"无法解析LLM响应中的JSON: {llm_response}")
                
        except Exception as e:
            print(f"❌ LLM分析失败: {e}")
            # 降级到关键词分析
            return self._fallback_analysis(user_input)
    
    def _fallback_analysis(self, user_input: str) -> dict:
        """降级关键词分析"""
        user_input_lower = user_input.lower()
        
        critical_keywords = ["分析", "审查", "评估", "检查", "验证", "风险", "问题", "漏洞"]
        multi_keywords = ["讨论", "观点", "角度", "看法", "聊聊", "谈谈", "交流"]
        
        critical_score = sum(1 for kw in critical_keywords if kw in user_input_lower)
        multi_score = sum(1 for kw in multi_keywords if kw in user_input_lower)
        
        if critical_score > multi_score and critical_score > 0:
            return {
                "workflow_type": "critical_review",
                "confidence": min(0.8, 0.6 + critical_score * 0.1),
                "reasoning": f"降级分析: 检测到{critical_score}个批判性关键词",
                "scenario": "expert_consultation"
            }
        elif multi_score > 0:
            return {
                "workflow_type": "multi_perspective", 
                "confidence": min(0.8, 0.6 + multi_score * 0.1),
                "reasoning": f"降级分析: 检测到{multi_score}个多视角关键词",
                "scenario": "casual_discussion"
            }
        else:
            return {
                "workflow_type": "critical_review",
                "confidence": 0.5,
                "reasoning": "降级分析: 默认选择",
                "scenario": "unknown"
            }

async def test_direct_llm_intent():
    """测试直接LLM意图分析"""
    print("🚀 开始直接LLM意图分析测试...")
    
    analyzer = DirectLLMIntentAnalyzer()
    
    test_cases = [
        {
            "input": "请分析这个技术方案的可行性和潜在风险",
            "expected_workflow": "critical_review",
            "expected_scenario": "expert_consultation"
        },
        {
            "input": "大家来讨论一下人工智能的发展前景",
            "expected_workflow": "multi_perspective", 
            "expected_scenario": "casual_discussion"
        },
        {
            "input": "研究区块链技术对金融行业的影响因素",
            "expected_workflow": "multi_perspective",
            "expected_scenario": "academic_research"
        },
        {
            "input": "我的创业公司应该选择什么技术栈？请给出建议",
            "expected_workflow": "critical_review",
            "expected_scenario": "expert_consultation"
        },
        {
            "input": "从不同角度看待远程工作的利弊",
            "expected_workflow": "multi_perspective",
            "expected_scenario": "casual_discussion"
        }
    ]
    
    results = []
    correct_workflow = 0
    correct_scenario = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试用例 {i}: {test_case['input']}")
        print(f"期望工作流: {test_case['expected_workflow']}")
        print(f"期望场景: {test_case['expected_scenario']}")
        
        try:
            result = await analyzer.analyze_intent(test_case["input"])
            
            workflow_correct = result["workflow_type"] == test_case["expected_workflow"]
            scenario_correct = result["scenario"] == test_case["expected_scenario"]
            
            if workflow_correct:
                correct_workflow += 1
            if scenario_correct:
                correct_scenario += 1
            
            print("\n📊 分析结果:")
            print(f"预测工作流: {result['workflow_type']} {'✅' if workflow_correct else '❌'}")
            print(f"预测场景: {result['scenario']} {'✅' if scenario_correct else '❌'}")
            print(f"置信度: {result['confidence']:.2f}")
            print(f"推理: {result['reasoning']}")
            
            results.append({
                "test_case": i,
                "input": test_case["input"],
                "expected_workflow": test_case["expected_workflow"],
                "predicted_workflow": result["workflow_type"],
                "expected_scenario": test_case["expected_scenario"],
                "predicted_scenario": result["scenario"],
                "workflow_correct": workflow_correct,
                "scenario_correct": scenario_correct,
                "confidence": result["confidence"],
                "reasoning": result["reasoning"]
            })
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            results.append({
                "test_case": i,
                "error": str(e),
                "workflow_correct": False,
                "scenario_correct": False
            })
    
    # 计算准确率
    total_tests = len(test_cases)
    workflow_accuracy = (correct_workflow / total_tests * 100) if total_tests > 0 else 0
    scenario_accuracy = (correct_scenario / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{'='*60}")
    print("📋 直接LLM意图分析测试报告")
    print(f"{'='*60}")
    print(f"总测试用例: {total_tests}")
    print(f"工作流选择准确率: {workflow_accuracy:.1f}% ({correct_workflow}/{total_tests})")
    print(f"场景识别准确率: {scenario_accuracy:.1f}% ({correct_scenario}/{total_tests})")
    
    # 评估是否达到V0.2.1要求
    workflow_target = 95.0
    scenario_target = 90.0
    
    workflow_met = workflow_accuracy >= workflow_target
    scenario_met = scenario_accuracy >= scenario_target
    
    print("\n🎯 V0.2.1任务目标达成情况:")
    print(f"工作流选择准确率≥95%: {'✅ 达成' if workflow_met else '❌ 未达成'}")
    print(f"场景识别准确率≥90%: {'✅ 达成' if scenario_met else '❌ 未达成'}")
    
    if workflow_met and scenario_met:
        print("\n🎉 V0.2.1任务验证通过！LLM意图分析满足要求。")
        return True
    else:
        print("\n⚠️ 需要进一步优化LLM意图分析。")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_direct_llm_intent())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)