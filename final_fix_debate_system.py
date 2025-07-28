#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彻底修复multi_role_debate_system.py的问题
"""

from pathlib import Path
import re

def fix_debate_system():
    """彻底修复辩论系统文件"""
    file_path = Path("src/real_demo_system/multi_role_debate_system.py")
    
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')
        
        # 修复所有f-string中的括号问题
        content = re.sub(r'f"debate_\(int\(datetime\.now\(\)\.timestamp\(\)\)\)"', 
                        'f"debate_{int(datetime.now().timestamp())}"', content)
        
        # 修复重复的行
        lines = content.split('\n')
        fixed_lines = []
        prev_line = ""
        
        for line in lines:
            # 跳过重复的行
            if line.strip() == prev_line.strip() and line.strip():
                continue
            
            # 修复特定的语法错误
            if 'debate_session = (' in line:
                line = line.replace('debate_session = (', 'debate_session = {')
            
            if '"debate_id": debate_id,' in line and line.count('"debate_id": debate_id,') > 1:
                line = '"debate_id": debate_id,'
            
            # 修复括号不匹配
            if line.strip().startswith('"') and line.strip().endswith(',') and ':' in line:
                # 这是字典的一行，确保格式正确
                pass
            
            fixed_lines.append(line)
            prev_line = line
        
        # 重新组合内容
        content = '\n'.join(fixed_lines)
        
        # 修复其他语法错误
        content = content.replace('cognitive_profiles = (}', 'cognitive_profiles = {}')
        content = content.replace('debate_session = (', 'debate_session = {')
        content = content.replace('round_result = (', 'round_result = {')
        
        # 确保所有的字典定义正确
        content = re.sub(r'= \(\s*"', '= {\n            "', content)
        content = re.sub(r'}\s*\)', '}', content)
        
        file_path.write_text(content, encoding='utf-8')
        print(f"✅ 彻底修复了 {file_path}")
    else:
        print(f"❌ 文件不存在: {file_path}")

if __name__ == "__main__":
    fix_debate_system()