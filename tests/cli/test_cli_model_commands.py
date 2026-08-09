from typer.testing import CliRunner

from daip_live.cli import app

runner = CliRunner()


def test_model_list_exits_successfully():
    """
    Tests that the 'daip model list' command runs and exits with a code 0.
    This is the RED test for fixing the non-zero exit code bug.
    """
    result = runner.invoke(app, ["model", "list"])
    assert result.exit_code == 0, (
        f"Expected exit code 0, but got {result.exit_code}. Stderr: {result.stderr}"
    )
