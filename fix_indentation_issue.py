#!/usr/bin/env python3
"""
修复tui.py缩进问题的专用脚本
"""
import os

def fix_indentation_issue():
    with open('src/daip_live/tui.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"修复前的缩进问题:")
    print(f"第455行({lines[454].strip()}): 缩进级别 = {(len(lines[454]) - len(lines[454].lstrip()))//4 if lines[454].strip() else 0}")
    print(f"第456行({lines[455].strip()}): 缩进级别 = {(len(lines[455]) - len(lines[455].lstrip()))//4 if lines[455].strip() else 0}")
    print(f"第457行({lines[456].strip()}): 缩进级别 = {(len(lines[456]) - len(lines[456].lstrip()))//4 if lines[456].strip() else 0}")
    
    # 检查语法结构 - 第455行是except，第457行(索引456)是try，但没有匹配的缩进
    # 修复: 将第457行的缩进减少到与第455行except相同的级别，这样第456行成为其内容
    if 456 < len(lines) and lines[456].lstrip().startswith('try:'):
        # 第457行应该与第455行(except)有相同缩进级别
        indent_level_of_except = len(lines[454]) - len(lines[454].lstrip())
        content = lines[456].lstrip()
        lines[456] = ' ' * indent_level_of_except + content
    
    if 455 < len(lines):
        # 第456行应该是第455行except的内容，缩进应该比except多一层
        indent_level_of_except = len(lines[454]) - len(lines[454].lstrip())
        content = lines[455].lstrip()
        lines[455] = ' ' * (indent_level_of_except + 4) + content
    
    # 修复后续的缩进 - 确保try块内的内容正确缩进
    if 458 < len(lines):
        level_after_try = len(lines[456]) - len(lines[456].lstrip())
        for i in range(457, 465):  # 修复try块内的缩进
            if i < len(lines) and lines[i].strip():
                content = lines[i].lstrip()
                lines[i] = ' ' * (level_after_try + 4) + content
    
    print(f"\n修复后的缩进:")
    for i in range(454, min(465, len(lines))):
        indent_level = (len(lines[i]) - len(lines[i].lstrip()))//4 if lines[i].strip() else 0
        print(f"  第{i+1}行: {indent_level}级缩进 | {lines[i].rstrip()}")
    
    # 保存修复后的文件
    with open('src/daip_live/tui.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    # 验证修复
    import ast
    try:
        content = ''.join(lines)
        ast.parse(content)
        print(f"\n✅ 修复成功! 文件语法检查通过!")
        return True
    except SyntaxError as e:
        print(f"\n❌ 修复后仍有语法错误: {e.lineno}: {e.msg}")
        return False


if __name__ == "__main__":
    success = fix_indentation_issue()
    if success:
        print(f"\n🎉 tui.py文件已成功修复!")
    else:
        print(f"\n⚠️  修复失败，需要进一步检查。")