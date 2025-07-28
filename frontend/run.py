#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personal Intelligence Hub 启动脚本

用于启动Lona Web应用的便捷脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main_app import app
    
    if __name__ == '__main__':
        print("=" * 60)
        print("🎭 Personal Intelligence Hub")
        print("基于制度原语的集体智慧涌现平台")
        print("=" * 60)
        print()
        print("🚀 正在启动Lona Web应用...")
        print("📍 访问地址: http://localhost:8080")
        print("🔧 开发模式: 已启用")
        print()
        print("按 Ctrl+C 停止服务器")
        print("=" * 60)
        
        app.run(
            host='localhost',
            port=8080,
            debug=True,
            shutdown_timeout=10
        )
        
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所需依赖:")
    print("pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ 启动失败: {e}")
    sys.exit(1)