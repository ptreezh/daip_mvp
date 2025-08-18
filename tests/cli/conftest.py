import pytest
from unittest.mock import patch, MagicMock
import re # ADD THIS IMPORT

# We need to import the app object directly for testing
from src.cli.main import app # Keep app

# ANSI escape code remover
ansi_escape = re.compile(r'\x1B(?:[@-Z\-_]|[[0-?]*[ -/]*[@-~])')

@pytest.fixture
def mock_console():
    """Fixture to mock the rich.console.Console object."""
    with patch('src.cli.main.console') as mock_rich_console:
        yield mock_rich_console

@pytest.fixture
def mock_healthy_system(mock_console): # Pass mock_console to this fixture
    """Fixture to mock a healthy system state."""
    with patch('src.config.settings') as mock_settings, \
         patch('src.cli.commands.MISSING_DEPENDENCIES', new=[]), \
         patch('src.cli.commands.check_system_health') as mock_check_health, \
         patch('src.main.app') as mock_fastapi_app:
        
        mock_settings.log_level = 'INFO'
        mock_settings.llm = MagicMock()
        mock_settings.llm.provider = 'ollama'
        mock_settings.llm.ollama.generation_model = 'llama2'
        mock_settings.vector_store = MagicMock()
        mock_settings.vector_store.chroma_db_path = '/path/to/chroma'

        mock_check_health.return_value = {
            "llm_connection": {"status": "✅ Connected", "details": "Ollama service is running"},
            "vector_store_access": {"status": "✅ Accessible", "details": "ChromaDB path is valid"},
            "dependencies_check": {"status": "✅ All installed", "details": "Required packages found"}
        }

        mock_fastapi_app.routes = [MagicMock(path='/api/v1/test')] # Simulate at least one route

        yield

@pytest.fixture
def mock_unhealthy_llm_system(mock_console): # Pass mock_console to this fixture
    """Fixture to mock an unhealthy system state due to LLM configuration."""
    with patch('src.config.settings') as mock_settings, \
         patch('src.cli.commands.MISSING_DEPENDENCIES', new=[]), \
         patch('src.cli.commands.check_system_health') as mock_check_health, \
         patch('src.main.app') as mock_fastapi_app:
        
        mock_settings.log_level = 'INFO'
        mock_settings.llm = MagicMock()
        mock_settings.llm.provider = None # No provider configured
        mock_settings.vector_store = MagicMock()
        mock_settings.vector_store.chroma_db_path = '/path/to/chroma'

        mock_check_health.return_value = {
            "llm_connection": {"status": "❌ Disconnected", "details": "LLM service not reachable"},
            "vector_store_access": {"status": "✅ Accessible", "details": "ChromaDB path is valid"},
            "dependencies_check": {"status": "✅ All installed", "details": "Required packages found"}
        }

        mock_fastapi_app.routes = [MagicMock(path='/api/v1/test')] # Simulate at least one route

        yield