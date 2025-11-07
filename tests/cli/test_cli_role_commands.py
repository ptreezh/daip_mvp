
from typer.testing import CliRunner
from daip_live.cli import app

runner = CliRunner()

def test_role_list_output_is_correct():
    """
    Tests that the 'daip role list' command output contains the word 'list'.
    This is the RED test for fixing the incorrect output bug.
    """
    result = runner.invoke(app, ["role", "list"])
    assert result.exit_code == 0
    assert "list" in result.stdout.lower(), f"Expected 'list' in output, but it was not found. Output: {result.stdout}"

