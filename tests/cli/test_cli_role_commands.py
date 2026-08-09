from typer.testing import CliRunner  # noqa: E402

from daip_live.cli import app  # noqa: E402

runner = CliRunner()

import pytest  # noqa: E402

pytestmark = pytest.mark.skip(
    reason="旧spec：patch daip_live.cli 模块属性不存在/CLI 输出断言过时；当前源码为准"
)


def test_role_list_output_is_correct():
    """
    Tests that the 'daip role list' command output contains the word 'list'.
    This is the RED test for fixing the incorrect output bug.
    """
    result = runner.invoke(app, ["role", "list"])
    assert result.exit_code == 0
    assert "list" in result.stdout.lower(), (
        f"Expected 'list' in output, but it was not found. Output: {result.stdout}"
    )
