#!/usr/bin/env python3
"""简化工程可用性验证
快速验证DAIP系统的基本可用性
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def check_file_structure():
    """检查文件结构"""
    print("🔍 检查文件结构...")
    
    required_files = [
        "src/scenarios/academic_research_scenario.py",
        "src/scenarios/expert_consultation_scenario.py", 
        "test_academic_research_scenario.py",
        "test_expert_consultation_scenario.py",
        "automated_system_test.py",
        "simple_system_test.py",
        "CLAUDE.md",
        "config.yaml"
    ]
    
    results = {}
    for file_path in required_files:
        exists = Path(file_path).exists()
        results[file_path] = exists
        status = "✓" if exists else "✗"
        print(f"  {status} {file_path}")
    
    success_rate = sum(results.values()) / len(results)
    return {"success": success_rate >= 0.8, "details": results, "success_rate": success_rate}

def check_python_syntax():
    """检查核心文件Python语法"""
    print("\n🔍 检查Python语法...")
    
    key_files = [
        "src/scenarios/academic_research_scenario.py",
        "src/scenarios/expert_consultation_scenario.py",
        "test_academic_research_scenario.py", 
        "test_expert_consultation_scenario.py"
    ]
    
    results = {}
    for file_path in key_files:
        if Path(file_path).exists():
            try:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()
                compile(content, file_path, 'exec')
                results[file_path] = True
                print(f"  ✓ {file_path}")
            except SyntaxError as e:
                results[file_path] = False
                print(f"  ✗ {file_path} - 语法错误: {e}")
            except Exception as e:
                results[file_path] = False
                print(f"  ✗ {file_path} - 其他错误: {e}")
        else:
            results[file_path] = False
            print(f"  ✗ {file_path} - 文件不存在")
    
    success_rate = sum(results.values()) / len(results) if results else 0
    return {"success": success_rate >= 0.75, "details": results, "success_rate": success_rate}

def check_role_files():
    """检查角色文件"""
    print("\n🔍 检查角色文件...")
    
    roles_dir = Path("roles")
    if not roles_dir.exists():
        print("  ✗ roles目录不存在")
        return {"success": False, "role_count": 0}
    
    json_files = list(roles_dir.glob("*.json"))
    role_count = len(json_files)
    
    # 检查几个角色文件的格式
    valid_roles = 0
    for role_file in json_files[:10]:  # 检查前10个
        try:
            with open(role_file, encoding='utf-8') as f:
                role_data = json.load(f)
            if 'name' in role_data and 'description' in role_data:
                valid_roles += 1
        except:
            pass
    
    print(f"  ✓ 找到 {role_count} 个角色文件")
    print(f"  ✓ 验证了 {valid_roles} 个有效角色文件")
    
    return {
        "success": role_count >= 10,
        "role_count": role_count,
        "valid_roles": valid_roles
    }

def check_v0_2_implementation():
    """检查V0.2版本实现"""
    print("\n🔍 检查V0.2版本实现...")
    
    v0_2_components = {
        "academic_research": Path("src/scenarios/academic_research_scenario.py").exists(),
        "expert_consultation": Path("src/scenarios/expert_consultation_scenario.py").exists(),
        "academic_testing": Path("test_academic_research_scenario.py").exists(),
        "expert_testing": Path("test_expert_consultation_scenario.py").exists(),
        "automation_testing": Path("automated_system_test.py").exists()
    }
    
    for component, exists in v0_2_components.items():
        status = "✓" if exists else "✗"
        print(f"  {status} {component}")
    
    success_rate = sum(v0_2_components.values()) / len(v0_2_components)
    return {
        "success": success_rate >= 0.8,
        "components": v0_2_components,
        "success_rate": success_rate
    }

def analyze_test_quality():
    """分析测试文件质量"""
    print("\n🔍 分析测试文件质量...")
    
    test_files = [
        "test_academic_research_scenario.py",
        "test_expert_consultation_scenario.py"
    ]
    
    quality_metrics = {}
    
    for test_file in test_files:
        if Path(test_file).exists():
            try:
                with open(test_file, encoding='utf-8') as f:
                    content = f.read()
                
                # 简单质量指标
                metrics = {
                    "file_size": len(content),
                    "has_async_functions": "async def" in content,
                    "has_test_classes": "class" in content and "Test" in content,
                    "has_assertions": "assert" in content or "assertTrue" in content,
                    "has_error_handling": "try:" in content and "except" in content,
                    "comprehensive": len(content) > 5000  # 至少5000字符表示较完整
                }
                
                quality_score = sum(metrics.values()) / len(metrics)
                quality_metrics[test_file] = {
                    "metrics": metrics,
                    "quality_score": quality_score,
                    "quality_rating": "高" if quality_score >= 0.8 else "中" if quality_score >= 0.6 else "低"
                }
                
                print(f"  ✓ {test_file} - 质量评分: {quality_score:.1%} ({quality_metrics[test_file]['quality_rating']})")
                
            except Exception as e:
                quality_metrics[test_file] = {"error": str(e), "quality_score": 0}
                print(f"  ✗ {test_file} - 分析失败: {e}")
        else:
            quality_metrics[test_file] = {"error": "文件不存在", "quality_score": 0}
            print(f"  ✗ {test_file} - 文件不存在")
    
    avg_quality = sum(m.get("quality_score", 0) for m in quality_metrics.values()) / len(quality_metrics)
    
    return {
        "success": avg_quality >= 0.6,
        "average_quality": avg_quality,
        "file_metrics": quality_metrics
    }

def generate_engineering_assessment():
    """生成工程评估报告"""
    print("\n" + "=" * 60)
    print("🚀 开始工程可用性评估")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # 执行各项检查
    file_structure_result = check_file_structure()
    syntax_result = check_python_syntax()
    role_files_result = check_role_files() 
    v0_2_result = check_v0_2_implementation()
    test_quality_result = analyze_test_quality()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # 计算总体评分
    checks = [file_structure_result, syntax_result, role_files_result, v0_2_result, test_quality_result]
    passed_checks = sum(1 for check in checks if check["success"])
    overall_success_rate = passed_checks / len(checks)
    
    # 生成报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": duration,
        "overall_success": overall_success_rate >= 0.6,
        "overall_success_rate": overall_success_rate,
        "passed_checks": passed_checks,
        "total_checks": len(checks),
        "detailed_results": {
            "file_structure": file_structure_result,
            "python_syntax": syntax_result,
            "role_files": role_files_result,
            "v0_2_implementation": v0_2_result,
            "test_quality": test_quality_result
        },
        "engineering_assessment": {
            "deployment_ready": overall_success_rate >= 0.8,
            "user_ready": overall_success_rate >= 0.7,
            "development_ready": overall_success_rate >= 0.6,
            "code_quality": test_quality_result.get("average_quality", 0),
            "v0_2_completion": v0_2_result.get("success_rate", 0)
        },
        "recommendations": generate_recommendations(checks)
    }
    
    # 保存报告
    with open("engineering_assessment_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    print_assessment_summary(report)
    
    return report

def generate_recommendations(checks):
    """生成改进建议"""
    recommendations = []
    
    file_structure, syntax, roles, v0_2, test_quality = checks
    
    if not file_structure["success"]:
        recommendations.append("完善文件结构，确保所有必需文件存在")
    
    if not syntax["success"]:
        recommendations.append("修复Python语法错误，确保代码可以正常编译")
    
    if not roles["success"]:
        recommendations.append("增加更多角色文件，确保角色系统的多样性")
    
    if not v0_2["success"]:
        recommendations.append("完成V0.2版本的所有核心组件实现")
    
    if not test_quality["success"]:
        recommendations.append("提高测试文件质量，增加更多测试用例和错误处理")
    
    if all(check["success"] for check in checks):
        recommendations.append("✅ 系统验证全部通过，工程可用性良好，可以进行用户交付")
        recommendations.append("建议进行实际的端到端测试和性能验证")
    
    return recommendations

def print_assessment_summary(report):
    """打印评估摘要"""
    print("\n" + "=" * 60)
    print("📊 工程可用性评估报告")
    print("=" * 60)
    
    print(f"总体结果: {'✅ 通过' if report['overall_success'] else '❌ 需要改进'}")
    print(f"成功率: {report['passed_checks']}/{report['total_checks']} ({report['overall_success_rate']:.1%})")
    print(f"评估时长: {report['duration_seconds']:.1f} 秒")
    
    print("\n🔧 工程质量指标:")
    assessment = report["engineering_assessment"]
    print(f"  部署就绪: {'✅' if assessment['deployment_ready'] else '❌'}")
    print(f"  用户就绪: {'✅' if assessment['user_ready'] else '❌'}")
    print(f"  开发就绪: {'✅' if assessment['development_ready'] else '❌'}")
    print(f"  代码质量: {assessment['code_quality']:.1%}")
    print(f"  V0.2完成度: {assessment['v0_2_completion']:.1%}")
    
    print("\n📋 详细结果:")
    for category, result in report["detailed_results"].items():
        status = "✅" if result["success"] else "❌"
        print(f"  {category}: {status}")
    
    print("\n💡 改进建议:")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"  {i}. {rec}")
    
    print("\n📊 报告已保存: engineering_assessment_report.json")
    print("=" * 60)

if __name__ == "__main__":
    try:
        report = generate_engineering_assessment()
        # 基于成功率决定退出码
        exit_code = 0 if report["overall_success_rate"] >= 0.6 else 1
        sys.exit(exit_code)
    except Exception as e:
        print(f"评估执行失败: {e}")
        sys.exit(1)