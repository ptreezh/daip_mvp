"""
测试中文字符编码和实际匹配
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_actual_chinese_matching():
    print("🔍 测试中文字符的实际匹配")
    print("="*50)
    
    recognizer = EnhancedIntentRecognizer()
    
    # 测试用户实际输入的字符串（通过复制粘贴确保编码一致）
    test_inputs = [
        "辩论下 女权与AI冲突",
        "辩论一下 AI伦理问题",
        "让我们辩论 AI对社会的影响",
        "开始辩论 人工智能的未来发展",
    ]
    
    print("测试辩论意图模式匹配:")
    for test_input in test_inputs:
        intent = recognizer.recognize_intent(test_input)
        if intent:
            print(f"  ✅ '{test_input}' → {intent.name} (置信度: {intent.confidence:.2f})")
        else:
            print(f"  ❌ '{test_input}' → 未识别")
    
    print()
    
    # 检查字符
    for test_input in test_inputs:
        print(f"输入: '{test_input}'")
        print(f"字符: {[hex(ord(c)) for c in test_input[:4]]}")  # 显示前几个字符的编码
        print()
    
    # 现在手动测试正则表达式
    import re
    
    print("手动正则表达式测试:")
    patterns_to_test = [
        r"辩论.*下",
        r"辩论.*一下", 
        r"辩论.*吧",
        r"辩论.*",
        r"让我.*辩论.*",
        r"辩论.*下.*"
    ]
    
    for test_input in test_inputs[:2]:  # 只测试前两个
        print(f"\n输入: '{test_input}'")
        for pattern in patterns_to_test:
            match = re.search(pattern, test_input, re.IGNORECASE)
            if match:
                print(f"  ✓ '{pattern}' → '{match.group(0)}'")
            else:
                print(f"  ❌ '{pattern}' → 无匹配")

if __name__ == "__main__":
    test_actual_chinese_matching()