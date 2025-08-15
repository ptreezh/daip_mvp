#!/usr/bin/env python3
"""多角色对话功能集成测试套件

测试多角色对话引擎与现有组件的集成，验证完整的对话流程和异常处理。
"""

import asyncio
import logging
import os
import sys
import unittest
from datetime import datetime
from unittest.mock import AsyncMock, Mock

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.debate_system.debate_flow_definition import DebatePhase, DebateSession, ParticipantRole
from src.debate_system.multi_role_dialogue_engine import (
    ConversationTurn,
    DialogueState,
    MultiRoleDialogueEngine,
    RoleContext,
)


class TestMultiRoleDialogueIntegration(unittest.TestCase):
    """多角色对话集成测试"""
    
    def setUp(self):
        """测试设置"""
        # 创建模拟组件
        self.mock_cognitive_agent = Mock()
        self.mock_role_manager = Mock()
        self.mock_llm_manager = AsyncMock()
        self.mock_memory_agent = AsyncMock()
        self.mock_participant_manager = Mock()
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        
        # 创建对话引擎
        self.dialogue_engine = MultiRoleDialogueEngine(
            cognitive_agent=self.mock_cognitive_agent,
            role_manager=self.mock_role_manager,
            llm_manager=self.mock_llm_manager,
            memory_agent=self.mock_memory_agent,
            participant_manager=self.mock_participant_manager
        )
        
        # 创建测试会话
        self.test_session = DebateSession(
            title="测试辩论",
            topic="人工智能的未来发展",
            description="讨论AI技术的发展趋势"
        )
    
    async def test_role_selection_for_topic(self):
        """测试基于话题的角色选择"""
        print("🧪 测试角色选择功能...")
        
        # 模拟可用角色
        mock_roles = {
            "ai_expert": {
                "name": "AI专家",
                "expertise_areas": ["人工智能", "机器学习", "深度学习"],
                "speaking_style": "technical",
                "description": "专注于人工智能技术研究"
            },
            "ethicist": {
                "name": "伦理学家",
                "expertise_areas": ["伦理学", "哲学", "社会影响"],
                "speaking_style": "philosophical",
                "description": "关注技术的伦理和社会影响"
            },
            "economist": {
                "name": "经济学家",
                "expertise_areas": ["经济学", "市场分析", "产业发展"],
                "speaking_style": "analytical",
                "description": "分析技术的经济影响"
            }
        }
        
        self.mock_role_manager.get_available_roles.return_value = mock_roles
        
        # 测试角色选择
        selected_roles = await self.dialogue_engine.role_selector.select_roles_for_topic(
            "人工智能的未来发展", max_roles=3
        )
        
        # 验证结果
        self.assertIsInstance(selected_roles, list)
        self.assertGreater(len(selected_roles), 0)
        self.assertLessEqual(len(selected_roles), 3)
        
        # 验证角色上下文
        for role_context in selected_roles:
            self.assertIsInstance(role_context, RoleContext)
            self.assertIn(role_context.role_id, mock_roles.keys())
            self.assertIsInstance(role_context.expertise_areas, list)
        
        print(f"✅ 成功选择了 {len(selected_roles)} 个角色")
    
    async def test_llm_response_generation(self):
        """测试LLM响应生成"""
        print("🧪 测试LLM响应生成...")
        
        # 模拟LLM响应
        mock_response = "作为AI专家，我认为人工智能的发展将带来巨大的机遇和挑战。"
        self.mock_llm_manager.generate_response.return_value = mock_response
        
        # 创建测试角色上下文
        role_context = RoleContext(
            role_id="ai_expert",
            role_name="AI专家",
            role_type=ParticipantRole.EXPERT,
            expertise_areas=["人工智能", "机器学习"]
        )
        
        # 创建对话上下文
        from src.debate_system.multi_role_dialogue_engine import DialogueContext
        dialogue_context = DialogueContext(
            session_id=self.test_session.session_id,
            topic="人工智能的未来发展",
            current_phase=DebatePhase.MAIN_ARGUMENTS
        )
        
        # 测试响应生成
        turn = await self.dialogue_engine.conversation_manager.generate_role_response(
            role_context, dialogue_context, ConversationTurn.OPENING
        )
        
        # 验证结果
        self.assertIsNotNone(turn)
        self.assertEqual(turn.speaker_role_id, "ai_expert")
        self.assertEqual(turn.turn_type, ConversationTurn.OPENING)
        self.assertEqual(turn.content, mock_response)
        self.assertGreater(turn.confidence_score, 0)
        
        # 验证LLM调用
        self.mock_llm_manager.generate_response.assert_called_once()
        call_args = self.mock_llm_manager.generate_response.call_args
        self.assertIn("prompt", call_args.kwargs)
        self.assertIn("AI专家", call_args.kwargs["prompt"])
        
        print("✅ LLM响应生成测试通过")
    
    async def test_llm_retry_mechanism(self):
        """测试LLM调用重试机制"""
        print("🧪 测试LLM重试机制...")
        
        # 模拟前两次调用失败，第三次成功
        self.mock_llm_manager.generate_response.side_effect = [
            Exception("网络错误"),
            Exception("超时"),
            "这是重试后的成功响应"
        ]
        
        # 测试重试机制
        response = await self.dialogue_engine.conversation_manager._call_llm_with_retry(
            "test_role", "测试提示词"
        )
        
        # 验证结果
        self.assertEqual(response, "这是重试后的成功响应")
        self.assertEqual(self.mock_llm_manager.generate_response.call_count, 3)
        
        print("✅ LLM重试机制测试通过")
    
    async def test_convergence_detection(self):
        """测试讨论收敛检测"""
        print("🧪 测试讨论收敛检测...")
        
        # 创建模拟对话历史
        from src.debate_system.multi_role_dialogue_engine import DialogueContext, DialogueTurn
        
        dialogue_context = DialogueContext(
            session_id=self.test_session.session_id,
            topic="测试话题",
            current_phase=DebatePhase.MAIN_ARGUMENTS
        )
        
        # 添加相似的对话轮次（模拟收敛）
        similar_content = [
            "我认为这个观点很有道理",
            "我同意这个观点很有道理",
            "确实，这个观点很有道理"
        ]
        
        for i, content in enumerate(similar_content):
            turn = DialogueTurn(
                speaker_role_id=f"role_{i}",
                content=content,
                timestamp=datetime.now()
            )
            dialogue_context.dialogue_history.append(turn)
        
        # 测试收敛检测
        convergence = await self.dialogue_engine.convergence_detector.detect_convergence(
            dialogue_context
        )
        
        # 验证结果
        self.assertIsInstance(convergence, dict)
        self.assertIn('viewpoint_similarity', convergence)
        self.assertIn('repetition_level', convergence)
        self.assertIn('activity_level', convergence)
        self.assertIn('overall_convergence', convergence)
        
        # 验证收敛度较高（因为内容相似）
        self.assertGreater(convergence['viewpoint_similarity'], 0.5)
        self.assertGreater(convergence['overall_convergence'], 0.3)
        
        print("✅ 讨论收敛检测测试通过")
    
    async def test_complete_dialogue_flow(self):
        """测试完整的对话流程"""
        print("🧪 测试完整对话流程...")
        
        # 设置模拟数据
        mock_roles = {
            "expert1": {
                "name": "专家1",
                "expertise_areas": ["技术"],
                "speaking_style": "formal"
            },
            "expert2": {
                "name": "专家2", 
                "expertise_areas": ["伦理"],
                "speaking_style": "thoughtful"
            }
        }
        
        self.mock_role_manager.get_available_roles.return_value = mock_roles
        
        # 模拟LLM响应
        responses = [
            "专家1的开场观点",
            "专家2的开场观点",
            "专家1的回应",
            "专家2的回应"
        ]
        self.mock_llm_manager.generate_response.side_effect = responses
        
        # 启动对话
        success = await self.dialogue_engine.start_dialogue(
            self.test_session, "测试话题", max_roles=2
        )
        
        # 验证启动成功
        self.assertTrue(success)
        self.assertIn(self.test_session.session_id, self.dialogue_engine.active_dialogues)
        self.assertEqual(
            self.dialogue_engine.dialogue_state[self.test_session.session_id],
            DialogueState.ACTIVE
        )
        
        # 继续对话
        continue_success = await self.dialogue_engine.continue_dialogue(
            self.test_session.session_id
        )
        self.assertTrue(continue_success)
        
        # 获取对话摘要
        summary = await self.dialogue_engine.get_dialogue_summary(
            self.test_session.session_id
        )
        
        # 验证摘要
        self.assertIsNotNone(summary)
        self.assertEqual(summary['session_id'], self.test_session.session_id)
        self.assertEqual(summary['topic'], "测试话题")
        self.assertGreater(summary['total_turns'], 0)
        
        # 结束对话
        end_success = await self.dialogue_engine.end_dialogue(
            self.test_session.session_id
        )
        self.assertTrue(end_success)
        self.assertEqual(
            self.dialogue_engine.dialogue_state[self.test_session.session_id],
            DialogueState.COMPLETED
        )
        
        print("✅ 完整对话流程测试通过")
    
    async def test_error_handling(self):
        """测试错误处理"""
        print("🧪 测试错误处理...")
        
        # 测试角色选择失败
        self.mock_role_manager.get_available_roles.side_effect = Exception("角色管理器错误")
        
        success = await self.dialogue_engine.start_dialogue(
            self.test_session, "测试话题"
        )
        self.assertFalse(success)
        
        # 重置模拟
        self.mock_role_manager.get_available_roles.side_effect = None
        self.mock_role_manager.get_available_roles.return_value = {}
        
        # 测试无可用角色
        success = await self.dialogue_engine.start_dialogue(
            self.test_session, "测试话题"
        )
        self.assertFalse(success)
        
        # 测试不存在的会话
        continue_success = await self.dialogue_engine.continue_dialogue("nonexistent")
        self.assertFalse(continue_success)
        
        summary = await self.dialogue_engine.get_dialogue_summary("nonexistent")
        self.assertIsNone(summary)
        
        print("✅ 错误处理测试通过")
    
    async def test_memory_integration(self):
        """测试记忆系统集成"""
        print("🧪 测试记忆系统集成...")
        
        # 创建测试对话轮次
        from src.debate_system.multi_role_dialogue_engine import DialogueTurn
        
        turn = DialogueTurn(
            speaker_role_id="test_role",
            content="测试发言内容",
            turn_type=ConversationTurn.OPENING
        )
        
        # 测试记忆更新
        await self.dialogue_engine._update_memory(self.test_session.session_id, turn)
        
        # 验证记忆系统调用
        self.mock_memory_agent.store_memory.assert_called_once()
        call_args = self.mock_memory_agent.store_memory.call_args
        
        self.assertIn("key", call_args.kwargs)
        self.assertIn("content", call_args.kwargs)
        self.assertIn("memory_type", call_args.kwargs)
        self.assertEqual(call_args.kwargs["memory_type"], "dialogue_history")
        
        print("✅ 记忆系统集成测试通过")


