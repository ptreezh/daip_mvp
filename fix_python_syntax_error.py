#!/usr/bin/env python3
"""
精确修复tui.py文件中的语法错误
解决第441行的'expected an indented block after 'try' statement'错误
"""
import re


def fix_python_syntax_errors():
    """修复Python语法错误"""
    print("🔍 检查tui.py中的语法错误...")
    
    with open('src/daip_live/tui.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"文件总行数: {len(lines)}")
    
    # 找到问题区域
    print(f"\n检查第435-445行:")
    for i in range(434, min(445, len(lines))):
        content = lines[i].rstrip()
        indent_spaces = len(lines[i]) - len(lines[i].lstrip()) if lines[i].strip() else 0
        print(f"{i+1:4d}: {indent_spaces:2d}sp | {repr(content)}")
    
    # 问题分析：
    # 第441行应该是第440行（Python索引439）的try语句的异常处理
    # 但第440行的try块缺少缩进的语句体
    
    if 439 < len(lines) and 'try:' in lines[439] and lines[439].strip() == 'try:':
        print(f"\n在第440行发现未正确缩进的try块")
        
        # 找到跟在try后面的语句块（需要缩进）
        try_block_start = 439
        try_block_end = -1
        
        # 查找try块后面未正确缩进的内容
        for i in range(try_block_start + 1, min(try_block_start + 10, len(lines))):
            if lines[i].strip() and (len(lines[i]) - len(lines[i].lstrip())) == 0:  # 没有缩进但非空
                print(f"第{i+1}行没有缩进但仍为内容行: {repr(lines[i].rstrip())}")
                # 修复：将其缩进与try块相同（加4个空格）
                try_indent = len(lines[try_block_start]) - len(lines[try_block_start].lstrip())
                lines[i] = ' ' * (try_indent + 4) + lines[i].lstrip()
                print(f"  已修复第{i+1}行缩进为 {try_indent + 4} 个空格")
            elif lines[i].strip() and not lines[i].strip().startswith('except') and not lines[i].strip().startswith('finally'):
                # 检查缩进是否足够
                current_indent = len(lines[i]) - len(lines[i].lstrip())
                if current_indent < len(lines[try_block_start]) - len(lines[try_block_start].lstrip()) + 4:
                    try_indent = len(lines[try_block_start]) - len(lines[try_block_start].lstrip())
                    lines[i] = ' ' * (try_indent + 4) + lines[i].lstrip()
                    print(f"  已修复第{i+1}行缩进")
            else:
                # 如果是except或finally或空行则跳出
                break
    
    # 更仔细分析第439行（try）和第440行（应该是except）
    print(f"\n更仔细分析第440-442行:")
    for i in range(439, min(443, len(lines))):
        print(f"   {i+1:4d}: {repr(lines[i])}")
    
    # 如果第439行是try，第440行应该是缩进的语句，但很可能它被错误地缩进了
    # 修复方案：找到try块的正确缩进级别，确保后续语句正确缩进直到except
    try_line_idx = 439
    if try_line_idx < len(lines) and 'try:' in lines[try_line_idx]:
        base_indent = len(lines[try_line_idx]) - len(lines[try_line_idx].lstrip())
        print(f"   try块的基准缩进: {base_indent} 个空格")
        
        # 确保try之后的行适当缩进
        for i in range(try_line_idx + 1, len(lines)):
            if i >= len(lines):
                break
                
            line_content = lines[i].lstrip()
            if not line_content:  # 空行
                continue
                
            # 检查是否是except/else/finally语句，这些不应该缩进到try的内部
            if line_content.startswith('except ') or line_content.startswith('else:') or line_content.startswith('finally:'):
                expected_indent = base_indent  # 这些应该与try在同一缩进级别
                actual_indent = len(lines[i]) - len(lines[i].lstrip())
                
                if actual_indent != expected_indent:
                    print(f"   发现缩进不正确的语句在第{i+1}行: '{line_content}' - 原缩进{actual_indent}，应为{expected_indent}")
                    lines[i] = ' ' * expected_indent + line_content
                    print(f"   已修复为: {repr(lines[i])}")
                break
            else:
                # 这应该是try块内部的语句，需要额外4个空格的缩进
                expected_indent = base_indent + 4
                actual_indent = len(lines[i]) - len(lines[i].lstrip()) if lines[i].strip() else 0
                
                if lines[i].strip() and actual_indent < expected_indent:
                    print(f"   修复第{i+1}行缩进: '{line_content}' - 从{actual_indent}增加到{expected_indent}")
                    lines[i] = ' ' * expected_indent + line_content
                    print(f"   修复后: {repr(lines[i])}")
    
    # 现在修复文件
    print(f"\n📝 应用修复并保存...")
    with open('src/daip_live/tui.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    # 验证修复
    print(f"🔍 验证修复后的语法...")
    
    import ast
    try:
        content = ''.join(lines)
        ast.parse(content)
        print(f"✅ 语法检查通过！")
        return True
    except SyntaxError as e:
        print(f"❌ 修复后仍有语法错误: {e.lineno}: {e.msg}")
        start = max(0, e.lineno-3)
        end = min(len(lines), e.lineno+3)
        for j in range(start, end):
            marker = '>>> ' if j == e.lineno-1 else '    '
            print(f"{marker}{j+1:4d}: {lines[j].rstrip()}")
        return False


def main():
    """主修复函数"""
    print("🔧 修复DAIP-LIVE TUI Python语法错误")
    print("问题: 第441行 - expected an indented block after 'try' statement on line 439")
    
    success = fix_python_syntax_errors()
    
    if success:
        print(f"\n🎉 修复成功!")
        print(f"Python语法错误已修复，文件现在可以正确解析!")
        return True
    else:
        print(f"\n⚠️  修复可能未完成，请再次检查错误")
        return False


if __name__ == "__main__":
    main()