"""
测试意图识别器支持的意图范围，特别是 wiki 功能
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_intent_recognition_capabilities():
    print("="*70)
    print("🔍 意图识别能力测试")
    print("="*70)
    
    recognizer = EnhancedIntentRecognizer()
    
    # 测试 wiki 相关意图
    wiki_tests = [
        "创建wiki页面",
        "创建 wiki 页面",
        "新建 wiki 项目规划",
        "写个 wiki 人工智能",
        "编辑 wiki",
        "wiki 页面",
        "显示 wiki",
        "列出 wiki",
        "导出 wiki",
        "搜索 wiki 人工智能"
    ]
    
    print("📚 wiki 意图识别测试:")
    for test in wiki_tests:
        intent = recognizer.recognize_intent(test)
        if intent:
            print(f"  '{test}' → {intent.name} (置信度: {intent.confidence:.2f})")
        else:
            print(f"  '{test}' → 未识别")
    
    # 测试其他主要类型
    print("\n🎯 其他主要意图识别测试:")
    other_tests = [
        # 论文相关
        "论文 人工智能",
        "搜索 机器学习论文",
        "下载论文",
        "找量子计算的论文",
        
        # 辩论相关
        "开始辩论 AI伦理",
        "我们来辩论 人工智能",
        "发起辩论",
        
        # 通用聊天
        "你好",
        "帮我写代码",
        "你是谁",
        "随便聊聊",
        
        # 项目相关
        "初始化项目",
        "创建新项目",
        "设置项目环境",
        
        # 会议相关
        "压缩上下文",
        "清理历史记录"
    ]
    
    for test in other_tests:
        intent = recognizer.recognize_intent(test)
        if intent:
            print(f"  '{test}' → {intent.name} (置信度: {intent.confidence:.2f})")
        else:
            print(f"  '{test}' → 未识别")
    
    print("\n📝 意图识别器支持的主要意图类型:")
    supported_intents = {
        "search_papers": "论文搜索和下载",
        "start_debate": "开始辩论",
        "create_wiki": "创建wiki页面",
        "initialize_project": "项目初始化",
        "view_debate_history": "查看辩论历史",
        "chat": "普通聊天",
        "question": "问题类对话",
        "compress_context": "压缩上下文"
    }
    
    for intent_type, description in supported_intents.items():
        print(f"  • {intent_type}: {description}")
    
    print(f"\n✅ 意图识别系统支持 {len(supported_intents)} 种主要功能类型")
    print("="*70)

if __name__ == "__main__":
    test_intent_recognition_capabilities()