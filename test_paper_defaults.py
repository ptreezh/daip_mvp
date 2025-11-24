import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_paper_search_defaults():
    print("Testing paper search with default parameters...")
    
    recognizer = EnhancedIntentRecognizer()
    
    # 测试各种简化的论文搜索请求
    test_inputs = [
        "论文",           # 简单调用，使用默认参数
        "文献",           # 简单调用，使用默认参数  
        "找文献",         # 找文献请求
        "搜索论文",       # 搜索论文请求
        "论文机器学习",   # 带关键词
        "find paper",     # 英文简单请求
        "search papers",  # 英文搜索请求
        "学术论文",       # 学术相关
    ]
    
    for text in test_inputs:
        print(f"\nInput: '{text}'")
        intent = recognizer.recognize_intent(text)
        if intent and intent.name == "search_papers":
            print(f"  Intent: {intent.name}")
            print(f"  Confidence: {intent.confidence:.2f}")
            print(f"  Query: {intent.parameters.get('query', 'N/A')}")
            print(f"  Max Results: {intent.parameters.get('max_results', 'N/A')}")
            print(f"  Source: {intent.parameters.get('source', 'N/A')}")
        else:
            print("  Not recognized as paper search")
    
    print("\nTest completed.")

if __name__ == "__main__":
    test_paper_search_defaults()