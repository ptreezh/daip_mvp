#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-02 20:05:00
@Author  : DAIP-LIVE Team
@File    : test_casual_discussion_scenario.py
@Description:
    V0.2.7 轻松讨论场景质量保证测试
    
    按照.kiro规范要求进行完整的质量验证：
    - 功能测试：完成"最近看的好电影"轻松讨论案例
    - 自然性测试：验证对话的自然流畅性和趣味性
    - 话题转换测试：测试话题切换的平滑性和相关性
    - 用户体验测试：确认轻松愉快的讨论氛围和用户参与度
    - 性能测试：确保轻松模式下的响应速度和系统稳定性
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

# 导入待测试组件
from src.scenarios.casual_discussion_scenario import CasualDiscussionScenario, CasualDiscussionConfig

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CasualDiscussionQualityAssurance:
    """轻松讨论场景质量保证测试套件"""
    
    def __init__(self):
        self.test_results = {}
        self.scenario = CasualDiscussionScenario()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有质量保证测试"""
        logger.info("=" * 60)
        logger.info("🎭 开始轻松讨论场景质量保证测试")
        logger.info("=" * 60)
        
        test_suite = [
            ("功能完整性测试", self.test_functional_completeness),
            ("自然性和趣味性测试", self.test_naturalness_and_fun),
            ("话题转换机制测试", self.test_topic_transition),
            ("社交互动功能测试", self.test_social_interactions),
            ("用户体验流程测试", self.test_user_experience),
            ("性能和稳定性测试", self.test_performance_stability),
            ("氛围营造能力测试", self.test_atmosphere_creation)
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
        """功能完整性测试 - 完成"最近看的好电影"轻松讨论案例"""
        logger.info("执行最近看的好电影轻松讨论案例...")
        
        try:
            # 配置轻松讨论参数
            config = CasualDiscussionConfig(
                max_participants=4,
                discussion_style="casual",
                topic_flexibility=0.8,
                humor_level=0.7,
                social_elements=True,
                emoji_usage=True,
                energy_level="medium"
            )
            
            user_preferences = {
                "interests": ["电影", "娱乐", "艺术", "文化"],
                "discussion_style": "casual",
                "humor_tolerance": 0.8,
                "social_interaction_preference": "moderate"
            }
            
            # 执行完整轻松讨论
            question = "最近看的好电影"
            
            start_time = time.time()
            result = await self.scenario.start_casual_discussion(
                initial_topic=question,
                user_preferences=user_preferences,
                config=config
            )
            end_time = time.time()
            
            # 验证结果完整性
            validation_checks = {
                "discussion_success": result.get("success", False),
                "has_participants": "selected_participants" in result and len(result.get("selected_participants", [])) >= 3,
                "has_discussion_rounds": "discussion_result" in result and len(result.get("discussion_result", {}).get("discussion_rounds", [])) >= 3,
                "has_social_interactions": "social_summary" in result,
                "has_topic_evolution": "topic_evolution" in result,
                "execution_time_reasonable": (end_time - start_time) < 180,  # 3分钟限制
                "has_engagement_metrics": "metadata" in result and "engagement_score" in result["metadata"],
                "has_fun_factor": "metadata" in result and "fun_factor" in result["metadata"],
                "movie_topic_relevance": self._check_movie_topic_relevance(result)
            }
            
            success = all(validation_checks.values())
            
            return {
                "success": success,
                "execution_time": end_time - start_time,
                "participant_count": len(result.get("selected_participants", [])),
                "discussion_rounds": len(result.get("discussion_result", {}).get("discussion_rounds", [])),
                "validation_checks": validation_checks,
                "casual_discussion_result": {
                    "topic": result.get("initial_topic"),
                    "discussion_id": result.get("discussion_id"),
                    "engagement_score": result.get("metadata", {}).get("engagement_score", 0),
                    "fun_factor": result.get("metadata", {}).get("fun_factor", 0),
                    "social_interactions": result.get("social_summary", {}).get("interaction_stats", {}).get("total_interactions", 0)
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "功能完整性测试执行失败"
            }
    
    async def test_naturalness_and_fun(self) -> Dict[str, Any]:
        """自然性和趣味性测试 - 验证对话的自然流畅性和趣味性"""
        logger.info("执行自然性和趣味性测试...")
        
        try:
            # 测试多种不同风格的轻松话题
            test_topics = [
                {
                    "topic": "周末最喜欢做什么",
                    "expected_style": "relaxed",
                    "humor_expectation": 0.6
                },
                {
                    "topic": "有什么有趣的旅行经历",
                    "expected_style": "storytelling",
                    "humor_expectation": 0.7
                },
                {
                    "topic": "推荐一些好听的音乐",
                    "expected_style": "sharing",
                    "humor_expectation": 0.5
                }
            ]
            
            naturalness_results = []
            
            for i, test_case in enumerate(test_topics):
                logger.info(f"自然性测试 {i+1}: {test_case['topic']}")
                
                config = CasualDiscussionConfig(
                    max_participants=3,
                    humor_level=test_case["humor_expectation"],
                    social_elements=True
                )
                
                result = await self.scenario.start_casual_discussion(
                    initial_topic=test_case["topic"],
                    config=config
                )
                
                if not result.get("success"):
                    naturalness_results.append({
                        "test_case": i+1,
                        "success": False,
                        "error": result.get("error", "Unknown error")
                    })
                    continue
                
                discussion_rounds = result.get("discussion_result", {}).get("discussion_rounds", [])
                
                # 验证自然性和趣味性
                naturalness_checks = {
                    "natural_conversation_flow": self._assess_conversation_flow(discussion_rounds),
                    "appropriate_humor_level": self._assess_humor_appropriateness(
                        discussion_rounds, test_case["humor_expectation"]
                    ),
                    "emoji_usage_natural": self._assess_emoji_naturalness(discussion_rounds),
                    "topic_relevance_maintained": self._assess_topic_consistency(
                        discussion_rounds, test_case["topic"]
                    ),
                    "participant_style_diversity": self._assess_style_diversity(discussion_rounds),
                    "engagement_sustainability": self._assess_engagement_sustainability(discussion_rounds)
                }
                
                naturalness_score = sum(naturalness_checks.values()) / len(naturalness_checks)
                
                naturalness_results.append({
                    "test_case": i+1,
                    "topic": test_case["topic"],
                    "naturalness_checks": naturalness_checks,
                    "naturalness_score": naturalness_score,
                    "fun_factor": result.get("metadata", {}).get("fun_factor", 0),
                    "engagement_score": result.get("metadata", {}).get("engagement_score", 0),
                    "success": naturalness_score >= 0.7 and result.get("metadata", {}).get("fun_factor", 0) >= 0.5
                })
            
            # 计算整体自然性和趣味性评分
            successful_tests = sum(1 for result in naturalness_results if result.get("success", False))
            total_tests = len(naturalness_results)
            success_rate = successful_tests / total_tests if total_tests > 0 else 0
            
            avg_naturalness = sum(r.get("naturalness_score", 0) for r in naturalness_results) / total_tests if total_tests > 0 else 0
            avg_fun_factor = sum(r.get("fun_factor", 0) for r in naturalness_results) / total_tests if total_tests > 0 else 0
            
            success = success_rate >= 0.8  # 80%成功率要求
            
            return {
                "success": success,
                "success_rate": success_rate,
                "successful_tests": successful_tests,
                "total_tests": total_tests,
                "average_naturalness_score": avg_naturalness,
                "average_fun_factor": avg_fun_factor,
                "naturalness_results": naturalness_results,
                "overall_assessment": {
                    "conversation_quality": "优秀" if avg_naturalness >= 0.8 else "良好" if avg_naturalness >= 0.6 else "需改进",
                    "entertainment_value": "高" if avg_fun_factor >= 0.7 else "中" if avg_fun_factor >= 0.5 else "低"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "自然性和趣味性测试执行失败"
            }
    
    async def test_topic_transition(self) -> Dict[str, Any]:
        """话题转换机制测试 - 测试话题切换的平滑性和相关性"""
        logger.info("执行话题转换机制测试...")
        
        try:
            # 使用容易引发话题转换的初始话题
            initial_topic = "分享一个让你印象深刻的经历"
            
            config = CasualDiscussionConfig(
                max_participants=4,
                topic_flexibility=0.9,  # 高话题灵活度
                social_elements=True
            )
            
            result = await self.scenario.start_casual_discussion(
                initial_topic=initial_topic,
                config=config
            )
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": "话题转换测试基础讨论失败",
                    "details": result.get("error", "Unknown error")
                }
            
            topic_evolution = result.get("topic_evolution", {})
            discussion_rounds = result.get("discussion_result", {}).get("discussion_rounds", [])
            
            # 验证话题转换质量
            transition_checks = {
                "has_topic_evolution": len(topic_evolution.get("topic_flow", [])) > 1,
                "natural_transitions": topic_evolution.get("natural_transitions", 0) > 0,
                "topic_relevance_maintained": self._check_transition_relevance(topic_evolution),
                "smooth_flow": self._assess_transition_smoothness(discussion_rounds),
                "topic_drift_reasonable": 0.2 <= topic_evolution.get("topic_drift_score", 0) <= 0.8,
                "participant_follow_along": self._check_participant_adaptation(discussion_rounds)
            }
            
            # 话题转换质量分析
            transition_quality = {
                "total_transitions": topic_evolution.get("natural_transitions", 0),
                "topic_drift_score": topic_evolution.get("topic_drift_score", 0),
                "final_topic_diversity": len(topic_evolution.get("final_directions", [])),
                "transition_smoothness": self._calculate_transition_smoothness(discussion_rounds),
                "contextual_coherence": self._assess_contextual_coherence(topic_evolution)
            }
            
            success = (
                sum(transition_checks.values()) >= len(transition_checks) * 0.7 and
                transition_quality["transition_smoothness"] >= 0.6
            )
            
            return {
                "success": success,
                "transition_checks": transition_checks,
                "transition_quality": transition_quality,
                "topic_evolution_summary": {
                    "initial_topic": topic_evolution.get("initial_topic"),
                    "final_directions": topic_evolution.get("final_directions", []),
                    "total_topic_changes": len(topic_evolution.get("topic_flow", [])),
                    "natural_transition_count": topic_evolution.get("natural_transitions", 0)
                },
                "transition_examples": self._extract_transition_examples(discussion_rounds)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "话题转换机制测试执行失败"
            }
    
    async def test_social_interactions(self) -> Dict[str, Any]:
        """社交互动功能测试 - 验证表情、点赞、高亮等社交元素"""
        logger.info("执行社交互动功能测试...")
        
        try:
            # 配置高社交互动的讨论
            config = CasualDiscussionConfig(
                max_participants=4,
                social_elements=True,
                emoji_usage=True,
                humor_level=0.8
            )
            
            # 使用容易引发互动的话题
            topic = "分享一件让你特别开心的事"
            
            result = await self.scenario.start_casual_discussion(
                initial_topic=topic,
                config=config
            )
            
            if not result.get("success"):
                return {
                    "success": False,
                    "error": "社交互动测试基础讨论失败",
                    "details": result.get("error", "Unknown error")
                }
            
            social_summary = result.get("social_summary", {})
            interaction_stats = social_summary.get("interaction_stats", {})
            discussion_rounds = result.get("discussion_result", {}).get("discussion_rounds", [])
            
            # 验证社交互动功能
            social_checks = {
                "has_social_interactions": interaction_stats.get("total_interactions", 0) > 0,
                "has_likes": interaction_stats.get("likes_count", 0) > 0,
                "has_emoji_reactions": interaction_stats.get("emoji_reactions_count", 0) > 0,
                "has_highlights": interaction_stats.get("highlights_count", 0) > 0,
                "interaction_rate_healthy": interaction_stats.get("interaction_rate", 0) > 0.5,
                "social_atmosphere_positive": social_summary.get("atmosphere_rating") in ["positive", "very_positive"],
                "popular_content_identified": len(social_summary.get("popular_content", [])) > 0
            }
            
            # 社交元素质量分析
            social_quality = {
                "total_interactions": interaction_stats.get("total_interactions", 0),
                "interaction_diversity": len([k for k, v in interaction_stats.items() if k.endswith("_count") and v > 0]),
                "engagement_level": social_summary.get("social_engagement_score", 0),
                "atmosphere_quality": social_summary.get("atmosphere_rating", "neutral"),
                "emoji_usage_rate": self._calculate_emoji_usage_rate(discussion_rounds),
                "content_appreciation": len(social_summary.get("popular_content", []))
            }
            
            # 验证社交功能的实际效果
            social_effectiveness = {
                "encourages_participation": self._assess_participation_encouragement(discussion_rounds, social_summary),
                "creates_positive_atmosphere": social_summary.get("atmosphere_rating") != "neutral",
                "facilitates_connection": social_quality["engagement_level"] > 0.6,
                "maintains_casual_tone": self._check_casual_tone_maintenance(discussion_rounds)
            }
            
            success = (
                sum(social_checks.values()) >= len(social_checks) * 0.7 and
                sum(social_effectiveness.values()) >= len(social_effectiveness) * 0.6
            )
            
            return {
                "success": success,
                "social_checks": social_checks,
                "social_quality": social_quality,
                "social_effectiveness": social_effectiveness,
                "interaction_breakdown": {
                    "likes": interaction_stats.get("likes_count", 0),
                    "emoji_reactions": interaction_stats.get("emoji_reactions_count", 0),
                    "highlights": interaction_stats.get("highlights_count", 0),
                    "total": interaction_stats.get("total_interactions", 0)
                },
                "popular_content_analysis": social_summary.get("popular_content", [])[:3]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "社交互动功能测试执行失败"
            }
    
    async def test_user_experience(self) -> Dict[str, Any]:
        """用户体验流程测试 - 确认轻松愉快的讨论氛围和用户参与度"""
        logger.info("执行用户体验流程测试...")
        
        try:
            # 模拟不同用户偏好的体验测试
            user_scenarios = [
                {
                    "name": "内向用户体验",
                    "preferences": {
                        "social_interaction_preference": "low",
                        "humor_tolerance": 0.5,
                        "discussion_style": "gentle"
                    },
                    "config": CasualDiscussionConfig(max_participants=3, humor_level=0.5),
                    "topic": "分享一本喜欢的书"
                },
                {
                    "name": "外向用户体验",
                    "preferences": {
                        "social_interaction_preference": "high",
                        "humor_tolerance": 0.9,
                        "discussion_style": "energetic"
                    },
                    "config": CasualDiscussionConfig(max_participants=4, humor_level=0.8, energy_level="high"),
                    "topic": "最搞笑的一次经历"
                },
                {
                    "name": "平衡用户体验",
                    "preferences": {
                        "social_interaction_preference": "moderate",
                        "humor_tolerance": 0.7,
                        "discussion_style": "balanced"
                    },
                    "config": CasualDiscussionConfig(max_participants=4, humor_level=0.6),
                    "topic": "聊聊最近的兴趣爱好"
                }
            ]
            
            ux_results = []
            
            for scenario in user_scenarios:
                logger.info(f"测试用户体验场景: {scenario['name']}")
                
                start_time = time.time()
                
                result = await self.scenario.start_casual_discussion(
                    initial_topic=scenario["topic"],
                    user_preferences=scenario["preferences"],
                    config=scenario["config"]
                )
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                if not result.get("success"):
                    ux_results.append({
                        "scenario_name": scenario["name"],
                        "success": False,
                        "error": result.get("error", "Unknown error")
                    })
                    continue
                
                # 用户体验指标
                ux_metrics = {
                    "scenario_name": scenario["name"],
                    "discussion_success": result.get("success", False),
                    "response_time": execution_time,
                    "engagement_score": result.get("metadata", {}).get("engagement_score", 0),
                    "fun_factor": result.get("metadata", {}).get("fun_factor", 0),
                    "atmosphere_comfort": self._assess_atmosphere_comfort(result, scenario["preferences"]),
                    "content_appropriateness": self._assess_content_appropriateness(result, scenario["preferences"]),
                    "interaction_comfort": self._assess_interaction_comfort(result, scenario["preferences"]),
                    "topic_engagement": self._assess_topic_engagement(result),
                    "overall_satisfaction": self._estimate_user_satisfaction(result, scenario["preferences"])
                }
                
                ux_results.append(ux_metrics)
            
            # 计算整体用户体验得分
            total_scenarios = len(ux_results)
            successful_scenarios = sum(1 for r in ux_results if r.get("success", r.get("discussion_success", False)))
            high_satisfaction = sum(1 for r in ux_results if r.get("overall_satisfaction", 0) >= 0.7)
            comfortable_atmosphere = sum(1 for r in ux_results if r.get("atmosphere_comfort", 0) >= 0.7)
            
            success = (
                successful_scenarios == total_scenarios and
                high_satisfaction >= total_scenarios * 0.8 and
                comfortable_atmosphere >= total_scenarios * 0.7
            )
            
            return {
                "success": success,
                "overall_metrics": {
                    "success_rate": successful_scenarios / total_scenarios,
                    "satisfaction_rate": high_satisfaction / total_scenarios,
                    "comfort_rate": comfortable_atmosphere / total_scenarios,
                    "average_engagement": sum(r.get("engagement_score", 0) for r in ux_results) / total_scenarios,
                    "average_fun_factor": sum(r.get("fun_factor", 0) for r in ux_results) / total_scenarios
                },
                "scenario_results": ux_results,
                "user_experience_assessment": {
                    "accessibility": "高" if successful_scenarios == total_scenarios else "中",
                    "adaptability": "强" if high_satisfaction >= total_scenarios * 0.8 else "中",
                    "comfort": "优秀" if comfortable_atmosphere >= total_scenarios * 0.8 else "良好"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "用户体验流程测试执行失败"
            }
    
    async def test_performance_stability(self) -> Dict[str, Any]:
        """性能和稳定性测试 - 确保轻松模式下的响应速度和系统稳定性"""
        logger.info("执行性能和稳定性测试...")
        
        try:
            # 连续执行多次轻松讨论，检查稳定性
            stability_runs = 3
            performance_results = []
            
            for i in range(stability_runs):
                logger.info(f"稳定性测试运行 {i+1}/{stability_runs}")
                
                topic = f"随机话题测试 {i+1}: 说说今天的心情"
                
                try:
                    start_time = time.time()
                    result = await self.scenario.start_casual_discussion(
                        initial_topic=topic,
                        config=CasualDiscussionConfig(max_participants=3)
                    )
                    end_time = time.time()
                    
                    run_result = {
                        "run_number": i+1,
                        "success": result.get("success", False),
                        "execution_time": end_time - start_time,
                        "participant_count": len(result.get("selected_participants", [])),
                        "discussion_rounds": len(result.get("discussion_result", {}).get("discussion_rounds", [])),
                        "social_interactions": result.get("social_summary", {}).get("interaction_stats", {}).get("total_interactions", 0),
                        "memory_usage": self._estimate_memory_usage(result),
                        "error": result.get("error") if not result.get("success") else None
                    }
                    
                except Exception as e:
                    run_result = {
                        "run_number": i+1,
                        "success": False,
                        "error": str(e),
                        "execution_time": 0,
                        "participant_count": 0,
                        "discussion_rounds": 0,
                        "social_interactions": 0,
                        "memory_usage": 0
                    }
                
                performance_results.append(run_result)
                
                # 短暂休息避免资源竞争
                await asyncio.sleep(0.5)
            
            # 分析性能和稳定性指标
            successful_runs = sum(1 for r in performance_results if r["success"])
            execution_times = [r["execution_time"] for r in performance_results if r["success"]]
            
            performance_metrics = {
                "successful_runs": successful_runs,
                "total_runs": stability_runs,
                "success_rate": successful_runs / stability_runs,
                "average_execution_time": sum(execution_times) / len(execution_times) if execution_times else 0,
                "max_execution_time": max(execution_times) if execution_times else 0,
                "min_execution_time": min(execution_times) if execution_times else 0,
                "execution_time_variance": max(execution_times) - min(execution_times) if execution_times else 0,
                "average_memory_usage": sum(r["memory_usage"] for r in performance_results) / stability_runs
            }
            
            # 性能标准检查
            performance_checks = {
                "all_runs_successful": successful_runs == stability_runs,
                "response_time_acceptable": performance_metrics["average_execution_time"] < 120,  # 2分钟内
                "performance_consistent": performance_metrics["execution_time_variance"] < 60,  # 变化小于1分钟
                "memory_usage_reasonable": performance_metrics["average_memory_usage"] < 100,  # 简化的内存检查
                "no_critical_errors": all(r.get("error") is None for r in performance_results if r["success"])
            }
            
            success = (
                sum(performance_checks.values()) >= len(performance_checks) * 0.8 and
                performance_metrics["success_rate"] >= 0.9
            )
            
            return {
                "success": success,
                "performance_metrics": performance_metrics,
                "performance_checks": performance_checks,
                "stability_assessment": {
                    "reliability": "高" if successful_runs == stability_runs else "中",
                    "consistency": "好" if performance_metrics["execution_time_variance"] < 30 else "一般",
                    "efficiency": "优秀" if performance_metrics["average_execution_time"] < 60 else "良好"
                },
                "individual_runs": performance_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "性能和稳定性测试执行失败"
            }
    
    async def test_atmosphere_creation(self) -> Dict[str, Any]:
        """氛围营造能力测试 - 验证轻松愉快讨论氛围的营造效果"""
        logger.info("执行氛围营造能力测试...")
        
        try:
            # 测试不同氛围要求的话题
            atmosphere_tests = [
                {
                    "name": "轻松休闲氛围",
                    "topic": "周末在家最喜欢做什么",
                    "config": CasualDiscussionConfig(energy_level="low", humor_level=0.6),
                    "expected_atmosphere": "relaxed"
                },
                {
                    "name": "活跃有趣氛围",
                    "topic": "分享一个有趣的巧合",
                    "config": CasualDiscussionConfig(energy_level="high", humor_level=0.8),
                    "expected_atmosphere": "energetic"
                },
                {
                    "name": "温暖支持氛围",
                    "topic": "说说最近让你感动的事",
                    "config": CasualDiscussionConfig(energy_level="medium", humor_level=0.4),
                    "expected_atmosphere": "supportive"
                }
            ]
            
            atmosphere_results = []
            
            for test in atmosphere_tests:
                logger.info(f"氛围测试: {test['name']}")
                
                result = await self.scenario.start_casual_discussion(
                    initial_topic=test["topic"],
                    config=test["config"]
                )
                
                if not result.get("success"):
                    atmosphere_results.append({
                        "test_name": test["name"],
                        "success": False,
                        "error": result.get("error", "Unknown error")
                    })
                    continue
                
                discussion_rounds = result.get("discussion_result", {}).get("discussion_rounds", [])
                social_summary = result.get("social_summary", {})
                
                # 评估氛围营造效果
                atmosphere_assessment = {
                    "energy_level_match": self._assess_energy_level_match(
                        discussion_rounds, test["config"].energy_level
                    ),
                    "humor_appropriateness": self._assess_humor_level_match(
                        discussion_rounds, test["config"].humor_level
                    ),
                    "emotional_tone": self._assess_emotional_tone(discussion_rounds),
                    "participant_comfort": self._assess_participant_comfort_level(discussion_rounds),
                    "conversation_naturalness": self._assess_conversation_naturalness(discussion_rounds),
                    "social_warmth": social_summary.get("atmosphere_rating", "neutral")
                }
                
                # 氛围质量评分
                atmosphere_score = self._calculate_atmosphere_score(atmosphere_assessment, test["expected_atmosphere"])
                
                atmosphere_results.append({
                    "test_name": test["name"],
                    "expected_atmosphere": test["expected_atmosphere"],
                    "atmosphere_assessment": atmosphere_assessment,
                    "atmosphere_score": atmosphere_score,
                    "engagement_score": result.get("metadata", {}).get("engagement_score", 0),
                    "fun_factor": result.get("metadata", {}).get("fun_factor", 0),
                    "success": atmosphere_score >= 0.7
                })
            
            # 计算整体氛围营造能力
            successful_tests = sum(1 for r in atmosphere_results if r.get("success", False))
            total_tests = len(atmosphere_results)
            success_rate = successful_tests / total_tests if total_tests > 0 else 0
            
            avg_atmosphere_score = sum(r.get("atmosphere_score", 0) for r in atmosphere_results) / total_tests if total_tests > 0 else 0
            
            success = success_rate >= 0.8  # 80%成功率要求
            
            return {
                "success": success,
                "success_rate": success_rate,
                "successful_tests": successful_tests,
                "total_tests": total_tests,
                "average_atmosphere_score": avg_atmosphere_score,
                "atmosphere_results": atmosphere_results,
                "atmosphere_creation_assessment": {
                    "versatility": "强" if successful_tests == total_tests else "中",
                    "effectiveness": "高" if avg_atmosphere_score >= 0.8 else "中",
                    "consistency": "好" if success_rate >= 0.8 else "一般"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "氛围营造能力测试执行失败"
            }
    
    # 辅助方法
    def _check_movie_topic_relevance(self, result: Dict[str, Any]) -> bool:
        """检查电影话题相关性"""
        discussion_rounds = result.get("discussion_result", {}).get("discussion_rounds", [])
        movie_keywords = ["电影", "影片", "导演", "演员", "剧情", "票房", "影院"]
        
        for round_data in discussion_rounds:
            contributions = round_data.get("contributions", [])
            for contribution in contributions:
                content = contribution.get("content", "")
                if any(keyword in content for keyword in movie_keywords):
                    return True
        
        return False
    
    def _assess_conversation_flow(self, discussion_rounds: List[Dict[str, Any]]) -> bool:
        """评估对话流畅性"""
        if len(discussion_rounds) < 2:
            return False
        
        # 检查对话的连贯性
        for i in range(1, len(discussion_rounds)):
            prev_round = discussion_rounds[i-1]
            curr_round = discussion_rounds[i]
            
            prev_engagement = prev_round.get("engagement_level", 0)
            curr_engagement = curr_round.get("engagement_level", 0)
            
            # 参与度不应该急剧下降
            if curr_engagement < prev_engagement * 0.5:
                return False
        
        return True
    
    def _assess_humor_appropriateness(self, discussion_rounds: List[Dict[str, Any]], expected_level: float) -> bool:
        """评估幽默程度的适当性"""
        humor_indicators = ["😂", "哈哈", "好笑", "有趣", "搞笑", "逗", "🤣"]
        total_humor_count = 0
        total_contributions = 0
        
        for round_data in discussion_rounds:
            contributions = round_data.get("contributions", [])
            for contribution in contributions:
                content = contribution.get("content", "")
                humor_count = sum(1 for indicator in humor_indicators if indicator in content)
                total_humor_count += humor_count
                total_contributions += 1
        
        if total_contributions == 0:
            return False
        
        humor_ratio = total_humor_count / total_contributions
        expected_ratio = expected_level * 0.3  # 简化的期望比例
        
        return abs(humor_ratio - expected_ratio) <= 0.2
    
    def _assess_emoji_naturalness(self, discussion_rounds: List[Dict[str, Any]]) -> bool:
        """评估表情符号使用的自然性"""
        total_emoji = 0
        total_contributions = 0
        
        for round_data in discussion_rounds:
            contributions = round_data.get("contributions", [])
            for contribution in contributions:
                emoji_count = contribution.get("emoji_usage", 0)
                total_emoji += emoji_count
                total_contributions += 1
        
        if total_contributions == 0:
            return False
        
        # 自然的表情符号使用率应该在合理范围内
        emoji_ratio = total_emoji / total_contributions
        return 0.1 <= emoji_ratio <= 1.0
    
    def _assess_topic_consistency(self, discussion_rounds: List[Dict[str, Any]], original_topic: str) -> bool:
        """评估话题一致性"""
        topic_keywords = set(original_topic.lower().split())
        
        for round_data in discussion_rounds:
            contributions = round_data.get("contributions", [])
            round_relevance = 0
            
            for contribution in contributions:
                content = contribution.get("content", "").lower()
                relevance = contribution.get("topic_relevance", 0)
                round_relevance += relevance
            
            # 每轮至少应该有一定的话题相关性
            avg_relevance = round_relevance / len(contributions) if contributions else 0
            if avg_relevance < 0.3:
                return False
        
        return True
    
    def _assess_style_diversity(self, discussion_rounds: List[Dict[str, Any]]) -> bool:
        """评估参与者风格多样性"""
        participant_styles = {}
        
        for round_data in discussion_rounds:
            contributions = round_data.get("contributions", [])
            for contribution in contributions:
                participant_id = contribution.get("participant_id", "unknown")
                style_score = contribution.get("style_score", 0.5)
                
                if participant_id not in participant_styles:
                    participant_styles[participant_id] = []
                participant_styles[participant_id].append(style_score)
        
        # 检查是否有足够的风格差异
        avg_styles = []
        for participant_id, scores in participant_styles.items():
            avg_styles.append(sum(scores) / len(scores))
        
        if len(avg_styles) < 2:
            return True
        
        # 风格差异应该存在
        style_variance = max(avg_styles) - min(avg_styles)
        return style_variance > 0.1
    
    def _assess_engagement_sustainability(self, discussion_rounds: List[Dict[str, Any]]) -> bool:
        """评估参与度持续性"""
        engagement_levels = [round_data.get("engagement_level", 0.5) for round_data in discussion_rounds]
        
        if not engagement_levels:
            return False
        
        # 参与度不应该持续下降
        declining_count = 0
        for i in range(1, len(engagement_levels)):
            if engagement_levels[i] < engagement_levels[i-1]:
                declining_count += 1
        
        # 允许部分下降，但不能超过一半的轮次
        return declining_count <= len(engagement_levels) / 2
    
    def _check_transition_relevance(self, topic_evolution: Dict[str, Any]) -> bool:
        """检查话题转换的相关性"""
        topic_flow = topic_evolution.get("topic_flow", [])
        
        if len(topic_flow) < 2:
            return True
        
        # 检查相邻话题之间是否有关联
        for i in range(1, len(topic_flow)):
            prev_keywords = set(topic_flow[i-1].get("keywords", []))
            curr_keywords = set(topic_flow[i].get("keywords", []))
            
            # 应该有一些关键词重叠
            overlap = len(prev_keywords & curr_keywords)
            if overlap == 0 and len(prev_keywords) > 0 and len(curr_keywords) > 0:
                return False
        
        return True
    
    def _assess_transition_smoothness(self, discussion_rounds: List[Dict[str, Any]]) -> bool:
        """评估话题转换的平滑性"""
        for round_data in discussion_rounds:
            contributions = round_data.get("contributions", [])
            for contribution in contributions:
                content = contribution.get("content", "")
                
                # 检查是否有生硬的话题转换
                abrupt_indicators = ["突然", "忽然", "话说回来", "不说这个了"]
                if any(indicator in content for indicator in abrupt_indicators):
                    return False
        
        return True
    
    def _check_participant_adaptation(self, discussion_rounds: List[Dict[str, Any]]) -> bool:
        """检查参与者对话题转换的适应性"""
        participant_relevance = {}
        
        for round_data in discussion_rounds:
            contributions = round_data.get("contributions", [])
            for contribution in contributions:
                participant_id = contribution.get("participant_id", "unknown")
                relevance = contribution.get("topic_relevance", 0)
                
                if participant_id not in participant_relevance:
                    participant_relevance[participant_id] = []
                participant_relevance[participant_id].append(relevance)
        
        # 所有参与者的平均相关性应该保持在合理水平
        for participant_id, relevance_scores in participant_relevance.items():
            avg_relevance = sum(relevance_scores) / len(relevance_scores)
            if avg_relevance < 0.4:
                return False
        
        return True
    
    def _calculate_transition_smoothness(self, discussion_rounds: List[Dict[str, Any]]) -> float:
        """计算话题转换平滑度"""
        smoothness_scores = []
        
        for i, round_data in enumerate(discussion_rounds):
            contributions = round_data.get("contributions", [])
            round_smoothness = 0
            
            for contribution in contributions:
                topic_relevance = contribution.get("topic_relevance", 0.5)
                engagement_score = contribution.get("engagement_score", 0.5)
                
                # 平滑度 = 话题相关性 + 参与度
                contribution_smoothness = (topic_relevance + engagement_score) / 2
                round_smoothness += contribution_smoothness
            
            if contributions:
                smoothness_scores.append(round_smoothness / len(contributions))
        
        return sum(smoothness_scores) / len(smoothness_scores) if smoothness_scores else 0.5
    
    def _assess_contextual_coherence(self, topic_evolution: Dict[str, Any]) -> float:
        """评估上下文连贯性"""
        topic_flow = topic_evolution.get("topic_flow", [])
        
        if len(topic_flow) < 2:
            return 1.0
        
        coherence_scores = []
        
        for i in range(1, len(topic_flow)):
            prev_engagement = topic_flow[i-1].get("engagement", 0.5)
            curr_engagement = topic_flow[i].get("engagement", 0.5)
            
            # 连贯性基于参与度的连续性
            coherence = 1 - abs(curr_engagement - prev_engagement)
            coherence_scores.append(coherence)
        
        return sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.5
    
    def _extract_transition_examples(self, discussion_rounds: List[Dict[str, Any]]) -> List[str]:
        """提取话题转换示例"""
        examples = []
        
        for round_data in discussion_rounds:
            contributions = round_data.get("contributions", [])
            for contribution in contributions:
                content = contribution.get("content", "")
                
                # 寻找话题转换的语言标志
                transition_indicators = ["这让我想到", "说到这个", "顺便说", "另外"]
                for indicator in transition_indicators:
                    if indicator in content:
                        examples.append(content[:100] + "..." if len(content) > 100 else content)
                        break
        
        return examples[:3]  # 返回前3个示例
    
    def _calculate_emoji_usage_rate(self, discussion_rounds: List[Dict[str, Any]]) -> float:
        """计算表情符号使用率"""
        total_emoji = 0
        total_contributions = 0
        
        for round_data in discussion_rounds:
            contributions = round_data.get("contributions", [])
            for contribution in contributions:
                emoji_count = contribution.get("emoji_usage", 0)
                total_emoji += emoji_count
                total_contributions += 1
        
        return total_emoji / total_contributions if total_contributions > 0 else 0
    
    def _assess_participation_encouragement(self, discussion_rounds: List[Dict[str, Any]], social_summary: Dict[str, Any]) -> bool:
        """评估社交元素对参与的促进作用"""
        interaction_stats = social_summary.get("interaction_stats", {})
        total_interactions = interaction_stats.get("total_interactions", 0)
        
        # 检查参与度是否随着社交互动增加而提升
        engagement_levels = [round_data.get("engagement_level", 0.5) for round_data in discussion_rounds]
        
        if not engagement_levels:
            return False
        
        # 简化检查：有社交互动且参与度较高
        return total_interactions > 0 and sum(engagement_levels) / len(engagement_levels) > 0.6
    
    def _check_casual_tone_maintenance(self, discussion_rounds: List[Dict[str, Any]]) -> bool:
        """检查轻松语调的维持"""
        formal_indicators = ["此外", "因此", "综上所述", "总而言之", "基于以上分析"]
        
        for round_data in discussion_rounds:
            contributions = round_data.get("contributions", [])
            for contribution in contributions:
                content = contribution.get("content", "")
                
                # 检查是否有过于正式的表达
                if any(indicator in content for indicator in formal_indicators):
                    return False
        
        return True
    
    def _assess_atmosphere_comfort(self, result: Dict[str, Any], user_preferences: Dict[str, Any]) -> float:
        """评估氛围舒适度"""
        social_preference = user_preferences.get("social_interaction_preference", "moderate")
        actual_interactions = result.get("social_summary", {}).get("interaction_stats", {}).get("total_interactions", 0)
        
        # 根据用户偏好评估舒适度
        if social_preference == "low":
            return 1.0 if actual_interactions <= 5 else 0.7
        elif social_preference == "high":
            return 1.0 if actual_interactions >= 10 else 0.6
        else:  # moderate
            return 1.0 if 3 <= actual_interactions <= 12 else 0.8
    
    def _assess_content_appropriateness(self, result: Dict[str, Any], user_preferences: Dict[str, Any]) -> float:
        """评估内容适当性"""
        humor_tolerance = user_preferences.get("humor_tolerance", 0.7)
        actual_fun_factor = result.get("metadata", {}).get("fun_factor", 0)
        
        # 检查幽默程度是否符合用户偏好
        if abs(actual_fun_factor - humor_tolerance) <= 0.2:
            return 1.0
        elif abs(actual_fun_factor - humor_tolerance) <= 0.4:
            return 0.7
        else:
            return 0.5
    
    def _assess_interaction_comfort(self, result: Dict[str, Any], user_preferences: Dict[str, Any]) -> float:
        """评估互动舒适度"""
        discussion_style = user_preferences.get("discussion_style", "casual")
        engagement_score = result.get("metadata", {}).get("engagement_score", 0)
        
        # 基于讨论风格偏好评估
        if discussion_style == "gentle":
            return 1.0 if engagement_score >= 0.5 else 0.6
        elif discussion_style == "energetic":
            return 1.0 if engagement_score >= 0.8 else 0.7
        else:  # balanced/casual
            return 1.0 if engagement_score >= 0.6 else 0.8
    
    def _assess_topic_engagement(self, result: Dict[str, Any]) -> float:
        """评估话题参与度"""
        topic_evolution = result.get("topic_evolution", {})
        natural_transitions = topic_evolution.get("natural_transitions", 0)
        topic_drift = topic_evolution.get("topic_drift_score", 0)
        
        # 自然转换多且话题漂移适中表示良好的参与
        if natural_transitions >= 2 and 0.2 <= topic_drift <= 0.6:
            return 1.0
        elif natural_transitions >= 1:
            return 0.8
        else:
            return 0.6
    
    def _estimate_user_satisfaction(self, result: Dict[str, Any], user_preferences: Dict[str, Any]) -> float:
        """估算用户满意度"""
        comfort = self._assess_atmosphere_comfort(result, user_preferences)
        appropriateness = self._assess_content_appropriateness(result, user_preferences)
        interaction = self._assess_interaction_comfort(result, user_preferences)
        engagement = self._assess_topic_engagement(result)
        
        # 综合评分
        return (comfort * 0.3 + appropriateness * 0.25 + interaction * 0.25 + engagement * 0.2)
    
    def _estimate_memory_usage(self, result: Dict[str, Any]) -> float:
        """估算内存使用量（简化）"""
        # 简化的内存估算
        discussion_rounds = len(result.get("discussion_result", {}).get("discussion_rounds", []))
        participants = len(result.get("selected_participants", []))
        social_interactions = result.get("social_summary", {}).get("interaction_stats", {}).get("total_interactions", 0)
        
        # 简化计算
        estimated_memory = discussion_rounds * participants + social_interactions * 0.1
        return estimated_memory
    
    def _assess_energy_level_match(self, discussion_rounds: List[Dict[str, Any]], expected_energy: str) -> bool:
        """评估能量级别匹配"""
        avg_engagement = sum(round_data.get("engagement_level", 0.5) for round_data in discussion_rounds) / len(discussion_rounds) if discussion_rounds else 0.5
        
        if expected_energy == "low":
            return 0.3 <= avg_engagement <= 0.7
        elif expected_energy == "high":
            return avg_engagement >= 0.7
        else:  # medium
            return 0.5 <= avg_engagement <= 0.8
    
    def _assess_humor_level_match(self, discussion_rounds: List[Dict[str, Any]], expected_humor: float) -> bool:
        """评估幽默程度匹配"""
        humor_indicators = ["😂", "哈哈", "好笑", "有趣", "搞笑"]
        total_humor = 0
        total_content = 0
        
        for round_data in discussion_rounds:
            contributions = round_data.get("contributions", [])
            for contribution in contributions:
                content = contribution.get("content", "")
                humor_count = sum(1 for indicator in humor_indicators if indicator in content)
                total_humor += humor_count
                total_content += 1
        
        actual_humor_ratio = total_humor / total_content if total_content > 0 else 0
        expected_ratio = expected_humor * 0.3
        
        return abs(actual_humor_ratio - expected_ratio) <= 0.2
    
    def _assess_emotional_tone(self, discussion_rounds: List[Dict[str, Any]]) -> str:
        """评估情感语调"""
        positive_indicators = ["开心", "高兴", "棒", "好", "喜欢", "😊", "👍"]
        negative_indicators = ["难过", "糟糕", "不好", "失望", "😢"]
        
        positive_count = 0
        negative_count = 0
        
        for round_data in discussion_rounds:
            contributions = round_data.get("contributions", [])
            for contribution in contributions:
                content = contribution.get("content", "")
                positive_count += sum(1 for indicator in positive_indicators if indicator in content)
                negative_count += sum(1 for indicator in negative_indicators if indicator in content)
        
        if positive_count > negative_count * 2:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _assess_participant_comfort_level(self, discussion_rounds: List[Dict[str, Any]]) -> float:
        """评估参与者舒适度"""
        comfort_indicators = ["我觉得", "我想", "我认为", "个人认为"]
        total_comfort_expressions = 0
        total_contributions = 0
        
        for round_data in discussion_rounds:
            contributions = round_data.get("contributions", [])
            for contribution in contributions:
                content = contribution.get("content", "")
                comfort_count = sum(1 for indicator in comfort_indicators if indicator in content)
                total_comfort_expressions += comfort_count
                total_contributions += 1
        
        return total_comfort_expressions / total_contributions if total_contributions > 0 else 0.5
    
    def _assess_conversation_naturalness(self, discussion_rounds: List[Dict[str, Any]]) -> float:
        """评估对话自然性"""
        natural_indicators = ["对了", "是啊", "确实", "我也是", "哈哈"]
        total_natural_expressions = 0
        total_contributions = 0
        
        for round_data in discussion_rounds:
            contributions = round_data.get("contributions", [])
            for contribution in contributions:
                content = contribution.get("content", "")
                natural_count = sum(1 for indicator in natural_indicators if indicator in content)
                total_natural_expressions += natural_count
                total_contributions += 1
        
        return min(total_natural_expressions / total_contributions if total_contributions > 0 else 0.5, 1.0)
    
    def _calculate_atmosphere_score(self, assessment: Dict[str, Any], expected_atmosphere: str) -> float:
        """计算氛围评分"""
        base_score = 0.0
        
        # 基础评分
        if assessment.get("energy_level_match", False):
            base_score += 0.3
        if assessment.get("humor_appropriateness", False):
            base_score += 0.2
        
        # 情感语调评分
        emotional_tone = assessment.get("emotional_tone", "neutral")
        if expected_atmosphere == "relaxed" and emotional_tone in ["positive", "neutral"]:
            base_score += 0.2
        elif expected_atmosphere == "energetic" and emotional_tone == "positive":
            base_score += 0.2
        elif expected_atmosphere == "supportive" and emotional_tone == "positive":
            base_score += 0.2
        
        # 舒适度和自然性
        comfort_level = assessment.get("participant_comfort", 0.5)
        naturalness = assessment.get("conversation_naturalness", 0.5)
        
        base_score += comfort_level * 0.15
        base_score += naturalness * 0.15
        
        return min(base_score, 1.0)
    
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
            recommendations.append("所有测试通过，轻松讨论场景质量符合V0.2.7要求")
        
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
                "naturalness_and_fun": self.test_results.get("自然性和趣味性测试", {}).get("success", False),
                "topic_transition": self.test_results.get("话题转换机制测试", {}).get("success", False),
                "social_interactions": self.test_results.get("社交互动功能测试", {}).get("success", False),
                "user_experience": self.test_results.get("用户体验流程测试", {}).get("success", False),
                "performance_stability": self.test_results.get("性能和稳定性测试", {}).get("success", False),
                "atmosphere_creation": self.test_results.get("氛围营造能力测试", {}).get("success", False)
            }
        }
        
        # 保存报告
        await self.save_report(report)
        
        return report
    
    async def save_report(self, report: Dict[str, Any]):
        """保存质量保证报告"""
        try:
            report_path = Path("v0_2_7_casual_discussion_quality_report.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"质量保证报告已保存: {report_path}")
        except Exception as e:
            logger.error(f"报告保存失败: {e}")


async def main():
    """执行V0.2.7轻松讨论场景质量保证"""
    qa = CasualDiscussionQualityAssurance()
    
    try:
        final_report = await qa.run_all_tests()
        
        print("\n" + "=" * 80)
        print("📊 V0.2.7 轻松讨论场景质量保证报告")
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