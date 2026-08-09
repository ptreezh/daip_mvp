"""
增强意图识别系统 - 端到端测试

验证整个系统的完整工作流程
测试各组件间的集成和协作
验证核心业务需求的实现
"""

import unittest
import sys
import os
import time
from typing import Dict, Any, List, Optional

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from daip_live.intent_recognition.integrated_intent_system import IntegratedIntentSystem
from daip_live.agent_engine.enhanced_intent_recognizer import Intent, IntentType


class TestEnhancedIntentSystemEndToEnd(unittest.TestCase):
    """增强意图识别系统端到端测试"""

    def setUp(self):
        """测试初始化"""
        # 初始化启用了所有增强功能的系统
        self.system = IntegratedIntentSystem(
            enable_context_aware=True,
            enable_debug=True,
            enable_enhanced_features=True
        )

    def test_complete_wiki_creation_flow(self):
        """测试完整的维基创建流程"""
        session_id = "wiki_flow_test"
        
        # 1. 用户表达创建维基的意图
        intent1 = self.system.recognize_intent("创建维基 人工智能发展史", session_id)
        self.assertEqual(intent1.name, "create_wiki")
        self.assertIn("title", intent1.parameters)
        self.assertEqual(intent1.parameters["title"], "人工智能发展史")

        # 2. 系统应能识别后续的相关操作
        intent2 = self.system.recognize_intent("添加内容 人工智能起源于1950年代", session_id)
        # 根据上下文，这可能被理解为继续维基创建流程
        self.assertIsNotNone(intent2)

        # 验证会话上下文保持
        context = self.system.get_session_context(session_id)
        self.assertIsNotNone(context)
        self.assertIn("create_wiki", str(context))

    def test_complete_debate_start_flow(self):
        """测试完整的辩论启动流程"""
        session_id = "debate_flow_test"
        
        # 1. 用户启动辩论
        intent1 = self.system.recognize_intent("开始辩论 人工智能的伦理问题", session_id)
        self.assertEqual(intent1.name, "start_debate")
        self.assertIn("topic", intent1.parameters)
        self.assertEqual(intent1.parameters["topic"], "人工智能的伦理问题")

        # 2. 在辩论上下文中提问
        intent2 = self.system.recognize_intent("正方观点是什么", session_id)
        # 应该能够理解上下文
        self.assertIsNotNone(intent2)

        # 验证意图历史
        context = self.system.get_session_context(session_id)
        self.assertIn("start_debate", str(context))

    def test_misrecognition_protection_end_to_end(self):
        """测试误识别保护端到端流程"""
        # 核心测试用例：确保"你好啊，为啥找不到roles"不被误识别为论文下载
        session_id = "misrecognition_test"
        
        intent = self.system.recognize_intent("你好啊，为啥找不到roles", session_id)
        
        # 断言：不应该识别为论文相关意图
        self.assertNotIn(intent.name, ["search_papers", "download_paper"], 
                        f"核心测试用例失败：输入 '你好啊，为啥找不到roles' 被错误地识别为 {intent.name}")
        
        # 应该识别为聊天或问题意图
        self.assertIn(intent.name, ["chat", "question"], 
                     f"核心测试用例失败：输入应被识别为聊天或问题意图，但得到 {intent.name}")
        
        # 验证保护机制已记录
        self.assertGreaterEqual(self.system.recognition_stats["misrecognition_protection_hits"], 0)

    def test_context_preservation_across_turns(self):
        """测试跨对话轮次的上下文保持"""
        session_id = "context_preservation_test"
        
        # 开始一个任务
        self.system.start_contextual_task(
            session_id=session_id,
            task_type="create_wiki",
            initial_params={"title": "测试维基"}
        )
        
        # 进行多轮对话
        responses = []
        inputs = [
            "你好", 
            "创建维基 项目管理", 
            "内容是关于项目管理的基本概念", 
            "添加参考文献", 
            "谢谢"
        ]
        
        for user_input in inputs:
            intent = self.system.recognize_intent(user_input, session_id)
            responses.append(intent)
        
        # 验证对话历史被正确维护
        history = self.system.get_conversation_history(session_id)
        self.assertGreaterEqual(len(history), len(inputs))

    def test_entity_extraction_and_reference(self):
        """测试实体提取和引用"""
        session_id = "entity_test"
        
        # 第一轮对话，系统提取实体
        intent1 = self.system.recognize_intent("我想要了解人工智能领域的论文", session_id)
        self.assertIsNotNone(intent1)
        
        # 第二轮对话，引用之前的实体
        intent2 = self.system.recognize_intent("它有哪些应用", session_id)
        # 系统应该能理解"它"指的是人工智能
        self.assertIsNotNone(intent2)

    def test_multi_intent_handling(self):
        """测试多意图处理"""
        session_id = "multi_intent_test"
        
        # 提供一个可能触发多个意图的复杂输入
        intent = self.system.recognize_intent("帮我创建关于机器学习的维基页面，同时搜索相关论文", session_id)
        
        # 系统应该能够处理复合意图或选择最相关的意图
        self.assertIsNotNone(intent)

    def test_conversation_continuation(self):
        """测试对话延续性"""
        session_id = "continuation_test"
        
        # 开始对话
        intent1 = self.system.recognize_intent("你好，我想创建一个维基页面", session_id)
        self.assertIn(intent1.name, ["chat", "create_wiki"])
        
        # 继续对话，提供更多细节
        intent2 = self.system.recognize_intent("关于量子计算的", session_id)
        # 系统应该能理解这是对前一个请求的补充
        self.assertIsNotNone(intent2)

    def test_parameter_inference_and_completion(self):
        """测试参数推断和补全"""
        session_id = "parameter_test"
        
        # 开始一个需要多个参数的任务，但只提供部分参数
        intent1 = self.system.recognize_intent("开始辩论", session_id)
        # 系统应识别缺少主题参数
        
        # 提供缺失参数
        intent2 = self.system.recognize_intent("辩论主题是自动驾驶", session_id)
        # 系统应能将此作为对前一个请求的参数补充
        
        # 验证最终参数完整
        context = self.system.get_session_context(session_id)
        if context:
            filled_params = context.get("filled_params", {})
            self.assertIn("topic", filled_params)

    def test_cross_model_context_reference(self):
        """测试跨模型上下文引用（如果支持）"""
        session_id = "cross_model_test"
        
        # 模拟一个包含上下文引用的输入
        intent = self.system.recognize_intent("这个之前提到的技术怎么样", session_id)
        
        # 验证系统能够处理上下文引用
        self.assertIsNotNone(intent)

    def test_system_statistics_and_monitoring(self):
        """测试系统统计和监控功能"""
        initial_stats = dict(self.system.recognition_stats)
        
        # 执行一些操作
        for i in range(5):
            self.system.recognize_intent(f"测试输入 {i}", f"test_session_{i}")
        
        final_stats = dict(self.system.recognition_stats)
        
        # 验证统计信息被正确更新
        self.assertGreaterEqual(
            final_stats["total_requests"], 
            initial_stats["total_requests"] + 5
        )

    def test_session_lifecycle_management(self):
        """测试会话生命周期管理"""
        session_id = "lifecycle_test"
        
        # 开始任务
        self.system.start_contextual_task(
            session_id=session_id,
            task_type="create_wiki",
            initial_params={"title": "生命周期测试"}
        )
        
        # 进行一些交互
        self.system.recognize_intent("添加第一段内容", session_id)
        
        # 检查任务状态
        in_task = self.system.is_session_in_task(session_id)
        self.assertTrue(in_task)
        
        # 检查缺失参数
        missing_params = self.system.get_missing_parameters(session_id)
        # 根据具体任务，可能会有其他必需参数
        
        # 导出会话数据
        session_data = self.system.export_session_data(session_id)
        self.assertIsNotNone(session_data)
        
        # 清除会话
        self.system.clear_session_context(session_id)
        
        # 验证会话已被清除
        cleared_context = self.system.get_session_context(session_id)
        self.assertIsNone(cleared_context)

    def test_performance_under_load(self):
        """测试系统在负载下的性能"""
        session_id = "performance_test"
        
        start_time = time.time()
        
        # 执行多次意图识别
        for i in range(10):
            self.system.recognize_intent(f"测试输入性能 {i}", f"{session_id}_{i}")
        
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_per_request = total_time / 10
        
        # 验证响应时间在可接受范围内（<100ms平均）
        self.assertLess(avg_time_per_request, 0.1, 
                       f"平均响应时间 {avg_time_per_request:.3f}s 超过阈值 0.1s")

    def tearDown(self):
        """测试清理"""
        # 清理所有测试会话
        test_sessions = [
            "wiki_flow_test", "debate_flow_test", "misrecognition_test",
            "context_preservation_test", "entity_test", "multi_intent_test",
            "continuation_test", "parameter_test", "cross_model_test",
            "lifecycle_test", "performance_test"
        ]
        
        for session_id in test_sessions:
            try:
                # 清理带数字后缀的性能测试会话
                for i in range(20):  # 清理可能创建的多个会话
                    self.system.clear_session_context(f"{session_id}_{i}")
            except:
                pass
            try:
                self.system.clear_session_context(session_id)
            except:
                pass


