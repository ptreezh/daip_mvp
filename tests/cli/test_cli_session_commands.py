from typer.testing import CliRunner
from daip_live.cli import app

runner = CliRunner()

def test_session_clear_exits_successfully():
    """
    Tests that the 'daip session clear' command runs and exits with code 0.
    This is the RED test for fixing the non-zero exit code bug.
    We pipe 'y' to the command to confirm the action.
    """
    result = runner.invoke(app, ["session", "clear"], input='y\n')
    assert result.exit_code == 0, f"Expected exit code 0, but got {result.exit_code}. Stderr: {result.stderr}"

def test_session_list_output_is_correct():
    """
    Tests that the 'daip session list' command output contains the word 'list'.
    This is the RED test for fixing the incorrect output bug.
    """
    result = runner.invoke(app, ["session", "list"])
    assert result.exit_code == 0
    assert "list" in result.stdout.lower(), f"Expected 'list' in output, but it was not found. Output: {result.stdout}"

