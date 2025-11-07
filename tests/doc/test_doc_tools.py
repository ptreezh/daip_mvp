import os
from pathlib import Path

import pytest

from daip_live.doc.tools import fetch_arxiv, export_markdown

@pytest.mark.parametrize("query", ["test-1234"])
def test_fetch_arxiv_saves_files(tmp_path: Path, monkeypatch, query: str):
    os.chdir(tmp_path)
    papers = tmp_path/"docs"/"papers"
    def fake_download(q, max_n=1):
        papers.mkdir(parents=True, exist_ok=True)
        (papers/"paper1.pdf").write_bytes(b"%PDF-1.4\n%...mock...")
        (papers/"paper1.metadata.json").write_text("{}", encoding="utf-8")
        return 1
    monkeypatch.setattr("daip_live.doc.tools._download_arxiv", fake_download)
    n = fetch_arxiv(query)
    assert n == 1
    assert (papers/"paper1.pdf").exists()


def test_export_markdown_docx_without_pandoc(tmp_path: Path, monkeypatch):
    os.chdir(tmp_path)
    src = tmp_path/"a.md"
    src.write_text("# Title\n\nHello", encoding="utf-8")
    monkeypatch.setattr("daip_live.doc.tools._has_pandoc", lambda: False)
    out = export_markdown(str(src), to="docx")
    assert out.endswith(".docx")
    assert Path(out).exists()
