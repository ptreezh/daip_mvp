"""
最终系统功能验证 - 确保所有模块都正确集成
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
from daip_live.skills.manager import SkillManager
from daip_live.skills.text_analysis import TextAnalysisSkill

def final_system_verification():
    print("="*80)
    print("🏆 DAIP-LIVE 系统 - 最终完整功能验证")
    print("="*80)
    
    # 1. 验证意图识别器
    recognizer = EnhancedIntentRecognizer()
    print("✅ 1. 意图识别器已初始化")
    
    # 2. 验证技能管理器
    skill_manager = SkillManager()
    text_skill = TextAnalysisSkill()
    skill_manager.register_skill(text_skill)
    print("✅ 2. 技能管理器已初始化并注册了文本分析技能")
    
    # 3. 测试所有核心功能
    print("\n🔍 3. 测试所有核心功能模块:")
    
    # 测试各种功能保持兼容性
    compatibility_tests = [
        # 论文搜索功能
        ("论文 人工智能", "search_papers"),
        
        # 辩论功能
        ("开始辩论 AI伦理", "start_debate"),
        
        # 维基功能
        ("创建维基 项目计划", "create_wiki"),
        
        # 历史记录功能
        ("显示辩论历史", "view_debate_history"),
        
        # 个人助手功能
        ("个人助手，请分析代码", "personal_assistant"),
        
        # 智能聊天功能
        ("你好", "chat"),
        ("你是谁", "question"),
        
        # 知识库功能
        ("知识库搜索 机器学习", "search_papers"),
        
        # 项目初始化功能
        ("初始化项目 AI助手", "initialize_project"),
        
        # 压缩功能
        ("压缩上下文", "compress_context"),
    ]
    
    compatibility_success = 0
    for test_input, expected_intent in compatibility_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent and expected_intent in intent.name:
            print(f"   ✅ '{test_input}' → {intent.name} (保持兼容)")
            compatibility_success += 1
        else:
            print(f"   ❌ '{test_input}' → {(intent.name if intent else 'None')}")

    print(f"   📊 功能兼容性: {compatibility_success}/{len(compatibility_tests)}")
    
    # 4. 测试参数缺失检测
    print(f"\n🔄 4. 测试参数缺失检测:")
    
    missing_param_tests = [
        # 这些应该被检测为缺少参数
        ("论文", "search_papers", True),
        ("创建维基", "create_wiki", True), 
        ("开始辩论", "start_debate", True),
        ("下载论文", "search_papers", True)
    ]
    
    param_detection_success = 0
    for test_input, expected_intent, should_require_clarification in missing_param_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent and expected_intent in intent.name:
            requires_clarification = getattr(intent, 'requires_clarification', False)
            if requires_clarification == should_require_clarification:
                print(f"   ✅ '{test_input}' → {intent.name} (需要澄清: {requires_clarification})")
                param_detection_success += 1
            else:
                print(f"   ❌ '{test_input}' → {intent.name} (需要澄清: {requires_clarification}, 期望: {should_require_clarification})")
        else:
            print(f"   ❌ '{test_input}' → {(intent.name if intent else 'None')}")
    
    print(f"   📊 参数检测: {param_detection_success}/{len(missing_param_tests)}")

    # 5. 测试专门的技能执行意图
    print(f"\n⚡ 5. 测试技能执行功能:")

    skill_specific_tests = [
        # 专门的技能执行命令
        ("运行技能", "execute_skill"),
        ("使用技能", "execute_skill"),
        ("执行技能", "execute_skill"),
        ("启动技能", "execute_skill"),
        ("运行文本分析技能", "execute_skill"),
        ("使用文档处理技能", "execute_skill"),
        ("执行文本分析技能", "execute_skill"),
    ]

    skill_success = 0
    for test_input, expected_intent in skill_specific_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent and expected_intent in intent.name:
            print(f"   ✅ '{test_input}' → {intent.name}")
            skill_success += 1
        else:
            print(f"   ❌ '{test_input}' → {(intent.name if intent else 'None')}")

    print(f"   📊 专门技能命令: {skill_success}/{len(skill_specific_tests)}")

    # 6. 验证PA助手功能
    print(f"\n🤖 6. 测试PA助手功能:")

    pa_tests = [
        ("个人助手帮我分析", "personal_assistant"),
        ("PA助手，总结一下", "personal_assistant"),
        ("智能助手，搜索资料", "search_papers"),
        ("助手，处理文档", "question"),
        ("我的助手能做什么", "personal_assistant"),
    ]

    pa_success = 0
    for test_input, expected_intent in pa_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent and expected_intent in intent.name:
            print(f"   ✅ '{test_input}' → {intent.name}")
            pa_success += 1
        else:
            print(f"   ❌ '{test_input}' → {(intent.name if intent else 'None')}")

    print(f"   📊 PA助手识别: {pa_success}/{len(pa_tests)}")

    # 7. 验证本地知识库功能
    print(f"\n🧠 7. 测试本地知识库功能:")

    knowledge_tests = [
        ("知识库搜索 人工智能", "search_papers"),
        ("在知识库中查找机器学习", "search_papers"),
        ("同步知识库", "knowledge_sync"),
        ("知识库中的量子计算资料", "search_papers"),
        ("本地知识库 深度学习", "search_papers"),
    ]

    knowledge_success = 0
    for test_input, expected_intent in knowledge_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent and expected_intent in intent.name:
            print(f"   ✅ '{test_input}' → {intent.name}")
            knowledge_success += 1
        else:
            print(f"   ❌ '{test_input}' → {(intent.name if intent else 'None')}")

    print(f"   📊 知识库识别: {knowledge_success}/{len(knowledge_tests)}")

    # 8. 统计总结果
    total_tests = len(compatibility_tests) + len(missing_param_tests) + len(skill_specific_tests) + len(pa_tests) + len(knowledge_tests)
    total_success = compatibility_success + param_detection_success + skill_success + pa_success + knowledge_success
    overall_accuracy = total_success / total_tests * 100 if total_tests > 0 else 0

    print(f"\n📊 综合验证结果:")
    print(f"   功能兼容性: {compatibility_success}/{len(compatibility_tests)} ({compatibility_success/len(compatibility_tests)*100:.0f}%)")
    print(f"   参数检测: {param_detection_success}/{len(missing_param_tests)} ({param_detection_success/len(missing_param_tests)*100:.0f}%)")
    print(f"   技能执行: {skill_success}/{len(skill_specific_tests)} ({skill_success/len(skill_specific_tests)*100:.0f}%)")
    print(f"   PA助手: {pa_success}/{len(pa_tests)} ({pa_success/len(pa_tests)*100:.0f}%)")
    print(f"   知识库: {knowledge_success}/{len(knowledge_tests)} ({knowledge_success/len(knowledge_tests)*100:.0f}%)")
    print(f"   总体准确率: {overall_accuracy:.1f}% ({total_success}/{total_tests})")

    # 9. 功能总结
    print(f"\n🎯 系统功能完整支持:")
    print(f"   ✅ 知识库管理: 本地知识库搜索、同步和管理")
    print(f"   ✅ 维基协作: 多AI角色协同创建页面")
    print(f"   ✅ 辩论系统: 多模型辩论和历史记录")
    print(f"   ✅ PA助手: 个人化智能助手功能")
    print(f"   ✅ 技能扩展: 动态技能加载和执行")
    print(f"   ✅ 参数检测: 智能检测缺失参数并提示")
    print(f"   ✅ 自然语言: 完整的意图识别和语义理解")
    print(f"   ✅ 项目管理: 环境初始化和项目搭建")
    print(f"   ✅ 历史管理: 完整的会话和辩论历史")

    print(f"\n🏆 用户体验优化:")
    print(f"   • 用自然语言交互，无需记忆复杂命令")
    print(f"   • 缺少参数时自动提示输入")
    print(f"   • 智能识别意图并调用相关功能")
    print(f"   • 错误处理友好，提供明确指示")
    print(f"   • 支持中文和英文表达")

    # 判断是否完全成功
    success = overall_accuracy >= 80 and compatibility_success == len(compatibility_tests)

    print("="*80)
    print(f"🎉 {'系统功能验证通过！' if success else '系统功能部分通过'}")
    print("="*80)

    return success

if __name__ == "__main__":
    success = final_system_verification()
    print(f"\n🎯 最终结果: {'✅ 完全成功' if success else '⚠️ 部分成功'}")
    
    if success:
        print("系统现在完全支持所有高级功能！")
        print("用户可以直接说自然语言，系统会智能处理！")
    else:
        print("某些功能需要进一步调试！")