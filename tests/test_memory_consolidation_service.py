"""@Time    : 2025-07-23 11:30:00
@Author  : DAIP-LIVE Team
@File    : test_memory_consolidation_service.py
@Description:
    Unit tests for MemoryConsolidationService.
"""
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from src.core_services.memory_agent import MemAgent, Memory, MemoryType
from src.core_services.memory_consolidation_service import (
    ConflictResolutionStrategy,
    MemoryConflict,
    MemoryConsolidationService,
    SharingPolicy,
)


class TestMemoryConsolidationService:
    """Test cases for MemoryConsolidationService."""
    
    @pytest.fixture()
    def mock_mem_agent(self):
        """Create a mock MemAgent for testing."""
        return Mock(spec=MemAgent)
    
    @pytest.fixture()
    def consolidation_service(self, mock_mem_agent):
        """Create a MemoryConsolidationService instance for testing."""
        return MemoryConsolidationService(mock_mem_agent)
    
    @pytest.fixture()
    def sample_memories(self):
        """Create sample memories for testing."""
        return [
            Memory(
                id="mem_1",
                content="This is about machine learning algorithms",
                memory_type=MemoryType.SEMANTIC,
                source_id="user_1",
                importance=0.8,
                recency=0.9,
                created_at=datetime.now() - timedelta(days=1)
            ),
            Memory(
                id="mem_2", 
                content="Machine learning is a subset of AI",
                memory_type=MemoryType.SEMANTIC,
                source_id="user_1",
                importance=0.7,
                recency=0.8,
                created_at=datetime.now() - timedelta(days=2)
            ),
            Memory(
                id="mem_3",
                content="Deep learning uses neural networks",
                memory_type=MemoryType.SEMANTIC,
                source_id="user_1",
                importance=0.9,
                recency=0.7,
                created_at=datetime.now() - timedelta(days=3)
            ),
            Memory(
                id="mem_4",
                content="Yesterday I worked on a project",
                memory_type=MemoryType.EPISODIC,
                source_id="user_1",
                importance=0.6,
                recency=0.9,
                created_at=datetime.now() - timedelta(hours=12)
            ),
            Memory(
                id="mem_5",
                content="I learned how to use Python",
                memory_type=MemoryType.PROCEDURAL,
                source_id="user_1",
                importance=0.8,
                recency=0.6,
                created_at=datetime.now() - timedelta(days=5)
            )
        ]
    
    def test_service_initialization(self, mock_mem_agent):
        """Test service initialization."""
        service = MemoryConsolidationService(mock_mem_agent)
        
        assert service.mem_agent == mock_mem_agent
        assert service.sharing_policies == []
        assert service.consolidation_stats["total_consolidations"] == 0
        assert service.consolidation_stats["conflicts_resolved"] == 0
        assert service.consolidation_stats["memories_shared"] == 0
    
    def test_consolidate_memories_advanced(self, consolidation_service, mock_mem_agent, sample_memories):
        """Test advanced memory consolidation."""
        # Mock the retrieve_memories method
        mock_mem_agent.retrieve_memories.return_value = sample_memories
        mock_mem_agent.store_memory.return_value = "consolidated_id"
        
        # Consolidate memories
        result = consolidation_service.consolidate_memories_advanced("user_1")
        
        # Verify results
        assert len(result) >= 1  # Should have at least one consolidated memory
        
        # Verify that memories were grouped by type
        semantic_consolidated = [m for m in result if m.memory_type == MemoryType.SEMANTIC]
        assert len(semantic_consolidated) >= 1
        
        # Verify consolidated memory properties
        consolidated = semantic_consolidated[0]
        assert consolidated.source_id == "user_1"
        assert consolidated.metadata.get("consolidated") is True
        assert "consolidation_time" in consolidated.metadata
        assert "source_memories" in consolidated.metadata
        
        # Verify store_memory was called
        assert mock_mem_agent.store_memory.call_count >= 1
        
        # Verify statistics were updated
        assert consolidation_service.consolidation_stats["total_consolidations"] > 0
    
    def test_consolidate_memories_insufficient_data(self, consolidation_service, mock_mem_agent):
        """Test consolidation with insufficient memories."""
        # Mock with too few memories
        mock_mem_agent.retrieve_memories.return_value = [
            Memory(
                content="Single memory",
                memory_type=MemoryType.SEMANTIC,
                source_id="user_1",
                importance=0.5,
                recency=0.5
            )
        ]
        
        # Consolidate memories
        result = consolidation_service.consolidate_memories_advanced("user_1")
        
        # Should return empty list
        assert result == []
        
        # Store should not be called
        mock_mem_agent.store_memory.assert_not_called()
    
    def test_create_consolidated_memory(self, consolidation_service, sample_memories):
        """Test consolidated memory creation."""
        # Take first 3 semantic memories
        semantic_memories = [m for m in sample_memories if m.memory_type == MemoryType.SEMANTIC][:3]
        
        # Create consolidated memory
        consolidated = consolidation_service._create_consolidated_memory(
            semantic_memories,
            "Test Consolidated Memory",
            MemoryType.SEMANTIC,
            "user_1"
        )
        
        # Verify properties
        assert consolidated.memory_type == MemoryType.SEMANTIC
        assert consolidated.source_id == "user_1"
        assert "Test Consolidated Memory" in consolidated.content
        assert consolidated.metadata.get("consolidated") is True
        assert len(consolidated.metadata.get("source_memories", [])) == 3
        
        # Verify importance is boosted
        avg_importance = sum(m.importance for m in semantic_memories) / len(semantic_memories)
        expected_importance = min(avg_importance * 1.1, 1.0)
        assert abs(consolidated.importance - expected_importance) < 0.01
        
        # Verify recency is max of source memories
        max_recency = max(m.recency for m in semantic_memories)
        assert consolidated.recency == max_recency
    
    def test_detect_memory_conflicts_duplicates(self, consolidation_service, mock_mem_agent):
        """Test duplicate memory detection."""
        # Create duplicate memories
        duplicate_memories = [
            Memory(
                id="mem_1",
                content="Machine learning is a subset of artificial intelligence",
                memory_type=MemoryType.SEMANTIC,
                source_id="user_1",
                importance=0.8,
                recency=0.9
            ),
            Memory(
                id="mem_2",
                content="Machine learning is a subset of artificial intelligence",
                memory_type=MemoryType.SEMANTIC,
                source_id="user_1",
                importance=0.7,
                recency=0.8
            )
        ]
        
        mock_mem_agent.retrieve_memories.return_value = duplicate_memories
        
        # Detect conflicts
        conflicts = consolidation_service.detect_memory_conflicts("user_1")
        
        # Verify duplicate was detected
        assert len(conflicts) == 1
        conflict = conflicts[0]
        assert conflict.conflict_type == "duplication"
        assert conflict.severity == 0.6
        assert len(conflict.conflicting_memories) == 2
        assert "Duplicate memories detected" in conflict.description
    
    def test_detect_memory_conflicts_no_duplicates(self, consolidation_service, mock_mem_agent, sample_memories):
        """Test conflict detection with no duplicates."""
        mock_mem_agent.retrieve_memories.return_value = sample_memories
        
        # Detect conflicts
        conflicts = consolidation_service.detect_memory_conflicts("user_1")
        
        # Should find no conflicts (sample memories are different enough)
        assert len(conflicts) == 0
    
    def test_calculate_similarity(self, consolidation_service):
        """Test content similarity calculation."""
        # Test identical content
        similarity = consolidation_service._calculate_similarity(
            "machine learning algorithms",
            "machine learning algorithms"
        )
        assert similarity == 1.0
        
        # Test partial similarity
        similarity = consolidation_service._calculate_similarity(
            "machine learning algorithms",
            "machine learning models"
        )
        assert 0.0 < similarity < 1.0
        
        # Test no similarity
        similarity = consolidation_service._calculate_similarity(
            "machine learning",
            "cooking recipes"
        )
        assert similarity == 0.0
        
        # Test empty content
        similarity = consolidation_service._calculate_similarity("", "")
        assert similarity == 0.0
    
    def test_resolve_memory_conflict_confidence_based(self, consolidation_service, mock_mem_agent):
        """Test conflict resolution using confidence-based strategy."""
        # Create conflict with different importance levels
        memories = [
            Memory(
                id="mem_1",
                content="Content A",
                memory_type=MemoryType.SEMANTIC,
                source_id="user_1",
                importance=0.6,
                recency=0.8
            ),
            Memory(
                id="mem_2",
                content="Content B",
                memory_type=MemoryType.SEMANTIC,
                source_id="user_1",
                importance=0.9,  # Higher importance
                recency=0.7
            )
        ]
        
        conflict = MemoryConflict(
            conflicting_memories=memories,
            conflict_type="duplication",
            severity=0.6,
            description="Test conflict"
        )
        
        mock_mem_agent.store_memory.return_value = "resolved_id"
        
        # Resolve conflict
        resolved = consolidation_service.resolve_memory_conflict(
            conflict, 
            ConflictResolutionStrategy.CONFIDENCE_BASED
        )
        
        # Verify resolution
        assert resolved is not None
        assert resolved.content == "Content B"  # Higher importance memory
        assert resolved.importance == 0.9
        assert resolved.metadata.get("conflict_resolved") is True
        assert resolved.metadata.get("resolution_strategy") == "confidence_based"
        
        # Verify store was called
        mock_mem_agent.store_memory.assert_called_once()
        
        # Verify statistics were updated
        assert consolidation_service.consolidation_stats["conflicts_resolved"] == 1
    
    def test_resolve_memory_conflict_temporal(self, consolidation_service, mock_mem_agent):
        """Test conflict resolution using temporal strategy."""
        now = datetime.now()
        
        memories = [
            Memory(
                id="mem_1",
                content="Older content",
                memory_type=MemoryType.SEMANTIC,
                source_id="user_1",
                importance=0.8,
                recency=0.8,
                created_at=now - timedelta(days=2)
            ),
            Memory(
                id="mem_2",
                content="Newer content",
                memory_type=MemoryType.SEMANTIC,
                source_id="user_1",
                importance=0.6,
                recency=0.7,
                created_at=now - timedelta(days=1)  # More recent
            )
        ]
        
        conflict = MemoryConflict(
            conflicting_memories=memories,
            conflict_type="duplication",
            severity=0.6,
            description="Test conflict"
        )
        
        mock_mem_agent.store_memory.return_value = "resolved_id"
        
        # Resolve conflict
        resolved = consolidation_service.resolve_memory_conflict(
            conflict,
            ConflictResolutionStrategy.TEMPORAL
        )
        
        # Verify resolution
        assert resolved is not None
        assert resolved.content == "Newer content"  # More recent memory
        assert resolved.metadata.get("resolution_strategy") == "temporal"
    
    def test_resolve_memory_conflict_empty(self, consolidation_service):
        """Test conflict resolution with empty conflict."""
        conflict = MemoryConflict(
            conflicting_memories=[],
            conflict_type="duplication",
            severity=0.6,
            description="Empty conflict"
        )
        
        # Resolve conflict
        resolved = consolidation_service.resolve_memory_conflict(conflict)
        
        # Should return None
        assert resolved is None
    
    def test_add_sharing_policy(self, consolidation_service):
        """Test adding sharing policy."""
        policy = SharingPolicy(
            source_id="user_1",
            target_id="user_2",
            allowed_memory_types=[MemoryType.SEMANTIC, MemoryType.PROCEDURAL],
            importance_threshold=0.7,
            max_memories_per_share=5
        )
        
        # Add policy
        consolidation_service.add_sharing_policy(policy)
        
        # Verify policy was added
        assert len(consolidation_service.sharing_policies) == 1
        assert consolidation_service.sharing_policies[0] == policy
    
    def test_execute_sharing_policy(self, consolidation_service, mock_mem_agent, sample_memories):
        """Test executing sharing policy."""
        # Create policy
        policy = SharingPolicy(
            source_id="user_1",
            target_id="user_2",
            allowed_memory_types=[MemoryType.SEMANTIC],
            importance_threshold=0.7,
            max_memories_per_share=5
        )
        
        # Mock retrieve_memories to return semantic memories above threshold
        semantic_memories = [m for m in sample_memories if m.memory_type == MemoryType.SEMANTIC and m.importance >= 0.7]
        mock_mem_agent.retrieve_memories.return_value = semantic_memories
        mock_mem_agent.share_memories.return_value = True
        
        # Execute policy
        shared_count = consolidation_service.execute_sharing_policy(policy)
        
        # Verify sharing
        assert shared_count == len(semantic_memories)
        
        # Verify share_memories was called
        mock_mem_agent.share_memories.assert_called_once()
        call_args = mock_mem_agent.share_memories.call_args
        assert call_args[0][0] == "user_1"  # source_id
        assert call_args[0][1] == "user_2"  # target_id
        assert len(call_args[0][2]) == len(semantic_memories)  # memory_ids
        
        # Verify statistics were updated
        assert consolidation_service.consolidation_stats["memories_shared"] == shared_count
    
    def test_execute_sharing_policy_no_memories(self, consolidation_service, mock_mem_agent):
        """Test executing sharing policy with no qualifying memories."""
        policy = SharingPolicy(
            source_id="user_1",
            target_id="user_2",
            allowed_memory_types=[MemoryType.SEMANTIC],
            importance_threshold=0.9,  # Very high threshold
            max_memories_per_share=5
        )
        
        # Mock retrieve_memories to return empty list
        mock_mem_agent.retrieve_memories.return_value = []
        
        # Execute policy
        shared_count = consolidation_service.execute_sharing_policy(policy)
        
        # Verify no sharing occurred
        assert shared_count == 0
        mock_mem_agent.share_memories.assert_not_called()
    
    def test_execute_sharing_policy_sharing_fails(self, consolidation_service, mock_mem_agent, sample_memories):
        """Test executing sharing policy when sharing fails."""
        policy = SharingPolicy(
            source_id="user_1",
            target_id="user_2",
            allowed_memory_types=[MemoryType.SEMANTIC],
            importance_threshold=0.5,
            max_memories_per_share=5
        )
        
        # Mock retrieve_memories and share_memories
        semantic_memories = [m for m in sample_memories if m.memory_type == MemoryType.SEMANTIC]
        mock_mem_agent.retrieve_memories.return_value = semantic_memories
        mock_mem_agent.share_memories.return_value = False  # Sharing fails
        
        # Execute policy
        shared_count = consolidation_service.execute_sharing_policy(policy)
        
        # Verify no memories were counted as shared
        assert shared_count == 0
        
        # Verify share_memories was called but failed
        mock_mem_agent.share_memories.assert_called_once()
    
    def test_get_consolidation_stats(self, consolidation_service):
        """Test getting consolidation statistics."""
        # Modify some stats
        consolidation_service.consolidation_stats["total_consolidations"] = 5
        consolidation_service.consolidation_stats["conflicts_resolved"] = 2
        consolidation_service.consolidation_stats["memories_shared"] = 10
        
        # Get stats
        stats = consolidation_service.get_consolidation_stats()
        
        # Verify stats
        assert stats["total_consolidations"] == 5
        assert stats["conflicts_resolved"] == 2
        assert stats["memories_shared"] == 10
        
        # Verify it's a copy (modifying returned stats shouldn't affect original)
        stats["total_consolidations"] = 100
        assert consolidation_service.consolidation_stats["total_consolidations"] == 5


if __name__ == "__main__":
    pytest.main([__file__])