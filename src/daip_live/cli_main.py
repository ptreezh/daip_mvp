#!/usr/bin/env python3
"""Main CLI entry point with dependency injection."""

import sys
from pathlib import Path

# Add the src directory to the path so we can import daip_live
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path.parent))

from daip_live.cli import app  # noqa: E402
from daip_live.config import create_config_yaml_if_not_exists  # noqa: E402
from daip_live.container import Container  # noqa: E402


def main() -> None:
    """Main entry point with dependency injection setup."""
    create_config_yaml_if_not_exists()
    container = Container()
    # 只在运行CLI时进行模块绑定，避免在容器初始化时触发TUI加载
    from daip_live import cli

    container.wire(modules=[cli])  # 仅在此时绑定模块
    app()


if __name__ == "__main__":
    main()
