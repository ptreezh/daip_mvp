import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_intents():
    recognizer = EnhancedIntentRecognizer()
    print('🔍 测试修复后的意图识别准确性:')

    # 测试原有功能不被影响
    existing_tests = [
        ('论文 人工智能', 'search_papers'),
        ('开始辩论 AI伦理', 'start_debate'), 
        ('创建维基 项目计划', 'create_wiki'),
        ('显示辩论历史', 'view_debate_history'),
        ('你好', 'chat'),
        ('你是谁', 'question'),
    ]

    existing_success = 0
    for input_text, expected_intent in existing_tests:
        intent = recognizer.recognize_intent(input_text)
        if intent and expected_intent in intent.name:
            print("  ✅ '{}' -> {}".format(input_text, intent.name))
            existing_success += 1
        else:
            print("  ❌ '{}' -> {}".format(input_text, (intent.name if intent else 'None')))

    # 测试新的明确技能意图
    skill_tests = [
        ('运行技能', 'execute_skill'),
        ('使用技能', 'execute_skill'), 
        ('执行技能', 'execute_skill'),
        ('运行文本分析技能', 'execute_skill'),
        ('使用文档处理技能', 'execute_skill'),
    ]

    skill_success = 0
    for input_text, expected_intent in skill_tests:
        intent = recognizer.recognize_intent(input_text)
        if intent and expected_intent in intent.name:
            print("  ✅ [技能] '{}' -> {}".format(input_text, intent.name))
            skill_success += 1
        else:
            print("  ❌ [技能] '{}' -> {}".format(input_text, (intent.name if intent else 'None')))

    print('')
    print('📊 测试结果:')
    print('  原有功能准确性: {}/{} ({:.0f}%)'.format(existing_success, len(existing_tests), existing_success/len(existing_tests)*100))
    print('  技能功能准确性: {}/{} ({:.0f}%)'.format(skill_success, len(skill_tests), skill_success/len(skill_tests)*100 if len(skill_tests) > 0 else 0))

if __name__ == "__main__":
    test_intents()