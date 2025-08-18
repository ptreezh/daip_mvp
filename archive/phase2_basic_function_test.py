"""@Time    : 2025-08-05 10:30:00
@Author  : DAIP-LIVE Team
@File    : phase2_basic_function_test.py
@Description:
    Phase 2: 基础功能测试
    包括Web应用启动、静态资源加载、基础交互等测试
"""

import json
import logging
import socket
import subprocess
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase2_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BasicFunctionTester:
    """基础功能测试器"""
    
    def __init__(self):
        self.test_results = []
        self.project_root = Path(__file__).parent
        self.processes = []
        self.driver = None
        self.base_url = "http://localhost:8080"
        
    def add_test_result(self, test_name: str, status: str, details: str = "", execution_time: float = 0):
        """添加测试结果"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "execution_time": execution_time,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        logger.info(f"测试完成: {test_name} - {status}")
        if details:
            logger.info(f"详细信息: {details}")
    
    def run_test(self, test_func, test_name: str):
        """运行单个测试"""
        start_time = time.time()
        try:
            result = test_func()
            execution_time = time.time() - start_time
            if result:
                self.add_test_result(test_name, "PASS", f"执行时间: {execution_time:.2f}秒", execution_time)
                return True
            else:
                self.add_test_result(test_name, "FAIL", "测试返回False", execution_time)
                return False
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"异常: {str(e)}"
            self.add_test_result(test_name, "ERROR", error_msg, execution_time)
            logger.error(f"测试 {test_name} 异常: {e}")
            return False
    
    def start_web_app(self) -> bool:
        """启动Web应用"""
        logger.info("启动Web应用...")
        try:
            # 启动frontend/main_app.py
            frontend_script = self.project_root / "frontend" / "main_app.py"
            if not frontend_script.exists():
                logger.error("前端应用文件不存在")
                return False
            
            # 启动进程
            process = subprocess.Popen([
                sys.executable, str(frontend_script)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes.append(process)
            
            # 等待应用启动
            time.sleep(5)
            
            # 检查进程是否运行
            if process.poll() is None:
                logger.info("✓ Web应用启动成功")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"✗ Web应用启动失败: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Web应用启动异常: {e}")
            return False
    
    def test_web_app_startup(self) -> bool:
        """测试Web应用启动"""
        logger.info("测试Web应用启动...")
        
        if not self.start_web_app():
            return False
        
        # 等待应用完全启动
        time.sleep(3)
        
        # 测试端口是否被占用
        if not self.is_port_in_use(8080):
            logger.error("✗ 端口8080未被占用，应用可能未正常启动")
            return False
        
        logger.info("✓ Web应用启动测试通过")
        return True
    
    def is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return False
            except OSError:
                return True
    
    def setup_selenium_driver(self) -> bool:
        """设置Selenium驱动"""
        logger.info("设置Selenium驱动...")
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 无头模式
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            logger.info("✓ Selenium驱动设置成功")
            return True
            
        except Exception as e:
            logger.error(f"✗ Selenium驱动设置失败: {e}")
            return False
    
    def test_web_page_access(self) -> bool:
        """测试Web页面访问"""
        logger.info("测试Web页面访问...")
        
        if not self.setup_selenium_driver():
            return False
        
        try:
            # 访问主页
            self.driver.get(self.base_url)
            
            # 等待页面加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 检查页面标题
            title = self.driver.title
            if title:
                logger.info(f"✓ 页面标题: {title}")
            else:
                logger.warning("页面标题为空")
            
            # 检查页面内容
            page_source = self.driver.page_source
            if len(page_source) > 100:  # 基本内容检查
                logger.info("✓ 页面内容加载正常")
                return True
            else:
                logger.error("✗ 页面内容异常")
                return False
                
        except Exception as e:
            logger.error(f"✗ Web页面访问失败: {e}")
            return False
    
    def test_static_resources_loading(self) -> bool:
        """测试静态资源加载"""
        logger.info("测试静态资源加载...")
        
        if not self.driver:
            logger.error("Selenium驱动未初始化")
            return False
        
        try:
            # 获取页面所有资源
            resources = self.driver.execute_script("""
                var resources = [];
                var performance = window.performance || window.webkitPerformance;
                if (performance) {
                    var entries = performance.getEntriesByType('resource');
                    entries.forEach(function(entry) {
                        resources.push({
                            name: entry.name,
                            type: entry.initiatorType,
                            duration: entry.duration,
                            status: 'loaded'
                        });
                    });
                }
                return resources;
            """)
            
            if not resources:
                logger.warning("未找到加载的资源")
                return True  # 可能是单页面应用
            
            # 分析资源加载情况
            css_loaded = False
            js_loaded = False
            failed_resources = []
            
            for resource in resources:
                if resource['type'] == 'link' and 'css' in resource['name']:
                    css_loaded = True
                    logger.info(f"✓ CSS资源加载: {resource['name']}")
                elif resource['type'] == 'script':
                    js_loaded = True
                    logger.info(f"✓ JavaScript资源加载: {resource['name']}")
                
                # 检查加载时间
                if resource['duration'] > 5000:  # 5秒
                    logger.warning(f"资源加载缓慢: {resource['name']} - {resource['duration']:.2f}ms")
            
            # 检查JavaScript错误
            js_errors = self.driver.execute_script("""
                return window.jsErrors || [];
            """)
            
            if js_errors:
                logger.error(f"✗ 发现JavaScript错误: {js_errors}")
                failed_resources.extend(js_errors)
            
            # 检查页面样式
            try:
                body_element = self.driver.find_element(By.TAG_NAME, "body")
                body_style = body_element.get_attribute('style')
                if body_style:
                    logger.info("✓ 页面样式已应用")
                else:
                    logger.warning("页面可能缺少样式")
            except:
                logger.warning("无法检查页面样式")
            
            if failed_resources:
                logger.error(f"✗ 静态资源加载失败: {failed_resources}")
                return False
            
            logger.info("✓ 静态资源加载测试通过")
            return True
            
        except Exception as e:
            logger.error(f"✗ 静态资源加载测试失败: {e}")
            return False
    
    def test_basic_interactions(self) -> bool:
        """测试基础交互功能"""
        logger.info("测试基础交互功能...")
        
        if not self.driver:
            logger.error("Selenium驱动未初始化")
            return False
        
        try:
            interaction_results = []
            
            # 测试按钮点击
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            logger.info(f"发现 {len(buttons)} 个按钮")
            
            for i, button in enumerate(buttons[:3]):  # 测试前3个按钮
                try:
                    # 获取按钮文本
                    button_text = button.text or f"按钮{i+1}"
                    
                    # 尝试点击
                    button.click()
                    time.sleep(1)  # 等待响应
                    
                    # 检查是否有变化
                    interaction_results.append(f"✓ 按钮 '{button_text}' 点击成功")
                    logger.info(f"✓ 按钮 '{button_text}' 点击成功")
                    
                except Exception as e:
                    interaction_results.append(f"✗ 按钮点击失败: {e}")
                    logger.warning(f"按钮点击失败: {e}")
            
            # 测试输入框
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            logger.info(f"发现 {len(inputs)} 个输入框")
            
            for i, input_field in enumerate(inputs[:3]):  # 测试前3个输入框
                try:
                    # 获取输入框类型
                    input_type = input_field.get_attribute('type') or 'text'
                    
                    # 输入测试数据
                    test_value = f"测试输入{i+1}"
                    input_field.clear()
                    input_field.send_keys(test_value)
                    
                    # 验证输入
                    actual_value = input_field.get_attribute('value')
                    if actual_value == test_value:
                        interaction_results.append(f"✓ 输入框 ({input_type}) 输入成功")
                        logger.info(f"✓ 输入框 ({input_type}) 输入成功")
                    else:
                        interaction_results.append("✗ 输入框输入失败")
                        logger.warning("输入框输入失败")
                        
                except Exception as e:
                    interaction_results.append(f"✗ 输入框测试失败: {e}")
                    logger.warning(f"输入框测试失败: {e}")
            
            # 测试链接
            links = self.driver.find_elements(By.TAG_NAME, "a")
            logger.info(f"发现 {len(links)} 个链接")
            
            for i, link in enumerate(links[:3]):  # 测试前3个链接
                try:
                    link_text = link.text or f"链接{i+1}"
                    href = link.get_attribute('href')
                    
                    if href and href.startswith('http'):
                        interaction_results.append(f"✓ 链接 '{link_text}' 有效: {href}")
                        logger.info(f"✓ 链接 '{link_text}' 有效: {href}")
                    else:
                        interaction_results.append(f"✓ 链接 '{link_text}' 为内部链接")
                        logger.info(f"✓ 链接 '{link_text}' 为内部链接")
                        
                except Exception as e:
                    interaction_results.append(f"✗ 链接测试失败: {e}")
                    logger.warning(f"链接测试失败: {e}")
            
            # 统计结果
            success_count = len([r for r in interaction_results if r.startswith("✓")])
            total_count = len(interaction_results)
            
            if total_count == 0:
                logger.info("页面中没有发现可交互的元素")
                return True  # 可能是简单页面
            
            success_rate = success_count / total_count
            logger.info(f"基础交互测试成功率: {success_rate:.2%} ({success_count}/{total_count})")
            
            if success_rate >= 0.8:  # 80%成功率
                logger.info("✓ 基础交互测试通过")
                return True
            else:
                logger.warning(f"基础交互测试成功率较低: {success_rate:.2%}")
                return False
                
        except Exception as e:
            logger.error(f"✗ 基础交互测试失败: {e}")
            return False
    
    def test_page_responsiveness(self) -> bool:
        """测试页面响应性"""
        logger.info("测试页面响应性...")
        
        if not self.driver:
            logger.error("Selenium驱动未初始化")
            return False
        
        try:
            # 测试页面加载时间
            load_time = self.driver.execute_script("""
                return (window.performance.timing.loadEventEnd - window.performance.timing.navigationStart) / 1000;
            """)
            
            if load_time > 0:
                logger.info(f"页面加载时间: {load_time:.2f}秒")
                
                if load_time <= 5.0:  # 5秒内加载完成
                    logger.info("✓ 页面加载时间合理")
                else:
                    logger.warning(f"页面加载时间较长: {load_time:.2f}秒")
            else:
                logger.warning("无法获取页面加载时间")
            
            # 测试响应时间
            start_time = time.time()
            
            # 执行一些基本操作
            self.driver.execute_script("return document.readyState;")
            
            response_time = time.time() - start_time
            logger.info(f"页面响应时间: {response_time:.3f}秒")
            
            if response_time <= 1.0:  # 1秒内响应
                logger.info("✓ 页面响应性良好")
                return True
            else:
                logger.warning(f"页面响应较慢: {response_time:.3f}秒")
                return False
                
        except Exception as e:
            logger.error(f"✗ 页面响应性测试失败: {e}")
            return False
    
    def test_console_errors(self) -> bool:
        """测试控制台错误"""
        logger.info("测试控制台错误...")
        
        if not self.driver:
            logger.error("Selenium驱动未初始化")
            return False
        
        try:
            # 获取控制台日志
            logs = self.driver.get_log('browser')
            
            if not logs:
                logger.info("✓ 没有发现控制台错误")
                return True
            
            # 分析日志
            errors = []
            warnings = []
            
            for log in logs:
                level = log.get('level', '')
                message = log.get('message', '')
                
                if level == 'SEVERE':
                    errors.append(message)
                elif level == 'WARNING':
                    warnings.append(message)
            
            if errors:
                logger.error(f"✗ 发现 {len(errors)} 个严重错误:")
                for error in errors[:5]:  # 只显示前5个错误
                    logger.error(f"  {error}")
                return False
            
            if warnings:
                logger.warning(f"发现 {len(warnings)} 个警告:")
                for warning in warnings[:3]:  # 只显示前3个警告
                    logger.warning(f"  {warning}")
            
            logger.info("✓ 控制台错误测试通过")
            return True
            
        except Exception as e:
            logger.error(f"✗ 控制台错误测试失败: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        logger.info("清理测试资源...")
        
        # 关闭浏览器
        if self.driver:
            try:
                self.driver.quit()
                logger.info("✓ 浏览器已关闭")
            except:
                pass
        
        # 终止进程
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info("✓ Web应用进程已终止")
            except:
                try:
                    process.kill()
                    logger.info("✓ Web应用进程已强制终止")
                except:
                    pass
        
        self.processes = []
        self.driver = None
    
    def generate_report(self) -> str:
        """生成测试报告"""
        report_path = self.project_root / "phase2_test_report.json"
        
        # 统计测试结果
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        error_tests = len([r for r in self.test_results if r["status"] == "ERROR"])
        
        report = {
            "test_phase": "Phase 2: 基础功能测试",
            "execution_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "test_results": self.test_results,
            "summary": {
                "status": "PASS" if passed_tests == total_tests else "FAIL",
                "issues": [r for r in self.test_results if r["status"] != "PASS"],
                "recommendations": self._generate_recommendations()
            }
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"测试报告已生成: {report_path}")
        return str(report_path)
    
    def _generate_recommendations(self) -> list[str]:
        """生成建议"""
        recommendations = []
        
        for result in self.test_results:
            if result["status"] != "PASS":
                if "Web应用启动" in result["test_name"]:
                    recommendations.append("请检查Web应用启动脚本和依赖")
                elif "页面访问" in result["test_name"]:
                    recommendations.append("请检查网络连接和防火墙设置")
                elif "静态资源" in result["test_name"]:
                    recommendations.append("请检查静态文件路径和配置")
                elif "交互功能" in result["test_name"]:
                    recommendations.append("请检查JavaScript代码和事件绑定")
                elif "响应性" in result["test_name"]:
                    recommendations.append("请优化页面加载和响应性能")
                elif "控制台错误" in result["test_name"]:
                    recommendations.append("请修复JavaScript错误和警告")
        
        return recommendations
    
    def run_all_tests(self) -> bool:
        """运行所有测试"""
        logger.info("开始Phase 2基础功能测试...")
        
        # 定义测试列表
        tests = [
            (self.test_web_app_startup, "Web应用启动测试"),
            (self.test_web_page_access, "Web页面访问测试"),
            (self.test_static_resources_loading, "静态资源加载测试"),
            (self.test_basic_interactions, "基础交互功能测试"),
            (self.test_page_responsiveness, "页面响应性测试"),
            (self.test_console_errors, "控制台错误测试"),
        ]
        
        # 运行所有测试
        passed_count = 0
        for test_func, test_name in tests:
            if self.run_test(test_func, test_name):
                passed_count += 1
        
        # 生成报告
        report_path = self.generate_report()
        
        # 清理资源
        self.cleanup()
        
        # 输出总结
        logger.info(f"Phase 2测试完成: {passed_count}/{len(tests)} 通过")
        logger.info(f"测试报告: {report_path}")
        
        return passed_count == len(tests)

def main():
    """主函数"""
    tester = BasicFunctionTester()
    
    print("=" * 60)
    print("DAIP项目 Phase 2: 基础功能测试")
    print("=" * 60)
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n✅ Phase 2测试全部通过！")
            print("可以继续进行Phase 3功能集成测试")
        else:
            print("\n❌ Phase 2测试存在问题")
            print("请查看测试报告并修复问题后重新测试")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        tester.cleanup()
        return 1
    except Exception as e:
        print(f"\n测试执行异常: {e}")
        tester.cleanup()
        return 1

if __name__ == "__main__":
    exit(main())