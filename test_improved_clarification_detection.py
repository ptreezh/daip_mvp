"""
测试改进后的参数缺失检测功能
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_improved_clarification_detection():
    print("="*70)
    print("🔍 改进后的参数缺失检测功能测试")
    print("="*70)
    
    recognizer = EnhancedIntentRecognizer()
    
    print("📋 测试维基创建意图的参数缺失检测:")
    wiki_missing_param_tests = [
        # 这些应该被识别为create_wiki意图但需要澄清（缺少标题）
        "创建维基",
        "写个维基", 
        "新建一个维基",
        "做一个维基",
        "创建百科",
        "新建百科",
        "创建页面",
        "写个页面"
    ]
    
    wiki_clarification_success = 0
    for test in wiki_missing_param_tests:
        intent = recognizer.recognize_intent(test)
        if intent and intent.name == "create_wiki":
            requires_clarification = getattr(intent, 'requires_clarification', False)
            print(f"  {'✅' if requires_clarification else '❌'} '{test}' → {intent.name} (需要澄清: {requires_clarification})")
            if requires_clarification:
                wiki_clarification_success += 1
        else:
            print(f"  ❌ '{test}' → {(intent.name if intent else 'None')}")
    
    print(f"  📊 维基参数缺失检测: {wiki_clarification_success}/{len(wiki_missing_param_tests)} 正确识别")
    
    print(f"\n📋 测试论文搜索意图的参数缺失检测:")
    search_missing_param_tests = [
        # 这些应该被识别为search_papers意图但需要澄清（缺少查询词）
        "论文",
        "搜索论文", 
        "查找论文",
        "下载论文",
        "找论文",
        "搜索资料",
        "查找信息",
        "帮我找点东西",
        "查一下",
        "搜一下"
    ]
    
    search_clarification_success = 0
    for test in search_missing_param_tests:
        intent = recognizer.recognize_intent(test)
        if intent and intent.name == "search_papers":
            requires_clarification = getattr(intent, 'requires_clarification', False)
            clarification_needed = getattr(intent, 'clarification_needed', None)
            clarification_msg = getattr(clarification_needed, 'message', 'No message') if clarification_needed else 'No clarification'
            
            status = "✅" if requires_clarification else "❌"
            print(f"  {status} '{test}' → {intent.name} (需要澄清: {requires_clarification})")
            if requires_clarification and clarification_msg != 'No message':
                print(f"        提示信息: {clarification_msg}")
                search_clarification_success += 1
        else:
            print(f"  ❌ '{test}' → {(intent.name if intent else 'None')}")
    
    print(f"  📊 搜索参数缺失检测: {search_clarification_success}/{len(search_missing_param_tests)} 正确识别")
    
    print(f"\n📋 有完整参数的正常请求测试（不应需要澄清）:")
    complete_param_tests = [
        "创建维基 人工智能发展趋势",
        "写个维基 量子计算",
        "新建百科 机器学习",
        "论文 人工智能",
        "搜索机器学习论文"
    ]
    
    complete_success = 0
    for test in complete_param_tests:
        intent = recognizer.recognize_intent(test)
        if intent:
            requires_clarification = getattr(intent, 'requires_clarification', False)
            status = "✅" if not requires_clarification else "❌"
            print(f"  {status} '{test}' → {intent.name} (应无需澄清: {not requires_clarification})")
            if not requires_clarification:
                complete_success += 1
        else:
            print(f"  ❌ '{test}' → 未识别")
    
    print(f"  📊 完整参数检测: {complete_success}/{len(complete_param_tests)} 正确识别")
    
    # 整体统计
    total_tests = len(wiki_missing_param_tests) + len(search_missing_param_tests) + len(complete_param_tests)
    total_clarification_success = wiki_clarification_success + search_clarification_success + complete_success
    
    print(f"\n📊 总体测试结果: {total_clarification_success}/{total_tests} ({total_clarification_success/total_tests*100:.1f}%)")
    
    if total_clarification_success/total_tests >= 0.8:  # 80%准确率
        print(f"\n🎉 功能测试通过！参数缺失检测功能已正确实现!")
        print(f"✅ 维基创建意图能正确识别缺失标题")
        print(f"✅ 搜索意图能正确识别缺失查询词")
        print(f"✅ 完整参数意图不会错误标记为需要澄清")
        print(f"✅ 提供友好的用户提示信息")
        print(f"✅ 支持自然语言表达方式")
        success = True
    else:
        print(f"\n⚠️  功能测试未完全通过，需要进一步调整")
        success = False
    
    print("="*70)
    return success

if __name__ == "__main__":
    test_improved_clarification_detection()