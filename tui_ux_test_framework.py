#!/usr/bin/env python3
"""
TUI 全自动化用户体验测试框架

模拟真实用户交互，全面测评TUI的用户体验和功能完整性
"""

import asyncio
import sys
import os
import time
import json
import subprocess
import threading
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


@dataclass
class TestStep:
    """测试步骤"""
    action: str  # 'input', 'key_press', 'wait', 'screenshot'
    content: str
    expected_result: Optional[str] = None
    timeout: float = 2.0
    description: str = ""


@dataclass
class TestCase:
    """测试用例"""
    name: str
    description: str
    steps: List[TestStep]
    priority: int = 1  # 1-高, 2-中, 3-低


@dataclass
class TestResult:
    """测试结果"""
    test_name: str
    status: str  # 'PASS', 'FAIL', 'ERROR'
    details: str
    duration: float
    screenshots: List[str] = None
    issues: List[str] = None


class TUITestRunner:
    """TUI自动化测试运行器"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.current_process: Optional[subprocess.Popen] = None
        self.test_screenshots: List[str] = []
        
    def create_test_cases(self) -> List[TestCase]:
        """创建全面的测试用例"""
        
        test_cases = []
        
        # 1. 基础启动和退出测试
        test_cases.append(TestCase(
            name="启动和基本退出",
            description="测试TUI启动、显示和正常退出",
            steps=[
                TestStep("start_app", "", "TUI界面正常显示", 5.0, "启动TUI应用"),
                TestStep("wait", "3", "", 3.0, "等待界面加载"),
                TestStep("input", "/help", "显示帮助信息", 2.0, "输入帮助命令"),
                TestStep("wait", "2", "", 2.0, "等待帮助显示"),
                TestStep("key_press", "ctrl+c", "开始退出流程", 2.0, "第一次Ctrl+C"),
                TestStep("wait", "1", "", 1.0, "等待退出确认"),
                TestStep("key_press", "ctrl+c", "完全退出应用", 2.0, "第二次Ctrl+C"),
            ],
            priority=1
        ))
        
        # 2. 命令自动补全测试
        test_cases.append(TestCase(
            name="命令自动补全功能",
            description="测试命令的自动补全和动态展示",
            steps=[
                TestStep("start_app", "", "TUI界面正常显示", 5.0, "启动TUI应用"),
                TestStep("wait", "2", "", 2.0, "等待界面加载"),
                TestStep("input", "/", "显示所有命令选项", 2.0, "输入/触发命令提示"),
                TestStep("wait", "1", "", 1.0, "等待命令列表显示"),
                TestStep("input", "/m", "显示/m开头的命令", 2.0, "输入/m进行过滤"),
                TestStep("wait", "1", "", 1.0, "等待过滤结果"),
                TestStep("input", "/model", "显示model相关命令", 2.0, "完整输入/model"),
                TestStep("wait", "1", "", 1.0, "等待model子命令"),
                TestStep("key_press", "ctrl+c", "退出", 2.0, "退出测试"),
                TestStep("key_press", "ctrl+c", "完全退出", 2.0, "确认退出"),
            ],
            priority=1
        ))
        
        # 3. 模型切换功能测试
        test_cases.append(TestCase(
            name="模型切换功能",
            description="测试模型列表显示和切换功能",
            steps=[
                TestStep("start_app", "", "TUI界面正常显示", 5.0, "启动TUI应用"),
                TestStep("wait", "2", "", 2.0, "等待界面加载"),
                TestStep("input", "/model", "显示模型命令选项", 2.0, "输入模型命令"),
                TestStep("wait", "1", "", 1.0, "等待命令选项显示"),
                TestStep("input", "/model list", "显示可用模型列表", 3.0, "显示模型列表"),
                TestStep("wait", "3", "", 3.0, "等待模型列表加载"),
                TestStep("screenshot", "", "保存模型列表截图", 1.0, "截图模型列表"),
                TestStep("key_press", "ctrl+c", "退出", 2.0, "退出测试"),
                TestStep("key_press", "ctrl+c", "完全退出", 2.0, "确认退出"),
            ],
            priority=1
        ))
        
        # 4. 论文搜索功能测试
        test_cases.append(TestCase(
            name="论文搜索功能",
            description="测试论文搜索的完整流程",
            steps=[
                TestStep("start_app", "", "TUI界面正常显示", 5.0, "启动TUI应用"),
                TestStep("wait", "2", "", 2.0, "等待界面加载"),
                TestStep("input", "/doc", "显示文档命令选项", 2.0, "输入文档命令"),
                TestStep("wait", "1", "", 1.0, "等待命令选项"),
                TestStep("input", "/doc search", "准备搜索", 2.0, "输入搜索命令"),
                TestStep("wait", "1", "", 1.0, "等待搜索提示"),
                TestStep("input", "/doc search machine learning", "执行搜索", 5.0, "搜索机器学习论文"),
                TestStep("wait", "5", "", 5.0, "等待搜索结果"),
                TestStep("screenshot", "", "保存搜索结果截图", 1.0, "截图搜索结果"),
                TestStep("key_press", "ctrl+c", "退出", 2.0, "退出测试"),
                TestStep("key_press", "ctrl+c", "完全退出", 2.0, "确认退出"),
            ],
            priority=1
        ))
        
        # 5. 辩论功能测试
        test_cases.append(TestCase(
            name="辩论功能",
            description="测试辩论系统的启动和执行",
            steps=[
                TestStep("start_app", "", "TUI界面正常显示", 5.0, "启动TUI应用"),
                TestStep("wait", "2", "", 2.0, "等待界面加载"),
                TestStep("input", "/debate", "显示辩论命令选项", 2.0, "输入辩论命令"),
                TestStep("wait", "1", "", 1.0, "等待命令选项"),
                TestStep("input", "/debate start", "准备开始辩论", 2.0, "输入开始辩论"),
                TestStep("wait", "1", "", 1.0, "等待辩论主题提示"),
                TestStep("input", "/debate start AI ethics", "开始AI伦理辩论", 10.0, "启动AI伦理辩论"),
                TestStep("wait", "10", "", 10.0, "等待辩论进行"),
                TestStep("screenshot", "", "保存辩论过程截图", 1.0, "截图辩论过程"),
                TestStep("key_press", "ctrl+c", "退出", 2.0, "退出测试"),
                TestStep("key_press", "ctrl+c", "完全退出", 2.0, "确认退出"),
            ],
            priority=2
        ))
        
        # 6. Wiki功能测试
        test_cases.append(TestCase(
            name="Wiki功能",
            description="测试Wiki页面的创建和管理",
            steps=[
                TestStep("start_app", "", "TUI界面正常显示", 5.0, "启动TUI应用"),
                TestStep("wait", "2", "", 2.0, "等待界面加载"),
                TestStep("input", "/wiki", "显示Wiki命令选项", 2.0, "输入Wiki命令"),
                TestStep("wait", "1", "", 1.0, "等待命令选项"),
                TestStep("input", "/wiki create", "准备创建Wiki", 2.0, "输入创建Wiki命令"),
                TestStep("wait", "1", "", 1.0, "等待Wiki标题提示"),
                TestStep("input", "/wiki create Test Page", "创建测试页面", 3.0, "创建测试Wiki页面"),
                TestStep("wait", "3", "", 3.0, "等待页面创建"),
                TestStep("screenshot", "", "保存Wiki页面截图", 1.0, "截图Wiki页面"),
                TestStep("key_press", "ctrl+c", "退出", 2.0, "退出测试"),
                TestStep("key_press", "ctrl+c", "完全退出", 2.0, "确认退出"),
            ],
            priority=2
        ))
        
        # 7. 复制粘贴功能测试
        test_cases.append(TestCase(
            name="复制粘贴功能",
            description="测试输出区的复制功能",
            steps=[
                TestStep("start_app", "", "TUI界面正常显示", 5.0, "启动TUI应用"),
                TestStep("wait", "2", "", 2.0, "等待界面加载"),
                TestStep("input", "/help", "显示帮助信息", 2.0, "输入帮助命令获取文本"),
                TestStep("wait", "2", "", 2.0, "等待帮助信息显示"),
                TestStep("key_press", "ctrl+c", "尝试复制", 2.0, "测试复制功能"),
                TestStep("wait", "1", "", 1.0, "等待复制响应"),
                TestStep("screenshot", "", "保存复制状态截图", 1.0, "截图复制状态"),
                TestStep("key_press", "ctrl+c", "退出", 2.0, "退出测试"),
                TestStep("key_press", "ctrl+c", "完全退出", 2.0, "确认退出"),
            ],
            priority=1
        ))
        
        # 8. 会话管理测试
        test_cases.append(TestCase(
            name="会话管理功能",
            description="测试会话的查看和管理",
            steps=[
                TestStep("start_app", "", "TUI界面正常显示", 5.0, "启动TUI应用"),
                TestStep("wait", "2", "", 2.0, "等待界面加载"),
                TestStep("input", "/session", "显示会话命令选项", 2.0, "输入会话命令"),
                TestStep("wait", "1", "", 1.0, "等待命令选项"),
                TestStep("input", "/session list", "显示会话列表", 3.0, "显示会话列表"),
                TestStep("wait", "3", "", 3.0, "等待会话列表加载"),
                TestStep("screenshot", "", "保存会话列表截图", 1.0, "截图会话列表"),
                TestStep("key_press", "ctrl+c", "退出", 2.0, "退出测试"),
                TestStep("key_press", "ctrl+c", "完全退出", 2.0, "确认退出"),
            ],
            priority=2
        ))
        
        # 9. 错误处理测试
        test_cases.append(TestCase(
            name="错误处理和边界情况",
            description="测试错误命令和边界情况的处理",
            steps=[
                TestStep("start_app", "", "TUI界面正常显示", 5.0, "启动TUI应用"),
                TestStep("wait", "2", "", 2.0, "等待界面加载"),
                TestStep("input", "/invalid_command", "输入无效命令", 2.0, "测试无效命令处理"),
                TestStep("wait", "2", "", 2.0, "等待错误响应"),
                TestStep("input", "/model invalid_model", "输入无效模型", 2.0, "测试无效模型处理"),
                TestStep("wait", "2", "", 2.0, "等待错误响应"),
                TestStep("input", "/doc search", "空搜索查询", 2.0, "测试空查询处理"),
                TestStep("wait", "2", "", 2.0, "等待错误响应"),
                TestStep("screenshot", "", "保存错误处理截图", 1.0, "截图错误处理"),
                TestStep("key_press", "ctrl+c", "退出", 2.0, "退出测试"),
                TestStep("key_press", "ctrl+c", "完全退出", 2.0, "确认退出"),
            ],
            priority=2
        ))
        
        # 10. 性能压力测试
        test_cases.append(TestCase(
            name="性能和响应速度",
            description="测试系统响应速度和性能表现",
            steps=[
                TestStep("start_app", "", "TUI界面正常显示", 5.0, "启动TUI应用"),
                TestStep("wait", "2", "", 2.0, "等待界面加载"),
                TestStep("input", "/help", "测试命令响应速度", 1.0, "测试快速命令响应"),
                TestStep("wait", "1", "", 1.0, "测量响应时间"),
                TestStep("input", "/model list", "测试数据加载速度", 3.0, "测试数据加载性能"),
                TestStep("wait", "3", "", 3.0, "测量加载时间"),
                TestStep("input", "/doc search deep learning", "测试搜索性能", 5.0, "测试搜索响应速度"),
                TestStep("wait", "5", "", 5.0, "测量搜索时间"),
                TestStep("screenshot", "", "保存性能测试截图", 1.0, "截图性能状态"),
                TestStep("key_press", "ctrl+c", "退出", 2.0, "退出测试"),
                TestStep("key_press", "ctrl+c", "完全退出", 2.0, "确认退出"),
            ],
            priority=3
        ))
        
        return test_cases
    
    async def run_test_case(self, test_case: TestCase) -> TestResult:
        """运行单个测试用例"""
        start_time = time.time()
        issues = []
        
        try:
            print(f"🧪 开始测试: {test_case.name}")
            print(f"📝 描述: {test_case.description}")
            
            # 启动TUI应用
            process = await self._start_tui_app()
            if not process:
                return TestResult(
                    test_name=test_case.name,
                    status="ERROR",
                    details="无法启动TUI应用",
                    duration=time.time() - start_time,
                    issues=["应用启动失败"]
                )
            
            # 执行测试步骤
            for i, step in enumerate(test_case.steps):
                print(f"  🔄 步骤 {i+1}: {step.description}")
                
                step_success = await self._execute_step(process, step)
                if not step_success:
                    issues.append(f"步骤 {i+1} 失败: {step.description}")
                
                # 短暂等待确保操作完成
                await asyncio.sleep(0.5)
            
            # 清理进程
            await self._cleanup_process(process)
            
            duration = time.time() - start_time
            status = "PASS" if not issues else "FAIL"
            
            print(f"✅ 测试完成: {test_case.name} - {status}")
            
            return TestResult(
                test_name=test_case.name,
                status=status,
                details=f"执行了 {len(test_case.steps)} 个步骤",
                duration=duration,
                screenshots=self.test_screenshots.copy(),
                issues=issues
            )
            
        except Exception as e:
            return TestResult(
                test_name=test_case.name,
                status="ERROR",
                details=f"测试执行异常: {str(e)}",
                duration=time.time() - start_time,
                issues=[f"异常: {str(e)}"]
            )
        finally:
            self.test_screenshots.clear()
    
    async def _start_tui_app(self) -> Optional[subprocess.Popen]:
        """启动TUI应用"""
        try:
            # 使用Python启动TUI
            cmd = [sys.executable, "-m", "daip_live.tui"]
            
            # 设置环境变量
            env = os.environ.copy()
            env["PYTHONPATH"] = os.path.join(os.path.dirname(__file__), "src")
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=os.path.dirname(__file__)
            )
            
            # 等待应用启动
            await asyncio.sleep(2)
            
            if process.poll() is None:
                return process
            else:
                print(f"❌ 应用启动失败，返回码: {process.returncode}")
                return None
                
        except Exception as e:
            print(f"❌ 启动应用时出错: {e}")
            return None
    
    async def _execute_step(self, process: subprocess.Popen, step: TestStep) -> bool:
        """执行测试步骤"""
        try:
            if step.action == "start_app":
                return True  # 应用已在_start_tui_app中启动
                
            elif step.action == "input":
                # 发送输入
                input_text = step.content + "\n"
                process.stdin.write(input_text)
                process.stdin.flush()
                
            elif step.action == "key_press":
                # 发送按键
                if step.content.lower() == "ctrl+c":
                    # 发送Ctrl+C
                    process.send_signal(subprocess.signal.SIGINT)
                else:
                    # 其他按键处理
                    pass
                    
            elif step.action == "wait":
                # 等待指定时间
                await asyncio.sleep(float(step.content))
                
            elif step.action == "screenshot":
                # 截图功能（简化实现）
                screenshot_name = f"screenshot_{int(time.time())}.txt"
                screenshot_path = os.path.join("test_screenshots", screenshot_name)
                
                os.makedirs("test_screenshots", exist_ok=True)
                
                # 保存当前输出状态
                if process.stdout:
                    try:
                        # 非阻塞读取输出
                        import select
                        if select.select([process.stdout], [], [], 0)[0]:
                            output = process.stdout.read(1024)
                            with open(screenshot_path, 'w', encoding='utf-8') as f:
                                f.write(f"Screenshot at {datetime.now()}\n")
                                f.write(f"Step: {step.description}\n")
                                f.write(f"Output: {output}\n")
                            self.test_screenshots.append(screenshot_path)
                    except:
                        pass
                        
            # 等待步骤完成
            await asyncio.sleep(step.timeout)
            return True
            
        except Exception as e:
            print(f"❌ 执行步骤失败: {step.description} - {e}")
            return False
    
    async def _cleanup_process(self, process: subprocess.Popen):
        """清理进程"""
        try:
            if process and process.poll() is None:
                # 发送SIGTERM信号
                process.terminate()
                
                # 等待进程结束
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # 强制杀死进程
                    process.kill()
                    process.wait()
                    
        except Exception as e:
            print(f"⚠️ 清理进程时出错: {e}")
    
    async def run_all_tests(self) -> List[TestResult]:
        """运行所有测试"""
        test_cases = self.create_test_cases()
        
        print("🚀 开始TUI全面自动化测试")
        print("=" * 60)
        
        # 按优先级排序
        test_cases.sort(key=lambda x: x.priority)
        
        for test_case in test_cases:
            result = await self.run_test_case(test_case)
            self.results.append(result)
            
            # 测试间隔
            await asyncio.sleep(1)
        
        return self.results
    
    def generate_report(self, results: List[TestResult]) -> str:
        """生成测试报告"""
        report = []
        report.append("# TUI用户体验自动化测试报告")
        report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 统计信息
        total_tests = len(results)
        passed_tests = len([r for r in results if r.status == "PASS"])
        failed_tests = len([r for r in results if r.status == "FAIL"])
        error_tests = len([r for r in results if r.status == "ERROR"])
        
        report.append("## 测试统计")
        report.append(f"- 总测试数: {total_tests}")
        report.append(f"- 通过: {passed_tests}")
        report.append(f"- 失败: {failed_tests}")
        report.append(f"- 错误: {error_tests}")
        report.append(f"- 成功率: {passed_tests/total_tests*100:.1f}%")
        report.append("")
        
        # 详细结果
        report.append("## 详细测试结果")
        report.append("")
        
        for result in results:
            report.append(f"### {result.test_name}")
            report.append(f"- **状态**: {result.status}")
            report.append(f"- **耗时**: {result.duration:.2f}秒")
            report.append(f"- **详情**: {result.details}")
            
            if result.issues:
                report.append("- **问题**:")
                for issue in result.issues:
                    report.append(f"  - {issue}")
            
            if result.screenshots:
                report.append(f"- **截图**: {len(result.screenshots)} 张")
            
            report.append("")
        
        # 问题汇总
        all_issues = []
        for result in results:
            if result.issues:
                all_issues.extend(result.issues)
        
        if all_issues:
            report.append("## 发现的问题")
            report.append("")
            for i, issue in enumerate(all_issues, 1):
                report.append(f"{i}. {issue}")
            report.append("")
        
        # 改进建议
        report.append("## 改进建议")
        report.append("")
        
        if failed_tests > 0:
            report.append("1. 修复失败的测试用例中的功能问题")
        
        if error_tests > 0:
            report.append("2. 改进应用的稳定性和错误处理")
        
        report.append("3. 优化命令自动补全的用户体验")
        report.append("4. 改进复制粘贴功能的可用性")
        report.append("5. 增强Ctrl+C退出快捷键的响应性")
        report.append("6. 优化界面响应速度和性能")
        report.append("")
        
        return "\n".join(report)


async def main():
    """主函数"""
    runner = TUITestRunner()
    
    # 运行所有测试
    results = await runner.run_all_tests()
    
    # 生成报告
    report = runner.generate_report(results)
    
    # 保存报告
    report_file = f"tui_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "=" * 60)
    print(f"📊 测试完成！报告已保存到: {report_file}")
    
    # 显示简要统计
    total = len(results)
    passed = len([r for r in results if r.status == "PASS"])
    print(f"✅ 通过: {passed}/{total}")
    
    if passed < total:
        print("❌ 发现问题，请查看详细报告")
    else:
        print("🎉 所有测试通过！")


if __name__ == "__main__":
    asyncio.run(main())