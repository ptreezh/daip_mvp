import pytest
from unittest.mock import AsyncMock
from pathlib import Path

# This import will fail initially, which is the point of the RED step.
from src.daip_live.scaffolding.scaffolder import Scaffolder


@pytest.mark.asyncio
async def test_scaffolder_generates_content_from_llm():
    """Tests that the scaffolder service correctly calls the model provider."""
    # Arrange
    mock_model_provider = AsyncMock()
    mock_model_provider.generate.return_value = """---
files:
  - path: roles/analyst.yaml
    content: '...'"""

    scaffolder = Scaffolder(model_provider=mock_model_provider)
    description = "A simple project with one analyst."

    # Act
    await scaffolder.generate_from_description(description)

    # Assert
    # Check that the model provider was called with a prompt that includes the description.
    mock_model_provider.generate.assert_called_once()
    call_args, _ = mock_model_provider.generate.call_args
    prompt = call_args[0]
    assert description in prompt
    assert "YAML" in prompt # The meta-prompt should instruct the LLM to generate YAML.


@pytest.mark.asyncio
async def test_scaffolder_validates_and_returns_parsed_yaml():
    """Tests that the scaffolder parses the LLM's YAML output."""
    # Arrange
    mock_model_provider = AsyncMock()
    valid_yaml_output = """---
files:
  - path: roles/analyst.yaml
    content: 'persona: test'"""
    mock_model_provider.generate.return_value = valid_yaml_output

    scaffolder = Scaffolder(model_provider=mock_model_provider)

    # Act
    result = await scaffolder.generate_from_description("test")

    # Assert
    # The result should be a parsed Python dict, not a raw string.
    assert isinstance(result, dict)
    assert "files" in result
    assert result["files"][0]["path"] == "roles/analyst.yaml"


@pytest.mark.asyncio
async def test_scaffolder_retries_on_invalid_yaml():
    """Tests that the scaffolder asks the LLM to self-correct on invalid YAML."""
    # Arrange
    mock_model_provider = AsyncMock()
    invalid_yaml = "files: - path: roles/analyst.yaml\ncontent: 'persona: test'" # Missing indentation
    valid_yaml = """---
files:
  - path: roles/analyst.yaml
    content: 'persona: test'"""
    
    mock_model_provider.generate.side_effect = [invalid_yaml, valid_yaml]

    scaffolder = Scaffolder(model_provider=mock_model_provider, max_retries=1)

    # Act
    result = await scaffolder.generate_from_description("test")

    # Assert
    # It should have called the model provider twice (initial + 1 retry)
    assert mock_model_provider.generate.call_count == 2
    # The final result should be the successfully parsed YAML
    assert isinstance(result, dict)
    assert result["files"][0]["path"] == "roles/analyst.yaml"
    # The second prompt should contain an error message, asking for correction
    second_call_args, _ = mock_model_provider.generate.call_args_list[1]
    assert "Your previous YAML output was invalid" in second_call_args[0]


@pytest.mark.asyncio
async def test_scaffolder_previews_and_awaits_confirmation(mocker):
    """Tests that the scaffolder shows a preview and asks for user confirmation."""
    # Arrange
    # 1. Mock the generate_from_description method to return a fixed result
    mock_parsed_yaml = {
        "files": [
            {"path": "roles/new_role.yaml", "content": "persona: new"},
            {"path": "workflows/new_flow.yaml", "content": "name: new_flow"},
        ]
    }
    mock_generate = mocker.patch(
        "src.daip_live.scaffolding.scaffolder.Scaffolder.generate_from_description",
        return_value=mock_parsed_yaml
    )

    # 2. Mock typer.confirm to simulate user saying "yes"
    mock_confirm = mocker.patch("typer.confirm", return_value=True)
    # 3. Mock rich.print to capture the preview output
    mock_print = mocker.patch("rich.print")

    scaffolder = Scaffolder(model_provider=AsyncMock())

    # Act
    # We call a new, higher-level method that orchestrates the process.
    await scaffolder.execute("test description")

    # Assert
    # It should have generated the plan
    mock_generate.assert_called_once_with("test description")
    # It should have asked for confirmation
    mock_confirm.assert_called_once()
    # The confirmation prompt should contain the file paths
    confirm_prompt = mock_confirm.call_args[0][0]
    assert "roles/new_role.yaml" in confirm_prompt
    assert "workflows/new_flow.yaml" in confirm_prompt


@pytest.mark.asyncio
async def test_scaffolder_writes_files_on_confirmation(mocker):
    """Tests that the scaffolder writes files to the filesystem after confirmation."""
    # Arrange
    # 1. Mock the generate_from_description method
    mock_parsed_yaml = {
        "files": [
            {"path": "roles/new_role.yaml", "content": "persona: new"},
        ]
    }
    mocker.patch(
        "src.daip_live.scaffolding.scaffolder.Scaffolder.generate_from_description",
        return_value=mock_parsed_yaml
    )

    # 2. Mock user confirmation to be True
    mocker.patch("typer.confirm", return_value=True)

    # 3. Mock filesystem operations
    mock_makedirs = mocker.patch("os.makedirs")
    mock_open = mocker.patch("builtins.open", mocker.mock_open())

    scaffolder = Scaffolder(model_provider=AsyncMock())

    # Act
    await scaffolder.execute("test description")

    # Assert
    # It should have created the directory for the role
    mock_makedirs.assert_called_once_with(Path("roles"), exist_ok=True)
    # It should have opened the file for writing
    mock_open.assert_called_once_with(Path("roles/new_role.yaml"), "w", encoding="utf-8")
    # It should have written the correct content to the file
    handle = mock_open()
    handle.write.assert_called_once_with("persona: new")

