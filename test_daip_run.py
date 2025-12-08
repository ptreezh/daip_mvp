#!/usr/bin/env python3
"""Test the actual daip run command behavior"""

import subprocess
import sys
import os

def test_daip_run():
    # Run the daip command with a short timeout to see initialization
    try:
        # We'll run it with a timeout using a different approach
        result = subprocess.run([
            sys.executable, "-c", 
            """
import sys
sys.path.insert(0, 'src')
from daip_live.tui_modular import DAIP_TUI
print('Creating TUI...')
tui = DAIP_TUI()
print('TUI created successfully - initialization complete')
# Don't run the TUI, just test initialization
"""
        ], 
        capture_output=True, 
        text=True, 
        timeout=10,
        cwd=os.getcwd()
        )
        
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"Return code: {result.returncode}")
        
    except subprocess.TimeoutExpired:
        print("Process timed out (expected for TUI that waits for input)")
    except Exception as e:
        print(f"Error running test: {e}")

if __name__ == "__main__":
    test_daip_run()