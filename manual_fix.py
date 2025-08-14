#!/usr/bin/env python3
"""手动修复最后的语法错误
"""

from pathlib import Path


def manual_fix():
    """手动修复最后的语法错误"""
    file_path = Path("src/real_demo_system/multi_role_debate_system.py")

    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')

        # 直接替换问题行
        old_line = '        debate_id = f"debate_(int(datetime.now().timestamp()))"'
        new_line = '        debate_id = f"debate_{int(datetime.now().timestamp())}"'

        if old_line in content:
            content = content.replace(old_line, new_line)
            print("✅ 找到并修复了问题行")
        else:
            print("❌ 未找到问题行，尝试其他方式")
            # 尝试其他可能的格式
            variations = [
                'f"debate_(int(datetime.now().timestamp()))"',
                'f"debate_({int(datetime.now().timestamp())})"',
                'f"debate_( int(datetime.now().timestamp()) )"'
            ]

            for var in variations:
                if var in content:
                    content = content.replace(var, 'f"debate_{int(datetime.now().timestamp())}"')
                    print(f"✅ 修复了变体: {var}")
                    break

        file_path.write_text(content, encoding='utf-8')
        print(f"✅ 文件已保存: {file_path}")
    else:
        print(f"❌ 文件不存在: {file_path}")

if __name__ == "__main__":
    manual_fix()
