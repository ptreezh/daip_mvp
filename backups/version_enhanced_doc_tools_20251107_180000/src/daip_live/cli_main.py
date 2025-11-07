#!/usr/bin/env python3
"""Main CLI entry point with dependency injection."""

import sys
from pathlib import Path

# Add the src directory to the path so we can import daip_live
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path.parent))

from daip_live.container import Container
from daip_live.cli import app
from daip_live.config import create_config_yaml_if_not_exists


def main() -> None:
    """Main entry point with dependency injection setup."""
    create_config_yaml_if_not_exists()
    container = Container()
    container.config.from_yaml("config.yaml")
    from daip_live import cli
    container.wire(modules=[cli])
    app()


if __name__ == "__main__":
    main()