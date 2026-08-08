import os
import pytest
from pathlib import Path

from daip_live.p4_role_manager_tools.tool_manager import ToolManager

@pytest.fixture
def tm():
    return ToolManager()

def test_markdown_to_md_url_validation(tm, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # 自动恢复 CWD，避免污染后续测试的相对路径
    from daip_live.basic_tools.core import markdown_to_md
    with pytest.raises(Exception):
        markdown_to_md("ftp://example.com")

def test_markdown_to_md_domain_permission(tm, monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)  # 自动恢复 CWD，避免污染后续测试的相对路径
    from daip_live.basic_tools.core import markdown_to_md
    os.environ["MCP_ALLOWED_DOMAINS"] = "arxiv.org,doi.org"
    with pytest.raises(Exception):
        markdown_to_md("https://notallowed.com/page")

def test_fetch_paper_accepts_arxiv_id(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # 自动恢复 CWD，避免污染后续测试的相对路径
    from daip_live.basic_tools.core import fetch_paper
    with pytest.raises(Exception):
        fetch_paper("")

def test_fetch_paper_saves_pdf(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # 自动恢复 CWD，避免污染后续测试的相对路径
    from daip_live.basic_tools.core import fetch_paper
    def fake_call(identifier, save_dir):
        d = Path("docs")/"papers"
        d.mkdir(parents=True, exist_ok=True)
        p = d/"test.pdf"
        p.write_bytes(b"%PDF-1.4\n")
        return str(p)
    monkeypatch.setattr("daip_live.basic_tools.core._scihub_fetch", fake_call)
    out = fetch_paper("2305.06530")
    assert out.endswith(".pdf")
    assert Path(out).exists()
