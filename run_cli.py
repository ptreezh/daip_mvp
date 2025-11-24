#!/usr/bin/env python
"""
CLI入口点，用于运行DAIP系统中的命令
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.daip_live.cli.main import app

if __name__ == "__main__":
    # 运行CLI应用
    try:
        app()
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running CLI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)