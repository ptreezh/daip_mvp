# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 10:30:00
@Author  : DAIP-LIVE Team
@File    : test_critical_review_workflow.py
@Description:
    Unit tests for the CriticalReviewWorkflow class.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from src.workflows.critical_review_workflow import CriticalReviewWorkflow


class TestCriticalReviewWorkflow:
    """Test cases for CriticalReviewWorkflow."""
    
    @pytest.fixture
    def workflow(self):
        """Create a CriticalReviewWorkflow instance for testing."""
        return CriticalReviewWorkflow("test_workflow")
    
    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing."""
        services = {
            "llm_interface": AsyncMock(),
            "fact_extraction_service": AsyncMock(),
            "wiki_service": AsyncMock(),
            "synthesis_engine": AsyncMock()
        }
        
        # Configure LLM interface
        services["llm_interface"].generate.return_value = {
            "content": "Generated content for testing"
        }
        
        # Configure fact extraction service
        services["fact_extraction_service"].extract_facts.return_value = [
            {
                "content": "Test fact 1",
                "confidence": 0.8,
                "location": "paragraph_1",
                "type": "general",
                "method": "llm"
            }
        ]
        
        return services
    
    def test_workflow_initialization(self, workflow):
        """Test workflow initialization with default config."""
        assert workflow.workflow_id == "test_workflow"
        assert "generation" in workflow.config
        assert "fact_extraction" in workflow.config
        assert "parallel_review" in workflow.config
        assert "evidence_aggregation" in workflow.config
        assert "consensus" in workflow.config
        assert "revision" in workflow.config
        
        # Verify nodes were created
        assert workflow.generation_node is not None
        assert workflow.fact_extraction_node is not None
        assert workflow.parallel_review_node is not None
        assert workflow.evidence_aggregation_node is not None
        assert workflow.consensus_node is not None
        assert workflow.revision_node is not None
    
    def test_workflow_custom_config(self):
        """Test workflow initialization with custom config."""
        custom_config = {
            "generation": {
                "role_name": "专家创作者"
            },
            "consensus": {
                "consensus_method": "majority_vote",
                "credibility_threshold": 0.8
            }
        }
        
        workflow = CriticalReviewWorkflow("custom_workflow", custom_config)
        
        # Verify custom config was applied
        assert workflow.config["generation"]["role_name"] == "专家创作者"
        assert workflow.config["consensus"]["consensus_method"] == "majority_vote"
        assert workflow.config["consensus"]["credibility_threshold"] == 0.8
        
        # Verify default config for unspecified sections
        assert workflow.config["fact_extraction"]["min_confidence"] == 0.6
        assert workflow.config["revision"]["revision_role"] == "创作者"
    
    @pytest.mark.asyncio
    async def test_workflow_execute_success(self, workflow, mock_services):
        """Test successful workflow execution."""
        # Mock all node executions to return success
        with patch.object(workflow.generation_node, 'execute', AsyncMock(return_value={"success": True, "content": "Test content"})), \
             patch.object(workflow.fact_extraction_node, 'execute', AsyncMock(return_value={"success": True, "fact_count": 3, "facts": []})), \
             patch.object(workflow.parallel_review_node, 'execute', AsyncMock(return_value={"success": True, "review_count": 6})), \
             patch.object(workflow.evidence_aggregation_node, 'execute', AsyncMock(return_value={"success": True, "facts_processed": 3})), \
             patch.object(workflow.consensus_node, 'execute', AsyncMock(return_value={"success": True, "facts_needing_revision": ["fact_1"], "credibility_scores": {"fact_1": 0.4}})), \
             patch.object(workflow.revision_node, 'execute', AsyncMock(return_value={"success": True, "revised_content": "Revised content", "revision_needed": True, "revision_summary": "Revised 1 fact"})):
            
            result = await workflow.execute("Test prompt", "Test context", mock_services)
            
            # Verify result
            assert result["success"] is True
            assert result["original_content"] == "Test content"
            assert result["final_content"] == "Revised content"
            assert result["revision_needed"] is True
            assert result["facts_extracted"] == 3
            assert result["facts_reviewed"] == 6
            assert result["facts_needing_revision"] == 1
            assert "execution_details" in result
    
    @pytest.mark.asyncio
    async def test_workflow_execute_no_revision_needed(self, workflow, mock_services):
        """Test workflow execution when no revision is needed."""
        # Mock all node executions to return success, but with no facts needing revision
        with patch.object(workflow.generation_node, 'execute', AsyncMock(return_value={"success": True, "content": "Test content"})), \
             patch.object(workflow.fact_extraction_node, 'execute', AsyncMock(return_value={"success": True, "fact_count": 3, "facts": []})), \
             patch.object(workflow.parallel_review_node, 'execute', AsyncMock(return_value={"success": True, "review_count": 6})), \
             patch.object(workflow.evidence_aggregation_node, 'execute', AsyncMock(return_value={"success": True, "facts_processed": 3})), \
             patch.object(workflow.consensus_node, 'execute', AsyncMock(return_value={"success": True, "facts_needing_revision": [], "credibility_scores": {"fact_1": 0.8}})), \
             patch.object(workflow.revision_node, 'execute', AsyncMock(return_value={"success": True, "revised_content": "Test content", "revision_needed": False, "revision_summary": "No revision needed"})):
            
            result = await workflow.execute("Test prompt", "Test context", mock_services)
            
            # Verify result
            assert result["success"] is True
            assert result["original_content"] == "Test content"
            assert result["final_content"] == "Test content"  # Same as original
            assert result["revision_needed"] is False
            assert result["facts_needing_revision"] == 0
    
    @pytest.mark.asyncio
    async def test_workflow_execute_generation_failure(self, workflow, mock_services):
        """Test workflow execution when generation fails."""
        # Mock generation to fail
        with patch.object(workflow.generation_node, 'execute', AsyncMock(return_value={"success": False, "error": "Generation error"})):
            result = await workflow.execute("Test prompt", "Test context", mock_services)
            
            # Verify result
            assert result["success"] is False
            assert "error" in result
            assert "Generation" in result["error"]
    
    @pytest.mark.asyncio
    async def test_workflow_execute_fact_extraction_failure(self, workflow, mock_services):
        """Test workflow execution when fact extraction fails."""
        # Mock generation to succeed but fact extraction to fail
        with patch.object(workflow.generation_node, 'execute', AsyncMock(return_value={"success": True, "content": "Test content"})), \
             patch.object(workflow.fact_extraction_node, 'execute', AsyncMock(return_value={"success": False, "error": "Extraction error"})):
            
            result = await workflow.execute("Test prompt", "Test context", mock_services)
            
            # Verify result
            assert result["success"] is False
            assert "error" in result
            assert "Fact extraction" in result["error"]
    
    @pytest.mark.asyncio
    async def test_workflow_class_method(self, mock_services):
        """Test the class method for executing a workflow."""
        # Mock the workflow execute method
        with patch.object(CriticalReviewWorkflow, 'execute', AsyncMock(return_value={"success": True, "result": "test"})):
            result = await CriticalReviewWorkflow.execute_critical_review(
                "Test prompt",
                "Test context",
                mock_services,
                {"generation": {"role_name": "测试角色"}}
            )
            
            # Verify result
            assert result["success"] is True
            assert result["result"] == "test"


if __name__ == "__main__":
    pytest.main([__file__])