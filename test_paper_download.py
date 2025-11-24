import sys
sys.path.insert(0, './src')
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

# 测试各种论文下载意图
test_inputs = [
    '下载论文',
    '下载论文 人工智能',
    '下载人工智能论文',
    '获取论文 机器学习',
    '下载arxiv 1234.5678',
    '下载论文 1234.5678'
]

print('测试论文下载意图识别:')
for test_input in test_inputs:
    intent = recognizer.recognize_intent(test_input)
    if intent:
        if intent.name == "download_paper":
            print(f'  输入: "{test_input}" -> 意图: {intent.name}, 参数: {intent.parameters}')
        else:
            print(f'  输入: "{test_input}" -> 意图: {intent.name}')
    else:
        print(f'  输入: "{test_input}" -> 无匹配意图')

print()

# 检查是否有默认参数处理
print('检查论文搜索意图 (如果下载意图不匹配):')
for test_input in ['下载论文', '下载论文 人工智能']:
    intent = recognizer.recognize_intent(test_input)
    if intent:
        print(f'  输入: "{test_input}" -> 意图: {intent.name}, 参数: {getattr(intent, "parameters", {})}')
    else:
        print(f'  输入: "{test_input}" -> 无匹配意图')