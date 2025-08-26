import pytest
from typer.testing import CliRunner
from unittest.mock import patch, AsyncMock

from src.cli.main import app

runner = CliRunner()

@pytest.fixture
def mock_personal_assistant_router():
    """Fixture to mock PersonalAssistantRouter."""
    mock_router = AsyncMock()
    mock_router.process_query.return_value = None
    return mock_router

@patch('src.cli.main.get_personal_assistant_router')
def test_pa_chat_success(mock_get_router, mock_personal_assistant_router):
    """Test `pa chat` command successfully interacts with the mocked router."""
    # Arrange
    mock_get_router.return_value = mock_personal_assistant_router
    query = "Hello assistant!"

    # Act
    result = runner.invoke(app, ["pa", "chat", query])

    # Assert
    assert result.exit_code == 0
    mock_get_router.assert_called_once()
    mock_personal_assistant_router.process_query.assert_awaited_once_with(query)

@patch('src.cli.main.get_personal_assistant_router')
def test_pa_chat_service_error(mock_get_router, mock_personal_assistant_router):
    """Test `pa chat` command handles errors from the router."""
    # Arrange
    mock_get_router.return_value = mock_personal_assistant_router
    query = "Error query"
    mock_personal_assistant_router.process_query.side_effect = Exception("Service internal error")

    # Act
    result = runner.invoke(app, ["pa", "chat", query])

    # Assert
    assert result.exit_code == 1
    assert "Service internal error" in result.stdout
