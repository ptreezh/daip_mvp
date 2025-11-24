"""
测试修复后的意图识别优先级
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_intent_priority_resolution():
    print("="*80)
    print("🎯 测试意图识别优先级修复")
    print("="*80)
    
    recognizer = EnhancedIntentRecognizer()
    
    # 重点测试搜索和技能意图的区分
    print("🔍 搜索意图 vs 技能意图 区分测试:")
    
    # 这些应该是搜索意图而不是技能意图
    search_specific_tests = [
        ("论文 人工智能", "search_papers"),
        ("论文 深度学习", "search_papers"),
        ("搜索机器学习论文", "search_papers"),
        ("查找量子计算资料", "search_papers"),
        ("下载学术论文", "search_papers"),
        ("搜索学术资料", "search_papers"),
        ("论文 AI伦理", "search_papers"),
        ("搜索关于AI的论文", "search_papers"),
    ]
    
    # 这些应该是技能意图
    skill_specific_tests = [
        ("帮我分析这段文本", "execute_skill"),
        ("帮我处理这个问题", "execute_skill"),
        ("帮我总结这份报告", "execute_skill"),
        ("请帮我分析", "execute_skill"),
        ("帮我写个维基", "execute_skill"),
        ("执行技能分析", "execute_skill"),
        ("运行分析技能", "execute_skill"),
    ]
    
    search_correct = 0
    total_search = len(search_specific_tests)
    
    print(f"\n📋 搜索意图测试 ({total_search} 个):")
    for test, expected in search_specific_tests:
        intent = recognizer.recognize_intent(test)
        if intent and expected in intent.name:
            print(f"  ✅ '{test}' → {intent.name}")
            search_correct += 1
        else:
            print(f"  ❌ '{test}' → {(intent.name if intent else 'None')}")
    
    skill_correct = 0
    total_skill = len(skill_specific_tests)
    
    print(f"\n📋 技能意图测试 ({total_skill} 个):")
    for test, expected in skill_specific_tests:
        intent = recognizer.recognize_intent(test)
        if intent and expected in intent.name:
            print(f"  ✅ '{test}' → {intent.name}")
            skill_correct += 1
        else:
            print(f"  ❌ '{test}' → {(intent.name if intent else 'None')}")
    
    print(f"\n📊 修复后意图识别统计:")
    print(f"  搜索意图准确率: {search_correct}/{total_search} ({search_correct/total_search*100:.1f}%)")
    print(f"  技能意图准确率: {skill_correct}/{total_skill} ({skill_correct/total_skill*100:.1f}%)")
    
    overall_accuracy = (search_correct + skill_correct) / (total_search + total_skill) * 100
    print(f"  总体准确率: {(search_correct + skill_correct)}/{(total_search + total_skill)} ({overall_accuracy:.1f}%)")
    
    # 测试参数澄清功能
    print(f"\n🔄 参数缺失检测验证:")
    missing_param_tests = [
        ("论文", True),  # 应该需要澄清
        ("搜索论文", True),  # 应该需要澄清
        ("创建维基", True),  # 应该需要澄清
        ("开始辩论", True),  # 应该需要澄清
        ("帮我", True),     # 应该需要澄清
    ]
    
    param_clarification_correct = 0
    for test, should_require_clarification in missing_param_tests:
        intent = recognizer.recognize_intent(test)
        if intent:
            actual_clarification = getattr(intent, 'requires_clarification', False)
            status = "✅" if actual_clarification == should_require_clarification else "❌"
            print(f"  {status} '{test}' → {intent.name} (需要澄清: {actual_clarification}, 期望: {should_require_clarification})")
            if actual_clarification == should_require_clarification:
                param_clarification_correct += 1
        else:
            print(f"  ❌ '{test}' → 未识别")
    
    param_accuracy = param_clarification_correct / len(missing_param_tests) * 100
    print(f"  参数澄清准确率: {param_clarification_correct}/{len(missing_param_tests)} ({param_accuracy:.1f}%)")
    
    print(f"\n🏆 修复效果评估:")
    print(f"  ✅ 搜索意图: {'✅' if search_correct/total_search >= 0.8 else '❌'}")
    print(f"  ✅ 技能意图: {'✅' if skill_correct/total_skill >= 0.8 else '❌'}")  
    print(f"  ✅ 参数澄清: {'✅' if param_accuracy >= 0.8 else '❌'}")
    print(f"  ✅ 总体表现: {'✅' if overall_accuracy >= 0.8 else '❌'}")
    
    success = (search_correct/total_search >= 0.5 and 
              skill_correct/total_skill >= 0.5 and 
              param_accuracy >= 0.5)
    
    print(f"\n🎯 修复后系统状态: {'✅ 大幅改进' if success else '⚠️ 仍需调整'}")
    
    print("="*80)
    return success

if __name__ == "__main__":
    success = test_intent_priority_resolution()
    print(f"\n最终验证结果: {'✅ 意图优先级修复成功' if success else '❌ 意图优先级仍需优化'}")