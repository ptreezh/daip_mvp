# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-23 14:00:00
@Author  : DAIP-LIVE Team
@File    : test_critical_review_nodes_simple.py
@Description:
    Simplified unit tests for Critical Review Workflow nodes.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock

# Test the data models first
def test_extracted_fact_model():
    """Test ExtractedFact model creation."""
    from src.institutional_primitives.critical_review_nodes import ExtractedFact
    
    fact = ExtractedFact(
        id="fact_1",
        content="Test fact content",
        confidence=0.8,
        source_location="paragraph_1",
        fact_type="general"
    )
    
    assert fact.id == "fact_1"
    assert fact.content == "Test fact content"
    assert fact.confidence == 0.8
    assert fact.source_location == "paragraph_1"
    assert fact.fact_type == "general"


def test_evidence_model():
    """Test Evidence model creation."""
    from src.institutional_primitives.critical_review_nodes import Evidence
    
    evidence = Evidence(
        content="Supporting evidence",
        source="test_source",
        credibility=0.9,
        evidence_type="supporting"
    )
    
    assert evidence.content == "Supporting evidence"
    assert evidence.source == "test_source"
    assert evidence.credibility == 0.9
    assert evidence.evidence_type == "supporting"


def test_evidence_report_model():
    """Test EvidenceReport model creation."""
    from src.institutional_primitives.critical_review_nodes import EvidenceReport, Evidence
    
    supporting_evidence = Evidence(
        content="Support",
        source="source1",
        credibility=0.8,
        evidence_type="supporting"
    )
    
    report = EvidenceReport(
        fact_id="fact_1",
        supporting_evidence=[supporting_evidence],
        overall_assessment="Fact is supported",
        confidence_score=0.8,
        reviewer_id="reviewer_1"
    )
    
    assert report.fact_id == "fact_1"
    assert len(report.supporting_evidence) == 1
    assert report.overall_assessment == "Fact is supported"
    assert report.confidence_score == 0.8
    assert report.reviewer_id == "reviewer_1"


def test_generation_node_initialization():
    """Test GenerationNode initialization."""
    from src.institutional_primitives.critical_review_nodes import GenerationNode
    
    node = GenerationNode("gen_1", {"role_name": "测试创作者"})
    
    assert node.primitive_id == "gen_1"
    assert node.role_name == "测试创作者"
    assert node.capture_metadata is True


def test_generation_node_schemas():
    """Test GenerationNode input/output schemas."""
    from src.institutional_primitives.critical_review_nodes import GenerationNode
    
    node = GenerationNode("gen_1")
    
    input_schema = node.get_input_schema()
    output_schema = node.get_output_schema()
    
    # Verify input schema
    assert input_schema["type"] == "object"
    assert "prompt" in input_schema["properties"]
    assert "prompt" in input_schema["required"]
    
    # Verify output schema
    assert output_schema["type"] == "object"
    assert "content" in output_schema["properties"]
    assert "success" in output_schema["properties"]


def test_fact_extraction_node_initialization():
    """Test FactExtractionNode initialization."""
    from src.institutional_primitives.critical_review_nodes import FactExtractionNode
    
    node = FactExtractionNode("fact_1", {"min_confidence": 0.7, "max_facts": 15})
    
    assert node.primitive_id == "fact_1"
    assert node.min_confidence == 0.7
    assert node.max_facts == 15


def test_parallel_review_node_initialization():
    """Test ParallelReviewNode initialization."""
    from src.institutional_primitives.critical_review_nodes import ParallelReviewNode
    
    node = ParallelReviewNode("review_1", {
        "reviewer_roles": ["批判者", "验证者", "专家"],
        "max_parallel_reviews": 10
    })
    
    assert node.primitive_id == "review_1"
    assert node.reviewer_roles == ["批判者", "验证者", "专家"]
    assert node.max_parallel_reviews == 10


def test_evidence_aggregation_node_initialization():
    """Test EvidenceAggregationNode initialization."""
    from src.institutional_primitives.critical_review_nodes import EvidenceAggregationNode
    
    node = EvidenceAggregationNode("agg_1", {
        "min_evidence_threshold": 3,
        "weight_by_credibility": False
    })
    
    assert node.primitive_id == "agg_1"
    assert node.min_evidence_threshold == 3
    assert node.weight_by_credibility is False


def test_evidence_aggregation_calculate_score():
    """Test evidence score calculation."""
    from src.institutional_primitives.critical_review_nodes import EvidenceAggregationNode, Evidence
    
    node = EvidenceAggregationNode("agg_1", {"weight_by_credibility": True})
    
    evidence_list = [
        Evidence(content="test1", source="source1", credibility=0.8, evidence_type="supporting"),
        Evidence(content="test2", source="source2", credibility=0.6, evidence_type="supporting")
    ]
    
    score = node._calculate_evidence_score(evidence_list)
    expected_score = (0.8 + 0.6) / 2
    assert abs(score - expected_score) < 0.01
    
    # Test with empty list
    empty_score = node._calculate_evidence_score([])
    assert empty_score == 0.0


def test_evidence_aggregation_create_summary():
    """Test evidence summary creation."""
    from src.institutional_primitives.critical_review_nodes import EvidenceAggregationNode
    
    node = EvidenceAggregationNode("agg_1")
    
    evidence = {
        "supporting": [Mock(), Mock()],  # 2 supporting evidence
        "challenging": [Mock()],         # 1 challenging evidence
        "neutral": [],                   # 0 neutral evidence
        "reviewers": ["验证者", "批判者"]
    }
    
    summary = node._create_evidence_summary(evidence)
    
    assert "支持性证据 (2项)" in summary
    assert "质疑性证据 (1项)" in summary
    assert "2位审查者" in summary
    
    # Test with no evidence
    empty_evidence = {"supporting": [], "challenging": [], "neutral": [], "reviewers": []}
    empty_summary = node._create_evidence_summary(empty_evidence)
    assert empty_summary == "无足够证据"


