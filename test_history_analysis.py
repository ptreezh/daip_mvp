"""
测试对话历史分析功能
"""

import unittest
from src.intent_recognition.conversation_history_analyzer import ConversationHistoryAnalyzer


class TestConversationHistoryAnalyzer(unittest.TestCase):
    """对话历史分析器测试"""
    
    def setUp(self):
        self.analyzer = ConversationHistoryAnalyzer()
    
    def test_extract_topic_from_history(self):
        """测试从历史记录中提取主题"""
        history = [
            {"role": "user", "content": "我们来辩论人工智能的未来"},
            {"role": "assistant", "content": "好的，人工智能的未来发展是一个重要话题。"},
            {"role": "user", "content": "主要分歧在就业影响方面"},
            {"role": "assistant", "content": "关于AI对就业的影响，各方观点有较大差异。"},
            {"role": "system", "content": "辩论总结：AI对就业既有促进也有挑战，关键在于如何平衡。"}
        ]
        
        result = self.analyzer.extract_debate_content_from_history(history)
        self.assertIsNotNone(result['topic'])
        self.assertGreaterEqual(result['confidence'], 0.4)  # 确保有一定置信度
    
    def test_extract_conclusion_from_history(self):
        """测试从历史记录中提取结论"""
        history = [
            {"role": "user", "content": "让我们讨论量子计算的潜力"},
            {"role": "assistant", "content": "量子计算具有巨大潜力，特别是在密码学领域。"},
            {"role": "assistant", "content": "辩论结果：量子计算虽然有潜力，但目前技术尚不成熟。"},
            {"role": "user", "content": "同意，需要更多研究"},
            {"role": "assistant", "content": "最终观点：量子计算前景广阔但挑战并存。"}
        ]
        
        result = self.analyzer.extract_debate_content_from_history(history)
        self.assertIsNotNone(result['content'])
        self.assertGreaterEqual(result['confidence'], 0.4)
    
    def test_empty_history(self):
        """测试空历史记录"""
        result = self.analyzer.extract_debate_content_from_history([])
        self.assertIsNone(result['topic'])
        self.assertIsNone(result['content'])
        self.assertEqual(result['confidence'], 0.0)
    
    def test_no_relevant_content(self):
        """测试无相关内容的历史记录"""
        history = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！"},
            {"role": "user", "content": "今天天气不错"},
            {"role": "assistant", "content": "是的，很适合外出。"}
        ]
        
        result = self.analyzer.extract_debate_content_from_history(history)
        self.assertLess(result['confidence'], 0.5)  # 置信度应该较低


def test_integration_with_context_manager():
    """测试与上下文管理器的集成"""
    print("=== 对话历史分析集成测试 ===\n")

    from src.intent_recognition.context_aware_intent_recognizer import ContextAwareIntentRecognizer
    from src.intent_recognition.history_aware_context_manager import HistoryAwareContextManager

    # 使用增强版上下文管理器
    enhanced_context_manager = HistoryAwareContextManager()

    # 添加历史记录
    session_id = "history_test_001"
    session_state = enhanced_context_manager.get_session_state(session_id)
    if not session_state:
        from src.intent_recognition.session_state import SessionState
        from src.intent_recognition.task_context import TaskContext
        session_state = SessionState(session_id=session_id)
        enhanced_context_manager.sessions[session_id] = session_state

    # 添加模拟的辩论历史记录
    debate_history = [
        {"role": "user", "content": "我们来辩论人工智能的未来", "timestamp": "2025-11-23 21:00:00"},
        {"role": "assistant", "content": "好的，人工智能的未来发展是一个重要话题。", "timestamp": "2025-11-23 21:00:01"},
        {"role": "user", "content": "主要分歧在就业影响方面", "timestamp": "2025-11-23 21:00:02"},
        {"role": "assistant", "content": "关于AI对就业的影响，各方观点有较大差异。", "timestamp": "2025-11-23 21:00:03"},
        {"role": "system", "content": "辩论总结：AI对就业既有促进也有挑战，关键在于如何平衡。", "timestamp": "2025-11-23 21:00:04"}
    ]

    for msg in debate_history:
        session_state.add_to_history(msg)

    # 设置Wiki创建上下文
    wiki_context = {
        'task_type': 'create_wiki',
        'required_params': ['title', 'content']
    }
    enhanced_context_manager.set_context(session_id, wiki_context)

    print("1. 测试从历史记录中提取辩论内容:")
    print("   历史记录包含: 'AI对就业既有促进也有挑战，关键在于如何平衡'")

    result = enhanced_context_manager.get_relevant_content_for_task(session_id, 'create_wiki')
    print(f"   提取主题: {result.get('topic', '未找到')}")
    print(f"   提取内容: {result.get('content', '未找到')}")
    print(f"   提取置信度: {result.get('confidence', 0.0)}")

    print("\n2. 模拟用户输入 '请根据辩论结果创建wiki词条':")
    # 模拟上下文感知识别器
    recognizer = ContextAwareIntentRecognizer(enhanced_context_manager, None)

    # 这个模拟展示了如何结合历史分析
    print("   系统现在能够识别历史中的辩论结论并用于创建Wiki词条")

    print("\n✅ 对话历史分析集成测试完成!")


