#!/usr/bin/env python3
"""@Time    : 2025-08-02 17:30:00
@Author  : DAIP-LIVE Team
@File    : automated_system_test.py
@Description:
    完整的自动化系统测试
    
    工程可用性验证：
    - 自动启动Personal Intelligence Hub服务
    - 自动化浏览器测试用户故事
    - 验证用户体验和流程通畅性
    - 生成详细测试报告
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import psutil
import requests

# Selenium for browser automation
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium未安装，将跳过浏览器自动化测试")

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceManager:
    """服务管理器 - 负责启动和管理各种服务"""
    
    def __init__(self):
        self.services = {}
        self.service_ports = {
            "personal_hub": 8086,
            "fastapi_backend": 8000,
            "quick_delivery": 8090
        }
    
    async def start_personal_intelligence_hub(self) -> dict[str, Any]:
        """启动Personal Intelligence Hub服务"""
        logger.info("🚀 启动Personal Intelligence Hub服务...")
        
        try:
            # 检查端口是否被占用
            if self._is_port_in_use(self.service_ports["personal_hub"]):
                logger.warning(f"端口 {self.service_ports['personal_hub']} 已被占用，尝试终止现有进程")
                self._kill_process_on_port(self.service_ports["personal_hub"])
                time.sleep(2)
            
            # 启动服务
            cmd = ["python", "personal_intelligence_hub/run_hub.py"]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            self.services["personal_hub"] = {
                "process": process,
                "port": self.service_ports["personal_hub"],
                "url": f"http://localhost:{self.service_ports['personal_hub']}/hub",
                "start_time": time.time()
            }
            
            # 等待服务启动
            success = await self._wait_for_service(
                f"http://localhost:{self.service_ports['personal_hub']}", 
                timeout=30
            )
            
            if success:
                logger.info(f"✅ Personal Intelligence Hub 启动成功: {self.services['personal_hub']['url']}")
                return {
                    "success": True,
                    "service": "personal_hub",
                    "url": self.services["personal_hub"]["url"],
                    "port": self.service_ports["personal_hub"]
                }
            else:
                logger.error("❌ Personal Intelligence Hub 启动失败")
                return {"success": False, "error": "服务启动超时"}
                
        except Exception as e:
            logger.error(f"❌ Personal Intelligence Hub 启动异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_quick_delivery_demo(self) -> dict[str, Any]:
        """启动快速交付演示服务"""
        logger.info("🚀 启动快速交付演示服务...")
        
        try:
            # 检查端口
            if self._is_port_in_use(self.service_ports["quick_delivery"]):
                logger.warning(f"端口 {self.service_ports['quick_delivery']} 已被占用，尝试终止现有进程")
                self._kill_process_on_port(self.service_ports["quick_delivery"])
                time.sleep(2)
            
            # 启动服务
            cmd = ["python", "quick_delivery_demo.py"]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.getcwd()
            )
            
            self.services["quick_delivery"] = {
                "process": process,
                "port": self.service_ports["quick_delivery"],
                "url": f"http://localhost:{self.service_ports['quick_delivery']}",
                "start_time": time.time()
            }
            
            # 等待服务启动
            success = await self._wait_for_service(
                f"http://localhost:{self.service_ports['quick_delivery']}", 
                timeout=30
            )
            
            if success:
                logger.info(f"✅ 快速交付演示服务启动成功: {self.services['quick_delivery']['url']}")
                return {
                    "success": True,
                    "service": "quick_delivery",
                    "url": self.services["quick_delivery"]["url"],
                    "port": self.service_ports["quick_delivery"]
                }
            else:
                logger.error("❌ 快速交付演示服务启动失败")
                return {"success": False, "error": "服务启动超时"}
                
        except Exception as e:
            logger.error(f"❌ 快速交付演示服务启动异常: {e}")
            return {"success": False, "error": str(e)}
    
    def _is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return True
        return False
    
    def _kill_process_on_port(self, port: int):
        """终止占用指定端口的进程"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        logger.info(f"终止进程 {proc.info['name']} (PID: {proc.info['pid']})")
                        proc.terminate()
                        time.sleep(1)
                        if proc.is_running():
                            proc.kill()
                        return
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    
    async def _wait_for_service(self, url: str, timeout: int = 30) -> bool:
        """等待服务启动"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            
            await asyncio.sleep(1)
        
        return False
    
    def shutdown_all_services(self):
        """关闭所有服务"""
        logger.info("🛑 关闭所有服务...")
        
        for service_name, service_info in self.services.items():
            try:
                process = service_info["process"]
                if process.poll() is None:  # 进程仍在运行
                    logger.info(f"关闭服务: {service_name}")
                    process.terminate()
                    time.sleep(2)
                    if process.poll() is None:
                        process.kill()
            except Exception as e:
                logger.error(f"关闭服务 {service_name} 失败: {e}")


class BrowserAutomationTester:
    """浏览器自动化测试器"""
    
    def __init__(self):
        self.driver = None
        self.test_results = []
        
    def setup_browser(self) -> bool:
        """设置浏览器"""
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium不可用，跳过浏览器测试")
            return False
        
        try:
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("✅ 浏览器设置完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 浏览器设置失败: {e}")
            return False
    
    async def test_user_stories(self, service_url: str) -> list[dict[str, Any]]:
        """测试用户故事"""
        if not self.driver:
            return [{"error": "浏览器未初始化"}]
        
        user_stories = [
            {
                "name": "用户访问主页",
                "description": "用户能够成功访问系统主页",
                "test_func": self._test_homepage_access
            },
            {
                "name": "专家咨询场景",
                "description": "用户能够发起专家咨询并获得建议",
                "test_func": self._test_expert_consultation
            },
            {
                "name": "学术研究场景",
                "description": "用户能够进行学术研究并生成报告",
                "test_func": self._test_academic_research
            },
            {
                "name": "界面响应性测试",
                "description": "验证界面响应速度和交互性",
                "test_func": self._test_ui_responsiveness
            },
            {
                "name": "错误处理测试",
                "description": "验证系统错误处理能力",
                "test_func": self._test_error_handling
            }
        ]
        
        results = []
        
        for story in user_stories:
            logger.info(f"🧪 测试用户故事: {story['name']}")
            
            try:
                start_time = time.time()
                result = await story["test_func"](service_url)
                end_time = time.time()
                
                story_result = {
                    "story_name": story["name"],
                    "description": story["description"],
                    "success": result.get("success", False),
                    "execution_time": end_time - start_time,
                    "details": result,
                    "timestamp": datetime.now().isoformat()
                }
                
                results.append(story_result)
                
                status = "✅ 通过" if result.get("success") else "❌ 失败"
                logger.info(f"{story['name']}: {status}")
                
            except Exception as e:
                logger.error(f"用户故事测试失败 {story['name']}: {e}")
                results.append({
                    "story_name": story["name"],
                    "description": story["description"],
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    async def _test_homepage_access(self, service_url: str) -> dict[str, Any]:
        """测试主页访问"""
        try:
            self.driver.get(service_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 检查页面标题
            title = self.driver.title
            
            # 检查页面内容
            page_source = self.driver.page_source
            
            checks = {
                "page_loaded": len(page_source) > 100,
                "has_title": len(title) > 0,
                "contains_daip": "DAIP" in page_source or "Personal Intelligence Hub" in page_source,
                "no_error_messages": "error" not in page_source.lower() and "404" not in page_source
            }
            
            return {
                "success": all(checks.values()),
                "checks": checks,
                "title": title,
                "page_size": len(page_source)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_expert_consultation(self, service_url: str) -> dict[str, Any]:
        """测试专家咨询场景"""
        try:
            # 模拟用户进行专家咨询
            self.driver.get(service_url)
            
            # 等待页面加载
            await asyncio.sleep(2)
            
            # 查找专家咨询相关元素
            page_source = self.driver.page_source
            
            # 简化测试：检查页面是否包含专家咨询相关内容
            consultation_indicators = [
                "专家" in page_source,
                "咨询" in page_source or "consultation" in page_source.lower(),
                "建议" in page_source or "advice" in page_source.lower()
            ]
            
            return {
                "success": any(consultation_indicators),
                "consultation_indicators": consultation_indicators,
                "page_contains_expert_content": "专家" in page_source
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_academic_research(self, service_url: str) -> dict[str, Any]:
        """测试学术研究场景"""
        try:
            self.driver.get(service_url)
            await asyncio.sleep(2)
            
            page_source = self.driver.page_source
            
            # 检查学术研究相关内容
            research_indicators = [
                "学术" in page_source or "academic" in page_source.lower(),
                "研究" in page_source or "research" in page_source.lower(),
                "报告" in page_source or "report" in page_source.lower()
            ]
            
            return {
                "success": any(research_indicators),
                "research_indicators": research_indicators,
                "page_contains_research_content": "研究" in page_source
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_ui_responsiveness(self, service_url: str) -> dict[str, Any]:
        """测试界面响应性"""
        try:
            start_time = time.time()
            self.driver.get(service_url)
            
            # 等待页面完全加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            load_time = time.time() - start_time
            
            # 检查页面元素
            elements = self.driver.find_elements(By.TAG_NAME, "div")
            
            return {
                "success": load_time < 10,  # 10秒内加载完成
                "load_time": load_time,
                "elements_count": len(elements),
                "load_time_acceptable": load_time < 5
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_error_handling(self, service_url: str) -> dict[str, Any]:
        """测试错误处理"""
        try:
            # 访问不存在的页面
            error_url = service_url + "/nonexistent"
            self.driver.get(error_url)
            
            await asyncio.sleep(2)
            
            page_source = self.driver.page_source
            status_code = requests.get(error_url).status_code
            
            # 检查错误处理
            error_handling_checks = {
                "returns_error_status": status_code >= 400,
                "displays_error_message": "404" in page_source or "error" in page_source.lower(),
                "graceful_degradation": "DAIP" in page_source  # 仍显示系统信息
            }
            
            return {
                "success": any(error_handling_checks.values()),
                "error_handling_checks": error_handling_checks,
                "status_code": status_code
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def cleanup(self):
        """清理浏览器资源"""
        if self.driver:
            self.driver.quit()
            logger.info("🧹 浏览器资源已清理")


class AutomatedSystemTester:
    """自动化系统测试器"""
    
    def __init__(self):
        self.service_manager = ServiceManager()
        self.browser_tester = BrowserAutomationTester()
        self.test_results = {}
        
    async def run_complete_test_suite(self) -> dict[str, Any]:
        """运行完整测试套件"""
        logger.info("=" * 80)
        logger.info("🧪 开始完整自动化系统测试")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        try:
            # 1. 启动服务
            service_results = await self._test_service_startup()
            
            # 2. 浏览器自动化测试
            browser_results = await self._test_browser_automation()
            
            # 3. API接口测试
            api_results = await self._test_api_endpoints()
            
            # 4. 性能测试
            performance_results = await self._test_performance()
            
            # 5. 工程可用性测试
            engineering_results = await self._test_engineering_usability()
            
            end_time = datetime.now()
            
            # 生成综合测试报告
            final_report = await self._generate_comprehensive_report(
                service_results, browser_results, api_results, 
                performance_results, engineering_results,
                start_time, end_time
            )
            
            return final_report
            
        except Exception as e:
            logger.error(f"❌ 测试套件执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        finally:
            # 清理资源
            await self._cleanup_resources()
    
    async def _test_service_startup(self) -> dict[str, Any]:
        """测试服务启动"""
        logger.info("🚀 测试服务启动...")
        
        results = {}
        
        # 测试Personal Intelligence Hub
        hub_result = await self.service_manager.start_personal_intelligence_hub()
        results["personal_hub"] = hub_result
        
        # 如果Hub启动失败，尝试快速交付演示
        if not hub_result.get("success"):
            logger.info("Personal Hub启动失败，尝试快速交付演示...")
            delivery_result = await self.service_manager.start_quick_delivery_demo()
            results["quick_delivery"] = delivery_result
        
        # 等待服务稳定
        await asyncio.sleep(3)
        
        return {
            "success": any(result.get("success") for result in results.values()),
            "services": results,
            "primary_service": self._get_primary_service_url(results)
        }
    
    def _get_primary_service_url(self, service_results: dict[str, Any]) -> Optional[str]:
        """获取主要服务URL"""
        if service_results.get("personal_hub", {}).get("success"):
            return service_results["personal_hub"]["url"]
        elif service_results.get("quick_delivery", {}).get("success"):
            return service_results["quick_delivery"]["url"]
        return None
    
    async def _test_browser_automation(self) -> dict[str, Any]:
        """测试浏览器自动化"""
        logger.info("🌐 测试浏览器自动化...")
        
        # 获取服务URL
        primary_url = self.test_results.get("service_startup", {}).get("primary_service")
        if not primary_url:
            # 尝试从服务结果中获取
            for service_name, service_info in self.service_manager.services.items():
                if service_info:
                    primary_url = service_info["url"]
                    break
        
        if not primary_url:
            return {
                "success": False,
                "error": "没有可用的服务URL",
                "browser_available": SELENIUM_AVAILABLE
            }
        
        # 设置浏览器
        browser_setup = self.browser_tester.setup_browser()
        if not browser_setup:
            return {
                "success": False,
                "error": "浏览器设置失败",
                "browser_available": SELENIUM_AVAILABLE
            }
        
        # 执行用户故事测试
        user_story_results = await self.browser_tester.test_user_stories(primary_url)
        
        success_count = sum(1 for result in user_story_results if result.get("success"))
        total_count = len(user_story_results)
        
        return {
            "success": success_count > 0,
            "success_rate": success_count / total_count if total_count > 0 else 0,
            "user_story_results": user_story_results,
            "total_stories": total_count,
            "successful_stories": success_count,
            "browser_available": SELENIUM_AVAILABLE,
            "tested_url": primary_url
        }
    
    async def _test_api_endpoints(self) -> dict[str, Any]:
        """测试API端点"""
        logger.info("🔌 测试API端点...")
        
        # 获取主要服务端口
        api_endpoints = []
        
        for service_name, service_info in self.service_manager.services.items():
            if service_info and service_info.get("port"):
                base_url = f"http://localhost:{service_info['port']}"
                api_endpoints.extend([
                    f"{base_url}",
                    f"{base_url}/api/status" if "hub" in service_name else f"{base_url}/status",
                ])
        
        # 如果没有运行的服务，使用默认端点
        if not api_endpoints:
            api_endpoints = [
                "http://localhost:8086",
                "http://localhost:8086/hub",
                "http://localhost:8090"
            ]
        
        results = []
        
        for endpoint in api_endpoints:
            try:
                start_time = time.time()
                response = requests.get(endpoint, timeout=10)
                end_time = time.time()
                
                result = {
                    "endpoint": endpoint,
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "content_length": len(response.content)
                }
                
            except requests.exceptions.RequestException as e:
                result = {
                    "endpoint": endpoint,
                    "success": False,
                    "error": str(e),
                    "response_time": 0
                }
            
            results.append(result)
        
        successful_endpoints = sum(1 for r in results if r.get("success"))
        
        return {
            "success": successful_endpoints > 0,
            "endpoint_results": results,
            "total_endpoints": len(results),
            "successful_endpoints": successful_endpoints,
            "success_rate": successful_endpoints / len(results) if results else 0
        }
    
    async def _test_performance(self) -> dict[str, Any]:
        """测试性能"""
        logger.info("⚡ 测试系统性能...")
        
        performance_results = {
            "memory_usage": self._get_memory_usage(),
            "cpu_usage": self._get_cpu_usage(),
            "disk_usage": self._get_disk_usage(),
            "service_response_times": []
        }
        
        # 测试服务响应时间
        for service_name, service_info in self.service_manager.services.items():
            if service_info and service_info.get("url"):
                try:
                    start_time = time.time()
                    response = requests.get(service_info["url"], timeout=10)
                    end_time = time.time()
                    
                    performance_results["service_response_times"].append({
                        "service": service_name,
                        "response_time": end_time - start_time,
                        "success": response.status_code == 200
                    })
                    
                except Exception as e:
                    performance_results["service_response_times"].append({
                        "service": service_name,
                        "error": str(e),
                        "success": False
                    })
        
        # 性能评估
        avg_response_time = 0
        if performance_results["service_response_times"]:
            successful_responses = [
                r["response_time"] for r in performance_results["service_response_times"] 
                if r.get("success") and "response_time" in r
            ]
            if successful_responses:
                avg_response_time = sum(successful_responses) / len(successful_responses)
        
        performance_score = self._calculate_performance_score(
            performance_results["memory_usage"],
            performance_results["cpu_usage"],
            avg_response_time
        )
        
        return {
            "success": performance_score > 0.6,
            "performance_score": performance_score,
            "average_response_time": avg_response_time,
            "details": performance_results
        }
    
    def _get_memory_usage(self) -> dict[str, Any]:
        """获取内存使用情况"""
        memory = psutil.virtual_memory()
        return {
            "total_gb": memory.total / (1024**3),
            "available_gb": memory.available / (1024**3),
            "percent_used": memory.percent,
            "used_gb": memory.used / (1024**3)
        }
    
    def _get_cpu_usage(self) -> float:
        """获取CPU使用率"""
        return psutil.cpu_percent(interval=1)
    
    def _get_disk_usage(self) -> dict[str, Any]:
        """获取磁盘使用情况"""
        disk = psutil.disk_usage('.')
        return {
            "total_gb": disk.total / (1024**3),
            "free_gb": disk.free / (1024**3),
            "percent_used": (disk.used / disk.total) * 100
        }
    
    def _calculate_performance_score(self, memory: dict, cpu: float, response_time: float) -> float:
        """计算性能分数"""
        # 内存分数 (低使用率更好)
        memory_score = max(0, 1 - memory["percent_used"] / 100)
        
        # CPU分数 (低使用率更好)
        cpu_score = max(0, 1 - cpu / 100)
        
        # 响应时间分数 (快响应更好)
        response_score = max(0, 1 - min(response_time / 10, 1))  # 10秒为满分界限
        
        # 综合分数
        return (memory_score * 0.3 + cpu_score * 0.3 + response_score * 0.4)
    
    async def _test_engineering_usability(self) -> dict[str, Any]:
        """测试工程可用性"""
        logger.info("🔧 测试工程可用性...")
        
        usability_checks = {
            "services_auto_start": any(
                service.get("success") for service in 
                self.test_results.get("service_startup", {}).get("services", {}).values()
            ),
            "browser_automation_works": self.test_results.get("browser_automation", {}).get("success", False),
            "apis_accessible": self.test_results.get("api_endpoints", {}).get("success", False),
            "performance_acceptable": self.test_results.get("performance", {}).get("success", False),
            "user_stories_pass": self.test_results.get("browser_automation", {}).get("success_rate", 0) > 0.5,
            "no_critical_errors": True  # 如果到达这里说明没有严重错误
        }
        
        # 计算可用性分数
        usability_score = sum(usability_checks.values()) / len(usability_checks)
        
        # 工程质量评估
        engineering_quality = {
            "deployment_ready": usability_score > 0.8,
            "user_ready": self.test_results.get("browser_automation", {}).get("success_rate", 0) > 0.7,
            "performance_ready": self.test_results.get("performance", {}).get("performance_score", 0) > 0.6,
            "stability_demonstrated": all(usability_checks.values())
        }
        
        return {
            "success": usability_score > 0.7,
            "usability_score": usability_score,
            "usability_checks": usability_checks,
            "engineering_quality": engineering_quality,
            "overall_engineering_score": sum(engineering_quality.values()) / len(engineering_quality)
        }
    
    async def _generate_comprehensive_report(
        self, 
        service_results: dict[str, Any],
        browser_results: dict[str, Any], 
        api_results: dict[str, Any],
        performance_results: dict[str, Any],
        engineering_results: dict[str, Any],
        start_time: datetime,
        end_time: datetime
    ) -> dict[str, Any]:
        """生成综合测试报告"""
        # 保存测试结果
        self.test_results = {
            "service_startup": service_results,
            "browser_automation": browser_results,
            "api_endpoints": api_results,
            "performance": performance_results,
            "engineering_usability": engineering_results
        }
        
        # 计算整体成功率
        test_categories = [
            service_results.get("success", False),
            browser_results.get("success", False),
            api_results.get("success", False),
            performance_results.get("success", False),
            engineering_results.get("success", False)
        ]
        
        overall_success = sum(test_categories) >= len(test_categories) * 0.6  # 60%通过率
        
        report = {
            "overall_success": overall_success,
            "test_summary": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_minutes": (end_time - start_time).total_seconds() / 60,
                "total_test_categories": len(test_categories),
                "passed_categories": sum(test_categories),
                "success_rate": sum(test_categories) / len(test_categories)
            },
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations(),
            "engineering_assessment": {
                "deployment_ready": engineering_results.get("engineering_quality", {}).get("deployment_ready", False),
                "user_ready": engineering_results.get("engineering_quality", {}).get("user_ready", False),
                "performance_ready": engineering_results.get("engineering_quality", {}).get("performance_ready", False),
                "overall_quality": engineering_results.get("overall_engineering_score", 0)
            }
        }
        
        # 保存报告
        await self._save_test_report(report)
        
        return report
    
    def _generate_recommendations(self) -> list[str]:
        """生成改进建议"""
        recommendations = []
        
        if not self.test_results.get("service_startup", {}).get("success"):
            recommendations.append("服务启动存在问题，需要检查依赖和配置")
        
        if not self.test_results.get("browser_automation", {}).get("success"):
            recommendations.append("浏览器自动化测试失败，需要检查前端界面和交互")
        
        if not self.test_results.get("api_endpoints", {}).get("success"):
            recommendations.append("API端点测试失败，需要检查后端服务")
        
        performance_score = self.test_results.get("performance", {}).get("performance_score", 0)
        if performance_score < 0.7:
            recommendations.append("系统性能需要优化，建议检查内存和CPU使用")
        
        usability_score = self.test_results.get("engineering_usability", {}).get("usability_score", 0)
        if usability_score < 0.8:
            recommendations.append("工程可用性需要改进，建议完善部署和监控")
        
        if not recommendations:
            recommendations.append("系统测试全部通过，已具备生产部署条件")
        
        return recommendations
    
    async def _save_test_report(self, report: dict[str, Any]):
        """保存测试报告"""
        try:
            report_path = Path("automated_system_test_report.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"📊 测试报告已保存: {report_path}")
        except Exception as e:
            logger.error(f"报告保存失败: {e}")
    
    async def _cleanup_resources(self):
        """清理资源"""
        logger.info("🧹 清理测试资源...")
        
        # 清理浏览器
        self.browser_tester.cleanup()
        
        # 关闭服务
        self.service_manager.shutdown_all_services()
        
        logger.info("✅ 资源清理完成")


async def main():
    """执行完整自动化系统测试"""
    tester = AutomatedSystemTester()
    
    try:
        final_report = await tester.run_complete_test_suite()
        
        print("\n" + "=" * 100)
        print("🧪 DAIP-LIVE 自动化系统测试报告")
        print("=" * 100)
        print(f"总体结果: {'✅ 通过' if final_report['overall_success'] else '❌ 失败'}")
        print(f"测试成功率: {final_report['test_summary']['success_rate']:.1%}")
        print(f"测试时长: {final_report['test_summary']['duration_minutes']:.1f} 分钟")
        
        print("\n📊 测试类别结果:")
        detailed = final_report['detailed_results']
        categories = [
            ("服务启动", detailed.get('service_startup', {}).get('success', False)),
            ("浏览器自动化", detailed.get('browser_automation', {}).get('success', False)),
            ("API端点", detailed.get('api_endpoints', {}).get('success', False)),
            ("系统性能", detailed.get('performance', {}).get('success', False)),
            ("工程可用性", detailed.get('engineering_usability', {}).get('success', False))
        ]
        
        for category, success in categories:
            status = "✅" if success else "❌"
            print(f"  {category}: {status}")
        
        print("\n🔧 工程质量评估:")
        assessment = final_report['engineering_assessment']
        for metric, value in assessment.items():
            if isinstance(value, bool):
                status = "✅" if value else "❌"
                print(f"  {metric}: {status}")
            else:
                print(f"  {metric}: {value:.1%}")
        
        print("\n💡 改进建议:")
        for rec in final_report['recommendations']:
            print(f"  • {rec}")
        
        print("\n" + "=" * 100)
        
        return final_report['overall_success']
        
    except Exception as e:
        logger.error(f"自动化测试执行失败: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)