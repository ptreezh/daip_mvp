
import os
import asyncio
import pytest
from pathlib import Path
from textual.pilot import Pilot

from textual.css.query import NoMatches

from daip_live.tui import DAIP_TUI, CommandHelpDialog
from daip_live.container import Container

@pytest.mark.asyncio
async def test_help_command_new_pattern(tmp_path: Path):
    """
    Tests the /help command using the modern, pilot-based testing pattern.
    """
    # 1. Environment Setup
    os.chdir(tmp_path)
    (tmp_path / "roles").mkdir()
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "config.yaml").write_text("""
llm_provider:
  default_model: ollama/qwen:0.5b
  embedding_model: mock-embedding
role_manager:
  roles_dir: roles
knowledge_base:
  directory: knowledge
database:
  path: ":memory:"
""", encoding="utf-8")

    # 2. Dependency Injection
    container = Container()
    container.config.from_yaml('config.yaml')

    app = DAIP_TUI(
        executor=container.agent_executor(),
        session_manager=container.session_manager(),
        role_manager=container.role_manager(),
        knowledge_manager=container.knowledge_manager(),
        debate_manager=container.debate_manager(),
        model_provider=container.model_provider(),
        db_manager=container.db_manager(),
        role_model_manager=container.role_model_manager(),
        enhanced_debate_manager=container.enhanced_debate_manager(),
    )

    # 3. Pilot-based Interaction
    async with app.run_test() as pilot:
        # Directly set the input value and press enter, which is more robust
        from textual.widgets import Input
        input_widget = app.query_one(Input)
        input_widget.value = "/help"
        await pilot.press("enter")

        # Wait for the dialog to appear by polling for its close button
        for _ in range(10):
            try:
                app.query_one("#close")
                break
            except NoMatches:
                await pilot.pause(0.1)
        else:
            pytest.fail("Help dialog with #close button did not appear in time")

        # 4. Assertion
        # The help command now opens a dialog screen. We need to check if that screen is active.
        assert isinstance(app.screen, CommandHelpDialog)

        # Optional: Check content of the help dialog
        help_content = app.screen.query_one("#help-content")
        assert "Available Commands" in help_content.parent.query_one("#help-label").renderable