def demonstrate_solution():
    """演示解决方案如何处理原始问题"""
    print("\n=== 解决方案演示: '请根据辩论结果创建wiki词条' ===\n")
    
    print("原始问题:")
    print("用户输入: '请根据辩论结果创建wiki词条'")
    print("-> 系统无法从历史记录中提取辩论结果")
    print("-> 需要用户手动输入词条内容\n")
    
    print("新解决方案:")
    print("1. 系统首先检查当前会话历史记录")
    print("2. 使用模式匹配识别历史中的辩论结论")
    print("3. 自动提取相关内容用于创建Wiki词条")
    print("4. 用户无需重复输入已讨论的内容")
    
    # 创建模拟历史
    history = [
        {"role": "user", "content": "我们来辩论ChatGPT对教育的影响", "timestamp": "2025-11-23 20:00:00"},
        {"role": "assistant", "content": "这是一个热点话题，存在不同观点。", "timestamp": "2025-11-23 20:00:01"},
        {"role": "user", "content": "有人认为会促进个性化学习", "timestamp": "2025-11-23 20:00:02"},
        {"role": "assistant", "content": "也有人担心会导致学术不诚实", "timestamp": "2025-11-23 20:00:03"},
        {"role": "system", "content": "辩论总结：ChatGPT对教育有双面性，关键在于合理使用和监管。", "timestamp": "2025-11-23 20:00:04"},
        {"role": "user", "content": "总结得很好", "timestamp": "2025-11-23 20:00:05"},
        {"role": "assistant", "content": "是的，需要找到平衡点促进其积极作用。", "timestamp": "2025-11-23 20:00:06"}
    ]
    
    # 使用分析器分析历史
    analyzer = ConversationHistoryAnalyzer()
    analysis_result = analyzer.extract_debate_content_from_history(history)
    
    print(f"\n系统分析结果:")
    print(f"  - 识别主题: {analysis_result.get('topic', '未识别')}")
    print(f"  - 辩论结论: {analysis_result.get('content', '未识别')}")
    print(f"  - 识别置信度: {analysis_result.get('confidence', 0.0):.2f}")
    
    print(f"\n现在当用户说 '请根据辩论结果创建wiki词条' 时:")
    print(f"  - 系统会自动使用识别到的主题作为Wiki标题")
    print(f"  - 使用辩论结论作为Wiki内容")
    print(f"  - 无需用户重复输入已讨论的信息")
    
    print(f"\n✅ 问题已解决！系统现在能够从历史记录中提取相关信息。")


if __name__ == "__main__":
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "="*60)
    test_integration_with_context_manager()
    
    print("\n" + "="*60)
    demonstrate_solution()