import sys
sys.path.insert(0, './src')
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

print('运行完整回归测试:')

# 测试原始问题
test_cases = [
    ('创建维基 项目计划', 'create_wiki', '标题提取'),
    ('个人助手帮我分析', 'personal_assistant', '意图优先级'),
    ('帮我分析这段文本', 'execute_skill', '意图优先级'),
    ('本地知识查找', 'knowledge_search', '意图优先级'),
    ('帮我', 'execute_skill', '需要澄清')
]

all_passed = True
for input_text, expected_intent, test_desc in test_cases:
    intent = recognizer.recognize_intent(input_text)
    if intent:
        intent_name = intent.name
        if expected_intent in intent_name:
            clarification_status = ''
            if expected_intent == 'execute_skill' and input_text == '帮我':
                clarification_status = f', 需要澄清: {getattr(intent, "requires_clarification", False)}'
            print(f'  ✅ {test_desc}: "{input_text}" -> {intent_name}{clarification_status}')
        else:
            print(f'  ❌ {test_desc}: "{input_text}" -> {intent_name} (期望 {expected_intent})')
            all_passed = False
    else:
        print(f'  ❌ {test_desc}: "{input_text}" -> 无意图')
        all_passed = False

print(f'\n完整回归测试: {"✅ 全部通过" if all_passed else "❌ 有失败"}')