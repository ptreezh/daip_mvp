#!/usr/bin/env python3
"""@Time    : 2025-08-06 08:30:00
@Author  : DAIP-LIVE Team
@File    : frontend_integration_test.py
@Description:
    Frontend Integration Test Script
    
    This script tests the frontend integration with the backend services
    to ensure complete functionality of the DAIP-LIVE system.
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

# Add project path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FrontendIntegrationTest:
    """Frontend Integration Test Suite"""
    
    def __init__(self):
        self.test_results = []
        self.base_url = "http://127.0.0.1:8002"
        self.web_base_url = "http://127.0.0.1:8001"
        
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
        
        status = "OK" if success else "FAIL"
        logger.info(f"{status} {test_name} - {details} (execution time: {execution_time:.2f}s)")
        
    def test_backend_service_availability(self):
        """测试后端服务可用性"""
        logger.info("Testing backend service availability")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            execution_time = time.time() - start_time
            
            success = response.status_code == 200
            details = f"后端健康检查 - HTTP {response.status_code}" if success else f"后端健康检查 - HTTP {response.status_code}"
            
            self.log_test_result("后端服务可用性", success, details, execution_time)
            return success
            
        except Exception as e:
            execution_time = time.time() - start_time
            details = f"后端服务连接失败: {str(e)}"
            self.log_test_result("后端服务可用性", False, details, execution_time)
            return False
    
    def test_web_service_availability(self):
        """测试Web服务可用性"""
        logger.info("Testing web service availability")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.web_base_url}/health", timeout=10)
            execution_time = time.time() - start_time
            
            success = response.status_code == 200
            details = f"Web健康检查 - HTTP {response.status_code}" if success else f"Web健康检查 - HTTP {response.status_code}"
            
            self.log_test_result("Web服务可用性", success, details, execution_time)
            return success
            
        except Exception as e:
            execution_time = time.time() - start_time
            details = f"Web服务连接失败: {str(e)}"
            self.log_test_result("Web服务可用性", False, details, execution_time)
            return False
    
    def test_backend_api_endpoints(self):
        """测试后端API端点"""
        logger.info("Testing backend API endpoints")
        
        endpoints = [
            ("/status", "系统状态"),
            ("/scenarios", "场景列表"),
            ("/roles", "角色管理"),
            ("/memory", "记忆服务"),
            ("/wiki", "Wiki服务")
        ]
        
        success_count = 0
        total_count = len(endpoints)
        
        for endpoint, description in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                execution_time = time.time() - start_time
                
                success = response.status_code == 200
                details = f"{description} - HTTP {response.status_code}"
                
                if success:
                    success_count += 1
                
                self.log_test_result(f"API端点_{description}", success, details, execution_time)
                
            except Exception as e:
                execution_time = time.time() - start_time
                details = f"{description} - 连接失败: {str(e)}"
                self.log_test_result(f"API端点_{description}", False, details, execution_time)
        
        overall_success = success_count == total_count
        self.log_test_result("后端API端点总体", overall_success, f"{success_count}/{total_count} 端点可用")
        return overall_success
    
    def test_web_interface_functionality(self):
        """测试Web界面功能"""
        logger.info("Testing web interface functionality")
        
        try:
            # 测试Web界面主页
            start_time = time.time()
            response = requests.get(f"{self.web_base_url}/", timeout=10)
            execution_time = time.time() - start_time
            
            success = response.status_code == 200
            details = f"Web界面主页 - HTTP {response.status_code}"
            
            if success:
                # 检查页面内容
                content = response.text
                if "DAIP-LIVE" in content and "智能协作系统" in content:
                    details += " - 页面内容正确"
                else:
                    success = False
                    details += " - 页面内容不正确"
            
            self.log_test_result("Web界面主页", success, details, execution_time)
            
            if not success:
                return False
            
            # 测试智能聊天功能
            start_time = time.time()
            chat_payload = {
                "user_input": "AI在教育中的应用研究",
                "user_preferences": {}
            }
            response = requests.post(f"{self.web_base_url}/chat", json=chat_payload, timeout=30)
            execution_time = time.time() - start_time
            
            success = response.status_code == 200
            details = f"智能聊天功能 - HTTP {response.status_code}"
            
            if success:
                try:
                    result = response.json()
                    if result.get("success") and result.get("result"):
                        details += " - 聊天响应正常"
                    else:
                        success = False
                        details += " - 聊天响应异常"
                except:
                    success = False
                    details += " - 响应格式错误"
            
            self.log_test_result("智能聊天功能", success, details, execution_time)
            
            # 测试场景执行功能
            start_time = time.time()
            scenario_payload = {
                "topic": "是否应该采用微服务架构",
                "scenario_type": "expert_consultation",
                "user_preferences": {}
            }
            response = requests.post(f"{self.web_base_url}/scenario", json=scenario_payload, timeout=30)
            execution_time = time.time() - start_time
            
            success = response.status_code == 200
            details = f"场景执行功能 - HTTP {response.status_code}"
            
            if success:
                try:
                    result = response.json()
                    if result.get("success") and result.get("result"):
                        details += " - 场景执行正常"
                    else:
                        success = False
                        details += " - 场景执行异常"
                except:
                    success = False
                    details += " - 响应格式错误"
            
            self.log_test_result("场景执行功能", success, details, execution_time)
            
            return True
            
        except Exception as e:
            self.log_test_result("Web界面功能", False, f"测试失败: {str(e)}")
            return False
    
    def test_core_services_integration(self):
        """测试核心服务集成"""
        logger.info("Testing core services integration")
        
        try:
            # 测试角色管理器
            from src.core_services.role_manager import RoleManager
            
            start_time = time.time()
            role_manager = RoleManager()
            roles = role_manager.list_roles()
            execution_time = time.time() - start_time
            
            success = isinstance(roles, list)
            details = f"角色管理器 - 加载了 {len(roles)} 个角色"
            
            self.log_test_result("角色管理器集成", success, details, execution_time)
            
            # 测试记忆服务
            from src.core_services.memory_service import MemoryService
            
            start_time = time.time()
            memory_service = MemoryService()
            execution_time = time.time() - start_time
            
            success = memory_service is not None
            details = "记忆服务 - 初始化成功"
            
            self.log_test_result("记忆服务集成", success, details, execution_time)
            
            # 测试Wiki服务
            from src.core_services.wiki_service import WikiService
            
            start_time = time.time()
            wiki_service = WikiService()
            execution_time = time.time() - start_time
            
            success = wiki_service is not None
            details = "Wiki服务 - 初始化成功"
            
            self.log_test_result("Wiki服务集成", success, details, execution_time)
            
            return True
            
        except Exception as e:
            self.log_test_result("核心服务集成", False, f"测试失败: {str(e)}")
            return False
    
    def test_frontend_components(self):
        """测试前端组件"""
        logger.info("Testing frontend components")
        
        try:
            # 测试后端连接器
            from frontend.services.backend_connector import BackendConnector
            
            start_time = time.time()
            backend_connector = BackendConnector()
            execution_time = time.time() - start_time
            
            success = backend_connector is not None
            details = "后端连接器 - 初始化成功"
            
            self.log_test_result("后端连接器", success, details, execution_time)
            
            # 测试聊天界面
            from frontend.components.chat_interface import ChatInterface
            
            start_time = time.time()
            chat_interface = ChatInterface(
                assistant_service=backend_connector,
                session_id="test_session"
            )
            execution_time = time.time() - start_time
            
            success = chat_interface is not None
            details = "聊天界面 - 初始化成功"
            
            self.log_test_result("聊天界面", success, details, execution_time)
            
            # 测试任务面板
            from frontend.components.task_panel import TaskPanel
            
            start_time = time.time()
            task_panel = TaskPanel(task_service=backend_connector.task_service)
            execution_time = time.time() - start_time
            
            success = task_panel is not None
            details = "任务面板 - 初始化成功"
            
            self.log_test_result("任务面板", success, details, execution_time)
            
            return True
            
        except Exception as e:
            self.log_test_result("前端组件", False, f"测试失败: {str(e)}")
            return False
    
    def test_scenario_execution(self):
        """测试场景执行"""
        logger.info("Testing scenario execution")
        
        try:
            from web_demo_app import ScenarioSimulator
            
            simulator = ScenarioSimulator()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # 测试学术研究场景
                start_time = time.time()
                result = loop.run_until_complete(
                    simulator.simulate_academic_research(
                        "AI在教育中的应用研究",
                        {"depth": "comprehensive"}
                    )
                )
                execution_time = time.time() - start_time
                
                success = result.get("success")
                details = f"学术研究场景 - 执行{'成功' if success else '失败'}"
                
                self.log_test_result("学术研究场景", success, details, execution_time)
                
                # 测试专家咨询场景
                start_time = time.time()
                result = loop.run_until_complete(
                    simulator.simulate_expert_consultation(
                        "是否应该采用微服务架构",
                        {"industry": "technology"}
                    )
                )
                execution_time = time.time() - start_time
                
                success = result.get("success")
                details = f"专家咨询场景 - 执行{'成功' if success else '失败'}"
                
                self.log_test_result("专家咨询场景", success, details, execution_time)
                
                # 测试轻松讨论场景
                start_time = time.time()
                result = loop.run_until_complete(
                    simulator.simulate_casual_discussion(
                        "最近有什么好电影推荐",
                        {"mood": "relaxed"}
                    )
                )
                execution_time = time.time() - start_time
                
                success = result.get("success")
                details = f"轻松讨论场景 - 执行{'成功' if success else '失败'}"
                
                self.log_test_result("轻松讨论场景", success, details, execution_time)
                
                return True
                
            finally:
                loop.close()
                
        except Exception as e:
            self.log_test_result("场景执行", False, f"测试失败: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("DAIP-LIVE Frontend Integration Test")
        print("=" * 80)
        print()
        
        # 运行所有测试
        tests = [
            ("Backend Service Availability", self.test_backend_service_availability),
            ("Web Service Availability", self.test_web_service_availability),
            ("Backend API Endpoints", self.test_backend_api_endpoints),
            ("Web Interface Functionality", self.test_web_interface_functionality),
            ("Core Services Integration", self.test_core_services_integration),
            ("Frontend Components", self.test_frontend_components),
            ("Scenario Execution", self.test_scenario_execution),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_test_result(test_name, False, f"测试异常: {str(e)}")
            print()
        
        # 生成测试报告
        self.generate_test_report()
    
    def generate_test_report(self):
        """生成测试报告"""
        print("=" * 80)
        print("测试报告")
        print("=" * 80)
        
        # 统计测试结果
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - successful_tests
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        print(f"总测试数: {total_tests}")
        print(f"成功测试: {successful_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"成功率: {success_rate:.2%}")
        print()
        
        # 显示失败的测试
        if failed_tests > 0:
            print("Failed tests:")
            print("-" * 40)
            for result in self.test_results:
                if not result["success"]:
                    print(f"X {result['test_name']}: {result['details']}")
            print()
        
        # 测试结果评估
        print("测试结果评估:")
        print("-" * 40)
        
        if success_rate >= 0.9:
            print("Excellent! Frontend integration test achieved excellent level")
            print("System can be deployed to production")
            overall_status = "EXCELLENT"
        elif success_rate >= 0.8:
            print("Good! Frontend integration is basically usable, suggest optimizing minor issues")
            print("System can be deployed for trial use")
            overall_status = "GOOD"
        elif success_rate >= 0.7:
            print("Fair! Frontend integration has many issues that need fixing")
            print("Suggest fixing issues before deployment")
            overall_status = "FAIR"
        else:
            print("Poor! Frontend integration has serious issues that need comprehensive fixing")
            print("Not recommended for deployment")
            overall_status = "POOR"
        
        # 保存详细报告
        report_data = {
            "test_timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "detailed_results": self.test_results
        }
        
        report_file = project_root / "frontend_integration_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\nDetailed report saved to: {report_file}")
        
        return overall_status

if __name__ == "__main__":
    # 运行前端集成测试
    test_suite = FrontendIntegrationTest()
    test_suite.run_all_tests()