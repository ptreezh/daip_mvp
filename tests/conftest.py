import os
import sys
from unittest.mock import Mock

# Add the project root directory to the Python path.
# This allows tests to import modules from the 'src' directory,
# e.g., 'from src.interaction_manager import InteractionManager'.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Setup mock app_state for tests
def pytest_sessionstart(session):
    """Initialize test environment"""
    # Create mock app state
    from src.api.dependencies import app_state
    from src.app_state import AppState
    
    # Create a mock AppState with required services
    mock_app_state = Mock(spec=AppState)
    mock_app_state.virtual_team_service = Mock()
    mock_app_state.memory_service = Mock()
    mock_app_state.role_manager = Mock()
    
    # Setup mock methods
    mock_app_state.virtual_team_service.start_collaboration = Mock(return_value=None)
    mock_app_state.virtual_team_service.adjust_collaboration = Mock(return_value=None)
    mock_app_state.memory_service.store_memory = Mock(return_value=None)
    mock_app_state.role_manager.select_roles_for_topic = Mock(
        return_value=[
            {"id": "technical_expert", "name": "Technical Expert"},
            {"id": "business_analyst", "name": "Business Analyst"},
            {"id": "research_scientist", "name": "Research Scientist"}
        ]
    )
    
    # Set the global app_state
    app_state = mock_app_state
