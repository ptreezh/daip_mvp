"""
DAIP Service Integration Tests for newP6 TUI

This test suite implements TDD approach for service integration functionality.
Tests are written first (RED), then implementation follows (GREEN), then refactoring.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import List, Dict, Any

# Import real implementations
from daip_live.tui_v1.services.base import BaseServiceAdapter
from daip_live.tui_v1.services.container import ServiceContainer
from daip_live.tui_v1.services.session_service import SessionServiceAdapter
from daip_live.tui_v1.services.knowledge_service import KnowledgeServiceAdapter
from daip_live.tui_v1.services.model_service import ModelServiceAdapter


# RED TESTS - These will fail initially, driving implementation

class TestServiceContainer:
    """Test service container functionality"""

    def test_service_container_creation(self):
        """Test service container creation"""
        # This will fail initially - driving need for ServiceContainer
        container = ServiceContainer()

        assert container is not None
        assert hasattr(container, '_services')
        assert hasattr(container, '_initialized')
        assert container._initialized == False

    def test_register_service(self):
        """Test service registration"""
        container = ServiceContainer()
        mock_adapter = Mock(spec=BaseServiceAdapter)
        mock_service = Mock()

        container.register_service("test_service", mock_adapter)

        assert len(container._services) == 1
        assert "test_service" in container._services
        assert container._services["test_service"] == mock_adapter

    def test_register_multiple_services(self):
        """Test registering multiple services"""
        container = ServiceContainer()
        adapter1 = Mock(spec=BaseServiceAdapter)
        adapter2 = Mock(spec=BaseServiceAdapter)
        adapter3 = Mock(spec=BaseServiceAdapter)

        container.register_service("service1", adapter1)
        container.register_service("service2", adapter2)
        container.register_service("service3", adapter3)

        assert len(container._services) == 3
        assert "service1" in container._services
        assert "service2" in container._services
        assert "service3" in container._services

    def test_get_registered_service(self):
        """Test retrieving registered service"""
        container = ServiceContainer()
        mock_adapter = Mock(spec=BaseServiceAdapter)

        container.register_service("test_service", mock_adapter)
        container._initialized = True  # Initialize container
        retrieved = container.get_service("test_service")

        assert retrieved == mock_adapter

    def test_get_nonexistent_service(self):
        """Test retrieving non-existent service returns None"""
        container = ServiceContainer()

        result = container.get_service("nonexistent")
        assert result is None

    def test_service_count(self):
        """Test service count functionality"""
        container = ServiceContainer()

        assert container.count() == 0

        container.register_service("service1", Mock(spec=BaseServiceAdapter))
        assert container.count() == 1

        container.register_service("service2", Mock(spec=BaseServiceAdapter))
        assert container.count() == 2

    def test_clear_services(self):
        """Test clearing all services"""
        container = ServiceContainer()
        container.register_service("service1", Mock(spec=BaseServiceAdapter))
        container.register_service("service2", Mock(spec=BaseServiceAdapter))

        assert container.count() == 2

        container.clear()
        assert container.count() == 0
        assert len(container._services) == 0

    @pytest.mark.asyncio
    async def test_initialize_services(self):
        """Test service initialization"""
        container = ServiceContainer()
        mock_adapter = Mock(spec=BaseServiceAdapter)
        mock_adapter.initialize = AsyncMock()
        mock_event_system = Mock()
        mock_state_manager = Mock()

        container.register_service("test_service", mock_adapter)

        await container.initialize_all(mock_event_system, mock_state_manager)

        assert container._initialized == True
        mock_adapter.set_dependencies.assert_called_once_with(mock_event_system, mock_state_manager)
        mock_adapter.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_services(self):
        """Test service shutdown"""
        container = ServiceContainer()
        mock_adapter = Mock(spec=BaseServiceAdapter)
        mock_adapter.shutdown = AsyncMock()

        container.register_service("test_service", mock_adapter)
        container._initialized = True

        await container.shutdown_all()

        mock_adapter.shutdown.assert_called_once()


class TestBaseServiceAdapter:
    """Test base service adapter functionality"""

    def test_base_adapter_creation(self):
        """Test base adapter creation"""
        mock_service = Mock()
        adapter = BaseServiceAdapter(mock_service)

        assert adapter.service == mock_service
        assert adapter.event_system is None
        assert adapter.state_manager is None

    def test_set_dependencies(self):
        """Test setting dependencies"""
        mock_service = Mock()
        adapter = BaseServiceAdapter(mock_service)
        mock_event_system = Mock()
        mock_state_manager = Mock()

        adapter.set_dependencies(mock_event_system, mock_state_manager)

        assert adapter.event_system == mock_event_system
        assert adapter.state_manager == mock_state_manager

    @pytest.mark.asyncio
    async def test_base_adapter_lifecycle(self):
        """Test base adapter lifecycle"""
        mock_service = Mock()
        adapter = BaseServiceAdapter(mock_service)

        # Should not raise exceptions
        await adapter.initialize()
        await adapter.shutdown()


class TestSessionServiceAdapter:
    """Test session service adapter functionality"""

    @pytest.fixture
    def mock_session_service(self):
        service = Mock()
        service.list_sessions.return_value = [
            {"id": "12345", "name": "Test Session", "status": "active"},
            {"id": "67890", "name": "Another Session", "status": "inactive"}
        ]
        service.get_session.return_value = {"id": "12345", "status": "active"}
        service.create_session.return_value = {"id": "ABCDE", "name": "New Session"}
        service.delete_session.return_value = True
        service.switch_session.return_value = True
        return service

    @pytest.fixture
    def session_adapter(self, mock_session_service):
        return SessionServiceAdapter(mock_session_service)

    @pytest.mark.asyncio
    async def test_list_sessions(self, session_adapter):
        """Test listing sessions"""
        sessions = await session_adapter.list_sessions()

        assert len(sessions) == 2
        assert sessions[0]["id"] == "12345"
        assert sessions[1]["name"] == "Another Session"

    @pytest.mark.asyncio
    async def test_get_session(self, session_adapter):
        """Test getting session details"""
        session = await session_adapter.get_session("12345")

        assert session["id"] == "12345"
        assert session["status"] == "active"

    @pytest.mark.asyncio
    async def test_create_session(self, session_adapter):
        """Test creating session"""
        session = await session_adapter.create_session("Test Session")

        assert session["id"] == "ABCDE"
        assert session["name"] == "New Session"

    @pytest.mark.asyncio
    async def test_delete_session(self, session_adapter):
        """Test deleting session"""
        result = await session_adapter.delete_session("12345")

        assert result == True

    @pytest.mark.asyncio
    async def test_switch_session(self, session_adapter):
        """Test switching session"""
        result = await session_adapter.switch_session("12345")

        assert result == True


class TestKnowledgeServiceAdapter:
    """Test knowledge service adapter functionality"""

    @pytest.fixture
    def mock_knowledge_service(self):
        service = Mock()
        service.search.return_value = [
            {"id": "doc1", "title": "Microservices", "relevance": 0.95},
            {"id": "doc2", "title": "Architecture", "relevance": 0.87}
        ]
        service.add_document.return_value = {"id": "doc3", "status": "added"}
        service.sync.return_value = {"status": "synced", "documents": 1234}
        service.get_stats.return_value = {"documents": 1234, "size": "45MB"}
        return service

    @pytest.fixture
    def knowledge_adapter(self, mock_knowledge_service):
        return KnowledgeServiceAdapter(mock_knowledge_service)

    @pytest.mark.asyncio
    async def test_search_documents(self, knowledge_adapter):
        """Test searching documents"""
        results = await knowledge_adapter.search_documents("microservices")

        assert len(results) == 2
        assert results[0]["title"] == "Microservices"
        assert results[0]["relevance"] == 0.95

    @pytest.mark.asyncio
    async def test_add_document(self, knowledge_adapter):
        """Test adding document"""
        result = await knowledge_adapter.add_document("/path/to/document.pdf")

        assert result["status"] == "added"
        assert result["id"] == "doc3"

    @pytest.mark.asyncio
    async def test_sync_knowledge_base(self, knowledge_adapter):
        """Test syncing knowledge base"""
        result = await knowledge_adapter.sync_knowledge_base()

        assert result["status"] == "synced"
        assert result["documents"] == 1234

    @pytest.mark.asyncio
    async def test_get_knowledge_stats(self, knowledge_adapter):
        """Test getting knowledge statistics"""
        stats = await knowledge_adapter.get_knowledge_stats()

        assert stats["documents"] == 1234
        assert stats["size"] == "45MB"


class TestModelServiceAdapter:
    """Test model service adapter functionality"""

    @pytest.fixture
    def mock_model_service(self):
        service = Mock()
        service.list_models.return_value = [
            {"name": "gpt-4o-mini", "provider": "OpenAI", "status": "available"},
            {"name": "claude-3-sonnet", "provider": "Anthropic", "status": "available"},
            {"name": "llama-3-70b", "provider": "Local", "status": "unavailable"}
        ]
        service.get_status.return_value = {"name": "gpt-4o-mini", "status": "ready", "response_time": 0.8}
        # Don't define switch_model method to trigger fallback logic (Mock auto-creates but returns Mock object)
        service.get_metrics.return_value = {"name": "gpt-4o-mini", "tokens_per_minute": 1000, "avg_response_time": 0.7}
        return service

    @pytest.fixture
    def model_adapter(self, mock_model_service):
        return ModelServiceAdapter(mock_model_service)

    @pytest.mark.asyncio
    async def test_list_models(self, model_adapter):
        """Test listing models"""
        models = await model_adapter.list_models()

        assert len(models) == 3
        assert models[0]["name"] == "gpt-4o-mini"
        assert models[0]["provider"] == "OpenAI"
        assert models[2]["status"] == "unavailable"

    @pytest.mark.asyncio
    async def test_get_model_status(self, model_adapter):
        """Test getting model status"""
        status = await model_adapter.get_model_status("gpt-4o-mini")

        assert status["name"] == "gpt-4o-mini"
        assert status["status"] == "ready"
        assert status["response_time"] == 0.8

    @pytest.mark.asyncio
    async def test_switch_model(self, model_adapter):
        """Test switching model"""
        result = await model_adapter.switch_model("claude-3-sonnet")

        assert result["name"] == "claude-3-sonnet"
        assert result["status"] == "active"

    @pytest.mark.asyncio
    async def test_get_model_metrics(self, model_adapter):
        """Test getting model metrics"""
        metrics = await model_adapter.get_model_metrics("gpt-4o-mini")

        assert metrics["tokens_per_minute"] == 1000
        assert metrics["avg_response_time"] == 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])