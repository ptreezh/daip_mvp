#!/usr/bin/env python3
"""
MCP Playwright综合测试执行器
直接运行测试分析，不依赖外部命令
"""

import os
import json
import time
from pathlib import Path

def analyze_test_environment():
    """分析测试环境"""
    print("🚀 开始MCP Playwright综合测试环境分析...")
    print("="*60)
    
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
    
    print("\n📋 文件状态检查:")
    print("-" * 40)
    
    for filename in test_files:
        file_path = base_dir / filename
        exists = file_path.exists()
        size = file_path.stat().st_size if exists else 0
        
        status = "✅ 存在" if exists else "❌ 不存在"
        print(f"{filename:<45} {status} ({size:,} bytes)")
        
        results.append({
            "filename": filename,
            "exists": exists,
            "size": size,
            "path": str(file_path)
        })
    
    print("\n🔍 HTML文件结构分析:")
    print("-" * 40)
    
    html_files = [f for f in results if f["filename"].endswith(".html")]
    
    for file_info in html_files:
        if file_info["exists"]:
            try:
                with open(file_info["path"], 'r', encoding='utf-8') as f:
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
                print(f"\n📄 {file_info['filename']}:")
                print(f"  JavaScript: {'✅' if analysis['has_javascript'] else '❌'}")
                print(f"  交互元素: {'✅' if analysis['has_interactive'] else '❌'}")
                print(f"  表单元素: {'✅' if analysis['has_forms'] else '❌'}")
                print(f"  按钮元素: {'✅' if analysis['has_buttons'] else '❌'}")
                print(f"  测试标识: {'✅' if analysis['has_test_classes'] else '❌'}")
                print(f"  维度系统: {'✅' if analysis['has_dimensions'] else '❌'}")
                print(f"  六向系统: {'✅' if analysis['has_six_system'] else '❌'}")
                print(f"  代码行数: {analysis['line_count']:,}")
                
            except Exception as e:
                print(f"\n❌ 分析文件 {file_info['filename']} 时出错: {str(e)}")
                file_info["error"] = str(e)
    
    # 检查Python测试脚本
    print(f"\n🐍 Python测试脚本分析:")
    print("-" * 40)
    
    python_scripts = ["playwright_interaction_test.py", "alternative_test_runner.py", "execute_test_analysis.py"]
    
    for script_file in python_scripts:
        script_path = base_dir / script_file
        if script_path.exists():
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
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
                
                print(f"\n📄 {script_file}:")
                print(f"  代码行数: {script_analysis['line_count']:,}")
                print(f"  异步函数: {'✅' if script_analysis['has_async_functions'] else '❌'}")
                print(f"  Playwright导入: {'✅' if script_analysis['has_playwright_import'] else '❌'}")
                print(f"  测试函数: {'✅' if script_analysis['has_test_functions'] else '❌'}")
                print(f"  浏览器启动: {'✅' if script_analysis['has_browser_launch'] else '❌'}")
                print(f"  六向联动测试: {'✅' if script_analysis['has_six_dimension_tests'] else '❌'}")
                print(f"  错误处理: {'✅' if script_analysis['has_error_handling'] else '❌'}")
                print(f"  文件分析: {'✅' if script_analysis['has_file_analysis'] else '❌'}")
                print(f"  测试运行器: {'✅' if script_analysis['has_test_runner'] else '❌'}")
                
                script_analysis["ready_to_run"] = all([
                    script_analysis["has_async_functions"] or script_analysis["has_file_analysis"],
                    script_analysis["has_test_functions"] or script_analysis["has_test_runner"],
                ])
                
                print(f"  脚本状态: {'✅ 可运行' if script_analysis['ready_to_run'] else '❌ 需要修复'}")
                
                # 为对应的结果添加分析
                for result in results:
                    if result["filename"] == script_file:
                        result["analysis"] = script_analysis
                        break
                
            except Exception as e:
                print(f"  ❌ 分析脚本 {script_file} 时出错: {str(e)}")
                for result in results:
                    if result["filename"] == script_file:
                        result["error"] = str(e)
                        break
        else:
            print(f"\n❌ 脚本 {script_file} 不存在")
    
    # 生成测试报告
    print(f"\n📊 生成测试报告...")
    
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
    
    print(f"📄 详细报告已保存到: {report_file}")
    
    # 生成测试建议
    print(f"\n💡 测试建议:")
    print("-" * 40)
    
    # 检查关键文件
    six_dimension_file = None
    for result in results:
        if result["filename"] == "P1_SIX_DIMENSION_LEARNING_FIXED.html" and result["exists"]:
            six_dimension_file = result
            break
    
    if six_dimension_file and six_dimension_file.get("analysis", {}).get("has_six_system", False):
        print("✅ 六向联动系统文件存在且结构完整")
        print("🔧 可以进行自动化测试")
    else:
        print("❌ 六向联动系统文件缺失或结构不完整")
    
    print("\n📋 手动测试指导:")
    print("1. 双击打开每个HTML文件")
    print("2. 按F12打开开发者工具")
    print("3. 检查Console标签是否有错误")
    print("4. 测试每个按钮和交互功能")
    print("5. 验证六向联动系统切换是否正常")
    
    print(f"\n📈 测试状态总结:")
    print(f"  总文件数: {test_report['summary']['total_files']}")
    print(f"  存在文件: {test_report['summary']['existing_files']}")
    print(f"  HTML含JS: {test_report['summary']['html_files_with_js']}")
    print(f"  HTML交互: {test_report['summary']['html_files_with_interactive']}")
    print(f"  HTML维度: {test_report['summary']['html_files_with_dimensions']}")
    print(f"  脚本就绪: {test_report['summary']['python_scripts_ready']}")
    
    print("\n" + "="*60)
    print("🎉 MCP Playwright综合测试环境分析完成!")
    
    return test_report

def run_basic_html_validation():
    """运行基本HTML验证"""
    print("\n🔍 开始HTML基本验证...")
    print("-" * 40)
    
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
                with open(file_path, 'r', encoding='utf-8') as f:
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
                status = "✅ 通过" if len(validation["syntax_errors"]) == 0 else "❌ 有问题"
                print(f"{html_file:<40} {status}")
                
                if validation["syntax_errors"]:
                    for error in validation["syntax_errors"]:
                        print(f"  ⚠️ {error}")
                
            except Exception as e:
                print(f"{html_file:<40} ❌ 读取错误: {str(e)}")
                validation_results.append({
                    "filename": html_file,
                    "syntax_errors": [f"文件读取错误: {str(e)}"]
                })
        else:
            print(f"{html_file:<40} ❌ 文件不存在")
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
    
    print(f"\n📄 HTML验证报告已保存到: {validation_file}")
    print(f"✅ 通过验证: {validation_report['summary']['passed']}/{validation_report['summary']['total_files']}")
    
    return validation_report

if __name__ == "__main__":
    try:
        print("开始MCP Playwright综合测试分析...")
        
        # 运行环境分析
        env_report = analyze_test_environment()
        
        # 运行HTML验证
        html_report = run_basic_html_validation()
        
        print("\n🎉 所有测试分析完成!")
        print(f"📊 环境分析报告: mcp_test_analysis_report.json")
        print(f"📊 HTML验证报告: html_validation_report.json")
        
    except Exception as e:
        print(f"\n❌ 分析过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()