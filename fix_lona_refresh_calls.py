#!/usr/bin/env python3
"""
修复Lona框架中错误的refresh()调用

根据Lona框架的正确使用方式，UI会自动更新，不需要手动refresh
"""

import os
import re
from pathlib import Path

def fix_refresh_calls():
    """移除所有错误的refresh()调用"""
    
    frontend_dir = Path("frontend")
    
    # 需要修复的文件列表
    files_to_fix = [
        "components/chat_interface.py",
        "components/transparency_monitor.py", 
        "components/wiki_panel.py",
        "components/task_panel.py",
        "components/memory_panel.py"
    ]
    
    for file_path in files_to_fix:
        full_path = frontend_dir / file_path
        if not full_path.exists():
            print(f"⚠️ 文件不存在: {full_path}")
            continue
            
        print(f"🔧 修复文件: {full_path}")
        
        # 读取文件内容
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除 await self.refresh() 调用
        # 保留代码逻辑，只移除refresh调用
        patterns_to_fix = [
            (r'\s*await self\.refresh\(\)\s*\n', '\n'),
            (r'\s*await self\.refresh\(\)', ''),
        ]
        
        original_content = content
        for pattern, replacement in patterns_to_fix:
            content = re.sub(pattern, replacement, content)
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已修复: {full_path}")
        else:
            print(f"ℹ️ 无需修复: {full_path}")

def add_lona_compatibility_note():
    """在组件中添加Lona兼容性说明"""
    
    note = '''
# Lona框架说明:
# Lona会自动检测数据变化并更新UI，无需手动调用refresh()
# 当组件的数据属性（如self.messages）发生变化时，UI会自动重新渲染
'''
    
    chat_interface_path = Path("frontend/components/chat_interface.py")
    if chat_interface_path.exists():
        with open(chat_interface_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在文件开头添加说明（在imports之后）
        if "# Lona框架说明:" not in content:
            # 找到imports结束的位置
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith('logger = logging.getLogger'):
                    insert_pos = i + 1
                    break
            
            lines.insert(insert_pos, note)
            
            with open(chat_interface_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print(f"✅ 已添加Lona兼容性说明到: {chat_interface_path}")

if __name__ == "__main__":
    print("🔧 开始修复Lona框架refresh()调用问题...")
    fix_refresh_calls()
    add_lona_compatibility_note()
    print("✅ 修复完成！现在组件符合Lona框架的正确使用方式。")