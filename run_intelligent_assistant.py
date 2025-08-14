#!/usr/bin/env python3
"""智能助手启动脚本

一键启动完整的智能助手系统
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from src.intelligent_assistant_app import main

if __name__ == "__main__":
    print("🚀 启动DAIP-LIVE智能助手系统...")
    print("=" * 60)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 系统已安全退出")
    except Exception as e:
        print(f"❌ 系统运行错误: {e}")
        sys.exit(1)
