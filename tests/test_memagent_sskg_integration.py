"""@Time    : 2025-07-23 12:30:00
@Author  : DAIP-LIVE Team
@File    : test_memagent_sskg_integration.py
@Description:
    Unit tests for MemAgent-SSKG integration service.
"""
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from src.core_services.enhanced_sskg_manager import (
    EnhancedSSKGManager,
    KnowledgeNode,
    NodeType,
    RelationType,
)
from src.core_services.memagent_sskg_integration import MemoryKnowledgeMapping, UnifiedMemoryInterface
from src.core_services.memory_agent import MemAgent, Memory, MemoryType


class TestUnifiedMemoryInterface:
    """Test cases for UnifiedMemoryInterface."""
    
    @pytest.fixture()
    def mock_mem_agent(self):
        """Create a mock MemAgent for testing."""
        return Mock(spec=MemAgent)
    
    @pytest.fixture()
    def mock_sskg_manager(self):
        """Create a mock SSKG manager for testing."""
        return Mock(spec=EnhancedSSKGManager)
    
    @pytest.fixture()
    def unified_interface(self, mock_mem_agent, mock_sskg_manager):
        """Create a UnifiedMemoryInterface instance for testing."""
        return UnifiedMemoryInterface(mock_mem_agent, mock_sskg_manager)
    
    @pytest.fixture()
    def sample_memories(self):
        """Create sample memories for testing."""
        return [
            Memory(
                id="mem_1",
                content="Machine learning algorithms are powerful tools",
                memory_type=MemoryType.SEMANTIC,
                source_id="user_1",
                importance=0.8,
                recency=0.9,
                created_at=datetime.now() - timedelta(days=1)
            ),
            Memory(
                id="mem_2",
                content="I learned Python programming yesterday",
                memory_type=MemoryType.EPISODIC,
                source_id="user_1",
                importance=0.7,
                recency=0.8,
                created_at=datetime.now() - timedelta(days=2)
            )
        ]
    
    @pytest.fixture()
    def sample_knowledge_nodes(self):
        """Create sample knowledge nodes for testing."""
        return [
            KnowledgeNode(
                id="node_1",
                node_type=NodeType.FACT,
                content="Deep learning is a subset of machine learning",
                confidence=0.9,
                metadata={"owner_id": "user_1", "memory_type": "semantic"}
            ),
            KnowledgeNode(
                id="node_2",
                node_type=NodeType.EVENT,
                content="User completed Python tutorial",
                confidence=0.8,
                metadata={"owner_id": "user_1", "memory_type": "episodic"}
            )
        ]
    
    def test_interface_initialization(self, mock_mem_agent, mock_sskg_manager):
        """Test interface initialization."""
        interface = UnifiedMemoryInterface(mock_mem_agent, mock_sskg_manager)
        
        assert interface.mem_agent == mock_mem_agent
        assert interface.sskg_manager == mock_sskg_manager
        assert interface.memory_knowledge_mappings == {}
        assert interface.integration_stats["memories_transformed"] == 0
        assert interface.integration_stats["knowledge_nodes_created"] == 0
        assert interface.integration_stats["cross_references_created"] == 0
        assert interface.integration_stats["unified_queries"] == 0
    
    def test_unified_memory_retrieval_mem_agent_only(
        self, unified_interface, mock_mem_agent, mock_sskg_manager, sample_memories
    ):
        """Test unified memory retrieval with MemAgent only."""
        # Mock MemAgent response
        mock_mem_agent.retrieve_memories.return_value = sample_memories
        
        # Retrieve memories without including knowledge
        result = unified_interface.unified_memory_retrieval(
            context="machine learning",
            include_knowledge=False,
            limit=5
        )
        
        # Verify results
        assert len(result) == 2
        assert all(isinstance(m, Memory) for m in result)
        assert result[0].content == "Machine learning algorithms are powerful tools"
        
        # Verify MemAgent was called
        mock_mem_agent.retrieve_memories.assert_called_once()
        
        # Verify SSKG was not queried
        mock_sskg_manager.query.assert_not_called()
        
        # Verify statistics
        assert unified_interface.integration_stats["unified_queries"] == 1
    
    def test_unified_memory_retrieval_with_knowledge(
        self, unified_interface, mock_mem_agent, mock_sskg_manager, 
        sample_memories, sample_knowledge_nodes
    ):
        """Test unified memory retrieval including knowledge nodes."""
        # Mock responses
        mock_mem_agent.retrieve_memories.return_value = sample_memories
        mock_sskg_manager.query.return_value = sample_knowledge_nodes
        
        # Retrieve memories including knowledge
        result = unified_interface.unified_memory_retrieval(
            context="machine learning",
            include_knowledge=True,
            limit=10
        )
        
        # Verify results include both memories and converted knowledge
        assert len(result) >= 2  # At least the original memories
        
        # Verify both systems were called
        mock_mem_agent.retrieve_memories.assert_called_once()
        mock_sskg_manager.query.assert_called_once()
        
        # Check that knowledge nodes were converted to memories
        sskg_memories = [m for m in result if m.metadata.get("source_system") == "sskg"]
        assert len(sskg_memories) == 2
        
        # Verify converted memory properties
        sskg_memory = sskg_memories[0]
        assert sskg_memory.id.startswith("sskg_")
        assert sskg_memory.metadata["source_system"] == "sskg"
        assert "original_node_id" in sskg_memory.metadata
    
    def test_infer_memory_type_from_node(self, unified_interface):
        """Test memory type inference from knowledge nodes."""
        # Test with explicit memory_type in metadata
        node_with_metadata = KnowledgeNode(
            id="node_1",
            node_type=NodeType.FACT,
            content="Test content",
            metadata={"memory_type": "procedural"}
        )
        
        memory_type = unified_interface._infer_memory_type_from_node(node_with_metadata)
        assert memory_type == MemoryType.PROCEDURAL
        
        # Test inference from node type
        fact_node = KnowledgeNode(
            id="node_2",
            node_type=NodeType.FACT,
            content="Test fact"
        )
        
        memory_type = unified_interface._infer_memory_type_from_node(fact_node)
        assert memory_type == MemoryType.SEMANTIC
        
        # Test event node
        event_node = KnowledgeNode(
            id="node_3",
            node_type=NodeType.EVENT,
            content="Test event"
        )
        
        memory_type = unified_interface._infer_memory_type_from_node(event_node)
        assert memory_type == MemoryType.EPISODIC
    
    def test_calculate_recency_from_node(self, unified_interface):
        """Test recency calculation from knowledge nodes."""
        now = datetime.now()
        
        # Test very recent node (1 hour ago)
        recent_node = KnowledgeNode(
            id="node_1",
            node_type=NodeType.FACT,
            content="Recent content",
            updated_at=now - timedelta(hours=1)
        )
        
        recency = unified_interface._calculate_recency_from_node(recent_node)
        assert recency == 1.0
        
        # Test week-old node
        week_old_node = KnowledgeNode(
            id="node_2",
            node_type=NodeType.FACT,
            content="Week old content",
            updated_at=now - timedelta(days=5)
        )
        
        recency = unified_interface._calculate_recency_from_node(week_old_node)
        assert recency == 0.8
        
        # Test very old node
        old_node = KnowledgeNode(
            id="node_3",
            node_type=NodeType.FACT,
            content="Old content",
            updated_at=now - timedelta(days=100)
        )
        
        recency = unified_interface._calculate_recency_from_node(old_node)
        assert recency == 0.2
    
    def test_deduplicate_memories(self, unified_interface):
        """Test memory deduplication."""
        # Create memories with some duplicates
        memories = [
            Memory(
                id="mem_1",
                content="Machine learning is powerful",
                memory_type=MemoryType.SEMANTIC,
                source_id="user_1",
                importance=0.8,
                recency=0.9
            ),
            Memory(
                id="mem_2",
                content="Machine learning is powerful",  # Duplicate
                memory_type=MemoryType.SEMANTIC,
                source_id="user_1",
                importance=0.7,
                recency=0.8
            ),
            Memory(
                id="mem_3",
                content="Python is a programming language",
                memory_type=MemoryType.SEMANTIC,
                source_id="user_1",
                importance=0.6,
                recency=0.7
            )
        ]
        
        # Deduplicate
        unique_memories = unified_interface._deduplicate_memories(memories)
        
        # Verify deduplication
        assert len(unique_memories) == 2
        contents = [m.content for m in unique_memories]
        assert "Machine learning is powerful" in contents
        assert "Python is a programming language" in contents
    
    def test_transform_memory_to_knowledge(
        self, unified_interface, mock_sskg_manager, sample_memories
    ):
        """Test transforming memory to knowledge node."""
        memory = sample_memories[0]
        
        # Mock SSKG manager responses
        mock_sskg_manager.add_node.return_value = "knowledge_node_1"
        mock_sskg_manager.query.return_value = []  # No related nodes
        
        # Transform memory
        node_id = unified_interface.transform_memory_to_knowledge(memory)
        
        # Verify transformation
        assert node_id == "knowledge_node_1"
        
        # Verify SSKG manager was called
        mock_sskg_manager.add_node.assert_called_once()
        
        # Verify mapping was created
        assert memory.id in unified_interface.memory_knowledge_mappings
        mapping = unified_interface.memory_knowledge_mappings[memory.id]
        assert mapping.memory_id == memory.id
        assert mapping.knowledge_node_id == node_id
        assert mapping.mapping_type == "direct"
        
        # Verify statistics
        assert unified_interface.integration_stats["memories_transformed"] == 1
        assert unified_interface.integration_stats["knowledge_nodes_created"] == 1
    
    def test_memory_type_to_node_type(self, unified_interface):
        """Test memory type to node type conversion."""
        # Test all memory types
        assert unified_interface._memory_type_to_node_type(MemoryType.EPISODIC) == NodeType.EVENT
        assert unified_interface._memory_type_to_node_type(MemoryType.SEMANTIC) == NodeType.FACT
        assert unified_interface._memory_type_to_node_type(MemoryType.PROCEDURAL) == NodeType.CONCEPT
        assert unified_interface._memory_type_to_node_type(MemoryType.META) == NodeType.CONCEPT
    
    def test_determine_relation_type(self, unified_interface, sample_memories, sample_knowledge_nodes):
        """Test relation type determination."""
        memory = sample_memories[0]
        knowledge_node = sample_knowledge_nodes[0]
        
        # Test default relation type
        relation_type = unified_interface._determine_relation_type(memory, knowledge_node)
        assert relation_type == RelationType.RELATED_TO
        
        # Test causal relation
        causal_memory = Memory(
            id="mem_causal",
            content="This happened because of machine learning algorithms",
            memory_type=MemoryType.SEMANTIC,
            source_id="user_1",
            importance=0.8,
            recency=0.9
        )
        
        causal_node = KnowledgeNode(
            id="node_causal",
            node_type=NodeType.FACT,
            content="The result was improved performance",
            confidence=0.8
        )
        
        relation_type = unified_interface._determine_relation_type(causal_memory, causal_node)
        assert relation_type == RelationType.CAUSES
    
    def test_create_cross_references(
        self, unified_interface, mock_mem_agent, mock_sskg_manager, sample_memories
    ):
        """Test creating cross-references between memory and knowledge nodes."""
        # Mock responses
        mock_mem_agent.retrieve_memories.return_value = sample_memories
        mock_sskg_manager.query.return_value = [
            KnowledgeNode(
                id="node_1",
                node_type=NodeType.FACT,
                content="Related knowledge",
                confidence=0.8
            )
        ]
        mock_sskg_manager.add_relation.return_value = True
        
        # Create cross-references
        unified_interface.create_cross_references("mem_1", ["node_1"])
        
        # Verify relation was created
        mock_sskg_manager.add_relation.assert_called_once()
        
        # Verify statistics
        assert unified_interface.integration_stats["cross_references_created"] == 1
    
    def test_get_memory_knowledge_mapping(self, unified_interface):
        """Test getting memory-knowledge mapping."""
        # Create a mapping
        mapping = MemoryKnowledgeMapping(
            memory_id="mem_1",
            knowledge_node_id="node_1",
            mapping_type="direct",
            confidence=0.8,
            created_at=datetime.now()
        )
        
        unified_interface.memory_knowledge_mappings["mem_1"] = mapping
        
        # Get mapping
        retrieved_mapping = unified_interface.get_memory_knowledge_mapping("mem_1")
        assert retrieved_mapping == mapping
        
        # Test non-existent mapping
        non_existent = unified_interface.get_memory_knowledge_mapping("mem_999")
        assert non_existent is None
    
    def test_sync_memory_to_knowledge(
        self, unified_interface, mock_mem_agent, mock_sskg_manager, sample_memories
    ):
        """Test synchronizing memory with knowledge representation."""
        memory = sample_memories[0]
        
        # Create existing mapping
        mapping = MemoryKnowledgeMapping(
            memory_id=memory.id,
            knowledge_node_id="node_1",
            mapping_type="direct",
            confidence=0.8,
            created_at=datetime.now()
        )
        unified_interface.memory_knowledge_mappings[memory.id] = mapping
        
        # Mock responses
        mock_mem_agent.retrieve_memories.return_value = sample_memories
        mock_sskg_manager.query.return_value = [
            KnowledgeNode(
                id="node_1",
                node_type=NodeType.FACT,
                content="Old content",
                confidence=0.5,
                metadata={"old_data": True}
            )
        ]
        mock_sskg_manager.update_node.return_value = True
        
        # Sync memory
        success = unified_interface.sync_memory_to_knowledge(memory.id)
        
        # Verify sync
        assert success is True
        mock_sskg_manager.update_node.assert_called_once()
        
        # Verify update call
        call_args = mock_sskg_manager.update_node.call_args
        assert call_args[0][0] == "node_1"  # node_id
        updates = call_args[0][1]
        assert updates["content"] == memory.content
        assert updates["confidence"] == memory.importance
    
    def test_sync_memory_to_knowledge_no_mapping(
        self, unified_interface, mock_mem_agent, mock_sskg_manager, sample_memories
    ):
        """Test syncing memory with no existing mapping."""
        memory = sample_memories[0]
        
        # Mock responses
        mock_mem_agent.retrieve_memories.return_value = sample_memories
        mock_sskg_manager.add_node.return_value = "new_node_1"
        mock_sskg_manager.query.return_value = []
        
        # Sync memory (should create new knowledge node)
        success = unified_interface.sync_memory_to_knowledge(memory.id)
        
        # Verify new node was created
        assert success is True
        mock_sskg_manager.add_node.assert_called_once()
        
        # Verify mapping was created
        assert memory.id in unified_interface.memory_knowledge_mappings
    
    def test_get_integration_stats(self, unified_interface):
        """Test getting integration statistics."""
        # Modify some stats
        unified_interface.integration_stats["memories_transformed"] = 5
        unified_interface.integration_stats["unified_queries"] = 10
        
        # Add a mapping
        mapping = MemoryKnowledgeMapping(
            memory_id="mem_1",
            knowledge_node_id="node_1",
            mapping_type="direct",
            confidence=0.8,
            created_at=datetime.now()
        )
        unified_interface.memory_knowledge_mappings["mem_1"] = mapping
        
        # Get stats
        stats = unified_interface.get_integration_stats()
        
        # Verify stats
        assert stats["memories_transformed"] == 5
        assert stats["unified_queries"] == 10
        assert stats["total_mappings"] == 1
        assert "mapping_details" in stats
        assert "mem_1" in stats["mapping_details"]


if __name__ == "__main__":
    pytest.main([__file__])