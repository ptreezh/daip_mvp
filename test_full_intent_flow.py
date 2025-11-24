"""
测试完整的意图识别流程，看看是否在其他地方被重置了
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

print("🔍 全面测试完整意图识别流程")
recognizer = EnhancedIntentRecognizer()

# 测试各种输入
test_cases = [
    "创建维基 人工智能发展史",
    "辩论 AI伦理问题", 
    "下载论文 机器学习"
]

for test_input in test_cases:
    print(f"\\n测试输入: '{test_input}'")
    
    # 直接调用意图识别
    intent = recognizer.recognize_intent(test_input)
    
    if intent:
        print(f"意图: {intent.name}")
        print(f"参数: {intent.parameters}")
        print(f"需要澄清: {intent.requires_clarification}")
        
        # 详细分析
        if intent.name == "download_paper":
            paper_id = intent.parameters.get("paper_id")
            search_query = intent.parameters.get("search_query", "")
            print(f"  - paper_id: {paper_id}")
            print(f"  - search_query: '{search_query}'")
            print(f"  - 条件检查: not paper_id={not paper_id}, search_query exists={bool(search_query and search_query != '')}")
            
            # 手动执行澄清检查来验证结果
            should_not_need_clarification = not paper_id and search_query and search_query != ""
            print(f"  - 澄清检查结果应为: {'不需要' if should_not_need_clarification else '需要'}")
            
    else:
        print("未识别到意图")