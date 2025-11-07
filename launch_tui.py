#!/usr/bin/env python3
"""
TUI启动助手
帮助用户正确启动TUI并提供故障排除
"""

import sys
import os
import platform
import subprocess
import webbrowser

def print_welcome():
    """打印欢迎信息"""
    print("=" * 60)
    print("🤖 DAIP-LIVE TUI 启动助手")
    print("=" * 60)
    print()

def check_prerequisites():
    """检查启动前提条件"""
    print("🔍 检查启动前提条件...")
    
    # 检查项目文件
    required_files = ['config.yaml', 'poetry.lock']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print(f"  ❌ 缺少必要文件: {missing_files}")
        return False
    
    # 检查Ollama服务
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("  ✅ Ollama服务运行正常")
        else:
            print("  ⚠️  Ollama服务未运行（非必需，但建议启动）")
    except FileNotFoundError:
        print("  ⚠️  未安装Ollama（非必需，但建议安装）")
    except Exception as e:
        print(f"  ⚠️  检查Ollama服务时出错: {e}")
    
    print()
    return True

def suggest_terminals():
    """推荐现代终端"""
    print("📋 推荐的终端应用:")
    print("  1. Windows Terminal (推荐)")
    print("     - 完整的ANSI支持")
    print("     - 更好的字体渲染")
    print("     - 多标签页支持")
    print("     下载: Microsoft Store 或 https://aka.ms/terminal")
    print()
    print("  2. VS Code 终端")
    print("     - 内置终端支持")
    print("     - 与代码编辑器集成")
    print()
    print("  3. PowerShell 7+")
    print("     - 比传统cmd更好的兼容性")
    print()

def launch_tui():
    """启动TUI"""
    print("🚀 启动TUI...")
    print()
    print("请选择启动方式:")
    print("  1. 直接启动 (在当前终端)")
    print("  2. 打开Windows Terminal并启动")
    print("  3. 显示启动命令 (手动复制)")
    print("  4. 退出")
    print()
    
    try:
        choice = input("请输入选择 (1-4): ").strip()
        
        if choice == "1":
            print("正在启动TUI...")
            print("如果界面未显示，请尝试使用Windows Terminal")
            print()
            try:
                subprocess.run([sys.executable, '-m', 'daip_live.cli', 'run'])
            except KeyboardInterrupt:
                print("\n👋 TUI已退出")
            except Exception as e:
                print(f"❌ 启动失败: {e}")
                
        elif choice == "2":
            # 尝试打开Windows Terminal
            try:
                # 构建启动命令
                cmd = f"cd /d {os.getcwd()} && python -m daip_live.cli run"
                subprocess.run(['wt', '-w', '0', 'new-tab', '--title', 'DAIP-LIVE TUI', cmd])
                print("✅ Windows Terminal已启动")
            except FileNotFoundError:
                print("❌ 未找到Windows Terminal，请先安装")
                print("   下载地址: https://aka.ms/terminal")
            except Exception as e:
                print(f"❌ 启动Windows Terminal失败: {e}")
                
        elif choice == "3":
            print("📋 启动命令:")
            print(f"   cd /d {os.getcwd()}")
            print("   python -m daip_live.cli run")
            print()
            print("请复制以上命令到支持ANSI的终端中执行")
            
        elif choice == "4":
            print("👋 再见!")
            return
            
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n👋 再见!")

def show_troubleshooting():
    """显示故障排除信息"""
    print("\n🔧 常见问题与解决方案:")
    print("  问题1: 界面显示异常或乱码")
    print("    解决方案: 使用Windows Terminal或设置环境变量")
    print("      set PYTHONIOENCODING=utf-8")
    print()
    print("  问题2: 启动后无响应")
    print("    解决方案: 检查Ollama服务是否运行")
    print("      ollama serve")
    print()
    print("  问题3: 显示'命令未找到'")
    print("    解决方案: 确保在项目根目录下运行")
    print()

def main():
    print_welcome()
    
    if not check_prerequisites():
        print("❌ 前提条件检查失败，请检查项目配置")
        return
    
    suggest_terminals()
    launch_tui()
    show_troubleshooting()

if __name__ == "__main__":
    main()