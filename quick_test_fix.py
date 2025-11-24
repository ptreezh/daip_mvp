"""
简单验证修复后的意图识别功能
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_fixed_recognizer():
    print("Testing improved intent recognition...")
    
    recognizer = EnhancedIntentRecognizer()
    
    test_inputs = [
        "你是谁",
        "帮我写代码",  
        "？",  # 问号模式
        "怎么做",
        "怎么办"
    ]
    
    for text in test_inputs:
        intent = recognizer.recognize_intent(text)
        if intent:
            print(f"'{text}' → {intent.name} (confidence: {intent.confidence:.2f})")
        else:
            print(f"'{text}' → No intent recognized")

if __name__ == "__main__":
    test_fixed_recognizer()