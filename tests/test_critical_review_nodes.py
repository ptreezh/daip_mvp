# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-23 13:30:00
@Author  : DAIP-LIVE Team
@File    : test_critical_review_nodes.py
@Description:
    Unit tests for Critical Review Workflow nodes.
"""
import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

try:
    from src.institutional_primitives.critical_review_nodes import (
        GenerationNode,
        FactExtractionNode,
        ParallelReviewNode,
        EvidenceAggregationNode,
        ExtractedFact,
        Evidence,
        EvidenceReport
    )
except ImportError as e:
    print(f"Import error: {e}")
    # Create mock classes for testing
    class GenerationNode:
        pass
    class FactExtractionNode:
        pass
    class ParallelReviewNode:
        pass
    class EvidenceAggregationNode:
        pass
    class ExtractedFact:
        pass
    class Evidence:
        pass
    class EvidenceReport:
        pass
from src.institutional_primitives.base import ExecutionContext


class TestGenerationNode:
    """Test cases for GenerationNode."""
    
    @pytest.fixture
    def generation_node(self):
        """Create a GenerationNode instance for testing."""
        return GenerationNode("gen_1", {"role_name": "测试创作者", "capture_metadata": True})
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock execution context."""
        context = Mock(spec=ExecutionContext)
        context.execution_id = "exec_123"
        context.node_id = "node_gen"
        context.state = {}
        context.services = {}
        context.mark_started = Mock()
        context.mark_completed = Mock()
        context.mark_failed = Mock()
        return context
    
    @pytest.fixture
    def mock_llm_interface(self):
        """Create a mock LLM interface."""
        llm = AsyncMock()
        llm.generate.return_value = {
            "content": "这是生成的测试内容，包含一些事实声明。",
            "model": "test-model",
            "usage": {"tokens": 100}
        }
        return llm
    
    @pytest.mark.asyncio
    async def test_generation_node_success(self, generation_node, mock_context, mock_llm_interface):
        """Test successful content generation."""
        # Setup
        mock_context.services["llm_interface"] = mock_llm_interface
        inputs = {
            "prompt": "请生成一些关于机器学习的内容",
            "role_context": "你是一个AI专家"
        }
        
        # Execute
        result = await generation_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is True
        assert result["content"] == "这是生成的测试内容，包含一些事实声明。"
        assert "metadata" in result
        assert result["metadata"]["role_name"] == "测试创作者"
        assert "generation_timestamp" in result["metadata"]
        
        # Verify context state was updated
        assert mock_context.state["original_content"] == "这是生成的测试内容，包含一些事实声明。"
        
        # Verify context methods were called
        mock_context.mark_started.assert_called_once()
        mock_context.mark_completed.assert_called_once()
        
        # Verify LLM was called correctly
        mock_llm_interface.generate.assert_called_once()
        call_args = mock_llm_interface.generate.call_args[0][0]
        assert len(call_args) == 1
        assert "测试创作者" in call_args[0]["content"]
    
    @pytest.mark.asyncio
    async def test_generation_node_missing_prompt(self, generation_node, mock_context):
        """Test generation with missing prompt."""
        # Setup
        inputs = {}
        
        # Execute
        result = await generation_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "error" in result
        assert "Prompt is required" in result["error"]
        
        # Verify context was marked as failed
        mock_context.mark_failed.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generation_node_missing_llm_interface(self, generation_node, mock_context):
        """Test generation with missing LLM interface."""
        # Setup
        inputs = {"prompt": "test prompt"}
        
        # Execute
        result = await generation_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "LLM interface not available" in result["error"]
    
    def test_generation_node_schemas(self, generation_node):
        """Test input and output schemas."""
        input_schema = generation_node.get_input_schema()
        output_schema = generation_node.get_output_schema()
        
        # Verify input schema
        assert input_schema["type"] == "object"
        assert "prompt" in input_schema["properties"]
        assert "prompt" in input_schema["required"]
        
        # Verify output schema
        assert output_schema["type"] == "object"
        assert "content" in output_schema["properties"]
        assert "success" in output_schema["properties"]


