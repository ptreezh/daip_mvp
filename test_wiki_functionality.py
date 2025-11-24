import sys
sys.path.insert(0, './src')
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

# 测试Wiki相关意图识别
wiki_test_cases = [
    '创建维基 项目计划',
    '写个维基 人工智能',
    '新建Wiki 量子计算',
    '创建词条 机器学习',
    '建造维基 深度学习',
    '创建百科 人工智能伦理'
]

print('Wiki功能意图识别测试:')
for test_input in wiki_test_cases:
    intent = recognizer.recognize_intent(test_input)
    if intent and 'wiki' in intent.name:
        print(f'  ✅ \"{test_input}\" -> {intent.name}')
        print(f'    参数: {intent.parameters}')
        if hasattr(intent, 'requires_clarification'):
            print(f'    需要澄清: {intent.requires_clarification}')
    else:
        print(f'  ❌ \"{test_input}\" -> {intent.name if intent else None} (期望: create_wiki)')