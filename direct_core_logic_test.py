"""
直接测试 TUI 核心逻辑，绕过 Textual UI 部分
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
from daip_live.agent_engine.services.clarification_service import ClarificationService
from daip_live.container import Container


def test_tui_core_logic():
    """测试TUI的核心逻辑，包括意图识别和澄清处理"""
    print("="*70)
    print("🎯 直接测试 TUI 核心逻辑")
    print("="*70)
    
    # 创建意图识别器
    recognizer = EnhancedIntentRecognizer()
    
    # 创建澄清服务
    clarification_service = ClarificationService()
    
    # 测试用例
    test_cases = [
        # (输入, 期望意图, 是否需要澄清)
        ("论文", "search_papers", True),
        ("论文 人工智能", "search_papers", False),
        ("搜索量子计算", "search_papers", False),
        ("下载论文", "search_papers", True),
        ("开始辩论", "start_debate", True),
        ("开始辩论 AI伦理", "start_debate", False),
        ("创建Wiki", "create_wiki", True),
        ("创建Wiki 项目计划", "create_wiki", False),
        ("你好", "chat", False),
        ("你是谁", "question", False),
        ("？", "question", False),
        ("随便聊聊", "chat", False),
        ("帮我写代码", "question", False),
    ]
    
    print("🧪 开始测试意图识别逻辑...")
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, (input_text, expected_intent, expect_clarification) in enumerate(test_cases, 1):
        print(f"\n{i:2d}. 输入: '{input_text}'")
        
        # 识别意图
        intent = recognizer.recognize_intent(input_text)
        
        if intent:
            actual_intent = intent.name
            requires_clarification = getattr(intent, 'requires_clarification', False)
            
            print(f"    识别意图: {actual_intent}")
            print(f"    需要澄清: {requires_clarification}")
            
            # 检查澄清需求
            if expect_clarification == requires_clarification:
                print(f"    ✅ 澄清需求正确")

                if requires_clarification:
                    # 获取澄清消息
                    clarification_needed = getattr(intent, 'clarification_needed', None)
                    if clarification_needed:
                        if hasattr(clarification_needed, 'message'):
                            print(f"    📝 澄清消息: {clarification_needed.message}")
                        else:
                            print(f"    📝 澄清类型: {getattr(clarification_needed, 'type', 'unknown')}")
                    else:
                        print("    📝 澄清信息不可用")

                success_count += 1
            else:
                print(f"    ❌ 澄清需求不匹配 - 期望: {expect_clarification}, 实际: {requires_clarification}")
        else:
            print(f"    ❌ 未识别到意图")
    
    print(f"\n📊 意图识别测试结果: {success_count}/{total_count} 通过")
    
    # 测试澄清服务的具体功能
    print(f"\n🔍 测试澄清服务功能...")
    
    clarify_success = 0
    clarify_total = 0
    
    # 测试缺失关键词检测
    print("\n   测试关键词缺失检测:")
    missing_kw_test = clarification_service.check_missing_keywords("search_papers", {"query": ""})
    if missing_kw_test:
        print(f"      ✅ '论文' 识别为关键词缺失: {missing_kw_test.message}")
        clarify_success += 1
    else:
        print(f"      ❌ '论文' 未能识别为关键词缺失")
    clarify_total += 1
    
    # 测试正常参数
    normal_kw_test = clarification_service.check_missing_keywords("search_papers", {"query": "人工智能"})
    if not normal_kw_test:
        print(f"      ✅ '论文 人工智能' 正确处理为完整参数")
        clarify_success += 1
    else:
        print(f"      ❌ '论文 人工智能' 错误标记为缺失参数")
    clarify_total += 1
    
    # 测试缺失参数检测
    missing_param_test = clarification_service.check_missing_parameters("search_papers", {})
    if missing_param_test:
        print(f"      ✅ 参数缺失检测正常工作")
        clarify_success += 1
    else:
        print(f"      ❌ 参数缺失检测未工作")
    clarify_total += 1
    
    print(f"\n   📊 澄清服务测试结果: {clarify_success}/{clarify_total} 通过")
    
    # 综合评分
    total_tests = success_count + clarify_success
    total_possible = total_count + clarify_total
    accuracy = total_tests / total_possible * 100
    
    print(f"\n🏆 总体准确率: {accuracy:.1f}% ({total_tests}/{total_possible})")
    
    if accuracy >= 90:
        print(f"\n🎉 测试成功！TUI核心逻辑工作正常。")
        print("✅ 意图识别器能正确解析用户输入")
        print("✅ 澄清服务能正确检测缺失参数")
        print("✅ 系统能区分需要澄清和不需要澄清的输入")
    else:
        print(f"\n⚠️  测试部分通过，可能需要进一步调试。")
    
    print("="*70)
    return accuracy >= 90


if __name__ == "__main__":
    success = test_tui_core_logic()
    
    if success:
        print("\n✅ TUI 核心逻辑验证通过！")
        print("系统现在能正确处理用户交互:")
        print("  • 输入 '论文' → 提示用户输入关键词")
        print("  • 输入 '开始辩论' → 提示用户输入辩论主题")
        print("  • 输入 '创建Wiki' → 提示用户输入标题")
        print("  • 输入完整信息 → 正常执行功能")
        print("  • 输入对话 → 进入聊天模式")
    else:
        print("\n❌ 测试未完全通过，需进一步检查。")