"""Unit tests for the Knowledge Conflict Resolver.
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager, KnowledgeNode, NodeType
from src.core_services.conflict_resolution_system import (
    ConflictType,
    KnowledgeConflictResolver,
    ResolutionStrategy,
)
from src.core_services.perspective_conflict_detector import ConflictDetectionResult


class TestKnowledgeConflictResolver(unittest.TestCase):
    """Test cases for the Knowledge Conflict Resolver."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock SSKG manager
        self.sskg_manager = MagicMock(spec=EnhancedSSKGManager)

        # Create conflict resolver
        self.resolver = KnowledgeConflictResolver(self.sskg_manager)

        # Create test nodes
        self.node1 = KnowledgeNode(
            id="node1",
            node_type=NodeType.FACT,
            content="The Earth orbits the Sun.",
            confidence=0.9,
            metadata={"source": "reputable_publication"}
        )

        self.node2 = KnowledgeNode(
            id="node2",
            node_type=NodeType.FACT,
            content="The Earth does not orbit the Sun.",
            confidence=0.5,
            metadata={"source": "unverified_source"}
        )

        self.node3 = KnowledgeNode(
            id="node3",
            node_type=NodeType.FACT,
            content="The Earth orbits the Sun in 365.25 days.",
            confidence=0.8,
            metadata={"source": "verified_database"}
        )

        # Configure mock
        self.sskg_manager.get_node.side_effect = lambda node_id: {
            "node1": self.node1,
            "node2": self.node2,
            "node3": self.node3
        }.get(node_id)

    def test_detect_conflicts_direct_contradiction(self):
        """Test detecting direct contradictions."""
        # Configure mock to return contradicting node
        self.sskg_manager.query.return_value = [self.node2]

        # Detect conflicts
        conflicts = self.resolver.detect_conflicts("node1")

        # Verify results
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].conflict_type, ConflictType.DIRECT_CONTRADICTION)
        self.assertEqual(set(conflicts[0].conflicting_nodes), {"node1", "node2"})

    def test_detect_conflicts_partial_overlap(self):
        """Test detecting partial overlaps."""
        # Configure mock to return partially overlapping node
        self.sskg_manager.query.return_value = [self.node3]

        # Patch similarity calculation to return moderate overlap
        with patch.object(self.resolver, '_calculate_contradiction_score', return_value=0.4):
            # Detect conflicts
            conflicts = self.resolver.detect_conflicts("node1")

            # Verify results
            self.assertEqual(len(conflicts), 1)
            self.assertEqual(conflicts[0].conflict_type, ConflictType.PARTIAL_OVERLAP)
            self.assertEqual(set(conflicts[0].conflicting_nodes), {"node1", "node3"})

    def test_resolve_conflicts_highest_confidence(self):
        """Test resolving conflicts by highest confidence."""
        # Create test conflict
        conflict = ConflictDetectionResult(
            conflict_type=ConflictType.DIRECT_CONTRADICTION,
            conflicting_nodes=["node1", "node2"],
            confidence=0.8,
            description="Test conflict"
        )

        # Resolve conflict
        results = self.resolver.resolve_conflicts([conflict], ResolutionStrategy.HIGHEST_CONFIDENCE)

        # Verify results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].resolution_strategy, ResolutionStrategy.HIGHEST_CONFIDENCE)
        self.assertEqual(results[0].resolved_node_id, "node1")  # node1 has higher confidence

    def test_resolve_conflicts_most_recent(self):
        """Test resolving conflicts by most recent."""
        # Set different timestamps
        self.node1.updated_at = datetime.now() - timedelta(days=1)
        self.node2.updated_at = datetime.now()

        # Create test conflict
        conflict = ConflictDetectionResult(
            conflict_type=ConflictType.TEMPORAL_INCONSISTENCY,
            conflicting_nodes=["node1", "node2"],
            confidence=0.8,
            description="Test conflict"
        )

        # Resolve conflict
        results = self.resolver.resolve_conflicts([conflict], ResolutionStrategy.MOST_RECENT)

        # Verify results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].resolution_strategy, ResolutionStrategy.MOST_RECENT)
        self.assertEqual(results[0].resolved_node_id, "node2")  # node2 is more recent

    def test_resolve_conflicts_source_reliability(self):
        """Test resolving conflicts by source reliability."""
        # Create test conflict
        conflict = ConflictDetectionResult(
            conflict_type=ConflictType.SOURCE_DISAGREEMENT,
            conflicting_nodes=["node1", "node2"],
            confidence=0.8,
            description="Test conflict"
        )

        # Resolve conflict
        results = self.resolver.resolve_conflicts([conflict], ResolutionStrategy.SOURCE_RELIABILITY)

        # Verify results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].resolution_strategy, ResolutionStrategy.SOURCE_RELIABILITY)
        self.assertEqual(results[0].resolved_node_id, "node1")  # node1 has more reliable source

    def test_resolve_conflicts_synthesis(self):
        """Test resolving conflicts by synthesis."""
        # Configure mock to return new node ID
        self.sskg_manager.add_node.return_value = "new_node"

        # Create test conflict
        conflict = ConflictDetectionResult(
            conflict_type=ConflictType.PARTIAL_OVERLAP,
            conflicting_nodes=["node1", "node3"],
            confidence=0.8,
            description="Test conflict"
        )

        # Resolve conflict
        results = self.resolver.resolve_conflicts([conflict], ResolutionStrategy.SYNTHESIS)

        # Verify results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].resolution_strategy, ResolutionStrategy.SYNTHESIS)
        self.assertEqual(results[0].resolved_node_id, "new_node")

        # Verify that a new node was created
        self.sskg_manager.add_node.assert_called_once()

    def test_select_resolution_strategy(self):
        """Test automatic selection of resolution strategy."""
        # Create test conflicts with different types
        conflicts = [
            ConflictDetectionResult(
                conflict_type=ConflictType.DIRECT_CONTRADICTION,
                conflicting_nodes=["node1", "node2"],
                confidence=0.8,
                description="Direct contradiction"
            ),
            ConflictDetectionResult(
                conflict_type=ConflictType.TEMPORAL_INCONSISTENCY,
                conflicting_nodes=["node1", "node2"],
                confidence=0.8,
                description="Temporal inconsistency"
            ),
            ConflictDetectionResult(
                conflict_type=ConflictType.SOURCE_DISAGREEMENT,
                conflicting_nodes=["node1", "node2"],
                confidence=0.8,
                description="Source disagreement"
            ),
            ConflictDetectionResult(
                conflict_type=ConflictType.PARTIAL_OVERLAP,
                conflicting_nodes=["node1", "node3"],
                confidence=0.8,
                description="Partial overlap"
            )
        ]

        # Resolve conflicts with automatic strategy selection
        results = self.resolver.resolve_conflicts(conflicts)

        # Verify that appropriate strategies were selected
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0].resolution_strategy, ResolutionStrategy.HIGHEST_CONFIDENCE)
        self.assertEqual(results[1].resolution_strategy, ResolutionStrategy.MOST_RECENT)
        self.assertEqual(results[2].resolution_strategy, ResolutionStrategy.SOURCE_RELIABILITY)
        self.assertEqual(results[3].resolution_strategy, ResolutionStrategy.SYNTHESIS)

    def test_track_knowledge_evolution(self):
        """Test tracking knowledge evolution."""
        # Configure mock to return related nodes
        derived_node = KnowledgeNode(
            id="derived_node",
            node_type=NodeType.FACT,
            content="The Earth orbits the Sun in exactly 365.25 days.",
            confidence=0.95,
            created_at=datetime.now()
        )

        source_node = KnowledgeNode(
            id="source_node",
            node_type=NodeType.FACT,
            content="The Earth orbits the Sun.",
            confidence=0.7,
            created_at=datetime.now() - timedelta(days=30)
        )

        self.sskg_manager.get_related_nodes.side_effect = lambda **kwargs: (
            [(derived_node, "derived_from")] if kwargs.get("direction") == "incoming"
            else [(source_node, "derived_from")]
        )

        # Track evolution
        evolution = self.resolver.track_knowledge_evolution("node1")

        # Verify results
        self.assertEqual(len(evolution), 2)
        self.assertEqual(evolution[0]["event_type"], "derived_from_source")
        self.assertEqual(evolution[0]["node_id"], "source_node")
        self.assertEqual(evolution[1]["event_type"], "derived_from")
        self.assertEqual(evolution[1]["node_id"], "derived_node")


