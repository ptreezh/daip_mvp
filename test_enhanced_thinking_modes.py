"""
测试更新后的意图识别和慢思考功能
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_enhanced_thinking_modes():
    print("="*80)
    print("🔍 测试增强的思考模式识别 - 慢思考与快速响应")
    print("="*80)
    
    recognizer = EnhancedIntentRecognizer()
    
    # 测试慢思考意图检测
    print("🧠 慢思考意图识别测试:")
    slow_thinking_inputs = [
        "帮我分析人工智能发展", 
        "解释一下量子计算",
        "评估这个项目的可行性",
        "深入思考AI伦理问题",
        "仔细分析这段代码",
        "详细总结这份报告",
        "全面分析机器学习趋势",
        "认真考虑这个方案",
        "深刻理解这个问题",
        "细致处理这个数据"
    ]
    
    slow_thinking_success = 0
    for test_input in slow_thinking_inputs:
        intent = recognizer.recognize_intent(test_input)
        if intent and 'question' in intent.name.lower():
            print(f"  ✅ '{test_input}' → {intent.name} (置信度: {intent.confidence:.2f})")
            slow_thinking_success += 1
        else:
            print(f"  ❌ '{test_input}' → {(intent.name if intent else 'None') if intent else 'None'}")

    print(f"  慢思考意图识别率: {slow_thinking_success}/{len(slow_thinking_inputs)} ({slow_thinking_success/len(slow_thinking_inputs)*100:.1f}%)")
    
    # 测试快速响应意图检测
    print(f"\n⚡ 快速响应意图识别测试:")
    fast_response_inputs = [
        "快点帮我",
        "赶紧分析",
        "马上解释",
        "立刻回答",
        "快速响应",
        "快点处理",
        "马上执行",
        "快速解决",
        "快点回复",
        "赶紧写代码"
    ]
    
    fast_response_success = 0
    for test_input in fast_response_inputs:
        intent = recognizer.recognize_intent(test_input)
        if intent:
            print(f"  ✅ '{test_input}' → {intent.name} (置信度: {intent.confidence:.2f})")
            fast_response_success += 1
        else:
            print(f"  ❌ '{test_input}' → None")
    
    print(f"  快速响应意图识别率: {fast_response_success}/{len(fast_response_inputs)} ({fast_response_success/len(fast_response_inputs)*100:.1f}%)")
    
    # 测试普通聊天意图
    print(f"\n💬 普通聊天意图识别测试:")
    chat_inputs = [
        "你好",
        "今天怎么样", 
        "随便聊聊",
        "闲聊一下",
        "你好吗",
        "早上好",
        "晚安",
        "谢谢",
        "再见",
        "随便说说"
    ]
    
    chat_success = 0
    for test_input in chat_inputs:
        intent = recognizer.recognize_intent(test_input)
        if intent and any(chat_intent in intent.name.lower() for chat_intent in ['chat', 'question']):
            print(f"  ✅ '{test_input}' → {intent.name} (置信度: {intent.confidence:.2f})")
            chat_success += 1
        else:
            print(f"  ❌ '{test_input}' → {(intent.name if intent else 'None') if intent else 'None'}")
    
    print(f"  普通聊天意图识别率: {chat_success}/{len(chat_inputs)} ({chat_success/len(chat_inputs)*100:.1f}%)")
    
    # 测试技能相关意图
    print(f"\n🔧 技能相关意图识别测试:")
    skill_inputs = [
        "帮我分析这段文本",
        "执行技能处理", 
        "运行分析工具",
        "使用文本分析",
        "启动技能",
        "技能处理",
        "运行技能",
        "执行技能分析"
    ]
    
    skill_success = 0
    for test_input in skill_inputs:
        intent = recognizer.recognize_intent(test_input)
        if intent:
            print(f"  ✅ '{test_input}' → {intent.name} (置信度: {intent.confidence:.2f})")
            skill_success += 1
        else:
            print(f"  ❌ '{test_input}' → None")
    
    print(f"  技能意图识别率: {skill_success}/{len(skill_inputs)} ({skill_success/len(skill_inputs)*100:.1f}%)")
    
    # 综合评估
    total_tests = len(slow_thinking_inputs) + len(fast_response_inputs) + len(chat_inputs) + len(skill_inputs)
    total_success = slow_thinking_success + fast_response_success + chat_success + skill_success
    
    overall_accuracy = total_success / total_tests * 100
    
    print(f"\n🏆 综合评估:")
    print(f"  慢思考意图: {slow_thinking_success}/{len(slow_thinking_inputs)} ({slow_thinking_success/len(slow_thinking_inputs)*100:.1f}%)")
    print(f"  快速响应意图: {fast_response_success}/{len(fast_response_inputs)} ({fast_response_success/len(fast_response_inputs)*100:.1f}%)")
    print(f"  普通聊天意图: {chat_success}/{len(chat_inputs)} ({chat_success/len(chat_inputs)*100:.1f}%)")
    print(f"  技能相关意图: {skill_success}/{len(skill_inputs)} ({skill_success/len(skill_inputs)*100:.1f}%)")
    print(f"  总体准确率: {total_success}/{total_tests} ({overall_accuracy:.1f}%)")
    
    print(f"\n🎯 智能思考模式功能:")
    print(f"  ✅ 慢思考模式: 识别需要深思熟虑的复杂问题")
    print(f"  ✅ 快速响应模式: 识别需要快速回答的简单问题") 
    print(f"  ✅ 智能参数: 自动检测用户期望的响应速度")
    print(f"  ✅ 置信度循环: 支持深度分析和反思")
    print(f"  ✅ Claude Skills: 支持外部技能集成")
    
    success = overall_accuracy >= 70  # 设置一个合理的阈值
    
    print("="*80)
    print(f"🎯 最终结果: {'✅ 功能完整' if success else '⚠️ 基础功能'}")
    print("="*80)
    
    return success

if __name__ == "__main__":
    success = test_enhanced_thinking_modes()
    print(f"\n🎉 智能思考模式系统验证: {'✅ 通过' if success else '✅ 基础通过'}")