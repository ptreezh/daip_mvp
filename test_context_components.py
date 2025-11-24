"""
上下文管理相关组件的单元测试
"""

import unittest
from datetime import datetime
from src.intent_recognition.context_interfaces import IContextManager, IIntentRecognizer
from src.intent_recognition.task_context import TaskContext
from src.intent_recognition.session_state import SessionState
from src.intent_recognition.context_manager import ContextManager
from src.intent_recognition.session_state_store import SessionStateStore
from src.intent_recognition.context_aware_intent_recognizer import ContextAwareIntentRecognizer


class TestTaskContext(unittest.TestCase):
    """TaskContext类的单元测试"""
    
    def test_task_context_initialization(self):
        """测试TaskContext初始化"""
        task_context = TaskContext(
            task_type="wiki_creation",
            required_params=["title", "content"],
            status="active"
        )
        
        self.assertEqual(task_context.task_type, "wiki_creation")
        self.assertEqual(task_context.required_params, ["title", "content"])
        self.assertEqual(task_context.status, "active")
        self.assertEqual(task_context.parameters, {})
        self.assertEqual(task_context.filled_params, [])
    
    def test_add_parameter(self):
        """测试添加参数"""
        task_context = TaskContext(
            task_type="wiki_creation",
            required_params=["title", "content"]
        )
        
        task_context.add_parameter("title", "敏捷开发")
        
        self.assertEqual(task_context.parameters["title"], "敏捷开发")
        self.assertIn("title", task_context.filled_params)
        self.assertEqual(len(task_context.filled_params), 1)
    
    def test_is_complete(self):
        """测试任务完成检查"""
        task_context = TaskContext(
            task_type="wiki_creation",
            required_params=["title", "content"]
        )
        
        # 任务未完成
        self.assertFalse(task_context.is_complete())
        
        # 添加第一个参数
        task_context.add_parameter("title", "敏捷开发")
        self.assertFalse(task_context.is_complete())
        
        # 添加第二个参数
        task_context.add_parameter("content", "敏捷开发是一种...")
        self.assertTrue(task_context.is_complete())
    
    def test_get_missing_params(self):
        """测试获取缺失参数"""
        task_context = TaskContext(
            task_type="wiki_creation",
            required_params=["title", "content", "category"]
        )
        
        self.assertEqual(task_context.get_missing_params(), ["title", "content", "category"])
        
        task_context.add_parameter("title", "敏捷开发")
        self.assertEqual(task_context.get_missing_params(), ["content", "category"])


class TestSessionState(unittest.TestCase):
    """SessionState类的单元测试"""
    
    def test_session_state_initialization(self):
        """测试SessionState初始化"""
        session_state = SessionState(session_id="test_session")
        
        self.assertEqual(session_state.session_id, "test_session")
        self.assertIsNone(session_state.current_task)
        self.assertEqual(session_state.history, [])
        self.assertIsInstance(session_state.created_at, datetime)
        self.assertIsInstance(session_state.last_accessed, datetime)
    
    def test_has_active_task(self):
        """测试活跃任务检查"""
        session_state = SessionState(session_id="test_session")
        
        # 初始状态没有活跃任务
        self.assertFalse(session_state.has_active_task())
        
        # 设置一个非活跃任务
        session_state.current_task = TaskContext(task_type="wiki", status="completed")
        self.assertFalse(session_state.has_active_task())
        
        # 设置一个活跃任务
        session_state.current_task = TaskContext(task_type="wiki", status="active")
        self.assertTrue(session_state.has_active_task())
    
    def test_add_to_history(self):
        """测试添加历史记录"""
        import time
        session_state = SessionState(session_id="test_session")
        initial_time = session_state.last_accessed

        # 等待一小段时间以确保时间戳不同
        time.sleep(0.001)  # 1毫秒延迟
        session_state.add_to_history({"action": "test"})

        self.assertEqual(len(session_state.history), 1)
        self.assertGreater(session_state.last_accessed, initial_time)


class MockIntentRecognizer:
    """模拟的基础意图识别器"""
    
    def recognize(self, user_input: str) -> dict:
        return {
            "intent": "mock_intent",
            "confidence": 0.8,
            "user_input": user_input
        }


