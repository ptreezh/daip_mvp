"""@Time    : 2025-07-23 10:00:00
@Author  : DAIP-LIVE Team
@File    : test_memory_agent.py
@Description:
    Unit tests for MemAgent core functionality.
"""
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.core_services.enhanced_sskg_manager import EnhancedSSKGManager, KnowledgeNode, NodeType
from src.core_services.memory_agent import MemAgent, Memory, MemoryQuery, MemoryType, TrainingExample


class TestMemAgent:
    """Test cases for MemAgent core functionality."""

    @pytest.fixture
    def mock_sskg_manager(self):
        """Create a mock SSKG manager for testing."""
        mock_manager = Mock(spec=EnhancedSSKGManager)
        return mock_manager

    @pytest.fixture
    def temp_model_path(self):
        """Create a temporary path for RL model storage."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            yield Path(f.name)
        # Cleanup is handled by tempfile

    @pytest.fixture
    def mem_agent(self, mock_sskg_manager, temp_model_path):
        """Create a MemAgent instance for testing."""
        return MemAgent(
            sskg_manager=mock_sskg_manager,
            model_path=temp_model_path,
            enable_rl=True
        )

    @pytest.fixture
    def sample_memory(self):
        """Create a sample memory for testing."""
        return Memory(
            content="This is a test memory about machine learning concepts",
            memory_type=MemoryType.SEMANTIC,
            source_id="test_user",
            importance=0.8,
            recency=0.9
        )

    def test_memory_agent_initialization(self, mock_sskg_manager, temp_model_path):
        """Test MemAgent initialization."""
        # Test with RL enabled
        agent = MemAgent(
            sskg_manager=mock_sskg_manager,
            model_path=temp_model_path,
            enable_rl=True
        )

        assert agent.sskg_manager == mock_sskg_manager
        assert agent.model_path == temp_model_path
        assert agent.enable_rl is True
        assert agent.rl_model is not None
        assert "weights" in agent.rl_model

        # Test with RL disabled
        agent_no_rl = MemAgent(
            sskg_manager=mock_sskg_manager,
            enable_rl=False
        )

        assert agent_no_rl.enable_rl is False
        assert agent_no_rl.rl_model is None

    def test_store_memory(self, mem_agent, sample_memory, mock_sskg_manager):
        """Test memory storage functionality."""
        # Mock SSKG manager response
        mock_sskg_manager.store_memory.return_value = "node_123"

        # Store memory
        memory_id = mem_agent.store_memory(sample_memory)

        # Verify memory was stored
        assert memory_id is not None
        assert memory_id.startswith("mem_")

        # Verify SSKG manager was called correctly
        mock_sskg_manager.store_memory.assert_called_once()
        call_args = mock_sskg_manager.store_memory.call_args

        assert call_args[1]["content"] == sample_memory.content
        assert call_args[1]["memory_type"] == sample_memory.memory_type.value
        assert call_args[1]["owner_id"] == sample_memory.source_id
        assert call_args[1]["importance"] == sample_memory.importance

    def test_retrieve_memories_simple(self, mem_agent, mock_sskg_manager):
        """Test simple memory retrieval without RL."""
        # Disable RL for this test
        mem_agent.enable_rl = False

        # Mock SSKG response
        mock_node = KnowledgeNode(
            id="node_123",
            content="Test memory content",
            node_type=NodeType.MEMORY,
            confidence=0.8,
            metadata={
                "memory_id": "mem_123",
                "memory_type": "semantic",
                "owner_id": "test_user",
                "recency": 0.9,
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 5,
                "related_memories": []
            }
        )
        mock_sskg_manager.query.return_value = [mock_node]
        mock_sskg_manager.update_node.return_value = True

        # Retrieve memories
        context = "machine learning concepts"
        memories = mem_agent.retrieve_memories(context, limit=5)

        # Verify results
        assert len(memories) == 1
        memory = memories[0]
        assert memory.content == "Test memory content"
        assert memory.memory_type == MemoryType.SEMANTIC
        assert memory.source_id == "test_user"
        assert memory.importance == 0.8

        # Verify SSKG manager was called
        mock_sskg_manager.query.assert_called_once()
        mock_sskg_manager.update_node.assert_called_once()

    def test_retrieve_memories_with_rl(self, mem_agent, mock_sskg_manager):
        """Test RL-based memory retrieval."""
        # Ensure RL is enabled
        mem_agent.enable_rl = True

        # Mock SSKG response with multiple memories
        mock_nodes = [
            KnowledgeNode(
                id=f"node_{i}",
                content=f"Test memory content {i}",
                node_type=NodeType.MEMORY,
                confidence=0.7 + (i * 0.1),
                metadata={
                    "memory_id": f"mem_{i}",
                    "memory_type": "semantic",
                    "owner_id": "test_user",
                    "recency": 0.8 + (i * 0.05),
                    "created_at": datetime.now().isoformat(),
                    "last_accessed": datetime.now().isoformat(),
                    "access_count": i * 2,
                    "related_memories": []
                }
            )
            for i in range(5)
        ]
        mock_sskg_manager.query.return_value = mock_nodes
        mock_sskg_manager.update_node.return_value = True

        # Retrieve memories
        context = "machine learning concepts"
        memories = mem_agent.retrieve_memories(context, limit=3)

        # Verify results
        assert len(memories) <= 3
        assert all(isinstance(m, Memory) for m in memories)

        # Verify memories are sorted by RL score (higher scores first)
        if len(memories) > 1:
            # We can't easily verify exact ordering without knowing the RL weights,
            # but we can verify that all memories are valid
            for memory in memories:
                assert memory.content is not None
                assert memory.memory_type == MemoryType.SEMANTIC

    def test_memory_query_filtering(self, mem_agent, mock_sskg_manager):
        """Test memory query with various filters."""
        # Disable RL for predictable results
        mem_agent.enable_rl = False

        # Mock SSKG response
        mock_node = KnowledgeNode(
            id="node_123",
            content="High importance memory",
            node_type=NodeType.MEMORY,
            confidence=0.9,
            metadata={
                "memory_id": "mem_123",
                "memory_type": "semantic",
                "owner_id": "test_user",
                "recency": 0.8,
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 10,
                "related_memories": []
            }
        )
        mock_sskg_manager.query.return_value = [mock_node]
        mock_sskg_manager.update_node.return_value = True

        # Test query with filters
        query = MemoryQuery(
            content="machine learning",
            memory_types=[MemoryType.SEMANTIC],
            source_id="test_user",
            min_importance=0.5,
            min_recency=0.7,
            limit=5
        )

        memories = mem_agent.retrieve_memories("context", query)

        # Verify filtering worked
        assert len(memories) == 1
        memory = memories[0]
        assert memory.memory_type == MemoryType.SEMANTIC
        assert memory.source_id == "test_user"
        assert memory.importance >= 0.5
        assert memory.recency >= 0.7

    def test_consolidate_memories(self, mem_agent, mock_sskg_manager):
        """Test memory consolidation functionality."""
        # Mock SSKG response with multiple memories
        mock_nodes = [
            KnowledgeNode(
                id=f"node_{i}",
                content=f"Episodic memory {i}",
                node_type=NodeType.MEMORY,
                confidence=0.8,
                metadata={
                    "memory_id": f"mem_{i}",
                    "memory_type": "episodic",
                    "owner_id": "test_user",
                    "recency": 0.9,
                    "created_at": datetime.now().isoformat(),
                    "last_accessed": datetime.now().isoformat(),
                    "access_count": 5,
                    "related_memories": []
                }
            )
            for i in range(5)
        ]
        mock_sskg_manager.query.return_value = mock_nodes
        mock_sskg_manager.store_memory.return_value = "consolidated_node"

        # Consolidate memories
        consolidated = mem_agent.consolidate_memories("test_user", MemoryType.EPISODIC)

        # Verify consolidation
        assert len(consolidated) == 1
        consolidated_memory = consolidated[0]
        assert "Recent experiences of test_user" in consolidated_memory.content
        assert consolidated_memory.memory_type == MemoryType.EPISODIC
        assert consolidated_memory.metadata.get("consolidated") is True
        assert len(consolidated_memory.related_memories) == 5

    def test_train_memory_selector(self, mem_agent):
        """Test RL model training functionality."""
        # Create training examples
        sample_memories = [
            Memory(
                id=f"mem_{i}",
                content=f"Training memory {i}",
                memory_type=MemoryType.SEMANTIC,
                source_id="test_user",
                importance=0.5 + (i * 0.1),
                recency=0.6 + (i * 0.1)
            )
            for i in range(5)
        ]

        training_examples = [
            TrainingExample(
                context="machine learning concepts",
                candidate_memories=sample_memories,
                selected_memories=["mem_3", "mem_4"],  # Higher importance memories
                reward=0.8
            ),
            TrainingExample(
                context="recent events",
                candidate_memories=sample_memories,
                selected_memories=["mem_4"],  # Highest recency
                reward=0.9
            )
        ]

        # Train the model
        result = mem_agent.train_memory_selector(training_examples)

        # Verify training results
        assert result["success"] is True
        assert "weights" in result
        assert result["training_examples"] == 2

        # Verify weights are normalized
        total_weight = sum(result["weights"].values())
        assert abs(total_weight - 1.0) < 0.01  # Allow for small floating point errors

    def test_get_memory_importance(self, mem_agent):
        """Test memory importance calculation."""
        # Test with relevant content
        memory_content = "This is critical information about machine learning algorithms"
        context = "machine learning concepts"

        importance = mem_agent.get_memory_importance(memory_content, context)

        # Verify importance calculation
        assert 0.0 <= importance <= 1.0
        assert importance > 0.3  # Should be above baseline due to relevance and keywords

        # Test with irrelevant content
        irrelevant_content = "Random text about cooking recipes"
        irrelevant_importance = mem_agent.get_memory_importance(irrelevant_content, context)

        # Should be lower than relevant content
        assert irrelevant_importance < importance

    def test_organize_memories(self, mem_agent):
        """Test memory organization functionality."""
        # Create memories of different types
        memories = [
            Memory(
                content="Episodic memory 1",
                memory_type=MemoryType.EPISODIC,
                source_id="test_user",
                importance=0.7,
                recency=0.9
            ),
            Memory(
                content="Semantic memory 1",
                memory_type=MemoryType.SEMANTIC,
                source_id="test_user",
                importance=0.9,
                recency=0.5
            ),
            Memory(
                content="Procedural memory 1",
                memory_type=MemoryType.PROCEDURAL,
                source_id="test_user",
                importance=0.6,
                recency=0.7,
                access_count=10
            ),
            Memory(
                content="Episodic memory 2",
                memory_type=MemoryType.EPISODIC,
                source_id="test_user",
                importance=0.5,
                recency=0.8
            )
        ]

        # Organize memories
        organized = mem_agent.organize_memories(memories)

        # Verify organization
        assert MemoryType.EPISODIC in organized
        assert MemoryType.SEMANTIC in organized
        assert MemoryType.PROCEDURAL in organized

        # Verify sorting
        episodic_memories = organized[MemoryType.EPISODIC]
        assert len(episodic_memories) == 2
        # Should be sorted by recency (descending)
        assert episodic_memories[0].recency >= episodic_memories[1].recency

        semantic_memories = organized[MemoryType.SEMANTIC]
        assert len(semantic_memories) == 1

        procedural_memories = organized[MemoryType.PROCEDURAL]
        assert len(procedural_memories) == 1

    def test_share_memories(self, mem_agent, mock_sskg_manager):
        """Test memory sharing functionality."""
        # Mock SSKG response
        mock_node = KnowledgeNode(
            id="node_123",
            content="Shared memory content",
            node_type=NodeType.MEMORY,
            confidence=0.8,
            metadata={
                "memory_id": "mem_123",
                "memory_type": "semantic",
                "owner_id": "source_user",
                "recency": 0.7,
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 5,
                "related_memories": []
            }
        )
        mock_sskg_manager.query.return_value = [mock_node]
        mock_sskg_manager.store_memory.return_value = "shared_node"

        # Share memories
        success = mem_agent.share_memories("source_user", "target_user", ["mem_123"])

        # Verify sharing
        assert success is True

        # Verify SSKG manager was called for querying and storing
        mock_sskg_manager.query.assert_called_once()
        mock_sskg_manager.store_memory.assert_called_once()

        # Verify the stored memory has sharing metadata
        store_call_args = mock_sskg_manager.store_memory.call_args
        stored_metadata = store_call_args[1]["metadata"]
        assert "shared_from" in stored_metadata
        assert stored_metadata["shared_from"] == "source_user"
        assert "original_memory_id" in stored_metadata

    def test_calculate_relevance(self, mem_agent):
        """Test relevance calculation between context and memory."""
        context = "machine learning algorithms and neural networks"

        # Test high relevance
        high_relevance_content = "deep learning algorithms for neural networks"
        high_score = mem_agent._calculate_relevance(context, high_relevance_content)

        # Test low relevance
        low_relevance_content = "cooking recipes and kitchen utensils"
        low_score = mem_agent._calculate_relevance(context, low_relevance_content)

        # Test no relevance
        no_relevance_content = "xyz abc def"
        no_score = mem_agent._calculate_relevance(context, no_relevance_content)

        # Verify relevance scores
        assert 0.0 <= high_score <= 1.0
        assert 0.0 <= low_score <= 1.0
        assert 0.0 <= no_score <= 1.0
        assert high_score > low_score
        assert low_score >= no_score

    def test_rl_model_persistence(self, mock_sskg_manager, temp_model_path):
        """Test RL model saving and loading."""
        # Create agent and train model
        agent = MemAgent(
            sskg_manager=mock_sskg_manager,
            model_path=temp_model_path,
            enable_rl=True
        )

        # Modify model weights
        original_weights = agent.rl_model["weights"].copy()
        agent.rl_model["weights"]["importance"] = 0.5
        agent.rl_model["training_examples"] = 10

        # Save model by training (which triggers save)
        training_examples = [
            TrainingExample(
                context="test",
                candidate_memories=[],
                selected_memories=[],
                reward=0.5
            )
        ]
        agent.train_memory_selector(training_examples)

        # Create new agent and verify model was loaded
        new_agent = MemAgent(
            sskg_manager=mock_sskg_manager,
            model_path=temp_model_path,
            enable_rl=True
        )

        # Verify model was loaded correctly
        assert new_agent.rl_model["training_examples"] == 11  # 10 + 1 from training
        # Note: weights will be normalized, so we can't check exact values
        assert new_agent.rl_model["weights"] != original_weights


if __name__ == "__main__":
    pytest.main([__file__])
