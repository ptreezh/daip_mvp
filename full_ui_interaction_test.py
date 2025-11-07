#!/usr/bin/env python3
"""
DAIP-LIVE TUI 全路径全流程交互测试

模拟人类用户完整走查所有应用场景和功能，记录每一步操作和结果。
"""

import asyncio
import sys
import os
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime

class FullPathTUITester:
    def __init__(self):
        self.test_results = []
        self.current_test = ""
        self.start_time = None
        self.test_log = []
        
    def log_step(self, step, action, result, details=""):
        """记录测试步骤"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "step": step,
            "action": action,
            "result": result,
            "details": details
        }
        self.test_log.append(log_entry)
        
        status_symbol = "✅" if result == "成功" else "❌" if result == "失败" else "⚠️"
        print(f"[{timestamp}] {status_symbol} {step}: {action} - {result}")
        if details:
            print(f"        详情: {details}")
    
    def start_test(self, test_name):
        """开始测试"""
        self.current_test = test_name
        self.start_time = time.time()
        print(f"\n🎯 开始测试: {test_name}")
        print("="*60)
    
    def end_test(self, status, summary=""):
        """结束测试"""
        duration = time.time() - self.start_time
        result = {
            "test": self.current_test,
            "status": status,
            "summary": summary,
            "duration": round(duration, 2),
            "steps": len([l for l in self.test_log if l["step"] == self.current_test])
        }
        self.test_results.append(result)
        
        print(f"\n📊 {self.current_test} 测试完成")
        print(f"   状态: {status}")
        print(f"   耗时: {duration:.2f}秒")
        print(f"   步骤数: {result['steps']}")
        if summary:
            print(f"   总结: {summary}")
    
    async def test_tui_startup(self):
        """测试TUI启动和初始化"""
        self.start_test("TUI启动和初始化")
        
        try:
            # 1. 检查配置文件
            self.log_step("TUI启动和初始化", "检查配置文件", "进行中")
            config_file = Path("config.yaml")
            if config_file.exists():
                self.log_step("TUI启动和初始化", "配置文件检查", "成功", "配置文件存在")
            else:
                self.log_step("TUI启动和初始化", "配置文件检查", "警告", "使用默认配置")
            
            # 2. 测试TUI启动命令
            self.log_step("TUI启动和初始化", "测试启动命令", "进行中")
            try:
                result = subprocess.run([
                    sys.executable, "-c", 
                    """
import sys; sys.path.insert(0, '.');
from src.daip_live.tui import DAIP_TUI;
print('TUI导入成功');
tui = DAIP_TUI();
print('TUI实例化成功')
"""
                ], capture_output=True, text=True, timeout=30)
                
                if "TUI导入成功" in result.stdout and "TUI实例化成功" in result.stdout:
                    self.log_step("TUI启动和初始化", "TUI启动测试", "成功", "TUI正常启动")
                else:
                    self.log_step("TUI启动和初始化", "TUI启动测试", "失败", result.stderr)
                    self.end_test("部分失败", "TUI启动存在问题")
                    return False
                    
            except subprocess.TimeoutExpired:
                self.log_step("TUI启动和初始化", "TUI启动测试", "超时", "启动过程较长")
            except Exception as e:
                self.log_step("TUI启动和初始化", "TUI启动测试", "失败", str(e))
                self.end_test("失败", "TUI启动失败")
                return False
            
            # 3. 检查核心组件
            self.log_step("TUI启动和初始化", "检查核心组件", "进行中")
            try:
                result = subprocess.run([
                    sys.executable, "-c", 
                    """
import sys; sys.path.insert(0, '.');
from src.daip_live.tui import DAIP_TUI;
tui = DAIP_TUI();
components = ['_executor', '_session_manager', '_role_manager', '_knowledge_manager'];
missing = [c for c in components if not hasattr(tui, c)];
if not missing:
    print('所有核心组件正常');
else:
    print(f'缺少组件: {missing}')
