import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

# 测试修复后的下载论文功能
test_input = '下载论文 机器学习'
intent = recognizer.recognize_intent(test_input)

print(f'测试输入: {test_input}')
if intent:
    print(f'意图: {intent.name}')
    print(f'参数: {intent.parameters}')
    search_query = intent.parameters.get('search_query', '')
    print(f'搜索查询: \"{search_query}\"')
    
    if search_query and search_query != '':
        print(f'✅ 修复成功: 提取到搜索关键词 \"{search_query}\"')
        print(f'✅ 不需要澄清: {getattr(intent, "requires_clarification", False)}')
    else:
        print(f'❌ 修复失败: 未提取到搜索关键词')
else:
    print('❌ 未识别到意图')