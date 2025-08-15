#!/usr/bin/env python3
"""@Time    : 2025-08-05 22:45:00
@Author  : DAIP-LIVE Team
@File    : comprehensive_web_interface_test_suite.py
@Description:
    DAIP-LIVE Web Interface Comprehensive Test Suite
    
    完整的Web界面工程可用性测试套件，覆盖：
    - 基础服务可用性测试
    - Web应用启动和运行测试
    - 三大核心场景功能测试
    - 用户交互流程测试
    - 真实LLM调用测试
    - 前后端集成测试
    - 性能和稳定性测试
    
    测试原则：
    1. 真实性：不使用模拟，测试真实系统功能
    2. 完整性：覆盖所有核心功能场景
    3. 工程可用性：确保系统可以真实运行和使用
    4. 自动化：支持完全自动化的测试执行
"""

import asyncio
import json
import logging
import sys
import time
import unittest
from datetime import datetime
from pathlib import Path

import requests

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebInterfaceTestSuite(unittest.TestCase):
    """Web界面综合测试套件"""
    
    def setUp(self):
        """测试前置设置"""
        self.test_start_time = datetime.now()
        self.test_results = []
        logger.info(f"🧪 开始测试套件: {self.__class__.__name__}")
        
    def tearDown(self):
        """测试后置清理"""
        duration = datetime.now() - self.test_start_time
        logger.info(f"✅ 测试套件完成: {self.__class__.__name__}, 耗时: {duration.total_seconds():.2f}秒")
        
    def log_test_result(self, test_name: str, success: bool, details: str = "", execution_time: float = 0):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        logger.info(f"{status} {test_name} - {details} (耗时: {execution_time:.2f}秒)")
        
    def assert_service_available(self, url: str, service_name: str, timeout: int = 10):
        """断言服务可用"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            execution_time = time.time() - start_time
            
            success = response.status_code == 200
            details = f"{service_name} - HTTP {response.status_code}" if success else f"{service_name} - HTTP {response.status_code}"
            
            self.log_test_result(f"服务可用性_{service_name}", success, details, execution_time)
            self.assertTrue(success, f"{service_name} 服务不可用")
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            details = f"{service_name} - 连接失败: {str(e)}"
            self.log_test_result(f"服务可用性_{service_name}", False, details, execution_time)
            self.fail(f"{service_name} 服务连接失败: {e}")

class BasicServiceAvailabilityTest(WebInterfaceTestSuite):
    """基础服务可用性测试"""
    
    def test_01_main_api_service(self):
        """测试1: 主API服务可用性"""
        logger.info("🧪 测试1: 主API服务可用性")
        
        try:
            # 测试导入主应用
            from src.main import app
            self.assertIsNotNone(app, "主应用导入失败")
            
            # 测试应用配置
            self.assertTrue(hasattr(app, 'title'), "主应用缺少title属性")
            self.assertTrue(hasattr(app, 'version'), "主应用缺少version属性")
            
            self.log_test_result("主API服务导入", True, "主应用成功导入")
            
        except Exception as e:
            self.log_test_result("主API服务导入", False, f"导入失败: {str(e)}")
            self.fail(f"主API服务导入失败: {e}")
    
    def test_02_web_demo_service(self):
        """测试2: Web演示服务可用性"""
        logger.info("🧪 测试2: Web演示服务可用性")
        
        try:
            # 测试导入Web演示应用
            from web_demo_app import app as web_app
            self.assertIsNotNone(web_app, "Web演示应用导入失败")
            
            # 测试Web应用配置
            self.assertTrue(hasattr(web_app, 'title'), "Web应用缺少title属性")
            self.assertEqual(web_app.title, "DAIP-LIVE V0.2 Web Demo", "Web应用title不正确")
            
            self.log_test_result("Web演示服务导入", True, "Web演示应用成功导入")
            
        except Exception as e:
            self.log_test_result("Web演示服务导入", False, f"导入失败: {str(e)}")
            self.fail(f"Web演示服务导入失败: {e}")
    
    def test_03_core_services_import(self):
        """测试3: 核心服务导入测试"""
        logger.info("🧪 测试3: 核心服务导入测试")
        
        services_to_test = [
            ("PersonalAssistantService", "src.core_services.personal_assistant_adapter"),
            ("RoleManager", "src.core_services.role_manager"),
            ("MemoryService", "src.core_services.memory_service"),
            ("WikiService", "src.core_services.wiki_service"),
            ("SynthesisEngine", "src.core_services.synthesis_engine"),
        ]
        
        failed_services = []
        
        for service_name, module_path in services_to_test:
            try:
                module = __import__(module_path, fromlist=[service_name])
                service_class = getattr(module, service_name)
                self.assertIsNotNone(service_class, f"{service_name} 类不存在")
                self.log_test_result(f"核心服务_{service_name}", True, "导入成功")
                
            except Exception as e:
                failed_services.append(service_name)
                self.log_test_result(f"核心服务_{service_name}", False, f"导入失败: {str(e)}")
        
        if failed_services:
            self.fail(f"以下核心服务导入失败: {', '.join(failed_services)}")
    
    def test_04_frontend_components_import(self):
        """测试4: 前端组件导入测试"""
        logger.info("🧪 测试4: 前端组件导入测试")
        
        components_to_test = [
            ("ChatInterface", "frontend.components.chat_interface"),
            ("TransparencyMonitor", "frontend.components.transparency_monitor"),
            ("WikiPanel", "frontend.components.wiki_panel"),
            ("TaskPanel", "frontend.components.task_panel"),
            ("BackendConnector", "frontend.services.backend_connector"),
            ("PersonalAssistantService", "frontend.services.personal_assistant"),
        ]
        
        failed_components = []
        
        for component_name, module_path in components_to_test:
            try:
                module = __import__(module_path, fromlist=[component_name])
                component_class = getattr(module, component_name)
                self.assertIsNotNone(component_class, f"{component_name} 类不存在")
                self.log_test_result(f"前端组件_{component_name}", True, "导入成功")
                
            except Exception as e:
                failed_components.append(component_name)
                self.log_test_result(f"前端组件_{component_name}", False, f"导入失败: {str(e)}")
        
        if failed_components:
            self.fail(f"以下前端组件导入失败: {', '.join(failed_components)}")

class WebApplicationFunctionalityTest(WebInterfaceTestSuite):
    """Web应用功能性测试"""
    
    def test_01_scenario_simulator_functionality(self):
        """测试1: 场景模拟器功能测试"""
        logger.info("🧪 测试1: 场景模拟器功能测试")
        
        try:
            from web_demo_app import ScenarioSimulator
            
            simulator = ScenarioSimulator()
            self.assertIsNotNone(simulator, "场景模拟器创建失败")
            
            # 测试场景推荐功能
            test_inputs = [
                ("AI在教育中的应用研究", "academic_research"),
                ("是否应该采用微服务架构", "expert_consultation"),
                ("最近有什么好电影推荐", "casual_discussion"),
            ]
            
            for input_text, expected_scenario in test_inputs:
                # 这里需要异步运行，我们创建一个简单的测试
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    recommended = loop.run_until_complete(
                        simulator.recommend_scenario(input_text)
                    )
                    self.assertEqual(recommended, expected_scenario, 
                                   f"场景推荐错误: '{input_text}' -> {recommended}, 期望: {expected_scenario}")
                    self.log_test_result(f"场景推荐_{input_text}", True, f"推荐: {recommended}")
                finally:
                    loop.close()
            
        except Exception as e:
            self.log_test_result("场景模拟器功能", False, f"测试失败: {str(e)}")
            self.fail(f"场景模拟器功能测试失败: {e}")
    
    def test_02_backend_connector_real_services(self):
        """测试2: 后端连接器真实服务测试"""
        logger.info("🧪 测试2: 后端连接器真实服务测试")
        
        try:
            from frontend.services.backend_connector import BackendConnector
            
            # 测试后端连接器创建
            connector = BackendConnector()
            self.assertIsNotNone(connector, "后端连接器创建失败")
            
            # 测试必要服务属性
            required_services = [
                'wiki_service', 'task_service', 'role_manager', 
                'workflow_integrator', 'consensus_selector',
                'intent_analysis_service', 'user_profile_service'
            ]
            
            for service in required_services:
                self.assertTrue(hasattr(connector, service), 
                              f"后端连接器缺少服务: {service}")
                service_obj = getattr(connector, service)
                self.assertIsNotNone(service_obj, f"服务 {service} 为None")
            
            self.log_test_result("后端连接器服务", True, "所有必要服务都可用")
            
            # 测试健康检查
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                health_ok = loop.run_until_complete(connector.health_check())
                self.assertTrue(health_ok, "健康检查失败")
                self.log_test_result("后端连接器健康检查", True, "健康检查通过")
            finally:
                loop.close()
                
        except Exception as e:
            self.log_test_result("后端连接器真实服务", False, f"测试失败: {str(e)}")
            self.fail(f"后端连接器真实服务测试失败: {e}")
    
    def test_03_chat_interface_initialization(self):
        """测试3: 聊天界面初始化测试"""
        logger.info("🧪 测试3: 聊天界面初始化测试")
        
        try:
            from frontend.components.chat_interface import ChatInterface
            from frontend.services.backend_connector import BackendConnector
            
            # 创建后端连接器和聊天界面
            backend_connector = BackendConnector()
            chat_interface = ChatInterface(
                assistant_service=backend_connector, 
                session_id="test_session"
            )
            
            self.assertIsNotNone(chat_interface, "聊天界面创建失败")
            self.assertEqual(chat_interface.session_id, "test_session", "会话ID设置错误")
            
            # 测试消息历史
            self.assertTrue(hasattr(chat_interface, 'messages'), "聊天界面缺少messages属性")
            self.assertTrue(len(chat_interface.messages) > 0, "聊天界面应该有欢迎消息")
            
            # 测试UI组件
            self.assertTrue(hasattr(chat_interface, 'message_input'), "聊天界面缺少输入框")
            self.assertTrue(hasattr(chat_interface, 'send_button'), "聊天界面缺少发送按钮")
            
            self.log_test_result("聊天界面初始化", True, "聊天界面成功初始化")
            
        except Exception as e:
            self.log_test_result("聊天界面初始化", False, f"初始化失败: {str(e)}")
            self.fail(f"聊天界面初始化测试失败: {e}")

class CoreScenarioFunctionalityTest(WebInterfaceTestSuite):
    """核心场景功能性测试"""
    
    def test_01_academic_research_scenario(self):
        """测试1: 学术研究场景功能测试"""
        logger.info("🧪 测试1: 学术研究场景功能测试")
        
        try:
            from web_demo_app import ScenarioSimulator
            
            simulator = ScenarioSimulator()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # 测试学术研究场景
                result = loop.run_until_complete(
                    simulator.simulate_academic_research(
                        "AI在教育中的应用研究",
                        {"depth": "comprehensive"}
                    )
                )
                
                self.assertTrue(result.get("success"), "学术研究场景执行失败")
                self.assertIn("result", result, "缺少result字段")
                
                research_result = result["result"]
                self.assertEqual(research_result["scenario_type"], "academic_research", 
                               "场景类型错误")
                self.assertIn("research_phases", research_result, "缺少研究阶段")
                self.assertIn("final_report", research_result, "缺少最终报告")
                
                # 验证报告质量
                self.assertTrue(len(research_result["final_report"]) > 1000, 
                               "学术报告长度不足")
                self.assertTrue(research_result.get("word_count", 0) > 5000, 
                               "字数统计不足")
                
                self.log_test_result("学术研究场景", True, 
                                   f"生成报告 {research_result.get('word_count', 0)} 字")
                
            finally:
                loop.close()
                
        except Exception as e:
            self.log_test_result("学术研究场景", False, f"测试失败: {str(e)}")
            self.fail(f"学术研究场景功能测试失败: {e}")
    
    def test_02_expert_consultation_scenario(self):
        """测试2: 专家咨询场景功能测试"""
        logger.info("🧪 测试2: 专家咨询场景功能测试")
        
        try:
            from web_demo_app import ScenarioSimulator
            
            simulator = ScenarioSimulator()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # 测试专家咨询场景
                result = loop.run_until_complete(
                    simulator.simulate_expert_consultation(
                        "是否应该采用微服务架构",
                        {"industry": "technology"}
                    )
                )
                
                self.assertTrue(result.get("success"), "专家咨询场景执行失败")
                self.assertIn("result", result, "缺少result字段")
                
                consultation_result = result["result"]
                self.assertEqual(consultation_result["scenario_type"], "expert_consultation", 
                               "场景类型错误")
                self.assertIn("matched_experts", consultation_result, "缺少匹配专家")
                self.assertIn("expert_opinions", consultation_result, "缺少专家意见")
                self.assertIn("synthesis_recommendation", consultation_result, "缺少综合建议")
                
                # 验证专家匹配质量
                self.assertTrue(len(consultation_result["matched_experts"]) >= 2, 
                               "匹配专家数量不足")
                self.assertTrue(len(consultation_result["expert_opinions"]) >= 2, 
                               "专家意见数量不足")
                
                self.log_test_result("专家咨询场景", True, 
                                   f"匹配 {len(consultation_result['matched_experts'])} 位专家")
                
            finally:
                loop.close()
                
        except Exception as e:
            self.log_test_result("专家咨询场景", False, f"测试失败: {str(e)}")
            self.fail(f"专家咨询场景功能测试失败: {e}")
    
    def test_03_casual_discussion_scenario(self):
        """测试3: 轻松讨论场景功能测试"""
        logger.info("🧪 测试3: 轻松讨论场景功能测试")
        
        try:
            from web_demo_app import ScenarioSimulator
            
            simulator = ScenarioSimulator()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # 测试轻松讨论场景
                result = loop.run_until_complete(
                    simulator.simulate_casual_discussion(
                        "最近有什么好电影推荐",
                        {"mood": "relaxed"}
                    )
                )
                
                self.assertTrue(result.get("success"), "轻松讨论场景执行失败")
                self.assertIn("result", result, "缺少result字段")
                
                discussion_result = result["result"]
                self.assertEqual(discussion_result["scenario_type"], "casual_discussion", 
                               "场景类型错误")
                self.assertIn("participants", discussion_result, "缺少参与者")
                self.assertIn("conversation_flow", discussion_result, "缺少对话流程")
                
                # 验证讨论质量
                self.assertTrue(len(discussion_result["participants"]) >= 3, 
                               "参与者数量不足")
                self.assertTrue(len(discussion_result["conversation_flow"]) >= 3, 
                               "对话流程长度不足")
                
                # 验证氛围评分
                atmosphere_score = discussion_result.get("atmosphere_score", 0)
                self.assertTrue(atmosphere_score > 0.7, "氛围评分过低")
                
                self.log_test_result("轻松讨论场景", True, 
                                   f"氛围评分 {atmosphere_score:.2f}")
                
            finally:
                loop.close()
                
        except Exception as e:
            self.log_test_result("轻松讨论场景", False, f"测试失败: {str(e)}")
            self.fail(f"轻松讨论场景功能测试失败: {e}")

class IntegrationTest(WebInterfaceTestSuite):
    """集成测试"""
    
    def test_01_full_web_interface_workflow(self):
        """测试1: 完整Web界面工作流测试"""
        logger.info("🧪 测试1: 完整Web界面工作流测试")
        
        try:
            from web_demo_app import ScenarioSimulator
            
            simulator = ScenarioSimulator()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # 测试智能场景推荐工作流
                smart_chat_result = loop.run_until_complete(
                    simulator.simulate_academic_research(
                        "AI在教育中的应用研究",
                        {}
                    )
                )
                
                self.assertTrue(smart_chat_result.get("success"), "智能聊天失败")
                
                # 测试指定场景工作流
                academic_result = loop.run_until_complete(
                    simulator.simulate_academic_research(
                        "机器学习最新发展趋势",
                        {"depth": "advanced"}
                    )
                )
                
                self.assertTrue(academic_result.get("success"), "学术研究场景失败")
                
                # 测试专家咨询工作流
                expert_result = loop.run_until_complete(
                    simulator.simulate_expert_consultation(
                        "如何进行数字化转型",
                        {"company_size": "medium"}
                    )
                )
                
                self.assertTrue(expert_result.get("success"), "专家咨询场景失败")
                
                # 测试轻松讨论工作流
                casual_result = loop.run_until_complete(
                    simulator.simulate_casual_discussion(
                        "推荐一些好书",
                        {"genre": "fiction"}
                    )
                )
                
                self.assertTrue(casual_result.get("success"), "轻松讨论场景失败")
                
                self.log_test_result("完整Web界面工作流", True, "所有场景都成功执行")
                
            finally:
                loop.close()
                
        except Exception as e:
            self.log_test_result("完整Web界面工作流", False, f"测试失败: {str(e)}")
            self.fail(f"完整Web界面工作流测试失败: {e}")
    
    def test_02_performance_and_stability(self):
        """测试2: 性能和稳定性测试"""
        logger.info("🧪 测试2: 性能和稳定性测试")
        
        try:
            from web_demo_app import ScenarioSimulator
            
            simulator = ScenarioSimulator()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # 并发测试
                async def concurrent_test():
                    tasks = []
                    
                    # 创建多个并发请求
                    for i in range(5):
                        task = simulator.simulate_academic_research(
                            f"测试话题 {i}",
                            {"test_id": i}
                        )
                        tasks.append(task)
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    success_count = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
                    return success_count, len(results)
                
                success_count, total_count = loop.run_until_complete(concurrent_test())
                
                # 验证并发成功率
                success_rate = success_count / total_count
                self.assertTrue(success_rate >= 0.8, 
                               f"并发成功率过低: {success_rate:.2%}")
                
                self.log_test_result("性能和稳定性", True, 
                                   f"并发测试 {success_count}/{total_count} ({success_rate:.2%})")
                
            finally:
                loop.close()
                
        except Exception as e:
            self.log_test_result("性能和稳定性", False, f"测试失败: {str(e)}")
            self.fail(f"性能和稳定性测试失败: {e}")

def run_comprehensive_test_suite():
    """运行综合测试套件"""
    print("=" * 80)
    print("🧪 DAIP-LIVE Web Interface Comprehensive Test Suite")
    print("=" * 80)
    print()
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        BasicServiceAvailabilityTest,
        WebApplicationFunctionalityTest,
        CoreScenarioFunctionalityTest,
        IntegrationTest,
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 汇总所有测试结果
    all_results = []
    for test_case in result._tests:
        if hasattr(test_case, 'test_results'):
            all_results.extend(test_case.test_results)
    
    # 生成详细报告
    print("\n" + "=" * 80)
    print("📊 详细测试报告")
    print("=" * 80)
    
    # 按测试类型分组
    test_categories = {}
    for test_result in all_results:
        category = test_result["test_name"].split("_")[0]
        if category not in test_categories:
            test_categories[category] = []
        test_categories[category].append(test_result)
    
    # 输出分类报告
    for category, results in test_categories.items():
        print(f"\n📁 {category.upper()} 测试")
        print("-" * 40)
        
        category_success = sum(1 for r in results if r["success"])
        category_total = len(results)
        category_success_rate = category_success / category_total if category_total > 0 else 0
        
        print(f"成功率: {category_success}/{category_total} ({category_success_rate:.2%})")
        
        # 显示失败的测试
        failed_tests = [r for r in results if not r["success"]]
        if failed_tests:
            print("失败测试:")
            for failed_test in failed_tests:
                print(f"  ❌ {failed_test['test_name']}: {failed_test['details']}")
    
    # 总体统计
    total_success = sum(1 for r in all_results if r["success"])
    total_tests = len(all_results)
    total_success_rate = total_success / total_tests if total_tests > 0 else 0
    
    print("\n🎯 总体统计")
    print("=" * 40)
    print(f"总测试数: {total_tests}")
    print(f"成功测试: {total_success}")
    print(f"失败测试: {total_tests - total_success}")
    print(f"总体成功率: {total_success_rate:.2%}")
    
    # 执行时间统计
    total_time = sum(r["execution_time"] for r in all_results)
    avg_time = total_time / total_tests if total_tests > 0 else 0
    print(f"总执行时间: {total_time:.2f}秒")
    print(f"平均测试时间: {avg_time:.2f}秒")
    
    # 测试结果评估
    print("\n🏆 测试结果评估")
    print("=" * 40)
    
    if total_success_rate >= 0.95:
        print("🎉 优秀！Web界面工程可用性达到优秀水平")
        print("✅ 系统可以投入生产使用")
        overall_status = "EXCELLENT"
    elif total_success_rate >= 0.85:
        print("👍 良好！Web界面基本可用，建议优化少数问题")
        print("✅ 系统可以投入试用使用")
        overall_status = "GOOD"
    elif total_success_rate >= 0.70:
        print("⚠️ 一般！Web界面存在较多问题，需要修复")
        print("❌ 建议修复问题后再投入使用")
        overall_status = "FAIR"
    else:
        print("❌ 较差！Web界面存在严重问题，需要全面修复")
        print("❌ 不建议投入使用")
        overall_status = "POOR"
    
    # 保存详细报告
    report_data = {
        "test_timestamp": datetime.now().isoformat(),
        "overall_status": overall_status,
        "total_tests": total_tests,
        "successful_tests": total_success,
        "failed_tests": total_tests - total_success,
        "success_rate": total_success_rate,
        "total_execution_time": total_time,
        "average_execution_time": avg_time,
        "test_categories": test_categories,
        "detailed_results": all_results
    }
    
    report_file = project_root / "comprehensive_web_test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存到: {report_file}")
    
    # 返回测试结果
    return {
        "success": total_success_rate >= 0.85,
        "total_tests": total_tests,
        "successful_tests": total_success,
        "success_rate": total_success_rate,
        "overall_status": overall_status,
        "report_file": str(report_file)
    }

if __name__ == "__main__":
    # 运行综合测试套件
    test_result = run_comprehensive_test_suite()
    
    # 根据测试结果设置退出码
    exit_code = 0 if test_result["success"] else 1
    sys.exit(exit_code)