class TestFactExtractionNode:
    """Test cases for FactExtractionNode."""
    
    @pytest.fixture
    def fact_extraction_node(self):
        """Create a FactExtractionNode instance for testing."""
        return FactExtractionNode("fact_1", {"min_confidence": 0.6, "max_facts": 10})
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock execution context."""
        context = Mock(spec=ExecutionContext)
        context.execution_id = "exec_123"
        context.node_id = "node_fact"
        context.state = {"original_content": "测试内容包含一些事实"}
        context.services = {}
        context.mark_started = Mock()
        context.mark_completed = Mock()
        context.mark_failed = Mock()
        return context
    
    @pytest.fixture
    def mock_fact_service(self):
        """Create a mock fact extraction service."""
        service = AsyncMock()
        service.extract_facts.return_value = [
            {
                "content": "机器学习是人工智能的一个分支",
                "confidence": 0.8,
                "location": "paragraph_1",
                "type": "definition",
                "method": "llm"
            },
            {
                "content": "深度学习使用神经网络",
                "confidence": 0.7,
                "location": "paragraph_2",
                "type": "technical",
                "method": "llm"
            },
            {
                "content": "低置信度事实",
                "confidence": 0.3,
                "location": "paragraph_3",
                "type": "general",
                "method": "llm"
            }
        ]
        return service
    
    @pytest.mark.asyncio
    async def test_fact_extraction_success(self, fact_extraction_node, mock_context, mock_fact_service):
        """Test successful fact extraction."""
        # Setup
        mock_context.services["fact_extraction_service"] = mock_fact_service
        inputs = {"content": "测试内容包含机器学习和深度学习的事实"}
        
        # Execute
        result = await fact_extraction_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is True
        assert result["fact_count"] == 2  # Only facts above confidence threshold
        assert len(result["facts"]) == 2
        
        # Verify fact details
        fact1 = result["facts"][0]
        assert fact1["content"] == "机器学习是人工智能的一个分支"
        assert fact1["confidence"] == 0.8
        assert fact1["fact_type"] == "definition"
        
        # Verify context state was updated
        assert "extracted_facts" in mock_context.state
        assert len(mock_context.state["extracted_facts"]) == 2
        
        # Verify service was called
        mock_fact_service.extract_facts.assert_called_once_with("测试内容包含机器学习和深度学习的事实")
    
    @pytest.mark.asyncio
    async def test_fact_extraction_from_state(self, fact_extraction_node, mock_context, mock_fact_service):
        """Test fact extraction using content from workflow state."""
        # Setup
        mock_context.services["fact_extraction_service"] = mock_fact_service
        inputs = {}  # No content in inputs, should use state
        
        # Execute
        result = await fact_extraction_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is True
        mock_fact_service.extract_facts.assert_called_once_with("测试内容包含一些事实")
    
    @pytest.mark.asyncio
    async def test_fact_extraction_no_content(self, fact_extraction_node, mock_context):
        """Test fact extraction with no content."""
        # Setup
        mock_context.state = {}  # No content in state either
        inputs = {}
        
        # Execute
        result = await fact_extraction_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "Content is required" in result["error"]
    
    @pytest.mark.asyncio
    async def test_fact_extraction_missing_service(self, fact_extraction_node, mock_context):
        """Test fact extraction with missing service."""
        # Setup
        inputs = {"content": "test content"}
        
        # Execute
        result = await fact_extraction_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "Fact extraction service not available" in result["error"]


class TestParallelReviewNode:
    """Test cases for ParallelReviewNode."""
    
    @pytest.fixture
    def parallel_review_node(self):
        """Create a ParallelReviewNode instance for testing."""
        return ParallelReviewNode("review_1", {
            "reviewer_roles": ["批判者", "验证者"],
            "max_parallel_reviews": 3
        })
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock execution context."""
        context = Mock(spec=ExecutionContext)
        context.execution_id = "exec_123"
        context.node_id = "node_review"
        context.state = {}
        context.services = {}
        context.mark_started = Mock()
        context.mark_completed = Mock()
        context.mark_failed = Mock()
        return context
    
    @pytest.fixture
    def mock_llm_interface(self):
        """Create a mock LLM interface."""
        llm = AsyncMock()
        llm.generate.return_value = {
            "content": "这是详细的审查分析，包含具体的证据和推理过程。"
        }
        return llm
    
    @pytest.fixture
    def sample_facts(self):
        """Create sample extracted facts for testing."""
        return [
            {
                "id": "fact_1",
                "content": "机器学习是人工智能的一个分支",
                "confidence": 0.8,
                "source_location": "paragraph_1",
                "fact_type": "definition",
                "metadata": {}
            },
            {
                "id": "fact_2",
                "content": "深度学习使用神经网络",
                "confidence": 0.7,
                "source_location": "paragraph_2",
                "fact_type": "technical",
                "metadata": {}
            }
        ]
    
    @pytest.mark.asyncio
    async def test_parallel_review_success(self, parallel_review_node, mock_context, mock_llm_interface, sample_facts):
        """Test successful parallel review."""
        # Setup
        mock_context.services["llm_interface"] = mock_llm_interface
        inputs = {"facts": sample_facts}
        
        # Execute
        result = await parallel_review_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is True
        assert result["review_count"] > 0
        assert len(result["evidence_reports"]) > 0
        
        # Should have reviews from both roles for each fact
        expected_reviews = len(sample_facts) * len(parallel_review_node.reviewer_roles)
        assert result["review_count"] == expected_reviews
        
        # Verify context state was updated
        assert "evidence_reports" in mock_context.state
        
        # Verify LLM was called multiple times (once per fact per reviewer)
        assert mock_llm_interface.generate.call_count == expected_reviews
    
    @pytest.mark.asyncio
    async def test_parallel_review_from_state(self, parallel_review_node, mock_context, mock_llm_interface, sample_facts):
        """Test parallel review using facts from workflow state."""
        # Setup
        mock_context.services["llm_interface"] = mock_llm_interface
        mock_context.state["extracted_facts"] = sample_facts
        inputs = {}  # No facts in inputs, should use state
        
        # Execute
        result = await parallel_review_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is True
        assert result["review_count"] > 0
    
    @pytest.mark.asyncio
    async def test_parallel_review_no_facts(self, parallel_review_node, mock_context):
        """Test parallel review with no facts."""
        # Setup
        inputs = {}
        
        # Execute
        result = await parallel_review_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "Facts are required" in result["error"]
    
    @pytest.mark.asyncio
    async def test_parallel_review_missing_llm(self, parallel_review_node, mock_context, sample_facts):
        """Test parallel review with missing LLM interface."""
        # Setup
        inputs = {"facts": sample_facts}
        
        # Execute
        result = await parallel_review_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "LLM interface not available" in result["error"]


