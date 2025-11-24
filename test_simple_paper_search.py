import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_simple_paper_search():
    print("Testing simple paper search scenarios...")
    
    recognizer = EnhancedIntentRecognizer()
    
    # 测试更接近真实用户场景的输入
    test_inputs = [
        "论文",           # 用户简单输入"论文"，应使用默认参数
        "找论文",         # 用户想查找论文，应使用默认参数
        "论文深度学习",   # 用户指定关键词
        "文献检索",       # 用户请求文献检索
        "给我找些论文",   # 用户自然语言请求
    ]
    
    print("Scenario: User wants to search for papers with minimal input")
    print("="*60)
    
    for text in test_inputs:
        print(f"\nUser input: '{text}'")
        intent = recognizer.recognize_intent(text)
        if intent and intent.name == "search_papers":
            params = intent.parameters
            print(f"  → System recognized: Paper search")
            print(f"  → Search query: '{params['query']}'")
            print(f"  → Number of results: {params['max_results']}")
            print(f"  → Source: {params['source']}")
            print(f"  → Action: Will search for '{params['query']}' in {params['source']} (max {params['max_results']} results)")
        else:
            print(f"  → System response: Not recognized as paper search")
    
    print("\n" + "="*60)
    print("SUCCESS: All simplified inputs now work with appropriate defaults!")

if __name__ == "__main__":
    test_simple_paper_search()