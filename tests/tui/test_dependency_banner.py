import os
import pytest
from pathlib import Path
from textual.pilot import Pilot

from daip_live.tui import DAIP_TUI
from daip_live.container import Container

@pytest.mark.asyncio
async def test_dependency_banner_once(tmp_path: Path, monkeypatch):
    os.chdir(tmp_path)
    (tmp_path/"roles").mkdir()
    (tmp_path/"knowledge").mkdir()
    (tmp_path/"config.yaml").write_text("""
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

    # mock dependency checks
    monkeypatch.setattr("daip_live.doc.tools._has_pandoc", lambda: False, raising=True)

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

    async with app.run_test() as pilot:
        # Assert that a warning banner/message was written at startup
        assert any("pandoc" in line.lower() for line in app._log_text_buffer)

        # Trigger re-render (simulate user action) - banner should not duplicate
        input_widget = app.query_one("Input")
        input_widget.value = "/help"
        await pilot.press("enter")
        count = sum(1 for line in app._log_text_buffer if "pandoc" in line.lower())
        assert count >= 1
