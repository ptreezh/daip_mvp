"""
Unit tests for the SSKG Storage Adapters.
"""

import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytest

from src.core_services.sskg_storage_adapters import (
    RoleMemoryAdapter,
    WikiAdapter,
    SessionAdapter,
    StorageAdapterManager
)


class MockSSKGManager:
    """Mock SSKG manager for testing."""
    
    def __init__(self):
        self.nodes = {}
        self.relations = []
        self.node_counter = 0
    
    def add_node(self, node):
        self.node_counter += 1
        node_id = f"node_{self.node_counter}"
        node.id = node_id
        self.nodes[node_id] = node
        return node_id
    
    def add_relation(self, relation):
        self.relations.append(relation)
        return True
    
    def get_node(self, node_id):
        return self.nodes.get(node_id)
    
    def update_node(self, node_id, updates):
        if node_id in self.nodes:
            node = self.nodes[node_id]
            for key, value in updates.items():
                setattr(node, key, value)
            return True
        return False
    
    def delete_node(self, node_id):
        if node_id in self.nodes:
            del self.nodes[node_id]
            return True
        return False
    
    def query(self, query_params):
        # Simple mock query implementation
        results = []
        node_types = query_params.get("node_types", [])
        metadata_filters = query_params.get("metadata_filters", {})
        limit = query_params.get("limit", 10)
        
        for node in self.nodes.values():
            # Check node type
            if node_types and node.node_type not in node_types:
                continue
            
            # Check metadata filters
            match = True
            for key, value in metadata_filters.items():
                if node.metadata.get(key) != value:
                    match = False
                    break
            
            if match:
                results.append(node)
                if len(results) >= limit:
                    break
        
        return results


class TestRoleMemoryAdapter(unittest.TestCase):
    """Test cases for the Role Memory Adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sskg_manager = MockSSKGManager()
        self.adapter = RoleMemoryAdapter(self.sskg_manager)
    
    def test_store_role_data(self):
        """Test storing role data."""
        role_data = {
            "role_id": "test_role",
            "name": "Test Role",
            "personality": {"trait1": "value1"},
            "cognitive_framework": {"framework": "test"},
            "memories": [
                {
                    "content": "Test memory 1",
                    "type": "episodic",
                    "importance": 0.8
                },
                {
                    "content": "Test memory 2",
                    "type": "semantic",
                    "importance": 0.6
                }
            ]
        }
        
        role_node_id = self.adapter.store(role_data)
        
        # Verify role node was created
        self.assertIsNotNone(role_node_id)
        self.assertIn(role_node_id, self.sskg_manager.nodes)
        
        # Verify role node content
        role_node = self.sskg_manager.nodes[role_node_id]
        self.assertEqual(role_node.content, "Role: Test Role")
        self.assertEqual(role_node.metadata["role_id"], "test_role")
        self.assertEqual(role_node.metadata["name"], "Test Role")
        
        # Verify memory nodes were created
        memory_nodes = [node for node in self.sskg_manager.nodes.values() 
                       if hasattr(node, 'node_type') and node.node_type.value == "memory"]
        self.assertEqual(len(memory_nodes), 2)
    
    def test_retrieve_role_data(self):
        """Test retrieving role data."""
        # First store role data
        role_data = {
            "role_id": "test_role",
            "name": "Test Role",
            "personality": {"trait1": "value1"},
            "memories": [{"content": "Test memory", "type": "episodic"}]
        }
        self.adapter.store(role_data)
        
        # Retrieve role data
        retrieved_data = self.adapter.retrieve("test_role")
        
        # Verify retrieved data
        self.assertIsNotNone(retrieved_data)
        self.assertEqual(retrieved_data["role_id"], "test_role")
        self.assertEqual(retrieved_data["name"], "Test Role")
        self.assertEqual(len(retrieved_data["memories"]), 1)
    
    def test_update_role_data(self):
        """Test updating role data."""
        # First store role data
        role_data = {"role_id": "test_role", "name": "Original Name"}
        self.adapter.store(role_data)
        
        # Update role data
        updated_data = {"name": "Updated Name", "personality": {"new_trait": "new_value"}}
        result = self.adapter.update("test_role", updated_data)
        
        # Verify update was successful
        self.assertTrue(result)
        
        # Verify updated data
        retrieved_data = self.adapter.retrieve("test_role")
        self.assertEqual(retrieved_data["name"], "Updated Name")
    
    def test_delete_role_data(self):
        """Test deleting role data."""
        # First store role data
        role_data = {"role_id": "test_role", "name": "Test Role"}
        self.adapter.store(role_data)
        
        # Delete role data
        result = self.adapter.delete("test_role")
        
        # Verify deletion was successful
        self.assertTrue(result)
        
        # Verify role data is gone
        retrieved_data = self.adapter.retrieve("test_role")
        self.assertIsNone(retrieved_data)

class
 TestWikiAdapter(unittest.TestCase):
    """Test cases for the Wiki Adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sskg_manager = MockSSKGManager()
        self.adapter = WikiAdapter(self.sskg_manager)
    
    def test_store_wiki_data(self):
        """Test storing wiki data."""
        wiki_data = {
            "page_id": "test_page",
            "title": "Test Page",
            "content": "This is test content",
            "tags": ["tag1", "tag2"],
            "category": "test_category",
            "author": "test_author"
        }
        
        wiki_node_id = self.adapter.store(wiki_data)
        
        # Verify wiki node was created
        self.assertIsNotNone(wiki_node_id)
        self.assertIn(wiki_node_id, self.sskg_manager.nodes)
        
        # Verify wiki node content
        wiki_node = self.sskg_manager.nodes[wiki_node_id]
        self.assertEqual(wiki_node.content, "This is test content")
        self.assertEqual(wiki_node.metadata["page_id"], "test_page")
        self.assertEqual(wiki_node.metadata["title"], "Test Page")
    
    def test_retrieve_wiki_data(self):
        """Test retrieving wiki data."""
        # First store wiki data
        wiki_data = {
            "page_id": "test_page",
            "title": "Test Page",
            "content": "Test content"
        }
        self.adapter.store(wiki_data)
        
        # Retrieve wiki data
        retrieved_data = self.adapter.retrieve("test_page")
        
        # Verify retrieved data
        self.assertIsNotNone(retrieved_data)
        self.assertEqual(retrieved_data["page_id"], "test_page")
        self.assertEqual(retrieved_data["title"], "Test Page")
        self.assertEqual(retrieved_data["content"], "Test content")
    
    def test_update_wiki_data(self):
        """Test updating wiki data."""
        # First store wiki data
        wiki_data = {"page_id": "test_page", "title": "Original Title", "content": "Original content"}
        self.adapter.store(wiki_data)
        
        # Update wiki data
        updated_data = {"title": "Updated Title", "content": "Updated content"}
        result = self.adapter.update("test_page", updated_data)
        
        # Verify update was successful
        self.assertTrue(result)
        
        # Verify updated data
        retrieved_data = self.adapter.retrieve("test_page")
        self.assertEqual(retrieved_data["title"], "Updated Title")
        self.assertEqual(retrieved_data["content"], "Updated content")
    
    def test_delete_wiki_data(self):
        """Test deleting wiki data."""
        # First store wiki data
        wiki_data = {"page_id": "test_page", "title": "Test Page"}
        self.adapter.store(wiki_data)
        
        # Delete wiki data
        result = self.adapter.delete("test_page")
        
        # Verify deletion was successful
        self.assertTrue(result)
        
        # Verify wiki data is gone
        retrieved_data = self.adapter.retrieve("test_page")
        self.assertIsNone(retrieved_data)


