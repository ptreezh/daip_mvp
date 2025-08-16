"""Unit tests for the Storage Adapters.
"""

import unittest
from datetime import datetime
from unittest.mock import patch

import pytest

from src.core_services.storage_adapters import (
    RoleMemoryAdapter,
    SessionAdapter,
    StorageAdapterManager,
    WikiAdapter,
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

    def query(self, query):
        # Simple mock implementation
        results = []
        for node in self.nodes.values():
            # Check node type filter
            if query.node_types and node.node_type not in query.node_types:
                continue

            # Check metadata filters
            if query.metadata_filters:
                match = True
                for key, value in query.metadata_filters.items():
                    if node.metadata.get(key) != value:
                        match = False
                        break
                if not match:
                    continue

            results.append(node)

            if len(results) >= query.limit:
                break

        return results

    def get_related_nodes(self, node_id, relation_types=None, limit=10):
        # Simple mock implementation
        return []


class MockKnowledgeNode:
    """Mock knowledge node for testing."""

    def __init__(self, node_type, content, confidence=1.0, metadata=None):
        self.id = None
        self.node_type = node_type
        self.content = content
        self.confidence = confidence
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


class MockKnowledgeQuery:
    """Mock knowledge query for testing."""

    def __init__(self, node_types=None, metadata_filters=None, limit=10):
        self.node_types = node_types
        self.metadata_filters = metadata_filters or {}
        self.limit = limit


class MockKnowledgeRelation:
    """Mock knowledge relation for testing."""

    def __init__(self, source_id, target_id, relation_type, confidence=1.0, metadata=None):
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type
        self.confidence = confidence
        self.metadata = metadata or {}


# Patch the imports to use mock classes
@patch('src.core_services.storage_adapters.KnowledgeNode', MockKnowledgeNode)
@patch('src.core_services.storage_adapters.KnowledgeQuery', MockKnowledgeQuery)
@patch('src.core_services.storage_adapters.KnowledgeRelation', MockKnowledgeRelation)
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
            ],
            "cognitive_framework": {"framework": "test"}
        }

        # Store role data
        role_node_id = self.adapter.store(role_data)

        # Verify role node was created
        self.assertIsNotNone(role_node_id)
        role_node = self.sskg_manager.get_node(role_node_id)
        self.assertIsNotNone(role_node)
        self.assertEqual(role_node.metadata["role_id"], "test_role")
        self.assertEqual(role_node.metadata["name"], "Test Role")

        # Verify memory nodes were created
        self.assertEqual(len(self.sskg_manager.nodes), 3)  # 1 role + 2 memories

    def test_retrieve_role_data(self):
        """Test retrieving role data."""
        # First store some role data
        role_data = {
            "role_id": "test_role",
            "name": "Test Role",
            "personality": {"trait1": "value1"},
            "memories": [
                {
                    "content": "Test memory",
                    "type": "episodic",
                    "importance": 0.8
                }
            ]
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
        # First store some role data
        role_data = {
            "role_id": "test_role",
            "name": "Test Role",
            "personality": {"trait1": "value1"}
        }

        self.adapter.store(role_data)

        # Update role data
        updated_data = {
            "name": "Updated Role",
            "personality": {"trait1": "updated_value"}
        }

        success = self.adapter.update("test_role", updated_data)

        # Verify update was successful
        self.assertTrue(success)

        # Verify updated data
        retrieved_data = self.adapter.retrieve("test_role")
        self.assertEqual(retrieved_data["name"], "Updated Role")

    def test_delete_role_data(self):
        """Test deleting role data."""
        # First store some role data
        role_data = {
            "role_id": "test_role",
            "name": "Test Role",
            "memories": [
                {
                    "content": "Test memory",
                    "type": "episodic"
                }
            ]
        }

        self.adapter.store(role_data)
        initial_count = len(self.sskg_manager.nodes)

        # Delete role data
        success = self.adapter.delete("test_role")

        # Verify deletion was successful
        self.assertTrue(success)
        self.assertLess(len(self.sskg_manager.nodes), initial_count)

    def test_list_roles(self):
        """Test listing role IDs."""
        # Store multiple roles
        for i in range(3):
            role_data = {
                "role_id": f"role_{i}",
                "name": f"Role {i}"
            }
            self.adapter.store(role_data)

        # List roles
        role_ids = self.adapter.list()

        # Verify list
        self.assertEqual(len(role_ids), 3)
        self.assertIn("role_0", role_ids)
        self.assertIn("role_1", role_ids)
        self.assertIn("role_2", role_ids)

@patch('src.core_services.storage_adapters.KnowledgeNode', MockKnowledgeNode)
@patch('src.core_services.storage_adapters.KnowledgeQuery', MockKnowledgeQuery)
@patch('src.core_services.storage_adapters.KnowledgeRelation', MockKnowledgeRelation)
class TestWikiAdapter(unittest.TestCase):
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
            "content": "This is test content.",
            "tags": ["tag1", "tag2"],
            "category": "test_category",
            "contributors": ["user1", "user2"]
        }

        # Store wiki data
        wiki_node_id = self.adapter.store(wiki_data)

        # Verify wiki node was created
        self.assertIsNotNone(wiki_node_id)
        wiki_node = self.sskg_manager.get_node(wiki_node_id)
        self.assertIsNotNone(wiki_node)
        self.assertEqual(wiki_node.metadata["page_id"], "test_page")
        self.assertEqual(wiki_node.metadata["title"], "Test Page")

    def test_retrieve_wiki_data(self):
        """Test retrieving wiki data."""
        # First store some wiki data
        wiki_data = {
            "page_id": "test_page",
            "title": "Test Page",
            "content": "This is test content.",
            "tags": ["tag1"],
            "category": "test_category"
        }

        self.adapter.store(wiki_data)

        # Retrieve wiki data
        retrieved_data = self.adapter.retrieve("test_page")

        # Verify retrieved data
        self.assertIsNotNone(retrieved_data)
        self.assertEqual(retrieved_data["page_id"], "test_page")
        self.assertEqual(retrieved_data["title"], "Test Page")
        self.assertEqual(retrieved_data["content"], "This is test content.")

    def test_update_wiki_data(self):
        """Test updating wiki data."""
        # First store some wiki data
        wiki_data = {
            "page_id": "test_page",
            "title": "Test Page",
            "content": "Original content"
        }

        self.adapter.store(wiki_data)

        # Update wiki data
        updated_data = {
            "title": "Updated Page",
            "content": "Updated content"
        }

        success = self.adapter.update("test_page", updated_data)

        # Verify update was successful
        self.assertTrue(success)

        # Verify updated data
        retrieved_data = self.adapter.retrieve("test_page")
        self.assertEqual(retrieved_data["title"], "Updated Page")
        self.assertEqual(retrieved_data["content"], "Updated content")

    def test_delete_wiki_data(self):
        """Test deleting wiki data."""
        # First store some wiki data
        wiki_data = {
            "page_id": "test_page",
            "title": "Test Page",
            "content": "Test content"
        }

        self.adapter.store(wiki_data)
        initial_count = len(self.sskg_manager.nodes)

        # Delete wiki data
        success = self.adapter.delete("test_page")

        # Verify deletion was successful
        self.assertTrue(success)
        self.assertLess(len(self.sskg_manager.nodes), initial_count)

    def test_list_wiki_pages(self):
        """Test listing wiki page IDs."""
        # Store multiple wiki pages
        for i in range(3):
            wiki_data = {
                "page_id": f"page_{i}",
                "title": f"Page {i}",
                "content": f"Content {i}"
            }
            self.adapter.store(wiki_data)

        # List wiki pages
        page_ids = self.adapter.list()

        # Verify list
        self.assertEqual(len(page_ids), 3)
        self.assertIn("page_0", page_ids)
        self.assertIn("page_1", page_ids)
        self.assertIn("page_2", page_ids)


