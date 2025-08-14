#!/usr/bin/env python3
"""启动工程可用的智能助手
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from src.working_intelligent_assistant import main

if __name__ == "__main__":
    print("🚀 启动DAIP-LIVE工程可用智能助手...")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 系统已安全退出")
    except Exception as e:
        print(f"❌ 系统运行错误: {e}")
        sys.exit(1)
