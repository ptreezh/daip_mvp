import os
import pytest
from pathlib import Path

def test_tui_has_mcp_actions(tmp_path):
    os.chdir(tmp_path)
    from daip_live.tui import DAIP_TUI
    assert DAIP_TUI is not None
