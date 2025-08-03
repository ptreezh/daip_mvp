#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-02 16:00:00  
@Author  : DAIP-LIVE Team
@File    : test_academic_research_scenario.py
@Description:
    V0.2.4 学术研究场景质量保证
    
    按照.kiro规范要求进行完整的质量验证：
    - 功能测试：完成完整学术研究案例
    - 性能测试：万字级报告生成性能验证  
    - 认知差异验证：不同角色观点差异性检查
    - 知识沉淀验证：WikiService集成验证
    - 用户体验测试：流程易用性和完整性
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

# 导入待测试组件
from src.scenarios.academic_research_scenario import AcademicResearchScenario, AcademicResearchConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AcademicResearchQualityAssurance:
    """学术研究场景质量保证测试套件"""
    
    def __init__(self):
        self.test_results = {}
        self.scenario = AcademicResearchScenario()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有质量保证测试"""
        logger.info("=" * 60)
        logger.info("🎓 开始学术研究场景质量保证测试")
        logger.info("=" * 60)
        
        test_suite = [
            ("功能完整性测试", self.test_functional_completeness),
            ("性能基准测试", self.test_performance_benchmarks),
            ("认知差异验证", self.test_cognitive_diversity),
            ("知识沉淀验证", self.test_knowledge_persistence),
            ("用户体验测试", self.test_user_experience),
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
        """功能完整性测试 - 完成AI在教育中的应用研究案例"""
        logger.info("执行AI在教育中的应用研究案例...")
        
        try:
            # 配置学术研究参数
            config = AcademicResearchConfig(
                target_word_count=10000,
                max_iterations=3,
                quality_threshold=0.8,
                research_depth="comprehensive",
                enable_wiki_collaboration=True,
                enable_consensus_computation=True,
                academic_rigor_level="high"
            )
            
            # 执行完整学术研究
            research_topic = "人工智能在教育中的应用：机遇、挑战与未来发展"
            
            start_time = time.time()
            result = await self.scenario.conduct_academic_research(
                topic=research_topic,
                config=config
            )
            end_time = time.time()
            
            # 验证结果完整性
            validation_checks = {
                "research_success": result.get("success", False),
                "has_research_plan": "research_plan" in result,
                "has_expert_team": "expert_team" in result and len(result.get("expert_team", [])) > 0,
                "has_synthesis_result": "synthesis_result" in result,
                "has_academic_report": "academic_report" in result,
                "has_wiki_collaboration": "wiki_collaboration" in result,
                "has_consensus_result": "consensus_result" in result,
                "execution_time_reasonable": (end_time - start_time) < 1800,  # 30分钟限制
                "word_count_adequate": result.get("metadata", {}).get("word_count", 0) >= 8000  # 至少8000字
            }
            
            success = all(validation_checks.values())
            
            return {
                "success": success,
                "execution_time": end_time - start_time,
                "word_count": result.get("metadata", {}).get("word_count", 0),
                "validation_checks": validation_checks,
                "research_result": {
                    "topic": result.get("topic"),
                    "research_id": result.get("research_id"),
                    "expert_count": len(result.get("expert_team", [])),
                    "quality_score": result.get("metadata", {}).get("quality_score", 0)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "功能完整性测试执行失败"
            }
    
    async def test_performance_benchmarks(self) -> Dict[str, Any]:
        """性能基准测试 - 验证万字级报告生成性能"""
        logger.info("执行性能基准测试...")
        
        try:
            performance_tests = []
            
            # 测试不同配置下的性能
            test_configs = [
                {"target_words": 8000, "depth": "medium"},
                {"target_words": 10000, "depth": "comprehensive"},
                {"target_words": 12000, "depth": "deep"}
            ]
            
            for i, test_config in enumerate(test_configs):
                logger.info(f"性能测试 {i+1}: 目标字数 {test_config['target_words']}")
                
                config = AcademicResearchConfig(
                    target_word_count=test_config["target_words"],
                    research_depth=test_config["depth"],
                    max_iterations=2  # 减少迭代次数以控制测试时间
                )
                
                start_time = time.time()
                result = await self.scenario.conduct_academic_research(
                    topic=f"性能测试主题 {i+1}: 技术创新与社会发展",
                    config=config
                )
                end_time = time.time()
                
                execution_time = end_time - start_time
                word_count = result.get("metadata", {}).get("word_count", 0)
                
                performance_tests.append({
                    "test_id": i+1,
                    "target_words": test_config["target_words"],
                    "actual_words": word_count,
                    "execution_time": execution_time,
                    "words_per_second": word_count / execution_time if execution_time > 0 else 0,
                    "within_time_limit": execution_time < 1800,  # 30分钟
                    "achieved_target": word_count >= test_config["target_words"] * 0.8  # 至少80%目标字数
                })
            
            # 计算性能指标
            avg_execution_time = sum(test["execution_time"] for test in performance_tests) / len(performance_tests)
            avg_words_per_second = sum(test["words_per_second"] for test in performance_tests) / len(performance_tests)
            all_within_time_limit = all(test["within_time_limit"] for test in performance_tests)
            all_achieved_target = all(test["achieved_target"] for test in performance_tests)
            
            success = all_within_time_limit and all_achieved_target and avg_execution_time < 1800
            
            return {
                "success": success,
                "performance_metrics": {
                    "average_execution_time": avg_execution_time,
                    "average_words_per_second": avg_words_per_second,
                    "all_within_time_limit": all_within_time_limit,
                    "all_achieved_target": all_achieved_target
                },
                "individual_tests": performance_tests
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "性能基准测试执行失败"
            }
    
    async def test_cognitive_diversity(self) -> Dict[str, Any]:
        """认知差异验证 - 确认不同角色的观点差异性"""
        logger.info("执行认知差异验证...")
        
        try:
            # 使用争议性话题测试认知差异
            controversial_topic = "人工智能技术发展的伦理边界与监管策略"
            
            config = AcademicResearchConfig(
                target_word_count=8000,
                max_iterations=2,
                enable_consensus_computation=True,
                academic_rigor_level="high"
            )
            
            result = await self.scenario.conduct_academic_research(
                topic=controversial_topic,
                config=config
            )
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": "研究执行失败",
                    "details": result.get("error", "Unknown error")
                }
            
            # 分析专家团队的多样性
            expert_team = result.get("expert_team", [])
            synthesis_result = result.get("synthesis_result", {})
            consensus_result = result.get("consensus_result", {})
            
            # 验证角色多样性
            role_diversity_checks = {
                "multiple_experts": len(expert_team) >= 3,
                "different_perspectives": len(set(expert.get("perspective", "") for expert in expert_team)) >= 3,
                "varied_expertise": len(set(expert.get("expertise_domain", "") for expert in expert_team)) >= 2
            }
            
            # 验证观点差异性
            viewpoint_diversity_checks = {
                "has_synthesis_insights": len(synthesis_result.get("insights", [])) > 0,
                "has_consensus_data": "consensus_strength" in consensus_result,
                "moderate_consensus": 0.3 < consensus_result.get("consensus_strength", 1.0) < 0.9,  # 适度共识表明有差异
                "has_conflicting_views": consensus_result.get("conflicts_identified", 0) > 0
            }
            
            success = (
                all(role_diversity_checks.values()) and 
                any(viewpoint_diversity_checks.values())  # 至少一些观点差异指标
            )
            
            return {
                "success": success,
                "expert_team_size": len(expert_team),
                "role_diversity_checks": role_diversity_checks,
                "viewpoint_diversity_checks": viewpoint_diversity_checks,
                "consensus_strength": consensus_result.get("consensus_strength", 0),
                "conflicts_identified": consensus_result.get("conflicts_identified", 0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "认知差异验证执行失败"
            }
    
    async def test_knowledge_persistence(self) -> Dict[str, Any]:
        """知识沉淀验证 - 验证WikiService集成"""
        logger.info("执行知识沉淀验证...")
        
        try:
            # 执行研究并检查知识持久化
            topic = "知识沉淀测试：数字化转型的理论与实践"
            
            config = AcademicResearchConfig(
                target_word_count=6000,
                enable_wiki_collaboration=True,
                enable_consensus_computation=True
            )
            
            result = await self.scenario.conduct_academic_research(
                topic=topic,
                config=config
            )
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": "研究执行失败",
                    "details": result.get("error", "Unknown error")
                }
            
            # 验证知识沉淀组件
            persistence_checks = {
                "has_wiki_collaboration": "wiki_collaboration" in result,
                "has_knowledge_persistence": "knowledge_persistence" in result,
                "wiki_collaboration_success": result.get("wiki_collaboration", {}).get("success", False),
                "knowledge_entries_created": len(result.get("knowledge_persistence", {}).get("entries", [])) > 0,
                "has_structured_output": "academic_report" in result and len(result.get("academic_report", {})) > 0
            }
            
            # 检查Wiki协作结果
            wiki_result = result.get("wiki_collaboration", {})
            wiki_checks = {
                "wiki_entries_count": len(wiki_result.get("entries", [])),
                "wiki_collaboration_enabled": wiki_result.get("enabled", False),
                "wiki_consensus_integration": "consensus_points" in wiki_result
            }
            
            success = (
                persistence_checks.get("wiki_collaboration_success", False) and
                persistence_checks.get("knowledge_entries_created", False) and
                wiki_checks.get("wiki_entries_count", 0) > 0
            )
            
            return {
                "success": success,
                "persistence_checks": persistence_checks,
                "wiki_checks": wiki_checks,
                "knowledge_entries_count": len(result.get("knowledge_persistence", {}).get("entries", [])),
                "wiki_entries_count": wiki_checks.get("wiki_entries_count", 0)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "知识沉淀验证执行失败"
            }
    
    async def test_user_experience(self) -> Dict[str, Any]:
        """用户体验测试 - 验证流程易用性和完整性"""
        logger.info("执行用户体验测试...")
        
        try:
            # 模拟用户使用流程
            user_scenarios = [
                {
                    "name": "简单研究",
                    "topic": "机器学习基础概念",
                    "config": AcademicResearchConfig(target_word_count=5000, research_depth="medium")
                },
                {
                    "name": "复杂研究", 
                    "topic": "区块链技术在供应链管理中的应用研究",
                    "config": AcademicResearchConfig(target_word_count=8000, research_depth="comprehensive")
                }
            ]
            
            ux_results = []
            
            for scenario in user_scenarios:
                logger.info(f"测试用户场景: {scenario['name']}")
                
                start_time = time.time()
                result = await self.scenario.conduct_academic_research(
                    topic=scenario["topic"],
                    config=scenario["config"]
                )
                end_time = time.time()
                
                # 用户体验指标
                ux_metrics = {
                    "scenario_name": scenario["name"],
                    "research_success": result.get("success", False),
                    "response_time": end_time - start_time,
                    "response_time_acceptable": (end_time - start_time) < 600,  # 10分钟内响应
                    "result_completeness": len(result.keys()) >= 5,  # 至少5个结果字段
                    "error_handling": "error" not in result or result.get("success", False),
                    "output_quality": result.get("metadata", {}).get("quality_score", 0) > 0.5
                }
                
                ux_results.append(ux_metrics)
            
            # 计算整体用户体验得分
            total_scenarios = len(ux_results)
            successful_scenarios = sum(1 for r in ux_results if r["research_success"])
            acceptable_response_times = sum(1 for r in ux_results if r["response_time_acceptable"])
            complete_results = sum(1 for r in ux_results if r["result_completeness"])
            
            success = (
                successful_scenarios == total_scenarios and
                acceptable_response_times == total_scenarios and
                complete_results == total_scenarios
            )
            
            return {
                "success": success,
                "overall_metrics": {
                    "success_rate": successful_scenarios / total_scenarios,
                    "acceptable_response_rate": acceptable_response_times / total_scenarios,
                    "completeness_rate": complete_results / total_scenarios,
                    "average_response_time": sum(r["response_time"] for r in ux_results) / total_scenarios
                },
                "scenario_results": ux_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "用户体验测试执行失败"
            }
    
    async def test_integration_stability(self) -> Dict[str, Any]:
        """集成稳定性测试 - 验证组件协作稳定性"""
        logger.info("执行集成稳定性测试...")
        
        try:
            # 连续执行多次研究，检查稳定性
            stability_runs = 3
            results = []
            
            for i in range(stability_runs):
                logger.info(f"稳定性测试运行 {i+1}/{stability_runs}")
                
                topic = f"稳定性测试 {i+1}: 数字经济与创新发展"
                config = AcademicResearchConfig(
                    target_word_count=6000,
                    max_iterations=2
                )
                
                try:
                    start_time = time.time()
                    result = await self.scenario.conduct_academic_research(
                        topic=topic,
                        config=config
                    )
                    end_time = time.time()
                    
                    run_result = {
                        "run_number": i+1,
                        "success": result.get("success", False),
                        "execution_time": end_time - start_time,
                        "word_count": result.get("metadata", {}).get("word_count", 0),
                        "error": result.get("error") if not result.get("success") else None
                    }
                    
                except Exception as e:
                    run_result = {
                        "run_number": i+1,
                        "success": False,
                        "error": str(e),
                        "execution_time": 0,
                        "word_count": 0
                    }
                
                results.append(run_result)
                
                # 短暂休息避免资源竞争
                await asyncio.sleep(1)
            
            # 分析稳定性指标
            successful_runs = sum(1 for r in results if r["success"])
            consistency_check = len(set(r["success"] for r in results)) == 1  # 所有运行结果一致
            execution_time_variance = max(r["execution_time"] for r in results) - min(r["execution_time"] for r in results)
            
            success = (
                successful_runs == stability_runs and
                consistency_check and
                execution_time_variance < 300  # 执行时间差异小于5分钟
            )
            
            return {
                "success": success,
                "stability_metrics": {
                    "successful_runs": successful_runs,
                    "total_runs": stability_runs,
                    "success_rate": successful_runs / stability_runs,
                    "consistency_check": consistency_check,
                    "execution_time_variance": execution_time_variance,
                    "average_execution_time": sum(r["execution_time"] for r in results) / len(results)
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
            recommendations.append("所有测试通过，学术研究场景质量符合V0.2.4要求")
        
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
                "performance_benchmarks": self.test_results.get("性能基准测试", {}).get("success", False),
                "cognitive_diversity": self.test_results.get("认知差异验证", {}).get("success", False),
                "knowledge_persistence": self.test_results.get("知识沉淀验证", {}).get("success", False),
                "user_experience": self.test_results.get("用户体验测试", {}).get("success", False),
                "integration_stability": self.test_results.get("集成稳定性测试", {}).get("success", False)
            }
        }
        
        # 保存报告
        await self.save_report(report)
        
        return report
    
    async def save_report(self, report: Dict[str, Any]):
        """保存质量保证报告"""
        try:
            report_path = Path("v0_2_4_academic_research_quality_report.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"质量保证报告已保存: {report_path}")
        except Exception as e:
            logger.error(f"报告保存失败: {e}")


async def main():
    """执行V0.2.4学术研究场景质量保证"""
    qa = AcademicResearchQualityAssurance()
    
    try:
        final_report = await qa.run_all_tests()
        
        print("\n" + "=" * 80)
        print("📊 V0.2.4 学术研究场景质量保证报告")
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