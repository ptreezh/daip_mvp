"""
Unit tests for the result synthesizer.
"""
import pytest
from src.daip_live.subagents.base import AnalysisResult
from src.daip_live.skills.base import SkillOutput
from src.daip_live.execution.synthesizer import ResultSynthesizer


class TestResultSynthesizer:
    """Test cases for the ResultSynthesizer class."""
    
    @pytest.fixture
    def result_synthesizer(self):
        """Create a ResultSynthesizer instance for testing."""
        return ResultSynthesizer()
    
    def test_synthesize_subagent_results_single(self, result_synthesizer):
        """Test synthesizing a single Subagent result."""
        result = AnalysisResult(
            content="Single analysis result",
            metadata={"key": "value"},
            confidence=0.8,
            subagent_name="test_subagent"
        )
        
        synthesized = result_synthesizer.synthesize_subagent_results([result])
        assert synthesized == result
    
    def test_synthesize_subagent_results_multiple(self, result_synthesizer):
        """Test synthesizing multiple Subagent results."""
        results = [
            AnalysisResult(
                content="First analysis result",
                metadata={"source": "subagent1"},
                confidence=0.8,
                subagent_name="subagent1"
            ),
            AnalysisResult(
                content="Second analysis result",
                metadata={"source": "subagent2"},
                confidence=0.9,
                subagent_name="subagent2"
            )
        ]
        
        synthesized = result_synthesizer.synthesize_subagent_results(results)
        
        assert synthesized.content == "First analysis result\n\n---\n\nSecond analysis result"
        assert synthesized.metadata["synthesized"] == True
        assert synthesized.metadata["result_count"] == 2
        assert abs(synthesized.confidence - 0.85) < 0.001  # Average of 0.8 and 0.9
    
    def test_synthesize_subagent_results_empty(self, result_synthesizer):
        """Test synthesizing empty Subagent results."""
        synthesized = result_synthesizer.synthesize_subagent_results([])
        
        assert "No results to synthesize" in synthesized.content
        assert synthesized.metadata["synthesized"] == True
        assert synthesized.metadata["result_count"] == 0
    
    def test_synthesize_skill_outputs_single(self, result_synthesizer):
        """Test synthesizing a single skill output."""
        output = SkillOutput(
            result="Single skill output",
            metadata={"key": "value"},
            confidence=0.75,
            execution_time=0.1
        )
        
        synthesized = result_synthesizer.synthesize_skill_outputs([output])
        assert synthesized == output
    
    def test_synthesize_skill_outputs_multiple(self, result_synthesizer):
        """Test synthesizing multiple skill outputs."""
        outputs = [
            SkillOutput(
                result="First skill output",
                metadata={"source": "skill1"},
                confidence=0.8,
                execution_time=0.1
            ),
            SkillOutput(
                result="Second skill output",
                metadata={"source": "skill2"},
                confidence=0.85,
                execution_time=0.15
            )
        ]
        
        synthesized = result_synthesizer.synthesize_skill_outputs(outputs)
        
        assert synthesized.result == "First skill output\n\n---\n\nSecond skill output"
        assert synthesized.metadata["synthesized"] == True
        assert synthesized.metadata["output_count"] == 2
        assert abs(synthesized.confidence - 0.825) < 0.001  # Average of 0.8 and 0.85
        assert abs(synthesized.execution_time - 0.25) < 0.001  # Sum of 0.1 and 0.15
    
    def test_synthesize_skill_outputs_empty(self, result_synthesizer):
        """Test synthesizing empty skill outputs."""
        synthesized = result_synthesizer.synthesize_skill_outputs([])
        
        assert "No outputs to synthesize" in synthesized.result
        assert synthesized.metadata["synthesized"] == True
        assert synthesized.metadata["output_count"] == 0
    
    def test_resolve_conflicts_single(self, result_synthesizer):
        """Test resolving conflicts with a single result."""
        result = AnalysisResult(
            content="Single analysis result",
            metadata={"key": "value"},
            confidence=0.8,
            subagent_name="test_subagent"
        )
        
        resolved = result_synthesizer.resolve_conflicts([result])
        
        # Should return a result with the same content but additional conflict resolution metadata
        assert resolved.content == result.content
        assert resolved.confidence == result.confidence
        assert resolved.subagent_name == result.subagent_name
        assert "conflict_resolution" in resolved.metadata
    
    def test_resolve_conflicts_multiple(self, result_synthesizer):
        """Test resolving conflicts with multiple results."""
        results = [
            AnalysisResult(
                content="Low confidence result",
                metadata={"source": "subagent1"},
                confidence=0.6,
                subagent_name="subagent1"
            ),
            AnalysisResult(
                content="High confidence result",
                metadata={"source": "subagent2"},
                confidence=0.9,
                subagent_name="subagent2"
            ),
            AnalysisResult(
                content="Medium confidence result",
                metadata={"source": "subagent3"},
                confidence=0.7,
                subagent_name="subagent3"
            )
        ]
        
        resolved = result_synthesizer.resolve_conflicts(results)
        
        # Should return the result with highest confidence
        assert resolved.content == "High confidence result"
        assert resolved.confidence == 0.9
        assert resolved.subagent_name == "subagent2"
        assert resolved.metadata["conflict_resolution"]["method"] == "highest_confidence"
        assert resolved.metadata["conflict_resolution"]["selected_from"] == 3