class TestSessionAdapter(unittest.TestCase):
    """Test cases for the Session Adapter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sskg_manager = MockSSKGManager()
        self.adapter = SessionAdapter(self.sskg_manager)
    
    def test_store_session_data(self):
        """Test storing session data."""
        session_data = {
            "session_id": "test_session",
            "user_id": "test_user",
            "state": {"key": "value"},
            "conversation_history": [{"message": "Hello"}],
            "context": {"context_key": "context_value"}
        }
        
        session_node_id = self.adapter.store(session_data)
        
        # Verify session node was created
        self.assertIsNotNone(session_node_id)
        self.assertIn(session_node_id, self.sskg_manager.nodes)
        
        # Verify session node metadata
        session_node = self.sskg_manager.nodes[session_node_id]
        self.assertEqual(session_node.metadata["session_id"], "test_session")
        self.assertEqual(session_node.metadata["user_id"], "test_user")
    
    def test_retrieve_session_data(self):
        """Test retrieving session data."""
        # First store session data
        session_data = {
            "session_id": "test_session",
            "user_id": "test_user",
            "state": {"key": "value"}
        }
        self.adapter.store(session_data)
        
        # Retrieve session data
        retrieved_data = self.adapter.retrieve("test_session")
        
        # Verify retrieved data
        self.assertIsNotNone(retrieved_data)
        self.assertEqual(retrieved_data["session_id"], "test_session")
        self.assertEqual(retrieved_data["user_id"], "test_user")
        self.assertEqual(retrieved_data["state"]["key"], "value")


class TestStorageAdapterManager(unittest.TestCase):
    """Test cases for the Storage Adapter Manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sskg_manager = MockSSKGManager()
        self.manager = StorageAdapterManager(self.sskg_manager)
    
    def test_get_adapter(self):
        """Test getting adapters."""
        # Test getting existing adapter
        role_adapter = self.manager.get_adapter("role_memory")
        self.assertIsNotNone(role_adapter)
        self.assertIsInstance(role_adapter, RoleMemoryAdapter)
        
        # Test getting non-existent adapter
        unknown_adapter = self.manager.get_adapter("unknown")
        self.assertIsNone(unknown_adapter)
    
    def test_list_adapters(self):
        """Test listing adapters."""
        adapters = self.manager.list_adapters()
        self.assertIn("role_memory", adapters)
        self.assertIn("wiki", adapters)
        self.assertIn("session", adapters)
    
    def test_store_and_retrieve_data(self):
        """Test storing and retrieving data through the manager."""
        # Store role data
        role_data = {"role_id": "test_role", "name": "Test Role"}
        role_id = self.manager.store_data("role_memory", role_data)
        self.assertIsNotNone(role_id)
        
        # Retrieve role data
        retrieved_data = self.manager.retrieve_data("role_memory", "test_role")
        self.assertIsNotNone(retrieved_data)
        self.assertEqual(retrieved_data["role_id"], "test_role")


if __name__ == "__main__":
    unittest.main()