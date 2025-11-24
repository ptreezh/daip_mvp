"""
测试增强意图识别器的智能参数处理功能
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer


def test_parameter_processing():
    print("="*90)
    print("🧪 测试智能参数处理功能")
    print("="*90)

    recognizer = EnhancedIntentRecognizer()

    # 测试参数处理 - 这些应该被标记为需要澄清
    param_tests = [
        # 这些应该被标记为需要澄清
        ("论文", "search_papers", True),
        ("创建维基", "create_wiki", True),
        ("开始辩论", "start_debate", True),
        ("帮我", "question", True),

        # 这些不应该需要澄清
        ("论文 AI伦理", "search_papers", False),
        ("创建维基 项目计划", "create_wiki", False),
        ("开始辩论 量子计算", "start_debate", False),
        ("帮我分析这段文本", "execute_skill", False),
    ]

    param_success = 0
    for test_input, expected_intent, expect_clarification in param_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent and expected_intent in intent.name:
            requires_clarification = getattr(intent, 'requires_clarification', False)
            if requires_clarification == expect_clarification:
                param_success += 1
                print(f"   ✅ '{test_input}' → {getattr(intent, 'name', 'unknown')} (需要澄清: {requires_clarification})")
            else:
                print(f"   ❌ '{test_input}' → {getattr(intent, 'name', 'unknown')} (需要澄清: {requires_clarification}, 期望: {expect_clarification})")
        else:
            print(f"   ❌ '{test_input}' → {(intent.name if intent else 'None')} (期望: {expected_intent})")

    param_accuracy = param_success / len(param_tests) * 100
    print(f"\n📊 参数处理准确率: {param_success}/{len(param_tests)} ({param_accuracy:.1f}%)")
    return param_accuracy, param_success, len(param_tests)


if __name__ == "__main__":
    accuracy, success, total = test_parameter_processing()
    print(f"\n🎯 智能参数处理测试完成: {accuracy:.1f}% ({success}/{total})")