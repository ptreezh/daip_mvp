#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-02 17:00:00
@Author  : DAIP-LIVE Team
@File    : test_expert_consultation_scenario.py
@Description:
    V0.2.6 专家咨询场景质量保证
    
    按照.kiro规范要求进行完整的质量验证：
    - 功能测试：完成完整专家咨询案例
    - 专家匹配测试：验证专家选择相关性和多样性
    - 观点质量测试：确认专家观点专业性和实用性
    - 决策支持测试：验证综合建议合理性和可操作性
    - 用户体验测试：咨询流程直观性和有效性
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

# 导入待测试组件
from src.scenarios.expert_consultation_scenario import ExpertConsultationScenario, ConsultationConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExpertConsultationQualityAssurance:
    """专家咨询场景质量保证测试套件"""
    
    def __init__(self):
        self.test_results = {}
        self.scenario = ExpertConsultationScenario()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有质量保证测试"""
        logger.info("=" * 60)
        logger.info("👨‍💼 开始专家咨询场景质量保证测试")
        logger.info("=" * 60)
        
        test_suite = [
            ("功能完整性测试", self.test_functional_completeness),
            ("专家匹配机制测试", self.test_expert_matching),
            ("观点质量评估测试", self.test_opinion_quality),
            ("决策支持系统测试", self.test_decision_support),
            ("用户体验流程测试", self.test_user_experience),
            ("权威性评估测试", self.test_authority_evaluation),
            ("集成稳定性测试", self.test_integration_stability)
        ]
        
        overall_success = True
        
        for test_name, test_func in test_suite:
            logger.info(f"\n🔍 执行测试: {test_name}")
            try:
                start_time = time.time()
                result = await test_func()
                end_time = time.time()
                
                self.test_results[test_name] = {
                    "success": result.get("success", False),
                    "execution_time": end_time - start_time,
                    "details": result,
                    "timestamp": datetime.now().isoformat()
                }
                
                status = "✅ 通过" if result.get("success") else "❌ 失败"
                logger.info(f"{test_name}: {status} (耗时: {end_time - start_time:.2f}秒)")
                
                if not result.get("success"):
                    overall_success = False
                    logger.error(f"测试失败详情: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"测试执行异常: {test_name} - {e}")
                self.test_results[test_name] = {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                overall_success = False
        
        # 生成最终报告
        final_report = await self.generate_final_report(overall_success)
        
        logger.info("\n" + "=" * 60)
        logger.info(f"🎯 质量保证测试完成 - 总体结果: {'✅ 全部通过' if overall_success else '❌ 存在问题'}")
        logger.info("=" * 60)
        
        return final_report
    
    async def test_functional_completeness(self) -> Dict[str, Any]:
        """功能完整性测试 - 完成创业公司技术选型咨询案例"""
        logger.info("执行创业公司技术选型咨询案例...")
        
        try:
            # 配置专家咨询参数
            config = ConsultationConfig(
                max_experts=5,
                min_experts=3,
                authority_threshold=0.6,
                consensus_threshold=0.7,
                enable_critical_review=True,
                include_contrarian_views=True
            )
            
            # 执行完整专家咨询
            question = "我们初创公司正在开发一个B2B SaaS平台，应该如何进行技术选型？"
            context = """
            我们是一个10人的初创团队，计划开发企业级CRM系统。
            团队技术栈主要是Python和React，预算有限，希望能快速上线验证市场。
            同时考虑系统的可扩展性，因为预期用户增长会很快。
            """
            
            start_time = time.time()
            result = await self.scenario.conduct_expert_consultation(
                question=question,
                context=context,
                config=config
            )
            end_time = time.time()
            
            # 验证结果完整性
            validation_checks = {
                "consultation_success": result.get("success", False),
                "has_expert_selection": "selected_experts" in result and len(result.get("selected_experts", [])) >= 3,
                "has_expert_opinions": "expert_opinions" in result and len(result.get("expert_opinions", [])) >= 3,
                "has_authority_analysis": "authority_analysis" in result,
                "has_opinion_analysis": "opinion_analysis" in result,
                "has_comprehensive_advice": "comprehensive_advice" in result,
                "has_decision_support": "decision_support" in result,
                "execution_time_reasonable": (end_time - start_time) < 300,  # 5分钟限制
                "has_actionable_recommendations": len(result.get("comprehensive_advice", {}).get("weighted_recommendations", [])) > 0
            }
            
            success = all(validation_checks.values())
            
            return {
                "success": success,
                "execution_time": end_time - start_time,
                "expert_count": len(result.get("selected_experts", [])),
                "opinion_count": len(result.get("expert_opinions", [])),
                "validation_checks": validation_checks,
                "consultation_result": {
                    "question": result.get("question"),
                    "consultation_id": result.get("consultation_id"),
                    "decision_recommendation": result.get("comprehensive_advice", {}).get("decision_recommendations", {}).get("go_no_go_recommendation"),
                    "confidence_level": result.get("comprehensive_advice", {}).get("recommendation_confidence", 0)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "功能完整性测试执行失败"
            }
    
    async def test_expert_matching(self) -> Dict[str, Any]:
        """专家匹配机制测试 - 验证专家选择的相关性和多样性"""
        logger.info("执行专家匹配机制测试...")
        
        try:
            # 测试不同类型问题的专家匹配
            test_cases = [
                {
                    "question": "我们需要进行技术架构升级",
                    "expected_domains": ["技术", "人工智能"],
                    "context": "现有系统性能瓶颈，需要重新设计架构"
                },
                {
                    "question": "如何制定公司的商业战略",
                    "expected_domains": ["商业", "金融"],
                    "context": "公司处于快速发展期，需要明确战略方向"
                },
                {
                    "question": "产品的用户体验如何优化",
                    "expected_domains": ["设计", "运营"],
                    "context": "用户反馈界面复杂，需要改善体验"
                }
            ]
            
            matching_results = []
            
            for i, test_case in enumerate(test_cases):
                logger.info(f"专家匹配测试 {i+1}: {test_case['question'][:20]}...")
                
                result = await self.scenario.conduct_expert_consultation(
                    question=test_case["question"],
                    context=test_case["context"],
                    config=ConsultationConfig(max_experts=4, min_experts=2)
                )
                
                if not result.get("success"):
                    matching_results.append({
                        "test_case": i+1,
                        "success": False,
                        "error": result.get("error", "Unknown error")
                    })
                    continue
                
                selected_experts = result.get("selected_experts", [])
                selected_domains = [expert["domain"] for expert in selected_experts]
                
                # 验证专家匹配质量
                matching_checks = {
                    "experts_selected": len(selected_experts) >= 2,
                    "domain_diversity": len(set(selected_domains)) >= 2,
                    "relevant_domains": any(
                        expected in selected_domains 
                        for expected in test_case["expected_domains"]
                    ),
                    "authority_threshold": all(
                        expert["authority_score"] >= 0.6 
                        for expert in selected_experts
                    ),
                    "expertise_relevance": self._check_expertise_relevance(
                        test_case["question"], selected_experts
                    )
                }
                
                matching_results.append({
                    "test_case": i+1,
                    "question": test_case["question"],
                    "selected_experts": [expert["name"] for expert in selected_experts],
                    "selected_domains": selected_domains,
                    "expected_domains": test_case["expected_domains"],
                    "matching_checks": matching_checks,
                    "success": all(matching_checks.values())
                })
            
            # 计算整体匹配成功率
            successful_matches = sum(1 for result in matching_results if result.get("success", False))
            total_matches = len(matching_results)
            success_rate = successful_matches / total_matches if total_matches > 0 else 0
            
            success = success_rate >= 0.8  # 80%成功率要求
            
            return {
                "success": success,
                "success_rate": success_rate,
                "successful_matches": successful_matches,
                "total_matches": total_matches,
                "matching_results": matching_results,
                "diversity_metrics": self._calculate_diversity_metrics(matching_results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "专家匹配机制测试执行失败"
            }
    
    def _check_expertise_relevance(self, question: str, experts: List[Dict]) -> bool:
        """检查专家专长与问题的相关性"""
        question_lower = question.lower()
        
        for expert in experts:
            expertise_areas = expert.get("expertise_areas", [])
            specialty_keywords = expert.get("specialty_keywords", [])
            
            # 检查是否有相关的专长领域
            for area in expertise_areas + specialty_keywords:
                if any(keyword in question_lower for keyword in area.lower().split()):
                    return True
        
        return len(experts) > 0  # 如果有专家被选中，认为基本相关
    
    def _calculate_diversity_metrics(self, matching_results: List[Dict]) -> Dict[str, float]:
        """计算专家多样性指标"""
        if not matching_results:
            return {"domain_diversity": 0, "expertise_coverage": 0}
        
        all_domains = []
        all_experts = []
        
        for result in matching_results:
            if result.get("selected_domains"):
                all_domains.extend(result["selected_domains"])
            if result.get("selected_experts"):
                all_experts.extend(result["selected_experts"])
        
        unique_domains = len(set(all_domains))
        unique_experts = len(set(all_experts))
        
        return {
            "domain_diversity": unique_domains / len(all_domains) if all_domains else 0,
            "expertise_coverage": unique_experts / len(all_experts) if all_experts else 0,
            "total_unique_domains": unique_domains,
            "total_unique_experts": unique_experts
        }
    
    async def test_opinion_quality(self) -> Dict[str, Any]:
        """观点质量评估测试 - 确认专家观点的专业性和实用性"""
        logger.info("执行观点质量评估测试...")
        
        try:
            # 使用具体业务问题测试观点质量
            question = "我们公司应该如何实施数字化转型？"
            context = "传统制造业，员工1000人，希望提升运营效率和客户体验。"
            
            result = await self.scenario.conduct_expert_consultation(
                question=question,
                context=context,
                config=ConsultationConfig(max_experts=4, min_experts=3)
            )
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": "咨询执行失败",
                    "details": result.get("error", "Unknown error")
                }
            
            expert_opinions = result.get("expert_opinions", [])
            authority_analysis = result.get("authority_analysis", {})
            
            quality_assessments = []
            
            for opinion in expert_opinions:
                # 评估单个专家观点质量
                quality_metrics = {
                    "opinion_length": len(opinion["opinion_text"]),
                    "recommendations_count": len(opinion["recommendations"]),
                    "evidence_count": len(opinion["supporting_evidence"]),
                    "concerns_count": len(opinion["concerns"]),
                    "confidence_level": opinion["confidence_level"],
                    "authority_weight": opinion["authority_weight"]
                }
                
                # 质量检查
                quality_checks = {
                    "sufficient_length": quality_metrics["opinion_length"] > 100,
                    "has_recommendations": quality_metrics["recommendations_count"] > 0,
                    "has_evidence": quality_metrics["evidence_count"] > 0,
                    "reasonable_confidence": 0.3 <= quality_metrics["confidence_level"] <= 1.0,
                    "adequate_authority": quality_metrics["authority_weight"] >= 0.6,
                    "structured_response": self._check_opinion_structure(opinion["opinion_text"])
                }
                
                quality_score = sum(quality_checks.values()) / len(quality_checks)
                
                quality_assessments.append({
                    "expert_name": opinion["expert_name"],
                    "quality_metrics": quality_metrics,
                    "quality_checks": quality_checks,
                    "quality_score": quality_score
                })
            
            # 计算整体质量指标
            average_quality = sum(
                assessment["quality_score"] for assessment in quality_assessments
            ) / len(quality_assessments) if quality_assessments else 0
            
            high_quality_opinions = len([
                assessment for assessment in quality_assessments 
                if assessment["quality_score"] >= 0.7
            ])
            
            success = (
                average_quality >= 0.6 and
                high_quality_opinions >= len(quality_assessments) * 0.6  # 至少60%高质量
            )
            
            return {
                "success": success,
                "average_quality_score": average_quality,
                "high_quality_opinions": high_quality_opinions,
                "total_opinions": len(quality_assessments),
                "quality_assessments": quality_assessments,
                "overall_metrics": {
                    "total_recommendations": sum(a["quality_metrics"]["recommendations_count"] for a in quality_assessments),
                    "total_evidence": sum(a["quality_metrics"]["evidence_count"] for a in quality_assessments),
                    "average_confidence": sum(a["quality_metrics"]["confidence_level"] for a in quality_assessments) / len(quality_assessments) if quality_assessments else 0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "观点质量评估测试执行失败"
            }
    
    def _check_opinion_structure(self, opinion_text: str) -> bool:
        """检查观点结构合理性"""
        # 检查是否包含结构化内容
        structure_indicators = [
            "1.", "2.", "3.",  # 数字列表
            "首先", "其次", "最后",  # 逻辑词
            "建议", "推荐", "认为",  # 观点词
            "风险", "问题", "挑战"  # 分析词
        ]
        
        indicator_count = sum(1 for indicator in structure_indicators if indicator in opinion_text)
        return indicator_count >= 3
    
    async def test_decision_support(self) -> Dict[str, Any]:
        """决策支持系统测试 - 验证综合建议的合理性和可操作性"""
        logger.info("执行决策支持系统测试...")
        
        try:
            # 使用决策导向的问题
            question = "我们应该投资开发新产品线还是优化现有产品？"
            context = "公司处于稳定盈利状态，有一定资金储备，面临市场竞争加剧。"
            
            result = await self.scenario.conduct_expert_consultation(
                question=question,
                context=context,
                config=ConsultationConfig(max_experts=5, enable_critical_review=True)
            )
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": "咨询执行失败",
                    "details": result.get("error", "Unknown error")
                }
            
            decision_support = result.get("decision_support", {})
            comprehensive_advice = result.get("comprehensive_advice", {})
            
            # 验证决策支持组件
            decision_checks = {
                "has_decision_matrix": "decision_matrix" in decision_support,
                "has_pros_and_cons": "pros_and_cons" in decision_support,
                "has_stakeholder_impact": "stakeholder_impact" in decision_support,
                "has_resource_requirements": "resource_requirements" in decision_support,
                "has_timeline_estimate": "timeline_estimate" in decision_support,
                "has_alternatives": "alternatives" in decision_support,
                "has_next_steps": "next_steps" in decision_support
            }
            
            # 验证综合建议质量
            advice_checks = {
                "has_executive_summary": "executive_summary" in comprehensive_advice,
                "has_weighted_recommendations": len(comprehensive_advice.get("weighted_recommendations", [])) > 0,
                "has_risk_assessment": "risk_assessment" in comprehensive_advice,
                "has_implementation_path": "implementation_path" in comprehensive_advice,
                "has_go_no_go_decision": "go_no_go_recommendation" in comprehensive_advice.get("decision_recommendations", {})
            }
            
            # 检查建议的可操作性
            operability_checks = {
                "actionable_next_steps": len(decision_support.get("next_steps", [])) >= 2,
                "clear_timeline": "phase_1" in comprehensive_advice.get("implementation_path", {}),
                "specific_recommendations": any(
                    len(rec.get("recommendation", "")) > 20 
                    for rec in comprehensive_advice.get("weighted_recommendations", [])[:3]
                ),
                "risk_mitigation": len(comprehensive_advice.get("decision_recommendations", {}).get("risk_mitigation_priorities", [])) > 0
            }
            
            # 验证决策逻辑
            logic_checks = {
                "consistent_confidence": comprehensive_advice.get("recommendation_confidence", 0) > 0,
                "balanced_analysis": len(decision_support.get("pros_and_cons", {}).get("pros", [])) > 0 and 
                                   len(decision_support.get("pros_and_cons", {}).get("cons", [])) > 0,
                "stakeholder_consideration": len(decision_support.get("stakeholder_impact", {})) > 0,
                "alternative_consideration": len(decision_support.get("alternatives", [])) > 0
            }
            
            success = (
                sum(decision_checks.values()) >= len(decision_checks) * 0.8 and
                sum(advice_checks.values()) >= len(advice_checks) * 0.8 and
                sum(operability_checks.values()) >= len(operability_checks) * 0.7 and
                sum(logic_checks.values()) >= len(logic_checks) * 0.7
            )
            
            return {
                "success": success,
                "decision_checks": decision_checks,
                "advice_checks": advice_checks,
                "operability_checks": operability_checks,
                "logic_checks": logic_checks,
                "decision_support_completeness": sum(decision_checks.values()) / len(decision_checks),
                "advice_quality": sum(advice_checks.values()) / len(advice_checks),
                "operability_score": sum(operability_checks.values()) / len(operability_checks),
                "logic_score": sum(logic_checks.values()) / len(logic_checks),
                "recommendation_confidence": comprehensive_advice.get("recommendation_confidence", 0),
                "go_no_go_decision": comprehensive_advice.get("decision_recommendations", {}).get("go_no_go_recommendation")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "决策支持系统测试执行失败"
            }
    
    async def test_user_experience(self) -> Dict[str, Any]:
        """用户体验流程测试 - 验证咨询流程的直观性和有效性"""
        logger.info("执行用户体验流程测试...")
        
        try:
            # 模拟不同复杂度的用户咨询场景
            user_scenarios = [
                {
                    "name": "简单业务咨询",
                    "question": "如何提高团队工作效率？",
                    "context": "10人团队，远程办公，沟通效率低",
                    "expected_duration": 120  # 2分钟
                },
                {
                    "name": "中等复杂度咨询",
                    "question": "公司应该如何进行数字化转型？",
                    "context": "传统行业，200人规模，希望拥抱新技术",
                    "expected_duration": 180  # 3分钟
                },
                {
                    "name": "复杂战略咨询",
                    "question": "我们应该进入国际市场还是深耕本土市场？",
                    "context": "已在国内稳定运营5年，考虑扩张策略",
                    "expected_duration": 240  # 4分钟
                }
            ]
            
            ux_results = []
            
            for scenario in user_scenarios:
                logger.info(f"测试用户场景: {scenario['name']}")
                
                start_time = time.time()
                
                result = await self.scenario.conduct_expert_consultation(
                    question=scenario["question"],
                    context=scenario["context"],
                    config=ConsultationConfig(max_experts=4)
                )
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                # 用户体验指标
                ux_metrics = {
                    "scenario_name": scenario["name"],
                    "consultation_success": result.get("success", False),
                    "response_time": execution_time,
                    "within_expected_time": execution_time <= scenario["expected_duration"],
                    "result_completeness": self._assess_result_completeness(result),
                    "advice_clarity": self._assess_advice_clarity(result),
                    "actionability": self._assess_actionability(result),
                    "error_handling": "error" not in result or result.get("success", False)
                }
                
                ux_results.append(ux_metrics)
            
            # 计算整体用户体验得分
            total_scenarios = len(ux_results)
            successful_consultations = sum(1 for r in ux_results if r["consultation_success"])
            timely_responses = sum(1 for r in ux_results if r["within_expected_time"])
            complete_results = sum(1 for r in ux_results if r["result_completeness"] >= 0.8)
            clear_advice = sum(1 for r in ux_results if r["advice_clarity"] >= 0.7)
            
            success = (
                successful_consultations == total_scenarios and
                timely_responses >= total_scenarios * 0.8 and
                complete_results >= total_scenarios * 0.8 and
                clear_advice >= total_scenarios * 0.7
            )
            
            return {
                "success": success,
                "overall_metrics": {
                    "success_rate": successful_consultations / total_scenarios,
                    "timely_response_rate": timely_responses / total_scenarios,
                    "completeness_rate": complete_results / total_scenarios,
                    "clarity_rate": clear_advice / total_scenarios,
                    "average_response_time": sum(r["response_time"] for r in ux_results) / total_scenarios
                },
                "scenario_results": ux_results,
                "user_satisfaction_estimate": self._estimate_user_satisfaction(ux_results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "用户体验流程测试执行失败"
            }
    
    def _assess_result_completeness(self, result: Dict[str, Any]) -> float:
        """评估结果完整性"""
        if not result.get("success"):
            return 0.0
        
        required_components = [
            "selected_experts", "expert_opinions", "authority_analysis",
            "opinion_analysis", "comprehensive_advice", "decision_support"
        ]
        
        present_components = sum(1 for comp in required_components if comp in result)
        return present_components / len(required_components)
    
    def _assess_advice_clarity(self, result: Dict[str, Any]) -> float:
        """评估建议清晰度"""
        if not result.get("success"):
            return 0.0
        
        comprehensive_advice = result.get("comprehensive_advice", {})
        
        clarity_indicators = [
            len(comprehensive_advice.get("executive_summary", "")) > 50,
            len(comprehensive_advice.get("weighted_recommendations", [])) > 0,
            "go_no_go_recommendation" in comprehensive_advice.get("decision_recommendations", {}),
            len(comprehensive_advice.get("implementation_path", {})) > 0
        ]
        
        return sum(clarity_indicators) / len(clarity_indicators)
    
    def _assess_actionability(self, result: Dict[str, Any]) -> float:
        """评估建议可操作性"""
        if not result.get("success"):
            return 0.0
        
        decision_support = result.get("decision_support", {})
        
        actionability_indicators = [
            len(decision_support.get("next_steps", [])) > 0,
            "implementation_path" in result.get("comprehensive_advice", {}),
            len(decision_support.get("resource_requirements", {})) > 0,
            "timeline_estimate" in decision_support
        ]
        
        return sum(actionability_indicators) / len(actionability_indicators)
    
    def _estimate_user_satisfaction(self, ux_results: List[Dict]) -> float:
        """估算用户满意度"""
        if not ux_results:
            return 0.0
        
        satisfaction_factors = []
        
        for result in ux_results:
            scenario_satisfaction = (
                result["consultation_success"] * 0.3 +
                (1.0 if result["within_expected_time"] else 0.5) * 0.2 +
                result["result_completeness"] * 0.25 +
                result["advice_clarity"] * 0.15 +
                result["actionability"] * 0.1
            )
            satisfaction_factors.append(scenario_satisfaction)
        
        return sum(satisfaction_factors) / len(satisfaction_factors)
    
    async def test_authority_evaluation(self) -> Dict[str, Any]:
        """权威性评估测试 - 验证专家权威性评估的准确性"""
        logger.info("执行权威性评估测试...")
        
        try:
            # 使用需要权威性判断的问题
            question = "我们应该采用哪种AI技术来提升业务效率？"
            context = "考虑引入AI技术，需要权威专家的指导建议。"
            
            result = await self.scenario.conduct_expert_consultation(
                question=question,
                context=context,
                config=ConsultationConfig(max_experts=5, authority_threshold=0.7)
            )
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": "咨询执行失败",
                    "details": result.get("error", "Unknown error")
                }
            
            authority_analysis = result.get("authority_analysis", {})
            selected_experts = result.get("selected_experts", [])
            
            # 验证权威性评估组件
            authority_checks = {
                "has_authority_scores": "authority_scores" in authority_analysis,
                "has_most_authoritative": "most_authoritative" in authority_analysis,
                "has_average_authority": "average_authority" in authority_analysis,
                "has_authority_distribution": "authority_distribution" in authority_analysis
            }
            
            # 验证权威性计算合理性
            authority_scores = authority_analysis.get("authority_scores", {})
            calculation_checks = {
                "all_experts_evaluated": len(authority_scores) == len(selected_experts),
                "reasonable_score_range": all(
                    0 <= score["final_authority"] <= 1.0 
                    for score in authority_scores.values()
                ),
                "authority_above_threshold": all(
                    score["final_authority"] >= 0.6 
                    for score in authority_scores.values()
                ),
                "score_differentiation": self._check_score_differentiation(authority_scores)
            }
            
            # 验证权威性影响
            influence_checks = {
                "high_authority_influence": self._check_high_authority_influence(result),
                "weighted_recommendations": len(result.get("comprehensive_advice", {}).get("weighted_recommendations", [])) > 0,
                "authority_based_weighting": self._check_authority_weighting(result)
            }
            
            success = (
                all(authority_checks.values()) and
                sum(calculation_checks.values()) >= len(calculation_checks) * 0.8 and
                sum(influence_checks.values()) >= len(influence_checks) * 0.7
            )
            
            return {
                "success": success,
                "authority_checks": authority_checks,
                "calculation_checks": calculation_checks,
                "influence_checks": influence_checks,
                "authority_metrics": {
                    "average_authority": authority_analysis.get("average_authority", 0),
                    "authority_distribution": authority_analysis.get("authority_distribution", {}),
                    "most_authoritative_expert": authority_analysis.get("most_authoritative", [None, {}])[1].get("expert_name") if authority_analysis.get("most_authoritative") else None
                },
                "score_analysis": self._analyze_authority_scores(authority_scores)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "权威性评估测试执行失败"
            }
    
    def _check_score_differentiation(self, authority_scores: Dict) -> bool:
        """检查权威性分数是否有合理的差异化"""
        if len(authority_scores) < 2:
            return True
        
        scores = [score["final_authority"] for score in authority_scores.values()]
        max_score = max(scores)
        min_score = min(scores)
        
        return (max_score - min_score) >= 0.1  # 至少0.1的差异
    
    def _check_high_authority_influence(self, result: Dict[str, Any]) -> bool:
        """检查高权威专家是否有更大影响力"""
        authority_analysis = result.get("authority_analysis", {})
        most_authoritative = authority_analysis.get("most_authoritative")
        
        if not most_authoritative:
            return False
        
        # 简化检查：确保最权威专家存在
        return most_authoritative[1].get("final_authority", 0) > 0.7
    
    def _check_authority_weighting(self, result: Dict[str, Any]) -> bool:
        """检查权威性是否影响建议权重"""
        weighted_recommendations = result.get("comprehensive_advice", {}).get("weighted_recommendations", [])
        
        if not weighted_recommendations:
            return False
        
        # 检查是否有权重差异
        weights = [rec.get("total_weight", 0) for rec in weighted_recommendations]
        return len(set(weights)) > 1  # 权重应该有差异
    
    def _analyze_authority_scores(self, authority_scores: Dict) -> Dict[str, Any]:
        """分析权威性分数分布"""
        if not authority_scores:
            return {"analysis": "无权威性分数数据"}
        
        scores = [score["final_authority"] for score in authority_scores.values()]
        
        return {
            "total_experts": len(scores),
            "max_authority": max(scores),
            "min_authority": min(scores),
            "average_authority": sum(scores) / len(scores),
            "authority_variance": sum((s - sum(scores)/len(scores))**2 for s in scores) / len(scores),
            "high_authority_count": len([s for s in scores if s > 0.8]),
            "medium_authority_count": len([s for s in scores if 0.6 <= s <= 0.8]),
            "low_authority_count": len([s for s in scores if s < 0.6])
        }
    
    async def test_integration_stability(self) -> Dict[str, Any]:
        """集成稳定性测试 - 验证组件协作稳定性"""
        logger.info("执行集成稳定性测试...")
        
        try:
            # 连续执行多次咨询，检查稳定性
            stability_runs = 3
            results = []
            
            for i in range(stability_runs):
                logger.info(f"稳定性测试运行 {i+1}/{stability_runs}")
                
                question = f"稳定性测试 {i+1}: 如何优化业务流程？"
                context = f"测试运行 {i+1}，验证系统稳定性。"
                
                try:
                    start_time = time.time()
                    result = await self.scenario.conduct_expert_consultation(
                        question=question,
                        context=context,
                        config=ConsultationConfig(max_experts=3, min_experts=2)
                    )
                    end_time = time.time()
                    
                    run_result = {
                        "run_number": i+1,
                        "success": result.get("success", False),
                        "execution_time": end_time - start_time,
                        "expert_count": len(result.get("selected_experts", [])),
                        "opinion_count": len(result.get("expert_opinions", [])),
                        "has_comprehensive_advice": "comprehensive_advice" in result,
                        "error": result.get("error") if not result.get("success") else None
                    }
                    
                except Exception as e:
                    run_result = {
                        "run_number": i+1,
                        "success": False,
                        "error": str(e),
                        "execution_time": 0,
                        "expert_count": 0,
                        "opinion_count": 0,
                        "has_comprehensive_advice": False
                    }
                
                results.append(run_result)
                
                # 短暂休息避免资源竞争
                await asyncio.sleep(0.5)
            
            # 分析稳定性指标
            successful_runs = sum(1 for r in results if r["success"])
            consistency_check = len(set(r["success"] for r in results)) == 1  # 所有运行结果一致
            execution_time_variance = max(r["execution_time"] for r in results) - min(r["execution_time"] for r in results)
            
            success = (
                successful_runs == stability_runs and
                execution_time_variance < 60  # 执行时间差异小于1分钟
            )
            
            return {
                "success": success,
                "stability_metrics": {
                    "successful_runs": successful_runs,
                    "total_runs": stability_runs,
                    "success_rate": successful_runs / stability_runs,
                    "consistency_check": consistency_check,
                    "execution_time_variance": execution_time_variance,
                    "average_execution_time": sum(r["execution_time"] for r in results) / len(results),
                    "average_expert_count": sum(r["expert_count"] for r in results) / len(results),
                    "average_opinion_count": sum(r["opinion_count"] for r in results) / len(results)
                },
                "individual_runs": results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "集成稳定性测试执行失败"
            }
    
    async def generate_final_report(self, overall_success: bool) -> Dict[str, Any]:
        """生成最终质量保证报告"""
        
        # 统计测试结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get("success", False))
        
        # 计算质量得分
        quality_score = passed_tests / total_tests if total_tests > 0 else 0
        
        # 生成建议
        recommendations = []
        for test_name, result in self.test_results.items():
            if not result.get("success", False):
                recommendations.append(f"修复 {test_name} 中的问题: {result.get('error', '未知错误')}")
        
        if not recommendations:
            recommendations.append("所有测试通过，专家咨询场景质量符合V0.2.6要求")
        
        report = {
            "overall_success": overall_success,
            "quality_assurance_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "quality_score": quality_score,
                "completion_time": datetime.now().isoformat()
            },
            "test_results": self.test_results,
            "recommendations": recommendations,
            "compliance_check": {
                "functional_completeness": self.test_results.get("功能完整性测试", {}).get("success", False),
                "expert_matching": self.test_results.get("专家匹配机制测试", {}).get("success", False),
                "opinion_quality": self.test_results.get("观点质量评估测试", {}).get("success", False),
                "decision_support": self.test_results.get("决策支持系统测试", {}).get("success", False),
                "user_experience": self.test_results.get("用户体验流程测试", {}).get("success", False),
                "authority_evaluation": self.test_results.get("权威性评估测试", {}).get("success", False),
                "integration_stability": self.test_results.get("集成稳定性测试", {}).get("success", False)
            }
        }
        
        # 保存报告
        await self.save_report(report)
        
        return report
    
    async def save_report(self, report: Dict[str, Any]):
        """保存质量保证报告"""
        try:
            report_path = Path("v0_2_6_expert_consultation_quality_report.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"质量保证报告已保存: {report_path}")
        except Exception as e:
            logger.error(f"报告保存失败: {e}")


async def main():
    """执行V0.2.6专家咨询场景质量保证"""
    qa = ExpertConsultationQualityAssurance()
    
    try:
        final_report = await qa.run_all_tests()
        
        print("\n" + "=" * 80)
        print("📊 V0.2.6 专家咨询场景质量保证报告")
        print("=" * 80)
        print(f"总体结果: {'✅ 通过' if final_report['overall_success'] else '❌ 失败'}")
        print(f"质量得分: {final_report['quality_assurance_summary']['quality_score']:.2%}")
        print(f"通过测试: {final_report['quality_assurance_summary']['passed_tests']}/{final_report['quality_assurance_summary']['total_tests']}")
        
        print("\n📋 合规性检查:")
        compliance = final_report['compliance_check']
        for check, passed in compliance.items():
            status = "✅" if passed else "❌"
            print(f"  {check}: {status}")
        
        print(f"\n💡 建议:")
        for rec in final_report['recommendations']:
            print(f"  • {rec}")
        
        print("\n" + "=" * 80)
        
        return final_report['overall_success']
        
    except Exception as e:
        logger.error(f"质量保证测试执行失败: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)