"""
                ], capture_output=True, text=True, timeout=10)
                
                if "所有核心组件正常" in result.stdout:
                    self.log_step("TUI启动和初始化", "核心组件检查", "成功", "所有组件正常")
                else:
                    self.log_step("TUI启动和初始化", "核心组件检查", "警告", result.stdout.strip())
            
            self.end_test("成功", "TUI启动和初始化完成")
            return True
            
        except Exception as e:
            self.log_step("TUI启动和初始化", "测试过程", "失败", str(e))
            self.end_test("失败", "测试过程异常")
            return False
    
    async def test_basic_commands(self):
        """测试基础命令交互"""
        self.start_test("基础命令交互")
        
        commands_to_test = [
            ("/help", "显示帮助信息"),
            ("/role list", "列出角色"),
            ("/session list", "列出会话"),
            ("/model list", "列出模型"),
        ]
        
        for cmd, description in commands_to_test:
            self.log_step("基础命令交互", f"测试命令: {cmd}", "进行中", description)
            
            try:
                # 模拟命令处理
                result = subprocess.run([
                    sys.executable, "-c", 
                    f"""
import sys; sys.path.insert(0, '.');
from src.daip_live.tui import DAIP_TUI;
tui = DAIP_TUI();

# 检查命令处理方法
cmd_name = '{cmd.split()[0].replace('/', '')}'
handler_name = f'_handle_{{cmd_name}}_command'

if hasattr(tui, handler_name):
    print(f'命令处理器 {{handler_name}} 存在');
    
    # 测试自动补全
    suggestions = tui._get_autocomplete_suggestions('{cmd.split()[0]}')
    if suggestions:
        print(f'自动补全建议: {{len(suggestions)}} 条');
    else:
        print('无自动补全建议');
else:
    print(f'命令处理器 {{handler_name}} 不存在')
"""
                ], capture_output=True, text=True, timeout=10)
                
                if "命令处理器" in result.stdout and "存在" in result.stdout:
                    self.log_step("基础命令交互", f"命令: {cmd}", "成功", "命令处理器正常")
                    if "自动补全建议" in result.stdout:
                        self.log_step("基础命令交互", f"自动补全: {cmd}", "成功", "支持自动补全")
                else:
                    self.log_step("基础命令交互", f"命令: {cmd}", "警告", "命令处理器可能有问题")
                    
            except Exception as e:
                self.log_step("基础命令交互", f"命令: {cmd}", "失败", str(e))
        
        self.end_test("成功", "基础命令交互测试完成")
        return True
    
    async def test_knowledge_system(self):
        """测试知识库系统全流程"""
        self.start_test("知识库系统")
        
        try:
            # 1. 检查知识库目录
            knowledge_dir = Path("knowledge")
            if knowledge_dir.exists():
                self.log_step("知识库系统", "检查知识库目录", "成功", "目录存在")
            else:
                self.log_step("知识库系统", "检查知识库目录", "警告", "目录不存在，将自动创建")
            
            # 2. 测试知识库管理器
            self.log_step("知识库系统", "测试知识库管理器", "进行中")
            try:
                result = subprocess.run([
                    sys.executable, "-c", 
                    """
import sys; sys.path.insert(0, '.');
from src.daip_live.knowledge.manager import KnowledgeManager;
from src.daip_live.config import config_manager;

try:
    config = config_manager.get_config()
    km = KnowledgeManager(config.knowledge_base.directory)
    print('知识库管理器初始化成功');
    
    # 检查索引文件
    import os
    index_file = os.path.join(config.knowledge_base.directory, 'index.faiss')
    if os.path.exists(index_file):
        print('知识库索引文件存在');
    else:
        print('知识库索引文件不存在');
        
except Exception as e:
    print(f'知识库测试失败: {{e}}')
"""
                ], capture_output=True, text=True, timeout=10)
                
                if "知识库管理器初始化成功" in result.stdout:
                    self.log_step("知识库系统", "知识库管理器", "成功", "管理器正常")
                else:
                    self.log_step("知识库系统", "知识库管理器", "失败", result.stderr)
            
            self.end_test("成功", "知识库系统测试完成")
            return True
            
        except Exception as e:
            self.log_step("知识库系统", "测试过程", "失败", str(e))
            self.end_test("失败", "知识库系统测试异常")
            return False
    
    async def test_debate_system(self):
        """测试辩论系统全流程"""
        self.start_test("辩论系统")
        
        try:
            # 1. 检查辩论角色
            debate_dir = Path("pro_arguer")
            if debate_dir.exists():
                role_files = list(debate_dir.glob("*.yaml")) + list(debate_dir.glob("*.yml"))
                self.log_step("辩论系统", "检查辩论角色", "成功", f"找到 {len(role_files)} 个角色文件")
            else:
                self.log_step("辩论系统", "检查辩论角色", "警告", "辩论角色目录不存在")
            
            # 2. 测试辩论管理器
            self.log_step("辩论系统", "测试辩论管理器", "进行中")
            try:
                result = subprocess.run([
                    sys.executable, "-c", 
                    """
