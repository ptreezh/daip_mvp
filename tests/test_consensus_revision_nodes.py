# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-23 14:00:00
@Author  : DAIP-LIVE Team
@File    : test_consensus_revision_nodes.py
@Description:
    Unit tests for ConsensusNode and RevisionNode implementations.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from src.institutional_primitives.consensus_node import ConsensusNode
from src.institutional_primitives.revision_node import RevisionNode


class TestConsensusNode:
    """Test cases for ConsensusNode."""
    
    def test_initialization(self):
        """Test ConsensusNode initialization."""
        node = ConsensusNode("consensus_1", {
            "consensus_method": "majority_vote",
            "credibility_threshold": 0.7,
            "use_synthesis_engine": False
        })
        
        assert node.primitive_id == "consensus_1"
        assert node.consensus_method == "majority_vote"
        assert node.credibility_threshold == 0.7
        assert node.use_synthesis_engine is False
    
    def test_weighted_average_consensus(self):
        """Test weighted average consensus calculation."""
        node = ConsensusNode("consensus_1")
        
        evidence_data = {
            "supporting_score": 0.8,
            "challenging_score": 0.3,
            "neutral_score": 0.1
        }
        
        credibility, details = node._calculate_weighted_average_consensus(evidence_data)
        
        assert 0.0 <= credibility <= 1.0
        assert credibility > 0.5  # Should favor supporting evidence
        assert details["method"] == "weighted_average"
        assert details["supporting_score"] == 0.8
        assert details["challenging_score"] == 0.3
    
    def test_majority_vote_consensus(self):
        """Test majority vote consensus calculation."""
        node = ConsensusNode("consensus_1")
        
        # Test supporting majority
        evidence_data = {
            "supporting_count": 3,
            "challenging_count": 1,
            "neutral_count": 0
        }
        
        credibility, details = node._calculate_majority_vote_consensus(evidence_data)
        
        assert credibility > 0.5  # Should favor supporting evidence
        assert details["method"] == "majority_vote"
        assert details["supporting_votes"] == 3
        assert details["challenging_votes"] == 1
        assert details["outcome"] == "supporting"
    
    def test_majority_vote_challenging(self):
        """Test majority vote with challenging majority."""
        node = ConsensusNode("consensus_1")
        
        evidence_data = {
            "supporting_count": 1,
            "challenging_count": 3,
            "neutral_count": 0
        }
        
        credibility, details = node._calculate_majority_vote_consensus(evidence_data)
        
        assert credibility < 0.5  # Should favor challenging evidence
        assert details["outcome"] == "challenging"
    
    def test_no_evidence(self):
        """Test consensus calculation with no evidence."""
        node = ConsensusNode("consensus_1")
        
        evidence_data = {
            "supporting_count": 0,
            "challenging_count": 0,
            "neutral_count": 0
        }
        
        credibility, details = node._calculate_majority_vote_consensus(evidence_data)
        
        assert credibility == 0.5  # Should be neutral
        assert details["outcome"] == "no_evidence"
    
    def test_simplified_methods(self):
        """Test simplified methods for backward compatibility."""
        node = ConsensusNode("consensus_1")
        
        # Test _calculate_weighted_consensus
        evidence_data = {
            "supporting_score": 0.8,
            "challenging_score": 0.3,
            "neutral_score": 0.1
        }
        
        credibility = node._calculate_weighted_consensus(evidence_data)
        assert 0.0 <= credibility <= 1.0
        assert credibility > 0.5
        
        # Test _calculate_majority_vote
        evidence_data = {
            "supporting_count": 3,
            "challenging_count": 1
        }
        
        credibility = node._calculate_majority_vote(evidence_data)
        assert credibility == 0.75  # 3/(3+1)
    
    def test_input_output_schemas(self):
        """Test input and output schemas."""
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


class TestRevisionNode:
    """Test cases for RevisionNode."""
    
    def test_initialization(self):
        """Test RevisionNode initialization."""
        node = RevisionNode("revision_1", {
            "revision_role": "专家创作者",
            "max_revision_attempts": 5,
            "provide_evidence_details": False
        })
        
        assert node.primitive_id == "revision_1"
        assert node.revision_role == "专家创作者"
        assert node.max_revision_attempts == 5
        assert node.provide_evidence_details is False
    
    def test_prepare_revision_instructions(self):
        """Test revision instruction preparation."""
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
    
    def test_prepare_instructions_no_revision(self):
        """Test instruction preparation when no revision is needed."""
        node = RevisionNode("revision_1")
        
        instructions = node._prepare_revision_instructions([], {}, {}, [])
        
        assert "所有内容均已通过事实验证" in instructions
    
    def test_prepare_instructions_without_details(self):
        """Test instruction preparation without evidence details."""
        node = RevisionNode("revision_1", {"provide_evidence_details": False})
        
        facts_needing_revision = ["fact_1"]
        credibility_scores = {"fact_1": 0.3}
        consensus_details = {"fact_1": {"method": "weighted_average"}}
        extracted_facts = [{"id": "fact_1", "content": "测试事实"}]
        
        instructions = node._prepare_revision_instructions(
            facts_needing_revision,
            credibility_scores,
            consensus_details,
            extracted_facts
        )
        
        assert "测试事实" in instructions
        assert "0.30" in instructions
        # Should not contain detailed evidence information
        assert "加权平均" not in instructions
    
    def test_input_output_schemas(self):
        """Test input and output schemas."""
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


if __name__ == "__main__":
    pytest.main([__file__])