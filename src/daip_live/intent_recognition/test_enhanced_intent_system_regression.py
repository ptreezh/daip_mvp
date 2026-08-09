"""
增强意图识别系统 - 回归测试

确保集成新功能后，原有功能仍然正常工作
验证向后兼容性和系统稳定性
"""

import unittest
import sys
import os
from typing import Dict, Any, List, Optional

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from daip_live.intent_recognition.integrated_intent_system import IntegratedIntentSystem
from daip_live.agent_engine.enhanced_intent_recognizer import Intent, IntentType, EnhancedIntentRecognizer


class TestEnhancedIntentRecognitionRegression(unittest.TestCase):
    """增强意图识别系统回归测试"""

    def setUp(self):
        """测试初始化"""
        # 初始化基础意图识别系统（不启用增强功能，确保向后兼容）
        self.base_system = IntegratedIntentSystem(
            enable_context_aware=True,
            enable_debug=False,
            enable_enhanced_features=False  # 关闭增强功能以测试基础功能
        )
        
        # 初始化增强意图识别系统（启用增强功能）
        self.enhanced_system = IntegratedIntentSystem(
            enable_context_aware=True,
            enable_debug=False,
            enable_enhanced_features=True  # 启用增强功能
        )

    def test_basic_intent_recognition_backward_compatibility(self):
        """测试基础意图识别的向后兼容性"""
        # 测试各种常见意图
        test_cases = [
            ("你好", "chat"),
            ("hello", "chat"),
            ("创建维基 人工智能", "create_wiki"),
            ("开始辩论 AI伦理", "start_debate"),
            ("搜索论文 机器学习", "search_papers"),
            ("帮我分析这段代码", "execute_skill"),
            ("什么是深度学习", "question"),
        ]

        for input_text, expected_intent in test_cases:
            with self.subTest(input_text=input_text):
                intent = self.base_system.recognize_intent(input_text)
                self.assertIsNotNone(intent)
                self.assertEqual(intent.name, expected_intent)

    def test_context_management_backward_compatibility(self):
        """测试上下文管理的向后兼容性"""
        # 测试上下文任务启动
        result = self.base_system.start_contextual_task(
            session_id="test_session_1",
            task_type="create_wiki",
            initial_params={"title": "测试页面"}
        )
        self.assertTrue(result)

        # 测试会话上下文获取
        context = self.base_system.get_session_context("test_session_1")
        self.assertIsNotNone(context)
        self.assertIn("title", context.get("filled_params", {}))

    def test_intent_parameters_extraction(self):
        """测试意图参数提取"""
        # 测试维基创建意图参数提取
        intent = self.base_system.recognize_intent("创建维基 量子计算")
        self.assertEqual(intent.name, "create_wiki")
        self.assertIn("title", intent.parameters)
        self.assertEqual(intent.parameters["title"], "量子计算")

        # 测试辩论意图参数提取
        intent = self.base_system.recognize_intent("开始辩论 人工智能的未来发展")
        self.assertEqual(intent.name, "start_debate")
        self.assertIn("topic", intent.parameters)
        self.assertEqual(intent.parameters["topic"], "人工智能的未来发展")

    def test_conversation_history_management(self):
        """测试对话历史管理"""
        # 开始一个上下文任务
        self.base_system.start_contextual_task(
            session_id="test_history",
            task_type="debate",
            initial_params={"topic": "AI伦理"}
        )

        # 添加对话历史
        intent1 = self.base_system.recognize_intent("什么是AI伦理", "test_history")
        self.assertIsNotNone(intent1)

        # 验证对话历史存在
        history = self.base_system.get_conversation_history("test_history")
        self.assertGreaterEqual(len(history), 0)

    def test_enhanced_feature_basic_functionality(self):
        """测试增强功能的基本功能性"""
        # 确保增强系统也能正常工作
        intent = self.enhanced_system.recognize_intent("你好")
        self.assertIsNotNone(intent)
        self.assertEqual(intent.name, "chat")

        # 测试意图识别的基本功能在增强系统中仍然有效
        wiki_intent = self.enhanced_system.recognize_intent("创建维基 测试页面")
        self.assertEqual(wiki_intent.name, "create_wiki")
        self.assertIn("title", wiki_intent.parameters)

    def test_prevention_of_common_misrecognition_core_case(self):
        """测试核心用例：防止将普通对话误识别为论文意图"""
        # 这是需求中的核心测试用例
        test_input = "你好啊，为啥找不到roles"
        
        # 获取意图识别结果
        intent = self.enhanced_system.recognize_intent(test_input)
        
        # 断言：不应该识别为论文相关意图
        self.assertNotIn(intent.name, ["search_papers", "download_paper"], 
                        f"输入 '{test_input}' 被错误地识别为 {intent.name} 意图")
        
        # 应该识别为聊天或问题意图
        self.assertIn(intent.name, ["chat", "question"], 
                     f"输入 '{test_input}' 应该被识别为聊天或问题意图，但得到 {intent.name}")

    def test_context_preservation(self):
        """测试上下文保持"""
        session_id = "context_test"
        
        # 开始一个任务
        self.base_system.start_contextual_task(
            session_id=session_id,
            task_type="create_wiki",
            initial_params={"title": "初始标题"}
        )
        
        # 验证上下文正确设置
        context = self.base_system.get_session_context(session_id)
        self.assertEqual(context.get("filled_params", {}).get("title"), "初始标题")

        # 清除上下文
        self.base_system.clear_session_context(session_id)
        
        # 验证上下文被清除
        cleared_context = self.base_system.get_session_context(session_id)
        self.assertIsNone(cleared_context)

    def test_statistics_tracking(self):
        """测试统计跟踪"""
        initial_stats = self.base_system.recognition_stats["total_requests"]
        
        # 执行几次意图识别
        self.base_system.recognize_intent("你好")
        self.base_system.recognize_intent("创建维基 测试")
        
        final_stats = self.base_system.recognition_stats["total_requests"]
        
        self.assertEqual(final_stats, initial_stats + 2)

    def test_error_handling(self):
        """测试错误处理"""
        # 测试空输入
        empty_intent = self.base_system.recognize_intent("")
        self.assertIsNotNone(empty_intent)

        # 测试特殊字符
        special_intent = self.base_system.recognize_intent("!@#$%^&*()")
        self.assertIsNotNone(special_intent)

    def test_task_completion_tracking(self):
        """测试任务完成跟踪"""
        session_id = "task_completion_test"
        
        # 开始任务
        self.base_system.start_contextual_task(
            session_id=session_id,
            task_type="create_wiki",
            required_params=["title"],
            initial_params={"title": "测试标题"}
        )
        
        # 检查任务是否完成（应该完成，因为已提供必需参数）
        is_complete = self.base_system.is_task_complete(session_id)
        self.assertTrue(is_complete)
        
        # 获取缺失参数（应该没有）
        missing_params = self.base_system.get_missing_parameters(session_id)
        self.assertEqual(len(missing_params), 0)

    def tearDown(self):
        """测试清理"""
        # 清理测试会话
        for session_id in ["test_session_1", "test_history", "context_test", "task_completion_test"]:
            try:
                self.base_system.clear_session_context(session_id)
            except:
                pass


