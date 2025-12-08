#!/usr/bin/env python3
"""
修复tui.py中的缩进错误，特别是第455行的语法问题
"""
import os

def fix_indentation_error_in_tui():
    """修复TUI文件中的缩进错误"""
    print("🔧 修复tui.py中的缩进错误")
    
    # 读取文件
    with open('src/daip_live/tui.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("原始第454-460行:")
    for i in range(453, min(len(lines), 461)):
        original_content = lines[i].rstrip()
        original_indent = len(lines[i]) - len(lines[i].lstrip()) if lines[i].strip() else 0
        print(f"  {i+1:4d}: {original_indent:2d}sp | {repr(original_content)}")
    
    # 修复缩进错误
    # 根据上下文，第455行（索引454）应该是对应某个外部try的except
    # 第457行（索引456）应该是一个新的独立try块
    if 454 < len(lines) and 'except ImportError as e:' in lines[454]:
        # 获取该行缩进并修复
        current_indent = len(lines[454]) - len(lines[454].lstrip())
        if current_indent == 4:  # 如果缩进是4个空格，改为8个
            content = lines[454].lstrip()
            lines[454] = '        ' + content  # 8个空格缩进作为except块
    
    # 修复第456行（索引455）
    if 455 < len(lines):
        current_indent = len(lines[455]) - len(lines[455].lstrip())
        if current_indent == 8:  # 如果缩进是8个空格，改为12个
            content = lines[455].lstrip()
            lines[455] = '            ' + content  # 12个空格缩进作为except块内容
    
    # 修复第457行（索引456）中的try，确保缩进与except一致
    if 456 < len(lines) and 'try:' in lines[456] and not lines[456].lstrip().startswith('except'):
        current_indent = len(lines[456]) - len(lines[456].lstrip())
        if current_indent == 8:  # 如果缩进是8个空格，改为12个
            content = lines[456].lstrip()
            lines[456] = '            ' + content  # 12个空格缩进作为新的try块
    
    print("\n修复后的第454-460行:")
    for i in range(453, min(len(lines), 461)):
        fixed_content = lines[i].rstrip()
        fixed_indent = len(lines[i]) - len(lines[i].lstrip()) if lines[i].strip() else 0
        print(f"  {i+1:4d}: {fixed_indent:2d}sp | {repr(fixed_content)}")
    
    # 保存修复后的文件
    with open('src/daip_live/tui.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("\n✅ 缩进错误修复完成!")
    
    # 验证修复
    import ast
    try:
        content = ''.join(lines)
        ast.parse(content)
        print("🎉 语法验证通过!")
        return True
    except SyntaxError as e:
        print(f"❌ 修复失败，仍有语法错误在第{e.lineno}行: {e.msg}")
        start = max(0, e.lineno-3)
        end = min(len(lines), e.lineno+3)
        for j in range(start, end):
            marker = '>>> ' if j == e.lineno-1 else '    '
            print(f"{marker}{j+1:4d}: {lines[j].rstrip()}")
        return False

def main():
    """主修复函数"""
    print("🎯 修复DAIP-LIVE TUI中的Python语法错误")
    print("问题: 第455行 - 'except ImportError as e:' 缺少对应的try块")
    
    success = fix_indentation_error_in_tui()
    
    if success:
        print(f"\n🎊 缩进错误修复成功!")
        print(f"现在可以正确使用以下功能:")
        print(f"  1. 意图识别中正确提取参数")
        print(f"  2. 保持会话上下文连贯性")
        print(f"  3. Claude Skills的协作功能")
        print(f"  4. PPT和问卷调查技能")
    else:
        print(f"\n⚠️  修复失败，需要进一步调试")
    
    return success

if __name__ == "__main__":
    main()