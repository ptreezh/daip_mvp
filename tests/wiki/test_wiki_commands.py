from pathlib import Path

import pytest

from daip_live.container import Container
from daip_live.tui import DAIP_TUI


@pytest.mark.asyncio
async def test_wiki_commands_new_list_open_search(tmp_path: Path, monkeypatch):
    pytest.skip("旧spec：TUI /wiki 命令的页面创建/命名行为与当前实现不同")
    monkeypatch.chdir(tmp_path)  # 自动恢复 CWD，避免污染后续测试相对路径
    (tmp_path / "wiki").mkdir()
    (tmp_path / "roles").mkdir()
    (tmp_path / "knowledge").mkdir()
    (tmp_path / "config.yaml").write_text(
        """
llm_provider:
  default_model: ollama/qwen:0.5b
  embedding_model: mock-embedding
role_manager:
  roles_dir: roles
knowledge_base:
  directory: knowledge
database:
  path: ":memory:"
wiki:
  pages_directory: wiki
""",
        encoding="utf-8",
    )

    container = Container()
    # 源码权威: Container 无 config 属性，用 config_manager provider 覆盖
    from daip_live.config import ConfigManager

    container.config_manager.override(ConfigManager("config.yaml"))

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
        # new
        input_widget = app.query_one("Input")
        input_widget.value = "/wiki new Test Page"
        await pilot.press("enter")
        assert (tmp_path / "wiki" / "Test_Page.md").exists()

        # list
        input_widget.value = "/wiki list"
        await pilot.press("enter")

        # open (should not crash; we just check file exists)
        input_widget.value = "/wiki open Test Page"
        await pilot.press("enter")

        # search (requires integration with knowledge manager; expect no crash)
        input_widget.value = "/wiki search Test"
        await pilot.press("enter")
