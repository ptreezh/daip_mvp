"""
集成测试 - 测试上下文感知意图识别与现有系统的集成
"""

import unittest
from unittest.mock import Mock, MagicMock
from src.intent_recognition.context_interfaces import IContextManager, IIntentRecognizer
from src.intent_recognition.context_manager import ContextManager
from src.intent_recognition.context_aware_intent_recognizer import ContextAwareIntentRecognizer


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        self.context_manager = ContextManager()
        from src.daip_live.agent_engine.enhanced_intent_recognizer import Intent
        # 模拟现有的意图识别系统
        self.mock_base_intent_recognizer = Mock()
        self.mock_base_intent_recognizer.recognize_intent = Mock(return_value=Intent(
            name="general_intent",
            confidence=0.7,
            parameters={},
            tool_name=None
        ))
        # 同时模拟recognize方法，以确保测试可以检查调用情况
        self.mock_base_intent_recognizer.recognize = Mock(return_value={
            "intent": "general_intent",
            "confidence": 0.7,
            "user_input": "test input"
        })
        
        self.recognizer = ContextAwareIntentRecognizer(
            context_manager=self.context_manager,
            base_intent_recognizer=self.mock_base_intent_recognizer
        )
        self.session_id = "integration_test_session"
    
    def test_integration_wiki_creation_workflow(self):
        """测试Wiki创建工作流的完整集成"""
        # 1. 开始Wiki创建任务
        wiki_context = {
            'task_type': 'wiki_creation',
            'required_params': ['title', 'content']
        }
        self.context_manager.set_context(self.session_id, wiki_context)
        
        # 2. 提供Wiki标题 - 应该被识别为任务参数而不是新意图
        result1 = self.recognizer.recognize_intent(self.session_id, "敏捷开发与规范编程")
        
        self.assertEqual(result1["intent"], "contextual_wiki_creation_param")
        self.assertEqual(result1["param_name"], "title")
        self.assertEqual(result1["param_value"], "敏捷开发与规范编程")
        self.assertFalse(result1["task_completed"])
        self.assertEqual(result1["remaining_params"], ["content"])
        
        # 3. 提供Wiki内容 - 应该继续作为任务参数处理
        result2 = self.recognizer.recognize_intent(self.session_id, "敏捷开发是一种以用户需求为核心...")
        
        self.assertEqual(result2["intent"], "contextual_wiki_creation_param")
        self.assertEqual(result2["param_name"], "content")
        self.assertEqual(result2["param_value"], "敏捷开发是一种以用户需求为核心...")
        self.assertTrue(result2["task_completed"])
        self.assertEqual(result2["completed_task"]["task_type"], "wiki_creation")
        self.assertEqual(result2["completed_task"]["parameters"]["title"], "敏捷开发与规范编程")
        self.assertEqual(result2["completed_task"]["parameters"]["content"], "敏捷开发是一种以用户需求为核心...")
        
        # 4. 验证上下文已被清除，后续输入使用常规意图识别
        result3 = self.recognizer.recognize_intent(self.session_id, "另一个请求")
        
        # 这次应该调用基础意图识别器
        self.assertEqual(result3["intent"], "general_intent")
        self.assertEqual(result3["user_input"], "另一个请求")
    
    def test_integration_normal_flow_when_no_context(self):
        """测试在没有上下文时的正常流程"""
        # 不设置任何上下文
        result = self.recognizer.recognize_intent(self.session_id, "你好")
        
        # 应该使用基础意图识别器
        self.assertEqual(result["intent"], "general_intent")
        self.assertEqual(result["user_input"], "你好")
        self.mock_base_intent_recognizer.recognize_intent.assert_called_once_with("你好")
    
    def test_integration_with_different_task_types(self):
        """测试不同任务类型"""
        # 开始辩论任务
        debate_context = {
            'task_type': 'debate',
            'required_params': ['topic', 'position']
        }
        self.context_manager.set_context(self.session_id, debate_context)
        
        # 提供辩论主题
        result = self.recognizer.recognize_intent(self.session_id, "人工智能的未来")
        
        self.assertEqual(result["intent"], "contextual_debate_param")
        self.assertEqual(result["param_name"], "topic")
        self.assertEqual(result["param_value"], "人工智能的未来")


if __name__ == '__main__':
    unittest.main()