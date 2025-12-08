import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

# 详细调试下载论文功能
test_input = '下载论文 机器学习'
print(f"测试输入: '{test_input}'")

intent = recognizer.recognize_intent(test_input)
print(f"意图: {intent.name if intent else 'None'}")

if intent:
    print(f"  参数: {intent.parameters}")
    paper_id = intent.parameters.get("paper_id")
    search_query = intent.parameters.get("search_query", "")
    print(f"  paper_id: {paper_id}")
    print(f"  search_query: '{search_query}'")
    print(f"  requires_clarification: {getattr(intent, 'requires_clarification', 'N/A')}")
    
    # 检查条件判断
    print(f"  条件检查:")
    print(f"    not paper_id: {not paper_id}")
    print(f"    (not search_query or search_query == ''): {(not search_query or search_query == '')}")  
    print(f"    search_query非空: {bool(search_query and search_query != '')}")
    print(f"    not paper_id and search_query: {not paper_id and search_query}")
    
    # 现在根据我们看到的逻辑：因为search_query非空("机器学习")，
    # 所以第一个if条件 "not paper_id and (not search_query or search_query == '')" 不成立
    # 应该满足elif条件 "elif not paper_id and search_query:" 
    # 然后设置 requires_clarification = False