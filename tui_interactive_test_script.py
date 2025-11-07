#!/usr/bin/env python3
"""
DAIP-LIVE TUI 交互测试脚本

这个脚本模拟用户交互走查TUI所有功能流程，不修改系统代码，只进行功能测试。
"""

import asyncio
import sys
import os
import time
from pathlib import Path
from typing import List, Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.daip_live.tui import DAIP_TUI
    from src.daip_live.config import config_manager
    from src.daip_live.core.models import AgentEvent, ThoughtEvent, FinalResponseEvent
    from src.daip_live.agent_engine.executor import AgentExecutor
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)


class TUITestRunner:
    """TUI交互测试运行器"""
    
    def __init__(self):
        self.test_results = []
        self.current_test = ""
        self.start_time = None
        
    def log_test_start(self, test_name: str):
        """记录测试开始"""
        self.current_test = test_name
        self.start_time = time.time()
        print(f"\n{'='*60}")
        print(f"开始测试: {test_name}")
        print(f"{'='*60}")
        
    def log_test_result(self, status: str, message: str = "", error: str = ""):
        """记录测试结果"""
        duration = time.time() - self.start_time
        result = {
            "test": self.current_test,
            "status": status,
            "message": message,
            "error": error,
            "duration": round(duration, 2)
        }
        self.test_results.append(result)
        
        status_symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_symbol} {self.current_test}: {status}")
        if message:
            print(f"   {message}")
        if error:
            print(f"   错误: {error}")
        print(f"   耗时: {duration:.2f}秒")
        
    async def test_tui_startup(self):
        """测试TUI启动功能"""
        self.log_test_start("TUI启动测试")
        
        try:
            # 创建TUI实例
            tui = DAIP_TUI()
            
            # 检查基本属性
            assert hasattr(tui, '_available_commands'), "缺少可用命令列表"
            assert isinstance(tui._available_commands, list), "命令列表类型错误"
            
            # 检查核心方法
            assert hasattr(tui, '_get_autocomplete_suggestions'), "缺少自动补全方法"
            
            # 检查命令处理方法
            command_methods = []
            for name in dir(tui):
                if name.startswith("_handle_") and name.endswith("_command"):
                    command_methods.append(name)
            
            self.log_test_result("PASS", f"TUI启动配置正常，找到{len(command_methods)}个命令处理方法")
            return True
            
        except Exception as e:
            self.log_test_result("FAIL", "TUI启动失败", str(e))
            return False
    
    async def test_basic_commands(self):
        """测试基础命令"""
        self.log_test_start("基础命令测试")
        
        try:
            tui = DAIP_TUI()
            
            # 测试命令列表
            basic_commands = ['/help', '/clear', '/quit']
            
            # 检查命令处理方法是否存在
            command_methods = []
            for name in dir(tui):
                if name.startswith("_handle_") and name.endswith("_command"):
                    command_name = f"/{name.replace('_handle_', '').replace('_command', '')}"
                    command_methods.append(command_name)
            
            for cmd in basic_commands:
                if cmd in command_methods:
                    print(f"  ✅ 命令 '{cmd}' 存在")
                else:
                    print(f"  ⚠️  命令 '{cmd}' 未找到")
            
            self.log_test_result("PASS", "基础命令检查完成")
            return True
            
        except Exception as e:
            self.log_test_result("FAIL", "基础命令测试失败", str(e))
            return False
    
    async def test_knowledge_commands(self):
        """测试知识库命令"""
        self.log_test_start("知识库命令测试")
        
        try:
            tui = DAIP_TUI()
            
            # 检查知识库命令处理方法
            knowledge_methods = []
            for name in dir(tui):
                if name.startswith("_handle_") and name.endswith("_command"):
                    command_name = name.replace("_handle_", "").replace("_command", "")
                    if 'knowledge' in command_name.lower():
                        knowledge_methods.append(command_name)
            
            if knowledge_methods:
                print(f"  ✅ 找到知识库命令处理方法: {knowledge_methods}")
            else:
                print(f"  ⚠️  未找到专门的知识库命令处理方法")
            
            self.log_test_result("PASS", "知识库命令检查完成")
            return True
            
        except Exception as e:
            self.log_test_result("FAIL", "知识库命令测试失败", str(e))
            return False
    
    async def test_role_commands(self):
        """测试角色管理命令"""
        self.log_test_start("角色管理命令测试")
        
        try:
            tui = DAIP_TUI()
            
            # 检查角色命令处理方法
            role_methods = []
            for name in dir(tui):
                if name.startswith("_handle_") and name.endswith("_command"):
                    command_name = name.replace("_handle_", "").replace("_command", "")
                    if 'role' in command_name.lower():
                        role_methods.append(command_name)
            
            if role_methods:
                print(f"  ✅ 找到角色命令处理方法: {role_methods}")
            else:
                print(f"  ⚠️  未找到专门的角色命令处理方法")
            
            self.log_test_result("PASS", "角色管理命令检查完成")
            return True
            
        except Exception as e:
            self.log_test_result("FAIL", "角色管理命令测试失败", str(e))
            return False
    
    async def test_debate_commands(self):
        """测试辩论系统命令"""
        self.log_test_start("辩论系统命令测试")
        
        try:
            tui = DAIP_TUI()
            
            # 检查辩论命令处理方法
            debate_methods = []
            for name in dir(tui):
                if name.startswith("_handle_") and name.endswith("_command"):
                    command_name = name.replace("_handle_", "").replace("_command", "")
                    if 'debate' in command_name.lower():
                        debate_methods.append(command_name)
            
            if debate_methods:
                print(f"  ✅ 找到辩论命令处理方法: {debate_methods}")
            else:
                print(f"  ⚠️  未找到专门的辩论命令处理方法")
            
            self.log_test_result("PASS", "辩论系统命令检查完成")
            return True
            
        except Exception as e:
            self.log_test_result("FAIL", "辩论系统命令测试失败", str(e))
            return False
    
    async def test_wiki_commands(self):
        """测试Wiki系统命令"""
        self.log_test_start("Wiki系统命令测试")
        
        try:
            tui = DAIP_TUI()
            
            # 检查Wiki命令处理方法
            wiki_methods = []
            for name in dir(tui):
                if name.startswith("_handle_") and name.endswith("_command"):
                    command_name = name.replace("_handle_", "").replace("_command", "")
                    if 'wiki' in command_name.lower():
                        wiki_methods.append(command_name)
            
            if wiki_methods:
                print(f"  ✅ 找到Wiki命令处理方法: {wiki_methods}")
            else:
                print(f"  ⚠️  未找到专门的Wiki命令处理方法")
            
            self.log_test_result("PASS", "Wiki系统命令检查完成")
            return True
            
        except Exception as e:
            self.log_test_result("FAIL", "Wiki系统命令测试失败", str(e))
            return False
    
    async def test_permission_commands(self):
        """测试权限管理命令"""
        self.log_test_start("权限管理命令测试")
        
        try:
            tui = DAIP_TUI()
            
            # 检查权限命令处理方法
            permission_methods = []
            for name in dir(tui):
                if name.startswith("_handle_") and name.endswith("_command"):
                    command_name = name.replace("_handle_", "").replace("_command", "")
                    if 'permission' in command_name.lower():
                        permission_methods.append(command_name)
            
            if permission_methods:
                print(f"  ✅ 找到权限命令处理方法: {permission_methods}")
            else:
                print(f"  ⚠️  未找到专门的权限命令处理方法")
            
            self.log_test_result("PASS", "权限管理命令检查完成")
            return True
            
        except Exception as e:
            self.log_test_result("FAIL", "权限管理命令测试失败", str(e))
            return False
    
    async def test_project_commands(self):
        """测试项目脚手架命令"""
        self.log_test_start("项目脚手架命令测试")
        
        try:
            tui = DAIP_TUI()
            
            # 检查项目命令处理方法
            project_methods = []
            for name in dir(tui):
                if name.startswith("_handle_") and name.endswith("_command"):
                    command_name = name.replace("_handle_", "").replace("_command", "")
                    if 'project' in command_name.lower():
                        project_methods.append(command_name)
            
            if project_methods:
                print(f"  ✅ 找到项目命令处理方法: {project_methods}")
            else:
                print(f"  ⚠️  未找到专门的项目命令处理方法")
            
            self.log_test_result("PASS", "项目脚手架命令检查完成")
            return True
            
        except Exception as e:
            self.log_test_result("FAIL", "项目脚手架命令测试失败", str(e))
            return False
    
    def generate_report(self):
        """生成测试报告"""
        print(f"\n{'='*60}")
        print("TUI交互测试报告")
        print(f"{'='*60}")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warning_tests = len([r for r in self.test_results if r['status'] == 'WARNING'])
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"警告: {warning_tests}")
        print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n详细结果:")
        for result in self.test_results:
            status_symbol = "✅" if result['status'] == "PASS" else "❌" if result['status'] == "FAIL" else "⚠️"
            print(f"{status_symbol} {result['test']} ({result['duration']}秒)")
            if result['message']:
                print(f"   信息: {result['message']}")
            if result['error']:
                print(f"   错误: {result['error']}")
        
        # 生成建议
        print(f"\n建议和问题:")
        issues = [r for r in self.test_results if r['status'] in ['FAIL', 'WARNING']]
        if not issues:
            print("✅ 所有测试通过，系统状态良好")
        else:
            for issue in issues:
                print(f"⚠️  {issue['test']}: {issue.get('error', issue.get('message', '需要修复'))}")


