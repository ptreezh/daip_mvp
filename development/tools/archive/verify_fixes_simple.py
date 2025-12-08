"""
简化验证测试 - 验证修复后的功能
"""
import sys
sys.path.insert(0, './src')

print("🔍 验证修复后的Wiki和辩论功能")

try:
    from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
    recognizer = EnhancedIntentRecognizer()
    
    print("✅ 意图识别器创建成功")
    
    # 测试Wiki相关功能
    wiki_tests = [
        ("创建维基 人工智能历史", "create_wiki", "维基创建"),
        ("创建词条 机器学习", "create_wiki", "词条创建"),
        ("写个维基 量子计算", "create_wiki", "维基创建"),
        ("创建百科 深度学习", "create_wiki", "百科创建"),
        ("创建", "question", "空创建请求")
    ]
    
    print("\\n📋 Wiki意图识别测试:")
    wiki_success = 0
    for test_input, expected_intent, desc in wiki_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent and expected_intent in intent.name:
            actual_title = intent.parameters.get('title', 'N/A')
            print(f"  ✅ {desc}: '{test_input}' -> {intent.name} (标题: {actual_title})")
            wiki_success += 1
        else:
            print(f"  ❌ {desc}: '{test_input}' -> {intent.name if intent else 'None'} (期望: {expected_intent})")
    
    # 测试辩论相关功能
    debate_tests = [
        ("辩论 AI伦理", "start_debate", "辩论启动"),
        ("多模型辩论 量子计算", "start_debate", "多模型辩论"),
        ("开始辩论 机器学习", "start_debate", "开始辩论")
    ]
    
    print("\\n📝 辩论意图识别测试:")
    debate_success = 0
    for test_input, expected_intent, desc in debate_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent and expected_intent in intent.name:
            actual_topic = intent.parameters.get('topic', 'N/A')
            print(f"  ✅ {desc}: '{test_input}' -> {intent.name} (主题: {actual_topic})")
            debate_success += 1
        else:
            print(f"  ❌ {desc}: '{test_input}' -> {intent.name if intent else 'None'} (期望: {expected_intent})")
    
    print(f"\\n✅ 修复验证结果:")
    print(f"   Wiki功能: {wiki_success}/5 通过")
    print(f"   辩论功能: {debate_success}/3 通过")
    
    if wiki_success >= 4 and debate_success >= 2:
        print("   🎉 大部分功能已修复成功！")
    else:
        print("   ⚠️  仍需进一步修复")
        
except Exception as e:
    print(f"❌ 验证失败: {e}")
    import traceback
    traceback.print_exc()