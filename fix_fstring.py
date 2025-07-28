#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复f-string问题
"""

from pathlib import Path
import re

def fix_fstring_issue():
    """修复f-string中的括号问题"""
    file_path = Path("src/real_demo_system/multi_role_debate_system.py")
    
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')
        
        # 修复f-string中的括号问题
        # 将 f"debate_(int(datetime.now().timestamp()))" 
        # 改为 f"debate_{int(datetime.now().timestamp())}"
        content = content.replace(
            'f"debate_(int(datetime.now().timestamp()))"',
            'f"debate_{int(datetime.now().timestamp())}"'
        )
        
        file_path.write_text(content, encoding='utf-8')
        print(f"✅ 修复了 {file_path}")
    else:
        print(f"❌ 文件不存在: {file_path}")

if __name__ == "__main__":
    fix_fstring_issue()