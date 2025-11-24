"""
诊断测试：检查为什么"多模型辩论"和"下载论文 机器学习"没有按预期工作
"""
import sys
sys.path.insert(0, './src')

from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

recognizer = EnhancedIntentRecognizer()

print("🔍 诊断测试：检查混合意图识别器的澄清逻辑")

# 详细分析"多模型辩论"情况
test_input = "多模型辩论"
print(f"\\n1. 测试输入: '{test_input}'")
intent = recognizer.recognize_intent(test_input)
print(f"  意图: {intent.name if intent else 'None'}")
if intent:
    print(f"  参数: {intent.parameters}")
    print(f"  需要澄清: {getattr(intent, 'requires_clarification', 'N/A')}")
    print(f"  澄清需求: {getattr(intent, 'clarification_needed', 'N/A')}")

# 详细分析"下载论文 机器学习"情况  
test_input2 = "下载论文 机器学习"
print(f"\\n2. 测试输入: '{test_input2}'")
intent2 = recognizer.recognize_intent(test_input2)
print(f"  意图: {intent2.name if intent2 else 'None'}")
if intent2:
    print(f"  参数: {intent2.parameters}")
    print(f"  需要澄清: {getattr(intent2, 'requires_clarification', 'N/A')}")
    print(f"  澄清需求: {getattr(intent2, 'clarification_needed', 'N/A')}")
    # 特别检查search_query参数
    search_query = intent2.parameters.get('search_query', '')
    paper_id = intent2.parameters.get('paper_id', None)
    print(f"  搜索查询: '{search_query}' (长度: {len(search_query)})")
    print(f"  论文ID: {paper_id}")
    
    # 检查是否应该不需要澄清
    if search_query and search_query != "":
        print(f"  ⚠️  有有效的search_query但仍然需要澄清 - 逻辑错误")
    else:
        print(f"  ✅ 没有有效查询，需要澄清是正确的")

# 检查其他情况
test_input3 = "多模型辩论 量子计算"
print(f"\\n3. 测试输入: '{test_input3}'")
intent3 = recognizer.recognize_intent(test_input3)
print(f"  意图: {intent3.name if intent3 else 'None'}")
if intent3:
    print(f"  参数: {intent3.parameters}")
    print(f"  需要澄清: {getattr(intent3, 'requires_clarification', 'N/A')}")
    topic = intent3.parameters.get('topic', '')
    print(f"  主题: '{topic}' (长度: {len(topic)})")
    
    if topic and topic != "":
        print(f"  ✅ 有有效主题，不需要澄清")
    else:
        print(f"  ❌ 没有有效主题，需要澄清")

print("\\n✅ 诊断测试完成")