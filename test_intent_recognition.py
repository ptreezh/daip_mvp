#!/usr/bin/env python3
"""
测试意图识别功能
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_intent_recognition():
    print("开始测试意图识别功能...")
    
    # 创建意图识别器实例
    recognizer = EnhancedIntentRecognizer()
    print("✅ 意图识别器创建成功")
    
    # 测试用例
    test_cases = [
        '创建维基 人工智能发展史',
        '帮我写个维基 量子计算',
        '新建百科 机器学习',
        '创建词条 自然语言处理',
        '创建维基测试页面'  # 简单测试
    ]
    
    print(f"\n测试用例数量: {len(test_cases)}")
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n--- 测试 {i} ---")
        print(f"输入: {test_input}")
        
        try:
            intent = recognizer.recognize_intent(test_input)
            
            if intent:
                print(f"✅ 识别成功!")
                print(f"  意图名称: {intent.name}")
                print(f"  参数: {intent.parameters}")
                print(f"  置信度: {intent.confidence}")
                print(f"  需要澄清: {getattr(intent, 'requires_clarification', 'N/A')}")
                if hasattr(intent, 'clarification_needed') and intent.clarification_needed:
                    print(f"  澄清需求: {intent.clarification_needed}")
            else:
                print("❌ 未识别到意图")
                
        except Exception as e:
            print(f"❌ 处理时发生错误: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n测试完成!")

if __name__ == "__main__":
    test_intent_recognition()