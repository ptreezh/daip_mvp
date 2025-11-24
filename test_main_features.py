"""
测试增强意图识别器的主要功能模块
"""
import sys
sys.path.insert(0, './src')

import asyncio
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
from daip_live.skills.manager import SkillManager
from daip_live.skills.text_analysis import TextAnalysisSkill


def test_main_feature_accuracy():
    print("="*90)
    print("🧪 测试主要功能模块的意图识别准确率")
    print("="*90)

    recognizer = EnhancedIntentRecognizer()
    skill_manager = SkillManager()
    text_skill = TextAnalysisSkill()
    skill_manager.register_skill(text_skill)

    # 测试所有主要功能
    main_feature_tests = [
        # 论文搜索
        ("论文 人工智能", "search_papers"),
        ("搜索机器学习论文", "search_papers"),
        ("查找量子计算相关文献", "search_papers"),

        # 维基协作
        ("创建维基 项目计划", "create_wiki"),
        ("写个维基 深度学习", "create_wiki"),

        # 辩论系统
        ("开始辩论 AI伦理", "start_debate"),
        ("发起关于量子计算的辩论", "start_debate"),
        ("显示辩论历史", "view_debate_history"),

        # PA助手
        ("个人助手帮我分析", "personal_assistant"),
        ("智能助手总结一下", "question"),

        # 技能系统
        ("帮我分析这段文本", "execute_skill"),
        ("执行文本分析", "execute_skill"),
        ("使用技能处理文档", "execute_skill"),

        # 知识库
        ("知识库搜索 机器学习", "search_papers"),
        ("本地知识查找", "knowledge_search"),

        # 基础交互
        ("你好", "chat"),
        ("你是谁", "question"),
        ("？", "question")
    ]

    main_success = 0
    for test_input, expected_intent in main_feature_tests:
        intent = recognizer.recognize_intent(test_input)
        if intent and expected_intent in intent.name:
            main_success += 1
            print(f"   ✅ '{test_input} → {intent.name}'")
        else:
            print(f"   ❌ '{test_input}' → {(intent.name if intent else 'None')} (期望: {expected_intent})")

    main_accuracy = main_success / len(main_feature_tests) * 100
    print(f"\n📊 主要功能准确率: {main_success}/{len(main_feature_tests)} ({main_accuracy:.1f}%)")
    return main_accuracy, main_success, len(main_feature_tests)


if __name__ == "__main__":
    accuracy, success, total = test_main_feature_accuracy()
    print(f"\n🎯 意图识别准确率测试完成: {accuracy:.1f}% ({success}/{total})")