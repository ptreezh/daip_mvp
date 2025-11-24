import sys
sys.path.insert(0, './src')
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

# 测试Wiki意图识别，特别关注标题提取
wiki_tests = [
    ("创建词条 人工智能", "create_wiki", "标题提取测试"),
    ("新建词条 机器学习", "create_wiki", "标题提取测试"),
    ("创建维基 深度学习", "create_wiki", "标题提取测试"),
    ("创建百科 自然语言处理", "create_wiki", "标题提取测试"),
    ("查看词条 人工智能", "create_wiki", "查看意图测试"),
    ("浏览词条 机器学习", "create_wiki", "查看意图测试")
]

print("Wiki意图识别和参数提取测试:")
for test_input, expected_intent, test_desc in wiki_tests:
    intent = recognizer.recognize_intent(test_input)
    if intent and expected_intent in intent.name:
        title = intent.parameters.get('title', 'N/A')
        print(f"  ✅ {test_desc}: \"{test_input}\" -> {intent.name}")
        print(f"     提取标题: '{title}'")
        if test_input.split()[1] in ['词条', '维基', '百科'] and len(test_input.split()) > 2:
            expected_title = ' '.join(test_input.split()[2:])  # 取第一个词(创建/查看等)和第二个词(词条/维基)之后的内容
            if title == expected_title:
                print(f"     🎯 标题提取正确!")
            else:
                print(f"     ⚠️  标题提取不准确，期望: '{expected_title}'")
    else:
        print(f"  ❌ {test_desc}: \"{test_input}\" -> {intent.name if intent else 'None'}")
    print()

# 测试论文下载意图和搜索查询提取
paper_tests = [
    ("下载论文 人工智能", "download_paper", "搜索下载意图测试"),
    ("获取文章 量子计算", "download_paper", "搜索下载意图测试"),
    ("下载文献 区块链", "download_paper", "搜索下载意图测试")
]

print("论文搜索下载意图识别和参数提取测试:")
for test_input, expected_intent, test_desc in paper_tests:
    intent = recognizer.recognize_intent(test_input)
    if intent and expected_intent in intent.name:
        search_query = intent.parameters.get('search_query', 'N/A')
        paper_id = intent.parameters.get('paper_id', 'N/A')
        print(f"  ✅ {test_desc}: \"{test_input}\" -> {intent.name}")
        print(f"     搜索查询: '{search_query}'")
        print(f"     论文ID: '{paper_id}'")
        expected_query = ' '.join(test_input.split()[2:])  # 取"下载论文"之后的内容
        if search_query == expected_query:
            print(f"     🎯 搜索查询提取正确!")
        else:
            print(f"     ⚠️  搜索查询提取不准确，期望: '{expected_query}'")
    else:
        print(f"  ❌ {test_desc}: \"{test_input}\" -> {intent.name if intent else 'None'}")
    print()