class TestEvidenceAggregationNode:
    """Test cases for EvidenceAggregationNode."""
    
    @pytest.fixture
    def evidence_aggregation_node(self):
        """Create an EvidenceAggregationNode instance for testing."""
        return EvidenceAggregationNode("agg_1", {
            "min_evidence_threshold": 2,
            "weight_by_credibility": True
        })
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock execution context."""
        context = Mock(spec=ExecutionContext)
        context.execution_id = "exec_123"
        context.node_id = "node_agg"
        context.state = {}
        context.services = {}
        context.mark_started = Mock()
        context.mark_completed = Mock()
        context.mark_failed = Mock()
        return context
    
    @pytest.fixture
    def sample_evidence_reports(self):
        """Create sample evidence reports for testing."""
        return [
            {
                "fact_id": "fact_1",
                "supporting_evidence": [
                    {
                        "content": "支持性证据1",
                        "source": "验证者_review",
                        "credibility": 0.8,
                        "evidence_type": "supporting",
                        "metadata": {}
                    }
                ],
                "challenging_evidence": [],
                "neutral_evidence": [],
                "overall_assessment": "事实得到验证",
                "confidence_score": 0.8,
                "reviewer_id": "验证者",
                "review_timestamp": datetime.now().isoformat()
            },
            {
                "fact_id": "fact_1",
                "supporting_evidence": [],
                "challenging_evidence": [
                    {
                        "content": "质疑性证据1",
                        "source": "批判者_review",
                        "credibility": 0.6,
                        "evidence_type": "challenging",
                        "metadata": {}
                    }
                ],
                "neutral_evidence": [],
                "overall_assessment": "存在质疑",
                "confidence_score": 0.6,
                "reviewer_id": "批判者",
                "review_timestamp": datetime.now().isoformat()
            },
            {
                "fact_id": "fact_2",
                "supporting_evidence": [
                    {
                        "content": "强支持性证据",
                        "source": "验证者_review",
                        "credibility": 0.9,
                        "evidence_type": "supporting",
                        "metadata": {}
                    }
                ],
                "challenging_evidence": [],
                "neutral_evidence": [],
                "overall_assessment": "事实高度可信",
                "confidence_score": 0.9,
                "reviewer_id": "验证者",
                "review_timestamp": datetime.now().isoformat()
            }
        ]
    
    @pytest.mark.asyncio
    async def test_evidence_aggregation_success(self, evidence_aggregation_node, mock_context, sample_evidence_reports):
        """Test successful evidence aggregation."""
        # Setup
        inputs = {"evidence_reports": sample_evidence_reports}
        
        # Execute
        result = await evidence_aggregation_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is True
        assert result["facts_processed"] == 2  # fact_1 and fact_2
        
        # Verify aggregated evidence structure
        aggregated = result["aggregated_evidence"]
        assert "fact_1" in aggregated
        assert "fact_2" in aggregated
        
        # Verify fact_1 aggregation (has both supporting and challenging evidence)
        fact1_agg = aggregated["fact_1"]
        assert fact1_agg["supporting_count"] == 1
        assert fact1_agg["challenging_count"] == 1
        assert fact1_agg["credibility_score"] < 0.8  # Should be reduced due to challenging evidence
        
        # Verify fact_2 aggregation (only supporting evidence)
        fact2_agg = aggregated["fact_2"]
        assert fact2_agg["supporting_count"] == 1
        assert fact2_agg["challenging_count"] == 0
        assert fact2_agg["credibility_score"] > 0.5  # Should be high due to strong support
        
        # Verify context state was updated
        assert "aggregated_evidence" in mock_context.state
    
    @pytest.mark.asyncio
    async def test_evidence_aggregation_from_state(self, evidence_aggregation_node, mock_context, sample_evidence_reports):
        """Test evidence aggregation using reports from workflow state."""
        # Setup
        mock_context.state["evidence_reports"] = sample_evidence_reports
        inputs = {}  # No reports in inputs, should use state
        
        # Execute
        result = await evidence_aggregation_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is True
        assert result["facts_processed"] == 2
    
    @pytest.mark.asyncio
    async def test_evidence_aggregation_no_reports(self, evidence_aggregation_node, mock_context):
        """Test evidence aggregation with no reports."""
        # Setup
        inputs = {}
        
        # Execute
        result = await evidence_aggregation_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "Evidence reports are required" in result["error"]
    
    def test_calculate_evidence_score(self, evidence_aggregation_node):
        """Test evidence score calculation."""
        # Test with credibility weighting
        evidence_list = [
            Evidence(content="test1", source="source1", credibility=0.8, evidence_type="supporting"),
            Evidence(content="test2", source="source2", credibility=0.6, evidence_type="supporting")
        ]
        
        score = evidence_aggregation_node._calculate_evidence_score(evidence_list)
        expected_score = (0.8 + 0.6) / 2
        assert abs(score - expected_score) < 0.01
        
        # Test with empty list
        empty_score = evidence_aggregation_node._calculate_evidence_score([])
        assert empty_score == 0.0
    
    def test_create_evidence_summary(self, evidence_aggregation_node):
        """Test evidence summary creation."""
        evidence = {
            "supporting": [Mock(), Mock()],  # 2 supporting evidence
            "challenging": [Mock()],         # 1 challenging evidence
            "neutral": [],                   # 0 neutral evidence
            "reviewers": ["验证者", "批判者"]
        }
        
        summary = evidence_aggregation_node._create_evidence_summary(evidence)
        
        assert "支持性证据 (2项)" in summary
        assert "质疑性证据 (1项)" in summary
        assert "2位审查者" in summary
        
        # Test with no evidence
        empty_evidence = {"supporting": [], "challenging": [], "neutral": [], "reviewers": []}
        empty_summary = evidence_aggregation_node._create_evidence_summary(empty_evidence)
        assert empty_summary == "无足够证据"


if __name__ == "__main__":
    pytest.main([__file__])
c
lass TestConsensusNode:
    """Test cases for ConsensusNode."""
    
    @pytest.fixture
    def consensus_node(self):
        """Create a ConsensusNode instance for testing."""
        return ConsensusNode("consensus_1", {
            "consensus_method": "weighted_average",
            "credibility_threshold": 0.6,
            "use_synthesis_engine": False
        })
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock execution context."""
        context = Mock(spec=ExecutionContext)
        context.execution_id = "exec_123"
        context.node_id = "node_consensus"
        context.state = {}
        context.services = {}
        context.mark_started = Mock()
        context.mark_completed = Mock()
        context.mark_failed = Mock()
        return context
    
    @pytest.fixture
    def sample_aggregated_evidence(self):
        """Create sample aggregated evidence for testing."""
        return {
            "fact_1": {
                "fact_id": "fact_1",
                "supporting_count": 2,
                "challenging_count": 1,
                "neutral_count": 0,
                "supporting_score": 0.8,
                "challenging_score": 0.6,
                "neutral_score": 0.0,
                "credibility_score": 0.7,
                "reviewers": ["验证者", "批判者"],
                "evidence_summary": "支持性证据 (2项)，质疑性证据 (1项)，由2位审查者提供"
            },
            "fact_2": {
                "fact_id": "fact_2",
                "supporting_count": 1,
                "challenging_count": 0,
                "neutral_count": 0,
                "supporting_score": 0.9,
                "challenging_score": 0.0,
                "neutral_score": 0.0,
                "credibility_score": 0.8,
                "reviewers": ["验证者"],
                "evidence_summary": "支持性证据 (1项)，由1位审查者提供"
            }
        }
    
    @pytest.mark.asyncio
    async def test_consensus_node_success(self, consensus_node, mock_context, sample_aggregated_evidence):
        """Test successful consensus calculation."""
        # Setup
        inputs = {"aggregated_evidence": sample_aggregated_evidence}
        
        # Execute
        result = await consensus_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is True
        assert len(result["consensus_results"]) == 2
        assert len(result["credibility_scores"]) == 2
        
        # Verify consensus results
        consensus_results = result["consensus_results"]
        assert "fact_1" in consensus_results
        assert "fact_2" in consensus_results
        
        # Verify fact_1 consensus (mixed evidence)
        fact1_result = consensus_results["fact_1"]
        assert fact1_result["consensus_method"] == "weighted_average"
        assert 0.0 <= fact1_result["final_credibility"] <= 1.0
        
        # Verify fact_2 consensus (strong support)
        fact2_result = consensus_results["fact_2"]
        assert fact2_result["final_credibility"] > 0.6  # Should be high due to strong support
        assert fact2_result["consensus_status"] == "accepted"
        
        # Verify context state was updated
        assert "consensus_results" in mock_context.state
        assert "final_credibility_scores" in mock_context.state
        assert "facts_needing_revision" in mock_context.state
    
    @pytest.mark.asyncio
    async def test_consensus_node_from_state(self, consensus_node, mock_context, sample_aggregated_evidence):
        """Test consensus calculation using evidence from workflow state."""
        # Setup
        mock_context.state["aggregated_evidence"] = sample_aggregated_evidence
        inputs = {}  # No evidence in inputs, should use state
        
        # Execute
        result = await consensus_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is True
        assert len(result["consensus_results"]) == 2
    
    @pytest.mark.asyncio
    async def test_consensus_node_no_evidence(self, consensus_node, mock_context):
        """Test consensus calculation with no evidence."""
        # Setup
        inputs = {}
        
        # Execute
        result = await consensus_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "Aggregated evidence is required" in result["error"]
    
    def test_calculate_weighted_consensus(self, consensus_node):
        """Test weighted consensus calculation."""
        evidence_data = {
            "supporting_score": 0.8,
            "challenging_score": 0.3,
            "neutral_score": 0.5
        }
        
        credibility = consensus_node._calculate_weighted_consensus(evidence_data)
        
        # Should be between 0 and 1
        assert 0.0 <= credibility <= 1.0
        # Should be relatively high due to strong support and weak challenge
        assert credibility > 0.5
    
    def test_calculate_majority_vote(self, consensus_node):
        """Test majority vote consensus calculation."""
        # Test supporting majority
        evidence_data = {
            "supporting_count": 3,
            "challenging_count": 1,
            "neutral_count": 0
        }
        
        credibility = consensus_node._calculate_majority_vote(evidence_data)
        assert credibility > 0.5
        
        # Test challenging majority
        evidence_data = {
            "supporting_count": 1,
            "challenging_count": 3,
            "neutral_count": 0
        }
        
        credibility = consensus_node._calculate_majority_vote(evidence_data)
        assert credibility < 0.5
        
        # Test tie
        evidence_data = {
            "supporting_count": 2,
            "challenging_count": 2,
            "neutral_count": 0
        }
        
        credibility = consensus_node._calculate_majority_vote(evidence_data)
        assert credibility == 0.5
    
    def test_create_consensus_summary(self, consensus_node):
        """Test consensus summary creation."""
        consensus_results = {
            "fact_1": {"consensus_status": "accepted"},
            "fact_2": {"consensus_status": "rejected"},
            "fact_3": {"consensus_status": "uncertain"}
        }
        
        summary = consensus_node._create_consensus_summary(consensus_results)
        
        assert "总计3个事实" in summary
        assert "接受1个" in summary
        assert "拒绝1个" in summary
        assert "不确定1个" in summary