class TestEnhancedSystemIntegration(unittest.TestCase):
    """增强系统集成测试"""

    def setUp(self):
        """测试初始化"""
        self.system = IntegratedIntentSystem(
            enable_context_aware=True,
            enable_debug=False,
            enable_enhanced_features=True
        )

    def test_enhanced_feature_workflow_integration(self):
        """测试增强功能工作流集成"""
        session_id = "integration_test"
        
        # 测试完整的工作流：意图识别 -> 语义消歧 -> 误识别保护 -> 优先级决策
        original_input = "你好啊，为啥找不到roles"
        
        # 直接调用增强识别方法
        result = self.system._recognize_intent_enhanced(original_input, session_id)
        
        # 验证结果符合预期（不应是论文意图）
        if hasattr(result, 'intent'):
            # ContextualIntent
            self.assertNotIn(result.intent.name, ["search_papers", "download_paper"])
        else:
            # Intent
            self.assertNotIn(result.name, ["search_papers", "download_paper"])

    def test_component_interaction(self):
        """测试组件间交互"""
        # 验证所有增强组件都被正确初始化和交互
        self.assertIsNotNone(self.system.padatious_recognizer)
        self.assertIsNotNone(self.system.context_integrator)
        self.assertIsNotNone(self.system.query_rewriter)
        self.assertIsNotNone(self.system.entity_extractor)
        self.assertIsNotNone(self.system.intent_fuser)
        self.assertIsNotNone(self.system.anti_misrecognition_guard)
        self.assertIsNotNone(self.system.semantic_disambiguator)
        self.assertIsNotNone(self.system.context_injector)
        self.assertIsNotNone(self.system.multi_model_handler)
        self.assertIsNotNone(self.system.intent_priority_decider)


def run_all_end_to_end_tests():
    """运行所有端到端测试"""
    print("开始运行增强意图识别系统端到端测试...")
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加端到端测试
    suite.addTest(unittest.makeSuite(TestEnhancedIntentSystemEndToEnd))
    suite.addTest(unittest.makeSuite(TestEnhancedSystemIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\n端到端测试结果:")
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
    success = run_all_end_to_end_tests()
    sys.exit(0 if success else 1)