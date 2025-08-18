#!/usr/bin/env python3
"""
简单的语法检查脚本
"""

import ast
import sys
import os

def check_file_syntax(file_path):
    """检查文件语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试解析AST
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax Error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """主函数"""
    files_to_check = [
        'frontend/components/debate_stream.py',
        'frontend/components/consensus_visualizer.py'
    ]
    
    print("=== Syntax Check Results ===")
    
    all_ok = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            is_ok, error = check_file_syntax(file_path)
            if is_ok:
                print(f"✓ {file_path}: OK")
            else:
                print(f"✗ {file_path}: {error}")
                all_ok = False
        else:
            print(f"? {file_path}: File not found")
            all_ok = False
    
    print(f"\n=== Summary ===")
    if all_ok:
        print("✓ All files have valid syntax")
        return 0
    else:
        print("✗ Some files have syntax errors")
        return 1

if __name__ == "__main__":
    sys.exit(main())