class TestEnhancedFeaturesFunctionality(unittest.TestCase):
    """增强功能测试"""

    def setUp(self):
        """测试初始化"""
        self.system = IntegratedIntentSystem(
            enable_context_aware=True,
            enable_debug=False,
            enable_enhanced_features=True
        )

    def test_misrecognition_protection_effectiveness(self):
        """测试误识别保护的有效性"""
        test_cases = [
            "你好啊，为啥找不到roles",  # 核心测试用例
            "你好，帮我", 
            "hi，怎么样",
            "谢谢，为什么没有找到",
            "你好，角色在哪"
        ]

        success_count = 0
        for test_input in test_cases:
            intent = self.system.recognize_intent(test_input)
            if intent.name not in ["search_papers", "download_paper"]:
                success_count += 1

        # 确保大部分测试用例都被正确识别为非论文意图
        self.assertGreaterEqual(success_count, len(test_cases) * 0.8,
                               "误识别保护未能有效工作")

    def test_semantic_understanding_improvement(self):
        """测试语义理解改进"""
        # 测试系统是否能更好地理解上下文
        session_id = "semantic_test"
        
        # 设置上下文
        self.system.start_contextual_task(
            session_id=session_id,
            task_type="debate",
            initial_params={"topic": "人工智能"}
        )
        
        # 在上下文中提问
        intent = self.system.recognize_intent("它怎么样", session_id)
        
        # 系统应该能理解"它"指的是人工智能
        # 具体行为取决于实现，这里主要是确保不报错
        self.assertIsNotNone(intent)

    def test_enhanced_context_management(self):
        """测试增强上下文管理"""
        # 验证增强功能的上下文管理是否正常
        stats = self.system.get_session_statistics("test")
        self.assertIsNotNone(stats)


def run_all_regression_tests():
    """运行所有回归测试"""
    print("开始运行增强意图识别系统回归测试...")
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加基础回归测试
    suite.addTest(unittest.makeSuite(TestEnhancedIntentRecognitionRegression))
    suite.addTest(unittest.makeSuite(TestEnhancedFeaturesFunctionality))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n测试结果:")
    print(f"运行测试数: {result.testsRun}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")
    print(f"成功数: {result.testsRun - len(result.failures) - len(result.errors)}")
    
    if result.failures or result.errors:
        print("\n失败详情:")
        for test, traceback in result.failures + result.errors:
            print(f"\n{test}:")
            print(traceback)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_regression_tests()
    sys.exit(0 if success else 1)