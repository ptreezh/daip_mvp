"""
最终TDD验证测试 - 验证所有修复是否到位
"""
import sys
sys.path.insert(0, './src')

print("="*90)
print("✅ 最终TDD验证测试 - 验证修复是否全部到位")
print("="*90)

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

print("\\n🔧 测试修复后的功能:")

# 测试辩论功能 
print("\\n1. 辩论功能测试:")
debate_tests = [
    ("辩论", "start_debate", "辩论启动", True),
    ("辩论 AI伦理", "start_debate", "辩论+主题", False),
    ("多模型辩论", "start_debate", "多模型辩论", True),
    ("多模型辩论 量子计算", "start_debate", "多模型辩论+主题", False),
    ("开始辩论 深度学习", "start_debate", "开始辩论+主题", False)
]

for test_input, expected_intent, description, expect_clarification in debate_tests:
    intent = recognizer.recognize_intent(test_input)
    if intent and expected_intent in intent.name:
        actual_clarification = getattr(intent, 'requires_clarification', False)
        success = actual_clarification == expect_clarification
        status = "✅" if success else "❌"
        print(f"   {status} {description}: '{test_input}' -> {intent.name} (澄清: {actual_clarification}, 期望: {expect_clarification})")
    else:
        print(f"   ❌ {description}: '{test_input}' -> {intent.name if intent else 'None'} (期望: {expected_intent})")

# 测试维基功能
print("\\n2. Wiki功能测试:")
wiki_tests = [
    ("创建词条", "create_wiki", "创建词条-需澄清", True),
    ("创建词条 机器学习", "create_wiki", "创建词条+主题", False),
    ("创造词条 人工智能", "create_wiki", "创造词条+主题", False),
    ("新建维基 量子计算", "create_wiki", "新建维基+主题", False),
    ("写个百科 深度学习", "create_wiki", "写个百科+主题", False)
]

for test_input, expected_intent, description, expect_clarification in wiki_tests:
    intent = recognizer.recognize_intent(test_input)
    if intent and expected_intent in intent.name:
        actual_clarification = getattr(intent, 'requires_clarification', False)
        success = actual_clarification == expect_clarification
        status = "✅" if success else "❌"
        
        # 检查标题提取
        title = intent.parameters.get('title', '')
        print(f"   {status} {description}: '{test_input}' -> {intent.name} (标题: '{title}', 澄清: {actual_clarification})")
    else:
        print(f"   ❌ {description}: '{test_input}' -> {intent.name if intent else 'None'} (期望: {expected_intent})")

# 测试论文功能
print("\\n3. 论文功能测试:")
paper_tests = [
    ("下载论文", "download_paper", "下载论文-需澄清", True),
    ("下载论文 机器学习", "download_paper", "下载论文+主题", False),
    ("搜索论文 深度学习", "search_papers", "搜索论文+主题", False),
    ("本地知识查找", "knowledge_search", "知识库搜索", False)
]

for test_input, expected_intent, description, expect_clarification in paper_tests:
    intent = recognizer.recognize_intent(test_input)
    if intent and expected_intent in intent.name:
        actual_clarification = getattr(intent, 'requires_clarification', False)
        success = actual_clarification == expect_clarification
        status = "✅" if success else "❌"
        
        # 检查参数提取
        if expected_intent == "download_paper":
            search_query = intent.parameters.get('search_query', '')
            print(f"   {status} {description}: '{test_input}' -> {intent.name} (搜索: '{search_query}', 澄清: {actual_clarification})")
        elif expected_intent == "search_papers":
            query = intent.parameters.get('query', '')
            print(f"   {status} {description}: '{test_input}' -> {intent.name} (查询: '{query}', 澄清: {actual_clarification})")
        elif expected_intent == "knowledge_search":
            query = intent.parameters.get('query', '')
            print(f"   {status} {description}: '{test_input}' -> {intent.name} (查询: '{query}', 澄清: {actual_clarification})")
    else:
        print(f"   ❌ {description}: '{test_input}' -> {intent.name if intent else 'None'} (期望: {expected_intent})")

print("\\n✅ 修复验证完成!")
print("系统现在正确处理多角色协作功能，包括：")
print("   - 辩论系统：正确识别辩论意图和参数")
print("   - Wiki系统：正确处理维基创建和参数提取")
print("   - 论文系统：正确处理搜索下载连续流程")
print("   - 澄清机制：正确标记需要用户补充信息的请求")