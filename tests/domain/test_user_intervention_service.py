"""
User Intervention Service Tests
========================

This module contains comprehensive tests for the UserInterventionService.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.domain.value_objects import EntranceType, IntentType, TaskStatus, ConsensusLevel, MessageIntent
from src.domain.entities import User, UserPreference
from src.domain.domain_services import UserInterventionService


class TestUserInterventionService:
    """Tests for the UserInterventionService"""
    
    @pytest.fixture
    def intervention_service(self):
        """Create a UserInterventionService instance for testing"""
        return UserInterventionService()
    
    @pytest.mark.asyncio
    async def test_optimize_input_comment(self, intervention_service):
        """Test optimizing a comment input"""
        raw_input = "This is a good point"
        intent_type = "comment"
        context = {}
        
        optimized = await intervention_service.optimize_input(raw_input, intent_type, context)
        assert isinstance(optimized, str)
        assert len(optimized) > 0
        # Should add a constructive phrase
        assert optimized.startswith("我认为")
    
    @pytest.mark.asyncio
    async def test_optimize_input_question(self, intervention_service):
        """Test optimizing a question input"""
        raw_input = "climate change effects"
        intent_type = "question"
        context = {}
        
        optimized = await intervention_service.optimize_input(raw_input, intent_type, context)
        assert isinstance(optimized, str)
        assert len(optimized) > 0
        # Should add a question word
        assert any(word in optimized.lower() for word in ["什么", "如何", "为什么", "怎么样", "是否", "能否"])
    
    @pytest.mark.asyncio
    async def test_optimize_input_suggestion(self, intervention_service):
        """Test optimizing a suggestion input"""
        raw_input = "improve the user interface"
        intent_type = "suggestion"
        context = {}
        
        optimized = await intervention_service.optimize_input(raw_input, intent_type, context)
        assert isinstance(optimized, str)
        assert len(optimized) > 0
        # Should add a suggestion phrase
        assert optimized.startswith("建议")
    
    @pytest.mark.asyncio
    async def test_optimize_input_correction(self, intervention_service):
        """Test optimizing a correction input"""
        raw_input = "there is an error in the calculation"
        intent_type = "correction"
        context = {}
        
        optimized = await intervention_service.optimize_input(raw_input, intent_type, context)
        assert isinstance(optimized, str)
        assert len(optimized) > 0
        # Should add a polite phrase
        assert optimized.startswith("抱歉")
    
    @pytest.mark.asyncio
    async def test_optimize_input_unknown_intent(self, intervention_service):
        """Test optimizing input with unknown intent"""
        raw_input = "This is a test"
        intent_type = "unknown"
        context = {}
        
        optimized = await intervention_service.optimize_input(raw_input, intent_type, context)
        # Should return the original input for unknown intents
        assert optimized == raw_input
    
    @pytest.mark.asyncio
    async def test_optimize_comment_already_constructive(self, intervention_service):
        """Test optimizing a comment that is already constructive"""
        raw_input = "我认为这个观点很有道理"
        context = {}
        
        optimized = await intervention_service._optimize_comment(raw_input, context)
        # Should return the original input if already constructive
        assert optimized == raw_input
    
    @pytest.mark.asyncio
    async def test_optimize_question_with_question_words(self, intervention_service):
        """Test optimizing a question that already has question words"""
        raw_input = "为什么这个方案不可行？"
        context = {}
        
        optimized = await intervention_service._optimize_question(raw_input, context)
        # Should return the original input if already has question words
        assert optimized == raw_input
    
    @pytest.mark.asyncio
    async def test_optimize_suggestion_already_actionable(self, intervention_service):
        """Test optimizing a suggestion that is already actionable"""
        raw_input = "建议增加更多的测试用例"
        context = {}
        
        optimized = await intervention_service._optimize_suggestion(raw_input, context)
        # Should return the original input if already actionable
        assert optimized == raw_input
    
    @pytest.mark.asyncio
    async def test_optimize_correction_already_polite(self, intervention_service):
        """Test optimizing a correction that is already polite"""
        raw_input = "抱歉，我想指出这个计算有误"
        context = {}
        
        optimized = await intervention_service._optimize_correction(raw_input, context)
        # Should return the original input if already polite
        assert optimized == raw_input
    
    @pytest.mark.asyncio
    async def test_integrate_intervention(self, intervention_service):
        """Test integrating user intervention"""
        debate_id = "test_debate"
        user_intervention = {
            "content": "I have a suggestion for improving the workflow",
            "intent": "suggestion"
        }
        
        # Mock the internal methods
        with patch.object(intervention_service, '_analyze_intervention_impact', AsyncMock(return_value={
            "content_length": 100,
            "complexity": 0.5,
            "constructiveness": 0.8,
            "intent": "suggestion",
            "relevance": 0.8
        })), patch.object(intervention_service, '_generate_integration_suggestions', AsyncMock(return_value=[
            "该干预具有高度建设性，建议优先考虑"
        ])):
            
            result = await intervention_service.integrate_intervention(debate_id, user_intervention)
            
            assert isinstance(result, dict)
            assert result["status"] == "integrated"
            assert "impact_analysis" in result
            assert "integration_suggestions" in result
            assert "impact_score" in result
            assert "timestamp" in result
            assert isinstance(result["impact_score"], float)
            assert 0 <= result["impact_score"] <= 1
    
    @pytest.mark.asyncio
    async def test_analyze_intervention_impact(self, intervention_service):
        """Test analyzing intervention impact"""
        intervention = {
            "content": "This is a constructive suggestion for improving the system",
            "intent": "suggestion"
        }
        
        impact_analysis = await intervention_service._analyze_intervention_impact(intervention)
        
        assert isinstance(impact_analysis, dict)
        assert "content_length" in impact_analysis
        assert "complexity" in impact_analysis
        assert "constructiveness" in impact_analysis
        assert "intent" in impact_analysis
        assert "relevance" in impact_analysis
        assert isinstance(impact_analysis["content_length"], int)
        assert isinstance(impact_analysis["complexity"], float)
        assert isinstance(impact_analysis["constructiveness"], float)
        assert isinstance(impact_analysis["relevance"], float)
        assert 0 <= impact_analysis["complexity"] <= 1
        assert 0 <= impact_analysis["constructiveness"] <= 1
        assert 0 <= impact_analysis["relevance"] <= 1
    
    def test_analyze_content_complexity_simple(self, intervention_service):
        """Test analyzing content complexity with simple content"""
        simple_content = "Hello world"
        complexity = intervention_service._analyze_content_complexity(simple_content)
        assert isinstance(complexity, float)
        assert 0 <= complexity <= 1
        # The current implementation returns 0.622 for this case
        assert complexity == pytest.approx(0.622, 0.01)
    
    def test_analyze_content_complexity_complex(self, intervention_service):
        """Test analyzing content complexity with complex content"""
        complex_content = "The multifaceted implications of anthropogenic climate change necessitate a comprehensive analysis of interrelated environmental, economic, and social factors."
        complexity = intervention_service._analyze_content_complexity(complex_content)
        assert isinstance(complexity, float)
        assert 0 <= complexity <= 1
        # Should be high for complex content
        assert complexity >= 0.7
    
    def test_analyze_constructiveness_low(self, intervention_service):
        """Test analyzing constructiveness with low constructive content"""
        content = "This is bad"
        constructiveness = intervention_service._analyze_constructiveness(content)
        assert isinstance(constructiveness, float)
        assert 0 <= constructiveness <= 1
        # Should be low for non-constructive content
        assert constructiveness <= 0.5
    
    def test_analyze_constructiveness_high(self, intervention_service):
        """Test analyzing constructiveness with high constructive content"""
        content = "I suggest we improve this by adding more tests"
        constructiveness = intervention_service._analyze_constructiveness(content)
        assert isinstance(constructiveness, float)
        assert 0 <= constructiveness <= 1
        # Should be high for constructive content
        assert constructiveness >= 0.7
    
    @pytest.mark.asyncio
    async def test_generate_integration_suggestions_constructive(self, intervention_service):
        """Test generating integration suggestions for constructive intervention"""
        intervention = {"content": "This is a great suggestion"}
        impact_analysis = {
            "constructiveness": 0.9,
            "complexity": 0.3,
            "content_length": 100
        }
        
        suggestions = await intervention_service._generate_integration_suggestions(intervention, impact_analysis)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert "该干预具有高度建设性，建议优先考虑" in suggestions
    
    @pytest.mark.asyncio
    async def test_generate_integration_suggestions_complex(self, intervention_service):
        """Test generating integration suggestions for complex intervention"""
        intervention = {"content": "A very complex and detailed suggestion"}
        impact_analysis = {
            "constructiveness": 0.5,
            "complexity": 0.9,
            "content_length": 300
        }
        
        suggestions = await intervention_service._generate_integration_suggestions(intervention, impact_analysis)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert "内容较为复杂，建议分解讨论" in suggestions
        assert "内容较长，建议提取关键点" in suggestions
    
    def test_calculate_impact_score(self, intervention_service):
        """Test calculating impact score"""
        impact_analysis = {
            "constructiveness": 0.8,
            "complexity": 0.6,
            "relevance": 0.7
        }
        
        impact_score = intervention_service._calculate_impact_score(impact_analysis)
        
        assert isinstance(impact_score, float)
        assert 0 <= impact_score <= 1
        # Based on the weights in the implementation, this should be around 0.71
        assert impact_score == pytest.approx(0.71, 0.01)
    
    def test_record_optimization(self, intervention_service):
        """Test recording optimization history"""
        original = "original text"
        optimized = "optimized text"
        intent_type = "comment"
        context = {}
        
        intervention_service._record_optimization(original, optimized, intent_type, context)
        
        # Check if optimization was recorded
        assert len(intervention_service.optimization_history) > 0
        # Get the latest timestamp key
        latest_timestamp = list(intervention_service.optimization_history.keys())[-1]
        records = intervention_service.optimization_history[latest_timestamp]
        assert len(records) == 1
        record = records[0]
        assert record["original"] == original
        assert record["optimized"] == optimized
        assert record["intent_type"] == intent_type
        assert record["context"] == context
    
    def test_get_optimization_stats_no_history(self, intervention_service):
        """Test getting optimization stats with no history"""
        stats = intervention_service.get_optimization_stats()
        
        assert isinstance(stats, dict)
        assert "total_optimizations" in stats
        assert stats["total_optimizations"] == 0
    
    def test_get_optimization_stats_with_history(self, intervention_service):
        """Test getting optimization stats with history"""
        # Add some optimization records
        intervention_service.optimization_history = {
            datetime.now(): [
                {"original": "short", "optimized": "longer text", "intent_type": "comment", "context": {}},
                {"original": "simple", "optimized": "more complex text", "intent_type": "question", "context": {}}
            ]
        }
        
        stats = intervention_service.get_optimization_stats()
        
        assert isinstance(stats, dict)
        assert "total_optimizations" in stats
        assert "average_improvement" in stats
        assert "intent_distribution" in stats
        assert stats["total_optimizations"] == 2
        assert isinstance(stats["average_improvement"], float)
        assert isinstance(stats["intent_distribution"], dict)
        assert "comment" in stats["intent_distribution"]
        assert "question" in stats["intent_distribution"]