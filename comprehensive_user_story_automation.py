#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-03 13:00:00
@Author  : DAIP-LIVE Team
@File    : comprehensive_user_story_automation.py
@Description:
    全面用户故事覆盖的自动化测试系统
    
    功能包括：
    - 自动启动后端服务和前端服务
    - 浏览器自动化用户故事走查
    - V0.2三场景完整用户流程验证
    - 真实用户交互模拟和验证
    - 端到端业务流程测试
"""

import asyncio
import logging
import time
import json
import subprocess
import psutil
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceManager:
    """服务管理器 - 自动启动和管理后端、前端服务"""
    
    def __init__(self):
        self.services = {}
        self.service_configs = {
            "backend": {
                "command": ["uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
                "port": 8000,
                "health_endpoint": "http://localhost:8000/health",
                "startup_timeout": 30
            },
            "frontend": {
                "command": ["python", "-m", "http.server", "3000", "--directory", "frontend"],
                "port": 3000,
                "health_endpoint": "http://localhost:3000",
                "startup_timeout": 15
            }
        }
    
    async def start_all_services(self) -> Dict[str, Any]:
        """启动所有服务"""
        logger.info("🚀 启动所有服务...")
        
        service_results = {}
        
        for service_name, config in self.service_configs.items():
            try:
                result = await self._start_service(service_name, config)
                service_results[service_name] = result
                
                if result["success"]:
                    logger.info(f"✅ {service_name} 服务启动成功 (PID: {result['pid']})")
                else:
                    logger.error(f"❌ {service_name} 服务启动失败: {result['error']}")
                    
            except Exception as e:
                logger.error(f"❌ {service_name} 服务启动异常: {e}")
                service_results[service_name] = {"success": False, "error": str(e)}
        
        all_success = all(result["success"] for result in service_results.values())
        
        return {
            "success": all_success,
            "services": service_results,
            "startup_time": datetime.now().isoformat()
        }
    
    async def _start_service(self, service_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """启动单个服务"""
        try:
            # 检查端口是否已被占用
            if self._is_port_in_use(config["port"]):
                logger.info(f"{service_name} 端口 {config['port']} 已被占用，尝试停止现有服务")
                self._kill_process_on_port(config["port"])
                await asyncio.sleep(2)
            
            # 启动服务
            process = subprocess.Popen(
                config["command"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.services[service_name] = {
                "process": process,
                "config": config
            }
            
            # 等待服务启动
            startup_success = await self._wait_for_service_ready(service_name, config)
            
            if startup_success:
                return {
                    "success": True,
                    "pid": process.pid,
                    "port": config["port"],
                    "health_endpoint": config["health_endpoint"]
                }
            else:
                process.terminate()
                return {
                    "success": False,
                    "error": f"服务在{config['startup_timeout']}秒内未就绪"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _wait_for_service_ready(self, service_name: str, config: Dict[str, Any]) -> bool:
        """等待服务就绪"""
        timeout = config["startup_timeout"]
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(config["health_endpoint"], timeout=2)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            
            await asyncio.sleep(1)
        
        return False
    
    def _is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return True
        return False
    
    def _kill_process_on_port(self, port: int):
        """杀死占用指定端口的进程"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                try:
                    process = psutil.Process(conn.pid)
                    process.terminate()
                except psutil.NoSuchProcess:
                    pass
    
    async def stop_all_services(self):
        """停止所有服务"""
        logger.info("🛑 停止所有服务...")
        
        for service_name, service_info in self.services.items():
            try:
                process = service_info["process"]
                if process.poll() is None:  # 进程仍在运行
                    process.terminate()
                    # 等待进程结束
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        
                logger.info(f"✅ {service_name} 服务已停止")
            except Exception as e:
                logger.error(f"❌ 停止 {service_name} 服务失败: {e}")


