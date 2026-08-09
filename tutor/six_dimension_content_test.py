#!/usr/bin/env python3
"""
六向联动内容展示专项测试
重点检查六向联动中六个方向的具体内容展示情况
验证每个方向的数据是否正确加载和显示，并记录任何缺失或异常的展示内容
"""

import asyncio
from playwright.async_api import async_playwright
import json
import time

# 六个方向的定义
DIMENSIONS = {
    'prompt': '🤖 规范化提示词',
    'spec': '📄 规范文档',
    'design': '🎨 设文档',
    'plan': '📋 实施计划',
    'code': '💻 代码实现',
    'correlation': '🔗 关联分析'
}

async def test_six_dimension_content_display():
    """测试六向联动中六个方向的具体内容展示情况"""
    
    print("🔍 开始六向联动内容展示专项测试...")
    print("🎯 重点检查六个方向的具体内容展示情况")
    
    results = {
        "timestamp": time.time(),
        "test_name": "六向联动内容展示专项测试",
        "requirements_tested": [],
        "dimensions_tested": [],
        "content_validation": {},
        "issues_found": [],
        "summary": {}
    }
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()
        
        # 捕获控制台消息
        console_messages = []
        def handle_console(msg):
            console_messages.append({
                "type": msg.type,
                "text": msg.text
            })
            print(f"[Console {msg.type}] {msg.text}")
        
        page.on("console", handle_console)
        
        try:
            # 加载六向联动系统
            print("\n📄 加载六向联动学习系统...")
            await page.goto(f"file:///D:/daip/refactdoc/tutor/P1_SIX_DIMENSION_LEARNING_FIXED.html")
            
            # 等待页面加载完成
            await page.wait_for_load_state('networkidle')
            print("✅ 页面加载完成")
            
            # 测试的需求列表
            requirements = ['FR-001', 'FR-002', 'NFR-001', 'DP-002']
            
            for req in requirements:
                print(f"\n📝 测试需求: {req}")
                results["requirements_tested"].append(req)
                
                # 选择需求
                req_option = page.locator(f'[data-requirement="{req}"]')
                if await req_option.count() > 0:
                    await req_option.click()
                    await page.wait_for_timeout(2000)  # 等待内容加载
                    
                    # 验证六向联动视图是否显示
                    dimension_view = await page.locator('#dimension-content').is_visible()
                    if not dimension_view:
                        results["issues_found"].append(f"需求 {req}: 六向联动视图未显示")
                        continue
                    
                    # 测试每个维度的内容展示
                    for dim_key, dim_name in DIMENSIONS.items():
                        print(f"  🔍 测试维度: {dim_name} ({dim_key})")
                        results["dimensions_tested"].append(dim_key)
                        
                        # 初始化内容验证结果
                        if dim_key not in results["content_validation"]:
                            results["content_validation"][dim_key] = {
                                "total_tests": 0,
                                "passed_tests": 0,
                                "failed_tests": 0,
                                "details": []
                            }
                        
                        results["content_validation"][dim_key]["total_tests"] += 1
                        
                        # 检查维度内容元素是否存在
                        content_element = page.locator(f'#{dim_key}-content')
                        element_exists = await content_element.count() > 0
                        
                        if not element_exists:
                            issue = f"需求 {req}, 维度 {dim_key}: 内容容器元素不存在"
                            results["issues_found"].append(issue)
                            results["content_validation"][dim_key]["failed_tests"] += 1
                            results["content_validation"][dim_key]["details"].append({
                                "requirement": req,
                                "status": "FAILED",
                                "issue": "内容容器元素不存在"
                            })
                            continue
                        
                        # 获取内容文本
                        content_text = await content_element.text_content()
                        
                        # 验证内容是否为空或仅包含占位符
                        if not content_text or content_text.strip() == "" or "内容将通过JavaScript动态加载" in content_text:
                            issue = f"需求 {req}, 维度 {dim_key}: 内容为空或仅为占位符"
                            results["issues_found"].append(issue)
                            results["content_validation"][dim_key]["failed_tests"] += 1
                            results["content_validation"][dim_key]["details"].append({
                                "requirement": req,
                                "status": "FAILED",
                                "issue": "内容为空或仅为占位符",
                                "content_preview": content_text[:100] if content_text else "空内容"
                            })
                        else:
                            # 内容存在，检查是否包含预期的结构元素
                            has_section_title = await content_element.locator('.section-title').count() > 0
                            has_section_content = await content_element.locator('.section-content').count() > 0
                            
                            if has_section_title and has_section_content:
                                results["content_validation"][dim_key]["passed_tests"] += 1
                                results["content_validation"][dim_key]["details"].append({
                                    "requirement": req,
                                    "status": "PASSED",
                                    "content_length": len(content_text),
                                    "has_title": has_section_title,
                                    "has_content": has_section_content
                                })
                                print(f"    ✅ 维度 {dim_key} 内容展示正常")
                            else:
                                issue = f"需求 {req}, 维度 {dim_key}: 内容结构不完整"
                                results["issues_found"].append(issue)
                                results["content_validation"][dim_key]["failed_tests"] += 1
                                results["content_validation"][dim_key]["details"].append({
                                    "requirement": req,
                                    "status": "FAILED",
                                    "issue": "内容结构不完整",
                                    "has_title": has_section_title,
                                    "has_content": has_section_content,
                                    "content_preview": content_text[:100] if content_text else "空内容"
                                })
                    
                    # 测试六向联动功能
                    print(f"  🔄 测试六向联动功能...")
                    
                    # 点击每个维度卡片，验证联动效果
                    for dim_key, dim_name in DIMENSIONS.items():
                        dimension_card = page.locator(f'.dimension-card[data-dimension="{dim_key}"]')
                        if await dimension_card.count() > 0:
                            # 记录点击前的状态
                            before_dimension = await page.evaluate("() => currentDimension")
                            
                            # 点击维度卡片
                            await dimension_card.click()
                            await page.wait_for_timeout(1500)  # 等待联动完成
                            
                            # 验证维度是否切换
                            after_dimension = await page.evaluate("() => currentDimension")
                            if after_dimension != dim_key:
                                issue = f"需求 {req}, 点击维度 {dim_key}: 维度切换失败，期望 {dim_key}，实际 {after_dimension}"
                                results["issues_found"].append(issue)
                        
                        # 每次点击后检查所有维度内容是否更新
                        for check_dim in DIMENSIONS.keys():
                            content_element = page.locator(f'#{check_dim}-content')
                            if await content_element.count() > 0:
                                content_text = await content_element.text_content()
                                # 如果内容仍为占位符，则说明联动未生效
                                if "内容将通过JavaScript动态加载" in content_text:
                                    issue = f"需求 {req}, 维度 {check_dim}: 六向联动后内容未更新"
                                    results["issues_found"].append(issue)
                    
                    # 返回需求选择界面，测试下一个需求
                    await page.evaluate("() => window.resetView()")
                    await page.wait_for_timeout(1000)
                else:
                    issue = f"需求 {req}: 需求选择元素不存在"
                    results["issues_found"].append(issue)
            
            # 生成测试摘要
            total_tests = sum([dim_data["total_tests"] for dim_data in results["content_validation"].values()])
            passed_tests = sum([dim_data["passed_tests"] for dim_data in results["content_validation"].values()])
            failed_tests = sum([dim_data["failed_tests"] for dim_data in results["content_validation"].values()])
            
            results["summary"] = {
                "total_requirements_tested": len(results["requirements_tested"]),
                "total_dimensions_tested": len(results["dimensions_tested"]),
                "total_content_tests": total_tests,
                "passed_content_tests": passed_tests,
                "failed_content_tests": failed_tests,
                "pass_rate": round((passed_tests / total_tests * 100) if total_tests > 0 else 0, 2),
                "issues_found_count": len(results["issues_found"])
            }
            
            # 输出测试结果
            print("\n" + "="*60)
            print("📊 测试结果汇总")
            print("="*60)
            print(f"测试需求数量: {results['summary']['total_requirements_tested']}")
            print(f"测试维度数量: {results['summary']['total_dimensions_tested']}")
            print(f"内容测试总数: {results['summary']['total_content_tests']}")
            print(f"通过测试数量: {results['summary']['passed_content_tests']}")
            print(f"失败测试数量: {results['summary']['failed_content_tests']}")
            print(f"通过率: {results['summary']['pass_rate']}%")
            print(f"发现问题数量: {results['summary']['issues_found_count']}")
            
            print("\n📋 各维度测试详情:")
            for dim_key, dim_name in DIMENSIONS.items():
                if dim_key in results["content_validation"]:
                    dim_data = results["content_validation"][dim_key]
                    pass_rate = round((dim_data['passed_tests'] / dim_data['total_tests'] * 100) if dim_data['total_tests'] > 0 else 0, 2)
                    print(f"  {dim_name}: {dim_data['passed_tests']}/{dim_data['total_tests']} ({pass_rate}%)")
            
            if results["issues_found"]:
                print("\n❌ 发现的问题:")
                for i, issue in enumerate(results["issues_found"], 1):
                    print(f"  {i}. {issue}")
            else:
                print("\n✅ 未发现明显问题")
            
            print("="*60)
            
            # 保存详细测试结果
            results["console_messages"] = console_messages
            
            with open('six_dimension_content_test_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print("💾 详细测试结果已保存到 six_dimension_content_test_results.json")
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {str(e)}")
            results["error"] = str(e)
            raise e
            
        finally:
            await browser.close()
            
            # 保存结果（即使出现异常也要保存）
            with open('six_dimension_content_test_results.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)

async def main():
    """主函数"""
    try:
        await test_six_dimension_content_display()
        print("\n🎉 六向联动内容展示专项测试完成！")
        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)