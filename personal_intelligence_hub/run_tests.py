#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personal Intelligence Hub - Test Runner

测试运行脚本，提供便捷的测试执行方式
"""

import sys
import subprocess
from pathlib import Path
import argparse


def run_tests(test_type="all", verbose=False, coverage=False):
    """运行测试"""
    
    # 基础pytest命令
    cmd = ["python", "-m", "pytest"]
    
    # 根据测试类型添加参数
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "slow":
        cmd.extend(["-m", "slow"])
    elif test_type != "all":
        # 运行特定测试文件
        cmd.append(f"tests/test_{test_type}.py")
    
    # 详细输出
    if verbose:
        cmd.append("-v")
    
    # 覆盖率报告
    if coverage:
        cmd.extend([
            "--cov=personal_intelligence_hub",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=70"
        ])
    
    # 执行测试
    print(f"🧪 运行测试: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Personal Intelligence Hub 测试运行器")
    
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration", "slow", "main_app", "chat_interface", 
                "personal_assistant", "transparency_monitor"],
        help="测试类型或特定测试模块"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出"
    )
    
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="生成覆盖率报告"
    )
    
    args = parser.parse_args()
    
    print("🎭 Personal Intelligence Hub 测试运行器")
    print("=" * 50)
    
    success = run_tests(args.test_type, args.verbose, args.coverage)
    
    if success:
        print("\n✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()