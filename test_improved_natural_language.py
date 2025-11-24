"""
测试改进后的自然语言意图识别
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_improved_natural_language_recognition():
    print("="*70)
    print("🎯 改进后的自然语言意图识别功能测试")
    print("="*70)
    
    recognizer = EnhancedIntentRecognizer()
    
    # 测试改进后的维基意图识别
    print("📝 维基意图识别改进测试:")
    wiki_tests = [
        # 之前无法识别的自然语言表达
        "创建个维基页面",
        "写个维基",
        "做个维基",
        "建个维基",
        "新建个维基",
        "创建维基",
        "写一个维基",
        "做一个维基页面",
        "新建百科页面",
        "创建个页面",
        "写个页面",
    ]
    
    wiki_success = 0
    for test in wiki_tests:
        intent = recognizer.recognize_intent(test)
        if intent and intent.name == "create_wiki":
            print(f"  ✅ '{test}' → {intent.name} (置信度: {intent.confidence:.2f})")
            wiki_success += 1
        else:
            print(f"  ❌ '{test}' → {(intent.name if intent else 'None')}")
    
    print(f"  📊 维基意图识别: {wiki_success}/{len(wiki_tests)} 通过")
    
    # 测试知识库/论文搜索意图识别
    print(f"\n🔍 知识库/论文搜索意图改进测试:")
    search_tests = [
        # 之前可能没有识别的自然语言表达
        "帮我找资料",
        "查一下信息",
        "搜索一下",
        "帮我找一下机器学习的资料",
        "查一下AI发展趋势",
        "帮我搜索量子计算的论文",
        "找找关于区块链的论文",
        "帮我查点资料",
        "找点信息",
        "搜索点内容",
        "帮我查一下",
        "帮我找一下",
        "找找看",
        "查查看",
        "搜一下"
    ]
    
    search_success = 0
    for test in search_tests:
        intent = recognizer.recognize_intent(test)
        if intent and 'search' in intent.name.lower():
            print(f"  ✅ '{test}' → {intent.name} (置信度: {intent.confidence:.2f})")
            search_success += 1
        else:
            print(f"  ❌ '{test}' → {(intent.name if intent else 'None')}")
    
    print(f"  📊 搜索意图识别: {search_success}/{len(search_tests)} 通过")
    
    # 测试需要澄清的缺失参数情景
    print(f"\n🔄 参数缺失检测测试:")
    missing_param_tests = [
        # 这些应该被识别为create_wiki意图但需要澄清
        "创建维基",
        "写个维基", 
        "做个维基",
        "新建百科",
        "创建页面"
    ]
    
    clarification_needed = 0
    for test in missing_param_tests:
        intent = recognizer.recognize_intent(test)
        if intent and intent.name == "create_wiki":
            print(f"  🔄 '{test}' → {intent.name} (需要澄清: {getattr(intent, 'requires_clarification', False)})")
            if getattr(intent, 'requires_clarification', False):
                clarification_needed += 1
        else:
            print(f"  ❌ '{test}' → {(intent.name if intent else 'None')}")
    
    print(f"  📊 需要澄清的参数缺失检测: {clarification_needed}/{len(missing_param_tests)} 正确标记")
    
    # 综合功能测试
    print(f"\n🏆 综合测试结果:")
    total_tests = len(wiki_tests) + len(search_tests) + len(missing_param_tests)
    total_success = wiki_success + search_success + clarification_needed
    overall_accuracy = total_success / total_tests * 100
    
    print(f"  总体准确率: {overall_accuracy:.1f}% ({total_success}/{total_tests})")
    
    if overall_accuracy >= 80:
        print(f"  🎉 自然语言意图识别已显著改进！")
        print(f"  ✅ 用户可以用自然语言表达需求")
        print(f"  ✅ 系统能智能识别用户意图")
        print(f"  ✅ 缺少参数时自动提示用户")
        print(f"  ✅ 无需记忆复杂命令语法")
    else:
        print(f"  ⚠️  仍需进一步改进意图识别")
    
    print("="*70)
    
    return overall_accuracy >= 80

if __name__ == "__main__":
    success = test_improved_natural_language_recognition()
    print(f"\n🎯 最终结果: {'✅ 成功' if success else '⚠️ 待改进'}")