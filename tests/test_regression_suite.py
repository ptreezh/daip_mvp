"""
全面回归测试套件
运行所有已实现的TDD测试以验证系统完整性
"""

import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始运行全面回归测试...")
    print("=" * 60)
    
    # 测试文件列表
    test_files = [
        "tests/test_debate_module.py",
        "tests/test_wiki_module.py", 
        "tests/test_claude_skills.py",
        "tests/test_knowledge_base.py",
        "tests/test_intent_recognition.py"
    ]
    
    all_tests_passed = True
    results = []
    
    for test_file in test_files:
        test_path = project_root / test_file
        if test_path.exists():
            print(f"\n运行测试: {test_file}")
            print("-" * 40)
            
            # 执行pytest
            exit_code = pytest.main([
                str(test_path),
                "-v",  # 详细输出
                "--tb=short"  # 简短的回溯
            ])
            
            if exit_code == 0:
                print(f"✅ {test_file} - 全部通过")
                results.append((test_file, True, "全部通过"))
            else:
                print(f"❌ {test_file} - 存在失败")
                results.append((test_file, False, "存在失败"))
                all_tests_passed = False
        else:
            print(f"⚠️  跳过测试: {test_file} (文件不存在)")
            results.append((test_file, None, "文件不存在"))
    
    # 输出汇总
    print("\n" + "=" * 60)
    print("回归测试汇总报告")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed, _ in results if passed is True)
    failed_count = sum(1 for _, passed, _ in results if passed is False)
    missing_count = sum(1 for _, passed, _ in results if passed is None)
    
    for test_file, passed, status in results:
        status_icon = "✅" if passed else "❌" if passed is False else "⚠️ "
        print(f"{status_icon} {test_file:<30} {status}")
    
    print(f"\n总计: {len(results)} 个测试模块")
    print(f"通过: {passed_count}")
    print(f"失败: {failed_count}")
    print(f"缺失: {missing_count}")
    
    if all_tests_passed:
        print("\n🎉 所有回归测试均已通过!")
        return True
    else:
        print(f"\n⚠️  有 {failed_count} 个测试模块存在失败")
        return False

def run_unit_tests_only():
    """仅运行单元测试"""
    print("运行单元测试...")
    # 这里可以添加特定的单元测试运行逻辑
    
def run_integration_tests_only():
    """仅运行集成测试"""
    print("运行集成测试...")
    # 这里可以添加特定的集成测试运行逻辑

def run_performance_tests():
    """运行性能相关测试"""
    print("运行性能测试...")
    # 这里可以添加性能测试逻辑

def main():
    """主函数"""
    try:
        # 运行所有回归测试
        all_passed = run_all_tests()
        
        # 根据测试结果返回适当的退出码
        if all_passed:
            print("\n✅ 回归测试整体通过")
            return 0
        else:
            print("\n❌ 回归测试存在失败")
            return 1
            
    except Exception as e:
        print(f"❌ 运行回归测试时发生异常: {e}")
        import traceback
        traceback.print_exc()
        return 2

# 额外的验证函数
def validate_test_coverage():
    """验证测试覆盖范围"""
    print("\n验证测试覆盖范围...")
    
    # 检查主要模块是否都有对应的测试
    modules_to_test = [
        ("src/daip_live/debate_module", "tests/test_debate_module.py"),
        ("src/daip_live/wiki", "tests/test_wiki_module.py"),
        ("src/daip_live/skills", "tests/test_claude_skills.py"),
        ("src/daip_live/knowledge", "tests/test_knowledge_base.py"),
        ("src/daip_live/intent_recognition", "tests/test_intent_recognition.py")
    ]
    
    print("模块测试覆盖情况:")
    for module_path, test_path in modules_to_test:
        module_exists = (project_root / module_path).exists()
        test_exists = (project_root / test_path).exists()
        
        status = "✅" if test_exists else "❌"
        print(f"{status} {module_path:<30} -> {test_path}")
    
    return all((project_root / test_path).exists() for _, test_path in modules_to_test)

def detailed_test_report():
    """生成详细测试报告"""
    print("\n生成详细测试报告...")
    
    # 运行pytest并生成详细报告
    import subprocess
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as report_file:
        report_path = report_file.name
    
    # 尝试生成HTML报告
    try:
        subprocess.run([
            sys.executable, '-m', 'pytest',
            'tests/',
            f'--html={report_path}',
            '--self-contained-html',
            '-v'
        ], check=True, capture_output=True, text=True)
        print(f"详细HTML报告已生成: {report_path}")
    except subprocess.CalledProcessError as e:
        print(f"生成HTML报告时出错: {e}")
        print("尝试直接运行pytest...")
        subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'])
    
    # 也生成JUnit XML报告用于CI/CD
    try:
        subprocess.run([
            sys.executable, '-m', 'pytest',
            'tests/',
            '--junitxml=test-results.xml',
            '-v'
        ], check=True)
        print("JUnit XML报告已生成: test-results.xml")
    except subprocess.CalledProcessError as e:
        print(f"生成JUnit报告时出错: {e}")

if __name__ == "__main__":
    # 首先验证测试覆盖范围
    coverage_valid = validate_test_coverage()
    if not coverage_valid:
        print("⚠️  某些模块可能缺少对应的测试文件")
    
    # 运行详细测试报告生成
    detailed_test_report()
    
    # 运行主要回归测试
    exit_code = main()
    
    # 根据结果决定退出码
    sys.exit(exit_code)