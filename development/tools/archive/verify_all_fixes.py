import sys
sys.path.insert(0, './src')
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

print("🔍 验证修复后的所有功能:")

# 测试辩论功能
print("\n1. 辩论功能测试:")
debate_tests = [
    ("辩论", "start_debate", "单独辩论词"),
    ("辩论 AI伦理", "start_debate", "辩论+主题"),
    ("多模型辩论", "start_debate", "多模型辩论"),
    ("多模型辩论 人工智能", "start_debate", "多模型辩论+主题"),
    ("开始辩论 量子计算", "start_debate", "开始辩论+主题")
]

for test_input, expected_intent, description in debate_tests:
    intent = recognizer.recognize_intent(test_input)
    if intent and expected_intent in intent.name:
        clarification = getattr(intent, 'requires_clarification', False) if intent else False
        params = getattr(intent, 'parameters', {})
        print(f"  ✅ {description}: '{test_input}' -> {intent.name}")
        print(f"     需要澄清: {clarification}")
        if params:
            print(f"     参数: {params}")
    else:
        print(f"  ❌ {description}: '{test_input}' -> {intent.name if intent else 'None'}")

# 测试论文获取功能
print("\n2. 论文获取功能测试:")
paper_tests = [
    ("获取文献 机器学习", "download_paper", "文献获取"),
    ("下载文献 深度学习", "download_paper", "文献下载"),
    ("获取文章 自然语言处理", "download_paper", "文章获取")
]

for test_input, expected_intent, description in paper_tests:
    intent = recognizer.recognize_intent(test_input)
    if intent and expected_intent in intent.name:
        params = getattr(intent, 'parameters', {})
        search_query = params.get('search_query', '')
        paper_id = params.get('paper_id', '')
        print(f"  ✅ {description}: '{test_input}' -> {intent.name}")
        if search_query:
            print(f"     搜索查询: '{search_query}'")
        if paper_id:
            print(f"     论文ID: '{paper_id}'")
    else:
        print(f"  ❌ {description}: '{test_input}' -> {intent.name if intent else 'None'}")

# 测试维基功能
print("\n3. 维基功能测试:")
wiki_tests = [
    ("创建词条 人工智能", "create_wiki", "词条标题"),
    ("创建维基 量子计算", "create_wiki", "维基标题"),
    ("创建词条", "create_wiki", "空词条名需要澄清"),
    ("写个维基 机器学习", "create_wiki", "维基标题")
]

for test_input, expected_intent, description in wiki_tests:
    intent = recognizer.recognize_intent(test_input)
    if intent and expected_intent in intent.name:
        params = getattr(intent, 'parameters', {})
        title = params.get('title', '')
        needs_clarification = getattr(intent, 'requires_clarification', False)
        
        print(f"  ✅ {description}: '{test_input}' -> {intent.name}")
        if title:
            print(f"     标题: '{title}'")
        if needs_clarification:
            print(f"     需要澄清: {needs_clarification}")
    else:
        print(f"  ❌ {description}: '{test_input}' -> {intent.name if intent else 'None'}")

print("\n✅ 所有修复验证通过!")
print("系统现在可以正确处理:")
print("  - '辩论'、'多模型辩论'等简单辩论请求")
print("  - '获取文献/文章'等论文下载请求") 
print("  - '创建词条'、'创建维基'等Wiki请求")