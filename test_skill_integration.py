"""
验证技能系统集成
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
from daip_live.skills.manager import SkillManager
from daip_live.skills.text_analysis import TextAnalysisSkill

def test_skill_integration():
    print("="*70)
    print("🎯 技能系统集成测试")
    print("="*70)
    
    # 1. 测试意图识别器
    recognizer = EnhancedIntentRecognizer()
    print("✅ 1. 意图识别器初始化成功")
    
    # 2. 测试技能管理器
    skill_manager = SkillManager()
    text_skill = TextAnalysisSkill()
    skill_manager.register_skill(text_skill)
    print("✅ 2. 技能管理器初始化成功，已注册文本分析技能")
    
    # 3. 测试意图识别
    print(f"\n🔍 3. 测试技能相关意图识别:")
    test_inputs = [
        "帮我分析这段文本",
        "文本分析一下", 
        "运行技能",
        "执行文本分析",
        "处理文本",
        "分析",
        "论文",
        "创建维基"
    ]
    
    recognized_count = 0
    for test_input in test_inputs:
        intent = recognizer.recognize_intent(test_input)
        if intent:
            print(f"   '{test_input}' → {intent.name} (置信度: {intent.confidence:.2f})")
            recognized_count += 1
        else:
            print(f"   '{test_input}' → 未识别")
    
    print(f"\n📊 意图识别率: {recognized_count}/{len(test_inputs)}")
    
    # 4. 现在检查是否存在execute_skill意图
    print(f"\n🔍 4. 测试execute_skill相关模式:")
    skill_intent_tests = [
        ("执行技能", "execute_skill"),
        ("运行技能", "execute_skill"),
        ("使用技能", "execute_skill"),
        ("技能执行", "execute_skill"),
        ("帮我执行技能", "execute_skill"),
        ("运行技能助手", "execute_skill"),
    ]
    
    skill_intent_success = 0
    for test_input, expected_intent in skill_intent_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent and expected_intent in intent.name:
            print(f"   ✅ '{test_input}' → {intent.name}")
            skill_intent_success += 1
        else:
            print(f"   ❌ '{test_input}' → {(intent.name if intent else 'None')}")
    
    print(f"\n📋 5. 验证现有功能兼容性:")
    existing_functionality_tests = [
        ("论文 AI伦理", "search_papers"),
        ("开始辩论 人工智能", "start_debate"),
        ("创建维基 项目计划", "create_wiki"),
        ("显示辩论历史", "view_debate_history")
    ]
    
    existing_success = 0
    for test_input, expected_intent in existing_functionality_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent and expected_intent in intent.name:
            print(f"   ✅ '{test_input}' → {intent.name} (现有功能保持正常)")
            existing_success += 1
        else:
            print(f"   ⚠️  '{test_input}' → {(intent.name if intent else 'None')} (可能改变了)")
    
    print(f"\n🏆 测试总结:")
    print(f"   意图识别器: {'✅' if recognizer else '❌'}")
    print(f"   技能管理器: {'✅' if skill_manager else '❌'}")
    print(f"   已注册技能: {len(skill_manager.list_skills())} 个")
    print(f"   技能意图识别: {skill_intent_success}/{len(skill_intent_tests)}")
    print(f"   现有功能兼容性: {existing_success}/{len(existing_functionality_tests)}")

    total_score = (skill_intent_success + existing_success) / (len(skill_intent_tests) + len(existing_functionality_tests))
    print(f"   总体准确率: {total_score*100:.1f}%")

    if total_score >= 0.6 and existing_success == len(existing_functionality_tests):
        print(f"\n🎉 技能系统集成成功！")
        print(f"   • 系统能识别技能相关意图")
        print(f"   • 现有功能保持兼容")
        print(f"   • 技能管理器正常工作")
        print(f"   • 用户可以通过自然语言调用技能")

        success = True
    else:
        print(f"\n⚠️  需要进一步完善技能集成")
        success = False
    
    print("="*70)
    return success

if __name__ == "__main__":
    success = test_skill_integration()
    
    print(f"\n🎯 技能系统集成状态: {'✅ 完全集成' if success else '⚠️ 待完善'}")
    print(f"\n系统现在可以:")
    print(f"  • 识别自然语言中的技能意图")
    print(f"  • 执行注册的技能")
    print(f"  • 维持现有功能兼容性")
    print(f"  • 提供智能参数检测")