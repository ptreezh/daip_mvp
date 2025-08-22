"""简化版Wiki协作系统的测试"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from src.core_services.wiki_collaboration_simplified import (
    SimpleTask,
    RoleFeedback,
    ExecutionRecord,
    SimpleIntentOptimizer,
    SimpleRoleCoordinator,
    SimpleExecutor,
    SimpleTaskCoordinator,
    CollaborationStorageManager,
    TaskType,
    TaskStatus
)
from src.core_services.wiki_service import WikiService


class TestWikiCollaborationSimplified(unittest.TestCase):
    """简化版Wiki协作系统的测试用例"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录用于测试
        self.test_dir = Path(tempfile.mkdtemp())
        self.storage_path = self.test_dir / "wiki_collaboration"
        
        # 创建存储管理器
        self.storage_manager = CollaborationStorageManager(str(self.storage_path))
        
        # 创建模拟的WikiService
        self.wiki_service = Mock(spec=WikiService)
        
    def tearDown(self):
        """测试后的清理工作"""
        # 删除临时目录
        shutil.rmtree(self.test_dir)
    
    def test_simple_task_serialization(self):
        """测试SimpleTask的序列化和反序列化"""
        from datetime import datetime
        
        # 创建任务对象
        task = SimpleTask(
            id="test_task_123",
            user_input="测试输入",
            optimized_intent="测试优化意图",
            target_entry="测试条目",
            task_type=TaskType.CREATE.value,
            status=TaskStatus.PENDING.value,
            created_at=datetime.now()
        )
        
        # 序列化
        task_dict = task.to_dict()
        self.assertIsInstance(task_dict, dict)
        self.assertEqual(task_dict["id"], "test_task_123")
        
        # 反序列化
        restored_task = SimpleTask.from_dict(task_dict)
        self.assertEqual(restored_task.id, task.id)
        self.assertEqual(restored_task.user_input, task.user_input)
    
    def test_role_feedback_serialization(self):
        """测试RoleFeedback的序列化和反序列化"""
        from datetime import datetime
        
        # 创建反馈对象
        feedback = RoleFeedback(
            task_id="test_task_123",
            role_name="测试角色",
            feedback="测试反馈内容",
            submitted_at=datetime.now()
        )
        
        # 序列化
        feedback_dict = feedback.to_dict()
        self.assertIsInstance(feedback_dict, dict)
        self.assertEqual(feedback_dict["role_name"], "测试角色")
        
        # 反序列化
        restored_feedback = RoleFeedback.from_dict(feedback_dict)
        self.assertEqual(restored_feedback.task_id, feedback.task_id)
        self.assertEqual(restored_feedback.feedback, feedback.feedback)
    
    def test_execution_record_serialization(self):
        """测试ExecutionRecord的序列化和反序列化"""
        from datetime import datetime
        
        # 创建执行记录对象
        record = ExecutionRecord(
            task_id="test_task_123",
            old_content="旧内容",
            new_content="新内容",
            executed_at=datetime.now(),
            success=True
        )
        
        # 序列化
        record_dict = record.to_dict()
        self.assertIsInstance(record_dict, dict)
        self.assertEqual(record_dict["task_id"], "test_task_123")
        self.assertTrue(record_dict["success"])
        
        # 反序列化
        restored_record = ExecutionRecord.from_dict(record_dict)
        self.assertEqual(restored_record.task_id, record.task_id)
        self.assertEqual(restored_record.new_content, record.new_content)
        self.assertTrue(restored_record.success)
    
    def test_simple_intent_optimizer(self):
        """测试SimpleIntentOptimizer"""
        optimizer = SimpleIntentOptimizer()
        
        # 测试创建意图
        result = optimizer.optimize("需要一个关于机器学习的新词条")
        self.assertEqual(result["task_type"], TaskType.CREATE.value)
        self.assertIn("机器学习", result["target_entry"])
        
        # 测试更新意图
        result = optimizer.optimize("更新深度学习词条")
        self.assertEqual(result["task_type"], TaskType.UPDATE.value)
        self.assertIn("深度学习", result["target_entry"])
        
        # 测试完善意图
        result = optimizer.optimize("深度学习词条缺少实际应用案例")
        self.assertEqual(result["task_type"], TaskType.ENHANCE.value)
        self.assertIn("深度学习", result["target_entry"])
    
    def test_collaboration_storage_manager(self):
        """测试CollaborationStorageManager"""
        from datetime import datetime
        
        # 创建测试数据
        task = SimpleTask(
            id="storage_test_task",
            user_input="测试输入",
            optimized_intent="测试优化意图",
            target_entry="测试条目",
            task_type=TaskType.CREATE.value,
            status=TaskStatus.PENDING.value,
            created_at=datetime.now()
        )
        
        feedback = RoleFeedback(
            task_id="storage_test_task",
            role_name="测试角色",
            feedback="测试反馈",
            submitted_at=datetime.now()
        )
        
        record = ExecutionRecord(
            task_id="storage_test_task",
            old_content="旧内容",
            new_content="新内容",
            executed_at=datetime.now(),
            success=True
        )
        
        # 测试保存和加载任务
        self.storage_manager.save_task(task)
        loaded_task = self.storage_manager.load_task("storage_test_task")
        self.assertIsNotNone(loaded_task)
        self.assertEqual(loaded_task.id, task.id)
        
        # 测试保存和加载反馈
        self.storage_manager.save_feedback(feedback)
        loaded_feedbacks = self.storage_manager.load_feedbacks("storage_test_task")
        self.assertEqual(len(loaded_feedbacks), 1)
        self.assertEqual(loaded_feedbacks[0].role_name, "测试角色")
        
        # 测试保存和加载执行记录
        self.storage_manager.save_execution_record(record)
        loaded_record = self.storage_manager.load_execution_record("storage_test_task")
        self.assertIsNotNone(loaded_record)
        self.assertTrue(loaded_record.success)
    
    def test_simple_role_coordinator(self):
        """测试SimpleRoleCoordinator"""
        from datetime import datetime
        
        # 创建角色协调器
        role_coordinator = SimpleRoleCoordinator(self.storage_manager)
        
        # 创建测试任务
        task = SimpleTask(
            id="role_test_task",
            user_input="更新机器学习词条",
            optimized_intent="更新机器学习词条",
            target_entry="机器学习",
            task_type=TaskType.UPDATE.value,
            status=TaskStatus.PENDING.value,
            created_at=datetime.now()
        )
        
        # 测试角色指派
        assigned_roles = role_coordinator._assign_roles(task)
        self.assertIsInstance(assigned_roles, list)
        # 验证至少有一个角色被指派
        self.assertGreater(len(assigned_roles), 0)
        
        # 测试角色指派和反馈收集
        feedbacks = role_coordinator.assign_and_collect(task)
        self.assertIsInstance(feedbacks, list)
        self.assertGreater(len(feedbacks), 0)
        
        # 验证反馈内容
        for feedback in feedbacks:
            self.assertIsInstance(feedback, RoleFeedback)
            self.assertEqual(feedback.task_id, task.id)
            self.assertTrue(len(feedback.feedback) > 0)
    
    @patch('src.core_services.wiki_collaboration_simplified.SimpleExecutor._generate_content')
    def test_simple_executor(self, mock_generate_content):
        """测试SimpleExecutor"""
        from datetime import datetime
        
        # 配置模拟方法
        mock_generate_content.return_value = "生成的测试内容"
        
        # 创建执行器
        executor = SimpleExecutor(self.wiki_service, self.storage_manager)
        
        # 创建测试任务和反馈
        task = SimpleTask(
            id="executor_test_task",
            user_input="创建测试词条",
            optimized_intent="创建测试词条",
            target_entry="测试词条",
            task_type=TaskType.CREATE.value,
            status=TaskStatus.PENDING.value,
            created_at=datetime.now()
        )
        
        feedback = RoleFeedback(
            task_id="executor_test_task",
            role_name="测试角色",
            feedback="测试反馈",
            submitted_at=datetime.now()
        )
        
        # 配置WikiService模拟
        self.wiki_service.create_entry.return_value = Mock()  # 模拟成功的创建
        
        # 测试执行
        result = executor.execute(task, [feedback])
        self.assertTrue(result)
        
        # 验证方法调用
        mock_generate_content.assert_called_once_with(task, [feedback])
        self.wiki_service.create_entry.assert_called_once()
    
    def test_simple_task_coordinator(self):
        """测试SimpleTaskCoordinator"""
        from datetime import datetime
        
        # 创建模拟组件
        intent_optimizer = Mock(spec=SimpleIntentOptimizer)
        role_coordinator = Mock(spec=SimpleRoleCoordinator)
        executor = Mock(spec=SimpleExecutor)
        
        # 配置模拟组件的返回值
        intent_optimizer.optimize.return_value = {
            "target_entry": "测试词条",
            "task_type": TaskType.CREATE.value,
            "optimized_intent": "创建测试词条"
        }
        
        role_coordinator.assign_and_collect.return_value = [
            RoleFeedback(
                task_id="coordinator_test_task",
                role_name="测试角色",
                feedback="测试反馈",
                submitted_at=datetime.now()
            )
        ]
        
        executor.execute.return_value = True
        
        # 创建任务协调器
        task_coordinator = SimpleTaskCoordinator(
            intent_optimizer, 
            role_coordinator, 
            executor, 
            self.storage_manager
        )
        
        # 测试任务发起
        task_id = task_coordinator.initiate_task("创建测试词条")
        self.assertIsInstance(task_id, str)
        self.assertTrue(len(task_id) > 0)
        
        # 验证组件调用
        intent_optimizer.optimize.assert_called_once_with("创建测试词条")
        role_coordinator.assign_and_collect.assert_called_once()
        executor.execute.assert_called_once()
        
        # 测试任务状态查询
        status = task_coordinator.get_task_status(task_id)
        self.assertIsInstance(status, dict)
        self.assertEqual(status["task_id"], task_id)
        self.assertEqual(status["status"], TaskStatus.COMPLETED.value)


if __name__ == '__main__':
    unittest.main()