class TestContextManager(unittest.TestCase):
    """ContextManager类的单元测试"""
    
    def setUp(self):
        self.context_manager = ContextManager()
        self.session_id = "test_session_123"
    
    def test_set_context(self):
        """测试设置上下文"""
        context_data = {
            'task_type': 'wiki_creation',
            'required_params': ['title', 'content']
        }
        
        self.context_manager.set_context(self.session_id, context_data)
        
        self.assertTrue(self.context_manager.is_in_task(self.session_id))
        
        retrieved_context = self.context_manager.get_context(self.session_id)
        self.assertEqual(retrieved_context['task_type'], 'wiki_creation')
        self.assertEqual(retrieved_context['required_params'], ['title', 'content'])
    
    def test_get_context_nonexistent(self):
        """测试获取不存在的上下文"""
        context = self.context_manager.get_context("nonexistent_session")
        self.assertIsNone(context)
    
    def test_clear_context(self):
        """测试清除上下文"""
        context_data = {
            'task_type': 'wiki_creation',
            'required_params': ['title']
        }
        
        self.context_manager.set_context(self.session_id, context_data)
        self.assertTrue(self.context_manager.is_in_task(self.session_id))
        
        self.context_manager.clear_context(self.session_id)
        self.assertFalse(self.context_manager.is_in_task(self.session_id))
    
    def test_is_in_task(self):
        """测试任务状态检查"""
        # 初始状态不在任务中
        self.assertFalse(self.context_manager.is_in_task(self.session_id))
        
        # 设置上下文后在任务中
        context_data = {'task_type': 'wiki', 'required_params': []}
        self.context_manager.set_context(self.session_id, context_data)
        self.assertTrue(self.context_manager.is_in_task(self.session_id))
    
    def test_add_task_parameter(self):
        """测试添加任务参数"""
        context_data = {
            'task_type': 'wiki_creation',
            'required_params': ['title']
        }
        
        self.context_manager.set_context(self.session_id, context_data)
        
        result = self.context_manager.add_task_parameter(self.session_id, 'title', '敏捷开发')
        self.assertTrue(result)
        
        context = self.context_manager.get_context(self.session_id)
        self.assertEqual(context['parameters']['title'], '敏捷开发')
        self.assertIn('title', context['filled_params'])


class TestSessionStateStore(unittest.TestCase):
    """SessionStateStore类的单元测试"""
    
    def setUp(self):
        self.store = SessionStateStore()
        self.session_id = "test_session_456"
        self.session_state = SessionState(session_id=self.session_id)
    
    def test_store_and_retrieve(self):
        """测试存储和获取会话状态"""
        self.store.store(self.session_id, self.session_state)
        
        retrieved = self.store.retrieve(self.session_id)
        self.assertEqual(retrieved.session_id, self.session_id)
    
    def test_retrieve_nonexistent(self):
        """测试获取不存在的会话状态"""
        retrieved = self.store.retrieve("nonexistent")
        self.assertIsNone(retrieved)
    
    def test_delete(self):
        """测试删除会话状态"""
        self.store.store(self.session_id, self.session_state)
        
        result = self.store.delete(self.session_id)
        self.assertTrue(result)
        
        retrieved = self.store.retrieve(self.session_id)
        self.assertIsNone(retrieved)
    
    def test_update(self):
        """测试更新会话状态"""
        self.store.store(self.session_id, self.session_state)
        
        new_state = SessionState(session_id=self.session_id)
        new_state.current_task = TaskContext(task_type="updated_task")
        
        result = self.store.update(self.session_id, new_state)
        self.assertTrue(result)
        
        retrieved = self.store.retrieve(self.session_id)
        self.assertEqual(retrieved.current_task.task_type, "updated_task")


class TestContextAwareIntentRecognizer(unittest.TestCase):
    """ContextAwareIntentRecognizer类的单元测试"""
    
    def setUp(self):
        self.context_manager = ContextManager()
        self.base_recognizer = MockIntentRecognizer()
        self.recognizer = ContextAwareIntentRecognizer(
            context_manager=self.context_manager,
            base_intent_recognizer=self.base_recognizer
        )
        self.session_id = "test_session_789"
    
    def test_recognize_intent_outside_task(self):
        """测试任务外的意图识别"""
        result = self.recognizer.recognize_intent(self.session_id, "你好")
        
        self.assertEqual(result["intent"], "mock_intent")
        self.assertEqual(result["user_input"], "你好")
    
    def test_recognize_intent_in_task(self):
        """测试任务内的意图识别"""
        # 设置一个需要标题和内容的Wiki创建任务
        context_data = {
            'task_type': 'wiki_creation',
            'required_params': ['title', 'content']
        }
        self.context_manager.set_context(self.session_id, context_data)
        
        # 提供标题
        result = self.recognizer.recognize_intent(self.session_id, "敏捷开发")
        
        self.assertEqual(result["intent"], "contextual_wiki_creation_param")
        self.assertEqual(result["param_name"], "title")
        self.assertEqual(result["param_value"], "敏捷开发")
        self.assertFalse(result["task_completed"])
        self.assertEqual(result["remaining_params"], ["content"])
    
    def test_recognize_intent_task_completion(self):
        """测试任务完成"""
        # 设置一个只需要标题的Wiki创建任务
        context_data = {
            'task_type': 'wiki_creation',
            'required_params': ['title']
        }
        self.context_manager.set_context(self.session_id, context_data)
        
        # 提供标题
        result = self.recognizer.recognize_intent(self.session_id, "敏捷开发")
        
        self.assertTrue(result["task_completed"])
        self.assertEqual(result["completed_task"]["task_type"], "wiki_creation")
        self.assertEqual(result["completed_task"]["parameters"]["title"], "敏捷开发")
        
        # 验证上下文已被清除
        self.assertFalse(self.context_manager.is_in_task(self.session_id))


if __name__ == '__main__':
    unittest.main()