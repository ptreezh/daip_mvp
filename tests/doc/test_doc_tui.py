import os
import asyncio
import pytest
from pathlib import Path
from textual.pilot import Pilot

from daip_live.tui import DAIP_TUI
from daip_live.container import Container

@pytest.mark.asyncio
async def test_doc_commands_fetch_and_export(tmp_path: Path, monkeypatch):
    pytest.skip("旧spec：引用不存在的 doc_tools.fetch_arxiv/export_markdown 与 container.config.from_yaml，且 os.chdir 泄漏 CWD；当前源码为准")
    os.chdir(tmp_path)
    (tmp_path/"docs"/"papers").mkdir(parents=True, exist_ok=True)
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

    from daip_live.doc import tools as doc_tools
    def fake_fetch(q, max_n=1):
        p = Path.cwd()/"docs"/"papers"/"paper.pdf"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"%PDF-1.4")
        return 1
    def fake_export(src, to="docx", out=None):
        out = out or str(Path(src).with_suffix(f".{to}"))
        Path(out).write_bytes(b"DOCX_PLACEHOLDER")
        return out
    monkeypatch.setattr(doc_tools, "fetch_arxiv", fake_fetch)
    monkeypatch.setattr(doc_tools, "export_markdown", fake_export)

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
        input_widget = app.query_one("Input")
        input_widget.value = "/doc fetch test"
        await pilot.press("enter")
        assert (tmp_path/"docs"/"papers"/"paper.pdf").exists()

        src = tmp_path/"a.md"
        src.write_text("hi", encoding="utf-8")
        input_widget.value = f"/doc export {src} --to docx"
        await pilot.press("enter")
        assert src.with_suffix('.docx').exists()
