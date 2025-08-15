"""@Time    : 2025-07-24 14:00:00
@Author  : DAIP-LIVE Team
@File    : test_multi_perspective_nodes.py
@Description:
    Unit tests for Multi-perspective Synthesis Workflow nodes.
"""
from unittest.mock import AsyncMock, Mock

import pytest

from src.institutional_primitives.base import ExecutionContext
from src.institutional_primitives.multi_perspective_nodes import (
    ExpertViewpoint,
    ParallelExplorationNode,
    SubProblem,
    SynthesisResult,
    TaskDecompositionNode,
    ViewpointSynthesisNode,
)


class TestSubProblemModel:
    """Test cases for SubProblem model."""
    
    def test_sub_problem_creation(self):
        """Test SubProblem model creation."""
        sub_problem = SubProblem(
            id="sub_1",
            perspective="经济",
            description="分析AI对就业市场的经济影响",
            questions=["AI如何影响就业率?", "哪些行业最受影响?"],
            expertise_required=["经济学", "劳动经济学"],
            priority=1
        )
        
        assert sub_problem.id == "sub_1"
        assert sub_problem.perspective == "经济"
        assert sub_problem.description == "分析AI对就业市场的经济影响"
        assert len(sub_problem.questions) == 2
        assert "AI如何影响就业率?" in sub_problem.questions
        assert "经济学" in sub_problem.expertise_required
        assert sub_problem.priority == 1


class TestExpertViewpointModel:
    """Test cases for ExpertViewpoint model."""
    
    def test_expert_viewpoint_creation(self):
        """Test ExpertViewpoint model creation."""
        viewpoint = ExpertViewpoint(
            expert_id="economist",
            expert_name="经济学家",
            expertise_areas=["经济学", "劳动经济学"],
            sub_problem_id="sub_1",
            viewpoint="AI将导致短期就业市场波动，但长期将创造新的就业机会。",
            supporting_evidence=["历史技术革命数据", "最新就业市场研究"],
            confidence=0.8,
            reasoning_process="基于历史技术革命的模式分析..."
        )
        
        assert viewpoint.expert_id == "economist"
        assert viewpoint.expert_name == "经济学家"
        assert "经济学" in viewpoint.expertise_areas
        assert viewpoint.sub_problem_id == "sub_1"
        assert "AI将导致短期就业市场波动" in viewpoint.viewpoint
        assert "历史技术革命数据" in viewpoint.supporting_evidence
        assert viewpoint.confidence == 0.8
        assert "基于历史技术革命的模式分析" in viewpoint.reasoning_process


class TestSynthesisResultModel:
    """Test cases for SynthesisResult model."""
    
    def test_synthesis_result_creation(self):
        """Test SynthesisResult model creation."""
        result = SynthesisResult(
            topic="AI对就业的影响",
            perspectives=["经济", "社会", "技术"],
            synthesis="综合分析表明，AI对就业的影响是多方面的...",
            key_insights=["AI将创造新的就业类型", "需要新的教育和培训体系"],
            expert_contributions={
                "经济学家": ["提供了经济角度的分析"],
                "社会学家": ["分析了社会结构变化"]
            },
            confidence=0.85
        )
        
        assert result.topic == "AI对就业的影响"
        assert "经济" in result.perspectives
        assert "AI对就业的影响是多方面的" in result.synthesis
        assert "AI将创造新的就业类型" in result.key_insights
        assert "经济学家" in result.expert_contributions
        assert result.confidence == 0.85


