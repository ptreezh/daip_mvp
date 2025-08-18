import pytest
from unittest.mock import AsyncMock, patch
from src.cli.commands import run_assistant_chat_command
from src.application.personal_assistant_service import PersonalAssistantService
from rich.console import Console

@pytest.fixture
def mock_personal_assistant_service():
    """Fixture to mock PersonalAssistantService."""
    with patch('src.cli.commands.PersonalAssistantService', autospec=True) as MockService:
        instance = MockService.return_value
        instance.initialize = AsyncMock()
        instance.create_session = AsyncMock(return_value={"session_id": "test_session_id"})
        instance.get_session = AsyncMock(side_effect=ValueError("Session not found")) # Simulate session not found initially
        instance.process_user_input = AsyncMock(return_value={"response": "Mocked assistant response."})
        yield instance

@pytest.mark.asyncio
async def test_run_assistant_chat_command_success(mock_personal_assistant_service, capsys):
    """
    Test that run_assistant_chat_command successfully interacts with the mocked
    PersonalAssistantService and prints the correct output.
    """
    query = "Hello assistant!"
    
    # Call the command
    await run_assistant_chat_command(query)
    
    # Assert service methods were called
    mock_personal_assistant_service.initialize.assert_called_once()
    mock_personal_assistant_service.get_session.assert_called_once_with("cli_session_cli_user")
    mock_personal_assistant_service.create_session.assert_called_once_with("cli_user")
    mock_personal_assistant_service.process_user_input.assert_called_once_with(
        "test_session_id",
        {
            "content": query,
            "scenario_type": "personal_assistant",
            "user_preferences": {"detail_level": "comprehensive"}
        }
    )
    
    # Capture console output and assert
    captured = capsys.readouterr()
    assert "✅ Assistant Response:" in captured.out
    assert "Mocked assistant response." in captured.out
    # Removed assertion for "Thinking..." as it's ephemeral spinner output

@pytest.mark.asyncio
async def test_run_assistant_chat_command_empty_query(capsys):
    """
    Test that run_assistant_chat_command handles empty queries gracefully.s
    """
    query = ""
    await run_assistant_chat_command(query)
    captured = capsys.readouterr()
    assert "❌ Error: Query cannot be empty." in captured.out

@pytest.mark.asyncio
async def test_run_assistant_chat_command_service_error(mock_personal_assistant_service, capsys):
    """
    Test that run_assistant_chat_command handles errors from PersonalAssistantService.
    """
    query = "Error query"
    mock_personal_assistant_service.process_user_input.side_effect = Exception("Service internal error")
    
    await run_assistant_chat_command(query)
    
    captured = capsys.readouterr()
    # Check for the presence of key phrases, ignoring whitespace and newlines
    assert "❌ An error occurred while interacting with the assistant:" in captured.out
    assert "Service internal" in captured.out # Check for first part
    assert "error" in captured.out # Check for second part