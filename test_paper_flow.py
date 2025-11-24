import sys
sys.path.insert(0, './src')
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

# 测试论文搜索和下载相关意图识别
paper_test_cases = [
    '搜索论文 人工智能',
    '查找机器学习论文',
    '论文 深度学习',
    '下载论文 量子计算',  # 现在应该被识别为download_paper意图
    '下载论文',  # 应该被识别为download_paper并要求澄清
    '下载arxiv 1234.5678',
    '获取论文 1111.2222'
]

print('论文搜索下载功能意图识别测试:')
for test_input in paper_test_cases:
    intent = recognizer.recognize_intent(test_input)
    if intent and ('search' in intent.name or 'download' in intent.name or 'paper' in intent.name):
        print(f'  ✅ \"{test_input}\" -> {intent.name}')
        print(f'    参数: {intent.parameters}')
        if hasattr(intent, 'requires_clarification'):
            print(f'    需要澄清: {intent.requires_clarification}')
    else:
        print(f'  输入: \"{test_input}\" -> {intent.name if intent else None}')
        print(f'    参数: {getattr(intent, "parameters", {}) if intent else "N/A"}')
    print()