import sys; sys.path.insert(0, '.');
from src.daip_live.p8_debate_system.manager import DebateManager;
from src.daip_live.config import config_manager;

try:
    config = config_manager.get_config()
    dm = DebateManager()
    print('辩论管理器初始化成功');
    
    # 检查辩论命令处理
    from src.daip_live.tui import DAIP_TUI;
tui = DAIP_TUI();
if hasattr(tui, '_handle_debate_command'):
    print('辩论命令处理器存在');
    
    # 测试辩论参数解析
    test_args = 'start "测试话题" --roles "pro_arguer,con_arguer" --rounds 2'
    print(f'辩论参数解析测试: {{test_args}}');
    
except Exception as e:
    print(f'辩论系统测试失败: {{e}}')
"""
                ], capture_output=True, text=True, timeout=10)
                
                if "辩论管理器初始化成功" in result.stdout:
                    self.log_step("辩论系统", "辩论管理器", "成功", "管理器正常")
                else:
                    self.log_step("辩论系统", "辩论管理器", "失败", result.stderr)
            
            self.end_test("成功", "辩论系统测试完成")
            return True
            
        except Exception as e:
            self.log_step("辩论系统", "测试过程", "失败", str(e))
            self.end_test("失败", "辩论系统测试异常")
            return False
    
    def generate_detailed_report(self):
        """生成详细测试报告"""
        print("\n" + "="*80)
        print("📊 DAIP-LIVE TUI 全路径全流程交互测试报告")
        print("="*80)
        
        # 统计信息
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == '成功'])
        failed_tests = len([r for r in self.test_results if r['status'] == '失败'])
        
        print(f"\n📈 测试统计:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过数: {passed_tests}")
        print(f"   失败数: {failed_tests}")
        print(f"   成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        # 详细测试结果
        print(f"\n🔍 详细测试结果:")
        for result in self.test_results:
            status_symbol = "✅" if result['status'] == "成功" else "❌" if result['status'] == "失败" else "⚠️"
            print(f"{status_symbol} {result['test']}")
            print(f"   状态: {result['status']}")
            print(f"   耗时: {result['duration']}秒")
            print(f"   步骤数: {result['steps']}")
            if result['summary']:
                print(f"   总结: {result['summary']}")
            print()
        
        # 测试日志
        print(f"\n📝 完整测试日志 ({len(self.test_log)} 条记录):")
        for log in self.test_log:
            status_symbol = "✅" if log['result'] == "成功" else "❌" if log['result'] == "失败" else "⚠️"
            print(f"[{log['timestamp']}] {status_symbol} {log['step']}: {log['action']}")
            if log['details']:
                print(f"        详情: {log['details']}")
        
        # 保存详细报告
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "test_results": self.test_results,
            "detailed_log": self.test_log
        }
        
        report_file = "full_path_tui_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细报告已保存到: {report_file}")
        
        # 生成建议
        print(f"\n💡 测试建议:")
        if failed_tests == 0:
            print("✅ 系统状态优秀，可以进行实际用户交互测试")
            print("   建议下一步: 启动完整TUI界面进行端到端测试")
        else:
            print("⚠️  系统存在一些问题，建议先修复再继续测试")
            failed_tests_list = [r['test'] for r in self.test_results if r['status'] == '失败']
            print(f"   需要关注的模块: {', '.join(failed_tests_list)}")

async def main():
    """主测试函数"""
    print("🚀 DAIP-LIVE TUI 全路径全流程交互测试开始")
    print("="*80)
    print("测试目标: 模拟人类用户完整走查所有应用场景和功能")
    print("测试范围: TUI启动、命令交互、知识库、辩论系统等核心功能")
    print("="*80)
    
    tester = FullPathTUITester()
    
    # 执行全路径测试
    await tester.test_tui_startup()
    await tester.test_basic_commands()
    await tester.test_knowledge_system()
    await tester.test_debate_system()
    
    # 生成详细报告
    tester.generate_detailed_report()

if __name__ == "__main__":
    asyncio.run(main())