class TestTaskDecompositionNode:
    """Test cases for TaskDecompositionNode."""
    
    @pytest.fixture()
    def decomposition_node(self):
        """Create a TaskDecompositionNode instance for testing."""
        return TaskDecompositionNode("decomp_1", {
            "planner_role": "规划者",
            "default_perspectives": ["经济", "社会", "技术", "伦理"],
            "max_sub_problems": 4
        })
    
    @pytest.fixture()
    def mock_context(self):
        """Create a mock execution context."""
        context = Mock(spec=ExecutionContext)
        context.execution_id = "exec_123"
        context.node_id = "node_decomp"
        context.state = {}
        context.services = {}
        context.mark_started = Mock()
        context.mark_completed = Mock()
        context.mark_failed = Mock()
        return context
    
    @pytest.fixture()
    def mock_llm_interface(self):
        """Create a mock LLM interface."""
        llm = AsyncMock()
        llm.generate.return_value = {
            "content": """以下是对主题的分解：

```json
[
  {
    "perspective": "经济",
    "description": "分析AI对就业市场的经济影响",
    "questions": ["AI如何影响就业率?", "哪些行业最受影响?", "如何应对就业市场变化?"],
    "expertise_required": ["经济学", "劳动经济学"],
    "priority": 1
  },
  {
    "perspective": "社会",
    "description": "探讨AI对社会结构和不平等的影响",
    "questions": ["AI如何影响社会阶层?", "如何确保AI带来的利益公平分配?"],
    "expertise_required": ["社会学", "公共政策"],
    "priority": 2
  },
  {
    "perspective": "技术",
    "description": "分析AI技术发展趋势及其对就业的影响",
    "questions": ["哪些AI技术对就业影响最大?", "未来技术发展方向如何?"],
    "expertise_required": ["计算机科学", "AI研究"],
    "priority": 1
  },
  {
    "perspective": "伦理",
    "description": "探讨AI替代人类工作的伦理问题",
    "questions": ["AI替代人类工作在伦理上是否合理?", "如何平衡效率与人文关怀?"],
    "expertise_required": ["伦理学", "哲学"],
    "priority": 3
  }
]
```"""
        }
        return llm
    
    @pytest.fixture()
    def mock_role_manager(self):
        """Create a mock role manager."""
        role_manager = Mock()
        planner_role = Mock()
        planner_role.system_prompt = "你是一位专业的任务分解专家，擅长将复杂问题分解为多个子问题。"
        role_manager.get_role_by_id.return_value = planner_role
        return role_manager
    
    @pytest.mark.asyncio()
    async def test_task_decomposition_success(self, decomposition_node, mock_context, mock_llm_interface, mock_role_manager):
        """Test successful task decomposition."""
        # Setup
        mock_context.services["llm_interface"] = mock_llm_interface
        mock_context.services["role_manager"] = mock_role_manager
        inputs = {"topic": "AI对就业的影响"}
        
        # Execute
        result = await decomposition_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is True
        assert result["topic"] == "AI对就业的影响"
        assert result["sub_problem_count"] == 4
        assert len(result["sub_problems"]) == 4
        
        # Verify sub-problem details
        sub_problems = result["sub_problems"]
        perspectives = [sp["perspective"] for sp in sub_problems]
        assert "经济" in perspectives
        assert "社会" in perspectives
        assert "技术" in perspectives
        assert "伦理" in perspectives
        
        # Verify context state was updated
        assert mock_context.state["topic"] == "AI对就业的影响"
        assert len(mock_context.state["sub_problems"]) == 4
        
        # Verify context methods were called
        mock_context.mark_started.assert_called_once()
        mock_context.mark_completed.assert_called_once()
        
        # Verify LLM was called correctly
        mock_llm_interface.generate.assert_called_once()
        call_args = mock_llm_interface.generate.call_args[0][0]
        assert len(call_args) == 2
        assert "规划者" in call_args[0]["content"]
        assert "AI对就业的影响" in call_args[1]["content"]
    
    @pytest.mark.asyncio()
    async def test_task_decomposition_missing_topic(self, decomposition_node, mock_context):
        """Test decomposition with missing topic."""
        # Setup
        inputs = {}
        
        # Execute
        result = await decomposition_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "error" in result
        assert "Topic is required" in result["error"]
        
        # Verify context was marked as failed
        mock_context.mark_failed.assert_called_once()
    
    @pytest.mark.asyncio()
    async def test_task_decomposition_missing_llm_interface(self, decomposition_node, mock_context):
        """Test decomposition with missing LLM interface."""
        # Setup
        inputs = {"topic": "AI对就业的影响"}
        
        # Execute
        result = await decomposition_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "LLM interface not available" in result["error"]
    
    def test_extract_json_from_text(self, decomposition_node):
        """Test JSON extraction from text."""
        # Test with JSON in triple backticks
        text = """Here's the decomposition:

```json
[
  {
    "perspective": "经济",
    "description": "分析影响",
    "questions": ["问题1", "问题2"],
    "expertise_required": ["经济学"],
    "priority": 1
  }
]
```"""
        result = decomposition_node._extract_json_from_text(text)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["perspective"] == "经济"
        
        # Test with JSON without backticks
        text = """Here's the decomposition:

[
  {
    "perspective": "经济",
    "description": "分析影响",
    "questions": ["问题1", "问题2"],
    "expertise_required": ["经济学"],
    "priority": 1
  }
]"""
        result = decomposition_node._extract_json_from_text(text)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["perspective"] == "经济"
        
        # Test with invalid JSON
        text = "This is not JSON"
        result = decomposition_node._extract_json_from_text(text)
        assert result == []


