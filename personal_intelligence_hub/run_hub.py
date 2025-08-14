#!/usr/bin/env python3
"""Personal Intelligence Hub - 启动脚本

快速启动Personal Intelligence Hub应用
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('HOST', 'localhost')
os.environ.setdefault('PORT', '8086')

def main():
    """主函数"""
    print("🚀 启动 Personal Intelligence Hub...")
    print("=" * 50)

    try:
        # 导入并运行主应用
        from personal_intelligence_hub.main_app import main as app_main
        app_main()

    except KeyboardInterrupt:
        print("\n👋 Personal Intelligence Hub 已停止")
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
