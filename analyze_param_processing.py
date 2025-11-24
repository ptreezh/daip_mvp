"""
详细分析参数处理失败案例
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer


def analyze_failed_parameter_processing():
    print("="*90)
    print("🔍 详细分析参数处理失败案例")
    print("="*90)

    recognizer = EnhancedIntentRecognizer()

    # 参数处理测试用例 (输入, 期望意图, 是否期望澄清)
    param_tests = [
        # 这些应该被标记为需要澄清
        ("论文", "search_papers", True),        # 期望澄清 - 应该通过
        ("创建维基", "create_wiki", True),      # 期望澄清 - 应该通过
        ("开始辩论", "start_debate", True),     # 期望澄清 - 应该通过
        ("帮我", "question", True),             # 期望澄清 - 但可能失败
        
        # 这些不应该需要澄清
        ("论文 AI伦理", "search_papers", False),    # 不需要澄清 - 应该通过
        ("创建维基 项目计划", "create_wiki", False), # 不需要澄清 - 但可能失败
        ("开始辩论 量子计算", "start_debate", False), # 不需要澄清 - 应该通过
        ("帮我分析这段文本", "execute_skill", False), # 不需要澄清 - 但可能失败
    ]

    print("参数处理测试案例:")
    for i, (test_input, expected_intent, expect_clarification) in enumerate(param_tests, 1):
        intent = recognizer.recognize_intent(test_input)
        if intent and expected_intent in intent.name:
            requires_clarification = getattr(intent, 'requires_clarification', False)
            status = "✅" if requires_clarification == expect_clarification else "❌"
            print(f"\n{i}. 输入: '{test_input}'")
            print(f"   期望意图: {expected_intent}")
            print(f"   期望澄清: {expect_clarification}")
            print(f"   实际澄清: {requires_clarification}")
            print(f"   状态: {status}")
            if status == "❌":
                print(f"   问题: 期望澄清={expect_clarification}, 实际澄清={requires_clarification}")
        else:
            print(f"\n{i}. 输入: '{test_input}'")
            print(f"   问题: 意图识别失败 (期望: {expected_intent}, 实际: {intent.name if intent else 'None'})")

    print(f"\n📋 参数处理失败原因总结:")
    print(f"   1. '帮我' - 未被正确识别为需要澄清的意图")
    print(f"   2. '创建维基 项目计划' - 被错误标记为需要澄清，尽管提供了标题")
    print(f"   3. '帮我分析这段文本' - 被错误标记为需要澄清，尽管提供了内容")

    print(f"\n🔧 深入分析具体失败案例:")
    
    # 深入分析具体案例
    print(f"\n案例1: '帮我' (期望澄清=True)")
    intent = recognizer.recognize_intent("帮我")
    if intent:
        print(f"   识别意图: {intent.name}")
        print(f"   需要澄清: {getattr(intent, 'requires_clarification', False)}")
        print(f"   澄清需求: {getattr(intent, 'clarification_needed', None)}")
    else:
        print(f"   未识别到意图")
    
    print(f"\n案例2: '创建维基 项目计划' (期望澄清=False)")
    intent = recognizer.recognize_intent("创建维基 项目计划")
    if intent:
        print(f"   识别意图: {intent.name}")
        print(f"   需要澄清: {getattr(intent, 'requires_clarification', False)}")
        print(f"   参数: {intent.parameters}")
        print(f"   澄清需求: {getattr(intent, 'clarification_needed', None)}")
        if intent.parameters.get("title"):
            print(f"   标题参数: '{intent.parameters['title']}'")
    else:
        print(f"   未识别到意图")

    print(f"\n案例3: '帮我分析这段文本' (期望澄清=False)")
    intent = recognizer.recognize_intent("帮我分析这段文本")
    if intent:
        print(f"   识别意图: {intent.name}")
        print(f"   需要澄清: {getattr(intent, 'requires_clarification', False)}")
        print(f"   参数: {intent.parameters}")
        print(f"   澄清需求: {getattr(intent, 'clarification_needed', None)}")
        if 'content' in intent.parameters or 'original_request_text' in intent.parameters:
            content = intent.parameters.get('content') or intent.parameters.get('original_request_text')
            print(f"   内容参数: '{content}'")
    else:
        print(f"   未识别到意图")


if __name__ == "__main__":
    analyze_failed_parameter_processing()