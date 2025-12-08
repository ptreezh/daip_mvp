"""
详细调试下载论文功能的澄清逻辑
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

# 详细调试下载论文功能
print("🔍 详细调试download_paper澄清逻辑")

recognizer = EnhancedIntentRecognizer()

test_input = "下载论文 机器学习"
print(f"\\n输入: '{test_input}'")

# 检查意图识别器
intent = recognizer.recognize_intent(test_input)
print(f"意图: {intent.name if intent else 'None'}")

if intent and intent.name == "download_paper":
    print(f"参数: {intent.parameters}")
    
    paper_id = intent.parameters.get("paper_id")
    search_query = intent.parameters.get("search_query", "")
    
    print(f"paper_id: {paper_id}")
    print(f"search_query: '{search_query}'")
    print(f"search_query非空: {bool(search_query and search_query != '')}")
    print(f"not paper_id: {not paper_id}")
    
    # 检查逻辑判断
    condition1 = not paper_id and (not search_query or search_query == "")
    condition2 = not paper_id and search_query and search_query != ""
    condition3 = paper_id
    
    print(f"条件1 (需要澄清): not paper_id AND (not search_query OR search_query == '') -> {condition1}")
    print(f"条件2 (不需要澄清): not paper_id AND search_query AND search_query != '' -> {condition2}")
    print(f"条件3 (不需要澄清): paper_id -> {condition3}")
    
    if condition1:
        print("  → 满足需要澄清条件")
    elif condition2:
        print("  → 满足不需要澄清条件（有搜索词）")
    elif condition3:
        print("  → 满足不需要澄清条件（有ID）")
    else:
        print("  → 满足else条件")
    
    print(f"最终是否需要澄清: {intent.requires_clarification}")

    # 重写检查逻辑
    print("\\n手动逻辑检查:")
    if not paper_id and (not search_query or search_query == ""):
        print("  空查询条件满足 -> 需要澄清")
    elif not paper_id and search_query and search_query != "":
        print("  有查询但无ID -> 不需要澄清")
    elif paper_id:
        print("  有ID -> 不需要澄清")
    else:
        print("  其他情况 -> 需要澄清")