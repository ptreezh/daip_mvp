# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 15:30:00
@Author  : DAIP-LIVE Team
@File    : test_multi_perspective_workflow.py
@Description:
    Unit tests for the MultiPerspectiveSynthesisWorkflow class.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from src.workflows.multi_perspective_workflow import MultiPerspectiveSynthesisWorkflow


class TestMultiPerspectiveSynthesisWorkflow:
    """Test cases for MultiPerspectiveSynthesisWorkflow."""
    
    @pytest.fixture
    def workflow(self):
        """Create a MultiPerspectiveSynthesisWorkflow instance for testing."""
        return MultiPerspectiveSynthesisWorkflow("test_workflow")
    
    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing."""
        services = {
            "llm_interface": AsyncMock(),
            "role_manager": Mock(),
            "tool_executor": Mock(),
            "synthesis_engine": AsyncMock()
        }
        
        # Configure LLM interface
        services["llm_interface"].generate.return_value = {
            "content": "Generated content for testing"
        }
        
        # Configure synthesis engine
        services["synthesis_engine"].synthesize_opinions.return_value = "Synthesized content for testing"
        
        return services
    
    def test_workflow_initialization(self, workflow):
        """Test workflow initialization with default config."""
        assert workflow.workflow_id == "test_workflow"
        assert "task_decomposition" in workflow.config
        assert "parallel_exploration" in workflow.config
        assert "viewpoint_synthesis" in workflow.config
        
        # Verify nodes were created
        assert workflow.task_decomposition_node is not None
        assert workflow.parallel_exploration_node is not None
        assert workflow.viewpoint_synthesis_node is not None
    
    def test_workflow_custom_config(self):
        """Test workflow initialization with custom config."""
        custom_config = {
            "task_decomposition": {
                "planner_role": "高级规划者",
                "default_perspectives": ["政治", "经济", "文化"]
            },
            "viewpoint_synthesis": {
                "synthesis_method": "weighted",
                "min_confidence_threshold": 0.7
            }
        }
        
        workflow = MultiPerspectiveSynthesisWorkflow("custom_workflow", custom_config)
        
        # Verify custom config was applied
        assert workflow.config["task_decomposition"]["planner_role"] == "高级规划者"
        assert workflow.config["task_decomposition"]["default_perspectives"] == ["政治", "经济", "文化"]
        assert workflow.config["viewpoint_synthesis"]["synthesis_method"] == "weighted"
        assert workflow.config["viewpoint_synthesis"]["min_confidence_threshold"] == 0.7
        
        # Verify default config for unspecified sections
        assert workflow.config["parallel_exploration"]["max_parallel_experts"] == 5
        assert workflow.config["parallel_exploration"]["default_expert_role"] == "专家"
    
    @pytest.mark.asyncio
    async def test_workflow_execute_success(self, workflow, mock_services):
        """Test successful workflow execution."""
        # Mock all node executions to return success
        with patch.object(workflow.task_decomposition_node, 'execute', AsyncMock(return_value={
                "success": True, 
                "topic": "AI对就业的影响", 
                "sub_problems": [{"id": "sub_1", "perspective": "经济"}],
                "sub_problem_count": 1
            })), \
             patch.object(workflow.parallel_exploration_node, 'execute', AsyncMock(return_value={
                "success": True, 
                "viewpoints": [{"expert_id": "economist", "viewpoint": "观点1"}],
                "viewpoint_count": 1
            })), \
             patch.object(workflow.viewpoint_synthesis_node, 'execute', AsyncMock(return_value={
                "success": True, 
                "synthesis": "综合分析结果", 
                "key_insights": ["洞察1", "洞察2"],
                "expert_contributions": {"经济学家": ["贡献1"]},
                "confidence": 0.8
            })):
            
            result = await workflow.execute("AI对就业的影响", ["经济", "社会"], mock_services)
            
            # Verify result
            assert result["success"] is True
            assert result["topic"] == "AI对就业的影响"
            assert result["synthesis"] == "综合分析结果"
            assert "洞察1" in result["key_insights"]
            assert "经济学家" in result["expert_contributions"]
            assert result["confidence"] == 0.8
            assert "execution_details" in result
    
    @pytest.mark.asyncio
    async def test_workflow_execute_decomposition_failure(self, workflow, mock_services):
        """Test workflow execution when decomposition fails."""
        # Mock decomposition to fail
        with patch.object(workflow.task_decomposition_node, 'execute', AsyncMock(return_value={
                "success": False, 
                "error": "Decomposition error"
            })):
            
            result = await workflow.execute("AI对就业的影响", ["经济", "社会"], mock_services)
            
            # Verify result
            assert result["success"] is False
            assert "error" in result
            assert "Task decomposition failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_workflow_execute_exploration_failure(self, workflow, mock_services):
        """Test workflow execution when exploration fails."""
        # Mock decomposition to succeed but exploration to fail
        with patch.object(workflow.task_decomposition_node, 'execute', AsyncMock(return_value={
                "success": True, 
                "topic": "AI对就业的影响", 
                "sub_problems": [{"id": "sub_1", "perspective": "经济"}],
                "sub_problem_count": 1
            })), \
             patch.object(workflow.parallel_exploration_node, 'execute', AsyncMock(return_value={
                "success": False, 
                "error": "Exploration error"
            })):
            
            result = await workflow.execute("AI对就业的影响", ["经济", "社会"], mock_services)
            
            # Verify result
            assert result["success"] is False
            assert "error" in result
            assert "Parallel exploration failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_workflow_execute_synthesis_failure(self, workflow, mock_services):
        """Test workflow execution when synthesis fails."""
        # Mock decomposition and exploration to succeed but synthesis to fail
        with patch.object(workflow.task_decomposition_node, 'execute', AsyncMock(return_value={
                "success": True, 
                "topic": "AI对就业的影响", 
                "sub_problems": [{"id": "sub_1", "perspective": "经济"}],
                "sub_problem_count": 1
            })), \
             patch.object(workflow.parallel_exploration_node, 'execute', AsyncMock(return_value={
                "success": True, 
                "viewpoints": [{"expert_id": "economist", "viewpoint": "观点1"}],
                "viewpoint_count": 1
            })), \
             patch.object(workflow.viewpoint_synthesis_node, 'execute', AsyncMock(return_value={
                "success": False, 
                "error": "Synthesis error"
            })):
            
            result = await workflow.execute("AI对就业的影响", ["经济", "社会"], mock_services)
            
            # Verify result
            assert result["success"] is False
            assert "error" in result
            assert "Viewpoint synthesis failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_workflow_class_method(self, mock_services):
        """Test the class method for executing a workflow."""
        # Mock the workflow execute method
        with patch.object(MultiPerspectiveSynthesisWorkflow, 'execute', AsyncMock(return_value={
                "success": True, 
                "result": "test"
            })):
            
            result = await MultiPerspectiveSynthesisWorkflow.execute_multi_perspective_synthesis(
                "AI对就业的影响",
                ["经济", "社会"],
                mock_services,
                {"task_decomposition": {"planner_role": "测试规划者"}}
            )
            
            # Verify result
            assert result["success"] is True
            assert result["result"] == "test"


if __name__ == "__main__":
    pytest.main([__file__])