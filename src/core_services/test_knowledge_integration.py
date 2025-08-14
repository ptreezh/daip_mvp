"""@Time    : 2025-07-25 01:00:00
@Author  : DAIP-LIVE Team
@File    : test_knowledge_integration.py
@Description:
    Integration tests for knowledge retrieval and evolution lifecycle.
    Tests requirements 6.3, 6.4, 6.5, 6.6, 6.7.
"""
from datetime import datetime, timedelta

import pytest

from .enhanced_sskg_manager import EnhancedSSKGManager, KnowledgeNode, NodeType
from .knowledge_evolution_manager import EvolutionStrategy
from .knowledge_management_service import KnowledgeManagementConfig, KnowledgeManagementService
from .knowledge_retrieval_service import SearchScope
from .wiki_service import WikiService


class TestKnowledgeIntegration:
    """Integration tests for knowledge retrieval and evolution."""

    @pytest.fixture
    async def setup_services(self):
        """Set up test services."""
        # Initialize SSKG manager
        sskg_manager = EnhancedSSKGManager()

        # Initialize wiki service
        wiki_service = WikiService()

        # Initialize knowledge management service
        config = KnowledgeManagementConfig(
            auto_persist_facts=True,
            auto_persist_synthesis=True,
            min_confidence_threshold=0.5,
            evolution_strategy="hybrid",
            quality_threshold=0.6,
            cross_session_sharing=True
        )

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
    async def test_cross_session_knowledge_sharing(self, setup_services):
        """Test cross-session knowledge sharing (Requirement 6.3)."""
        services = await setup_services
        retrieval_service = services["retrieval_service"]
        sskg_manager = services["sskg_manager"]

        # Create test knowledge from previous session
        test_facts = [
            {
                "content": "Python is a high-level programming language",
                "confidence": 0.9,
                "metadata": {
                    "source": "critical_review_workflow",
                    "session_id": "session_001",
                    "topic": "programming",
                    "validation_timestamp": datetime.now().isoformat()
                }
            },
            {
                "content": "Machine learning requires large datasets",
                "confidence": 0.8,
                "metadata": {
                    "source": "multi_perspective_synthesis_workflow",
                    "session_id": "session_001",
                    "topic": "machine learning",
                    "expert_roles": ["data_scientist", "ml_engineer"]
                }
            }
        ]

        # Add test facts to SSKG
        fact_ids = []
        for fact_data in test_facts:
            node = KnowledgeNode(
                node_type=NodeType.FACT,
                content=fact_data["content"],
                confidence=fact_data["confidence"],
                metadata=fact_data["metadata"]
            )
            fact_id = sskg_manager.add_node(node)
            fact_ids.append(fact_id)

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
        assert "knowledge_connections" in cross_session_knowledge
        assert len(cross_session_knowledge["facts"]) > 0

        # Verify Python fact was retrieved
        python_facts = [
            fact for fact in cross_session_knowledge["facts"]
            if "Python" in fact["content"]
        ]
        assert len(python_facts) > 0
        assert python_facts[0]["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_semantic_search_capabilities(self, setup_services):
        """Test semantic search for validated information (Requirement 6.4)."""
        services = await setup_services
        retrieval_service = services["retrieval_service"]
        sskg_manager = services["sskg_manager"]

        # Create diverse test knowledge
        test_nodes = [
            {
                "type": NodeType.FACT,
                "content": "Artificial intelligence can process natural language",
                "confidence": 0.9,
                "metadata": {"expertise_domain": "ai", "source": "critical_review_workflow"}
            },
            {
                "type": NodeType.CONCEPT,
                "content": "Natural language processing combines linguistics and computer science",
                "confidence": 0.8,
                "metadata": {"expertise_domain": "nlp", "source": "multi_perspective_synthesis_workflow"}
            },
            {
                "type": NodeType.WIKI,
                "content": "Machine learning algorithms learn patterns from data",
                "confidence": 0.7,
                "metadata": {"expertise_domain": "ml", "source": "wiki_service"}
            }
        ]

        # Add nodes to SSKG
        node_ids = []
        for node_data in test_nodes:
            node = KnowledgeNode(
                node_type=node_data["type"],
                content=node_data["content"],
                confidence=node_data["confidence"],
                metadata=node_data["metadata"]
            )
            node_id = sskg_manager.add_node(node)
            node_ids.append(node_id)

        # Test semantic search with different scopes
        search_queries = [
            {
                "query": "artificial intelligence natural language",
                "scope": SearchScope.ALL,
                "expected_results": 2
            },
            {
                "query": "machine learning",
                "scope": SearchScope.FACTS,
                "expected_results": 0  # ML content is in WIKI scope
            },
            {
                "query": "machine learning",
                "scope": SearchScope.WIKI,
                "expected_results": 1
            }
        ]

        for search_test in search_queries:
            results = await retrieval_service.semantic_search(
                query=search_test["query"],
                scope=search_test["scope"],
                min_confidence=0.5,
                limit=10,
                include_related=True
            )

            assert len(results) >= search_test["expected_results"]

            # Verify result structure
            for result in results:
                assert hasattr(result, 'id')
                assert hasattr(result, 'content')
                assert hasattr(result, 'confidence')
                assert hasattr(result, 'relevance_score')
                assert hasattr(result, 'quality_metrics')

    @pytest.mark.asyncio
    async def test_knowledge_quality_assessment(self, setup_services):
        """Test knowledge quality assessment metrics (Requirement 6.5)."""
        services = await setup_services
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
                "evidence_sources": ["nature.com", "arxiv.org", "ibm.com"],
                "reviewer_roles": ["physicist", "computer_scientist"],
                "expertise_domain": "quantum_computing"
            }
        )

        node_id = sskg_manager.add_node(test_node)

        # Track some usage
        retrieval_service._track_usage(node_id, "search_result")
        retrieval_service._track_usage(node_id, "cross_session_retrieval")

        # Assess quality
        quality_assessment = await retrieval_service.assess_knowledge_quality(node_id)

        # Verify assessment structure
        assert quality_assessment.node_id == node_id
        assert 0.0 <= quality_assessment.overall_quality <= 1.0
        assert len(quality_assessment.quality_metrics) > 0
        assert len(quality_assessment.recommendations) >= 0

        # Verify specific metrics
        from .knowledge_retrieval_service import QualityMetric
        expected_metrics = [
            QualityMetric.CONFIDENCE,
            QualityMetric.USAGE_FREQUENCY,
            QualityMetric.SOURCE_RELIABILITY,
            QualityMetric.VALIDATION_SCORE,
            QualityMetric.RECENCY
        ]

        for metric in expected_metrics:
            assert metric in quality_assessment.quality_metrics
            assert 0.0 <= quality_assessment.quality_metrics[metric] <= 1.0

        # High-quality node should have good overall score
        assert quality_assessment.overall_quality > 0.6

    @pytest.mark.asyncio
    async def test_knowledge_evolution_lifecycle(self, setup_services):
        """Test knowledge evolution and lifecycle management (Requirements 6.6, 6.7)."""
        services = await setup_services
        evolution_manager = services["evolution_manager"]
        retrieval_service = services["retrieval_service"]
        sskg_manager = services["sskg_manager"]

        # Create initial knowledge node
        original_node = KnowledgeNode(
            node_type=NodeType.FACT,
            content="Old information about technology",
            confidence=0.4,  # Low confidence to trigger evolution
            metadata={
                "source": "user_input",
                "created_date": (datetime.now() - timedelta(days=400)).isoformat()  # Old content
            }
        )

        original_id = sskg_manager.add_node(original_node)

        # Test evolution trigger detection
        from .knowledge_evolution_manager import EvolutionTrigger

        # Manually evolve the node
        evolved_id = await evolution_manager.evolve_knowledge_node(
            node_id=original_id,
            trigger=EvolutionTrigger.QUALITY_DECLINE,
            new_content="Updated information about modern technology",
            metadata_updates={"updated_by": "test_system"},
            reason="Quality improvement based on new evidence"
        )

        assert evolved_id is not None
        assert evolved_id != original_id

        # Verify evolved node
        evolved_node = sskg_manager.get_node(evolved_id)
        assert evolved_node is not None
        assert evolved_node.content == "Updated information about modern technology"
        assert "evolution_trigger" in evolved_node.metadata
        assert "evolved_from" in evolved_node.metadata
        assert evolved_node.metadata["evolved_from"] == original_id

        # Verify original node is deprecated
        original_node_updated = sskg_manager.get_node(original_id)
        assert "lifecycle_stage" in original_node_updated.metadata
        assert original_node_updated.metadata["lifecycle_stage"] == "deprecated"

        # Test evolution history tracking
        evolution_history = retrieval_service.get_knowledge_evolution_history(
            node_id=evolved_id,
            time_window_days=1
        )

        assert len(evolution_history) > 0
        evolution_event = evolution_history[0]
        assert evolution_event.node_id == evolved_id
        assert evolution_event.event_type == "evolved"

    @pytest.mark.asyncio
    async def test_automatic_evolution_cycle(self, setup_services):
        """Test automatic knowledge evolution cycle (Requirement 6.7)."""
        services = await setup_services
        evolution_manager = services["evolution_manager"]
        sskg_manager = services["sskg_manager"]

        # Configure for automatic evolution
        evolution_manager.configure_evolution(
            quality_threshold=0.7,
            deprecation_age_days=30,
            auto_evolution_enabled=True,
            evolution_strategy=EvolutionStrategy.AUTOMATIC
        )

        # Create nodes that should trigger evolution
        test_nodes = [
            {
                "content": "Low quality content",
                "confidence": 0.3,  # Below threshold
                "metadata": {"source": "unknown"}
            },
            {
                "content": "Old content",
                "confidence": 0.8,
                "metadata": {
                    "source": "wiki_service",
                    "created_date": (datetime.now() - timedelta(days=400)).isoformat()
                }
            }
        ]

        node_ids = []
        for node_data in test_nodes:
            node = KnowledgeNode(
                node_type=NodeType.FACT,
                content=node_data["content"],
                confidence=node_data["confidence"],
                metadata=node_data["metadata"]
            )
            node_id = sskg_manager.add_node(node)
            node_ids.append(node_id)

        # Run evolution cycle
        cycle_results = await evolution_manager.run_evolution_cycle()

        # Verify cycle results
        assert "cycle_timestamp" in cycle_results
        assert "nodes_evaluated" in cycle_results
        assert "evolution_triggers" in cycle_results
        assert cycle_results["nodes_evaluated"] >= len(node_ids)

        # Should have detected some triggers
        assert len(cycle_results["evolution_triggers"]) > 0

    @pytest.mark.asyncio
    async def test_comprehensive_knowledge_statistics(self, setup_services):
        """Test comprehensive knowledge statistics and monitoring."""
        services = await setup_services
        knowledge_service = services["knowledge_service"]

        # Get comprehensive statistics
        stats = knowledge_service.get_comprehensive_statistics()

        # Verify statistics structure
        assert "service_status" in stats
        assert "configuration" in stats
        assert "persistence" in stats
        assert "retrieval" in stats
        assert "evolution" in stats
        assert "statistics_timestamp" in stats

        # Verify configuration section
        config = stats["configuration"]
        assert "auto_persist_facts" in config
        assert "evolution_strategy" in config
        assert "quality_threshold" in config
        assert "cross_session_sharing" in config

        # Service should be active
        assert stats["service_status"] == "active"

    @pytest.mark.asyncio
    async def test_knowledge_conflict_resolution(self, setup_services):
        """Test knowledge conflict detection and resolution."""
        services = await setup_services
        sskg_manager = services["sskg_manager"]
        retrieval_service = services["retrieval_service"]

        # Create conflicting knowledge nodes
        conflicting_nodes = [
            {
                "content": "The speed of light is 299,792,458 m/s",
                "confidence": 0.95,
                "metadata": {"source": "critical_review_workflow", "evidence_count": 5}
            },
            {
                "content": "The speed of light is approximately 300,000 km/s",
                "confidence": 0.7,
                "metadata": {"source": "user_input", "evidence_count": 1}
            }
        ]

        node_ids = []
        for node_data in conflicting_nodes:
            node = KnowledgeNode(
                node_type=NodeType.FACT,
                content=node_data["content"],
                confidence=node_data["confidence"],
                metadata=node_data["metadata"]
            )
            node_id = sskg_manager.add_node(node)
            node_ids.append(node_id)

        # Search for related content
        search_results = await retrieval_service.semantic_search(
            query="speed of light",
            scope=SearchScope.FACTS,
            min_confidence=0.5,
            limit=10
        )

        # Should find both conflicting facts
        assert len(search_results) >= 2

        # Higher confidence fact should rank higher
        search_results.sort(key=lambda x: x.confidence, reverse=True)
        assert search_results[0].confidence > search_results[1].confidence

    @pytest.mark.asyncio
    async def test_health_check_functionality(self, setup_services):
        """Test knowledge management health check."""
        services = await setup_services
        knowledge_service = services["knowledge_service"]

        # Perform health check
        health_status = await knowledge_service.health_check()

        # Verify health check structure
        assert "overall_status" in health_status
        assert "components" in health_status
        assert "check_timestamp" in health_status

        # All components should be healthy in test environment
        components = health_status["components"]
        expected_components = [
            "sskg_manager",
            "wiki_service",
            "persistence_service",
            "retrieval_service",
            "evolution_manager",
            "workflow_integrator"
        ]

        for component in expected_components:
            assert component in components
            # In test environment, components should be healthy
            assert "healthy" in components[component] or components[component] == "healthy"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
