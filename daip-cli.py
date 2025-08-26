#!/usr/bin/env python
"""@Time    : 2025-07-21 14:35:00
@Author  : DAIP-LIVE Team
@File    : daip-cli.py
@Description: Standalone script to run the DAIP-LIVE CLI
"""

import sys
from pathlib import Path

# Add project root to path to ensure imports work correctly
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.cli.main import app
from rich.console import Console

if __name__ == "__main__":
    try:
        app()
    except Exception as e:
        console = Console()
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")
        # Optionally, add more logic here for logging or debugging
        # For example, you could write the full traceback to a log file
        # import traceback
        # with open("error.log", "a") as f:
        #     f.write(traceback.format_exc())
        sys.exit(1)
