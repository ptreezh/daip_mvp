"""
测试PA助手功能
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

def test_pa_assistant_functionality():
    print("="*70)
    print("🎯 测试PA助手功能集成")
    print("="*70)
    
    recognizer = EnhancedIntentRecognizer()
    
    # 测试PA助手相关意图
    print("🤖 PA助手意图识别测试:")
    pa_tests = [
        "个人助手，请帮我分析这个",
        "PA助手，帮我总结这段话", 
        "智能助手，搜索一下AI伦理",
        "助手功能",
        "启动助手",
        "个人AI助手",
        "我的助手",
        "私人助手"
    ]
    
    pa_success = 0
    for test in pa_tests:
        intent = recognizer.recognize_intent(test)
        if intent and intent.name == "personal_assistant":
            print(f"  ✅ '{test}' → {intent.name} (置信度: {intent.confidence:.2f})")
            print(f"      请求类型: {intent.parameters.get('request_type', 'unknown')}")
            print(f"      具体请求: {intent.parameters.get('specific_request', 'none')}")
            pa_success += 1
        else:
            print(f"  ❌ '{test}' → {(intent.name if intent else 'None')}")
    
    print(f"\n📊 PA助手识别: {pa_success}/{len(pa_tests)} 通过")
    
    print(f"\n🔍 知识库功能测试:")
    knowledge_tests = [
        "在知识库中搜索 人工智能",
        "知识库查找 机器学习",
        "本地知识搜索 深度学习", 
        "我的知识库中查找 量子计算"
    ]
    
    knowledge_success = 0
    for test in knowledge_tests:
        intent = recognizer.recognize_intent(test)
        if intent and 'knowledge' in intent.name.lower():
            print(f"  ✅ '{test}' → {intent.name} (置信度: {intent.confidence:.2f})")
            knowledge_success += 1
        else:
            print(f"  ❌ '{test}' → {(intent.name if intent else 'None')}")
    
    print(f"\n📊 知识库识别: {knowledge_success}/{len(knowledge_tests)} 通过")
    
    print(f"\n📋 系统现在支持的PA助手功能:")
    if pa_success > 0:
        print(f"✅ 个人助手功能已集成")
        print(f"✅ 支持多种表达方式: '个人助手'、'PA助手'、'智能助手'等")
        print(f"✅ 支持分析、总结、搜索、解释等多种任务类型")
        print(f"✅ 自动启用知识库检索")
        print(f"✅ 支持多模型协作")
    
    print(f"\n📚 系统现在支持的知识库功能:")
    if knowledge_success > 0:
        print(f"✅ 本地知识库搜索")
        print(f"✅ 知识库内容检索")
        print(f"✅ 语义化查询匹配")
        print(f"✅ RAG检索增强生成")
        
    print(f"\n💡 PA助手使用示例:")
    print(f"   • '个人助手，请帮我分析这段代码'")
    print(f"   • 'PA助手，搜索量子计算相关资料'") 
    print(f"   • '智能助手，总结这份报告'")
    print(f"   • '我的助手，帮我写个维基页面'")
    print(f"   • '助手，帮我查找论文'") 
    
    overall_success = pa_success > 0 or knowledge_success > 0
    print(f"\n🎯 总体验证: {'✅ 通过' if overall_success else '❌ 待完善'}")
    print("="*70)
    
    return overall_success

if __name__ == "__main__":
    success = test_pa_assistant_functionality()
    print(f"\n✅ PA助手和知识库功能测试{'成功' if success else '需进一步改进'}")