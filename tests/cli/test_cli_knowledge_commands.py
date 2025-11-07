
from typer.testing import CliRunner
from daip_live.cli import app

runner = CliRunner()

def test_knowledge_sync_exits_successfully():
    """
    Tests that the 'daip knowledge sync' command runs and exits with code 0.
    This is the RED test for fixing the non-zero exit code bug.
    """
    result = runner.invoke(app, ["sync"])
    assert result.exit_code == 0, f"Expected exit code 0, but got {result.exit_code}. Stderr: {result.stderr}"

