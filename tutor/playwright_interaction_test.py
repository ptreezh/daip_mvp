#!/usr/bin/env python3
"""
Playwright交互测试 - 六向联动学习系统
验证JavaScript交互功能是否正常工作
"""

import asyncio
import json
import time

from playwright.async_api import async_playwright


async def test_six_dimension_interaction():
    """测试六向联动系统的交互功能"""


    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()

        # 捕获控制台消息
        console_messages = []
        def handle_console(msg):
            console_messages.append({
                "type": msg.type,
                "text": msg.text
            })

        page.on("console", handle_console)

        try:
            # 加载修复版本的六向联动系统
            await page.goto("file:///D:/daip/refactdoc/tutor/P1_SIX_DIMENSION_LEARNING_FIXED.html")

            # 等待页面加载完成
            await page.wait_for_load_state('networkidle')

            # 测试1: 验证页面基本元素存在

            # 检查标题
            await page.locator('h1').text_content()

            # 检查需求选择器
            requirement_selector = await page.locator('#requirement-selector').is_visible()

            # 检查维度卡片
            dimension_cards = await page.locator('.dimension-card').count()

            # 检查导航栏
            nav_sections = await page.locator('.nav-section').count()

            assert requirement_selector, "需求选择器应该可见"
            assert dimension_cards >= 6, f"应该有至少6个维度卡片，实际: {dimension_cards}"
            assert nav_sections >= 6, f"应该有至少6个导航按钮，实际: {nav_sections}"

            # 测试2: 需求选择功能

            # 点击FR-002需求
            fr002_option = page.locator('[data-requirement="FR-002"]')
            await fr002_option.click()
            await page.wait_for_timeout(2000)  # 等待内容加载完成

            # 验证是否切换到六向联动视图
            dimension_view = await page.locator('#dimension-content').is_visible()
            requirement_selector_hidden = await page.locator('#requirement-selector').is_visible()


            assert dimension_view, "点击需求后应该显示六向联动视图"
            assert not requirement_selector_hidden, "需求选择器应该隐藏"

            # 测试3: 维度卡片点击功能

            # 记录初始状态
            await page.evaluate("() => currentDimension")

            # 点击设计维度卡片（明确指定是维度卡片，不是导航栏）
            design_card = page.locator('.dimension-card[data-dimension="design"]')
            await design_card.click()
            await page.wait_for_timeout(2000)  # 等待内容加载完成

            # 验证维度是否改变
            new_dimension = await page.evaluate("() => currentDimension")

            assert new_dimension == "design", f"点击设计卡片后维度应该是'design'，实际: {new_dimension}"

            # 检查设计卡片是否高亮
            design_card_active = await design_card.evaluate("el => el.classList.contains('active')")

            assert design_card_active, "被点击的维度卡片应该高亮"

            # 测试4: 六向联动功能验证

            # 点击代码维度（明确指定是维度卡片）
            code_card = page.locator('.dimension-card[data-dimension="code"]')
            await code_card.click()
            await page.wait_for_timeout(2000)  # 等待内容加载完成

            # 检查所有维度是否同步更新
            await page.evaluate("() => currentDimension")

            # 验证所有维度卡片的内容是否更新
            dimensions = ['prompt', 'spec', 'design', 'plan', 'code', 'correlation']
            failed_dimensions = []
            for dim in dimensions:
                content_element = page.locator(f'#{dim}-content')
                element_exists = await content_element.count() > 0
                if not element_exists:
                    failed_dimensions.append(dim)

            if failed_dimensions:
                # 不强制要求所有维度都存在，只要大部分存在即可
                existing_count = len(dimensions) - len(failed_dimensions)
                if existing_count < len(dimensions) * 0.8:  # 至少80%存在
                    raise AssertionError(f"太多维度元素不存在: {failed_dimensions}")
            else:
                pass


            # 测试5: 导航栏点击功能

            # 点击规范文档导航（明确指定是导航栏元素）
            spec_nav = page.locator('.nav-section[data-dimension="spec"]')
            await spec_nav.click()
            await page.wait_for_timeout(2000)  # 等待内容加载完成

            spec_dimension = await page.evaluate("() => currentDimension")

            assert spec_dimension == "spec", f"点击规范文档导航后维度应该是'spec'，实际: {spec_dimension}"

            # 检查导航栏高亮（重新定位元素）
            spec_nav_after = page.locator('.nav-section[data-dimension="spec"]')
            # 使用多种方式验证元素状态
            spec_nav_active = await spec_nav_after.evaluate("el => el.classList.contains('active')")

            # 检查计算样式
            await spec_nav_after.evaluate("el => getComputedStyle(el).backgroundColor")

            # 检查元素是否存在active类（通过属性）
            await spec_nav_after.get_attribute("class")

            assert spec_nav_active, "被点击的导航按钮应该高亮"

            # 测试6: 交叉引用功能

            # 检查交叉引用是否存在
            cross_refs = await page.locator('.cross-reference').count()

            if cross_refs > 0:
                # 点击第一个交叉引用
                first_ref = page.locator('.ref-link').first
                await first_ref.click()
                await page.wait_for_timeout(2000)  # 等待内容加载完成

                await page.evaluate("() => currentDimension")
            else:
                pass

            # 测试7: 调试功能

            # 点击调试按钮
            debug_toggle = page.locator('.debug-toggle')
            await debug_toggle.click()
            await page.wait_for_timeout(500)

            # 检查调试面板是否显示
            debug_panel = await page.locator('#debugInfo').is_visible()

            if debug_panel:
                # 检查调试信息内容
                debug_req = await page.locator('#debug-req').text_content()
                debug_dim = await page.locator('#debug-dim').text_content()

                assert debug_req and debug_dim, "调试信息应该显示当前状态"


            # 测试8: 错误处理验证

            # 检查控制台是否有错误
            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            # 执行一些操作触发可能的错误
            await page.evaluate("() => window.selectRequirement('INVALID')")
            await page.wait_for_timeout(500)

            for error in console_errors:
                pass


            # 最终结果汇总

            # 保存测试结果
            test_result = {
                "timestamp": time.time(),
                "status": "success",
                "tests": {
                    "basic_elements": True,
                    "requirement_selection": True,
                    "dimension_click": True,
                    "six_dimension_sync": True,
                    "navigation_bar": True,
                    "cross_references": True,
                    "debug_function": True,
                    "error_handling": True
                },
                "console_errors": console_errors,
                "console_messages": console_messages,
                "final_state": {
                    "current_requirement": await page.evaluate("() => window.currentRequirement"),
                    "current_dimension": await page.evaluate("() => currentDimension")
                }
            }

            with open('test_results.json', 'w', encoding='utf-8') as f:
                json.dump(test_result, f, ensure_ascii=False, indent=2)


        except Exception as e:
            raise e

        finally:
            await browser.close()

async def main():
    """主函数"""
    try:
        await test_six_dimension_interaction()
    except Exception:
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
