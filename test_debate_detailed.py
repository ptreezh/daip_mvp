import sys
sys.path.insert(0, './src')
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

# 测试辩论相关意图识别的详细过程
debate_test_cases = [
    '辩论',
    '辩论 AI伦理',
    '开始辩论',
    '开始辩论 AI伦理', 
    '发起关于量子计算的辩论',
    '多模型辩论',
    '多模型辩论 人工智能',
    '开始多模型辩论',
    '启动辩论 伦理问题'
]

print('辩论功能详细意图识别测试:')
for test_input in debate_test_cases:
    intent = recognizer.recognize_intent(test_input)
    print(f'  输入: "{test_input}"')
    if intent:
        print(f'    -> 意图: {intent.name}')
        print(f'    -> 参数: {intent.parameters}')
        if hasattr(intent, 'requires_clarification'):
            print(f'    -> 需要澄清: {intent.requires_clarification}')
    else:
        print(f'    -> 无匹配意图')
    print()