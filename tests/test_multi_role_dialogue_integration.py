#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多角色对话功能集成测试

测试多角色对话管理器的核心功能：
1. 角色选择和匹配
2. 对话轮次管理
3. 用户干预处理
4. LLM调用优化
5. 会话状态管理
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.core_services.multi_role_dialogue_manager import (
    MultiRoleDialogueManager,
    DialogueParticipant,
    DialogueSession
)


class TestMultiRoleDialogueIntegration:
    """多角色对话集成测试"""
    
    @pytest.fixture
    async def dialogue_manager(self):
        """创建对话管理器实例"""
        manager = MultiRoleDialogueManager()
        
        # Mock 依赖组件
        manager.role_manager = MagicMock()
        manager.llm_manager = AsyncMock()
        manager.memory_agent = AsyncMock()
        
        # Mock 初始化方法
        manager.llm_manager.initialize = AsyncMock()
        manager.memory_agent.initialize = AsyncMock()
        
        await manager.initialize()
        return manager
    
    @pytest.fixture
    def mock_roles(self):
        """创建模拟角色"""
        from src.core_services.role_manager import Role
        
        return [
            Role(
                id="system_synthesis_master",
                name="系统综合分析师",
                description="专业的系统分析和综合专家",
                system_prompt="你是一个系统综合分析师...",
                capabilities=["系统分析", "综合思维", "问题解决"]
            ),
            Role(
                id="socratic_dialogue_guide", 
                name="苏格拉底对话引导师",
                description="擅长引导深度思考的对话专家",
                system_prompt="你是一个苏格拉底对话引导师...",
                capabilities=["对话引导", "批判思维", "深度提问"]
            ),
            Role(
                id="task_decomposition_master",
                name="任务分解专家", 
                description="专业的任务分析和分解专家",
                system_prompt="你是一个任务分解专家...",
                capabilities=["任务分解", "流程设计", "项目管理"]
            )
        ]
    
    @pytest.mark.asyncio
    async def test_start_dialogue_session(self, dialogue_manager, mock_roles):
        """测试启动对话会话"""
        # 设置mock
        dialogue_manager.role_manager.list_roles.return_value = mock_roles
        
        # 启动对话会话
        session = await dialogue_manager.start_dialogue_session(
            topic="AI在教育中的应用前景",
            user_preferences={"expertise": ["教育", "技术"]}
        )
        
        # 验证会话创建
        assert isinstance(session, DialogueSession)
        assert session.topic == "AI在教育中的应用前景"
        assert session.status == 'active'
        assert len(session.participants) >= 2
        assert len(session.participants) <= 4
        
        # 验证会话已添加到活跃会话中
        assert session.session_id in dialogue_manager.active_sessions
    
    @pytest.mark.asyncio
    async def test_conduct_dialogue_round(self, dialogue_manager, mock_roles):
        """测试进行对话轮次"""
        # 设置mock
        dialogue_manager.role_manager.list_roles.return_value = mock_roles
        dialogue_manager.llm_manager.call_llm_for_role.return_value = {
            "response": "这是一个测试回应",
            "optimization_metrics": {"improvement_score": 0.8, "tokens_saved": 100}
        }
        
        # 启动会话
        session = await dialogue_manager.start_dialogue_session("测试主题")
        
        # 进行对话轮次
        dialogue_round = await dialogue_manager.conduct_dialogue_round(session.session_id)
        
        # 验证轮次结果
        assert dialogue_round.round_number == 1
        assert dialogue_round.topic == "测试主题"
        assert len(dialogue_round.responses) == len(session.participants)
        
        # 验证所有角色都有回应
        for response in dialogue_round.responses:
            assert "role_id" in response
            assert "role_name" in response
            assert "response" in response
            assert response["success"] == True
        
        # 验证会话状态更新
        assert len(session.rounds) == 1
        assert session.convergence_score > 0
    
    @pytest.mark.asyncio
    async def test_user_intervention(self, dialogue_manager, mock_roles):
        """测试用户干预功能"""
        # 设置mock
        dialogue_manager.role_manager.list_roles.return_value = mock_roles
        dialogue_manager.llm_manager.call_llm_for_role.return_value = {
            "response": "感谢用户的参与和观点",
            "optimization_metrics": {"improvement_score": 0.7}
        }
        
        # 启动会话并进行一轮对话
        session = await dialogue_manager.start_dialogue_session("测试主题")
        await dialogue_manager.conduct_dialogue_round(session.session_id)
        
        # 添加用户干预
        intervention_result = await dialogue_manager.add_user_intervention(
            session.session_id,
            "我认为还需要考虑实际应用中的挑战",
            "comment"
        )
        
        # 验证干预结果
        assert intervention_result["intervention_recorded"] == True
        assert len(intervention_result["role_responses"]) == len(session.participants)
        
        # 验证会话中记录了用户干预
        assert len(session.user_interventions) == 1
        assert session.user_interventions[0]["content"] == "我认为还需要考虑实际应用中的挑战"
        assert session.user_interventions[0]["type"] == "comment"
    
    @pytest.mark.asyncio
    async def test_role_selection_optimization(self, dialogue_manager, mock_roles):
        """测试角色选择优化"""
        # 扩展mock角色列表，包含更多专业角色
        extended_roles = mock_roles + [
            MagicMock(id="ai_ethics", name="AI伦理专家", capabilities=["AI伦理", "技术哲学"]),
            MagicMock(id="education_expert", name="教育专家", capabilities=["教育理论", "教学方法"]),
            MagicMock(id="economist", name="经济学家", capabilities=["经济分析", "市场研究"])
        ]
        
        dialogue_manager.role_manager.list_roles.return_value = extended_roles
        
        # 测试AI相关主题的角色选择
        session = await dialogue_manager.start_dialogue_session("AI在教育中的伦理问题")
        
        # 验证选择了相关的专业角色
        participant_names = [p.role_name for p in session.participants]
        assert any("AI" in name or "伦理" in name for name in participant_names)
    
    @pytest.mark.asyncio
    async def test_llm_call_optimization(self, dialogue_manager, mock_roles):
        """测试LLM调用优化"""
        dialogue_manager.role_manager.list_roles.return_value = mock_roles
        
        # 模拟优化的LLM调用
        dialogue_manager.llm_manager.call_llm_for_role.return_value = {
            "response": "优化后的回应内容",
            "optimization_applied": True,
            "optimization_metrics": {
                "improvement_score": 0.85,
                "tokens_saved": 150,
                "time_saved": 2.5,
                "context_compression": 0.6
            }
        }
        
        # 启动会话并进行对话
        session = await dialogue_manager.start_dialogue_session("测试LLM优化")
        dialogue_round = await dialogue_manager.conduct_dialogue_round(session.session_id)
        
        # 验证优化指标
        for response in dialogue_round.responses:
            if "optimization_metrics" in response:
                metrics = response["optimization_metrics"]
                assert metrics.get("improvement_score", 0) > 0
                assert "tokens_saved" in metrics or "time_saved" in metrics
        
        # 验证LLM管理器被正确调用
        assert dialogue_manager.llm_manager.call_llm_for_role.call_count == len(session.participants)
    
    @pytest.mark.asyncio
    async def test_convergence_calculation(self, dialogue_manager, mock_roles):
        """测试收敛度计算"""
        dialogue_manager.role_manager.list_roles.return_value = mock_roles
        dialogue_manager.llm_manager.call_llm_for_role.return_value = {
            "response": "测试回应",
            "optimization_metrics": {"improvement_score": 0.7}
        }
        
        # 启动会话
        session = await dialogue_manager.start_dialogue_session("测试收敛度")
        
        # 进行多轮对话
        initial_convergence = session.convergence_score
        
        await dialogue_manager.conduct_dialogue_round(session.session_id)
        round1_convergence = session.convergence_score
        
        await dialogue_manager.conduct_dialogue_round(session.session_id)
        round2_convergence = session.convergence_score
        
        # 验证收敛度递增
        assert round1_convergence > initial_convergence
        assert round2_convergence > round1_convergence
        assert 0 <= round2_convergence <= 1
    
    @pytest.mark.asyncio
    async def test_error_handling(self, dialogue_manager, mock_roles):
        """测试错误处理机制"""
        dialogue_manager.role_manager.list_roles.return_value = mock_roles
        
        # 模拟LLM调用失败
        dialogue_manager.llm_manager.call_llm_for_role.side_effect = Exception("LLM调用失败")
        
        # 启动会话
        session = await dialogue_manager.start_dialogue_session("测试错误处理")
        
        # 进行对话轮次（应该优雅处理错误）
        dialogue_round = await dialogue_manager.conduct_dialogue_round(session.session_id)
        
        # 验证错误处理
        assert len(dialogue_round.responses) == len(session.participants)
        for response in dialogue_round.responses:
            assert response["success"] == False
            assert "error" in response
            assert "技术问题" in response["response"] or "系统错误" in response["response"]
    
    @pytest.mark.asyncio
    async def test_session_management(self, dialogue_manager, mock_roles):
        """测试会话管理功能"""
        dialogue_manager.role_manager.list_roles.return_value = mock_roles
        
        # 创建多个会话
        session1 = await dialogue_manager.start_dialogue_session("主题1")
        session2 = await dialogue_manager.start_dialogue_session("主题2")
        
        # 验证会话列表
        active_sessions = dialogue_manager.list_active_sessions()
        assert len(active_sessions) == 2
        
        # 验证会话状态
        status1 = dialogue_manager.get_session_status(session1.session_id)
        assert status1["topic"] == "主题1"
        assert status1["status"] == "active"
        
        # 关闭会话
        summary = await dialogue_manager.close_session(session1.session_id)
        assert summary["session_id"] == session1.session_id
        assert summary["topic"] == "主题1"
        
        # 验证会话已从活跃列表中移除
        active_sessions = dialogue_manager.list_active_sessions()
        assert len(active_sessions) == 1
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self, dialogue_manager, mock_roles):
        """测试性能要求"""
        import time
        
        dialogue_manager.role_manager.list_roles.return_value = mock_roles
        dialogue_manager.llm_manager.call_llm_for_role.return_value = {
            "response": "快速回应",
            "optimization_metrics": {"improvement_score": 0.8}
        }
        
        # 测试会话启动性能
        start_time = time.time()
        session = await dialogue_manager.start_dialogue_session("性能测试")
        session_creation_time = time.time() - start_time
        
        # 验证会话创建时间 < 5秒
        assert session_creation_time < 5.0
        
        # 测试对话轮次性能
        start_time = time.time()
        await dialogue_manager.conduct_dialogue_round(session.session_id)
        round_time = time.time() - start_time
        
        # 验证单轮对话时间 < 30秒（任务要求）
        assert round_time < 30.0


if __name__ == "__main__":
    # 运行集成测试
    pytest.main([__file__, "-v"])