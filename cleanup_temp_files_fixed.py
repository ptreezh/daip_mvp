#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理本次对话中生成的临时脚本文件
"""

import os
import sys
import shutil
from pathlib import Path

# 本次对话中生成的临时文件列表
TEMP_FILES = [
    # 任务管理相关文件
    "task_manager.py",
    "task_dashboard.py", 
    "create_testing_task_list.py",
    "create_test_task_list.py",
    "test_task_viewer.py",
    "initialize_task_system.bat",
    "initialize_task_system.sh",
    
    # 测试执行文件
    "run_uc_tests.py",
    "run_all_uc_tests.bat",
    
    # 文档文件
    "TASK_MANAGEMENT_DOCUMENTATION.md",
    "TEST_TASK_OVERVIEW.md",
    "TEST_TASK_PLAN.md",
    
    # 配置文件
    "test_config.json",
    
    # 其他临时文件
    "comprehensive_automated_testing.py",
    "three_applications_test.py",
    "quick_test.py",
    "test_runner.py",
    "cleanup_temp_files.py"
]

def cleanup_files():
    """清理临时文件"""
    project_root = Path(".")
    deleted_files = []
    failed_files = []
    
    print("开始清理临时文件...")
    print("=" * 50)
    
    for filename in TEMP_FILES:
        file_path = project_root / filename
        
        if file_path.exists():
            try:
                # 如果是目录，递归删除
                if file_path.is_dir():
                    shutil.rmtree(file_path)
                    print(f"已删除目录: {filename}")
                else:
                    file_path.unlink()
                    print(f"已删除文件: {filename}")
                
                deleted_files.append(filename)
                
            except Exception as e:
                print(f"删除失败 {filename}: {e}")
                failed_files.append(filename)
        else:
            print(f"文件不存在: {filename}")
    
    print("\n" + "=" * 50)
    print("清理结果:")
    print(f"成功删除: {len(deleted_files)} 个文件")
    print(f"删除失败: {len(failed_files)} 个文件")
    
    if failed_files:
        print(f"\n以下文件删除失败:")
        for file in failed_files:
            print(f"   - {file}")
    
    # 检查是否还有相关目录需要清理
    temp_dirs = [
        "task_data",
        "task_reports", 
        "test_task_reports",
        "test_exports",
        ".crush"
    ]
    
    print(f"\n检查临时目录...")
    for dirname in temp_dirs:
        dir_path = project_root / dirname
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"已删除目录: {dirname}/")
            except Exception as e:
                print(f"删除目录失败 {dirname}: {e}")
    
    print("\n清理完成!")

if __name__ == "__main__":
    cleanup_files()