class TestParallelExplorationNode:
    """Test cases for ParallelExplorationNode."""
    
    @pytest.fixture()
    def exploration_node(self):
        """Create a ParallelExplorationNode instance for testing."""
        return ParallelExplorationNode("explore_1", {
            "max_parallel_experts": 3,
            "expert_roles": {
                "economist": ["经济学", "劳动经济学"],
                "sociologist": ["社会学", "公共政策"],
                "technologist": ["计算机科学", "AI研究"]
            },
            "default_expert_role": "专家",
            "use_tools": True
        })
    
    @pytest.fixture()
    def mock_context(self):
        """Create a mock execution context."""
        context = Mock(spec=ExecutionContext)
        context.execution_id = "exec_123"
        context.node_id = "node_explore"
        context.state = {
            "topic": "AI对就业的影响",
            "sub_problems": [
                {
                    "id": "sub_1",
                    "perspective": "经济",
                    "description": "分析AI对就业市场的经济影响",
                    "questions": ["AI如何影响就业率?", "哪些行业最受影响?"],
                    "expertise_required": ["经济学", "劳动经济学"],
                    "priority": 1
                },
                {
                    "id": "sub_2",
                    "perspective": "社会",
                    "description": "探讨AI对社会结构的影响",
                    "questions": ["AI如何影响社会阶层?"],
                    "expertise_required": ["社会学", "公共政策"],
                    "priority": 2
                }
            ]
        }
        context.services = {}
        context.mark_started = Mock()
        context.mark_completed = Mock()
        context.mark_failed = Mock()
        return context
    
    @pytest.fixture()
    def mock_llm_interface(self):
        """Create a mock LLM interface."""
        llm = AsyncMock()
        
        async def generate_side_effect(messages):
            content = messages[1]["content"]
            if "经济" in content:
                return {
                    "content": """以下是我的分析：

```json
{
  "viewpoint": "AI将导致短期就业市场波动，但长期将创造新的就业机会。",
  "supporting_evidence": ["历史技术革命数据", "最新就业市场研究"],
  "reasoning_process": "基于历史技术革命的模式分析...",
  "confidence": 0.8
}
```"""
                }
            else:
                return {
                    "content": """以下是我的分析：

```json
{
  "viewpoint": "AI可能加剧社会不平等，需要政策干预。",
  "supporting_evidence": ["收入差距研究", "技术采用模式"],
  "reasoning_process": "通过社会学理论分析...",
  "confidence": 0.7
}
```"""
                }
        
        llm.generate.side_effect = generate_side_effect
        return llm
    
    @pytest.fixture()
    def mock_role_manager(self):
        """Create a mock role manager."""
        role_manager = Mock()
        
        def get_role_by_id_side_effect(role_id):
            if role_id == "economist":
                role = Mock()
                role.system_prompt = "你是一位经济学专家，擅长分析经济趋势和就业市场。"
                role.name = "经济学家"
                return role
            elif role_id == "sociologist":
                role = Mock()
                role.system_prompt = "你是一位社会学专家，擅长分析社会结构和不平等问题。"
                role.name = "社会学家"
                return role
            return None
        
        role_manager.get_role_by_id.side_effect = get_role_by_id_side_effect
        return role_manager
    
    @pytest.fixture()
    def mock_tool_executor(self):
        """Create a mock tool executor."""
        tool_executor = Mock()
        tool_executor.execute.return_value = {
            "status": "success",
            "result": "研究表明，AI对就业的影响因行业而异，高度重复性工作最容易被替代。"
        }
        return tool_executor
    
    @pytest.mark.asyncio()
    async def test_parallel_exploration_success(self, exploration_node, mock_context, mock_llm_interface, mock_role_manager, mock_tool_executor):
        """Test successful parallel exploration."""
        # Setup
        mock_context.services["llm_interface"] = mock_llm_interface
        mock_context.services["role_manager"] = mock_role_manager
        mock_context.services["tool_executor"] = mock_tool_executor
        
        # Execute
        result = await exploration_node.execute({}, mock_context)
        
        # Verify
        assert result["success"] is True
        assert result["viewpoint_count"] == 2
        assert len(result["viewpoints"]) == 2
        
        # Verify viewpoint details
        viewpoints = result["viewpoints"]
        expert_ids = [vp["expert_id"] for vp in viewpoints]
        assert "economist" in expert_ids
        assert "sociologist" in expert_ids
        
        # Verify context state was updated
        assert "viewpoints" in mock_context.state
        assert len(mock_context.state["viewpoints"]) == 2
        
        # Verify context methods were called
        mock_context.mark_started.assert_called_once()
        mock_context.mark_completed.assert_called_once()
        
        # Verify LLM was called correctly
        assert mock_llm_interface.generate.call_count == 2
        
        # Verify tool executor was called
        assert mock_tool_executor.execute.call_count == 2
    
    @pytest.mark.asyncio()
    async def test_parallel_exploration_no_sub_problems(self, exploration_node, mock_context):
        """Test exploration with no sub-problems."""
        # Setup
        mock_context.state = {}
        
        # Execute
        result = await exploration_node.execute({}, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "error" in result
        assert "Sub-problems are required" in result["error"]
        
        # Verify context was marked as failed
        mock_context.mark_failed.assert_called_once()
    
    @pytest.mark.asyncio()
    async def test_parallel_exploration_missing_llm_interface(self, exploration_node, mock_context):
        """Test exploration with missing LLM interface."""
        # Execute
        result = await exploration_node.execute({}, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "LLM interface not available" in result["error"]
    
    def test_select_expert_role(self, exploration_node):
        """Test expert role selection based on required expertise."""
        # Test with matching expertise
        role = exploration_node._select_expert_role(["经济学", "劳动经济学"])
        assert role == "economist"
        
        # Test with partial match
        role = exploration_node._select_expert_role(["社会学", "心理学"])
        assert role == "sociologist"
        
        # Test with no match
        role = exploration_node._select_expert_role(["心理学", "教育学"])
        assert role == "专家"  # Default role
        
        # Test with empty expertise
        role = exploration_node._select_expert_role([])
        assert role == "专家"  # Default role


class TestViewpointSynthesisNode:
    """Test cases for ViewpointSynthesisNode."""
    
    @pytest.fixture()
    def synthesis_node(self):
        """Create a ViewpointSynthesisNode instance for testing."""
        return ViewpointSynthesisNode("synth_1", {
            "synthesis_method": "dialectical",
            "min_confidence_threshold": 0.6,
            "include_expert_attribution": True
        })
    
    @pytest.fixture()
    def mock_context(self):
        """Create a mock execution context."""
        context = Mock(spec=ExecutionContext)
        context.execution_id = "exec_123"
        context.node_id = "node_synth"
        context.state = {
            "topic": "AI对就业的影响",
            "viewpoints": [
                {
                    "expert_id": "economist",
                    "expert_name": "经济学家",
                    "expertise_areas": ["经济学", "劳动经济学"],
                    "sub_problem_id": "sub_1",
                    "viewpoint": "AI将导致短期就业市场波动，但长期将创造新的就业机会。",
                    "supporting_evidence": ["历史技术革命数据", "最新就业市场研究"],
                    "confidence": 0.8,
                    "reasoning_process": "基于历史技术革命的模式分析...",
                    "metadata": {"perspective": "经济"}
                },
                {
                    "expert_id": "sociologist",
                    "expert_name": "社会学家",
                    "expertise_areas": ["社会学", "公共政策"],
                    "sub_problem_id": "sub_2",
                    "viewpoint": "AI可能加剧社会不平等，需要政策干预。",
                    "supporting_evidence": ["收入差距研究", "技术采用模式"],
                    "confidence": 0.7,
                    "reasoning_process": "通过社会学理论分析...",
                    "metadata": {"perspective": "社会"}
                }
            ]
        }
        context.services = {}
        context.mark_started = Mock()
        context.mark_completed = Mock()
        context.mark_failed = Mock()
        return context
    
    @pytest.fixture()
    def mock_synthesis_engine(self):
        """Create a mock synthesis engine."""
        engine = AsyncMock()
        engine.synthesize_opinions.return_value = """综合分析表明，AI对就业的影响是多方面的：

1. 短期内，AI将导致某些行业就业岗位减少，特别是高度重复性工作。
2. 长期来看，新的就业机会将会出现，但需要劳动力具备新的技能。
3. 社会不平等可能加剧，因为技术采用和适应能力存在差异。
4. 需要政策干预来确保AI带来的利益公平分配。
5. 教育和培训体系需要改革，以适应AI时代的技能需求。

总的来说，AI对就业的影响既有挑战也有机遇，关键在于如何通过政策和教育体系的调整来最大化机遇并减少负面影响。"""
        return engine
    
    @pytest.mark.asyncio()
    async def test_viewpoint_synthesis_success(self, synthesis_node, mock_context, mock_synthesis_engine):
        """Test successful viewpoint synthesis."""
        # Setup
        mock_context.services["synthesis_engine"] = mock_synthesis_engine
        
        # Execute
        result = await synthesis_node.execute({}, mock_context)
        
        # Verify
        assert result["success"] is True
        assert result["topic"] == "AI对就业的影响"
        assert "AI对就业的影响是多方面的" in result["synthesis"]
        assert len(result["key_insights"]) > 0
        assert "经济学家" in result["expert_contributions"]
        assert "社会学家" in result["expert_contributions"]
        assert result["confidence"] >= 0.6
        
        # Verify context state was updated
        assert "synthesis_result" in mock_context.state
        
        # Verify context methods were called
        mock_context.mark_started.assert_called_once()
        mock_context.mark_completed.assert_called_once()
        
        # Verify synthesis engine was called correctly
        mock_synthesis_engine.synthesize_opinions.assert_called_once()
        call_args = mock_synthesis_engine.synthesize_opinions.call_args
        assert call_args[1]["topic"] == "AI对就业的影响"
    
    @pytest.mark.asyncio()
    async def test_viewpoint_synthesis_no_viewpoints(self, synthesis_node, mock_context):
        """Test synthesis with no viewpoints."""
        # Setup
        mock_context.state = {"topic": "AI对就业的影响"}
        
        # Execute
        result = await synthesis_node.execute({}, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "error" in result
        assert "Viewpoints are required" in result["error"]
        
        # Verify context was marked as failed
        mock_context.mark_failed.assert_called_once()
    
    @pytest.mark.asyncio()
    async def test_viewpoint_synthesis_missing_synthesis_engine(self, synthesis_node, mock_context):
        """Test synthesis with missing synthesis engine."""
        # Execute
        result = await synthesis_node.execute({}, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "Synthesis engine not available" in result["error"]
    
    def test_extract_key_insights(self, synthesis_node):
        """Test key insight extraction from synthesis text."""
        # Test with numbered list
        text = """分析结果：

1. 短期内，AI将导致某些行业就业岗位减少。
2. 长期来看，新的就业机会将会出现。
3. 社会不平等可能加剧。"""
        
        insights = synthesis_node._extract_key_insights(text)
        assert len(insights) == 3
        assert "短期内，AI将导致某些行业就业岗位减少" in insights
        
        # Test with bullet points
        text = """分析结果：

• 短期内，AI将导致某些行业就业岗位减少。
• 长期来看，新的就业机会将会出现。
• 社会不平等可能加剧。"""
        
        insights = synthesis_node._extract_key_insights(text)
        assert len(insights) == 3
        assert "短期内，AI将导致某些行业就业岗位减少" in insights
        
        # Test with insight sections
        text = """分析结果：

关键发现：短期内，AI将导致某些行业就业岗位减少。长期来看，新的就业机会将会出现。

结论：需要政策干预来确保AI带来的利益公平分配。"""
        
        insights = synthesis_node._extract_key_insights(text)
        assert len(insights) > 0
    
    def test_calculate_synthesis_confidence(self, synthesis_node):
        """Test synthesis confidence calculation."""
        # Test with multiple viewpoints
        viewpoints = [
            ExpertViewpoint(
                expert_id="economist",
                expert_name="经济学家",
                sub_problem_id="sub_1",
                viewpoint="观点1",
                confidence=0.8,
                metadata={"priority": 1}
            ),
            ExpertViewpoint(
                expert_id="sociologist",
                expert_name="社会学家",
                sub_problem_id="sub_2",
                viewpoint="观点2",
                confidence=0.6,
                metadata={"priority": 2}
            )
        ]
        
        confidence = synthesis_node._calculate_synthesis_confidence(viewpoints)
        assert 0.6 <= confidence <= 0.8
        
        # Test with empty viewpoints
        confidence = synthesis_node._calculate_synthesis_confidence([])
        assert confidence == 0.0


if __name__ == "__main__":
    pytest.main([__file__])