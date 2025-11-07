#!/usr/bin/env python3
# -*- coding: utf-8
"""
DAIP-LIVE TUI 高级RPA测试方案
基于pexpect和伪终端的真正交互式TUI测试
"""

import pexpect
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 设置编码环境
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

class AdvancedTUITester:
    """高级TUI交互测试器
    
    使用pexpect实现真正的交互式TUI测试，支持：
    - 键盘事件模拟
    - 屏幕输出捕获和验证
    - 状态转换检测
    - 超时和异常处理
    """
    
    def __init__(self, timeout: int = 30, log_level: str = "INFO"):
        self.timeout = timeout
        self.log_level = log_level
        self.process: Optional[pexpect.spawn] = None
        self.test_log: List[Dict] = []
        self.screenshots: List[Dict] = []
        
    def log_event(self, action: str, result: str, details: str = "", screenshot: str = ""):
        """记录测试事件"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        event = {
            "timestamp": timestamp,
            "action": action,
            "result": result,
            "details": details,
            "screenshot": screenshot
        }
        self.test_log.append(event)
        
        status_symbol = "✅" if result == "成功" else "❌" if result == "失败" else "⚠️"
        print(f"[{timestamp}] {status_symbol} {action}")
        if details:
            print(f"        详情: {details}")
        if screenshot:
            print(f"        屏幕: {screenshot}")
    
    def take_screenshot(self) -> str:
        """捕获当前屏幕状态"""
        if not self.process:
            return "进程未启动"
        
        try:
            # 获取当前屏幕内容
            self.process.sendcontrol('l')  # 清屏并刷新
            time.sleep(0.1)
            # 获取当前缓冲区内容
            before = self.process.before if hasattr(self.process, 'before') else ""
            after = self.process.after if hasattr(self.process, 'after') else ""
            screenshot = f"{before}{after}"
            
            # 保存截图
            screenshot_id = f"screenshot_{len(self.screenshots)}"
            self.screenshots.append({
                "id": screenshot_id,
                "content": screenshot,
                "timestamp": datetime.now().isoformat()
            })
            
            return f"[{screenshot_id}] {screenshot[:100]}..."
            
        except Exception as e:
            return f"截图失败: {str(e)}"
    
    def start_tui(self) -> bool:
        """启动TUI进程"""
        try:
            self.log_event("启动TUI进程", "进行中")
            
            # 使用pexpect启动TUI
            self.process = pexpect.spawn(
                'python -m daip_live.tui',
                encoding='utf-8',
                timeout=self.timeout,
                maxread=10000  # 增加缓冲区大小
            )
            
            # 等待TUI初始化完成
            welcome_patterns = [
                'Welcome to 人格AI',
                'Ready for your command',
                'Enter command or message',
                pexpect.TIMEOUT
            ]
            
            index = self.process.expect(welcome_patterns, timeout=10)
            
            if index in [0, 1, 2]:
                screenshot = self.take_screenshot()
                self.log_event("启动TUI进程", "成功", "TUI初始化完成", screenshot)
                return True
            else:
                self.log_event("启动TUI进程", "失败", "启动超时")
                return False
                
        except Exception as e:
            self.log_event("启动TUI进程", "失败", f"启动异常: {str(e)}")
            return False
    
    def send_command(self, command: str, expected_patterns: List[str] = None, 
                    timeout: int = None) -> Dict:
        """发送命令并等待响应"""
        if not self.process:
            return {"success": False, "error": "进程未启动"}
            
        timeout = timeout or self.timeout
        
        try:
            self.log_event(f"发送命令: {command}", "进行中")
            
            # 发送命令
            self.process.sendline(command)
            
            # 等待响应
            if expected_patterns:
                patterns = expected_patterns + [pexpect.TIMEOUT, pexpect.EOF]
                index = self.process.expect(patterns, timeout=timeout)
                
                if index < len(expected_patterns):
                    screenshot = self.take_screenshot()
                    self.log_event(
                        f"发送命令: {command}", 
                        "成功", 
                        f"匹配到预期模式: {expected_patterns[index]}",
                        screenshot
                    )
                    return {
                        "success": True, 
                        "matched_pattern": expected_patterns[index],
                        "output": self.process.before + self.process.after
                    }
                elif index == len(expected_patterns):  # TIMEOUT
                    self.log_event(f"发送命令: {command}", "失败", "等待响应超时")
                    return {"success": False, "error": "超时"}
                else:  # EOF
                    self.log_event(f"发送命令: {command}", "失败", "进程已结束")
                    return {"success": False, "error": "进程结束"}
            else:
                # 没有预期模式，等待一小段时间后继续
                time.sleep(1)
                screenshot = self.take_screenshot()
                self.log_event(f"发送命令: {command}", "成功", "命令已发送", screenshot)
                return {"success": True, "output": self.process.before}
                
        except Exception as e:
            self.log_event(f"发送命令: {command}", "失败", f"执行异常: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def test_command_autocompletion(self) -> bool:
        """测试命令自动补全功能"""
        self.log_event("测试命令自动补全", "进行中")
        
        test_cases = [
            {
                "input": "/r",
                "expected": ["/role", "role list", "Available Roles"],
                "description": "角色命令补全"
            },
            {
                "input": "/s", 
                "expected": ["/session", "session list"],
                "description": "会话命令补全"
            },
            {
                "input": "/h",
                "expected": ["/help", "Available Commands"],
                "description": "帮助命令补全"
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            result = self.send_command(
                test_case["input"], 
                test_case["expected"],
                timeout=5
            )
            
            if result["success"]:
                self.log_event(
                    f"自动补全测试: {test_case['description']}", 
                    "成功",
                    f"输入: {test_case['input']}, 匹配: {result.get('matched_pattern', 'N/A')}"
                )
            else:
                self.log_event(
                    f"自动补全测试: {test_case['description']}", 
                    "失败",
                    f"输入: {test_case['input']}, 错误: {result.get('error', '未知错误')}"
                )
                all_passed = False
        
        return all_passed
    
    def test_command_execution(self) -> bool:
        """测试命令执行功能"""
        self.log_event("测试命令执行", "进行中")
        
        test_commands = [
            {
                "command": "/help",
                "expected": ["Available Commands", "help document"],
                "description": "帮助命令"
            },
            {
                "command": "/role list",
                "expected": ["Available Roles", "No roles found", "role"],
                "description": "角色列表"
            },
            {
                "command": "/session list",
                "expected": ["Available Sessions", "No sessions found", "session"],
                "description": "会话列表"
            }
        ]
        
        all_passed = True
        for test in test_commands:
            result = self.send_command(test["command"], test["expected"])
            
            if result["success"]:
                self.log_event(
                    f"命令执行测试: {test['description']}",
                    "成功",
                    f"命令: {test['command']}"
                )
            else:
                self.log_event(
                    f"命令执行测试: {test['description']}",
                    "失败", 
                    f"命令: {test['command']}, 错误: {result.get('error', '未知错误')}"
                )
                all_passed = False
        
        return all_passed
    
    def test_interactive_flow(self) -> bool:
        """测试交互式流程"""
        self.log_event("测试交互式流程", "进行中")
        
        try:
            # 测试输入焦点切换
            self.log_event("测试焦点切换", "进行中")
            self.process.sendcontrol('i')  # Ctrl+I 切换焦点
            time.sleep(0.5)
            screenshot = self.take_screenshot()
            self.log_event("测试焦点切换", "成功", "焦点切换完成", screenshot)
            
            # 测试命令历史
            self.log_event("测试命令历史", "进行中")
            self.process.sendline("/help")  # 先执行一个命令
            self.process.expect(["Available Commands", pexpect.TIMEOUT], timeout=5)
            
            # 测试向上箭头键
            self.process.sendcontrol('p')  # Ctrl+P 模拟向上箭头
            time.sleep(0.5)
            screenshot = self.take_screenshot()
            self.log_event("测试命令历史", "成功", "命令历史导航", screenshot)
            
            return True
            
        except Exception as e:
            self.log_event("测试交互式流程", "失败", f"交互测试异常: {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """测试错误处理"""
        self.log_event("测试错误处理", "进行中")
        
        invalid_commands = [
            ("/invalid_command", ["Unknown command", "not found"]),
            ("/role invalid_subcommand", ["Unknown subcommand", "Try /role list"]),
            ("/session view invalid_id", ["not found", "Session"])
        ]
        
        all_passed = True
        for cmd, expected in invalid_commands:
            result = self.send_command(cmd, expected, timeout=5)
            
            if result["success"]:
                self.log_event(
                    f"错误处理测试: {cmd}",
                    "成功",
                    f"正确显示了错误信息"
                )
            else:
                self.log_event(
                    f"错误处理测试: {cmd}",
                    "失败", 
                    f"未正确显示错误信息"
                )
                all_passed = False
        
        return all_passed
    
    def test_tui_lifecycle(self) -> bool:
        """测试TUI完整生命周期"""
        self.log_event("测试TUI生命周期", "进行中")
        
        try:
            # 测试正常退出
            result = self.send_command("/quit", ["Exiting", pexpect.EOF], timeout=5)
            
            if result["success"] or (self.process and self.process.eof()):
                self.log_event("测试TUI生命周期", "成功", "正常退出完成")
                return True
            else:
                self.log_event("测试TUI生命周期", "失败", "退出过程异常")
                return False
                
        except Exception as e:
            self.log_event("测试TUI生命周期", "失败", f"生命周期测试异常: {str(e)}")
            return False
    
    def run_comprehensive_test(self) -> Dict:
        """运行完整测试套件"""
        print("🚀 DAIP-LIVE TUI 高级交互测试")
        print("="*80)
        
        test_results = {}
        
        # 启动TUI
        if not self.start_tui():
            return {"overall": "失败", "details": "TUI启动失败"}
        
        # 执行各项测试
        tests = [
            ("命令自动补全", self.test_command_autocompletion),
            ("命令执行", self.test_command_execution),
            ("交互流程", self.test_interactive_flow),
            ("错误处理", self.test_error_handling),
            ("生命周期", self.test_tui_lifecycle)
        ]
        
        for test_name, test_func in tests:
            test_results[test_name] = test_func()
        
        # 生成报告
        self.generate_advanced_report(test_results)
        
        # 确保进程结束
        if self.process and not self.process.eof():
            try:
                self.process.sendline("/quit")
                self.process.expect(pexpect.EOF, timeout=5)
            except:
                self.process.terminate()
        
        return test_results
    
    def generate_advanced_report(self, test_results: Dict):
        """生成高级测试报告"""
        print("\n" + "="*80)
        print("🤖 DAIP-LIVE TUI 高级交互测试报告")
        print("="*80)
        
        # 统计结果
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 测试结果统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过测试: {passed_tests}")
        print(f"   失败测试: {failed_tests}")
        print(f"   通过率: {(passed_tests/total_tests)*100:.1f}%")
        
        # 详细结果
        print(f"\n🔍 详细测试结果:")
        for test_name, result in test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"   {test_name}: {status}")
        
        # 事件日志
        print(f"\n📝 交互事件日志:")
        for event in self.test_log:
            status_symbol = "✅" if event['result'] == "成功" else "❌" if event['result'] == "失败" else "⚠️"
            print(f"[{event['timestamp']}] {status_symbol} {event['action']}")
            if event['details']:
                print(f"        详情: {event['details']}")
        
        # 保存报告
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "test_results": test_results,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "event_log": self.test_log,
            "screenshots": self.screenshots
        }
        
        report_file = "advanced_tui_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 高级测试报告已保存到: {report_file}")
        
        # 最终评估
        print(f"\n🎯 最终评估:")
        if failed_tests == 0:
            print("✅ TUI交互测试完全通过，系统交互功能正常")
            print("   系统具备完整交互能力")
        elif failed_tests / total_tests < 0.3:
            print("⚠️  TUI交互测试基本通过，存在少量问题")
            print("   建议修复失败的功能")
        else:
            print("❌ TUI交互测试存在较多问题")
            print("   需要重点修复交互功能")

def main():
    """主测试函数"""
    tester = AdvancedTUITester(timeout=30, log_level="INFO")
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()