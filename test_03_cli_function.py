#!/usr/bin/env python3
"""
Test 3: CLI Function Validation
验证CLI功能
"""

import sys
import os
import subprocess
import time

def test_cli_help():
    """测试CLI帮助命令"""
    print("1. 测试CLI帮助命令...")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'daip_live.cli', '--help'
        ], cwd=os.getcwd(), capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            if 'Usage:' in result.stdout and 'Commands:' in result.stdout:
                print("   ✅ CLI帮助命令执行成功")
                return True
            else:
                print("   ❌ CLI帮助命令输出不符合预期")
                print(f"      stdout: {result.stdout[:200]}...")
                return False
        else:
            print(f"   ❌ CLI帮助命令执行失败 (返回码: {result.returncode})")
            print(f"      stderr: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("   ❌ CLI帮助命令执行超时")
        return False
    except Exception as e:
        print(f"   ❌ CLI帮助命令执行异常: {e}")
        return False

def test_cli_run_command():
    """测试CLI运行命令"""
    print("2. 测试CLI运行命令...")
    try:
        # 启动CLI run命令，设置较短超时时间
        process = subprocess.Popen([
            sys.executable, '-m', 'daip_live.cli', 'run', '测试消息'
        ], cwd=os.getcwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
           text=True, encoding='utf-8')
        
        # 等待3秒观察是否有输出
        time.sleep(3)
        
        # 检查进程状态
        if process.poll() is None:
            # 进程仍在运行，说明TUI可能已启动
            process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
            
            print("   ✅ CLI运行命令启动成功 (TUI正在运行)")
            # 检查是否有输出
            if stdout.strip() or stderr.strip():
                if stdout.strip():
                    print(f"      stdout: {stdout[:100]}...")
                if stderr.strip():
                    print(f"      stderr: {stderr[:100]}...")
            return True
        else:
            # 进程已退出，检查输出
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                print("   ✅ CLI运行命令执行完成")
                if stdout.strip():
                    print(f"      stdout: {stdout[:100]}...")
                if stderr.strip():
                    print(f"      stderr: {stderr[:100]}...")
                return True
            else:
                print(f"   ❌ CLI运行命令执行失败 (返回码: {process.returncode})")
                if stdout:
                    print(f"      stdout: {stdout[:200]}...")
                if stderr:
                    print(f"      stderr: {stderr[:200]}...")
                return False
    except Exception as e:
        print(f"   ❌ CLI运行命令执行异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_subcommands():
    """测试CLI子命令"""
    print("3. 测试CLI子命令...")
    subcommands = ['role', 'session', 'debate', 'project']
    
    failed_commands = []
    for cmd in subcommands:
        try:
            result = subprocess.run([
                sys.executable, '-m', 'daip_live.cli', cmd, '--help'
            ], cwd=os.getcwd(), capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"   ✅ {cmd} 子命令帮助可用")
            else:
                print(f"   ❌ {cmd} 子命令帮助不可用")
                failed_commands.append(cmd)
        except subprocess.TimeoutExpired:
            print(f"   ❌ {cmd} 子命令帮助超时")
            failed_commands.append(cmd)
        except Exception as e:
            print(f"   ❌ {cmd} 子命令执行异常: {e}")
            failed_commands.append(cmd)
    
    if failed_commands:
        print(f"   ❌ 以下子命令测试失败: {failed_commands}")
        return False
    else:
        print("   ✅ 所有子命令测试通过")
        return True

def test_cli_version():
    """测试CLI版本信息"""
    print("4. 测试CLI版本信息...")
    # 这个测试可能不适用，因为我们没有明确的版本命令
    print("   ⚠️  跳过版本信息测试 (无明确版本命令)")
    return True

def main():
    print("=" * 60)
    print("测试3: CLI功能验证")
    print("=" * 60)
    
    tests = [
        test_cli_help,
        test_cli_run_command,
        test_cli_subcommands,
        test_cli_version
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ 测试 {test.__name__} 执行失败: {e}")
            results.append(False)
        print()
    
    print("=" * 60)
    if all(results):
        print("✅ 所有CLI功能测试通过!")
        return 0
    else:
        failed_count = len([r for r in results if not r])
        print(f"❌ {failed_count} 个测试失败!")
        return 1

if __name__ == "__main__":
    sys.exit(main())