class TestRevisionNode:
    """Test cases for RevisionNode."""
    
    @pytest.fixture
    def revision_node(self):
        """Create a RevisionNode instance for testing."""
        return RevisionNode("revision_1", {
            "revision_threshold": 0.6,
            "max_revision_attempts": 3,
            "provide_detailed_feedback": True
        })
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock execution context."""
        context = Mock(spec=ExecutionContext)
        context.execution_id = "exec_123"
        context.node_id = "node_revision"
        context.state = {"revision_attempt": 0}
        context.services = {}
        context.mark_started = Mock()
        context.mark_completed = Mock()
        context.mark_failed = Mock()
        return context
    
    @pytest.fixture
    def mock_llm_interface(self):
        """Create a mock LLM interface."""
        llm = AsyncMock()
        llm.generate.return_value = {
            "content": "这是修订后的内容，已经修正了不准确的事实声明。"
        }
        return llm
    
    @pytest.fixture
    def sample_consensus_results(self):
        """Create sample consensus results for testing."""
        return {
            "fact_1": {
                "fact_id": "fact_1",
                "final_credibility": 0.3,
                "consensus_status": "rejected",
                "evidence_summary": "质疑性证据较多",
                "reviewers": ["批判者", "验证者"]
            },
            "fact_2": {
                "fact_id": "fact_2",
                "final_credibility": 0.8,
                "consensus_status": "accepted",
                "evidence_summary": "支持性证据充分",
                "reviewers": ["验证者"]
            }
        }
    
    @pytest.fixture
    def sample_extracted_facts(self):
        """Create sample extracted facts for testing."""
        return [
            {
                "id": "fact_1",
                "content": "这是一个需要修订的事实声明",
                "confidence": 0.7,
                "source_location": "paragraph_1"
            },
            {
                "id": "fact_2",
                "content": "这是一个准确的事实声明",
                "confidence": 0.9,
                "source_location": "paragraph_2"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_revision_node_success(
        self, revision_node, mock_context, mock_llm_interface,
        sample_consensus_results, sample_extracted_facts
    ):
        """Test successful content revision."""
        # Setup
        mock_context.services["llm_interface"] = mock_llm_interface
        inputs = {
            "consensus_results": sample_consensus_results,
            "facts_needing_revision": ["fact_1"],
            "original_content": "原始内容包含一些需要修订的事实",
            "extracted_facts": sample_extracted_facts
        }
        
        # Execute
        result = await revision_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is True
        assert result["revision_needed"] is True
        assert result["revised_content"] == "这是修订后的内容，已经修正了不准确的事实声明。"
        assert "修订了1个低可信度事实" in result["revision_summary"]
        
        # Verify revision info
        revision_info = result["revision_info"]
        assert revision_info["revision_attempt"] == 1
        assert revision_info["facts_revised"] == ["fact_1"]
        assert "revision_timestamp" in revision_info
        
        # Verify context state was updated
        assert "revision_info" in mock_context.state
        assert "revised_content" in mock_context.state
        assert mock_context.state["revision_attempt"] == 1
        
        # Verify LLM was called
        mock_llm_interface.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_revision_node_no_revision_needed(
        self, revision_node, mock_context, sample_consensus_results
    ):
        """Test revision when no revision is needed."""
        # Setup
        inputs = {
            "consensus_results": sample_consensus_results,
            "facts_needing_revision": [],  # No facts need revision
            "original_content": "原始内容都是准确的"
        }
        
        # Execute
        result = await revision_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is True
        assert result["revision_needed"] is False
        assert result["revised_content"] == "原始内容都是准确的"
        assert "无需修订" in result["revision_summary"]
    
    @pytest.mark.asyncio
    async def test_revision_node_from_state(
        self, revision_node, mock_context, mock_llm_interface,
        sample_consensus_results, sample_extracted_facts
    ):
        """Test revision using data from workflow state."""
        # Setup
        mock_context.services["llm_interface"] = mock_llm_interface
        mock_context.state.update({
            "consensus_results": sample_consensus_results,
            "facts_needing_revision": ["fact_1"],
            "original_content": "原始内容包含一些需要修订的事实",
            "extracted_facts": sample_extracted_facts
        })
        inputs = {}  # No data in inputs, should use state
        
        # Execute
        result = await revision_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is True
        assert result["revision_needed"] is True
    
    @pytest.mark.asyncio
    async def test_revision_node_missing_consensus(self, revision_node, mock_context):
        """Test revision with missing consensus results."""
        # Setup
        inputs = {"original_content": "test content"}
        
        # Execute
        result = await revision_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "Consensus results are required" in result["error"]
    
    @pytest.mark.asyncio
    async def test_revision_node_missing_content(self, revision_node, mock_context):
        """Test revision with missing original content."""
        # Setup
        inputs = {"consensus_results": {}}
        
        # Execute
        result = await revision_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "Original content is required" in result["error"]
    
    @pytest.mark.asyncio
    async def test_revision_node_missing_llm(
        self, revision_node, mock_context, sample_consensus_results
    ):
        """Test revision with missing LLM interface."""
        # Setup
        inputs = {
            "consensus_results": sample_consensus_results,
            "facts_needing_revision": ["fact_1"],
            "original_content": "test content"
        }
        
        # Execute
        result = await revision_node.execute(inputs, mock_context)
        
        # Verify
        assert result["success"] is False
        assert "LLM interface not available" in result["error"]
    
    def test_create_revision_prompt(
        self, revision_node, sample_consensus_results, sample_extracted_facts
    ):
        """Test revision prompt creation."""
        original_content = "原始内容包含一些事实"
        facts_needing_revision = ["fact_1"]
        
        prompt = revision_node._create_revision_prompt(
            original_content,
            facts_needing_revision,
            sample_consensus_results,
            sample_extracted_facts
        )
        
        # Verify prompt contains key elements
        assert "原始内容" in prompt
        assert original_content in prompt
        assert "需要修订的问题" in prompt
        assert "这是一个需要修订的事实声明" in prompt
        assert "可信度分数：0.30" in prompt
        assert "修订要求" in prompt