@pytest.fixture()
def mock_sskg_manager():
    """Create a mock SSKG manager."""
    return MagicMock(spec=EnhancedSSKGManager)


@pytest.fixture()
def conflict_resolver(mock_sskg_manager):
    """Create a conflict resolver with mock SSKG manager."""
    return KnowledgeConflictResolver(mock_sskg_manager)


@pytest.fixture()
def test_nodes():
    """Create test nodes."""
    return {
        "node1": KnowledgeNode(
            id="node1",
            node_type=NodeType.FACT,
            content="The Earth orbits the Sun.",
            confidence=0.9,
            metadata={"source": "reputable_publication"}
        ),
        "node2": KnowledgeNode(
            id="node2",
            node_type=NodeType.FACT,
            content="The Earth does not orbit the Sun.",
            confidence=0.5,
            metadata={"source": "unverified_source"}
        ),
        "node3": KnowledgeNode(
            id="node3",
            node_type=NodeType.FACT,
            content="The Earth orbits the Sun in 365.25 days.",
            confidence=0.8,
            metadata={"source": "verified_database"}
        )
    }


class TestKnowledgeConflictResolverPytest:
    """Pytest-style tests for the Knowledge Conflict Resolver."""

    def test_detect_semantic_conflicts(self, conflict_resolver, test_nodes, mock_sskg_manager):
        """Test detecting semantic conflicts."""
        # Configure mock
        mock_sskg_manager.get_node.side_effect = lambda node_id: test_nodes.get(node_id)
        mock_sskg_manager.query.return_value = [test_nodes["node2"]]

        # Patch similarity calculation
        with patch.object(conflict_resolver, '_calculate_contradiction_score', return_value=0.8):
            # Detect conflicts
            conflicts = conflict_resolver._detect_semantic_conflicts(test_nodes["node1"])

            # Verify results
            assert len(conflicts) == 1
            assert conflicts[0].conflict_type == ConflictType.DIRECT_CONTRADICTION
            assert set(conflicts[0].conflicting_nodes) == {"node1", "node2"}

    def test_calculate_similarity_score(self, conflict_resolver, test_nodes):
        """Test calculating similarity scores."""
        # Calculate similarity between identical nodes
        score1 = conflict_resolver._calculate_similarity_score(test_nodes["node1"], test_nodes["node1"])
        assert score1 == 1.0

        # Calculate similarity between contradictory nodes
        score2 = conflict_resolver._calculate_similarity_score(test_nodes["node1"], test_nodes["node2"])
        assert 0 < score2 < 1.0

        # Calculate similarity between partially overlapping nodes
        score3 = conflict_resolver._calculate_similarity_score(test_nodes["node1"], test_nodes["node3"])
        assert score2 < score3 < 1.0

    def test_resolve_by_majority_vote(self, conflict_resolver, test_nodes, mock_sskg_manager):
        """Test resolving conflicts by majority vote."""
        # Create additional nodes with similar content
        node4 = KnowledgeNode(
            id="node4",
            node_type=NodeType.FACT,
            content="The Earth orbits the Sun.",
            confidence=0.85,
            metadata={"source": "expert_opinion"}
        )

        node5 = KnowledgeNode(
            id="node5",
            node_type=NodeType.FACT,
            content="The Earth orbits the Sun.",
            confidence=0.75,
            metadata={"source": "primary_source"}
        )

        # Configure mock
        mock_sskg_manager.get_node.side_effect = lambda node_id: {
            **test_nodes,
            "node4": node4,
            "node5": node5
        }.get(node_id)

        # Create test conflict
        conflict = ConflictDetectionResult(
            conflict_type=ConflictType.SOURCE_DISAGREEMENT,
            conflicting_nodes=["node1", "node2", "node3", "node4", "node5"],
            confidence=0.8,
            description="Test conflict"
        )

        # Patch similarity calculation to group similar nodes
        with patch.object(conflict_resolver, '_calculate_similarity_score',
                         side_effect=lambda a, b: 0.95 if "not" not in a.content and "not" not in b.content else 0.1):
            # Resolve conflict
            result = conflict_resolver._resolve_by_majority_vote(conflict, [
                test_nodes["node1"], test_nodes["node2"], test_nodes["node3"], node4, node5
            ])

            # Verify results
            assert result.resolution_strategy == ResolutionStrategy.MAJORITY_VOTE
            assert result.resolved_node_id == "node1"  # node1 has highest confidence in majority group
            assert result.confidence == 0.8  # 4 out of 5 nodes in majority group
