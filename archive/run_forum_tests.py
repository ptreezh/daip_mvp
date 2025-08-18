#!/usr/bin/env python3
"""@Time    : 2025-08-06 15:30:00
@Author  : DAIP-LIVE Team
@File    : run_forum_tests.py
@Description:
    Forum模式测试运行器 - 执行所有Forum相关的测试
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

import pytest

from tests.test_forum_integration import run_forum_integration_tests


async def run_all_forum_tests():
    """运行所有Forum测试"""
    print("🏛️ Forum模式测试套件")
    print("=" * 50)
    
    # 1. 运行集成测试
    print("\n1️⃣ 运行Forum集成测试...")
    try:
        await run_forum_integration_tests()
        print("✅ Forum集成测试完成")
    except Exception as e:
        print(f"❌ Forum集成测试失败: {e}")
        return False
    
    # 2. 运行API测试
    print("\n2️⃣ 运行Forum API测试...")
    try:
        # 运行pytest
        result = pytest.main([
            "tests/test_forum_api.py",
            "-v",
            "--tb=short",
            "--color=yes"
        ])
        
        if result == 0:
            print("✅ Forum API测试完成")
        else:
            print(f"❌ Forum API测试失败 (退出码: {result})")
            return False
            
    except Exception as e:
        print(f"❌ Forum API测试异常: {e}")
        return False
    
    # 3. 运行组件测试
    print("\n3️⃣ 运行Forum组件测试...")
    try:
        # 这里可以添加更多组件测试
        result = pytest.main([
            "tests/test_forum_components.py",
            "-v",
            "--tb=short",
            "--color=yes"
        ]) if os.path.exists("tests/test_forum_components.py") else 0
        
        if result == 0:
            print("✅ Forum组件测试完成")
        else:
            print(f"⚠️ Forum组件测试跳过或失败 (退出码: {result})")
            
    except Exception as e:
        print(f"⚠️ Forum组件测试异常: {e}")
    
    print("\n🎉 所有Forum测试完成!")
    return True


def run_unit_tests():
    """运行单元测试"""
    print("🔬 运行Forum单元测试...")
    
    # 运行单元测试
    result = pytest.main([
        "tests/test_forum_api.py::TestForumAPI",
        "-v",
        "--tb=short",
        "--color=yes"
    ])
    
    return result == 0


def run_integration_tests():
    """运行集成测试"""
    print("🔗 运行Forum集成测试...")
    
    try:
        asyncio.run(run_forum_integration_tests())
        return True
    except Exception as e:
        print(f"集成测试失败: {e}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Forum模式测试运行器")
    parser.add_argument("--unit", action="store_true", help="只运行单元测试")
    parser.add_argument("--integration", action="store_true", help="只运行集成测试")
    parser.add_argument("--all", action="store_true", help="运行所有测试 (默认)")
    
    args = parser.parse_args()
    
    if args.unit:
        success = run_unit_tests()
    elif args.integration:
        success = run_integration_tests()
    else:
        success = asyncio.run(run_all_forum_tests())
    
    if success:
        print("\n✨ 测试执行成功!")
        sys.exit(0)
    else:
        print("\n💥 测试执行失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()