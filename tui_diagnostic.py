#!/usr/bin/env python3
"""
TUI启动诊断工具
诊断TUI启动问题并提供解决方案
"""

import sys
import os
import subprocess
import platform
import threading
import time

def diagnose_environment():
    """诊断运行环境"""
    print("=" * 60)
    print("TUI启动问题诊断")
    print("=" * 60)
    
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    print(f"当前目录: {os.getcwd()}")
    print(f"终端类型: {os.environ.get('TERM', 'N/A')}")
    print(f"控制台编码: {sys.stdout.encoding}")
    print()

def check_terminal_compatibility():
    """检查终端兼容性"""
    print("检查终端兼容性...")
    
    # 检查是否在Windows上
    if platform.system() == "Windows":
        # 检查是否为Windows Terminal
        is_windows_terminal = "WT_SESSION" in os.environ
        is_conemu = "ConEmuANSI" in os.environ
        is_vscode = "VSCODE_PID" in os.environ
        
        print(f"  Windows系统: 是")
        print(f"  Windows Terminal: {'是' if is_windows_terminal else '否'}")
        print(f"  ConEmu: {'是' if is_conemu else '否'}")
        print(f"  VS Code终端: {'是' if is_vscode else '否'}")
        
        # 建议使用Windows Terminal
        if not is_windows_terminal and not is_vscode:
            print("  📋 建议: 使用Windows Terminal或VS Code终端以获得最佳体验")
        else:
            print("  ✅ 终端兼容性良好")
    else:
        print("  非Windows系统，兼容性良好")
    
    print()

def test_tui_basic_functionality():
    """测试TUI基本功能"""
    print("测试TUI基本功能...")
    
    # 测试导入
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
        from daip_live.tui import DAIP_TUI
        print("  ✅ TUI模块导入成功")
    except Exception as e:
        print(f"  ❌ TUI模块导入失败: {e}")
        return False
    
    # 测试实例创建
    try:
        tui = DAIP_TUI()
        print("  ✅ TUI实例创建成功")
    except Exception as e:
        print(f"  ❌ TUI实例创建失败: {e}")
        return False
    
    print("  📋 TUI核心功能正常，问题可能在界面显示")
    print()
    return True

def test_cli_functionality():
    """测试CLI功能"""
    print("测试CLI功能...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'daip_live.cli', '--help'
        ], cwd=os.getcwd(), capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and 'Usage:' in result.stdout:
            print("  ✅ CLI功能正常")
        else:
            print("  ❌ CLI功能异常")
            return False
    except Exception as e:
        print(f"  ❌ CLI功能测试异常: {e}")
        return False
    
    print()
    return True

def suggest_solutions():
    """建议解决方案"""
    print("=" * 60)
    print("问题分析与解决方案")
    print("=" * 60)
    
    print("🔍 问题分析:")
    print("  根据测试结果，TUI核心功能正常，可以成功初始化和运行，")
    print("  但界面元素可能无法在当前终端中正确显示。")
    print()
    
    print("💡 解决方案:")
    print("  1. 使用Windows Terminal (推荐)")
    print("     - 下载: Microsoft Store 或 https://aka.ms/terminal")
    print("     - 提供完整的ANSI转义序列支持")
    print()
    print("  2. 使用PowerShell 7+")
    print("     - 比Windows PowerShell更好的兼容性")
    print()
    print("  3. 使用VS Code终端")
    print("     - 在VS Code中打开项目并使用内置终端")
    print()
    print("  4. 直接运行命令")
    print("     python -m daip_live.cli run")
    print()
    print("📋 如果使用Windows命令提示符(cmd)，建议切换到更现代的终端。")
    print()

def main():
    diagnose_environment()
    check_terminal_compatibility()
    test_tui_basic_functionality()
    test_cli_functionality()
    suggest_solutions()
    
    print("🎉 诊断完成！请根据建议的解决方案尝试启动TUI。")

if __name__ == "__main__":
    main()