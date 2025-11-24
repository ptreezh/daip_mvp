import sys
sys.path.insert(0, './src')
from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

print("🔍 详细调试辩论意图识别问题:")

# 检查所有可能与"辩论"相关的意图模式
test_inputs = ["辩论", "辩论 AI伦理", "开始辩论", "开始辩论 AI伦理"]

for test_input in test_inputs:
    print(f"\\n测试输入: '{test_input}'")
    
    # 手动检查每个意图的模式是否匹配
    intent_patterns_to_check = [
        ("start_debate", [
            r"辩论\s*$",       # 简单的"辩论"
            r"辩论\s+(.+)$",   # "辩论 [主题]" 格式
            r"开始.*辩论",
            r"发起.*辩论",
            # 添加其他模式
        ]),
        ("chat", [
            r".*辩论.*",  # 可能有通用模式匹配了？
        ]),
        ("question", [
            r".*辩论.*",  # 或者这里？
        ])
    ]
    
    # 检查所有主要意图模式
    from daip_live.agent_engine.enhanced_intent_recognizer import IntentType
    for intent_name in recognizer.intent_patterns:
        if intent_name in ["start_debate", "chat", "question", "search_papers"]:
            patterns = recognizer.intent_patterns[intent_name]["patterns"]
            matched_pattern = None
            for pattern in patterns:
                import re
                if re.search(pattern, test_input, re.IGNORECASE):
                    matched_pattern = pattern
                    break
            if matched_pattern:
                print(f"  -> {intent_name} 匹配模式: {matched_pattern}")
    
    # 使用识别器实际识别意图
    final_intent = recognizer.recognize_intent(test_input)
    print(f"  -> 最终识别: {final_intent.name if final_intent else 'None'}")