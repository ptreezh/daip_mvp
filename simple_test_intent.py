"""
简单测试修复后的技能参数提取功能
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def simple_test():
    print("🔍 简单测试修复后的技能参数提取功能")
    print("="*60)
    
    # 创建意图识别器
    recognizer = EnhancedIntentRecognizer()
    
    # 测试简单的技能识别
    test_cases = [
        ("帮我分析", "create_wiki"),
        ("论文", "search_papers"), 
        ("开始辩论", "start_debate")
    ]
    
    for text, expected_intent in test_cases:
        print(f"\n输入: '{text}'")
        intent = recognizer.recognize_intent(text)
        if intent:
            print(f"  识别为: {intent.name}")
            print(f"  置信度: {intent.confidence:.2f}")
            
            # 检查参数
            if hasattr(intent, 'parameters'):
                content = intent.parameters.get('content', intent.parameters.get('query', 'N/A'))
                print(f"  内容参数: {content}")
                
                # 检查是否需要澄清
                requires_clarification = getattr(intent, 'requires_clarification', False)
                print(f"  需要澄清: {requires_clarification}")
                
                if requires_clarification:
                    clarification_needed = getattr(intent, 'clarification_needed', None)
                    if clarification_needed:
                        print(f"  澄清信息: {getattr(clarification_needed, 'message', 'N/A')}")
        else:
            print(f"  未识别")

if __name__ == "__main__":
    simple_test()