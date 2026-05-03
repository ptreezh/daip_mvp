#!/usr/bin/env python3
"""
执行测试分析 - 直接运行分析逻辑
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
        "playwright_interaction_test.py"
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
        print(f"{filename:<40} {status} ({size:,} bytes)")
        
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
                print(f"  代码行数: {analysis['line_count']:,}")
                
            except Exception as e:
                print(f"\n❌ 分析文件 {file_info['filename']} 时出错: {str(e)}")
                file_info["error"] = str(e)
    
    # 检查Playwright脚本
    print(f"\n🐍 Playwright测试脚本分析:")
    print("-" * 40)
    
    playwright_file = base_dir / "playwright_interaction_test.py"
    if playwright_file.exists():
        try:
            with open(playwright_file, 'r', encoding='utf-8') as f:
                playwright_content = f.read()
            
            playwright_analysis = {
                "line_count": playwright_content.count('\n') + 1,
                "size_bytes": len(playwright_content),
                "has_async_functions": "async def" in playwright_content,
                "has_playwright_import": "playwright" in playwright_content,
                "has_test_functions": "test_" in playwright_content,
                "has_browser_launch": "browser" in playwright_content and "launch" in playwright_content,
                "has_six_dimension_tests": "six_dimension" in playwright_content.lower(),
                "has_error_handling": "try:" in playwright_content and "except" in playwright_content
            }
            
            print(f"  代码行数: {playwright_analysis['line_count']:,}")
            print(f"  异步函数: {'✅' if playwright_analysis['has_async_functions'] else '❌'}")
            print(f"  Playwright导入: {'✅' if playwright_analysis['has_playwright_import'] else '❌'}")
            print(f"  测试函数: {'✅' if playwright_analysis['has_test_functions'] else '❌'}")
            print(f"  浏览器启动: {'✅' if playwright_analysis['has_browser_launch'] else '❌'}")
            print(f"  六向联动测试: {'✅' if playwright_analysis['has_six_dimension_tests'] else '❌'}")
            print(f"  错误处理: {'✅' if playwright_analysis['has_error_handling'] else '❌'}")
            
            playwright_analysis["ready_to_run"] = all([
                playwright_analysis["has_async_functions"],
                playwright_analysis["has_playwright_import"],
                playwright_analysis["has_test_functions"],
                playwright_analysis["has_browser_launch"]
            ])
            
            print(f"  脚本状态: {'✅ 可运行' if playwright_analysis['ready_to_run'] else '❌ 需要修复'}")
            
        except Exception as e:
            print(f"  ❌ 分析Playwright脚本时出错: {str(e)}")
            playwright_analysis = {"error": str(e), "ready_to_run": False}
    else:
        print("  ❌ Playwright测试脚本不存在")
        playwright_analysis = {"ready_to_run": False}
    
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
        "playwright_analysis": playwright_analysis,
        "summary": {
            "total_files": len(test_files),
            "existing_files": len([r for r in results if r["exists"]]),
            "html_files_with_js": len([r for r in results if r.get("analysis", {}).get("has_javascript", False)]),
            "html_files_with_interactive": len([r for r in results if r.get("analysis", {}).get("has_interactive", False)]),
            "playwright_ready": playwright_analysis.get("ready_to_run", False)
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
    
    if playwright_analysis.get("ready_to_run", False):
        print("✅ Playwright测试脚本准备就绪")
        print("🔧 安装命令: pip install playwright")
        print("🔧 安装浏览器: playwright install chromium")
        print("🚀 运行命令: python playwright_interaction_test.py")
    else:
        print("❌ Playwright测试脚本需要修复或环境配置")
    
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
    print(f"  Playwright就绪: {'是' if test_report['summary']['playwright_ready'] else '否'}")
    
    print("\n" + "="*60)
    print("🎉 MCP Playwright综合测试环境分析完成!")
    
    return test_report

if __name__ == "__main__":
    try:
        report = analyze_test_environment()
        print("\n✅ 分析成功完成!")
    except Exception as e:
        print(f"\n❌ 分析过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()
