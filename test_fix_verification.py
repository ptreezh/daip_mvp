import sys
sys.path.insert(0, './src')
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

# 测试修复后的情况
print('测试修复后的功能:')

test_cases = [
    '多模型辩论',
    '多模型辩论 量子计算', 
    '下载论文 机器学习'
]

for test_input in test_cases:
    print(f'\\n输入: "{test_input}"')
    intent = recognizer.recognize_intent(test_input)
    if intent:
        print(f'  意图: {intent.name}')
        print(f'  需要澄清: {getattr(intent, "requires_clarification", "N/A")}')
        if hasattr(intent, 'parameters'):
            print(f'  参数: {intent.parameters}')
    else:
        print('  无匹配意图')