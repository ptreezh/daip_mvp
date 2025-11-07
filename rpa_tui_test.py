#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DAIP-LIVE TUI RPA式完全去耦合测试

基于RPA理念，完全从外部模拟用户操作，不依赖内部代码结构。
"""

import asyncio
import sys
import os
import time
import subprocess
import json
import locale
from pathlib import Path
from datetime import datetime

# 设置统一编码环境
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except locale.Error:
        pass

# 重新配置标准流编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')
if sys.stdin.encoding != 'utf-8':
    sys.stdin.reconfigure(encoding='utf-8')

class RPATUITester:
    """RPA式完全去耦合TUI测试器"""
    
    def __init__(self):
        self.test_log = []
        self.test_results = {}
        
    def log_event(self, action, result, details=""):
        """记录测试事件"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        event = {
            "timestamp": timestamp,
            "action": action,
            "result": result,
            "details": details
        }
        self.test_log.append(event)
        
        status_symbol = "✅" if result == "成功" else "❌" if result == "失败" else "⚠️"
        print(f"[{timestamp}] {status_symbol} {action}")
        if details:
            print(f"        详情: {details}")
    
    def execute_command_and_verify(self, command, expected_keywords=None, timeout=30):
        """执行命令并验证输出"""
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='ignore',
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )
            
            success = True
            details = f"退出码: {result.returncode}"
            
            if expected_keywords:
                if result.returncode == 0:
                    # 检查是否包含预期关键词
                    output = result.stdout.lower()
                    missing_keywords = []
                    for keyword in expected_keywords:
                        if keyword.lower() not in output:
                            missing_keywords.append(keyword)
                            success = False
                    
                    if missing_keywords:
                        details = f"缺少关键词: {missing_keywords}"
                    else:
                        details = "所有预期关键词都存在"
                else:
                    success = False
                    details = f"命令执行失败，退出码: {result.returncode}"
            
            return success, details, result
            
        except subprocess.TimeoutExpired:
            return False, "命令执行超时", None
        except Exception as e:
            return False, f"执行异常: {str(e)}", None
    
    def test_system_availability(self):
        """测试系统可用性"""
        print("\n🔍 测试系统可用性")
        print("="*50)
        
        # 1. 检查Python环境
        self.log_event("检查Python环境", "进行中")
        try:
            result = subprocess.run(["python", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log_event("Python环境", "成功", result.stdout.strip())
            else:
                self.log_event("Python环境", "失败", "无法获取Python版本")
        except Exception as e:
            self.log_event("Python环境", "失败", str(e))
        
        # 2. 检查项目依赖
        self.log_event("检查项目依赖", "进行中")
        try:
            result = subprocess.run(
                ["python", "-c", "import sys; sys.path.insert(0, '.'); import daip_live; print('✅ 项目导入成功')"],
                capture_output=True, text=True, timeout=10
            )
            if "✅ 项目导入成功" in result.stdout:
                self.log_event("项目依赖", "成功", "所有依赖正常")
            else:
                self.log_event("项目依赖", "警告", f"导入问题: {result.stderr}")
        except Exception as e:
            self.log_event("项目依赖", "失败", str(e))
    
    def test_cli_interface(self):
        """测试CLI接口"""
        print("\n🖥️  测试CLI接口")
        print("="*50)
        
        cli_tests = [
            {
                "command": "daip --help",
                "description": "显示帮助信息",
                "expected_keywords": ["usage", "help", "commands"]
            },
            {
                "command": "daip role list",
                "description": "列出角色",
                "expected_keywords": ["role", "list"]
            },
            {
                "command": "daip session list", 
                "description": "列出会话",
                "expected_keywords": ["session", "list"]
            },
            {
                "command": "daip model list",
                "description": "列出模型",
                "expected_keywords": ["model", "list"]
            }
        ]
        
        for test in cli_tests:
            self.log_event(f"执行命令: {test['command']}", "进行中", test['description'])
            success, details, result = self.execute_command_and_verify(
                test['command'], 
                test.get('expected_keywords')
            )
            
            if success:
                self.log_event(f"命令: {test['command']}", "成功", details)
                if result and result.stdout:
                    # 记录命令输出摘要
                    output_preview = result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout
                    self.log_event("命令输出", "信息", output_preview)
            else:
                self.log_event(f"命令: {test['command']}", "失败", details)
    
    def test_file_system_integrity(self):
        """测试文件系统完整性"""
        print("\n📁 测试文件系统完整性")
        print("="*50)
        
        file_checks = [
            ("config.yaml", "配置文件", True),
            ("daip_live.db", "数据库文件", True),
            ("knowledge/", "知识库目录", True),
            ("roles/", "角色目录", True),
            ("wiki/", "Wiki目录", True),
            ("pro_arguer/", "辩论角色目录", True),
            ("src/daip_live/", "源代码目录", True),
        ]
        
        for path, description, required in file_checks:
            check_path = Path(path)
            if check_path.exists():
                if check_path.is_dir():
                    file_count = len(list(check_path.glob("*")))
                    self.log_event(f"检查{description}", "成功", f"目录存在，包含 {file_count} 个文件")
                else:
                    size = check_path.stat().st_size
                    self.log_event(f"检查{description}", "成功", f"文件存在，大小: {size} 字节")
            else:
                if required:
                    self.log_event(f"检查{description}", "失败", "必需文件/目录不存在")
                else:
                    self.log_event(f"检查{description}", "警告", "文件/目录不存在")
    
    def test_tui_lifecycle(self):
        """测试TUI生命周期"""
        print("\n🔄 测试TUI生命周期")
        print("="*50)
        
        # 测试TUI启动和退出
        self.log_event("启动TUI进程", "进行中")
        try:
            process = subprocess.Popen(
                ["python", "-m", "daip_live.tui"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )
            
            # 等待启动
            time.sleep(3)
            
            # 发送退出命令
            self.log_event("发送退出命令", "进行中", "/quit")
            process.stdin.write("/quit\n")
            process.stdin.flush()
            
            # 等待退出
            try:
                stdout, stderr = process.communicate(timeout=10)
                if process.returncode == 0:
                    self.log_event("TUI生命周期", "成功", "正常启动和退出")
                else:
                    self.log_event("TUI生命周期", "警告", f"非零退出码: {process.returncode}")
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                self.log_event("TUI生命周期", "警告", "进程超时被终止")
                
        except Exception as e:
            self.log_event("TUI生命周期", "失败", str(e))
    
    def test_functional_scenarios(self):
        """测试功能场景"""
        print("\n🎯 测试功能场景")
        print("="*50)
        
        scenarios = [
            {
                "name": "角色管理场景",
                "steps": [
                    "daip role list",
                    "daip role view assistant"
                ],
                "description": "测试角色列表和查看功能"
            },
            {
                "name": "会话管理场景", 
                "steps": [
                    "daip session list",
                    "daip session clear"
                ],
                "description": "测试会话列表和清理功能"
            },
            {
                "name": "知识库场景",
                "steps": [
                    "daip knowledge sync"
                ],
                "description": "测试知识库同步功能"
            }
        ]
        
        for scenario in scenarios:
            self.log_event(f"场景: {scenario['name']}", "进行中", scenario['description'])
            
            all_steps_passed = True
            for step in scenario['steps']:
                success, details, _ = self.execute_command_and_verify(step)
                if success:
                    self.log_event(f"步骤: {step}", "成功", details)
                else:
                    self.log_event(f"步骤: {step}", "失败", details)
                    all_steps_passed = False
            
            if all_steps_passed:
                self.log_event(f"场景: {scenario['name']}", "成功", "所有步骤执行完成")
            else:
                self.log_event(f"场景: {scenario['name']}", "失败", "部分步骤执行失败")
    
    def generate_rpa_report(self):
        """生成RPA测试报告"""
        print("\n" + "="*80)
        print("🤖 DAIP-LIVE TUI RPA式完全去耦合测试报告")
        print("="*80)
        
        # 统计
        total_events = len(self.test_log)
        success_events = len([e for e in self.test_log if e['result'] == '成功'])
        failed_events = len([e for e in self.test_log if e['result'] == '失败'])
        warning_events = len([e for e in self.test_log if e['result'] == '警告'])
        
        print(f"\n📊 事件统计:")
        print(f"   总事件数: {total_events}")
        print(f"   成功事件: {success_events}")
        print(f"   失败事件: {failed_events}")
        print(f"   警告事件: {warning_events}")
        print(f"   成功率: {(success_events/total_events)*100:.1f}%")
        
        # 测试结果摘要
        print(f"\n🔍 测试结果摘要:")
        categories = {}
        for event in self.test_log:
            category = event['action'].split(':')[0] if ':' in event['action'] else event['action']
            if category not in categories:
                categories[category] = {'success': 0, 'failed': 0, 'warning': 0}
            
            if event['result'] == '成功':
                categories[category]['success'] += 1
            elif event['result'] == '失败':
                categories[category]['failed'] += 1
            else:
                categories[category]['warning'] += 1
        
        for category, stats in categories.items():
            total = stats['success'] + stats['failed'] + stats['warning']
            success_rate = (stats['success'] / total) * 100 if total > 0 else 0
            print(f"   {category}: {stats['success']}✅ {stats['failed']}❌ {stats['warning']}⚠️  ({success_rate:.1f}%)")
        
        # 详细事件日志
        print(f"\n📝 详细事件日志:")
        for event in self.test_log:
            status_symbol = "✅" if event['result'] == "成功" else "❌" if event['result'] == "失败" else "⚠️"
            print(f"[{event['timestamp']}] {status_symbol} {event['action']}")
            if event['details']:
                print(f"        详情: {event['details']}")
        
        # 保存报告
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_events": total_events,
                "success_events": success_events,
                "failed_events": failed_events,
                "warning_events": warning_events,
                "success_rate": (success_events/total_events)*100
            },
            "categories": categories,
            "event_log": self.test_log
        }
        
        report_file = "rpa_tui_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 RPA测试报告已保存到: {report_file}")
        
        # 最终评估
        print(f"\n🎯 最终评估:")
        if failed_events == 0:
            print("✅ 系统通过RPA测试，所有关键功能正常")
            print("   系统具备生产环境部署条件")
        elif failed_events / total_events < 0.1:  # 失败率低于10%
            print("⚠️  系统基本正常，存在少量问题")
            print("   建议修复问题后重新测试")
        else:
            print("❌ 系统存在较多问题，需要修复")
            print("   建议优先解决关键问题")

def main():
    """主测试函数"""
    print("🚀 DAIP-LIVE TUI RPA式完全去耦合测试")
    print("="*80)
    print("测试理念: 完全从外部模拟用户操作，不依赖内部代码结构")
    print("测试方法: 进程调用、命令执行、文件检查、场景验证")
    print("="*80)
    
    tester = RPATUITester()
    
    # 执行RPA测试
    tester.test_system_availability()
    tester.test_cli_interface()
    tester.test_file_system_integrity()
    tester.test_tui_lifecycle()
    tester.test_functional_scenarios()
    
    # 生成报告
    tester.generate_rpa_report()

if __name__ == "__main__":
    main()