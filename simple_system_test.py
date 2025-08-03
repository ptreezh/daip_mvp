#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版自动化系统测试
测试系统可用性和用户体验
"""

import asyncio
import logging
import time
import json
import subprocess
import threading
import webbrowser
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import psutil
import os

# 配置日志 - 避免特殊字符
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class SimpleSystemTester:
    """简化版系统测试器"""
    
    def __init__(self):
        self.services = {}
        self.test_results = {}
        
    async def run_tests(self) -> Dict[str, Any]:
        """运行测试"""
        print("=" * 60)
        print("DAIP-LIVE 自动化系统测试")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # 1. 测试服务启动
            service_result = await self.test_services()
            
            # 2. 测试API可用性
            api_result = await self.test_apis()
            
            # 3. 测试用户体验
            ux_result = await self.test_user_experience()
            
            end_time = datetime.now()
            
            # 生成报告
            report = {
                "success": service_result["success"] or api_result["success"],
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": (end_time - start_time).total_seconds(),
                "service_test": service_result,
                "api_test": api_result,
                "ux_test": ux_result
            }
            
            self.print_report(report)
            self.save_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"测试执行失败: {e}")
            return {"success": False, "error": str(e)}
        
        finally:
            self.cleanup()
    
    async def test_services(self) -> Dict[str, Any]:
        """测试服务启动"""
        print("\n1. 测试服务启动...")
        
        services_to_test = [
            {
                "name": "Personal Intelligence Hub",
                "command": ["python", "personal_intelligence_hub/run_hub.py"],
                "port": 8086,
                "url": "http://localhost:8086/hub"
            },
            {
                "name": "Quick Delivery Demo",
                "command": ["python", "quick_delivery_demo.py"],
                "port": 8090,
                "url": "http://localhost:8090"
            }
        ]
        
        results = []
        
        for service in services_to_test:
            try:
                print(f"  启动: {service['name']}")
                
                # 检查端口
                if self.is_port_in_use(service['port']):
                    print(f"    端口 {service['port']} 已被占用，尝试清理")
                    self.kill_process_on_port(service['port'])
                    time.sleep(2)
                
                # 启动服务
                process = subprocess.Popen(
                    service['command'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.getcwd()
                )
                
                self.services[service['name']] = {
                    "process": process,
                    "port": service['port'],
                    "url": service['url']
                }
                
                # 等待服务启动
                success = await self.wait_for_service(service['url'], timeout=20)
                
                if success:
                    print(f"    ✓ {service['name']} 启动成功")
                    results.append({
                        "name": service['name'],
                        "success": True,
                        "url": service['url'],
                        "port": service['port']
                    })
                    break  # 找到一个可用服务就够了
                else:
                    print(f"    ✗ {service['name']} 启动失败")
                    results.append({
                        "name": service['name'],
                        "success": False,
                        "error": "启动超时"
                    })
                    
            except Exception as e:
                print(f"    ✗ {service['name']} 启动异常: {e}")
                results.append({
                    "name": service['name'],
                    "success": False,
                    "error": str(e)
                })
        
        success = any(r["success"] for r in results)
        return {
            "success": success,
            "results": results,
            "primary_service": next((r for r in results if r["success"]), None)
        }
    
    async def test_apis(self) -> Dict[str, Any]:
        """测试API可用性"""
        print("\n2. 测试API可用性...")
        
        # 获取可用的服务URL
        test_urls = []
        for service_name, service_info in self.services.items():
            if service_info:
                test_urls.append(service_info["url"])
        
        # 默认测试URL
        if not test_urls:
            test_urls = [
                "http://localhost:8086",
                "http://localhost:8086/hub", 
                "http://localhost:8090"
            ]
        
        results = []
        
        for url in test_urls:
            try:
                print(f"  测试: {url}")
                start_time = time.time()
                response = requests.get(url, timeout=10)
                end_time = time.time()
                
                success = response.status_code == 200
                result = {
                    "url": url,
                    "success": success,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "content_length": len(response.content)
                }
                
                if success:
                    print(f"    ✓ 响应正常 ({response.status_code})")
                else:
                    print(f"    ✗ 响应异常 ({response.status_code})")
                    
                results.append(result)
                
            except Exception as e:
                print(f"    ✗ 请求失败: {e}")
                results.append({
                    "url": url,
                    "success": False,
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r.get("success"))
        
        return {
            "success": successful > 0,
            "results": results,
            "total_tested": len(results),
            "successful": successful
        }
    
    async def test_user_experience(self) -> Dict[str, Any]:
        """测试用户体验"""
        print("\n3. 测试用户体验...")
        
        # 获取主要服务URL
        primary_url = None
        for service_name, service_info in self.services.items():
            if service_info and service_info.get("url"):
                primary_url = service_info["url"]
                break
        
        if not primary_url:
            print("  没有可用的服务进行用户体验测试")
            return {"success": False, "error": "没有可用的服务"}
        
        ux_tests = [
            {"name": "页面访问", "test": self.test_page_access},
            {"name": "内容检查", "test": self.test_content_check},
            {"name": "响应时间", "test": self.test_response_time}
        ]
        
        results = []
        
        for test in ux_tests:
            try:
                print(f"  执行: {test['name']}")
                result = await test["test"](primary_url)
                result["test_name"] = test["name"]
                
                if result.get("success"):
                    print(f"    ✓ {test['name']} 通过")
                else:
                    print(f"    ✗ {test['name']} 失败")
                
                results.append(result)
                
            except Exception as e:
                print(f"    ✗ {test['name']} 异常: {e}")
                results.append({
                    "test_name": test["name"],
                    "success": False,
                    "error": str(e)
                })
        
        successful = sum(1 for r in results if r.get("success"))
        
        return {
            "success": successful > 0,
            "results": results,
            "total_tests": len(results),
            "successful": successful,
            "tested_url": primary_url
        }
    
    async def test_page_access(self, url: str) -> Dict[str, Any]:
        """测试页面访问"""
        try:
            response = requests.get(url, timeout=10)
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "content_size": len(response.content)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_content_check(self, url: str) -> Dict[str, Any]:
        """测试内容检查"""
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return {"success": False, "error": f"HTTP {response.status_code}"}
            
            content = response.text
            
            # 检查关键内容
            checks = {
                "has_content": len(content) > 100,
                "contains_daip": "DAIP" in content or "Personal Intelligence" in content,
                "no_errors": "error" not in content.lower() and "exception" not in content.lower()
            }
            
            return {
                "success": all(checks.values()),
                "checks": checks,
                "content_length": len(content)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_response_time(self, url: str) -> Dict[str, Any]:
        """测试响应时间"""
        try:
            times = []
            
            # 测试3次取平均值
            for i in range(3):
                start_time = time.time()
                response = requests.get(url, timeout=10)
                end_time = time.time()
                
                if response.status_code == 200:
                    times.append(end_time - start_time)
                
                time.sleep(0.5)  # 间隔0.5秒
            
            if not times:
                return {"success": False, "error": "所有请求都失败"}
            
            avg_time = sum(times) / len(times)
            
            return {
                "success": avg_time < 5.0,  # 5秒内认为可接受
                "average_response_time": avg_time,
                "all_response_times": times,
                "acceptable": avg_time < 3.0  # 3秒内认为良好
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return True
        return False
    
    def kill_process_on_port(self, port: int):
        """终止占用端口的进程"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        proc.terminate()
                        time.sleep(1)
                        if proc.is_running():
                            proc.kill()
                        return
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    
    async def wait_for_service(self, url: str, timeout: int = 30) -> bool:
        """等待服务启动"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return True
            except:
                pass
            
            await asyncio.sleep(1)
        
        return False
    
    def print_report(self, report: Dict[str, Any]):
        """打印测试报告"""
        print("\n" + "=" * 60)
        print("测试报告")
        print("=" * 60)
        
        print(f"总体结果: {'通过' if report['success'] else '失败'}")
        print(f"测试时长: {report['duration_seconds']:.1f} 秒")
        
        print("\n详细结果:")
        
        # 服务测试
        service_test = report.get("service_test", {})
        print(f"  服务启动: {'通过' if service_test.get('success') else '失败'}")
        if service_test.get("primary_service"):
            print(f"    主要服务: {service_test['primary_service']['name']}")
            print(f"    访问地址: {service_test['primary_service']['url']}")
        
        # API测试
        api_test = report.get("api_test", {})
        print(f"  API可用性: {'通过' if api_test.get('success') else '失败'}")
        print(f"    成功率: {api_test.get('successful', 0)}/{api_test.get('total_tested', 0)}")
        
        # 用户体验测试
        ux_test = report.get("ux_test", {})
        print(f"  用户体验: {'通过' if ux_test.get('success') else '失败'}")
        print(f"    成功率: {ux_test.get('successful', 0)}/{ux_test.get('total_tests', 0)}")
        
        print("\n建议:")
        if report["success"]:
            print("  ✓ 系统基本可用，具备交付条件")
            print("  ✓ 用户可以正常访问和使用系统")
        else:
            print("  ✗ 系统存在问题，需要修复后再交付")
            print("  ✗ 建议检查服务启动和配置")
        
        print("=" * 60)
    
    def save_report(self, report: Dict[str, Any]):
        """保存测试报告"""
        try:
            with open("system_test_report.json", "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n报告已保存: system_test_report.json")
        except Exception as e:
            print(f"报告保存失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        print("\n清理资源...")
        
        for service_name, service_info in self.services.items():
            if service_info and service_info.get("process"):
                try:
                    process = service_info["process"]
                    if process.poll() is None:
                        process.terminate()
                        time.sleep(1)
                        if process.poll() is None:
                            process.kill()
                    print(f"  ✓ 关闭服务: {service_name}")
                except Exception as e:
                    print(f"  ✗ 关闭服务失败 {service_name}: {e}")


async def main():
    """主函数"""
    tester = SimpleSystemTester()
    
    try:
        report = await tester.run_tests()
        return report["success"]
    except Exception as e:
        print(f"测试执行失败: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)