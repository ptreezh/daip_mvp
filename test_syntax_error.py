import os

# 读取文件并显示具体行
with open('src/daip_live/tui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Lines 454-458 (0-indexed as 453-457):")
for i in range(453, min(458, len(lines))):
    print(f"{i+1:4d}: {lines[i].rstrip()}")

print("\nLines 445-465 for broader context:")
for i in range(445, min(465, len(lines))):
    print(f"{i+1:4d}: {lines[i].rstrip()}")