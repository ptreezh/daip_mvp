#!/usr/bin/env python3
"""Personal Intelligence Hub - Personal Assistant Service Tests

测试个人助手服务功能
"""

from unittest.mock import patch

import pytest

from personal_intelligence_hub.services.personal_assistant import (
    IntentResult,
    PersonalAssistantService,
    TeamProposal,
    WorkflowType,
)


class TestPersonalAssistantService:
    """个人助手服务测试类"""

    def setup_method(self):
        """测试前置设置"""
        self.service = PersonalAssistantService()

    def test_initialization(self):
        """测试服务初始化"""
        assert self.service.conversation_contexts == {}

    @pytest.mark.asyncio
    async def test_analyze_intent_critical_review(self):
        """测试意图分析 - 批判性审查"""
        user_input = "请帮我分析这个方案的可行性"

        result = await self.service.analyze_intent(user_input)

        assert isinstance(result, IntentResult)
        assert result.workflow_type == WorkflowType.CRITICAL_REVIEW
        assert result.confidence > 0.8
        assert "分析" in result.reasoning
        assert result.topic == user_input

    @pytest.mark.asyncio
    async def test_analyze_intent_multi_perspective(self):
        """测试意图分析 - 多视角讨论"""
        user_input = "我们来讨论一下这个问题的不同观点"

        result = await self.service.analyze_intent(user_input)

        assert isinstance(result, IntentResult)
        assert result.workflow_type == WorkflowType.MULTI_PERSPECTIVE
        assert result.confidence > 0.7
        assert "多角度" in result.reasoning
        assert result.topic == user_input

    @pytest.mark.asyncio
    async def test_analyze_intent_default(self):
        """测试意图分析 - 默认情况"""
        user_input = "你好，我需要帮助"

        result = await self.service.analyze_intent(user_input)

        assert isinstance(result, IntentResult)
        assert result.workflow_type == WorkflowType.CRITICAL_REVIEW
        assert result.confidence == 0.6
        assert "默认" in result.reasoning

    @pytest.mark.asyncio
    async def test_analyze_intent_with_context(self):
        """测试带上下文的意图分析"""
        user_input = "继续分析"
        context = {"previous_topic": "AI安全"}

        result = await self.service.analyze_intent(user_input, context)

        assert isinstance(result, IntentResult)
        assert result.topic == user_input

    @pytest.mark.asyncio
    async def test_assemble_team_critical_review(self):
        """测试团队组建 - 批判性审查"""
        topic = "AI伦理问题"
        workflow_type = WorkflowType.CRITICAL_REVIEW

        team = await self.service.assemble_team(topic, workflow_type)

        assert isinstance(team, TeamProposal)
        assert "Critic-AI" in team.agents
        assert "Analyst-AI" in team.agents
        assert "Validator-AI" in team.agents
        assert team.diversity_score == 0.85
        assert topic in team.rationale
        assert "继续吗？" in team.confirmation_message

    @pytest.mark.asyncio
    async def test_assemble_team_multi_perspective(self):
        """测试团队组建 - 多视角讨论"""
        topic = "气候变化政策"
        workflow_type = WorkflowType.MULTI_PERSPECTIVE

        team = await self.service.assemble_team(topic, workflow_type)

        assert isinstance(team, TeamProposal)
        assert "Advocate-AI" in team.agents
        assert "Skeptic-AI" in team.agents
        assert "Synthesizer-AI" in team.agents
        assert "Moderator-AI" in team.agents
        assert len(team.agents) == 4
        assert team.diversity_score == 0.85

    @pytest.mark.asyncio
    async def test_assemble_team_custom(self):
        """测试团队组建 - 自定义工作流"""
        topic = "技术评估"
        workflow_type = WorkflowType.CUSTOM

        team = await self.service.assemble_team(topic, workflow_type)

        assert isinstance(team, TeamProposal)
        assert "General-AI" in team.agents
        assert "Analyst-AI" in team.agents
        assert len(team.agents) == 2

    @pytest.mark.asyncio
    async def test_process_message_complete_flow(self):
        """测试完整的消息处理流程"""
        user_input = "请分析这个技术方案的风险"
        session_id = "test_session_123"

        response = await self.service.process_message(user_input, session_id)

        assert isinstance(response, str)
        assert len(response) > 0
        assert "分析" in response
        assert "Critic-AI" in response
        assert "继续吗？" in response
        assert "置信度" in response

    @pytest.mark.asyncio
    async def test_process_message_error_handling(self):
        """测试消息处理错误处理"""
        # 通过Mock引发异常来测试错误处理
        with patch.object(self.service, 'analyze_intent', side_effect=Exception("测试异常")):
            response = await self.service.process_message("测试", "session")

            assert "抱歉，处理您的请求时出现了问题" in response

    def test_get_conversation_context_new_session(self):
        """测试获取新会话的对话上下文"""
        session_id = "new_session_123"

        context = self.service.get_conversation_context(session_id)

        assert context["session_id"] == session_id
        assert context["message_history"] == []
        assert context["current_workflow"] is None
        assert context["active_agents"] == []

    def test_get_conversation_context_existing_session(self):
        """测试获取已存在会话的对话上下文"""
        session_id = "existing_session"

        # 先创建一个上下文
        original_context = self.service.get_conversation_context(session_id)
        original_context["message_history"].append({"test": "message"})

        # 再次获取应该返回相同的上下文
        retrieved_context = self.service.get_conversation_context(session_id)

        assert retrieved_context == original_context
        assert len(retrieved_context["message_history"]) == 1


class TestWorkflowType:
    """工作流类型枚举测试"""

    def test_workflow_type_values(self):
        """测试工作流类型枚举值"""
        assert WorkflowType.CRITICAL_REVIEW.value == "critical_review"
        assert WorkflowType.MULTI_PERSPECTIVE.value == "multi_perspective"
        assert WorkflowType.CUSTOM.value == "custom"


class TestIntentResult:
    """意图结果数据类测试"""

    def test_intent_result_creation(self):
        """测试意图结果创建"""
        result = IntentResult(
            workflow_type=WorkflowType.CRITICAL_REVIEW,
            confidence=0.85,
            reasoning="测试推理",
            topic="测试主题"
        )

        assert result.workflow_type == WorkflowType.CRITICAL_REVIEW
        assert result.confidence == 0.85
        assert result.reasoning == "测试推理"
        assert result.topic == "测试主题"


class TestTeamProposal:
    """团队提议数据类测试"""

    def test_team_proposal_creation(self):
        """测试团队提议创建"""
        proposal = TeamProposal(
            agents=["Agent1", "Agent2"],
            diversity_score=0.9,
            rationale="测试理由",
            confirmation_message="确认消息"
        )

        assert proposal.agents == ["Agent1", "Agent2"]
        assert proposal.diversity_score == 0.9
        assert proposal.rationale == "测试理由"
        assert proposal.confirmation_message == "确认消息"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
