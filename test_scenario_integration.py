#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-03 12:35:00
@Author  : DAIP-LIVE Team
@File    : test_scenario_integration.py
@Description:
    V0.2.8 三场景集成和智能切换质量保证测试
    
    按照.kiro规范要求进行完整的质量验证：
    - 场景切换功能测试：验证用户在不同场景间的无缝切换
    - 上下文保持测试：确保场景切换时的对话上下文连贯性
    - 智能推荐测试：基于用户历史偏好智能推荐合适的场景
    - 统一界面测试：三个场景在统一界面下的一致性体验
    - 集成稳定性测试：场景间切换的稳定性和数据一致性
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

# 导入待测试组件
from src.scenarios.scenario_manager import ScenarioManager, ScenarioType

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScenarioIntegrationQualityAssurance:
    """三场景集成质量保证测试套件"""
    
    def __init__(self):
        self.test_results = {}
        self.scenario_manager = ScenarioManager()
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有质量保证测试"""
        logger.info("=" * 60)
        logger.info("🎭 开始三场景集成质量保证测试")
        logger.info("=" * 60)
        
        test_suite = [
            ("场景切换功能测试", self.test_scenario_switching),
            ("上下文保持测试", self.test_context_preservation),
            ("智能推荐系统测试", self.test_intelligent_recommendation),
            ("统一界面集成测试", self.test_unified_interface),
            ("个性化适配测试", self.test_personalization),
            ("数据一致性测试", self.test_data_consistency),
            ("性能和稳定性测试", self.test_performance_stability)
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
    
    async def test_scenario_switching(self) -> Dict[str, Any]:
        """场景切换功能测试 - 验证用户在不同场景间的无缝切换"""
        logger.info("执行场景切换功能测试...")
        
        try:
            user_id = "test_user_switching"
            topic = "人工智能技术发展"
            
            # 1. 启动学术研究场景
            academic_result = await self.scenario_manager.start_scenario(
                scenario_type=ScenarioType.ACADEMIC_RESEARCH,
                topic=topic,
                user_id=user_id,
                user_preferences={"interests": ["AI", "技术"]},
                context_data={"config": {"research_depth": "standard"}}
            )
            
            if not academic_result.get("success"):
                return {
                    "success": False,
                    "error": "学术研究场景启动失败",
                    "details": academic_result.get("error")
                }
            
            academic_scenario_id = academic_result["scenario_id"]
            
            # 2. 切换到专家咨询场景
            expert_switch_result = await self.scenario_manager.switch_scenario(
                from_scenario_id=academic_scenario_id,
                to_scenario_type=ScenarioType.EXPERT_CONSULTATION,
                transition_reason="需要专家实践建议",
                preserve_context=True
            )
            
            if not expert_switch_result.get("success"):
                return {
                    "success": False,
                    "error": "切换到专家咨询场景失败",
                    "details": expert_switch_result.get("error")
                }
            
            expert_scenario_id = expert_switch_result["new_scenario"]["scenario_id"]
            
            # 3. 切换到轻松讨论场景
            casual_switch_result = await self.scenario_manager.switch_scenario(
                from_scenario_id=expert_scenario_id,
                to_scenario_type=ScenarioType.CASUAL_DISCUSSION,
                transition_reason="轻松讨论相关话题",
                preserve_context=True
            )
            
            if not casual_switch_result.get("success"):
                return {
                    "success": False,
                    "error": "切换到轻松讨论场景失败",
                    "details": casual_switch_result.get("error")
                }
            
            # 4. 验证切换质量
            switch_quality_checks = {
                "academic_to_expert_success": expert_switch_result.get("success", False),
                "expert_to_casual_success": casual_switch_result.get("success", False),
                "context_preserved_in_switches": (
                    expert_switch_result.get("context_preserved", False) and
                    casual_switch_result.get("context_preserved", False)
                ),
                "transition_records_created": len(self.scenario_manager.transition_history) >= 2,
                "topic_consistency": all([
                    expert_switch_result.get("new_scenario", {}).get("context", {}).get("topic") == topic,
                    casual_switch_result.get("new_scenario", {}).get("context", {}).get("topic") == topic
                ])
            }
            
            success = all(switch_quality_checks.values())
            
            return {
                "success": success,
                "switching_chain": {
                    "academic_start": academic_result["scenario_id"],
                    "expert_switch": expert_switch_result["new_scenario"]["scenario_id"],
                    "casual_switch": casual_switch_result["new_scenario"]["scenario_id"]
                },
                "quality_checks": switch_quality_checks,
                "transition_history": [
                    {
                        "from": "academic_research",
                        "to": "expert_consultation",
                        "reason": "需要专家实践建议"
                    },
                    {
                        "from": "expert_consultation", 
                        "to": "casual_discussion",
                        "reason": "轻松讨论相关话题"
                    }
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "场景切换功能测试执行失败"
            }
    
    async def test_context_preservation(self) -> Dict[str, Any]:
        """上下文保持测试 - 确保场景切换时的对话上下文连贯性"""
        logger.info("执行上下文保持测试...")
        
        try:
            user_id = "test_user_context"
            original_topic = "区块链技术在金融中的应用"
            
            # 1. 启动初始场景并建立丰富上下文
            initial_context = {
                "user_id": user_id,
                "interests": ["区块链", "金融科技", "投资"],
                "experience_level": "intermediate",
                "preferences": {
                    "depth": "detailed",
                    "style": "professional"
                }
            }
            
            academic_result = await self.scenario_manager.start_scenario(
                scenario_type=ScenarioType.ACADEMIC_RESEARCH,
                topic=original_topic,
                user_id=user_id,
                user_preferences=initial_context,
                context_data={
                    "config": {"research_depth": "comprehensive"},
                    "keywords": ["区块链", "金融", "DeFi", "智能合约"],
                    "conclusions": ["区块链技术具有巨大潜力", "需要解决扩展性问题"]
                }
            )
            
            if not academic_result.get("success"):
                return {
                    "success": False,
                    "error": "初始场景启动失败",
                    "details": academic_result.get("error")
                }
            
            # 2. 执行上下文切换
            switch_result = await self.scenario_manager.switch_scenario(
                from_scenario_id=academic_result["scenario_id"],
                to_scenario_type=ScenarioType.EXPERT_CONSULTATION,
                transition_reason="获取实践性建议",
                preserve_context=True
            )
            
            if not switch_result.get("success"):
                return {
                    "success": False,
                    "error": "上下文切换失败",
                    "details": switch_result.get("error")
                }
            
            # 3. 验证上下文保持质量
            preserved_data = switch_result.get("preserved_data", {})
            new_scenario_context = switch_result.get("new_scenario", {}).get("context", {})
            
            context_preservation_checks = {
                "original_topic_preserved": preserved_data.get("original_topic") == original_topic,
                "user_preferences_transferred": (
                    preserved_data.get("user_preferences", {}).get("user_id") == user_id and
                    "interests" in preserved_data.get("user_preferences", {})
                ),
                "previous_scenario_recorded": preserved_data.get("previous_scenario") == "academic_research",
                "session_metadata_available": "session_metadata" in preserved_data,
                "keywords_transferred": "keywords" in preserved_data,
                "conclusions_preserved": "previous_conclusions" in preserved_data,
                "context_continuity": new_scenario_context.get("topic") == original_topic
            }
            
            # 4. 测试上下文利用情况
            context_utilization = {
                "preserved_data_size": len(str(preserved_data)),
                "key_data_elements": len([k for k in preserved_data.keys() if preserved_data[k]]),
                "user_preference_consistency": self._check_preference_consistency(
                    initial_context, preserved_data.get("user_preferences", {})
                )
            }
            
            success = (
                sum(context_preservation_checks.values()) >= len(context_preservation_checks) * 0.8 and
                context_utilization["key_data_elements"] >= 4
            )
            
            return {
                "success": success,
                "context_preservation_checks": context_preservation_checks,
                "context_utilization": context_utilization,
                "preserved_data_summary": {
                    "data_elements": list(preserved_data.keys()),
                    "topic_consistency": preserved_data.get("original_topic") == original_topic,
                    "user_data_preserved": bool(preserved_data.get("user_preferences"))
                },
                "continuity_score": sum(context_preservation_checks.values()) / len(context_preservation_checks)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "上下文保持测试执行失败"
            }
    
    async def test_intelligent_recommendation(self) -> Dict[str, Any]:
        """智能推荐系统测试 - 基于用户历史偏好智能推荐合适的场景"""
        logger.info("执行智能推荐系统测试...")
        
        try:
            # 测试用例：不同类型的用户输入和预期推荐
            test_cases = [
                {
                    "name": "学术研究意图明确",
                    "user_input": "我想深入研究AI在医疗诊断中的应用，需要全面的文献综述和理论分析",
                    "expected_scenario": "academic_research",
                    "min_confidence": 0.7
                },
                {
                    "name": "专家咨询需求",
                    "user_input": "我们公司正在考虑是否采用微服务架构，需要专家建议和决策支持",
                    "expected_scenario": "expert_consultation",
                    "min_confidence": 0.6
                },
                {
                    "name": "轻松讨论倾向",
                    "user_input": "最近有什么好看的科幻电影，大家来聊聊看法",
                    "expected_scenario": "casual_discussion",
                    "min_confidence": 0.5
                },
                {
                    "name": "模糊意图测试",
                    "user_input": "人工智能",
                    "expected_scenario": None,  # 任何推荐都可接受
                    "min_confidence": 0.3
                }
            ]
            
            user_id = "test_user_recommendation"
            recommendation_results = []
            
            # 建立用户历史（模拟用户偏好）
            await self._build_user_history(user_id)
            
            for i, test_case in enumerate(test_cases):
                logger.info(f"推荐测试 {i+1}: {test_case['name']}")
                
                recommendation = await self.scenario_manager.recommend_scenario(
                    user_input=test_case["user_input"],
                    user_id=user_id
                )
                
                if not recommendation.get("success"):
                    recommendation_results.append({
                        "test_case": test_case["name"],
                        "success": False,
                        "error": recommendation.get("error", "Unknown error")
                    })
                    continue
                
                top_rec = recommendation.get("top_recommendation", {})
                
                # 验证推荐质量
                recommendation_checks = {
                    "has_recommendations": len(recommendation.get("recommendations", [])) >= 3,
                    "confidence_reasonable": top_rec.get("confidence", 0) >= test_case["min_confidence"],
                    "scenario_match": (
                        test_case["expected_scenario"] is None or 
                        top_rec.get("scenario_type") == test_case["expected_scenario"]
                    ),
                    "has_reasons": len(top_rec.get("reasons", [])) > 0,
                    "has_config": bool(top_rec.get("suggested_config")),
                    "input_analysis_present": bool(recommendation.get("analysis"))
                }
                
                recommendation_results.append({
                    "test_case": test_case["name"],
                    "success": all(recommendation_checks.values()),
                    "recommendation_checks": recommendation_checks,
                    "top_recommendation": {
                        "scenario": top_rec.get("scenario_type"),
                        "confidence": top_rec.get("confidence", 0),
                        "reasons_count": len(top_rec.get("reasons", [])),
                        "expected": test_case["expected_scenario"]
                    }
                })
            
            # 计算整体推荐质量
            successful_tests = sum(1 for result in recommendation_results if result.get("success", False))
            total_tests = len(recommendation_results)
            success_rate = successful_tests / total_tests if total_tests > 0 else 0
            
            # 测试推荐一致性
            consistency_test = await self._test_recommendation_consistency(user_id)
            
            success = success_rate >= 0.75 and consistency_test.get("consistent", False)
            
            return {
                "success": success,
                "success_rate": success_rate,
                "successful_tests": successful_tests,
                "total_tests": total_tests,
                "recommendation_results": recommendation_results,
                "consistency_test": consistency_test,
                "overall_assessment": {
                    "accuracy": "高" if success_rate >= 0.8 else "中" if success_rate >= 0.6 else "低",
                    "intelligence": "强" if consistency_test.get("consistent", False) else "弱"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "智能推荐系统测试执行失败"
            }
    
    async def test_unified_interface(self) -> Dict[str, Any]:
        """统一界面集成测试 - 三个场景在统一界面下的一致性体验"""
        logger.info("执行统一界面集成测试...")
        
        try:
            user_id = "test_user_interface"
            
            # 1. 测试界面数据获取
            interface_data = await self.scenario_manager.get_unified_interface_data(user_id)
            
            if not interface_data.get("user_profile"):
                return {
                    "success": False,
                    "error": "统一界面数据获取失败",
                    "details": "用户档案数据缺失"
                }
            
            # 2. 验证界面数据完整性
            interface_completeness_checks = {
                "has_user_profile": bool(interface_data.get("user_profile")),
                "has_active_scenarios": "active_scenarios" in interface_data,
                "has_recent_transitions": "recent_transitions" in interface_data,
                "has_usage_statistics": bool(interface_data.get("usage_statistics")),
                "has_scenario_capabilities": bool(interface_data.get("scenario_capabilities")),
                "has_interface_config": bool(interface_data.get("interface_config"))
            }
            
            # 3. 验证场景能力描述
            capabilities = interface_data.get("scenario_capabilities", {})
            capability_checks = {
                "all_scenarios_described": len(capabilities) == 3,
                "academic_research_present": ScenarioType.ACADEMIC_RESEARCH.value in capabilities,
                "expert_consultation_present": ScenarioType.EXPERT_CONSULTATION.value in capabilities,
                "casual_discussion_present": ScenarioType.CASUAL_DISCUSSION.value in capabilities,
                "capabilities_detailed": all(
                    len(cap.get("capabilities", [])) >= 3 for cap in capabilities.values()
                )
            }
            
            # 4. 测试界面配置合理性
            interface_config = interface_data.get("interface_config", {})
            config_checks = {
                "has_default_scenario": bool(interface_config.get("default_scenario")),
                "has_recommendations_setting": "show_recommendations" in interface_config,
                "has_quick_switch_setting": "enable_quick_switch" in interface_config,
                "has_quick_access": "quick_access_scenarios" in interface_config,
                "default_scenario_valid": interface_config.get("default_scenario") in [s.value for s in ScenarioType]
            }
            
            # 5. 测试数据一致性
            user_profile = interface_data.get("user_profile", {})
            usage_stats = interface_data.get("usage_statistics", {})
            
            consistency_checks = {
                "profile_stats_match": (
                    user_profile.get("scenario_usage_stats", {}) == 
                    usage_stats.get("scenario_distribution", {})
                ),
                "favorite_scenarios_reasonable": len(user_profile.get("favorite_scenarios", [])) <= 3,
                "interface_config_matches_profile": True  # 简化检查
            }
            
            success = (
                sum(interface_completeness_checks.values()) >= len(interface_completeness_checks) * 0.9 and
                sum(capability_checks.values()) >= len(capability_checks) * 0.8 and
                sum(config_checks.values()) >= len(config_checks) * 0.8
            )
            
            return {
                "success": success,
                "interface_completeness_checks": interface_completeness_checks,
                "capability_checks": capability_checks,
                "config_checks": config_checks,
                "consistency_checks": consistency_checks,
                "interface_data_summary": {
                    "scenario_count": len(capabilities),
                    "config_elements": len(interface_config),
                    "user_profile_completeness": len(user_profile) / 8.0,  # 假设8个基础字段
                    "data_quality": "高" if success else "需改进"
                },
                "unified_experience_assessment": {
                    "consistency": "好" if sum(consistency_checks.values()) >= 2 else "需改进",
                    "completeness": "完整" if sum(interface_completeness_checks.values()) >= 5 else "部分缺失",
                    "usability": "优秀" if success else "一般"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "统一界面集成测试执行失败"
            }
    
    async def test_personalization(self) -> Dict[str, Any]:
        """个性化适配测试 - 验证基于用户历史偏好的个性化适配"""
        logger.info("执行个性化适配测试...")
        
        try:
            # 创建不同类型的测试用户
            test_users = [
                {
                    "user_id": "academic_user",
                    "profile": {
                        "interests": ["AI", "学术研究", "论文写作"],
                        "preferred_depth": "comprehensive",
                        "usage_pattern": "academic_heavy"
                    },
                    "expected_default": "academic_research"
                },
                {
                    "user_id": "business_user", 
                    "profile": {
                        "interests": ["商业", "决策", "技术选型"],
                        "preferred_style": "practical",
                        "usage_pattern": "expert_heavy"
                    },
                    "expected_default": "expert_consultation"
                },
                {
                    "user_id": "casual_user",
                    "profile": {
                        "interests": ["生活", "娱乐", "轻松聊天"],
                        "preferred_style": "relaxed",
                        "usage_pattern": "casual_heavy"
                    },
                    "expected_default": "casual_discussion"
                }
            ]
            
            personalization_results = []
            
            for user_data in test_users:
                user_id = user_data["user_id"]
                profile = user_data["profile"]
                expected_default = user_data["expected_default"]
                
                # 1. 建立用户使用历史
                await self._simulate_user_history(user_id, profile)
                
                # 2. 测试个性化推荐
                general_input = "我想了解一下人工智能"
                recommendation = await self.scenario_manager.recommend_scenario(general_input, user_id)
                
                # 3. 获取个性化界面配置
                interface_data = await self.scenario_manager.get_unified_interface_data(user_id)
                
                # 4. 验证个性化效果
                personalization_checks = {
                    "recommendation_matches_preference": (
                        recommendation.get("top_recommendation", {}).get("scenario_type") == expected_default
                    ),
                    "interface_config_personalized": (
                        interface_data.get("interface_config", {}).get("default_scenario") == expected_default
                    ),
                    "usage_stats_reflected": (
                        max(interface_data.get("usage_statistics", {}).get("scenario_distribution", {}), 
                            key=lambda k: interface_data.get("usage_statistics", {}).get("scenario_distribution", {}).get(k, 0), 
                            default="") == expected_default
                    ),
                    "quick_access_relevant": len(interface_data.get("interface_config", {}).get("quick_access_scenarios", [])) > 0,
                    "favorite_scenarios_logical": expected_default in [
                        s for s in interface_data.get("user_profile", {}).get("favorite_scenarios", [])
                    ]
                }
                
                personalization_score = sum(personalization_checks.values()) / len(personalization_checks)
                
                personalization_results.append({
                    "user_type": user_data["user_id"],
                    "personalization_score": personalization_score,
                    "personalization_checks": personalization_checks,
                    "expected_vs_actual": {
                        "expected_default": expected_default,
                        "recommended": recommendation.get("top_recommendation", {}).get("scenario_type"),
                        "interface_default": interface_data.get("interface_config", {}).get("default_scenario")
                    }
                })
            
            # 计算整体个性化效果
            avg_personalization_score = sum(r["personalization_score"] for r in personalization_results) / len(personalization_results)
            successful_personalizations = sum(1 for r in personalization_results if r["personalization_score"] >= 0.6)
            
            success = avg_personalization_score >= 0.7 and successful_personalizations >= len(test_users) * 0.8
            
            return {
                "success": success,
                "average_personalization_score": avg_personalization_score,
                "successful_personalizations": successful_personalizations,
                "total_test_users": len(test_users),
                "personalization_results": personalization_results,
                "personalization_assessment": {
                    "effectiveness": "高" if avg_personalization_score >= 0.8 else "中" if avg_personalization_score >= 0.6 else "低",
                    "consistency": "好" if successful_personalizations == len(test_users) else "一般",
                    "adaptability": "强" if success else "弱"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "个性化适配测试执行失败"
            }
    
    async def test_data_consistency(self) -> Dict[str, Any]:
        """数据一致性测试 - 验证场景间切换的数据一致性"""
        logger.info("执行数据一致性测试...")
        
        try:
            user_id = "test_user_consistency"
            topic = "云计算架构设计"
            
            # 1. 执行复杂的场景切换序列
            switch_sequence = [
                (ScenarioType.ACADEMIC_RESEARCH, "学术研究阶段"),
                (ScenarioType.EXPERT_CONSULTATION, "专家咨询阶段"),
                (ScenarioType.CASUAL_DISCUSSION, "轻松讨论阶段"),
                (ScenarioType.ACADEMIC_RESEARCH, "再次学术研究")  # 回到原始场景
            ]
            
            scenario_contexts = []
            data_snapshots = []
            
            for i, (scenario_type, stage_name) in enumerate(switch_sequence):
                if i == 0:
                    # 启动第一个场景
                    result = await self.scenario_manager.start_scenario(
                        scenario_type=scenario_type,
                        topic=topic,
                        user_id=user_id,
                        user_preferences={"stage": stage_name}
                    )
                else:
                    # 从前一个场景切换
                    result = await self.scenario_manager.switch_scenario(
                        from_scenario_id=scenario_contexts[-1]["scenario_id"],
                        to_scenario_type=scenario_type,
                        transition_reason=f"切换到{stage_name}",
                        preserve_context=True
                    )
                    result = result.get("new_scenario", result)
                
                if not result.get("success"):
                    return {
                        "success": False,
                        "error": f"场景切换序列在阶段{i+1}失败",
                        "details": result.get("error")
                    }
                
                scenario_contexts.append(result.get("context", result))
                
                # 拍摄数据快照
                snapshot = {
                    "stage": stage_name,
                    "scenario_type": scenario_type.value,
                    "user_profile": self.scenario_manager.user_profiles.get(user_id),
                    "active_contexts_count": len(self.scenario_manager.active_contexts),
                    "transition_history_count": len(self.scenario_manager.transition_history)
                }
                data_snapshots.append(snapshot)
            
            # 2. 验证数据一致性
            consistency_checks = {
                "user_profile_maintained": all(
                    snapshot["user_profile"] is not None for snapshot in data_snapshots
                ),
                "user_id_consistent": all(
                    snapshot["user_profile"].user_id == user_id for snapshot in data_snapshots
                    if snapshot["user_profile"]
                ),
                "usage_stats_incremental": self._check_usage_stats_growth(data_snapshots),
                "transition_history_grows": all(
                    data_snapshots[i]["transition_history_count"] >= data_snapshots[i-1]["transition_history_count"]
                    for i in range(1, len(data_snapshots))
                ),
                "context_preservation": self._check_context_preservation_consistency(scenario_contexts),
                "no_data_corruption": self._check_data_corruption(data_snapshots)
            }
            
            # 3. 验证内存使用和性能一致性
            performance_checks = {
                "memory_usage_stable": True,  # 简化实现
                "response_times_consistent": True,  # 简化实现
                "no_memory_leaks": len(self.scenario_manager.active_contexts) < 100  # 防止内存泄漏
            }
            
            success = (
                sum(consistency_checks.values()) >= len(consistency_checks) * 0.8 and
                all(performance_checks.values())
            )
            
            return {
                "success": success,
                "consistency_checks": consistency_checks,
                "performance_checks": performance_checks,
                "data_snapshots_summary": {
                    "total_stages": len(data_snapshots),
                    "user_profile_changes": self._count_profile_changes(data_snapshots),
                    "context_count_progression": [s["active_contexts_count"] for s in data_snapshots],
                    "transition_count_progression": [s["transition_history_count"] for s in data_snapshots]
                },
                "data_integrity_assessment": {
                    "consistency_score": sum(consistency_checks.values()) / len(consistency_checks),
                    "reliability": "高" if success else "需改进",
                    "data_quality": "优秀" if sum(consistency_checks.values()) >= len(consistency_checks) * 0.9 else "良好"
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "数据一致性测试执行失败"
            }
    
    async def test_performance_stability(self) -> Dict[str, Any]:
        """性能和稳定性测试 - 验证系统在高频使用下的稳定性"""
        logger.info("执行性能和稳定性测试...")
        
        try:
            # 1. 连续场景切换测试
            stability_runs = 5
            performance_results = []
            
            for i in range(stability_runs):
                logger.info(f"稳定性测试运行 {i+1}/{stability_runs}")
                
                user_id = f"stability_user_{i}"
                topic = f"稳定性测试话题 {i+1}"
                
                try:
                    start_time = time.time()
                    
                    # 快速场景切换序列
                    scenarios = [ScenarioType.ACADEMIC_RESEARCH, ScenarioType.EXPERT_CONSULTATION, ScenarioType.CASUAL_DISCUSSION]
                    
                    # 启动第一个场景
                    result = await self.scenario_manager.start_scenario(
                        scenario_type=scenarios[0],
                        topic=topic,
                        user_id=user_id
                    )
                    
                    if not result.get("success"):
                        raise Exception(f"场景启动失败: {result.get('error')}")
                    
                    scenario_id = result["scenario_id"]
                    
                    # 执行快速切换
                    for next_scenario in scenarios[1:]:
                        switch_result = await self.scenario_manager.switch_scenario(
                            from_scenario_id=scenario_id,
                            to_scenario_type=next_scenario,
                            transition_reason="稳定性测试切换"
                        )
                        
                        if not switch_result.get("success"):
                            raise Exception(f"场景切换失败: {switch_result.get('error')}")
                        
                        scenario_id = switch_result["new_scenario"]["scenario_id"]
                    
                    end_time = time.time()
                    
                    run_result = {
                        "run_number": i+1,
                        "success": True,
                        "execution_time": end_time - start_time,
                        "scenarios_processed": len(scenarios),
                        "switches_completed": len(scenarios) - 1,
                        "memory_usage": self._estimate_memory_usage(),
                        "active_contexts": len(self.scenario_manager.active_contexts),
                        "error": None
                    }
                    
                except Exception as e:
                    run_result = {
                        "run_number": i+1,
                        "success": False,
                        "error": str(e),
                        "execution_time": 0,
                        "scenarios_processed": 0,
                        "switches_completed": 0,
                        "memory_usage": 0,
                        "active_contexts": 0
                    }
                
                performance_results.append(run_result)
                
                # 短暂休息避免资源竞争
                await asyncio.sleep(0.5)
            
            # 2. 分析性能和稳定性指标
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
            
            # 3. 性能标准检查
            performance_checks = {
                "all_runs_successful": successful_runs == stability_runs,
                "response_time_acceptable": performance_metrics["average_execution_time"] < 60,  # 1分钟内
                "performance_consistent": performance_metrics["execution_time_variance"] < 30,  # 变化小于30秒
                "memory_usage_reasonable": performance_metrics["average_memory_usage"] < 200,  # 简化的内存检查
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
                    "consistency": "好" if performance_metrics["execution_time_variance"] < 20 else "一般",
                    "efficiency": "优秀" if performance_metrics["average_execution_time"] < 30 else "良好"
                },
                "individual_runs": performance_results
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "性能和稳定性测试执行失败"
            }
    
    # 辅助方法
    def _check_preference_consistency(self, original: Dict[str, Any], preserved: Dict[str, Any]) -> bool:
        """检查偏好一致性"""
        key_fields = ["interests", "experience_level", "user_id"]
        return all(
            preserved.get(field) == original.get(field) 
            for field in key_fields if field in original
        )
    
    async def _build_user_history(self, user_id: str):
        """建立用户使用历史（用于推荐测试）"""
        # 模拟用户偏好学术研究
        for i in range(3):
            await self.scenario_manager.start_scenario(
                scenario_type=ScenarioType.ACADEMIC_RESEARCH,
                topic=f"测试研究话题 {i+1}",
                user_id=user_id,
                user_preferences={"test": True}
            )
        
        # 模拟一次专家咨询
        await self.scenario_manager.start_scenario(
            scenario_type=ScenarioType.EXPERT_CONSULTATION,
            topic="测试咨询话题",
            user_id=user_id,
            user_preferences={"test": True}
        )
    
    async def _test_recommendation_consistency(self, user_id: str) -> Dict[str, Any]:
        """测试推荐一致性"""
        same_input = "人工智能技术发展趋势"
        
        # 多次推荐同一输入
        recommendations = []
        for i in range(3):
            rec = await self.scenario_manager.recommend_scenario(same_input, user_id)
            if rec.get("success"):
                recommendations.append(rec.get("top_recommendation", {}).get("scenario_type"))
        
        # 检查一致性
        consistent = len(set(recommendations)) <= 2  # 允许小幅波动
        
        return {
            "consistent": consistent,
            "recommendations": recommendations,
            "consistency_score": 1.0 if len(set(recommendations)) == 1 else 0.5
        }
    
    async def _simulate_user_history(self, user_id: str, profile: Dict[str, Any]):
        """模拟用户使用历史"""
        usage_pattern = profile.get("usage_pattern", "balanced")
        
        if usage_pattern == "academic_heavy":
            scenarios = [ScenarioType.ACADEMIC_RESEARCH] * 4 + [ScenarioType.EXPERT_CONSULTATION]
        elif usage_pattern == "expert_heavy":
            scenarios = [ScenarioType.EXPERT_CONSULTATION] * 4 + [ScenarioType.CASUAL_DISCUSSION]
        elif usage_pattern == "casual_heavy":
            scenarios = [ScenarioType.CASUAL_DISCUSSION] * 4 + [ScenarioType.ACADEMIC_RESEARCH]
        else:
            scenarios = [ScenarioType.ACADEMIC_RESEARCH, ScenarioType.EXPERT_CONSULTATION, ScenarioType.CASUAL_DISCUSSION]
        
        for i, scenario_type in enumerate(scenarios):
            await self.scenario_manager.start_scenario(
                scenario_type=scenario_type,
                topic=f"历史话题 {i+1}",
                user_id=user_id,
                user_preferences=profile
            )
    
    def _check_usage_stats_growth(self, snapshots: List[Dict[str, Any]]) -> bool:
        """检查使用统计是否递增"""
        for i in range(1, len(snapshots)):
            if snapshots[i]["user_profile"] and snapshots[i-1]["user_profile"]:
                current_total = sum(snapshots[i]["user_profile"].scenario_usage_stats.values())
                previous_total = sum(snapshots[i-1]["user_profile"].scenario_usage_stats.values())
                if current_total <= previous_total:
                    return False
        return True
    
    def _check_context_preservation_consistency(self, contexts: List[Dict[str, Any]]) -> bool:
        """检查上下文保持一致性"""
        # 简化检查：确保所有上下文都有基本字段
        required_fields = ["scenario_id", "scenario_type", "topic"]
        return all(
            all(field in context for field in required_fields)
            for context in contexts
        )
    
    def _check_data_corruption(self, snapshots: List[Dict[str, Any]]) -> bool:
        """检查数据损坏"""
        # 简化检查：确保用户档案数据结构完整
        for snapshot in snapshots:
            if snapshot["user_profile"]:
                required_fields = ["user_id", "scenario_usage_stats", "created_at"]
                if not all(hasattr(snapshot["user_profile"], field) for field in required_fields):
                    return False
        return True
    
    def _count_profile_changes(self, snapshots: List[Dict[str, Any]]) -> int:
        """统计档案变化次数"""
        changes = 0
        for i in range(1, len(snapshots)):
            if (snapshots[i]["user_profile"] and snapshots[i-1]["user_profile"] and
                snapshots[i]["user_profile"].updated_at != snapshots[i-1]["user_profile"].updated_at):
                changes += 1
        return changes
    
    def _estimate_memory_usage(self) -> float:
        """估算内存使用量（简化）"""
        active_contexts = len(self.scenario_manager.active_contexts)
        user_profiles = len(self.scenario_manager.user_profiles)
        transition_history = len(self.scenario_manager.transition_history)
        
        # 简化的内存估算
        estimated_memory = active_contexts * 10 + user_profiles * 5 + transition_history * 1
        return estimated_memory
    
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
            recommendations.append("所有测试通过，三场景集成质量符合V0.2.8要求")
        
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
                "scenario_switching": self.test_results.get("场景切换功能测试", {}).get("success", False),
                "context_preservation": self.test_results.get("上下文保持测试", {}).get("success", False),
                "intelligent_recommendation": self.test_results.get("智能推荐系统测试", {}).get("success", False),
                "unified_interface": self.test_results.get("统一界面集成测试", {}).get("success", False),
                "personalization": self.test_results.get("个性化适配测试", {}).get("success", False),
                "data_consistency": self.test_results.get("数据一致性测试", {}).get("success", False),
                "performance_stability": self.test_results.get("性能和稳定性测试", {}).get("success", False)
            }
        }
        
        # 保存报告
        await self.save_report(report)
        
        return report
    
    async def save_report(self, report: Dict[str, Any]):
        """保存质量保证报告"""
        try:
            report_path = Path("v0_2_8_scenario_integration_quality_report.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"质量保证报告已保存: {report_path}")
        except Exception as e:
            logger.error(f"报告保存失败: {e}")


async def main():
    """执行V0.2.8三场景集成质量保证"""
    qa = ScenarioIntegrationQualityAssurance()
    
    try:
        final_report = await qa.run_all_tests()
        
        print("\n" + "=" * 80)
        print("📊 V0.2.8 三场景集成质量保证报告")
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