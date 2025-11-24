import sys
sys.path.insert(0, './src')
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

# 创建一个识别器实例
recognizer = EnhancedIntentRecognizer()

# 测试更全面的wiki相关短语
wiki_test_cases = [
    '创建词条',
    '创建词条 机器学习',
    '创建百科',
    '创建百科 人工智能',
    '创造词条 机器学习',
    '创建维基 项目计划',
    '新建维基 量子计算',
    '新建Wiki 量子计算',  # 这个之前测试有问题
    '词条 机器学习',
    '百科 人工智能'
]

print('Wiki相关意图识别测试:')
for test_input in wiki_test_cases:
    intent = recognizer.recognize_intent(test_input)
    if intent:
        print(f'  输入: "{test_input}" -> {intent.name}')
        if 'wiki' in intent.name:
            print(f'    ✅ Wiki意图: {intent.parameters}')
        else:
            print(f'    ❌ 非Wiki意图: {intent.name}')
    else:
        print(f'  输入: "{test_input}" -> 无匹配')
    print()