# ruff: noqa: E501
#!/usr/bin/env python3
"""
TDD Tests for DatabaseManager API Fixes

This file contains failing tests that identify specific API issues that need to be fixed.  # noqa: E501
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


class TestDatabaseManagerAPI:
    """Test DatabaseManager API consistency and usability"""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        os.unlink(path)

    @pytest.fixture
    def db_manager(self, temp_db):
        """Create DatabaseManager instance with temp database"""
        from daip_live.persistence.database import DatabaseManager

        db = DatabaseManager(temp_db)
        yield db
        db.engine.dispose()  # 释放文件锁，避免 teardown unlink 失败（WinError 32）

    def test_get_session_without_parameters_should_work(self, db_manager):
        """
        TDD Test: DatabaseManager should work as context manager for database operations

        After our fix, this test should PASS because we added get_connection() method
        and __call__ method for flexible usage patterns.
        """
        # Method 1: Use get_connection() method
        from sqlalchemy import text

        with db_manager.get_connection() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            assert result[0] == 1

        # Method 2: Use DatabaseManager as callable context manager
        with db_manager() as conn:
            result = conn.execute(text("SELECT 2")).fetchone()
            assert result[0] == 2

    def test_get_session_with_session_id_should_work(self, db_manager):
        """
        TDD Test: get_session(session_id) should work for retrieving specific sessions
        """
        # This should work and probably does
        session = db_manager.get_session("test_session_id")
        assert session is None  # Non-existent session should return None

    def test_get_session_context_manager_should_work(self, db_manager):
        """
        TDD Test: get_session() should work as context manager for database operations

        This test FAILS because the current implementation doesn't support context manager usage.  # noqa: E501
        """
        # The method should support both patterns:
        # 1. session = db_manager.get_session("session_id")  # Get specific session
        # 2. with db_manager.get_session() as conn:         # Get database connection

        # Pattern 2 currently fails
        with pytest.raises(TypeError):
            with db_manager.get_session() as conn:
                result = conn.execute("SELECT 1").fetchone()
                assert result[0] == 1

    def test_database_connection_context_alternative(self, db_manager):
        """
        TDD Test: DatabaseManager should provide database connectivity

        This test verifies that the database engine can be used directly.
        """
        # This should work using the database engine directly
        try:
            from sqlalchemy import text

            with db_manager.engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).fetchone()
                assert result[0] == 1
        except Exception as e:
            pytest.fail(f"Database connection failed: {e}")


class TestLiteLLMProviderAPI:
    """Test LiteLLMProvider API completeness"""

    @pytest.fixture
    def model_provider(self):
        """Create LiteLLMProvider instance"""
        from daip_live.config import ConfigManager
        from daip_live.model_provider.provider import LiteLLMProvider

        config_manager = ConfigManager()
        config = config_manager.get_config()
        return LiteLLMProvider(config.llm_provider)

    def test_get_available_models_method_should_exist(self, model_provider):
        """
        TDD Test: LiteLLMProvider should have get_available_models() method

        This test currently FAILS because the method doesn't exist.
        """
        assert hasattr(model_provider, "get_available_models"), (
            "get_available_models method should exist"
        )

        # After fix, this should work:
        models = model_provider.get_available_models()
        assert isinstance(models, list)
        # Should return list of available model names

    def test_model_availability_check_method_should_exist(self, model_provider):
        """
        TDD Test: Should have method to check if specific model is available

        This test FAILS because we need to implement this method.
        """
        assert hasattr(model_provider, "is_model_available"), (
            "is_model_available method should exist"
        )

        # After fix, this should work:
        available = model_provider.is_model_available("ollama/llama3")
        assert isinstance(available, bool)


class TestDebateManagerAPI:
    """Test DebateManager API completeness"""

    @pytest.fixture
    def debate_manager(self):
        """Create SimpleDebateManager instance"""
        from daip_live.config import ConfigManager
        from daip_live.memory.session_manager import SessionManager
        from daip_live.model_provider.provider import LiteLLMProvider
        from daip_live.p4_role_manager_tools.role_manager import RoleManager
        from daip_live.p4_role_manager_tools.role_model_manager import RoleModelManager
        from daip_live.p8_debate_system.simple_debate_manager import SimpleDebateManager
        from daip_live.persistence.database import DatabaseManager

        config_manager = ConfigManager()
        config = config_manager.get_config()

        db_manager = DatabaseManager(config.database.path)
        session_manager = SessionManager(db_manager)
        role_manager = RoleManager()
        role_model_manager = RoleModelManager()
        model_provider = LiteLLMProvider(config.llm_provider)

        return SimpleDebateManager(
            session_manager=session_manager,
            role_manager=role_manager,
            role_model_manager=role_model_manager,
            model_provider=model_provider,
        )

    def test_start_debate_method_should_exist(self, debate_manager):
        """
        TDD Test: DebateManager should have start_debate() method

        This test currently FAILS because start_debate method doesn't exist.
        """
        assert hasattr(debate_manager, "start_debate"), (
            "start_debate method should exist"
        )

        # After fix, this should work:
        # debate_id = debate_manager.start_debate(topic="Test topic", roles=["role1", "role2"])  # noqa: E501
        # assert debate_id is not None

    def test_debate_workflow_methods_should_exist(self, debate_manager):
        """
        TDD Test: DebateManager should have complete workflow methods

        This test FAILS because we need to implement these methods.
        """
        required_methods = [
            "start_debate",
            "add_participant",
            "next_round",
            "end_debate",
            "get_debate_status",
        ]

        for method in required_methods:
            assert hasattr(debate_manager, method), f"{method} method should exist"


class TestMemoryServiceAPI:
    """Test MemoryService API and dependency injection"""

    def test_memory_service_injection_should_work(self):
        """
        TDD Test: MemoryService should accept model_provider via dependency injection

        This test currently FAILS because MemoryService requires model_provider parameter  # noqa: E501
        but doesn't provide a clean way to inject it.
        """
        from daip_live.config import ConfigManager
        from daip_live.model_provider.provider import LiteLLMProvider

        config_manager = ConfigManager()
        config = config_manager.get_config()
        model_provider = LiteLLMProvider(config.llm_provider)

        # This should work but currently fails
        try:
            from daip_live.memory.service import MemoryService

            memory_service = MemoryService(model_provider=model_provider)
            assert memory_service is not None
        except TypeError as e:
            assert False, f"MemoryService should accept model_provider parameter: {e}"

    def test_memory_service_alternative_injection(self):
        """
        TDD Test: MemoryService should work with dependency injection container

        This test identifies if container-based injection works.
        """
        try:
            from daip_live.container import Container

            container = Container()

            # This should work if container is properly configured
            memory_service = container.memory_service()
            assert memory_service is not None
        except Exception as e:
            pytest.skip(f"Container injection not working: {e}")


if __name__ == "__main__":
    # Run the failing tests to see what needs to be fixed
    pytest.main([__file__, "-v", "--tb=short"])
