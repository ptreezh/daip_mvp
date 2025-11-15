import pytest
from unittest.mock import Mock, AsyncMock
from src.daip_live.p7_gui_v1.models.interaction_layer import InteractionLayer, FastAPIInteractionAdapter


class TestInteractionLayer:
    """TDD for Interaction Layer Interface"""
    
    def test_interaction_layer_is_abstract(self):
        """RED: Test that InteractionLayer is an abstract class"""
        from abc import ABC
        assert issubclass(InteractionLayer, ABC)
    
    @pytest.mark.asyncio
    async def test_interaction_layer_methods_exist(self):
        """RED: Test that InteractionLayer defines required methods"""
        # This will fail initially - we need to implement the interface
        adapter = FastAPIInteractionAdapter("http://localhost:8000")
        
        # Check that required methods exist
        assert hasattr(adapter, 'send_message')
        assert hasattr(adapter, 'get_sessions') 
        assert hasattr(adapter, 'create_session')
        assert hasattr(adapter, 'get_roles')
    
    @pytest.mark.asyncio
    async def test_send_message_method_signature(self):
        """RED: Test send_message method signature"""
        adapter = FastAPIInteractionAdapter("http://localhost:8000")
        
        # Method should exist and be callable
        assert callable(getattr(adapter, 'send_message', None))
    
    @pytest.mark.asyncio 
    async def test_get_sessions_method_signature(self):
        """RED: Test get_sessions method signature"""
        adapter = FastAPIInteractionAdapter("http://localhost:8000")
        
        # Method should exist and be callable
        assert callable(getattr(adapter, 'get_sessions', None))
    
    @pytest.mark.asyncio
    async def test_create_session_method_signature(self):
        """RED: Test create_session method signature"""
        adapter = FastAPIInteractionAdapter("http://localhost:8000")
        
        # Method should exist and be callable
        assert callable(getattr(adapter, 'create_session', None))
    
    @pytest.mark.asyncio
    async def test_get_roles_method_signature(self):
        """RED: Test get_roles method signature"""
        adapter = FastAPIInteractionAdapter("http://localhost:8000")
        
        # Method should exist and be callable
        assert callable(getattr(adapter, 'get_roles', None))