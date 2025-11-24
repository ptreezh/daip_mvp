import sys
sys.path.insert(0, './src')
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

# 测试各种论文下载意图，检查是否需要澄清
test_inputs = [
    '下载论文',
    '下载论文 人工智能',
    '下载论文 1234.5678'
]

print('测试论文下载意图识别和澄清需求:')
for test_input in test_inputs:
    intent = recognizer.recognize_intent(test_input)
    if intent:
        print(f'  输入: "{test_input}" -> 意图: {intent.name}')
        print(f'    参数: {intent.parameters}')
        if hasattr(intent, 'requires_clarification'):
            print(f'    需要澄清: {intent.requires_clarification}')
            if intent.requires_clarification:
                print(f'    澄清需求: {getattr(intent, "clarification_needed", "N/A")}')
        print()
    else:
        print(f'  输入: "{test_input}" -> 无匹配意图')
        print()