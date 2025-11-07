#!/usr/bin/env python3
"""
DAIP-LIVE 编码问题统一解决方案
解决Windows环境下GBK编码导致的UnicodeDecodeError问题
"""

import os
import sys
import locale
import subprocess

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

def create_encoding_safe_script():
    """创建编码安全的测试脚本模板"""
    template = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编码安全的测试脚本模板
"""

import os
import sys
import locale

# 设置编码环境
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except locale.Error:
        pass

# 重新配置标准流
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')
if sys.stdin.encoding != 'utf-8':
    sys.stdin.reconfigure(encoding='utf-8')

# 你的测试代码从这里开始
if __name__ == "__main__":
    print("✅ 编码环境已配置为UTF-8")
    print(f"stdout编码: {sys.stdout.encoding}")
    print(f"stderr编码: {sys.stderr.encoding}")
    print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', '未设置')}")
'''
    
    with open('encoding_safe_template.py', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("✅ 已创建编码安全模板: encoding_safe_template.py")

def check_system_encoding():
    """检查系统编码设置"""
    print("🔍 系统编码检查:")
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

def fix_encoding_issues():
    """修复编码问题的综合方案"""
    print("🔧 应用编码修复方案...")
    
    # 1. 设置环境变量
    setup_unicode_environment()
    
    # 2. 创建编码安全模板
    create_encoding_safe_script()
    
    # 3. 显示当前编码状态
    check_system_encoding()
    
    print("\n✅ 编码修复完成！")
    print("建议在所有测试脚本开头调用 setup_unicode_environment()")

if __name__ == "__main__":
    fix_encoding_issues()