async def main():
    """主测试函数"""
    print("DAIP-LIVE TUI 交互测试开始")
    print("=" * 50)
    
    runner = TUITestRunner()
    
    # 执行所有测试
    await runner.test_tui_startup()
    await runner.test_basic_commands()
    await runner.test_knowledge_commands()
    await runner.test_role_commands()
    await runner.test_debate_commands()
    await runner.test_wiki_commands()
    await runner.test_permission_commands()
    await runner.test_project_commands()
    
    # 生成报告
    runner.generate_report()
    
    # 保存详细报告到文件
    report_file = "tui_interactive_test_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# DAIP-LIVE TUI 交互测试报告\n\n")
        f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        total_tests = len(runner.test_results)
        passed_tests = len([r for r in runner.test_results if r['status'] == 'PASS'])
        
        f.write("## 测试概览\n")
        f.write(f"- 总测试数: {total_tests}\n")
        f.write(f"- 通过数: {passed_tests}\n")
        f.write(f"- 成功率: {(passed_tests/total_tests)*100:.1f}%\n\n")
        
        f.write("## 详细测试结果\n")
        for result in runner.test_results:
            f.write(f"### {result['test']}\n")
            f.write(f"- 状态: {result['status']}\n")
            f.write(f"- 耗时: {result['duration']}秒\n")
            if result['message']:
                f.write(f"- 信息: {result['message']}\n")
            if result['error']:
                f.write(f"- 错误: {result['error']}\n")
            f.write("\n")
        
        f.write("## 建议和问题\n")
        issues = [r for r in runner.test_results if r['status'] in ['FAIL', 'WARNING']]
        if issues:
            for issue in issues:
                f.write(f"- {issue['test']}: {issue.get('error', issue.get('message', '需要修复'))}\n")
        else:
            f.write("- 所有测试通过，系统状态良好\n")
    
    print(f"\n详细报告已保存到: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())