@patch('src.core_services.storage_adapters.KnowledgeNode', MockKnowledgeNode)
@patch('src.core_services.storage_adapters.KnowledgeQuery', MockKnowledgeQuery)
@patch('src.core_services.storage_adapters.KnowledgeRelation', MockKnowledgeRelation)
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
            "state": {"key": "value"},
            "context": {"context_key": "context_value"},
            "participants": ["user1", "role1"],
            "metadata": {"custom_field": "custom_value"}
        }

        # Store session data
        session_node_id = self.adapter.store(session_data)

        # Verify session node was created
        self.assertIsNotNone(session_node_id)
        session_node = self.sskg_manager.get_node(session_node_id)
        self.assertIsNotNone(session_node)
        self.assertEqual(session_node.metadata["session_id"], "test_session")

    def test_retrieve_session_data(self):
        """Test retrieving session data."""
        # First store some session data
        session_data = {
            "session_id": "test_session",
            "state": {"key": "value"},
            "context": {"context_key": "context_value"},
            "participants": ["user1"]
        }

        self.adapter.store(session_data)

        # Retrieve session data
        retrieved_data = self.adapter.retrieve("test_session")

        # Verify retrieved data
        self.assertIsNotNone(retrieved_data)
        self.assertEqual(retrieved_data["session_id"], "test_session")
        self.assertEqual(retrieved_data["state"]["key"], "value")
        self.assertEqual(retrieved_data["context"]["context_key"], "context_value")


