"""
Test script to verify TUI command implementation status.
"""
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from src.daip_live.tui import DAIP_TUI


def test_tui_commands():
    """Test that TUI commands are properly implemented."""
    print("Testing TUI command implementation...")
    
    # Create a TUI instance
    tui = DAIP_TUI()
    
    # Check available commands
    print(f"Available commands: {len(tui._available_commands)}")
    for cmd, help_text in tui._available_commands:
        print(f"  {cmd}: {help_text}")
    
    # Verify that /init is not in available commands
    init_commands = [cmd for cmd, _ in tui._available_commands if cmd == "/init"]
    if init_commands:
        print("ERROR: /init command should not be available!")
        return False
    else:
        print("SUCCESS: /init command correctly excluded from available commands")
    
    # Verify that /shortcut is not in available commands
    shortcut_commands = [cmd for cmd, _ in tui._available_commands if cmd == "/shortcut"]
    if shortcut_commands:
        print("ERROR: /shortcut command should not be available!")
        return False
    else:
        print("SUCCESS: /shortcut command correctly excluded from available commands")
    
    # Test that all available commands have handlers
    missing_handlers = []
    for cmd_name, _ in tui._available_commands:
        # Remove the leading '/'
        handler_name = f"_handle{cmd_name}_command".replace('/', '_')
        if not hasattr(tui, handler_name):
            missing_handlers.append((cmd_name, handler_name))
    
    if missing_handlers:
        print("ERROR: Missing handlers for commands:")
        for cmd, handler in missing_handlers:
            print(f"  {cmd} -> {handler}")
        return False
    else:
        print("SUCCESS: All available commands have handlers")
    
    print("All tests passed!")
    return True


if __name__ == "__main__":
    test_tui_commands()