class TestPerformanceAndStability(unittest.TestCase):
    """性能和稳定性测试"""
    
    def setUp(self):
        """测试设置"""
        # 创建轻量级模拟组件
        self.mock_components = {
            'cognitive_agent': Mock(),
            'role_manager': Mock(),
            'llm_manager': AsyncMock(),
            'memory_agent': AsyncMock(),
            'participant_manager': Mock()
        }
        
        # 快速响应设置
        self.mock_components['llm_manager'].generate_response.return_value = "快速响应"
        self.mock_components['role_manager'].get_available_roles.return_value = {
            "role1": {"name": "角色1", "expertise_areas": ["测试"], "speaking_style": "formal"}
        }
    
    async def test_response_time_performance(self):
        """测试响应时间性能"""
        print("🧪 测试响应时间性能...")
        
        dialogue_engine = MultiRoleDialogueEngine(**self.mock_components)
        
        # 创建测试会话
        test_session = DebateSession(
            title="性能测试",
            topic="测试话题"
        )
        
        # 测量启动时间
        start_time = datetime.now()
        success = await dialogue_engine.start_dialogue(test_session, "测试话题", max_roles=1)
        end_time = datetime.now()
        
        startup_time = (end_time - start_time).total_seconds()
        
        # 验证性能要求（应该在1秒内完成）
        self.assertTrue(success)
        self.assertLess(startup_time, 1.0, f"启动时间过长: {startup_time}秒")
        
        print(f"✅ 对话启动时间: {startup_time:.3f}秒")
    
    async def test_concurrent_dialogues(self):
        """测试并发对话处理"""
        print("🧪 测试并发对话处理...")
        
        dialogue_engine = MultiRoleDialogueEngine(**self.mock_components)
        
        # 创建多个测试会话
        sessions = [
            DebateSession(title=f"并发测试{i}", topic=f"话题{i}")
            for i in range(5)
        ]
        
        # 并发启动对话
        tasks = [
            dialogue_engine.start_dialogue(session, f"话题{i}", max_roles=1)
            for i, session in enumerate(sessions)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 验证所有对话都成功启动
        success_count = sum(1 for result in results if result is True)
        self.assertEqual(success_count, 5, "并发对话启动失败")
        
        # 验证对话引擎状态
        self.assertEqual(len(dialogue_engine.active_dialogues), 5)
        
        print(f"✅ 成功处理 {success_count} 个并发对话")
    
    async def test_memory_usage_stability(self):
        """测试内存使用稳定性"""
        print("🧪 测试内存使用稳定性...")
        
        dialogue_engine = MultiRoleDialogueEngine(**self.mock_components)
        
        # 模拟长时间运行
        for i in range(100):
            session = DebateSession(title=f"稳定性测试{i}", topic="测试话题")
            
            # 启动和结束对话
            await dialogue_engine.start_dialogue(session, "测试话题", max_roles=1)
            await dialogue_engine.end_dialogue(session.session_id)
        
        # 验证没有内存泄漏（活跃对话应该被清理）
        active_count = len(dialogue_engine.active_dialogues)
        completed_count = sum(
            1 for state in dialogue_engine.dialogue_state.values()
            if state == DialogueState.COMPLETED
        )
        
        self.assertGreaterEqual(completed_count, 90, "对话完成率过低")
        print(f"✅ 完成 {completed_count} 个对话，活跃对话: {active_count}")


async def run_all_tests():
    """运行所有测试"""
    print("🚀 开始多角色对话功能集成测试...")
    
    # 基础功能测试
    integration_test = TestMultiRoleDialogueIntegration()
    integration_test.setUp()
    
    await integration_test.test_role_selection_for_topic()
    await integration_test.test_llm_response_generation()
    await integration_test.test_llm_retry_mechanism()
    await integration_test.test_convergence_detection()
    await integration_test.test_complete_dialogue_flow()
    await integration_test.test_error_handling()
    await integration_test.test_memory_integration()
    
    # 性能和稳定性测试
    performance_test = TestPerformanceAndStability()
    performance_test.setUp()
    
    await performance_test.test_response_time_performance()
    await performance_test.test_concurrent_dialogues()
    await performance_test.test_memory_usage_stability()
    
    print("🎉 所有多角色对话功能测试完成！")


if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行测试
    asyncio.run(run_all_tests())