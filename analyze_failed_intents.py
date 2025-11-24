"""
详细分析意图识别失败案例
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer


def analyze_failed_intents():
    print("="*90)
    print("🔍 详细分析意图识别失败案例")
    print("="*90)

    recognizer = EnhancedIntentRecognizer()

    # 失败的测试用例
    failed_tests = [
        ("个人助手帮我分析", "personal_assistant", "question"),
        ("帮我分析这段文本", "execute_skill", "question"),
        ("执行文本分析", "execute_skill", "question"),
        ("本地知识查找", "knowledge_search", "search_papers"),
        ("？", "question", "None")  # 实际返回None
    ]

    print("失败的意图识别案例:")
    for i, (test_input, expected_intent, actual_result) in enumerate(failed_tests, 1):
        print(f"\n{i}. 输入: '{test_input}'")
        print(f"   期望意图: {expected_intent}")
        print(f"   实际结果: {actual_result}")
        
        # 让我们看看实际的识别结果
        intent = recognizer.recognize_intent(test_input)
        if intent:
            print(f"   实际识别: {intent.name}")
            print(f"   匹配置信度: {intent.confidence:.2f}")
            print(f"   需要澄清: {getattr(intent, 'requires_clarification', False)}")
        else:
            print(f"   实际识别: None")
        
        # 分析为什么失败
        print(f"   分析:")
        if "个人助手" in test_input and expected_intent == "personal_assistant":
            print(f"     - 可能原因: '个人助手'模式可能被更通用的'question'模式匹配")
        elif "帮我" in test_input and expected_intent == "execute_skill":
            print(f"     - 可能原因: '帮我'被识别为问题而非技能请求")
        elif test_input == "？" and actual_result == "None":
            print(f"     - 可能原因: 单独的问号未被正确识别为问题模式")
        elif "本地知识" in test_input:
            print(f"     - 可能原因: '本地知识查找'被更通用的搜索模式匹配")

    print(f"\n📋 失败原因总结:")
    print(f"   1. 意图模式冲突: 某些模式被更通用的模式覆盖")
    print(f"   2. 模式优先级: 问题模式可能比特定功能模式优先级更高")
    print(f"   3. 特殊字符处理: 单个字符可能没有适当的处理模式")
    print(f"   4. 部分匹配: '本地知识'可能触发了通用搜索而非知识库搜索")


if __name__ == "__main__":
    analyze_failed_intents()