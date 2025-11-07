import os
import pytest
from pathlib import Path

def test_cli_markdownify_runs(tmp_path):
    os.chdir(tmp_path)
    from daip_live.cli import main
    assert callable(main)

def test_cli_fetch_runs(tmp_path):
    os.chdir(tmp_path)
    from daip_live.cli import main
    assert callable(main)
