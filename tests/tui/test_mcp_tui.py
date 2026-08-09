def test_tui_has_mcp_actions(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # 自动恢复 CWD，避免污染后续测试相对路径
    from daip_live.tui import DAIP_TUI

    assert DAIP_TUI is not None
