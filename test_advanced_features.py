"""
测试知识库、本地知识库和PA助手功能
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_advanced_features():
    print("="*70)
    print("🔍 知识库和PA助手功能测试")
    print("="*70)
    
    recognizer = EnhancedIntentRecognizer()
    
    # 测试知识库相关功能
    print("📚 知识库功能测试:")
    knowledge_tests = [
        # 知识库查询
        "查询知识库",
        "搜索知识库",
        "在知识库中查找",
        "知识库搜索",
        "知识库查找",
        
        # 本地知识库
        "本地知识库",
        "查询本地知识",
        "搜索本地知识",
        "在本地知识中查找",
        "本地知识搜索",
        
        # 知识管理
        "管理知识库",
        "添加知识",
        "更新知识",
        "删除知识",
        "知识管理",
        
        # 个人助手相关
        "个人助手",
        "PA助手",
        "智能助手",
        "个人AI助手",
        "助手功能",
        "启动助手"
    ]
    
    recognized_knowledge = 0
    total_knowledge = len(knowledge_tests)
    
    for test in knowledge_tests:
        intent = recognizer.recognize_intent(test)
        if intent:
            print(f"  '{test}' → {intent.name} (置信度: {intent.confidence:.2f})")
            
            # 检查是否与知识或助手相关
            if any(keyword in test.lower() for keyword in ["知识库", "本地知识", "知识", "助手", "assistant", "pa"]):
                recognized_knowledge += 1
        else:
            print(f"  '{test}' → 未识别")
    
    print(f"\n📊 知识库/助手功能识别统计: {recognized_knowledge}/{total_knowledge} 相关")
    
    # 现有功能测试
    print(f"\n📋 现有已支持功能:")
    existing_features = [
        "论文 人工智能",
        "开始辩论 AI伦理", 
        "创建 Wiki 项目计划",
        "显示辩论历史",
        "你好"
    ]
    
    for test in existing_features:
        intent = recognizer.recognize_intent(test)
        if intent:
            print(f"  ✅ '{test}' → {intent.name}")
    
    print()
    print("="*70)
    print("🔍 分析:")
    print("知识库和本地知识库功能可能需要额外的模块实现")
    print("PA助手功能可能需要专门的个人助手模块")
    print("当前系统专注于: 论文搜索、辩论、Wiki、项目管理等功能")
    print("="*70)
    
    # 检查是否已支持相关意图类型
    print(f"\n📋 系统当前支持的意图类型:")
    all_patterns = recognizer.intent_patterns
    for intent_name, config in all_patterns.items():
        print(f"  • {intent_name}: {config['description']}")
    
    print(f"\n系统支持 {len(all_patterns)} 种主要意图类型")
    
    return recognized_knowledge > 0

if __name__ == "__main__":
    success = test_advanced_features()
    
    if success:
        print(f"\n✅ 系统已识别部分知识库/助手相关功能")
    else:
        print(f"\n⚠️  知识库、本地知识库和PA助手功能可能需要进一步扩展")
        print("建议:")
        print("• 创建专门的知识库管理模块")
        print("• 实现本地知识搜索功能") 
        print("• 开发PA助手核心功能")
        print("• 扩展intent识别以支持这些功能")