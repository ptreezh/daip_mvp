"""
全面回归测试套件
运行所有已实现的TDD测试以验证系统完整性
"""

import sys
from pathlib import Path

import pytest

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_all_tests():
    """运行所有测试"""

    # 测试文件列表
    test_files = [
        "tests/test_debate_module.py",
        "tests/test_wiki_module.py",
        "tests/test_claude_skills.py",
        "tests/test_knowledge_base.py",
        "tests/test_intent_recognition.py",
    ]

    all_tests_passed = True
    results = []

    for test_file in test_files:
        test_path = project_root / test_file
        if test_path.exists():
            # 执行pytest
            exit_code = pytest.main(
                [
                    str(test_path),
                    "-v",  # 详细输出
                    "--tb=short",  # 简短的回溯
                ]
            )

            if exit_code == 0:
                results.append((test_file, True, "全部通过"))
            else:
                results.append((test_file, False, "存在失败"))
                all_tests_passed = False
        else:
            results.append((test_file, None, "文件不存在"))

    # 输出汇总

    sum(1 for _, passed, _ in results if passed is True)
    sum(1 for _, passed, _ in results if passed is False)
    sum(1 for _, passed, _ in results if passed is None)

    for test_file, passed, status in results:
        pass

    if all_tests_passed:
        return True
    else:
        return False


def run_unit_tests_only():
    """仅运行单元测试"""
    # 这里可以添加特定的单元测试运行逻辑


def run_integration_tests_only():
    """仅运行集成测试"""
    # 这里可以添加特定的集成测试运行逻辑


def run_performance_tests():
    """运行性能相关测试"""
    # 这里可以添加性能测试逻辑


def main():
    """主函数"""
    try:
        # 运行所有回归测试
        all_passed = run_all_tests()

        # 根据测试结果返回适当的退出码
        if all_passed:
            return 0
        else:
            return 1

    except Exception:
        import traceback

        traceback.print_exc()
        return 2


# 额外的验证函数
def validate_test_coverage():
    """验证测试覆盖范围"""

    # 检查主要模块是否都有对应的测试
    modules_to_test = [
        ("src/daip_live/debate_module", "tests/test_debate_module.py"),
        ("src/daip_live/wiki", "tests/test_wiki_module.py"),
        ("src/daip_live/skills", "tests/test_claude_skills.py"),
        ("src/daip_live/knowledge", "tests/test_knowledge_base.py"),
        ("src/daip_live/intent_recognition", "tests/test_intent_recognition.py"),
    ]

    for module_path, test_path in modules_to_test:
        (project_root / module_path).exists()
        (project_root / test_path).exists()

    return all((project_root / test_path).exists() for _, test_path in modules_to_test)


def detailed_test_report():
    """生成详细测试报告"""

    # 运行pytest并生成详细报告
    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False
    ) as report_file:
        report_path = report_file.name

    # 尝试生成HTML报告
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                f"--html={report_path}",
                "--self-contained-html",
                "-v",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])

    # 也生成JUnit XML报告用于CI/CD
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "--junitxml=test-results.xml",
                "-v",
            ],
            check=True,
        )
    except subprocess.CalledProcessError:
        pass


if __name__ == "__main__":
    # 首先验证测试覆盖范围
    coverage_valid = validate_test_coverage()
    if not coverage_valid:
        pass

    # 运行详细测试报告生成
    detailed_test_report()

    # 运行主要回归测试
    exit_code = main()

    # 根据结果决定退出码
    sys.exit(exit_code)
