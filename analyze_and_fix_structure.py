"""
修复tui.py文件中Claude技能部分的缩进结构
"""
# 读取文件内容
with open('D:/DAIP/refactdoc/src/daip_live/tui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"文件总行数: {len(lines)}")

# 查找问题区域
problem_region_start = 450
problem_region_end = 470

print(f"问题区域 (第{problem_region_start+1}-{problem_region_end+1}行):")
for idx in range(problem_region_start, min(problem_region_end, len(lines))):
    line = lines[idx]
    # 计算缩进级别
    stripped = line.lstrip()
    if stripped:  # 非空行才计算缩进
        indent_spaces = len(line) - len(stripped)
        indent_levels = indent_spaces // 4  # 每4个空格为一级
    else:  # 空行使用0级
        indent_levels = 0
    
    # 显示内容
    content = repr(line.rstrip())
    print(f"{idx+1:4d}: {indent_levels}L | {content}")

print(f"\n🔍 修复缩进错误...")

# 找到并修复重复的代码块结构
# 问题在于从第455行开始有多余的重复except-try块

# 识别问题所在：
# 第450-453行已经有一个完整的try-except结构
# 但从第455行开始又有一个重复的except-try结构，这是错误的

# 修复逻辑：
# 保留第一个完整的try-except结构，删除重复的
fixed_lines = lines[:]  # 复制原内容

# 确定正确的缩进结构：找到第一个except块对应的try
first_except_block_start = -1
for i in range(445, 455):
    if i < len(fixed_lines) and 'except ImportError as e:' in fixed_lines[i] and 'Claude Skills integration not found' in fixed_lines[i]:
        first_except_block_start = i
        print(f"找到第一个except块在第{i+1}行")
        break

# 检查是否有多余的重复except块
duplicate_except_start = -1
for i in range(454, 465):
    if i < len(fixed_lines) and 'except ImportError as e:' in fixed_lines[i] and 'Claude Skills adapter manager not found' in fixed_lines[i]:
        duplicate_except_start = i
        print(f"找到重复except块在第{i+1}行")
        break

if duplicate_except_start != -1:
    # 找到重复块的结束
    block_end = duplicate_except_start
    for i in range(duplicate_except_start+1, min(duplicate_except_start+20, len(fixed_lines))):
        if 'except Exception as e:' in fixed_lines[i]:
            block_end = i
            break
    
    # 删除重复块
    print(f"删除第{duplicate_except_start+1}到第{block_end+1}行的重复代码块")
    
    # 删除重复代码块
    del fixed_lines[duplicate_except_start:block_end+1]
    
    print(f"修复后的文件总行数: {len(fixed_lines)}")

# 保存修复后的文件
with open('D:/DAIP/refactdoc/src/daip_live/tui.py.fixed', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print(f"修复后的文件已保存为 tui.py.fixed")

# 验证修复
import ast
try:
    content = ''.join(fixed_lines)
    ast.parse(content)
    print(f"✅ 修复后的文件语法检查通过!")
    
    # 备份原文件并替换
    import shutil
    shutil.move('D:/DAIP/refactdoc/src/daip_live/tui.py', 'D:/DAIP/refactdoc/src/daip_live/tui.py.backup_before_fix')
    shutil.move('D:/DAIP/refactdoc/src/daip_live/tui.py.fixed', 'D:/DAIP/refactdoc/src/daip_live/tui.py')
    print(f"✅ 原文件已备份并用修复后的文件替换")
    
except SyntaxError as e:
    print(f"❌ 修复后仍有语法错误: {e.lineno}: {e.msg}")
    # 仍然保存修复后的文件以供进一步检查
    with open('D:/DAIP/refactdoc/src/daip_live/tui.py.fixed_with_error', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    print(f"已保存到 tui.py.fixed_with_error 供进一步检查")