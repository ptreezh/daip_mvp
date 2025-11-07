# tui_runner.py

import asyncio
import sys

from daip_live.container import Container
from daip_live import tui

def main():
    """Application entry point."""
    container = Container()
    container.config.from_yaml("config.yaml")
    container.wire(modules=[tui])

    tui_app = container.tui_app()
    
    # The goal can be passed from the command line in the future
    # For now, we leave it as None
    tui_app.goal = None 

    asyncio.run(tui_app.run_async())


if __name__ == "__main__":
    main()