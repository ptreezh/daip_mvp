import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

# 测试参数提取
recognizer = EnhancedIntentRecognizer()

test_inputs = [
    '帮我分析人工智能伦理',
    '帮我处理量子计算文档', 
    '帮我总结这篇论文',
    '帮我分析一下这段文本'
]

print('🔄 测试技能参数提取修复...')
for test_input in test_inputs:
    print(f"测试输入: {test_input}")
    intent = recognizer.recognize_intent(test_input)
    if intent:
        print(f"  意图: {intent.name}")
        content = intent.parameters.get('content', '')
        print(f"  内容: '{content}'")
        requires_clarification = getattr(intent, 'requires_clarification', False)
        print(f"  需要澄清: {requires_clarification}")
        print()
    else:
        print(f"  未识别意图")
        print()