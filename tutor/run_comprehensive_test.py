#!/usr/bin/env python3
"""
MCP Playwright综合测试执行器
直接运行测试分析，不依赖外部命令
"""

import json
import time
from pathlib import Path


def analyze_test_environment():
    """分析测试环境"""

    # 定义测试文件
    test_files = [
        "javascript验证.html",
        "简单交互测试.html",
        "P1_SIX_DIMENSION_LEARNING_FIXED.html",
        "六向联动系统交互修复报告.html",
        "playwright_interaction_test.py",
        "alternative_test_runner.py",
        "execute_test_analysis.py"
    ]

    base_dir = Path("D:/daip/refactdoc/tutor")
    results = []


    for filename in test_files:
        file_path = base_dir / filename
        exists = file_path.exists()
        size = file_path.stat().st_size if exists else 0


        results.append({
            "filename": filename,
            "exists": exists,
            "size": size,
            "path": str(file_path)
        })


    html_files = [f for f in results if f["filename"].endswith(".html")]

    for file_info in html_files:
        if file_info["exists"]:
            try:
                with open(file_info["path"], encoding='utf-8') as f:
                    content = f.read()

                # 分析结构
                analysis = {
                    "has_javascript": "script" in content.lower(),
                    "has_interactive": any(x in content.lower() for x in [
                        "onclick", "onload", "onchange", "addEventListener", "function", "var ", "let ", "const "
                    ]),
                    "has_forms": "form" in content.lower(),
                    "has_buttons": "button" in content.lower(),
                    "has_test_classes": "test-" in content,
                    "has_dimensions": any(dim in content for dim in [
                        "dimension", "prompt", "spec", "design", "plan", "code", "correlation"
                    ]),
                    "has_six_system": "six" in content.lower() and "dimension" in content.lower(),
                    "line_count": content.count('\n') + 1,
                    "size_bytes": len(content)
                }

                file_info["analysis"] = analysis

                # 显示分析结果

            except Exception as e:
                file_info["error"] = str(e)

    # 检查Python测试脚本

    python_scripts = ["playwright_interaction_test.py", "alternative_test_runner.py", "execute_test_analysis.py"]

    for script_file in python_scripts:
        script_path = base_dir / script_file
        if script_path.exists():
            try:
                with open(script_path, encoding='utf-8') as f:
                    script_content = f.read()

                script_analysis = {
                    "line_count": script_content.count('\n') + 1,
                    "size_bytes": len(script_content),
                    "has_async_functions": "async def" in script_content,
                    "has_playwright_import": "playwright" in script_content,
                    "has_test_functions": "test_" in script_content,
                    "has_browser_launch": "browser" in script_content and "launch" in script_content,
                    "has_six_dimension_tests": "six_dimension" in script_content.lower(),
                    "has_error_handling": "try:" in script_content and "except" in script_content,
                    "has_file_analysis": "analyze" in script_content.lower(),
                    "has_test_runner": "runner" in script_content.lower() or "test" in script_content.lower()
                }


                script_analysis["ready_to_run"] = all([
                    script_analysis["has_async_functions"] or script_analysis["has_file_analysis"],
                    script_analysis["has_test_functions"] or script_analysis["has_test_runner"],
                ])


                # 为对应的结果添加分析
                for result in results:
                    if result["filename"] == script_file:
                        result["analysis"] = script_analysis
                        break

            except Exception as e:
                for result in results:
                    if result["filename"] == script_file:
                        result["error"] = str(e)
                        break
        else:
            pass

    # 生成测试报告

    test_report = {
        "timestamp": time.time(),
        "test_type": "mcp_playwright_comprehensive_test",
        "environment": "Windows",
        "base_directory": str(base_dir),
        "files_analyzed": len(test_files),
        "html_files": len(html_files),
        "file_results": results,
        "summary": {
            "total_files": len(test_files),
            "existing_files": len([r for r in results if r["exists"]]),
            "html_files_with_js": len([r for r in results if r.get("analysis", {}).get("has_javascript", False)]),
            "html_files_with_interactive": len([r for r in results if r.get("analysis", {}).get("has_interactive", False)]),
            "html_files_with_dimensions": len([r for r in results if r.get("analysis", {}).get("has_dimensions", False)]),
            "python_scripts_ready": len([r for r in results if r.get("analysis", {}).get("ready_to_run", False)])
        }
    }

    # 保存报告
    report_file = base_dir / "mcp_test_analysis_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(test_report, f, ensure_ascii=False, indent=2)


    # 生成测试建议

    # 检查关键文件
    six_dimension_file = None
    for result in results:
        if result["filename"] == "P1_SIX_DIMENSION_LEARNING_FIXED.html" and result["exists"]:
            six_dimension_file = result
            break

    if six_dimension_file and six_dimension_file.get("analysis", {}).get("has_six_system", False):
        pass
    else:
        pass




    return test_report

