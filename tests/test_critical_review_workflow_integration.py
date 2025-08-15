"""@Time    : 2025-07-24 10:00:00
@Author  : DAIP-LIVE Team
@File    : test_critical_review_workflow_integration.py
@Description:
    Integration tests for the complete Critical Review Workflow.
    Tests the end-to-end flow from content generation to revision.
"""
from unittest.mock import AsyncMock, Mock

import pytest

from src.institutional_primitives.base import ExecutionContext
from src.institutional_primitives.consensus_node import ConsensusNode
from src.institutional_primitives.critical_review_nodes import (
    EvidenceAggregationNode,
    FactExtractionNode,
    GenerationNode,
    ParallelReviewNode,
)
from src.institutional_primitives.revision_node import RevisionNode


class TestCriticalReviewWorkflowIntegration:
    """Integration tests for the complete Critical Review Workflow."""
    
    @pytest.fixture()
    def mock_context(self):
        """Create a mock execution context with shared state."""
        context = Mock(spec=ExecutionContext)
        context.execution_id = "exec_workflow_123"
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
        
        # Configure different responses based on the prompt content
        async def generate_side_effect(messages):
            prompt = messages[0]["content"]
            
            if "创作者" in prompt:
                # Generation node response
                return {
                    "content": "人工智能(AI)是计算机科学的一个分支，致力于创造能够模拟人类智能的机器。"
                    "机器学习是AI的核心技术，它使计算机能够从数据中学习而无需明确编程。"
                    "深度学习是机器学习的一个子领域，使用多层神经网络处理复杂数据。"
                    "2023年，全球AI市场规模达到5000亿美元。",
                    "model": "test-model",
                    "usage": {"tokens": 100}
                }
            elif "批判者" in prompt:
                # Challenger role response
                return {
                    "content": "我对'2023年，全球AI市场规模达到5000亿美元'这一说法提出质疑。"
                    "根据最新研究，2023年全球AI市场规模约为1500-2000亿美元，5000亿美元的数字被严重夸大。"
                    "此外，'机器学习是AI的核心技术'这一说法过于绝对，AI包含多种技术路线，机器学习只是其中之一。",
                }
            elif "验证者" in prompt:
                # Validator role response
                return {
                    "content": "我确认'人工智能是计算机科学的一个分支'和'深度学习是机器学习的一个子领域'这两个陈述是准确的。"
                    "关于'机器学习是AI的核心技术'，这在当前学术界和工业界确实被广泛认同，但表述可以更精确。"
                    "然而，'2023年全球AI市场规模达到5000亿美元'的数据无法验证，主流研究机构的估计值要低得多。",
                }
            elif "修订" in prompt:
                # Revision response
                return {
                    "content": "人工智能(AI)是计算机科学的一个分支，致力于创造能够模拟人类智能的机器。"
                    "机器学习是AI的重要技术之一，它使计算机能够从数据中学习而无需明确编程。"
                    "深度学习是机器学习的一个子领域，使用多层神经网络处理复杂数据。"
                    "2023年，全球AI市场规模估计约为1500-2000亿美元。",
                }
            else:
                # Default response
                return {"content": "默认回复内容"}
        
        llm.generate.side_effect = generate_side_effect
        return llm
    
    @pytest.fixture()
    def mock_fact_extraction_service(self):
        """Create a mock fact extraction service."""
        service = AsyncMock()
        service.extract_facts.return_value = [
            {
                "content": "人工智能是计算机科学的一个分支",
                "confidence": 0.9,
                "location": "sentence_1",
                "type": "definition",
                "method": "llm"
            },
            {
                "content": "机器学习是AI的核心技术",
                "confidence": 0.8,
                "location": "sentence_2",
                "type": "technical",
                "method": "llm"
            },
            {
                "content": "深度学习是机器学习的一个子领域",
                "confidence": 0.85,
                "location": "sentence_3",
                "type": "technical",
                "method": "llm"
            },
            {
                "content": "2023年，全球AI市场规模达到5000亿美元",
                "confidence": 0.7,
                "location": "sentence_4",
                "type": "statistical",
                "method": "llm"
            }
        ]
        return service
    
    @pytest.fixture()
    def mock_wiki_service(self):
        """Create a mock wiki service."""
        service = AsyncMock()
        service.search_pages.return_value = [
            {
                "title": "人工智能市场规模",
                "content": "根据多家研究机构的报告，2023年全球AI市场规模在1500-2000亿美元之间。",
                "last_updated": "2025-06-15"
            }
        ]
        return service
    
    @pytest.fixture()
    def mock_synthesis_engine(self):
        """Create a mock synthesis engine."""
        engine = AsyncMock()
        
        async def synthesize_side_effect(topic, history):
            if "Fact Credibility Analysis" in topic:
                fact_content = history[0]["opinion"]
                
                if "5000亿美元" in fact_content:
                    return "分析结果：这一事实声明的可信度较低。多个可靠来源表明2023年全球AI市场规模约为1500-2000亿美元，远低于5000亿美元。\n\n最终可信度评分：0.3"
                elif "机器学习是AI的核心技术" in fact_content:
                    return "分析结果：这一事实声明基本可信，但表述过于绝对。机器学习确实是当前AI的主要技术路线之一，但不是唯一核心技术。\n\n最终可信度评分：0.6"
                else:
                    return "分析结果：这一事实声明得到广泛认可和验证，可信度高。\n\n最终可信度评分：0.9"
            
            return "综合分析结果"
        
        engine.synthesize_opinions.side_effect = synthesize_side_effect
        return engine
    
    @pytest.mark.asyncio()
    async def test_critical_review_workflow_integration(
        self, 
        mock_context, 
        mock_llm_interface, 
        mock_fact_extraction_service,
        mock_wiki_service,
        mock_synthesis_engine
    ):
        """Test the complete Critical Review Workflow from generation to revision."""
        # Setup services
        mock_context.services["llm_interface"] = mock_llm_interface
        mock_context.services["fact_extraction_service"] = mock_fact_extraction_service
        mock_context.services["wiki_service"] = mock_wiki_service
        mock_context.services["synthesis_engine"] = mock_synthesis_engine
        
        # Create workflow nodes
        generation_node = GenerationNode("gen_1", {"role_name": "创作者"})
        fact_extraction_node = FactExtractionNode("fact_1", {"min_confidence": 0.6})
        parallel_review_node = ParallelReviewNode("review_1", {"reviewer_roles": ["批判者", "验证者"]})
        evidence_aggregation_node = EvidenceAggregationNode("agg_1")
        consensus_node = ConsensusNode("consensus_1", {"consensus_method": "synthesis", "credibility_threshold": 0.7})
        revision_node = RevisionNode("revision_1", {"revision_role": "创作者"})
        
        # Step 1: Generate content
        gen_result = await generation_node.execute(
            {"prompt": "请介绍人工智能的基本概念和市场规模"}, 
            mock_context
        )
        
        # Verify generation result
        assert gen_result["success"] is True
        assert "人工智能" in gen_result["content"]
        assert "5000亿美元" in gen_result["content"]
        
        # Step 2: Extract facts
        fact_result = await fact_extraction_node.execute({}, mock_context)
        
        # Verify fact extraction result
        assert fact_result["success"] is True
        assert fact_result["fact_count"] == 4
        
        # Step 3: Parallel review
        review_result = await parallel_review_node.execute({}, mock_context)
        
        # Verify review result
        assert review_result["success"] is True
        assert review_result["review_count"] > 0
        
        # Step 4: Evidence aggregation
        agg_result = await evidence_aggregation_node.execute({}, mock_context)
        
        # Verify aggregation result
        assert agg_result["success"] is True
        assert agg_result["facts_processed"] > 0
        
        # Step 5: Consensus calculation
        consensus_result = await consensus_node.execute({}, mock_context)
        
        # Verify consensus result
        assert consensus_result["success"] is True
        assert len(consensus_result["credibility_scores"]) > 0
        assert len(consensus_result["facts_needing_revision"]) > 0
        
        # The market size fact should need revision
        market_size_fact_id = None
        for fact in mock_context.state.get("extracted_facts", []):
            if "5000亿美元" in fact.get("content", ""):
                market_size_fact_id = fact.get("id")
                break
        
        assert market_size_fact_id is not None
        assert market_size_fact_id in consensus_result["facts_needing_revision"]
        
        # Step 6: Content revision
        revision_result = await revision_node.execute({}, mock_context)
        
        # Verify revision result
        assert revision_result["success"] is True
        assert revision_result["revision_needed"] is True
        assert "1500-2000亿美元" in revision_result["revised_content"]
        assert "5000亿美元" not in revision_result["revised_content"]
    
    @pytest.mark.asyncio()
    async def test_critical_review_workflow_no_revision_needed(
        self, 
        mock_context, 
        mock_llm_interface, 
        mock_fact_extraction_service,
        mock_wiki_service,
        mock_synthesis_engine
    ):
        """Test the workflow when no revision is needed."""
        # Setup services
        mock_context.services["llm_interface"] = mock_llm_interface
        mock_context.services["fact_extraction_service"] = mock_fact_extraction_service
        mock_context.services["wiki_service"] = mock_wiki_service
        mock_context.services["synthesis_engine"] = mock_synthesis_engine
        
        # Override fact extraction to return only high-credibility facts
        mock_fact_extraction_service.extract_facts.return_value = [
            {
                "content": "人工智能是计算机科学的一个分支",
                "confidence": 0.9,
                "location": "sentence_1",
                "type": "definition",
                "method": "llm"
            },
            {
                "content": "深度学习是机器学习的一个子领域",
                "confidence": 0.85,
                "location": "sentence_3",
                "type": "technical",
                "method": "llm"
            }
        ]
        
        # Create workflow nodes
        generation_node = GenerationNode("gen_1", {"role_name": "创作者"})
        fact_extraction_node = FactExtractionNode("fact_1", {"min_confidence": 0.6})
        parallel_review_node = ParallelReviewNode("review_1", {"reviewer_roles": ["批判者", "验证者"]})
        evidence_aggregation_node = EvidenceAggregationNode("agg_1")
        consensus_node = ConsensusNode("consensus_1", {"consensus_method": "synthesis", "credibility_threshold": 0.7})
        revision_node = RevisionNode("revision_1", {"revision_role": "创作者"})
        
        # Execute workflow steps
        await generation_node.execute({"prompt": "请介绍人工智能的基本概念"}, mock_context)
        await fact_extraction_node.execute({}, mock_context)
        await parallel_review_node.execute({}, mock_context)
        await evidence_aggregation_node.execute({}, mock_context)
        consensus_result = await consensus_node.execute({}, mock_context)
        
        # Verify no facts need revision
        assert len(consensus_result["facts_needing_revision"]) == 0
        
        # Execute revision node
        revision_result = await revision_node.execute({}, mock_context)
        
        # Verify revision was not needed
        assert revision_result["success"] is True
        assert revision_result["revision_needed"] is False
        assert "No revision needed" in revision_result["revision_summary"]
    
    @pytest.mark.asyncio()
    async def test_critical_review_workflow_error_handling(
        self, 
        mock_context, 
        mock_llm_interface, 
        mock_fact_extraction_service
    ):
        """Test error handling in the workflow."""
        # Setup services with only LLM interface
        mock_context.services["llm_interface"] = mock_llm_interface
        
        # Create workflow nodes
        generation_node = GenerationNode("gen_1", {"role_name": "创作者"})
        fact_extraction_node = FactExtractionNode("fact_1", {"min_confidence": 0.6})
        
        # Step 1: Generate content
        gen_result = await generation_node.execute(
            {"prompt": "请介绍人工智能的基本概念和市场规模"}, 
            mock_context
        )
        
        # Verify generation result
        assert gen_result["success"] is True
        
        # Step 2: Try fact extraction without the service
        fact_result = await fact_extraction_node.execute({}, mock_context)
        
        # Verify fact extraction fails gracefully
        assert fact_result["success"] is False
        assert "Fact extraction service not available" in fact_result["error"]
        
        # Now add the service and try again
        mock_context.services["fact_extraction_service"] = mock_fact_extraction_service
        fact_result = await fact_extraction_node.execute({}, mock_context)
        
        # Verify fact extraction succeeds
        assert fact_result["success"] is True
        assert fact_result["fact_count"] > 0


if __name__ == "__main__":
    pytest.main([__file__])