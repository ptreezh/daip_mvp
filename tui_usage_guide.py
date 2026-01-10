#!/usr/bin/env python3
"""Script to demonstrate proper TUI usage."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def show_usage_instructions():
    """Show instructions for using the DAIP-LIVE TUI."""
    print("🚀 DAIP-LIVE TUI Usage Instructions")
    print("=" * 50)
    print()
    print("The DAIP-LIVE TUI is a Terminal User Interface application.")
    print("When you run 'poetry run daip run', the TUI will:")
    print()
    print("1. Take over your entire terminal screen")
    print("2. Display a user interface with input/output areas")
    print("3. Wait for you to type commands and press Enter")
    print()
    print("INTERFACE ELEMENTS:")
    print("- Header at the top")
    print("- Main conversation area (left side)")
    print("- System status panel (right side)") 
    print("- Input field at the bottom")
    print("- Status bar showing current status")
    print()
    print("HOW TO INTERACT:")
    print("- Type commands like '/help', '/debate', '/wiki' in the input field")
    print("- Press Enter to submit your command")
    print("- Use Tab to move between input fields")
    print("- Press Ctrl+E to exit (requires confirmation)")
    print("- Press Ctrl+C to exit immediately")
    print()
    print("COMMON COMMANDS:")
    print("- /help          : Show help information")
    print("- /debate <topic>: Start a debate on a topic")
    print("- /wiki <title>  : Create a wiki page")
    print("- /search <query>: Search conversation history")
    print("- /model         : Show available models")
    print("- /copy          : Copy content to clipboard")
    print("- /quit          : Exit the application")
    print()
    print("TROUBLESHOOTING:")
    print("If the TUI appears to 'hang':")
    print("- This is normal behavior - the TUI is running and waiting for input")
    print("- Look for the TUI interface elements described above")
    print("- Type commands and press Enter to interact")
    print("- Use Ctrl+C or Ctrl+E to exit")
    print()
    print("The previous issue with immediate hanging on import has been fixed.")
    print("The TUI should now start and display its interface normally.")
    print("=" * 50)

if __name__ == "__main__":
    show_usage_instructions()