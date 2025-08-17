# tests/test_cli_framework.py

import io
import sys
from unittest.mock import patch

import pytest

# This import will fail initially, which is expected for the RED step.
from interactive_cli import main

def test_main_menu_is_displayed_on_start():
    """
    Tests if the main menu is correctly displayed when the application starts.
    Corresponds to ATC-FMW-01.
    """
    # Redirect stdout to capture the output
    captured_output = io.StringIO()
    sys.stdout = captured_output

    # Use patch to simulate user input '0' to exit immediately after starting.
    with patch('builtins.input', side_effect=['0']), \
         patch('sys.exit') as mock_exit:
        mock_exit.side_effect = SystemExit

        with pytest.raises(SystemExit):
            main()

    # Restore stdout
    sys.stdout = sys.__stdout__

    output = captured_output.getvalue()

    # Assertions for ATC-FMW-01
    assert "DAIP-LIVE 交互式指挥中心" in output
    assert "[1] 个人助手 (Personal Assistant)" in output
    assert "[2] 辩论大厅 (Debate Hall)" in output
    assert "[3] 实时聊天室 (Chat Room)" in output
    assert "[4] 知识维基 (Knowledge Wiki)" in output
    assert "[5] 角色管理 (Role Management)" in output
    assert "[6] 工作流与制度原语 (Workflows & Primitives)" in output
    assert "[0] 退出 (Exit)" in output


def test_app_exits_when_user_inputs_zero():
    """
    Tests if the application exits gracefully when the user inputs '0'.
    Corresponds to ATC-FMW-06.
    """
    with patch('builtins.input', side_effect=['0']), \
         patch('sys.exit') as mock_exit:
        mock_exit.side_effect = SystemExit

        with pytest.raises(SystemExit):
            main()
        
        mock_exit.assert_called_with(0)


def test_navigation_to_submenu_on_valid_input():
    """
    Tests if the correct handler function is called for a valid input.
    Corresponds to ATC-FMW-02.
    """
    # We patch the target function in the module where it's looked up.
    with patch('interactive_cli.start_role_management') as mock_start_role_management, \
         patch('builtins.input', side_effect=['5', '0']), \
         patch('sys.exit') as mock_exit:
        mock_exit.side_effect = SystemExit

        with pytest.raises(SystemExit):
            main()
        
        mock_start_role_management.assert_called_once()

def test_error_message_on_non_numeric_input():
    """
    Tests if a clear error message is shown for non-numeric input.
    Corresponds to T-FMW-08.
    """
    captured_output = io.StringIO()
    sys.stdout = captured_output

    with patch('builtins.input', side_effect=['abc', '0']), \
         patch('sys.exit') as mock_exit:
        mock_exit.side_effect = SystemExit

        with pytest.raises(SystemExit):
            main()

    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()

    assert "无效的输入，请输入一个数字。" in output

def test_error_message_on_out_of_range_input():
    """
    Tests if a clear error message is shown for out-of-range input.
    Corresponds to T-FMW-10.
    """
    captured_output = io.StringIO()
    sys.stdout = captured_output

    with patch('builtins.input', side_effect=['99', '0']), \
         patch('sys.exit') as mock_exit:
        mock_exit.side_effect = SystemExit

        with pytest.raises(SystemExit):
            main()

    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()

    assert "无效的选项，请重新输入。" in output