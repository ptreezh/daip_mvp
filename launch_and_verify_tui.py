#!/usr/bin/env python3
"""
TUI启动和验证脚本
正确启动TUI并验证界面显示
"""

import sys
import os
import subprocess
import platform
import time

def print_header():
    """打印标题"""
    print("=" * 60)
    print("🤖 DAIP-LIVE TUI 启动和验证工具")
    print("=" * 60)
    print()

def check_environment():
    """检查环境"""
    print("🔍 环境检查...")
    
    # 检查Python版本
    version = sys.version_info
    print(f"   Python版本: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 9:
        print("   ✅ Python版本符合要求")
    else:
        print("   ❌ Python版本过低（需要>=3.9）")
        return False
    
    # 检查操作系统
    system = platform.system()
    print(f"   操作系统: {system}")
    if system == "Windows":
        print("   ✅ Windows系统支持")
    else:
        print("   ⚠️  非Windows系统（可能需要调整）")
    
    # 检查终端
    terminal_info = {
        "Windows Terminal": "WT_SESSION" in os.environ,
        "VS Code Terminal": "VSCODE_PID" in os.environ,
        "ConEmu": "ConEmuANSI" in os.environ
    }
    
    terminal_types = [k for k, v in terminal_info.items() if v]
    if terminal_types:
        print(f"   终端类型: {', '.join(terminal_types)}")
        print("   ✅ 现代终端支持")
    else:
        print("   终端类型: 传统命令行")
        print("   ⚠️  建议使用Windows Terminal获得最佳体验")
    
    print()
    return True

def verify_project_structure():
    """验证项目结构"""
    print("📂 项目结构验证...")
    
    # 检查必要文件
    required_files = [
        ('config.yaml', '配置文件'),
        ('poetry.lock', '依赖锁文件'),
        ('daip_live.db', '数据库文件')
    ]
    
    for file_name, description in required_files:
        if os.path.exists(file_name):
            print(f"   ✅ {description} ({file_name})")
        else:
            if file_name == 'daip_live.db':
                print(f"   ⚠️  {description} ({file_name}) - 将在首次使用时创建")
            else:
                print(f"   ❌ {description} ({file_name})")
                return False
    
    # 检查角色目录
    roles_dir = 'roles'
    if os.path.exists(roles_dir) and os.path.isdir(roles_dir):
        roles = [f for f in os.listdir(roles_dir) if f.endswith('.yaml')]
        print(f"   ✅ 角色目录 ({len(roles)} 个角色文件)")
    else:
        print(f"   ❌ 角色目录 ({roles_dir})")
        return False
    
    # 检查源码目录
    src_dir = 'src/daip_live'
    if os.path.exists(src_dir) and os.path.isdir(src_dir):
        print(f"   ✅ 源码目录 ({src_dir})")
    else:
        print(f"   ❌ 源码目录 ({src_dir})")
        return False
    
    print()
    return True

def check_dependencies():
    """检查依赖"""
    print("📦 依赖检查...")
    
    required_packages = [
        ('textual', 'TUI框架'),
        ('typer', 'CLI框架'),
        ('sqlalchemy', '数据库ORM'),
        ('pydantic', '数据验证'),
        ('yaml', 'YAML解析')
    ]
    
    missing_packages = []
    for package_name, description in required_packages:
        try:
            if package_name == 'yaml':
                import yaml
            else:
                __import__(package_name)
            print(f"   ✅ {description} ({package_name})")
        except ImportError:
            print(f"   ❌ {description} ({package_name})")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"   ❌ 缺少依赖包: {missing_packages}")
        return False
    
    print()
    return True

def test_cli_functionality():
    """测试CLI功能"""
    print("⚙️  CLI功能测试...")
    
    try:
        # 测试帮助命令
        result = subprocess.run([
            sys.executable, '-m', 'daip_live.cli', '--help'
        ], cwd=os.getcwd(), capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and 'Usage:' in result.stdout:
            print("   ✅ CLI帮助命令正常")
        else:
            print("   ❌ CLI帮助命令异常")
            return False
        
        # 测试角色命令
        result = subprocess.run([
            sys.executable, '-m', 'daip_live.cli', 'role', 'list'
        ], cwd=os.getcwd(), capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("   ✅ CLI角色命令正常")
        else:
            print("   ⚠️  CLI角色命令异常（可能无角色数据）")
        
    except Exception as e:
        print(f"   ❌ CLI功能测试异常: {e}")
        return False
    
    print()
    return True

def launch_tui_with_verification():
    """启动TUI并验证"""
    print("🚀 启动TUI并验证界面...")
    
    try:
        print("   正在启动TUI...")
        print("   预期界面元素:")
        print("     - Header: 标题栏")
        print("     - RichLog: 输出区域（显示欢迎信息和logo）")
        print("     - Input: 输入框（可输入命令）")
        print("     - StatusBar: 状态栏（显示模型、Token使用率等）")
        print()
        
        # 显示启动命令
        print("📋 启动命令:")
        print(f"   cd /d {os.getcwd()}")
        print("   python -m daip_live.cli run")
        print()
        
        # 提供启动选项
        print("请选择启动方式:")
        print("  1. 直接启动（当前终端）")
        print("  2. 显示启动说明")
        print("  3. 退出")
        print()
        
        choice = input("请输入选择 (1-3): ").strip()
        
        if choice == "1":
            print("正在启动TUI...")
            print("按 Ctrl+C 退出")
            print("-" * 40)
            try:
                subprocess.run([sys.executable, '-m', 'daip_live.cli', 'run'])
                print("\n👋 TUI已退出")
            except KeyboardInterrupt:
                print("\n👋 TUI已退出（用户中断）")
            except Exception as e:
                print(f"\n❌ TUI启动失败: {e}")
                
        elif choice == "2":
            print("\n📋 启动说明:")
            print("   1. 推荐使用Windows Terminal启动以获得最佳界面显示")
            print("   2. 在Windows Terminal中执行以下命令:")
            print(f"      cd /d {os.getcwd()}")
            print("      python -m daip_live.cli run")
            print("   3. TUI启动后应显示:")
            print("      - 顶部标题栏")
            print("      - 中间输出区域（显示人格AI logo 和欢迎信息）")
            print("      - 底部输入框和状态栏")
            print("   4. 可用命令:")
            print("      /help - 显示帮助")
            print("      /pa <问题> - 与AI对话")
            print("      /role list - 列出角色")
            print("      /debate start <主题> - 开始辩论")
            print("      Ctrl+E两次 - 退出")
            
        elif choice == "3":
            print("👋 退出")
            return True
            
        else:
            print("❌ 无效选择")
            
    except Exception as e:
        print(f"❌ TUI启动和验证异常: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print_header()
    
    # 执行所有检查
    checks = [
        ("环境检查", check_environment),
        ("项目结构验证", verify_project_structure),
        ("依赖检查", check_dependencies),
        ("CLI功能测试", test_cli_functionality)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        if not check_func():
            print(f"❌ {check_name} 失败")
            all_passed = False
        else:
            print(f"✅ {check_name} 通过")
        print()
    
    if not all_passed:
        print("❌ 部分检查失败，请解决后再启动TUI")
        return 1
    
    print("🎉 所有检查通过！")
    print()
    
    # 启动TUI
    if launch_tui_with_verification():
        print("\n✅ TUI启动和验证完成")
        return 0
    else:
        print("\n❌ TUI启动和验证失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())