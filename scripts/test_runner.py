#!/usr/bin/env python3
"""
DAIP-LIVE 测试运行器

优化的测试运行脚本，支持分层测试、并行执行和智能重试。
"""

import argparse
import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional
import json
import pytest


class TestRunner:
    """测试运行器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_dir = project_root / "tests"
        self.src_dir = project_root / "src"
        self.coverage_dir = project_root / "coverage"
        self.coverage_dir.mkdir(exist_ok=True)

    def discover_tests(self, pattern: str = "**/*.py") -> List[Path]:
        """发现测试文件"""
        tests = list(self.test_dir.glob(pattern))
        return [t for t in tests if t.name.startswith("test_")]

    async def run_unit_tests(self, module: Optional[str] = None) -> bool:
        """运行单元测试"""
        print("🔬 运行单元测试")

        cmd = [
            sys.executable, "-m", "pytest",
            "tests/unit/",
            "-v",
            "--tb=short",
            "--strict-markers",
            "--disable-warnings"
        ]

        if module:
            cmd.extend(["-k", f"test_{module}"])

        # 添加覆盖率
        cmd.extend([
            "--cov=src/daip_live",
            f"--cov-report=html:{self.coverage_dir}/html",
            f"--cov-report=xml:{self.coverage_dir}/coverage.xml",
            "--cov-report=term-missing"
        ])

        result = subprocess.run(cmd, cwd=self.project_root)
        return result.returncode == 0

    async def run_integration_tests(self, module: Optional[str] = None) -> bool:
        """运行集成测试"""
        print("🔗 运行集成测试")

        cmd = [
            sys.executable, "-m", "pytest",
            "tests/integration/",
            "-v",
            "--tb=short",
            "-m", "not slow"
        ]

        if module:
            cmd.extend(["-k", f"test_{module}"])

        result = subprocess.run(cmd, cwd=self.project_root)
        return result.returncode == 0

    async def run_e2e_tests(self, module: Optional[str] = None) -> bool:
        """运行端到端测试"""
        print("🎯 运行端到端测试")

        cmd = [
            sys.executable, "-m", "pytest",
            "tests/e2e/",
            "-v",
            "--tb=long",
            "-m", "slow"
        ]

        if module:
            cmd.extend(["-k", f"test_{module}"])

        result = subprocess.run(cmd, cwd=self.project_root)
        return result.returncode == 0

    async def run_module_tests(self, module: str) -> bool:
        """运行特定模块的所有测试"""
        print(f"📦 运行模块测试: {module}")

        test_patterns = [
            f"tests/**/test_{module}*.py",
            f"tests/{module}/**/*.py"
        ]

        all_passed = True
        for pattern in test_patterns:
            cmd = [
                sys.executable, "-m", "pytest",
                pattern,
                "-v",
                "--tb=short"
            ]

            result = subprocess.run(cmd, cwd=self.project_root)
            if result.returncode != 0:
                all_passed = False

        return all_passed

    async def run_fast_tests(self) -> bool:
        """运行快速测试（跳过慢速测试）"""
        print("⚡ 运行快速测试")

        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "-m", "not slow and not integration and not e2e"
        ]

        result = subprocess.run(cmd, cwd=self.project_root)
        return result.returncode == 0

    async def run_regression_tests(self) -> bool:
        """运行回归测试"""
        print("🔄 运行回归测试")

        cmd = [
            sys.executable, "-m", "pytest",
            "tests/regression/",
            "-v",
            "--tb=long"
        ]

        result = subprocess.run(cmd, cwd=self.project_root)
        return result.returncode == 0

    def generate_test_report(self, results: Dict[str, bool]):
        """生成测试报告"""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": results,
            "summary": {
                "total": len(results),
                "passed": sum(results.values()),
                "failed": len(results) - sum(results.values())
            }
        }

        report_file = self.coverage_dir / "test_report.json"
        report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))

        print(f"📊 测试报告已生成: {report_file}")
        self.print_summary(report["summary"])

    def print_summary(self, summary: Dict[str, int]):
        """打印测试摘要"""
        print("\n" + "="*50)
        print("📊 测试摘要")
        print("="*50)
        print(f"总计: {summary['total']}")
        print(f"通过: {summary['passed']} ✅")
        print(f"失败: {summary['failed']} ❌")

        if summary['failed'] > 0:
            success_rate = (summary['passed'] / summary['total']) * 100
            print(f"成功率: {success_rate:.1f}%")
        print("="*50)

    async def run_with_retry(self, test_func, max_retries: int = 2) -> bool:
        """带重试的测试运行"""
        for attempt in range(max_retries + 1):
            try:
                result = await test_func()
                if result:
                    return True
                elif attempt < max_retries:
                    print(f"⚠️  测试失败，正在重试 ({attempt + 1}/{max_retries})")
                    await asyncio.sleep(2 ** attempt)  # 指数退避
            except Exception as e:
                print(f"❌ 测试异常: {e}")
                if attempt < max_retries:
                    print(f"🔄 正在重试 ({attempt + 1}/{max_retries})")
                    await asyncio.sleep(2 ** attempt)
        return False


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="DAIP-LIVE 测试运行器")
    parser.add_argument("command", choices=[
        "unit", "integration", "e2e", "module", "fast", "regression", "all"
    ], help="测试类型")
    parser.add_argument("--module", help="指定模块名称")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--no-retry", action="store_true", help="禁用重试")
    parser.add_argument("--parallel", action="store_true", help="并行执行")

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    runner = TestRunner(project_root)

    enable_retry = not args.no_retry
    results = {}

    if args.command == "unit":
        if enable_retry:
            results["unit"] = await runner.run_with_retry(
                lambda: runner.run_unit_tests(args.module)
            )
        else:
            results["unit"] = await runner.run_unit_tests(args.module)

    elif args.command == "integration":
        if enable_retry:
            results["integration"] = await runner.run_with_retry(
                lambda: runner.run_integration_tests(args.module)
            )
        else:
            results["integration"] = await runner.run_integration_tests(args.module)

    elif args.command == "e2e":
        if enable_retry:
            results["e2e"] = await runner.run_with_retry(
                lambda: runner.run_e2e_tests(args.module)
            )
        else:
            results["e2e"] = await runner.run_e2e_tests(args.module)

    elif args.command == "module":
        if not args.module:
            print("❌ 运行模块测试需要指定 --module 参数")
            sys.exit(1)

        if enable_retry:
            results[f"module_{args.module}"] = await runner.run_with_retry(
                lambda: runner.run_module_tests(args.module)
            )
        else:
            results[f"module_{args.module}"] = await runner.run_module_tests(args.module)

    elif args.command == "fast":
        if enable_retry:
            results["fast"] = await runner.run_with_retry(runner.run_fast_tests)
        else:
            results["fast"] = await runner.run_fast_tests()

    elif args.command == "regression":
        if enable_retry:
            results["regression"] = await runner.run_with_retry(runner.run_regression_tests)
        else:
            results["regression"] = await runner.run_regression_tests()

    elif args.command == "all":
        if args.module:
            print("运行指定模块的所有测试")
            if enable_retry:
                results[f"unit_{args.module}"] = await runner.run_with_retry(
                    lambda: runner.run_unit_tests(args.module)
                )
                results[f"integration_{args.module}"] = await runner.run_with_retry(
                    lambda: runner.run_integration_tests(args.module)
                )
            else:
                results[f"unit_{args.module}"] = await runner.run_unit_tests(args.module)
                results[f"integration_{args.module}"] = await runner.run_integration_tests(args.module)
        else:
            print("运行所有测试")
            if enable_retry:
                results["unit"] = await runner.run_with_retry(runner.run_unit_tests)
                results["integration"] = await runner.run_with_retry(runner.run_integration_tests)
                results["regression"] = await runner.run_with_retry(runner.run_regression_tests)
            else:
                results["unit"] = await runner.run_unit_tests()
                results["integration"] = await runner.run_integration_tests()
                results["regression"] = await runner.run_regression_tests()

    # 生成测试报告
    runner.generate_test_report(results)

    # 根据结果设置退出码
    if not all(results.values()):
        print("\n❌ 有测试失败")
        sys.exit(1)
    else:
        print("\n✅ 所有测试通过")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())