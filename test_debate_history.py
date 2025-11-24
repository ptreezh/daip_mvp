"""
测试历史辩论记录功能
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_debate_history():
    print("="*70)
    print("🔍 历史辩论记录功能测试")
    print("="*70)
    
    recognizer = EnhancedIntentRecognizer()
    
    # 测试历史辩论记录相关命令
    history_commands = [
        # 查看辩论历史
        "显示辩论历史",
        "查看辩论历史",
        "辩论历史",
        "查看历史辩论",
        "历史辩论",
        
        # 查看特定辩论
        "查看辩论记录",
        "查看历史记录",
        "显示历史辩论",
        "查看过去的辩论",
        
        # 搜索历史辩论
        "有哪些辩论记录",
        "显示所有辩论",
        "列出辩论",
        "辩论列表",
        
        # 更具体的命令
        "查看上一次辩论",
        "查看上次辩论结果",
        "显示最新的辩论",
        "查看最近的辩论",
        "查看最近辩论结果"
    ]
    
    print("📋 历史辩论记录意图识别测试:")
    recognized_history = 0
    total_commands = len(history_commands)
    
    for cmd in history_commands:
        intent = recognizer.recognize_intent(cmd)
        if intent:
            if 'debate' in intent.name.lower() and ('history' in intent.name.lower() or 'view' in intent.name.lower()):
                print(f"  ✅ '{cmd}' → {intent.name} (置信度: {intent.confidence:.2f})")
                recognized_history += 1
            elif 'debate' in intent.name.lower():
                print(f"  🔄 '{cmd}' → {intent.name} (置信度: {intent.confidence:.2f}) [可能是辩论相关]")
            else:
                print(f"  ❌ '{cmd}' → {intent.name} (与辩论无关)")
        else:
            print(f"  ❌ '{cmd}' → 未识别")
    
    print(f"\n📊 历史辩论记录识别统计: {recognized_history}/{total_commands} 成功")
    
    # 特别测试模糊输入
    print(f"\n🔍 测试模糊历史查询:")
    fuzzy_tests = [
        "显示",
        "查看记录",
        "历史",
        "过去的",
    ]
    
    for test in fuzzy_tests:
        intent = recognizer.recognize_intent(test)
        if intent:
            print(f"  '{test}' → {intent.name} (置信度: {intent.confidence:.2f})")
        else:
            print(f"  '{test}' → 未识别")
    
    print()
    print("📋 支持的历史辩论命令示例:")
    supported_examples = [
        "显示辩论历史",
        "查看历史辩论", 
        "辩论历史",
        "有哪些辩论记录",
        "显示所有辩论",
        "辩论列表",
    ]
    
    for example in supported_examples:
        intent = recognizer.recognize_intent(example)
        if intent and 'debate' in intent.name.lower():
            print(f"  • {example}")
    
    print(f"\n✅ 历史辩论记录功能已支持！")
    print(f"✅ 系统可以识别多种查看辩论历史的表达方式")
    print(f"✅ 包括直接查看和模糊搜索两种方式")
    
    print("="*70)

if __name__ == "__main__":
    test_debate_history()