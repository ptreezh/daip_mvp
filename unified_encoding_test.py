#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DAIP-LIVE 统一编码安全测试

解决Windows GBK编码问题，提供统一的测试环境
"""

import os
import sys
import locale
import subprocess
from pathlib import Path

def setup_unicode_environment():
    """设置统一的Unicode环境"""
    # 设置环境变量
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # 设置locale
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except locale.Error:
            # 如果都不支持，使用系统默认
            pass
    
    # 设置标准流编码
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
    if sys.stdin.encoding != 'utf-8':
        sys.stdin.reconfigure(encoding='utf-8')

def safe_subprocess_run(cmd, **kwargs):
    """安全的子进程执行，处理编码问题"""
    # 确保使用UTF-8编码
    env = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'}
    
    # 设置默认参数
    kwargs.setdefault('capture_output', True)
    kwargs.setdefault('text', True)
    kwargs.setdefault('encoding', 'utf-8')
    kwargs.setdefault('errors', 'ignore')
    kwargs.setdefault('env', env)
    
    try:
        return subprocess.run(cmd, **kwargs)
    except UnicodeDecodeError as e:
        # 如果仍然出现编码错误，使用二进制模式
        kwargs['text'] = False
        kwargs.pop('encoding', None)
        result = subprocess.run(cmd, **kwargs)
        
        # 手动解码
        if result.stdout:
            result.stdout = result.stdout.decode('utf-8', errors='ignore')
        if result.stderr:
            result.stderr = result.stderr.decode('utf-8', errors='ignore')
        
        return result

def test_encoding_environment():
    """测试编码环境"""
    print("🔍 测试编码环境设置")
    print("="*50)
    
    print(f"系统默认编码: {sys.getdefaultencoding()}")
    print(f"文件系统编码: {sys.getfilesystemencoding()}")
    print(f"stdout编码: {sys.stdout.encoding}")
    print(f"stderr编码: {sys.stderr.encoding}")
    print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', '未设置')}")
    
    try:
        current_locale = locale.getlocale()
        print(f"当前locale: {current_locale}")
    except:
        print("无法获取locale信息")
    
    # 测试Unicode输出
    print("\n🧪 测试Unicode输出:")
    test_strings = [
        "中文测试",
        "🎯 Emoji测试",
        "UTF-8: Café München 北京"
    ]
    
    for test_str in test_strings:
        print(f"  ✅ {test_str}")

def test_cli_with_encoding():
    """使用编码安全的CLI测试"""
    print("\n🖥️  编码安全的CLI测试")
    print("="*50)
    
    commands = [
        ("daip --help", "显示帮助信息"),
        ("daip role list", "列出角色"),
        ("daip session list", "列出会话"),
    ]
    
    for cmd, description in commands:
        print(f"\n执行命令: {cmd}")
        print(f"描述: {description}")
        
        try:
            result = safe_subprocess_run(cmd.split(), timeout=30)
            
            if result.returncode == 0:
                print(f"  ✅ 命令执行成功 (退出码: {result.returncode})")
                if result.stdout:
                    # 安全地显示输出
                    output_preview = result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout
                    print(f"    输出预览: {output_preview}")
            else:
                print(f"  ⚠️  命令返回非零退出码: {result.returncode}")
                if result.stderr:
                    error_preview = result.stderr[:200] + "..." if len(result.stderr) > 200 else result.stderr
                    print(f"    错误信息: {error_preview}")
                    
        except subprocess.TimeoutExpired:
            print("  ❌ 命令执行超时")
        except Exception as e:
            print(f"  ❌ 命令执行异常: {e}")

def test_tui_startup_with_encoding():
    """编码安全的TUI启动测试"""
    print("\n🚀 编码安全的TUI启动测试")
    print("="*50)
    
    try:
        # 启动TUI进程
        process = subprocess.Popen(
            ["python", "-m", "daip_live.tui"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'}
        )
        
        print("  ✅ TUI进程启动成功")
        
        # 等待启动
        import time
        time.sleep(3)
        
        # 发送退出命令
        process.stdin.write("/quit\n")
        process.stdin.flush()
        print("  ✅ 发送退出命令成功")
        
        # 等待进程结束
        try:
            stdout, stderr = process.communicate(timeout=10)
            print("  ✅ TUI正常退出")
            
            if process.returncode == 0:
                print(f"  ✅ 进程退出码: {process.returncode}")
            else:
                print(f"  ⚠️  进程退出码: {process.returncode}")
                
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            print("  ⚠️  进程超时被终止")
            
    except Exception as e:
        print(f"  ❌ TUI启动失败: {e}")

def create_encoding_safe_test_script():
    """创建编码安全的测试脚本"""
    template = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DAIP-LIVE 编码安全测试脚本

统一处理Windows GBK编码问题
"""

import os
import sys
import locale
import subprocess

def setup_unicode_environment():
    """设置统一的Unicode环境"""
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except locale.Error:
            pass
    
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')
    if sys.stdin.encoding != 'utf-8':
        sys.stdin.reconfigure(encoding='utf-8')

def safe_subprocess_run(cmd, **kwargs):
    """安全的子进程执行"""
    env = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'}
    
    kwargs.setdefault('capture_output', True)
    kwargs.setdefault('text', True)
    kwargs.setdefault('encoding', 'utf-8')
    kwargs.setdefault('errors', 'ignore')
    kwargs.setdefault('env', env)
    
    try:
        return subprocess.run(cmd, **kwargs)
    except UnicodeDecodeError:
        kwargs['text'] = False
        kwargs.pop('encoding', None)
        result = subprocess.run(cmd, **kwargs)
        
        if result.stdout:
            result.stdout = result.stdout.decode('utf-8', errors='ignore')
        if result.stderr:
            result.stderr = result.stderr.decode('utf-8', errors='ignore')
        
        return result

if __name__ == "__main__":
    setup_unicode_environment()
    print("✅ 编码环境已配置")
    
    # 在这里添加你的测试代码
    result = safe_subprocess_run(["daip", "--help"])
    if result.returncode == 0:
        print("✅ CLI命令测试通过")
    else:
        print(f"❌ CLI命令测试失败: {result.returncode}")
'''
    
    with open('encoding_safe_test.py', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("✅ 已创建编码安全测试脚本: encoding_safe_test.py")

def main():
    """主函数"""
    print("🔧 DAIP-LIVE 统一编码安全测试")
    print("="*60)
    print("目标: 解决Windows GBK编码问题，提供统一的测试环境")
    print("="*60)
    
    # 设置编码环境
    setup_unicode_environment()
    
    # 执行测试
    test_encoding_environment()
    test_cli_with_encoding()
    test_tui_startup_with_encoding()
    create_encoding_safe_test_script()
    
    print("\n" + "="*60)
    print("🎯 编码安全测试完成")
    print("="*60)
    print("✅ 所有测试脚本现在应该不会出现GBK编码错误")
    print("💡 建议: 在所有测试脚本开头调用 setup_unicode_environment()")
    print("📁 已创建: encoding_safe_test.py (编码安全测试模板)")

if __name__ == "__main__":
    main()