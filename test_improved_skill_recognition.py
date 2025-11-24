"""
测试改进后的技能识别
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_improved_skill_recognition():
    print("="*80)
    print("🔍 测试改进后的自然语言技能识别")
    print("="*80)
    
    recognizer = EnhancedIntentRecognizer()
    
    # 测试增强后的技能意图识别
    print("📋 测试自然语言技能请求识别:")
    skill_related_tests = [
        # 原先可能未识别的
        "帮我分析这段文本",
        "帮我处理这个文档",
        "帮我总结这份报告",
        "帮我生成一个计划",
        "请帮我搜索相关信息",
        "帮我翻译这段话",
        "帮我整理这些资料",
        
        # 简单请求
        "分析一下",
        "处理这个",
        "搜索一下",
        "翻译一下",
        "总结一下",
        
        # 助手请求
        "智能助手帮我",
        "AI助手分析",
        "个人助手处理",
        "PA助手搜索",
    ]
    
    recognized_as_skill = 0
    for test_input in skill_related_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent:
            if intent.name == "execute_skill":
                print(f"  ✅ '{test_input}' → {intent.name}")
                recognized_as_skill += 1
            else:
                print(f"  ➡️  '{test_input}' → {intent.name} (非技能意图)")
        else:
            print(f"  ❌ '{test_input}' → 未识别")
    
    print(f"  📊 技能识别准确率: {recognized_as_skill}/{len(skill_related_tests)} ({recognized_as_skill/len(skill_related_tests)*100:.1f}%)")
    
    # 测试参数缺失检测
    print(f"\n🔄 测试技能参数缺失检测:")
    missing_param_tests = [
        "帮我分析",
        "分析", 
        "处理",
        "帮我处理",
        "搜索",
        "帮我搜索",
        "帮我总结",
        "创建维基"
    ]
    
    param_missing_detected = 0
    for test_input in missing_param_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent and intent.name == "execute_skill":
            requires_clarification = getattr(intent, 'requires_clarification', False)
            clarification_msg = getattr(intent, 'clarification_needed', None)

            if requires_clarification and clarification_msg:
                print(f"  ✅ '{test_input}' → 需要澄清: {getattr(clarification_msg, 'message', '有澄清信息')[:50]}...")
                param_missing_detected += 1
            else:
                print(f"  ❌ '{test_input}' → 已识别但无澄清需求")
        else:
            print(f"  ❌ '{test_input}' → 未识别为技能意图")

    print(f"  📊 参数缺失检测: {param_missing_detected}/{len(missing_param_tests)} ({param_missing_detected/len(missing_param_tests)*100:.1f}%)")

    # 检查完整参数是否不需要澄清
    print(f"\n✅ 检查完整参数请求是否不需澄清:")
    complete_param_tests = [
        "帮我分析人工智能发展趋势",
        "帮我处理量子计算文档",
        "分析这段AI伦理文本",
        "处理项目计划文档"
    ]

    complete_no_clarification = 0
    for test_input in complete_param_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent and intent.name == "execute_skill":
            requires_clarification = getattr(intent, 'requires_clarification', False)
            if not requires_clarification:
                print(f"  ✅ '{test_input}' → 已识别但无需澄清")
                complete_no_clarification += 1
            else:
                print(f"  ❌ '{test_input}' → 错误标记为需要澄清")
        else:
            print(f"  ❌ '{test_input}' → 未识别为技能意图")

    print(f"  📊 完整参数请求检测: {complete_no_clarification}/{len(complete_param_tests)} ({complete_no_clarification/len(complete_param_tests)*100:.1f}%)")

    # 总体评估
    print(f"\n🏆 最终评估:")
    total_tests = len(skill_related_tests) + len(missing_param_tests) + len(complete_param_tests)
    total_success = recognized_as_skill + param_missing_detected + complete_no_clarification
    overall_accuracy = total_success / total_tests * 100

    print(f"   总体准确率: {overall_accuracy:.1f}% ({total_success}/{total_tests})")
    print(f"   自然语言技能识别: {recognized_as_skill}/{len(skill_related_tests)} ({recognized_as_skill/len(skill_related_tests)*100:.1f}%)")
    print(f"   参数缺失检测: {param_missing_detected}/{len(missing_param_tests)} ({param_missing_detected/len(missing_param_tests)*100:.1f}%)")
    print(f"   完整参数检测: {complete_no_clarification}/{len(complete_param_tests)} ({complete_no_clarification/len(complete_param_tests)*100:.1f}%)")

    if overall_accuracy >= 70:
        print(f"\n🎉 系统现在能够智能识别和处理技能相关的自然语言请求！")
        print(f"✅ 用户可以直接说自然语言触发技能执行")
        print(f"✅ 系统能智能检测参数是否完整")
        print(f"✅ 缺少参数时自动提示用户补全")
        print(f"✅ 支持多样的自然语言表达方式")
        success = True
    else:
        print(f"\n⚠️  系统仍需改进技能识别能力")
        success = False
    
    print("="*80)
    return success

if __name__ == "__main__":
    success = test_improved_skill_recognition()
    print(f"\n🎯 测试结果: {'✅ 成功' if success else '⚠️ 待改进'}")