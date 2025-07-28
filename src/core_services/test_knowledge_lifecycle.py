# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-25 02:00:00
@Author  : DAIP-LIVE Team
@File    : test_knowledge_lifecycle.py
@Description:
    Comprehensive integration tests for knowledge retrieval and evolution lifecycle.
    Implements testing for task 10.2 requirements 6.3, 6.4, 6.5, 6.6, 6.7.
"""
import pytest
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

from .enhanced_sskg_manager import EnhancedSSKGManager, KnowledgeNode, NodeType
from .wiki_service import WikiService
from .knowledge_retrieval_service import (
    KnowledgeRetrievalService, 
    SearchScope, 
    QualityMetric
)
from .knowledge_evolution_manager import (
    KnowledgeEvolutionManager, 
    EvolutionStrategy,
    EvolutionTrigger
)
from .knowledge_management_service import KnowledgeManagementService, KnowledgeManagementConfig


class TestKnowledgeLifecycle:
    """Comprehensive tests for knowledge retrieval and evolution lifecycle."""
    
    @pytest.fixture
    async def knowledge_ecosystem(self):
        """Set up a complete knowledge management ecosystem for testing."""
        # Initialize core components
        sskg_manager = EnhancedSSKGManager()
        wiki_service = WikiService()
        
        # Configure knowledge management
        config = KnowledgeManagementConfig(
            auto_persist_facts=True,
            auto_persist_synthesis=True,
            min_confidence_threshold=0.5,
            evolution_strategy="hybrid",
            quality_threshold=0.6,
            cross_session_sharing=True
        )
        
        # Initialize knowledge management service
        knowledge_service = KnowledgeManagementService(
            sskg_manager=sskg_manager,
            wiki_service=wiki_service,
            config=config
        )
        
        return {
            "sskg_manager": sskg_manager,
            "wiki_service": wiki_service,
            "knowledge_service": knowledge_service,
            "retrieval_service": knowledge_service.retrieval_service,
            "evolution_manager": knowledge_service.evolution_manager
        }
    
    @pytest.mark.asyncio
    async def test_cross_session_knowledge_sharing(self, knowledge_ecosystem):
        """Test cross-session knowledge sharing (Requirement 6.3)."""
        services = knowledge_ecosystem
        retrieval_service = services["retrieval_service"]
        sskg_manager = services["sskg_manager"]
        
        # Create test knowledge from previous session
        test_node = KnowledgeNode(
            node_type=NodeType.FACT,
            content="Python is a high-level programming language",
            confidence=0.9,
            metadata={
                "source": "critical_review_workflow",
                "session_id": "session_001",
                "topic": "programming"
            }
        )
        
        node_id = sskg_manager.add_node(test_node)
        
        # Test cross-session knowledge retrieval
        session_context = {
            "topic": "programming languages",
            "keywords": ["python", "programming"],
            "user_id": "test_user",
            "session_id": "session_002"
        }
        
        cross_session_knowledge = await retrieval_service.get_cross_session_knowledge(
            session_context=session_context,
            time_window_days=30,
            min_relevance=0.5
        )
        
        # Verify results
        assert "facts" in cross_session_knowledge
        assert "synthesis" in cross_session_knowledge
        assert len(cross_session_knowledge["facts"]) > 0
        
        # Verify Python fact was retrieved
        python_facts = [
            fact for fact in cross_session_knowledge["facts"]
            if "Python" in fact["content"]
        ]
        assert len(python_facts) > 0
    
    @pytest.mark.asyncio
    async def test_semantic_search_capabilities(self, knowledge_ecosystem):
        """Test semantic search for validated information (Requirement 6.4)."""
        services = knowledge_ecosystem
        retrieval_service = services["retrieval_service"]
        sskg_manager = services["sskg_manager"]
        
        # Create test knowledge
        test_nodes = [
            {
                "type": NodeType.FACT,
                "content": "Artificial intelligence processes natural language",
                "confidence": 0.9,
                "metadata": {"expertise_domain": "ai"}
            },
            {
                "type": NodeType.CONCEPT,
                "content": "Natural language processing combines linguistics and computer science",
                "confidence": 0.8,
                "metadata": {"expertise_domain": "nlp"}
            }
        ]
        
        # Add nodes to SSKG
        for node_data in test_nodes:
            node = KnowledgeNode(
                node_type=node_data["type"],
                content=node_data["content"],
                confidence=node_data["confidence"],
                metadata=node_data["metadata"]
            )
            sskg_manager.add_node(node)
        
        # Test semantic search
        results = await retrieval_service.semantic_search(
            query="artificial intelligence natural language",
            scope=SearchScope.ALL,
            min_confidence=0.5,
            limit=10
        )
        
        assert len(results) >= 2
        
        # Verify result structure
        for result in results:
            assert hasattr(result, 'id')
            assert hasattr(result, 'content')
            assert hasattr(result, 'confidence')
            assert hasattr(result, 'relevance_score')
    
    @pytest.mark.asyncio
    async def test_knowledge_quality_assessment(self, knowledge_ecosystem):
        """Test knowledge quality assessment metrics (Requirement 6.5)."""
        services = knowledge_ecosystem
        retrieval_service = services["retrieval_service"]
        sskg_manager = services["sskg_manager"]
        
        # Create test node with rich metadata
        test_node = KnowledgeNode(
            node_type=NodeType.FACT,
            content="Quantum computing uses quantum mechanical phenomena",
            confidence=0.85,
            metadata={
                "source": "critical_review_workflow",
                "validation_timestamp": datetime.now().isoformat(),
                "evidence_sources": ["nature.com", "arxiv.org"],
                "reviewer_roles": ["physicist", "computer_scientist"]
            }
        )
        
        node_id = sskg_manager.add_node(test_node)
        
        # Assess quality
        quality_assessment = await retrieval_service.assess_knowledge_quality(node_id)
        
        # Verify assessment structure
        assert quality_assessment.node_id == node_id
        assert 0.0 <= quality_assessment.overall_quality <= 1.0
        assert len(quality_assessment.quality_metrics) > 0
        
        # Verify specific metrics
        expected_metrics = [
            QualityMetric.CONFIDENCE,
            QualityMetric.SOURCE_RELIABILITY,
            QualityMetric.VALIDATION_SCORE
        ]
        
        for metric in expected_metrics:
            if metric in quality_assessment.quality_metrics:
                assert 0.0 <= quality_assessment.quality_metrics[metric] <= 1.0
    
    @pytest.mark.asyncio
    async def test_knowledge_evolution_lifecycle(self, knowledge_ecosystem):
        """Test knowledge evolution and lifecycle management (Requirements 6.6, 6.7)."""
        services = knowledge_ecosystem
        evolution_manager = services["evolution_manager"]
        sskg_manager = services["sskg_manager"]
        
        # Create initial knowledge node
        original_node = KnowledgeNode(
            node_type=NodeType.FACT,
            content="Old information about technology",
            confidence=0.4,
            metadata={"source": "user_input"}
        )
        
        original_id = sskg_manager.add_node(original_node)
        
        # Test evolution
        evolved_id = await evolution_manager.evolve_knowledge_node(
            node_id=original_id,
            trigger=EvolutionTrigger.QUALITY_DECLINE,
            new_content="Updated information about modern technology",
            reason="Quality improvement"
        )
        
        assert evolved_id is not None
        assert evolved_id != original_id
        
        # Verify evolved node
        evolved_node = sskg_manager.get_node(evolved_id)
        assert evolved_node is not None
        assert evolved_node.content == "Updated information about modern technology"
        assert "evolution_trigger" in evolved_node.metadata
    
    @pytest.mark.asyncio
    async def test_comprehensive_integration(self, knowledge_ecosystem):
        """Test comprehensive knowledge management integration."""
        services = knowledge_ecosystem
        knowledge_service = services["knowledge_service"]
        
        # Test search functionality
        search_result = await knowledge_service.search_knowledge(
            query="test knowledge",
            scope=SearchScope.ALL,
            limit=5
        )
        
        assert "query" in search_result
        assert "results" in search_result
        assert "total_results" in search_result
        
        # Test statistics
        stats = knowledge_service.get_comprehensive_statistics()
        assert stats["service_status"] == "active"
        assert "configuration" in stats
        
        # Test health check
        health_status = await knowledge_service.health_check()
        assert "overall_status" in health_status
        assert "components" in health_status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])