if __name__ == "__main__":
    pytest.main([__file__])


def test_consensus_node_initialization():
    """Test ConsensusNode initialization."""
    from src.institutional_primitives.consensus_node import ConsensusNode
    
    node = ConsensusNode("consensus_1", {
        "consensus_method": "majority_vote",
        "credibility_threshold": 0.7,
        "use_synthesis_engine": False
    })
    
    assert node.primitive_id == "consensus_1"
    assert node.consensus_method == "majority_vote"
    assert node.credibility_threshold == 0.7
    assert node.use_synthesis_engine is False


def test_consensus_node_weighted_average():
    """Test weighted average consensus calculation."""
    from src.institutional_primitives.consensus_node import ConsensusNode
    
    node = ConsensusNode("consensus_1")
    
    evidence_data = {
        "supporting_score": 0.8,
        "challenging_score": 0.3,
        "neutral_score": 0.1
    }
    
    credibility = node._calculate_weighted_consensus(evidence_data)
    
    assert 0.0 <= credibility <= 1.0
    # Verify credibility is within expected range
    assert 0.0 <= credibility <= 1.0
    # Should be relatively high due to strong support and weak challenge
    assert credibility > 0.5


def test_consensus_node_majority_vote():
    """Test majority vote consensus calculation."""
    from src.institutional_primitives.consensus_node import ConsensusNode
    
    node = ConsensusNode("consensus_1")
    
    # Test supporting majority
    evidence_data = {
        "supporting_count": 3,
        "challenging_count": 1,
        "neutral_count": 0
    }
    
    credibility = node._calculate_majority_vote(evidence_data)
    
    assert credibility > 0.5  # Should favor supporting evidence
    # Verify credibility is within expected range
    assert 0.0 <= credibility <= 1.0
    
    # Test challenging majority
    evidence_data_challenging = {
        "supporting_count": 1,
        "challenging_count": 3,
        "neutral_count": 0
    }
    
    credibility_challenging, details = node._calculate_majority_vote_consensus(evidence_data_challenging)
    assert credibility_challenging < 0.5  # Should favor challenging evidence


def test_revision_node_initialization():
    """Test RevisionNode initialization."""
    from src.institutional_primitives.revision_node import RevisionNode
    
    node = RevisionNode("revision_1", {
        "revision_role": "专家创作者",
        "max_revision_attempts": 5,
        "provide_evidence_details": False
    })
    
    assert node.primitive_id == "revision_1"
    assert node.revision_role == "专家创作者"
    assert node.max_revision_attempts == 5
    assert node.provide_evidence_details is False


def test_revision_node_prepare_instructions():
    """Test revision instruction preparation."""
    from src.institutional_primitives.revision_node import RevisionNode
    
    node = RevisionNode("revision_1", {"provide_evidence_details": True})
    
    facts_needing_revision = ["fact_1", "fact_2"]
    credibility_scores = {"fact_1": 0.3, "fact_2": 0.4}
    consensus_details = {
        "fact_1": {
            "method": "weighted_average",
            "supporting_score": 0.2,
            "challenging_score": 0.8
        },
        "fact_2": {
            "method": "majority_vote",
            "supporting_votes": 1,
            "challenging_votes": 3
        }
    }
    extracted_facts = [
        {"id": "fact_1", "content": "低可信度事实1"},
        {"id": "fact_2", "content": "低可信度事实2"}
    ]
    
    instructions = node._prepare_revision_instructions(
        facts_needing_revision,
        credibility_scores,
        consensus_details,
        extracted_facts
    )
    
    assert "低可信度事实1" in instructions
    assert "低可信度事实2" in instructions
    assert "0.30" in instructions  # credibility score
    assert "0.40" in instructions  # credibility score
    assert "加权平均" in instructions
    assert "多数投票" in instructions


def test_consensus_node_schemas():
    """Test ConsensusNode input/output schemas."""
    from src.institutional_primitives.consensus_node import ConsensusNode
    
    node = ConsensusNode("consensus_1")
    
    input_schema = node.get_input_schema()
    output_schema = node.get_output_schema()
    
    # Verify input schema
    assert input_schema["type"] == "object"
    assert "aggregated_evidence" in input_schema["properties"]
    assert "aggregated_evidence" in input_schema["required"]
    
    # Verify output schema
    assert output_schema["type"] == "object"
    assert "credibility_scores" in output_schema["properties"]
    assert "facts_needing_revision" in output_schema["properties"]
    assert "success" in output_schema["properties"]


def test_revision_node_schemas():
    """Test RevisionNode input/output schemas."""
    from src.institutional_primitives.revision_node import RevisionNode
    
    node = RevisionNode("revision_1")
    
    input_schema = node.get_input_schema()
    output_schema = node.get_output_schema()
    
    # Verify input schema
    assert input_schema["type"] == "object"
    assert "facts_needing_revision" in input_schema["properties"]
    assert "facts_needing_revision" in input_schema["required"]
    
    # Verify output schema
    assert output_schema["type"] == "object"
    assert "revised_content" in output_schema["properties"]
    assert "revision_needed" in output_schema["properties"]
    assert "success" in output_schema["properties"]