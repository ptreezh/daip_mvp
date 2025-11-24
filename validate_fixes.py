import sys
sys.path.insert(0, './src')
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

print("🔍 验证修复后的功能:")

# 测试论文获取功能
print("\\n1. 测试论文获取功能:")
paper_tests = [
    ("获取文献 机器学习", "download_paper", "文献获取"),
    ("下载文献 深度学习", "download_paper", "文献下载"),
    ("获取文章 自然语言处理", "download_paper", "文章获取")
]

for test_input, expected_intent, description in paper_tests:
    intent = recognizer.recognize_intent(test_input)
    if intent and expected_intent in intent.name:
        search_query = intent.parameters.get('search_query', '')
        paper_id = intent.parameters.get('paper_id', '')
        if search_query:
            print(f"   ✅ '{test_input}' -> {intent.name}, 搜索: '{search_query}'")
        elif paper_id:
            print(f"   ✅ '{test_input}' -> {intent.name}, ID: '{paper_id}'")
        else:
            print(f"   ✅ '{test_input}' -> {intent.name} (已识别)")
    else:
        print(f"   ❌ '{test_input}' -> {intent.name if intent else 'None'}")

# 测试辩论澄清功能
print("\\n2. 测试辩论澄清功能:")
debate_tests = [
    ("辩论", True, "单独辩论词"),
    ("辩论 AI伦理", False, "带主题辩论")
]

for test_input, should_need_clarification, description in debate_tests:
    intent = recognizer.recognize_intent(test_input)
    if intent:
        needs_clarification = getattr(intent, 'requires_clarification', False)
        if needs_clarification == should_need_clarification:
            print(f"   ✅ '{test_input}' -> {intent.name}, 需要澄清: {needs_clarification} ({description})")
        else:
            print(f"   ❌ '{test_input}' -> {intent.name}, 期望澄清: {should_need_clarification}, 实际: {needs_clarification}")
    else:
        print(f"   ❌ '{test_input}' -> 无匹配意图")

# 测试维基功能
print("\\n3. 测试维基功能:")
wiki_tests = [
    ("创建词条 人工智能", "create_wiki", "词条标题"),
    ("创建维基 量子计算", "create_wiki", "维基标题")
]

for test_input, expected_intent, feature in wiki_tests:
    intent = recognizer.recognize_intent(test_input)
    if intent and expected_intent in intent.name:
        title = intent.parameters.get('title', '')
        if title and title != test_input:
            print(f"   ✅ '{test_input}' -> {intent.name}, 标题: '{title}'")
        else:
            print(f"   ❌ '{test_input}' -> {intent.name}, 标题提取失败: '{title}'")
    else:
        print(f"   ❌ '{test_input}' -> {intent.name if intent else 'None'}")

print("\\n✅ 修复验证完成!")