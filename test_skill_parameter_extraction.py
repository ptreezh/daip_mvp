"""
测试技能参数提取功能
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_skill_parameter_extraction():
    print("="*70)
    print("🔍 测试技能参数提取功能")
    print("="*70)
    
    recognizer = EnhancedIntentRecognizer()
    
    # 测试各种参数提取场景
    print("📋 参数提取测试:")
    
    extraction_tests = [
        # 需要参数提取的场景
        ("帮我分析", "execute_skill", 0.5, "content should be empty"),
        ("帮我分析这段文本", "execute_skill", 0.8, "content should extract '这段文本'"), 
        ("帮我处理量子计算文档", "execute_skill", 0.8, "content should extract '量子计算文档'"),
        ("帮我搜索机器学习资料", "execute_skill", 0.8, "content should extract '机器学习资料'"),
        ("文本分析 人工智能发展趋势", "execute_skill", 0.8, "content should extract '人工智能发展趋势'"),
        ("创建维基", "create_wiki", 0.5, "title should be empty"),
        ("创建维基 项目计划", "create_wiki", 0.8, "title should extract '项目计划'"),
        ("论文", "search_papers", 0.5, "query should be empty"),
        ("论文 人工智能", "search_papers", 0.8, "query should extract '人工智能'")
    ]
    
    success_count = 0
    for test_input, expected_intent, min_confidence, desc in extraction_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent and expected_intent in intent.name and intent.confidence >= min_confidence:
            print(f"  ✅ '{test_input}' → {intent.name} (置信度: {intent.confidence:.2f})")
            
            # 检查参数提取是否正确
            if expected_intent == "execute_skill":
                content = intent.parameters.get("content", "")
                print(f"     参数提取: '{content}' ({'✅' if content.strip() else '⚠️ 空'})")
            elif expected_intent == "create_wiki":
                title = intent.parameters.get("title", "")
                print(f"     标题提取: '{title}' ({'✅' if title.strip() else '⚠️ 空'})") 
            elif expected_intent == "search_papers":
                query = intent.parameters.get("query", "")
                print(f"     查询提取: '{query}' ({'✅' if query.strip() else '⚠️ 空'})")
            
            success_count += 1
        else:
            print(f"  ❌ '{test_input}' → {(intent.name if intent else 'None')} (置信度: {intent.confidence if intent else 0:.2f})")
    
    print(f"\n📊 参数提取准确率: {success_count}/{len(extraction_tests)} ({success_count/len(extraction_tests)*100:.1f}%)")
    
    # 现在测试意图澄清检查
    print(f"\n🔄 意图澄清检测测试:")
    
    clarification_tests = [
        ("帮我分析", "execute_skill", True),      # 应该需要澄清
        ("帮我分析这段文本", "execute_skill", False), # 不需要澄清
        ("创建维基", "create_wiki", True),        # 应该需要澄清
        ("创建维基 项目计划", "create_wiki", False), # 不需要澄清
        ("论文", "search_papers", True),         # 应该需要澄清
        ("论文 人工智能", "search_papers", False), # 不需要澄清
    ]
    
    clarif_success = 0
    for test_input, expected_intent, should_require_clarification in clarification_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent and expected_intent in intent.name:
            requires_clarification = getattr(intent, 'requires_clarification', False)
            status = "✅" if requires_clarification == should_require_clarification else "❌"
            print(f"  {status} '{test_input}' → {intent.name} (需澄清: {requires_clarification}, 期望: {should_require_clarification})")
            if requires_clarification == should_require_clarification:
                clarif_success += 1
        else:
            print(f"  ❌ '{test_input}' → {(intent.name if intent else 'None') if intent else 'None'}")
    
    print(f"   澄清准确率: {clarif_success}/{len(clarification_tests)} ({clarif_success/len(clarification_tests)*100:.1f}%)")
    
    print(f"\n🏆 参数提取功能分析:")
    print(f"   参数提取成功: {success_count}/{len(extraction_tests)} ({success_count/len(extraction_tests)*100:.1f}%)")
    print(f"   澄清检测准确率: {clarif_success}/{len(clarification_tests)} ({clarif_success/len(clarification_tests)*100:.1f}%)")
    
    overall_success = clarif_success >= len(clarification_tests) * 0.7  # 70%以上为目标
    
    if overall_success:
        print(f"   ✅ 参数提取和澄清检测功能已改进!")
    else:
        print(f"   ⚠️  参数提取和澄清检测需要进一步改进")
    
    print("="*70)
    return overall_success

if __name__ == "__main__":
    success = test_skill_parameter_extraction()
    print(f"\n🎯 参数提取测试结果: {'✅ 通过' if success else '⚠️ 待改进'}")