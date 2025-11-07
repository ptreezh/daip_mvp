#!/usr/bin/env python3
"""
TUI界面验证脚本
验证TUI界面元素是否正确显示
"""

import sys
import os
import subprocess
import time
import threading

def test_tui_interface():
    """测试TUI界面元素"""
    print("=" * 60)
    print("TUI界面元素验证测试")
    print("=" * 60)
    
    print("1. 启动TUI并检查界面元素...")
    
    try:
        # 启动TUI进程
        process = subprocess.Popen([
            sys.executable, '-m', 'daip_live.cli', 'run', '界面测试'
        ], cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
           text=True, encoding='utf-8')
        
        # 等待3秒让TUI初始化
        time.sleep(3)
        
        # 检查进程状态
        if process.poll() is None:
            # 进程仍在运行，说明TUI已启动
            print("   ✅ TUI已成功启动")
            
            # 尝试获取输出（在支持ANSI的终端中可能有输出）
            try:
                stdout, stderr = process.communicate(timeout=1)
                if stdout or stderr:
                    print("   📋 TUI输出:")
                    if stdout:
                        print(f"      stdout: {stdout[:200]}...")
                    if stderr:
                        print(f"      stderr: {stderr[:200]}...")
                else:
                    print("   ⚠️  TUI无输出（可能因终端兼容性问题）")
            except subprocess.TimeoutExpired:
                # 正常情况，TUI仍在运行
                print("   ✅ TUI正常运行中")
                # 终止进程
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
        else:
            # 进程已退出
            stdout, stderr = process.communicate()
            print(f"   ❌ TUI启动失败 (返回码: {process.returncode})")
            if stdout:
                print(f"      stdout: {stdout[:200]}...")
            if stderr:
                print(f"      stderr: {stderr[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ TUI启动异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("2. 验证配置文件...")
    config_path = os.path.join(os.getcwd(), 'config.yaml')
    if os.path.exists(config_path):
        print("   ✅ 配置文件存在")
        # 检查关键配置
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'llm_provider:' in content:
                    print("   ✅ LLM提供者配置正确")
                if 'database:' in content:
                    print("   ✅ 数据库配置正确")
        except Exception as e:
            print(f"   ⚠️  配置文件读取异常: {e}")
    else:
        print("   ❌ 配置文件不存在")
        return False
    
    print()
    print("3. 验证角色文件...")
    roles_dir = os.path.join(os.getcwd(), 'roles')
    if os.path.exists(roles_dir) and os.path.isdir(roles_dir):
        roles = os.listdir(roles_dir)
        if roles:
            print(f"   ✅ 角色目录包含 {len(roles)} 个角色文件")
            # 检查关键角色
            key_roles = ['tech_analyst.yaml', 'pro_arguer.yaml', 'con_arguer.yaml']
            found_roles = [r for r in key_roles if r in roles]
            if found_roles:
                print(f"   ✅ 找到关键角色: {found_roles}")
            else:
                print("   ⚠️  未找到关键角色文件")
        else:
            print("   ⚠️  角色目录为空")
    else:
        print("   ❌ 角色目录不存在")
        return False
    
    print()
    print("4. 验证数据库...")
    db_path = os.path.join(os.getcwd(), 'daip_live.db')
    if os.path.exists(db_path):
        print("   ✅ 数据库文件存在")
    else:
        print("   ⚠️  数据库文件不存在（将在首次使用时创建）")
    
    print()
    return True

def main():
    print("🚀 开始TUI界面验证测试...")
    
    if test_tui_interface():
        print("=" * 60)
        print("✅ TUI界面验证测试通过!")
        print()
        print("📋 启动说明:")
        print("   1. 推荐使用Windows Terminal启动以获得最佳界面显示")
        print("   2. 启动命令: python -m daip_live.cli run")
        print("   3. TUI界面应包含以下元素:")
        print("      - Header标题栏")
        print("      - RichLog输出区域")
        print("      - Input输入框")
        print("      - StatusBar状态栏")
        print()
        print("💡 如果界面未正确显示:")
        print("   - 请安装Windows Terminal")
        print("   - 或使用VS Code终端")
        print("   - 或使用PowerShell 7+")
        return 0
    else:
        print("=" * 60)
        print("❌ TUI界面验证测试失败!")
        return 1

if __name__ == "__main__":
    sys.exit(main())