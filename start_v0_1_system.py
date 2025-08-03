#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DAIP-LIVE V0.1 最小可体验版本
基于现有Personal Intelligence Hub的完整系统启动脚本
按照.kiro/specs/real-multi-round-debate-system规范执行
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8+版本")
        return False
        
    # 检查项目根目录
    project_root = Path(__file__).parent
    if not (project_root / "personal_intelligence_hub").exists():
        print("❌ 未找到Personal Intelligence Hub目录")
        return False
        
    # 检查核心服务
    if not (project_root / "src" / "core_services").exists():
        print("❌ 未找到核心服务目录")
        return False
        
    print("✅ 环境检查通过")
    return True

def check_dependencies():
    """检查依赖"""
    print("📦 检查依赖包...")
    
    required_packages = ['lona', 'fastapi', 'aiohttp']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("正在安装依赖...")
        
        # 尝试安装依赖
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "lona", "fastapi", "aiohttp", "uvicorn"
            ])
            print("✅ 依赖安装成功")
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败，请手动安装: pip install lona fastapi aiohttp uvicorn")
            return False
    else:
        print("✅ 依赖检查通过")
    
    return True

def start_backend_services():
    """启动后端服务（如果需要）"""
    print("⚙️ 准备后端服务...")
    
    # 检查是否需要启动Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama服务已运行")
        else:
            print("⚠️ Ollama服务未运行，将使用模拟LLM")
    except:
        print("⚠️ Ollama服务未运行，将使用模拟LLM")
    
    print("✅ 后端服务准备完成")
    return True

def start_personal_intelligence_hub():
    """启动Personal Intelligence Hub"""
    print("🚀 启动Personal Intelligence Hub...")
    
    # 添加项目路径
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        # 导入并启动主应用
        from personal_intelligence_hub.main_app import main as hub_main
        
        print("=" * 60)
        print("🎭 DAIP-LIVE V0.1 最小可体验版本")
        print("📋 基于.kiro规范的完整系统")
        print("=" * 60)
        print("✨ 核心功能:")
        print("  • 🤖 PersonalAssistant 统一入口")
        print("  • 🔄 工作流智能选择 (Critical Review / Multi-Perspective)")
        print("  • 👥 多角色认知代理协作")
        print("  • 📊 透明度全程监控")
        print("  • 📚 知识Wiki协同构建")
        print("  • 🎯 任务管理和执行")
        print("=" * 60)
        print("📍 访问地址: http://localhost:8086")
        print("🚀 主界面: http://localhost:8086/hub")
        print("=" * 60)
        
        # 延迟1秒后自动打开浏览器
        import threading
        threading.Timer(2.0, lambda: webbrowser.open("http://localhost:8086/hub")).start()
        
        # 启动Hub应用
        hub_main()
        
    except KeyboardInterrupt:
        print("\n👋 DAIP-LIVE V0.1 已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n🔧 故障排除建议:")
        print("1. 检查Python版本 >= 3.8")
        print("2. 安装依赖: pip install -r personal_intelligence_hub/requirements.txt")
        print("3. 检查端口8086是否被占用")
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 DAIP-LIVE V0.1 最小可体验版本启动器")
    print("📋 按照.kiro/specs/real-multi-round-debate-system规范执行")
    print("=" * 60)
    
    # 环境检查
    if not check_environment():
        sys.exit(1)
    
    # 依赖检查
    if not check_dependencies():
        sys.exit(1)
    
    # 后端服务准备
    if not start_backend_services():
        sys.exit(1)
    
    # 启动Personal Intelligence Hub
    if not start_personal_intelligence_hub():
        sys.exit(1)

if __name__ == '__main__':
    main()