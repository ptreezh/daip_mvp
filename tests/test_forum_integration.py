#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 15:00:00
@Author  : DAIP-LIVE Team
@File    : test_forum_integration.py
@Description:
    Forum模式集成测试 - 完整的端到端测试场景
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from src.core_services.forum_service import forum_service, ForumSession
from src.core_services.forum_service import DebateOrchestrator, UserInterventionManager, ConsensusTracker
from src.api.routers.forum import forum_router
from frontend.components.forum_chat_interface import ForumChatInterface
from frontend.services.forum_websocket_integration import forum_websocket_integration
from frontend.services.dual_entrance_websocket_manager import dual_entrance_websocket_manager


class TestForumIntegration:
    """Forum集成测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        self.test_topic = "量子计算的商业应用前景"
        self.test_user_id = "integration_test_user"
        self.test_session_id = "integration_test_session_123"
        
        # 创建测试会话
        self.test_session = ForumSession(
            session_id=self.test_session_id,
            topic=self.test_topic,
            start_time=datetime.now(),
            active_agents=["technical_expert", "business_analyst", "research_scientist"],
            status="active"
        )
    
    async def test_forum_session_lifecycle(self):
        """测试Forum会话完整生命周期"""
        try:
            # 1. 创建会话
            session = await forum_service.start_forum_session(
                topic=self.test_topic,
                user_id=self.test_user_id
            )
            
            assert session.session_id is not None
            assert session.topic == self.test_topic
            assert session.status == "active"
            assert len(session.active_agents) > 0
            
            session_id = session.session_id
            
            # 2. 获取会话上下文
            context = await forum_service.get_session_context(session_id)
            assert context is not None
            assert context["session_id"] == session_id
            assert context["topic"] == self.test_topic
            
            # 3. 处理用户干预
            user_message = {
                "content": "我认为量子计算在金融领域有巨大潜力",
                "intent": "comment"
            }
            
            intervention_result = await forum_service.handle_user_intervention(
                session_id, user_message
            )
            
            assert intervention_result["status"] == "integrated"
            assert "optimized_input" in intervention_result
            
            # 4. 暂停会话
            pause_result = await forum_service.pause_session(session_id)
            assert pause_result is True
            
            # 5. 恢复会话
            resume_result = await forum_service.resume_session(session_id)
            assert resume_result is True
            
            # 6. 结束会话
            end_result = await forum_service.end_session(session_id)
            assert end_result is not None
            assert end_result["session_id"] == session_id
            
            print(f"✓ Forum会话生命周期测试通过: {session_id}")
            
        except Exception as e:
            print(f"✗ Forum会话生命周期测试失败: {e}")
            raise
    
    async def test_multi_agent_collaboration(self):
        """测试多智能体协作"""
        try:
            # 创建会话
            session = await forum_service.start_forum_session(
                topic="人工智能伦理问题",
                user_id=self.test_user_id
            )
            
            session_id = session.session_id
            
            # 模拟多轮讨论
            interventions = [
                {"content": "AI决策的透明性很重要", "intent": "comment"},
                {"content": "如何平衡创新与监管？", "intent": "question"},
                {"content": "建议建立AI伦理审查委员会", "intent": "suggestion"}
            ]
            
            for i, intervention in enumerate(interventions):
                result = await forum_service.handle_user_intervention(
                    session_id, intervention
                )
                
                assert result["status"] == "integrated"
                
                # 验证共识度变化
                context = await forum_service.get_session_context(session_id)
                assert context["consensus_level"] >= 0.0
                assert context["consensus_level"] <= 1.0
                
                # 模拟一些延迟
                await asyncio.sleep(0.1)
            
            # 验证最终状态
            final_context = await forum_service.get_session_context(session_id)
            assert final_context["user_intervention_count"] == len(interventions)
            assert final_context["message_count"] >= len(interventions)
            
            # 结束会话
            await forum_service.end_session(session_id)
            
            print(f"✓ 多智能体协作测试通过: {session_id}")
            
        except Exception as e:
            print(f"✗ 多智能体协作测试失败: {e}")
            raise
    
    async def test_user_intervention_optimization(self):
        """测试用户干预优化"""
        try:
            # 测试不同意图的优化
            test_cases = [
                {
                    "input": "量子计算",
                    "intent": "question",
                    "expected_keywords": ["量子计算", "问题"]
                },
                {
                    "input": "应该加强监管",
                    "intent": "suggestion", 
                    "expected_keywords": ["建议", "加强", "监管"]
                },
                {
                    "input": "这个观点不对",
                    "intent": "correction",
                    "expected_keywords": ["纠正", "准确"]
                },
                {
                    "input": "我同意这个观点",
                    "intent": "comment",
                    "expected_keywords": ["同意"]
                }
            ]
            
            for i, test_case in enumerate(test_cases):
                optimized = await forum_service.user_intervention_manager.optimize_input(
                    test_case["input"], test_case["intent"], "测试话题"
                )
                
                assert optimized is not None
                assert isinstance(optimized, str)
                assert len(optimized) > 0
                
                # 验证优化结果包含期望的关键词
                for keyword in test_case["expected_keywords"]:
                    if keyword in ["同意", "建议", "纠正"]:  # 这些关键词应该在优化结果中
                        assert keyword in optimized or any(kw in optimized for kw in test_case["expected_keywords"])
                
                print(f"✓ 用户干预优化测试通过[{i+1}]: {test_case['intent']} -> {optimized[:50]}...")
            
        except Exception as e:
            print(f"✗ 用户干预优化测试失败: {e}")
            raise
    
    async def test_consensus_tracking(self):
        """测试共识跟踪"""
        try:
            # 创建会话
            session = await forum_service.start_forum_session(
                topic="气候变化应对策略",
                user_id=self.test_user_id
            )
            
            session_id = session.session_id
            
            # 模拟消息流
            messages = [
                {"type": "agent", "content": "需要减少碳排放", "sender": "environmental_expert"},
                {"type": "agent", "content": "同意减排很重要", "sender": "policy_analyst"},
                {"type": "user", "content": "支持减排政策", "sender": "user"},
                {"type": "agent", "content": "经济发展也很重要", "sender": "economist"},
                {"type": "agent", "content": "可以平衡发展和环保", "sender": "sustainability_expert"}
            ]
            
            consensus_tracker = forum_service.consensus_tracker
            
            # 处理消息并跟踪共识
            for message in messages:
                await consensus_tracker.update_with_message(session_id, message)
                
                # 验证共识度变化
                consensus_level = await consensus_tracker.get_consensus_level(session_id)
                assert 0.0 <= consensus_level <= 1.0
                
                # 模拟延迟
                await asyncio.sleep(0.05)
            
            # 验证最终共识
            final_consensus = await consensus_tracker.get_final_consensus(session_id)
            assert "consensus_level" in final_consensus
            assert "summary" in final_consensus
            assert "key_arguments" in final_consensus
            
            # 结束会话
            await forum_service.end_session(session_id)
            
            print(f"✓ 共识跟踪测试通过: {session_id}")
            
        except Exception as e:
            print(f"✗ 共识跟踪测试失败: {e}")
            raise
    
    async def test_websocket_integration(self):
        """测试WebSocket集成"""
        try:
            # 初始化WebSocket集成
            await forum_websocket_integration.initialize()
            
            # 创建会话
            session_id = await forum_websocket_integration.start_forum_session(
                topic="远程工作未来趋势",
                user_id=self.test_user_id
            )
            
            assert session_id is not None
            
            # 发送用户干预
            intervention_success = await forum_websocket_integration.send_user_intervention(
                session_id, "远程工作提高了工作效率", "comment"
            )
            
            assert intervention_success is True
            
            # 发送会话控制
            control_success = await forum_websocket_integration.send_session_control(
                session_id, "pause"
            )
            
            assert control_success is True
            
            # 恢复会话
            resume_success = await forum_websocket_integration.send_session_control(
                session_id, "resume"
            )
            
            assert resume_success is True
            
            # 获取连接状态
            status = forum_websocket_integration.get_connection_status()
            assert status["status"] in ["connected", "disconnected"]  # 根据实际环境
            
            print(f"✓ WebSocket集成测试通过: {session_id}")
            
        except Exception as e:
            print(f"✗ WebSocket集成测试失败: {e}")
            raise
    
    async def test_forum_chat_interface(self):
        """测试Forum聊天界面"""
        try:
            # 创建聊天界面实例
            from frontend.services.personal_assistant import PersonalAssistantService
            
            # Mock PersonalAssistantService
            mock_assistant = Mock(spec=PersonalAssistantService)
            
            chat_interface = ForumChatInterface(
                assistant_service=mock_assistant,
                session_id=self.test_session_id
            )
            
            # 验证初始化
            assert chat_interface.session_id == self.test_session_id
            assert len(chat_interface.messages) > 0  # 应该有欢迎消息
            
            # 测试消息渲染
            for message in chat_interface.messages:
                rendered = chat_interface._render_message(message)
                assert rendered is not None
            
            # 测试上下文获取
            context = chat_interface.get_forum_context()
            assert context["session_id"] == self.test_session_id
            assert context["topic"] == ""
            
            # 测试消息历史
            history = chat_interface.get_message_history()
            assert isinstance(history, list)
            assert len(history) > 0
            
            print(f"✓ Forum聊天界面测试通过: {self.test_session_id}")
            
        except Exception as e:
            print(f"✗ Forum聊天界面测试失败: {e}")
            raise
    
    async def test_error_handling(self):
        """测试错误处理"""
        try:
            # 测试不存在的会话
            context = await forum_service.get_session_context("nonexistent_session")
            assert context is None
            
            # 测试无效的用户干预
            with pytest.raises(Exception):
                await forum_service.handle_user_intervention(
                    "nonexistent_session", {"content": "test", "intent": "comment"}
                )
            
            # 测试无效的会话控制
            pause_result = await forum_service.pause_session("nonexistent_session")
            assert pause_result is False
            
            resume_result = await forum_service.resume_session("nonexistent_session")
            assert resume_result is False
            
            end_result = await forum_service.end_session("nonexistent_session")
            assert end_result is None
            
            print("✓ 错误处理测试通过")
            
        except Exception as e:
            print(f"✗ 错误处理测试失败: {e}")
            raise
    
    async def test_performance_scalability(self):
        """测试性能和可扩展性"""
        try:
            # 创建多个并发会话
            concurrent_sessions = 5
            sessions = []
            
            # 创建会话
            create_tasks = []
            for i in range(concurrent_sessions):
                task = forum_service.start_forum_session(
                    topic=f"性能测试话题 {i}",
                    user_id=f"performance_user_{i}"
                )
                create_tasks.append(task)
            
            sessions = await asyncio.gather(*create_tasks)
            assert len(sessions) == concurrent_sessions
            
            session_ids = [s.session_id for s in sessions]
            
            # 并发用户干预
            intervention_tasks = []
            for session_id in session_ids:
                for i in range(3):  # 每个会话3次干预
                    task = forum_service.handle_user_intervention(
                        session_id,
                        {"content": f"并发干预 {i}", "intent": "comment"}
                    )
                    intervention_tasks.append(task)
            
            intervention_results = await asyncio.gather(*intervention_tasks)
            assert len(intervention_results) == concurrent_sessions * 3
            
            # 验证所有会话状态
            context_tasks = []
            for session_id in session_ids:
                task = forum_service.get_session_context(session_id)
                context_tasks.append(task)
            
            contexts = await asyncio.gather(*context_tasks)
            assert len(contexts) == concurrent_sessions
            
            for context in contexts:
                assert context is not None
                assert context["user_intervention_count"] == 3
            
            # 清理会话
            end_tasks = []
            for session_id in session_ids:
                task = forum_service.end_session(session_id)
                end_tasks.append(task)
            
            await asyncio.gather(*end_tasks)
            
            print(f"✓ 性能和可扩展性测试通过: {concurrent_sessions} 个并发会话")
            
        except Exception as e:
            print(f"✗ 性能和可扩展性测试失败: {e}")
            raise


class TestForumScenarios:
    """Forum场景测试"""
    
    async def test_expert_consultation_scenario(self):
        """测试专家咨询场景"""
        try:
            # 模拟专家咨询场景
            session = await forum_service.start_forum_session(
                topic="企业数字化转型策略",
                user_id="business_user"
            )
            
            # 模拟专家讨论
            expert_interventions = [
                {"content": "需要明确转型目标", "intent": "suggestion"},
                {"content": "技术选型很关键", "intent": "comment"},
                {"content": "如何评估ROI？", "intent": "question"},
                {"content": "应该分阶段实施", "intent": "suggestion"}
            ]
            
            for intervention in expert_interventions:
                await forum_service.handle_user_intervention(
                    session.session_id, intervention
                )
                await asyncio.sleep(0.1)
            
            # 验证共识形成
            context = await forum_service.get_session_context(session.session_id)
            assert context["consensus_level"] > 0.3  # 应该有一定共识
            
            await forum_service.end_session(session.session_id)
            
            print("✓ 专家咨询场景测试通过")
            
        except Exception as e:
            print(f"✗ 专家咨询场景测试失败: {e}")
            raise
    
    async def test_academic_research_scenario(self):
        """测试学术研究场景"""
        try:
            # 模拟学术研究场景
            session = await forum_service.start_forum_session(
                topic="机器学习在医疗诊断中的应用",
                user_id="researcher"
            )
            
            # 模拟学术讨论
            academic_interventions = [
                {"content": "数据质量是关键", "intent": "comment"},
                {"content": "需要考虑伦理问题", "intent": "suggestion"},
                {"content": "有哪些相关研究？", "intent": "question"},
                {"content": "建议进行临床试验", "intent": "suggestion"}
            ]
            
            for intervention in academic_interventions:
                await forum_service.handle_user_intervention(
                    session.session_id, intervention
                )
                await asyncio.sleep(0.1)
            
            # 验证讨论深度
            context = await forum_service.get_session_context(session.session_id)
            assert context["message_count"] >= len(academic_interventions)
            
            await forum_service.end_session(session.session_id)
            
            print("✓ 学术研究场景测试通过")
            
        except Exception as e:
            print(f"✗ 学术研究场景测试失败: {e}")
            raise


# 测试运行器
async def run_forum_integration_tests():
    """运行Forum集成测试"""
    print("🚀 开始Forum集成测试...")
    
    test_class = TestForumIntegration()
    scenario_test_class = TestForumScenarios()
    
    # 基础集成测试
    print("\n📋 基础集成测试:")
    await test_class.setup_method()
    await test_class.test_forum_session_lifecycle()
    
    await test_class.setup_method()
    await test_class.test_multi_agent_collaboration()
    
    await test_class.setup_method()
    await test_class.test_user_intervention_optimization()
    
    await test_class.setup_method()
    await test_class.test_consensus_tracking()
    
    await test_class.setup_method()
    await test_class.test_websocket_integration()
    
    await test_class.setup_method()
    await test_class.test_forum_chat_interface()
    
    await test_class.setup_method()
    await test_class.test_error_handling()
    
    await test_class.setup_method()
    await test_class.test_performance_scalability()
    
    # 场景测试
    print("\n🎭 场景测试:")
    await scenario_test_class.test_expert_consultation_scenario()
    await scenario_test_class.test_academic_research_scenario()
    
    print("\n✅ 所有Forum集成测试通过!")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(run_forum_integration_tests())