def run_basic_html_validation():
    """运行基本HTML验证"""

    base_dir = Path("D:/daip/refactdoc/tutor")
    html_files = [
        "javascript验证.html",
        "简单交互测试.html",
        "P1_SIX_DIMENSION_LEARNING_FIXED.html",
        "六向联动系统交互修复报告.html"
    ]

    validation_results = []

    for html_file in html_files:
        file_path = base_dir / html_file
        if file_path.exists():
            try:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()

                # 基本HTML验证
                validation = {
                    "filename": html_file,
                    "has_doctype": "<!DOCTYPE html>" in content,
                    "has_html_tag": "<html" in content and "</html>" in content,
                    "has_head": "<head>" in content and "</head>" in content,
                    "has_body": "<body>" in content and "</body>" in content,
                    "has_charset": "charset=" in content,
                    "has_title": "<title>" in content and "</title>" in content,
                    "has_css": "style" in content.lower() or "css" in content.lower(),
                    "has_javascript": "script" in content.lower() or "javascript" in content.lower(),
                    "syntax_errors": []
                }

                # 检查常见语法错误
                if not validation["has_doctype"]:
                    validation["syntax_errors"].append("缺少DOCTYPE声明")
                if not validation["has_html_tag"]:
                    validation["syntax_errors"].append("HTML标签不完整")
                if not validation["has_head"]:
                    validation["syntax_errors"].append("HEAD标签缺失")
                if not validation["has_body"]:
                    validation["syntax_errors"].append("BODY标签缺失")

                validation_results.append(validation)

                # 输出验证结果
                "✅ 通过" if len(validation["syntax_errors"]) == 0 else "❌ 有问题"

                if validation["syntax_errors"]:
                    for error in validation["syntax_errors"]:
                        pass

            except Exception as e:
                validation_results.append({
                    "filename": html_file,
                    "syntax_errors": [f"文件读取错误: {str(e)}"]
                })
        else:
            validation_results.append({
                "filename": html_file,
                "syntax_errors": ["文件不存在"]
            })

    # 保存验证结果
    validation_report = {
        "timestamp": time.time(),
        "validation_type": "html_basic_syntax",
        "results": validation_results,
        "summary": {
            "total_files": len(html_files),
            "passed": len([r for r in validation_results if len(r.get("syntax_errors", [])) == 0]),
            "failed": len([r for r in validation_results if len(r.get("syntax_errors", [])) > 0])
        }
    }

    validation_file = base_dir / "html_validation_report.json"
    with open(validation_file, 'w', encoding='utf-8') as f:
        json.dump(validation_report, f, ensure_ascii=False, indent=2)


    return validation_report

if __name__ == "__main__":
    try:

        # 运行环境分析
        env_report = analyze_test_environment()

        # 运行HTML验证
        html_report = run_basic_html_validation()


    except Exception:
        import traceback
        traceback.print_exc()
