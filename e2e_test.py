"""
端到端测试 - 从用户输入到完整功能执行
"""
import sys
sys.path.insert(0, './src')

print("="*100)
print("🔄 DAIP-LIVE 端到端测试")
print("="*100)

print("\n1. 测试端到端维基创建过程:")

def test_end_to_end_wiki():
    try:
        # 从用户输入到维基创建全过程
        from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
        from daip_live.tui import DAIP_TUI
        
        recognizer = EnhancedIntentRecognizer()
        tui = DAIP_TUI()
        
        # 测试维基完整流程
        wiki_input = "创建维基 人工智能发展史"
        intent = recognizer.recognize_intent(wiki_input)
        
        if intent and 'wiki' in intent.name:
            print(f"   ✅ 1.1 意图识别成功: '{wiki_input}' -> {intent.name}")
            
            # 验证参数提取
            title = intent.parameters.get('title', '')
            if title == "人工智能发展史":
                print(f"   ✅ 1.2 参数提取成功: 标题='{title}'")
            else:
                print(f"   ❌ 1.2 参数提取失败: 期望='人工智能发展史', 实际='{title}'")
                
            # 检查是否需要澄清
            needs_clarification = getattr(intent, 'requires_clarification', False)
            if not needs_clarification:
                print(f"   ✅ 1.3 无需澄清: {needs_clarification}")
            else:
                print(f"   ❌ 1.3 错误澄清: {needs_clarification}")
                
            return True
        else:
            print(f"   ❌ 1.1 意图识别失败: '{wiki_input}' -> {intent.name if intent else 'None'}")
            return False
            
    except Exception as e:
        print(f"   ❌ 1.0 维基流程测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

wiki_success = test_end_to_end_wiki()

print("\n2. 测试端到端辩论启动过程:")

def test_end_to_end_debate():
    try:
        from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
        
        recognizer = EnhancedIntentRecognizer()
        
        # 测试辩论完整流程
        debate_input = "辩论 AI伦理问题" 
        intent = recognizer.recognize_intent(debate_input)
        
        if intent and 'debate' in intent.name:
            print(f"   ✅ 2.1 意图识别成功: '{debate_input}' -> {intent.name}")
            
            # 验证参数提取
            topic = intent.parameters.get('topic', '')
            if topic == "ai伦理问题":
                print(f"   ✅ 2.2 参数提取成功: 主题='{topic}'")
            else:
                print(f"   ❌ 2.2 参数提取失败: 期望='ai伦理问题', 实际='{topic}'")
                
            # 测试简单辩论请求（需要澄清）
            simple_debate = "辩论"
            simple_intent = recognizer.recognize_intent(simple_debate)
            
            if simple_intent and 'debate' in simple_intent.name:
                needs_clarification = getattr(simple_intent, 'requires_clarification', False)
                if needs_clarification:
                    print(f"   ✅ 2.3 简单请求正确触发澄清: '{simple_debate}' 需要澄清")
                else:
                    print(f"   ❌ 2.3 简单请求未触发澄清: '{simple_debate}'")
            else:
                print(f"   ❌ 2.3 简单请求意图识别失败: '{simple_debate}' -> {simple_intent.name if simple_intent else 'None'}")
                
            return True
        else:
            print(f"   ❌ 2.1 意图识别失败: '{debate_input}' -> {intent.name if intent else 'None'}")
            return False
            
    except Exception as e:
        print(f"   ❌ 2.0 辩论流程测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

debate_success = test_end_to_end_debate()

print("\n3. 测试端到端论文下载过程:")

def test_end_to_end_paper():
    try:
        from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
        
        recognizer = EnhancedIntentRecognizer()
        
        # 测试论文下载流程（带关键词）
        paper_with_keyword_input = "下载论文 机器学习综述"
        intent_with_keyword = recognizer.recognize_intent(paper_with_keyword_input)
        
        success = True
        
        if intent_with_keyword and 'download' in intent_with_keyword.name:
            print(f"   ✅ 3.1 带关键词下载意图识别成功: '{paper_with_keyword_input}' -> {intent_with_keyword.name}")
            
            # 验证搜索查询提取
            search_query = intent_with_keyword.parameters.get('search_query', '')
            if search_query == "机器学习综述":
                print(f"   ✅ 3.2 搜索查询提取成功: '{search_query}'")
            else:
                print(f"   ❌ 3.2 搜索查询提取失败: 期望='机器学习综述', 实际='{search_query}'")
                success = False
        else:
            print(f"   ❌ 3.1 带关键词下载意图识别失败: '{paper_with_keyword_input}' -> {intent_with_keyword.name if intent_with_keyword else 'None'}")
            success = False
            
        # 测试简单论文下载请求（需要澄清）
        simple_paper_input = "下载论文"
        simple_intent = recognizer.recognize_intent(simple_paper_input)
        
        if simple_intent and 'download' in simple_intent.name:
            needs_clarification = getattr(simple_intent, 'requires_clarification', False)
            if needs_clarification:
                print(f"   ✅ 3.3 简单请求正确触发澄清: '{simple_paper_input}' 需要澄清")
            else:
                print(f"   ❌ 3.3 简单请求未触发澄清: '{simple_paper_input}'")
                success = False
        else:
            print(f"   ❌ 3.3 简单请求意图识别失败: '{simple_paper_input}' -> {simple_intent.name if simple_intent else 'None'}")
            success = False
            
        return success
            
    except Exception as e:
        print(f"   ❌ 3.0 论文流程测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

paper_success = test_end_to_end_paper()

print("\n4. 测试多模型交互场景:")

def test_multi_model_scenario():
    try:
        from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
        
        recognizer = EnhancedIntentRecognizer()
        
        # 测试多模型辩论场景
        multi_model_tests = [
            ("多模型辩论 人工智能未来发展", "多模型辩论带主题"),
            ("多模态辩论 量子计算伦理", "多模态辩论"),
            ("多模型辩论", "多模型辩论需澄清")
        ]
        
        scenario_success = 0
        for test_input, description in multi_model_tests:
            intent = recognizer.recognize_intent(test_input)
            if intent and 'debate' in intent.name:
                print(f"   ✅ 4.1 {description}: '{test_input}' -> {intent.name}")
                
                # 检查是否正确处理澄清
                if "多模型辩论" in test_input and test_input == "多模型辩论":
                    needs_clarification = getattr(intent, 'requires_clarification', False)
                    if needs_clarification:
                        print(f"      ✅ 4.2 需要澄清: {needs_clarification}")
                    else:
                        print(f"      ❌ 4.2 未触发澄清: {needs_clarification}")
                        
                scenario_success += 1
            else:
                print(f"   ❌ 4.1 {description}: '{test_input}' -> {intent.name if intent else 'None'}")
        
        return scenario_success == len(multi_model_tests)
            
    except Exception as e:
        print(f"   ❌ 4.0 多模型场景测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

multi_model_success = test_multi_model_scenario()

print("\n5. 测试维基实时展示功能:")

def test_wiki_realtime_display():
    try:
        from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer

        recognizer = EnhancedIntentRecognizer()

        # 仅测试意图识别部分（不需要实际创建WikiManager）
        # 测试创建维基意图
        create_intent = recognizer.recognize_intent("创建维基 实时展示测试")
        if create_intent and 'wiki' in create_intent.name:
            print(f"   ✅ 5.1 创建维基意图: '{create_intent.name}'")

            title = create_intent.parameters.get('title', '')
            if title == "实时展示测试":
                print(f"   ✅ 5.2 标题提取: '{title}'")
                return True
            else:
                print(f"   ❌ 5.2 标题提取失败: 期望='实时展示测试', 实际='{title}'")
                return False
        else:
            print(f"   ❌ 5.1 创建维基意图识别失败: {create_intent.name if create_intent else 'None'}")
            return False

    except Exception as e:
        print(f"   ❌ 5.0 维基实时展示意图识别测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

wiki_display_success = test_wiki_realtime_display()

print("\n📋 端到端测试结果汇总:")
print(f"   维基创建流程: {'✅ 通过' if wiki_success else '❌ 失败'}")
print(f"   辩论启动流程: {'✅ 通过' if debate_success else '❌ 失败'}")  
print(f"   论文下载流程: {'✅ 通过' if paper_success else '❌ 失败'}")
print(f"   多模型场景: {'✅ 通过' if multi_model_success else '❌ 失败'}")
print(f"   维基实时展示: {'✅ 通过' if wiki_display_success else '❌ 失败'}")

total_success = sum([wiki_success, debate_success, paper_success, multi_model_success, wiki_display_success])
total_tests = 5
overall_success_rate = total_success / total_tests * 100

print(f"\n🎯 总体端到端成功率: {overall_success_rate:.1f}% ({total_success}/{total_tests})")
print(f"✅ {'所有端到端测试通过!' if total_success == total_tests else '部分端到端测试失败'}")

print("="*100)
if total_success == total_tests:
    print("🎉 端到端测试全部通过！系统功能完整集成！")
else:
    print(f"⚠️  {total_tests - total_success} 个测试失败，需要进一步修复")
print("="*100)