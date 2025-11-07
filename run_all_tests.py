#!/usr/bin/env python3
"""
Test Runner: Execute All Tests
综合执行所有测试
"""

import sys
import os
import subprocess
import time

def run_test_script(script_name):
    """运行单个测试脚本"""
    print(f"\n{'='*60}")
    print(f"运行测试: {script_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            sys.executable, script_name
        ], cwd=os.getcwd(), capture_output=True, text=True, timeout=60, encoding='utf-8')
        
        # 输出结果
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ {script_name} 执行超时")
        return False
    except Exception as e:
        print(f"❌ {script_name} 执行异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 DAIP-LIVE TUI 调试测试套件")
    print("=" * 60)
    
    test_scripts = [
        'test_01_environment.py',
        'test_02_module_import.py',
        'test_03_cli_function.py',
        'test_04_tui_initialization.py',
        'test_05_full_startup.py'
    ]
    
    results = []
    for script in test_scripts:
        script_path = os.path.join(os.getcwd(), script)
        if os.path.exists(script_path):
            success = run_test_script(script)
            results.append((script, success))
        else:
            print(f"⚠️  测试脚本不存在: {script}")
            results.append((script, False))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for script, success in results:
        if success:
            print(f"✅ {script}")
            passed += 1
        else:
            print(f"❌ {script}")
            failed += 1
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("\n🎉 所有测试通过！TUI应该可以正常启动。")
        print("\n推荐启动方式:")
        print("  1. 使用CLI: python -m daip_live.cli run")
        print("  2. 使用脚本: start_debate_demo.bat")
        return 0
    else:
        print(f"\n⚠️  {failed} 个测试失败，需要进一步排查。")
        return 1

if __name__ == "__main__":
    sys.exit(main())