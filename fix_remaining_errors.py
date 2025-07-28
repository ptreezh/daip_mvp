#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复剩余的语法错误
"""

import re
from pathlib import Path


def fix_multi_role_debate_system():
    """修复multi_role_debate_system.py的问题"""
    file_path = Path("src/real_demo_system/multi_role_debate_system.py")
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')
        
        # 修复f-string中的括号问题
        content = re.sub(r'f"debate_\(int\(datetime\.now\(\)\.timestamp\(\)\)\)"', 
                        'f"debate_{int(datetime.now().timestamp())}"', content)
        
        # 修复错误的括号
        content = re.sub(r'cognitive_profiles = \(\}', 'cognitive_profiles = {}', content)
        
        file_path.write_text(content, encoding='utf-8')
        print(f"✅ 修复了 {file_path}")


def fix_sskg_storage_adapters():
    """修复sskg_storage_adapters.py的问题"""
    file_path = Path("src/core_services/sskg_storage_adapters.py")
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')
        
        # 查找并修复第794行附近的语法错误
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if i == 793:  # 第794行 (0-based index)
                # 检查是否有语法错误
                if line.strip() and not line.strip().startswith('#'):
                    # 修复常见的语法错误
                    if line.endswith('    '):
                        lines[i] = line.rstrip()
                    elif ':' in line and not line.strip().endswith(':'):
                        if 'def ' in line or 'class ' in line:
                            lines[i] = line.rstrip() + ':'
        
        file_path.write_text('\n'.join(lines), encoding='utf-8')
        print(f"✅ 修复了 {file_path}")


def fix_task_context_optimizer():
    """修复task_context_optimizer.py的问题"""
    file_path = Path("src/core_services/task_context_optimizer.py")
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')
        
        # 查找并修复第358行附近的缩进问题
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if i == 357:  # 第358行 (0-based index)
                # 检查缩进
                if line.strip() and not line.startswith('    ') and not line.startswith('def '):
                    # 如果是类方法，应该有4个空格缩进
                    if 'def ' in line:
                        lines[i] = '    ' + line.strip()
        
        file_path.write_text('\n'.join(lines), encoding='utf-8')
        print(f"✅ 修复了 {file_path}")


def main():
    """主函数"""
    print("🔧 修复剩余的语法错误...")
    
    fix_multi_role_debate_system()
    fix_sskg_storage_adapters()
    fix_task_context_optimizer()
    
    print("✅ 剩余语法错误修复完成！")


if __name__ == "__main__":
    main()