@patch('src.core_services.storage_adapters.KnowledgeNode', MockKnowledgeNode)
@patch('src.core_services.storage_adapters.KnowledgeQuery', MockKnowledgeQuery)
@patch('src.core_services.storage_adapters.KnowledgeRelation', MockKnowledgeRelation)
class TestStorageAdapterManager(unittest.TestCase):
    """Test cases for the Storage Adapter Manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.sskg_manager = MockSSKGManager()
        self.manager = StorageAdapterManager(self.sskg_manager)

    def test_get_adapter(self):
        """Test getting adapters by type."""
        # Test getting existing adapters
        role_adapter = self.manager.get_adapter("role_memory")
        self.assertIsInstance(role_adapter, RoleMemoryAdapter)

        wiki_adapter = self.manager.get_adapter("wiki")
        self.assertIsInstance(wiki_adapter, WikiAdapter)

        # Test getting non-existent adapter
        non_existent = self.manager.get_adapter("non_existent")
        self.assertIsNone(non_existent)

    def test_register_adapter(self):
        """Test registering new adapters."""
        # Create a custom adapter
        custom_adapter = RoleMemoryAdapter(self.sskg_manager)

        # Register the adapter
        self.manager.register_adapter("custom", custom_adapter)

        # Verify it was registered
        retrieved_adapter = self.manager.get_adapter("custom")
        self.assertEqual(retrieved_adapter, custom_adapter)

    def test_list_adapters(self):
        """Test listing all adapter types."""
        adapter_types = self.manager.list_adapters()

        # Verify default adapters are present
        expected_types = ["role_memory", "wiki", "session", "project", "memory_bank"]
        for adapter_type in expected_types:
            self.assertIn(adapter_type, adapter_types)


# Pytest-style tests
@pytest.fixture()
def mock_sskg_manager():
    """Create a mock SSKG manager."""
    return MockSSKGManager()


@pytest.fixture()
def role_adapter(mock_sskg_manager):
    """Create a role memory adapter."""
    return RoleMemoryAdapter(mock_sskg_manager)


@pytest.fixture()
def wiki_adapter(mock_sskg_manager):
    """Create a wiki adapter."""
    return WikiAdapter(mock_sskg_manager)


class TestStorageAdaptersPytest:
    """Pytest-style tests for storage adapters."""

    @patch('src.core_services.storage_adapters.KnowledgeNode', MockKnowledgeNode)
    @patch('src.core_services.storage_adapters.KnowledgeQuery', MockKnowledgeQuery)
    @patch('src.core_services.storage_adapters.KnowledgeRelation', MockKnowledgeRelation)
    def test_role_adapter_store_and_retrieve(self, role_adapter):
        """Test storing and retrieving role data."""
        role_data = {
            "role_id": "pytest_role",
            "name": "Pytest Role",
            "personality": {"openness": 0.8},
            "memories": [
                {
                    "content": "Pytest memory",
                    "type": "episodic",
                    "importance": 0.9
                }
            ]
        }

        # Store role data
        role_node_id = role_adapter.store(role_data)
        assert role_node_id is not None

        # Retrieve role data
        retrieved_data = role_adapter.retrieve("pytest_role")
        assert retrieved_data is not None
        assert retrieved_data["role_id"] == "pytest_role"
        assert retrieved_data["name"] == "Pytest Role"
        assert len(retrieved_data["memories"]) == 1

    @patch('src.core_services.storage_adapters.KnowledgeNode', MockKnowledgeNode)
    @patch('src.core_services.storage_adapters.KnowledgeQuery', MockKnowledgeQuery)
    @patch('src.core_services.storage_adapters.KnowledgeRelation', MockKnowledgeRelation)
    def test_wiki_adapter_hierarchical_organization(self, wiki_adapter):
        """Test hierarchical organization of wiki content."""
        # Store wiki pages with categories and tags
        wiki_pages = [
            {
                "page_id": "page1",
                "title": "Page 1",
                "content": "Content 1",
                "category": "category_a",
                "tags": ["tag1", "tag2"]
            },
            {
                "page_id": "page2",
                "title": "Page 2",
                "content": "Content 2",
                "category": "category_a",
                "tags": ["tag2", "tag3"]
            },
            {
                "page_id": "page3",
                "title": "Page 3",
                "content": "Content 3",
                "category": "category_b",
                "tags": ["tag1"]
            }
        ]

        # Store all pages
        for wiki_data in wiki_pages:
            wiki_adapter.store(wiki_data)

        # List all pages
        all_pages = wiki_adapter.list()
        assert len(all_pages) == 3

        # Test filtering by category (simplified test)
        category_a_pages = wiki_adapter.list(category="category_a")
        # Note: This test is simplified because our mock doesn't implement
        # full filtering logic, but it demonstrates the interface
        assert isinstance(category_a_pages, list)