class UserStoryAutomation:
    """用户故事自动化测试 - 浏览器自动化走查"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.test_results = {}
        
    async def setup_browser(self) -> bool:
        """设置浏览器环境"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 无头模式
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # 如果需要可视化调试，注释掉 --headless
            # chrome_options.add_argument("--headless")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            
            logger.info("✅ 浏览器环境设置成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 浏览器设置失败: {e}")
            return False
    
    async def run_user_story_tests(self) -> Dict[str, Any]:
        """运行用户故事测试"""
        logger.info("🎭 开始用户故事自动化测试")
        
        user_stories = [
            ("学术研究者故事", self._test_academic_researcher_story),
            ("商业决策者故事", self._test_business_decision_maker_story),
            ("普通用户故事", self._test_casual_user_story),
            ("场景切换用户故事", self._test_scenario_switching_story),
            ("个性化用户故事", self._test_personalization_story),
            ("错误处理用户故事", self._test_error_handling_story)
        ]
        
        overall_success = True
        
        for story_name, story_func in user_stories:
            logger.info(f"\n🔍 执行用户故事: {story_name}")
            try:
                start_time = time.time()
                result = await story_func()
                end_time = time.time()
                
                self.test_results[story_name] = {
                    "success": result.get("success", False),
                    "execution_time": end_time - start_time,
                    "details": result,
                    "timestamp": datetime.now().isoformat()
                }
                
                status = "✅ 通过" if result.get("success") else "❌ 失败"
                logger.info(f"{story_name}: {status} (耗时: {end_time - start_time:.2f}秒)")
                
                if not result.get("success"):
                    overall_success = False
                    logger.error(f"故事失败详情: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"用户故事执行异常: {story_name} - {e}")
                self.test_results[story_name] = {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                overall_success = False
        
        return {
            "overall_success": overall_success,
            "story_results": self.test_results,
            "total_stories": len(user_stories),
            "passed_stories": sum(1 for r in self.test_results.values() if r.get("success", False))
        }
    
    async def _test_academic_researcher_story(self) -> Dict[str, Any]:
        """学术研究者用户故事测试"""
        try:
            # 用户故事: 作为学术研究者，我想要深入研究AI在教育中的应用
            logger.info("📚 测试学术研究者用户故事")
            
            # 1. 访问主页
            self.driver.get("http://localhost:3000")
            await asyncio.sleep(2)
            
            # 2. 验证页面加载
            page_title = self.driver.title
            if not page_title:
                return {"success": False, "error": "主页未加载"}
            
            # 3. 寻找输入框并输入学术研究相关的查询
            try:
                input_element = self.wait.until(
                    EC.presence_of_element_located((By.TAG_NAME, "textarea"))
                )
                research_query = "我想深入研究AI在教育中的应用，包括机器学习算法如何改善个性化教学效果"
                input_element.clear()
                input_element.send_keys(research_query)
                
                # 4. 提交查询
                submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '发送') or contains(text(), 'Send')]")
                submit_button.click()
                
                # 5. 等待学术研究场景响应
                await self._wait_for_response()
                
                # 6. 验证学术研究场景特征
                academic_indicators = self._check_academic_response_indicators()
                
                success = academic_indicators["has_academic_content"]
                
                return {
                    "success": success,
                    "story_steps": {
                        "page_loaded": bool(page_title),
                        "input_successful": True,
                        "query_submitted": True,
                        "response_received": academic_indicators["has_response"],
                        "academic_context_detected": academic_indicators["has_academic_content"]
                    },
                    "academic_indicators": academic_indicators,
                    "query": research_query
                }
                
            except Exception as e:
                return {"success": False, "error": f"界面交互失败: {str(e)}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_business_decision_maker_story(self) -> Dict[str, Any]:
        """商业决策者用户故事测试"""
        try:
            # 用户故事: 作为技术总监，我需要专家建议来决定是否采用微服务架构
            logger.info("💼 测试商业决策者用户故事")
            
            # 1. 刷新页面或导航到新会话
            self.driver.refresh()
            await asyncio.sleep(2)
            
            # 2. 输入商业决策相关查询
            input_element = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "textarea"))
            )
            business_query = "我们公司现在是单体架构，团队有50人，我需要专家建议是否应该迁移到微服务架构"
            input_element.clear()
            input_element.send_keys(business_query)
            
            # 3. 提交查询
            submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '发送') or contains(text(), 'Send')]")
            submit_button.click()
            
            # 4. 等待专家咨询场景响应
            await self._wait_for_response()
            
            # 5. 验证专家咨询场景特征
            expert_indicators = self._check_expert_consultation_indicators()
            
            success = expert_indicators["has_expert_advice"]
            
            return {
                "success": success,
                "story_steps": {
                    "page_refreshed": True,
                    "business_query_submitted": True,
                    "expert_response_received": expert_indicators["has_response"],
                    "expert_context_detected": expert_indicators["has_expert_advice"]
                },
                "expert_indicators": expert_indicators,
                "query": business_query
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_casual_user_story(self) -> Dict[str, Any]:
        """普通用户故事测试"""
        try:
            # 用户故事: 作为普通用户，我想轻松聊聊最近看的好电影
            logger.info("😊 测试普通用户故事")
            
            # 1. 刷新页面
            self.driver.refresh()
            await asyncio.sleep(2)
            
            # 2. 输入轻松讨论相关查询
            input_element = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "textarea"))
            )
            casual_query = "最近看了什么好电影吗？大家来聊聊推荐一下"
            input_element.clear()
            input_element.send_keys(casual_query)
            
            # 3. 提交查询
            submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '发送') or contains(text(), 'Send')]")
            submit_button.click()
            
            # 4. 等待轻松讨论场景响应
            await self._wait_for_response()
            
            # 5. 验证轻松讨论场景特征
            casual_indicators = self._check_casual_discussion_indicators()
            
            success = casual_indicators["has_casual_tone"]
            
            return {
                "success": success,
                "story_steps": {
                    "casual_query_submitted": True,
                    "casual_response_received": casual_indicators["has_response"],
                    "casual_tone_detected": casual_indicators["has_casual_tone"]
                },
                "casual_indicators": casual_indicators,
                "query": casual_query
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_scenario_switching_story(self) -> Dict[str, Any]:
        """场景切换用户故事测试"""
        try:
            # 用户故事: 我先做学术研究，然后想要专家建议，最后轻松讨论
            logger.info("🔄 测试场景切换用户故事")
            
            switching_steps = []
            
            # 1. 开始学术研究
            self.driver.refresh()
            await asyncio.sleep(2)
            
            academic_query = "深度学习的最新发展趋势分析"
            input_element = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
            input_element.clear()
            input_element.send_keys(academic_query)
            
            submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '发送') or contains(text(), 'Send')]")
            submit_button.click()
            
            await self._wait_for_response()
            academic_response = self._check_academic_response_indicators()
            switching_steps.append({"step": "academic", "success": academic_response["has_academic_content"]})
            
            # 2. 切换到专家咨询
            await asyncio.sleep(2)
            expert_query = "基于刚才的研究，我需要专家建议如何在我们公司应用这些技术"
            
            input_element = self.driver.find_element(By.TAG_NAME, "textarea")
            input_element.clear()
            input_element.send_keys(expert_query)
            submit_button.click()
            
            await self._wait_for_response()
            expert_response = self._check_expert_consultation_indicators()
            switching_steps.append({"step": "expert", "success": expert_response["has_expert_advice"]})
            
            # 3. 切换到轻松讨论
            await asyncio.sleep(2)
            casual_query = "聊完正事，大家觉得AI技术发展会给我们生活带来什么有趣的变化？"
            
            input_element = self.driver.find_element(By.TAG_NAME, "textarea")
            input_element.clear()
            input_element.send_keys(casual_query)
            submit_button.click()
            
            await self._wait_for_response()
            casual_response = self._check_casual_discussion_indicators()
            switching_steps.append({"step": "casual", "success": casual_response["has_casual_tone"]})
            
            # 4. 验证切换成功
            successful_switches = sum(1 for step in switching_steps if step["success"])
            success = successful_switches >= 2  # 至少2个场景切换成功
            
            return {
                "success": success,
                "switching_steps": switching_steps,
                "successful_switches": successful_switches,
                "total_switches": len(switching_steps),
                "switch_success_rate": successful_switches / len(switching_steps)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_personalization_story(self) -> Dict[str, Any]:
        """个性化用户故事测试"""
        try:
            # 用户故事: 系统应该记住我的偏好并提供个性化体验
            logger.info("🎯 测试个性化用户故事")
            
            # 1. 建立用户偏好历史（模拟多次交互）
            preference_queries = [
                "我是研究生，经常需要做学术研究",
                "我对AI和机器学习特别感兴趣",
                "我喜欢深入的技术分析"
            ]
            
            personalization_indicators = []
            
            for i, query in enumerate(preference_queries):
                self.driver.refresh()
                await asyncio.sleep(1)
                
                input_element = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
                input_element.clear()
                input_element.send_keys(query)
                
                submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '发送') or contains(text(), 'Send')]")
                submit_button.click()
                
                await self._wait_for_response()
                
                # 检查是否有学术倾向的响应（基于用户偏好）
                response_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                has_academic_bias = any(word in response_text for word in ["研究", "分析", "学术", "深入"])
                
                personalization_indicators.append({
                    "query": query,
                    "academic_bias_detected": has_academic_bias
                })
            
            # 2. 最终测试：模糊查询应该倾向于学术场景
            final_query = "人工智能的发展"
            input_element = self.driver.find_element(By.TAG_NAME, "textarea")
            input_element.clear()
            input_element.send_keys(final_query)
            submit_button.click()
            
            await self._wait_for_response()
            final_response = self._check_academic_response_indicators()
            
            # 判断个性化是否生效
            academic_responses = sum(1 for indicator in personalization_indicators if indicator["academic_bias_detected"])
            personalization_success = academic_responses >= 2 and final_response["has_academic_content"]
            
            return {
                "success": personalization_success,
                "personalization_indicators": personalization_indicators,
                "final_query_academic_bias": final_response["has_academic_content"],
                "academic_bias_rate": academic_responses / len(personalization_indicators)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_error_handling_story(self) -> Dict[str, Any]:
        """错误处理用户故事测试"""
        try:
            # 用户故事: 当我输入无效内容时，系统应该优雅地处理
            logger.info("⚠️ 测试错误处理用户故事")
            
            error_test_cases = [
                {"input": "", "description": "空输入"},
                {"input": "   ", "description": "空白输入"},
                {"input": "x" * 10000, "description": "超长输入"},
                {"input": "!@#$%^&*()", "description": "特殊字符输入"}
            ]
            
            error_handling_results = []
            
            for test_case in error_test_cases:
                try:
                    self.driver.refresh()
                    await asyncio.sleep(1)
                    
                    input_element = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "textarea")))
                    input_element.clear()
                    input_element.send_keys(test_case["input"])
                    
                    submit_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '发送') or contains(text(), 'Send')]")
                    submit_button.click()
                    
                    # 等待响应或错误消息
                    await asyncio.sleep(3)
                    
                    # 检查页面是否仍然响应
                    page_responsive = True
                    try:
                        self.driver.find_element(By.TAG_NAME, "textarea")
                    except:
                        page_responsive = False
                    
                    # 检查是否有错误消息
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                    has_error_message = any(word in page_text for word in ["错误", "error", "失败", "invalid"])
                    
                    error_handling_results.append({
                        "test_case": test_case["description"],
                        "input_length": len(test_case["input"]),
                        "page_responsive": page_responsive,
                        "has_error_message": has_error_message,
                        "graceful_handling": page_responsive  # 页面仍可响应表示优雅处理
                    })
                    
                except Exception as e:
                    error_handling_results.append({
                        "test_case": test_case["description"],
                        "page_responsive": False,
                        "has_error_message": False,
                        "graceful_handling": False,
                        "error": str(e)
                    })
            
            # 计算错误处理质量
            graceful_cases = sum(1 for result in error_handling_results if result.get("graceful_handling", False))
            success = graceful_cases >= len(error_test_cases) * 0.75  # 75%的错误情况需要优雅处理
            
            return {
                "success": success,
                "error_handling_results": error_handling_results,
                "graceful_handling_rate": graceful_cases / len(error_test_cases),
                "total_test_cases": len(error_test_cases)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _wait_for_response(self, timeout: int = 30):
        """等待响应"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # 检查页面是否有新内容
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                if len(page_text) > 100:  # 简化检查：页面有足够内容
                    await asyncio.sleep(1)  # 额外等待确保内容加载完成
                    return True
            except:
                pass
            
            await asyncio.sleep(1)
        
        return False
    
    def _check_academic_response_indicators(self) -> Dict[str, bool]:
        """检查学术研究响应指标"""
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            academic_keywords = ["研究", "分析", "理论", "方法", "数据", "实验", "结论", "文献", "学术"]
            formal_indicators = ["首先", "其次", "然后", "总结", "综上所述"]
            
            has_academic_keywords = sum(1 for keyword in academic_keywords if keyword in page_text) >= 3
            has_formal_structure = any(indicator in page_text for indicator in formal_indicators)
            has_response = len(page_text) > 50
            
            return {
                "has_response": has_response,
                "has_academic_content": has_academic_keywords and has_formal_structure,
                "academic_keyword_count": sum(1 for keyword in academic_keywords if keyword in page_text),
                "has_formal_structure": has_formal_structure
            }
        except Exception as e:
            return {"has_response": False, "has_academic_content": False, "error": str(e)}
    
    def _check_expert_consultation_indicators(self) -> Dict[str, bool]:
        """检查专家咨询响应指标"""
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            expert_keywords = ["建议", "推荐", "专家", "经验", "方案", "决策", "评估", "考虑"]
            practical_indicators = ["实践", "应用", "实施", "操作", "执行"]
            
            has_expert_keywords = sum(1 for keyword in expert_keywords if keyword in page_text) >= 2
            has_practical_advice = any(indicator in page_text for indicator in practical_indicators)
            has_response = len(page_text) > 50
            
            return {
                "has_response": has_response,
                "has_expert_advice": has_expert_keywords or has_practical_advice,
                "expert_keyword_count": sum(1 for keyword in expert_keywords if keyword in page_text),
                "has_practical_advice": has_practical_advice
            }
        except Exception as e:
            return {"has_response": False, "has_expert_advice": False, "error": str(e)}
    
    def _check_casual_discussion_indicators(self) -> Dict[str, bool]:
        """检查轻松讨论响应指标"""
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            
            casual_keywords = ["聊聊", "觉得", "个人", "有趣", "好玩", "推荐", "分享", "大家"]
            informal_indicators = ["哈哈", "确实", "是啊", "我觉得", "个人认为"]
            
            has_casual_keywords = sum(1 for keyword in casual_keywords if keyword in page_text) >= 2
            has_informal_tone = any(indicator in page_text for indicator in informal_indicators)
            has_response = len(page_text) > 50
            
            return {
                "has_response": has_response,
                "has_casual_tone": has_casual_keywords or has_informal_tone,
                "casual_keyword_count": sum(1 for keyword in casual_keywords if keyword in page_text),
                "has_informal_tone": has_informal_tone
            }
        except Exception as e:
            return {"has_response": False, "has_casual_tone": False, "error": str(e)}
    
    async def cleanup_browser(self):
        """清理浏览器资源"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("✅ 浏览器资源清理完成")
            except Exception as e:
                logger.error(f"❌ 浏览器清理失败: {e}")


class ComprehensiveAutomationTester:
    """全面自动化测试协调器"""
    
    def __init__(self):
        self.service_manager = ServiceManager()
        self.user_story_automation = UserStoryAutomation()
        self.test_start_time = None
        
    async def run_comprehensive_automation_test(self) -> Dict[str, Any]:
        """运行全面的自动化测试"""
        logger.info("=" * 80)
        logger.info("🚀 开始全面用户故事覆盖自动化测试")
        logger.info("=" * 80)
        
        self.test_start_time = datetime.now()
        
        try:
            # 1. 启动所有服务
            logger.info("步骤 1: 启动服务")
            service_result = await self.service_manager.start_all_services()
            
            if not service_result["success"]:
                return {
                    "success": False,
                    "error": "服务启动失败",
                    "service_result": service_result
                }
            
            # 等待服务完全就绪
            await asyncio.sleep(5)
            
            # 2. 设置浏览器环境
            logger.info("步骤 2: 设置浏览器环境")
            browser_setup = await self.user_story_automation.setup_browser()
            
            if not browser_setup:
                await self.service_manager.stop_all_services()
                return {
                    "success": False,
                    "error": "浏览器设置失败"
                }
            
            # 3. 执行用户故事测试
            logger.info("步骤 3: 执行用户故事自动化测试")
            user_story_result = await self.user_story_automation.run_user_story_tests()
            
            # 4. 生成综合报告
            comprehensive_result = await self._generate_comprehensive_report(
                service_result, user_story_result
            )
            
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"全面自动化测试失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "test_duration": (datetime.now() - self.test_start_time).total_seconds()
            }
        
        finally:
            # 清理资源
            await self.user_story_automation.cleanup_browser()
            await self.service_manager.stop_all_services()
    
    async def _generate_comprehensive_report(
        self,
        service_result: Dict[str, Any],
        user_story_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成综合测试报告"""
        
        test_end_time = datetime.now()
        test_duration = (test_end_time - self.test_start_time).total_seconds()
        
        # 计算总体成功率
        service_success = service_result.get("success", False)
        user_story_success = user_story_result.get("overall_success", False)
        overall_success = service_success and user_story_success
        
        # 生成用户体验评估
        ux_assessment = self._assess_user_experience(user_story_result)
        
        # 生成系统可用性评估
        system_assessment = self._assess_system_usability(service_result, user_story_result)
        
        report = {
            "overall_success": overall_success,
            "test_summary": {
                "start_time": self.test_start_time.isoformat(),
                "end_time": test_end_time.isoformat(),
                "duration_seconds": test_duration,
                "duration_minutes": test_duration / 60
            },
            "service_deployment": {
                "success": service_success,
                "services_started": len([s for s in service_result.get("services", {}).values() if s.get("success", False)]),
                "total_services": len(service_result.get("services", {})),
                "details": service_result
            },
            "user_story_validation": {
                "success": user_story_success,
                "passed_stories": user_story_result.get("passed_stories", 0),
                "total_stories": user_story_result.get("total_stories", 0),
                "success_rate": user_story_result.get("passed_stories", 0) / max(user_story_result.get("total_stories", 1), 1),
                "details": user_story_result.get("story_results", {})
            },
            "user_experience_assessment": ux_assessment,
            "system_usability_assessment": system_assessment,
            "automation_quality": {
                "end_to_end_coverage": self._calculate_e2e_coverage(user_story_result),
                "scenario_coverage": self._calculate_scenario_coverage(user_story_result),
                "error_handling_quality": self._assess_error_handling_quality(user_story_result),
                "automation_reliability": overall_success
            },
            "recommendations": self._generate_recommendations(service_result, user_story_result),
            "next_steps": self._generate_next_steps(overall_success)
        }
        
        # 保存报告
        await self._save_comprehensive_report(report)
        
        return report
    
    def _assess_user_experience(self, user_story_result: Dict[str, Any]) -> Dict[str, Any]:
        """评估用户体验"""
        story_results = user_story_result.get("story_results", {})
        
        # 分析用户故事成功情况
        academic_success = story_results.get("学术研究者故事", {}).get("success", False)
        business_success = story_results.get("商业决策者故事", {}).get("success", False)
        casual_success = story_results.get("普通用户故事", {}).get("success", False)
        switching_success = story_results.get("场景切换用户故事", {}).get("success", False)
        personalization_success = story_results.get("个性化用户故事", {}).get("success", False)
        
        # 计算用户体验分数
        core_ux_score = (academic_success + business_success + casual_success) / 3
        advanced_ux_score = (switching_success + personalization_success) / 2
        overall_ux_score = (core_ux_score * 0.7) + (advanced_ux_score * 0.3)
        
        return {
            "overall_ux_score": overall_ux_score,
            "core_scenarios_ux": core_ux_score,
            "advanced_features_ux": advanced_ux_score,
            "scenario_specific_ux": {
                "academic_research": academic_success,
                "business_consultation": business_success,
                "casual_discussion": casual_success,
                "scenario_switching": switching_success,
                "personalization": personalization_success
            },
            "ux_rating": "优秀" if overall_ux_score >= 0.8 else "良好" if overall_ux_score >= 0.6 else "需改进"
        }
    
    def _assess_system_usability(self, service_result: Dict[str, Any], user_story_result: Dict[str, Any]) -> Dict[str, Any]:
        """评估系统可用性"""
        service_success = service_result.get("success", False)
        user_story_success = user_story_result.get("overall_success", False)
        
        # 计算系统各方面可用性
        deployment_usability = 1.0 if service_success else 0.0
        functional_usability = user_story_result.get("passed_stories", 0) / max(user_story_result.get("total_stories", 1), 1)
        
        # 获取错误处理质量
        error_handling_result = user_story_result.get("story_results", {}).get("错误处理用户故事", {})
        error_handling_usability = 1.0 if error_handling_result.get("success", False) else 0.5
        
        overall_usability = (deployment_usability * 0.3 + functional_usability * 0.5 + error_handling_usability * 0.2)
        
        return {
            "overall_usability": overall_usability,
            "deployment_usability": deployment_usability,
            "functional_usability": functional_usability,
            "error_handling_usability": error_handling_usability,
            "usability_rating": "优秀" if overall_usability >= 0.9 else "良好" if overall_usability >= 0.7 else "需改进",
            "production_ready": overall_usability >= 0.8
        }
    
    def _calculate_e2e_coverage(self, user_story_result: Dict[str, Any]) -> float:
        """计算端到端覆盖度"""
        story_results = user_story_result.get("story_results", {})
        
        # 端到端流程覆盖检查
        e2e_flows = [
            "学术研究者故事",  # 完整学术研究流程
            "商业决策者故事",  # 完整专家咨询流程
            "普通用户故事",   # 完整轻松讨论流程
            "场景切换用户故事"  # 跨场景流程
        ]
        
        covered_flows = sum(1 for flow in e2e_flows if story_results.get(flow, {}).get("success", False))
        return covered_flows / len(e2e_flows)
    
    def _calculate_scenario_coverage(self, user_story_result: Dict[str, Any]) -> Dict[str, bool]:
        """计算场景覆盖度"""
        story_results = user_story_result.get("story_results", {})
        
        return {
            "academic_research_covered": story_results.get("学术研究者故事", {}).get("success", False),
            "expert_consultation_covered": story_results.get("商业决策者故事", {}).get("success", False),
            "casual_discussion_covered": story_results.get("普通用户故事", {}).get("success", False),
            "scenario_switching_covered": story_results.get("场景切换用户故事", {}).get("success", False)
        }
    
    def _assess_error_handling_quality(self, user_story_result: Dict[str, Any]) -> Dict[str, Any]:
        """评估错误处理质量"""
        error_handling_result = user_story_result.get("story_results", {}).get("错误处理用户故事", {})
        
        if error_handling_result.get("success", False):
            details = error_handling_result.get("details", {})
            return {
                "graceful_handling": True,
                "handling_rate": details.get("graceful_handling_rate", 0),
                "quality": "优秀"
            }
        else:
            return {
                "graceful_handling": False,
                "handling_rate": 0,
                "quality": "需改进"
            }
    
    def _generate_recommendations(self, service_result: Dict[str, Any], user_story_result: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 服务部署建议
        if not service_result.get("success", False):
            recommendations.append("修复服务启动问题，确保后端和前端服务能够正常启动")
        
        # 用户故事建议
        story_results = user_story_result.get("story_results", {})
        for story_name, result in story_results.items():
            if not result.get("success", False):
                recommendations.append(f"改进{story_name}的用户体验，解决: {result.get('error', '未知问题')}")
        
        # 如果所有测试都通过
        if not recommendations:
            recommendations.extend([
                "✅ 所有自动化测试通过，系统具备良好的用户体验",
                "建议进行更大规模的用户验收测试",
                "考虑添加更多复杂的用户故事场景",
                "准备生产环境部署"
            ])
        
        return recommendations
    
    def _generate_next_steps(self, overall_success: bool) -> List[str]:
        """生成下一步行动"""
        if overall_success:
            return [
                "1. 执行生产环境部署测试",
                "2. 进行真实用户beta测试",
                "3. 收集用户反馈并持续改进",
                "4. 准备正式发布"
            ]
        else:
            return [
                "1. 修复所有失败的用户故事测试",
                "2. 改进系统稳定性和可用性",
                "3. 重新执行全面自动化测试",
                "4. 确保所有质量标准达到要求"
            ]
    
    async def _save_comprehensive_report(self, report: Dict[str, Any]):
        """保存综合报告"""
        try:
            report_path = Path("comprehensive_automation_test_report.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            logger.info(f"综合自动化测试报告已保存: {report_path}")
        except Exception as e:
            logger.error(f"报告保存失败: {e}")


async def main():
    """主函数 - 执行全面用户故事覆盖自动化测试"""
    tester = ComprehensiveAutomationTester()
    
    try:
        result = await tester.run_comprehensive_automation_test()
        
        print("\n" + "=" * 100)
        print("📊 全面用户故事覆盖自动化测试报告")
        print("=" * 100)
        print(f"总体结果: {'✅ 成功' if result.get('overall_success') else '❌ 失败'}")
        print(f"测试时长: {result.get('test_summary', {}).get('duration_minutes', 0):.1f}分钟")
        
        # 服务部署状态
        service_deployment = result.get("service_deployment", {})
        print(f"\n🚀 服务部署:")
        print(f"  服务启动: {'✅' if service_deployment.get('success') else '❌'}")
        print(f"  成功启动: {service_deployment.get('services_started', 0)}/{service_deployment.get('total_services', 0)}")
        
        # 用户故事验证状态
        user_story_validation = result.get("user_story_validation", {})
        print(f"\n👥 用户故事验证:")
        print(f"  故事验证: {'✅' if user_story_validation.get('success') else '❌'}")
        print(f"  通过故事: {user_story_validation.get('passed_stories', 0)}/{user_story_validation.get('total_stories', 0)}")
        print(f"  成功率: {user_story_validation.get('success_rate', 0):.1%}")
        
        # 用户体验评估
        ux_assessment = result.get("user_experience_assessment", {})
        print(f"\n🎯 用户体验评估:")
        print(f"  整体评分: {ux_assessment.get('overall_ux_score', 0):.1%}")
        print(f"  用户体验: {ux_assessment.get('ux_rating', '未知')}")
        
        # 系统可用性评估
        system_assessment = result.get("system_usability_assessment", {})
        print(f"\n⚙️ 系统可用性:")
        print(f"  可用性评分: {system_assessment.get('overall_usability', 0):.1%}")
        print(f"  可用性等级: {system_assessment.get('usability_rating', '未知')}")
        print(f"  生产就绪: {'✅' if system_assessment.get('production_ready') else '❌'}")
        
        # 自动化质量
        automation_quality = result.get("automation_quality", {})
        print(f"\n🤖 自动化质量:")
        print(f"  端到端覆盖: {automation_quality.get('end_to_end_coverage', 0):.1%}")
        print(f"  自动化可靠性: {'✅' if automation_quality.get('automation_reliability') else '❌'}")
        
        print(f"\n💡 建议:")
        for rec in result.get("recommendations", []):
            print(f"  • {rec}")
        
        print(f"\n🚀 下一步:")
        for step in result.get("next_steps", []):
            print(f"  {step}")
        
        print("\n" + "=" * 100)
        
        return result.get("overall_success", False)
        
    except Exception as e:
        logger.error(f"自动化测试执行失败: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)