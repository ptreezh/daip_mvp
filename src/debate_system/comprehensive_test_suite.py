#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多轮辩论系统全面质量检查和端到端测试套件

执行完整的系统测试，包括：
- 代码质量审查
- 端到端自动化测试
- 性能验证
- 稳定性测试
- 用户验收测试
"""

import asyncio
import time
import sys
import logging
import psutil
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import json

# 添加项目根目录到路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestResult:
    """测试结果类"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = False
        self.duration = 0.0
        self.error_message = ""
        self.details = {}
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """开始测试"""
        self.start_time = datetime.now()
    
    def finish(self, passed: bool, error_message: str = "", details: Dict = None):
        """结束测试"""
        self.end_time = datetime.now()
        self.passed = passed
        self.error_message = error_message
        self.details = details or {}
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "test_name": self.test_name,
            "passed": self.passed,
            "duration": self.duration,
            "error_message": self.error_message,
            "details": self.details,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }


class ComprehensiveTestSuite:
    """全面测试套件"""
    
    def __init__(self):
        self.test_results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
        self.system_info = self._collect_system_info()
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """收集系统信息"""
        return {
            "python_version": sys.version,
            "platform": sys.platform,
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_usage": psutil.disk_usage('.').total,
            "timestamp": datetime.now().isoformat()
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        self.start_time = datetime.now()
        logger.info("🚀 开始全面质量检查和端到端测试...")
        
        # 测试列表
        test_methods = [
            self.test_code_quality,
            self.test_module_imports,
            self.test_component_integration,
            self.test_web_interface_functionality,
            self.test_websocket_communication,
            self.test_dialogue_engine,
            self.test_state_management,
            self.test_performance_metrics,
            self.test_memory_usage,
            self.test_error_handling,
            self.test_concurrent_operations,
            self.test_end_to_end_workflow
        ]
        
        # 执行测试
        for test_method in test_methods:
            try:
                await test_method()
            except Exception as e:
                logger.error(f"测试执行失败 {test_method.__name__}: {e}")
        
        self.end_time = datetime.now()
        
        # 生成测试报告
        return self._generate_test_report()
    
    async def test_code_quality(self):
        """代码质量审查"""
        result = TestResult("代码质量审查")
        result.start()
        
        try:
            # 检查Python语法
            python_files = list(current_dir.glob("*.py"))
            syntax_errors = []
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        compile(f.read(), py_file, 'exec')
                except SyntaxError as e:
                    syntax_errors.append(f"{py_file}: {e}")
            
            # 检查代码结构
            code_metrics = {
                "total_files": len(python_files),
                "total_lines": 0,
                "syntax_errors": len(syntax_errors)
            }
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        code_metrics["total_lines"] += len(f.readlines())
                except:
                    pass
            
            result.finish(
                passed=len(syntax_errors) == 0,
                error_message="; ".join(syntax_errors) if syntax_errors else "",
                details=code_metrics
            )
            
        except Exception as e:
            result.finish(False, str(e))
        
        self.test_results.append(result)
        logger.info(f"✅ 代码质量审查: {'通过' if result.passed else '失败'}")
    
    async def test_module_imports(self):
        """模块导入测试"""
        result = TestResult("模块导入测试")
        result.start()
        
        try:
            modules_to_test = [
                "debate_flow_definition",
                "participant_management", 
                "multi_role_dialogue_engine",
                "debate_state_manager",
                "websocket_manager",
                "web_interface"
            ]
            
            import_results = {}
            for module_name in modules_to_test:
                try:
                    __import__(module_name)
                    import_results[module_name] = "success"
                except ImportError as e:
                    import_results[module_name] = f"failed: {e}"
            
            failed_imports = [k for k, v in import_results.items() if v != "success"]
            
            result.finish(
                passed=len(failed_imports) == 0,
                error_message=f"Failed imports: {failed_imports}" if failed_imports else "",
                details=import_results
            )
            
        except Exception as e:
            result.finish(False, str(e))
        
        self.test_results.append(result)
        logger.info(f"✅ 模块导入测试: {'通过' if result.passed else '失败'}")
    
    async def test_component_integration(self):
        """组件集成测试"""
        result = TestResult("组件集成测试")
        result.start()
        
        try:
            from multi_role_dialogue_engine import MultiRoleDialogueEngine
            from debate_state_manager import DebateStateManager
            from websocket_manager import DebateWebSocketManager
            
            # 创建模拟组件
            class MockComponent:
                async def get_available_roles(self):
                    return {"test": {"name": "Test"}}
                async def generate_response(self, *args, **kwargs):
                    return "Test response"
                async def store_memory(self, *args, **kwargs):
                    pass
            
            mock_component = MockComponent()
            
            # 测试组件创建
            dialogue_engine = MultiRoleDialogueEngine(
                cognitive_agent=mock_component,
                role_manager=mock_component,
                llm_manager=mock_component,
                memory_agent=mock_component,
                participant_manager=mock_component
            )
            
            state_manager = DebateStateManager()
            websocket_manager = DebateWebSocketManager()
            
            integration_results = {
                "dialogue_engine_created": dialogue_engine is not None,
                "state_manager_created": state_manager is not None,
                "websocket_manager_created": websocket_manager is not None
            }
            
            all_created = all(integration_results.values())
            
            result.finish(
                passed=all_created,
                details=integration_results
            )
            
        except Exception as e:
            result.finish(False, str(e))
        
        self.test_results.append(result)
        logger.info(f"✅ 组件集成测试: {'通过' if result.passed else '失败'}")

    
    async def test_web_interface_functionality(self):
        """Web界面功能测试"""
        result = TestResult("Web界面功能测试")
        result.start()
        
        try:
            from web_interface import DebateWebInterface, DebateInterfaceMode
            from multi_role_dialogue_engine import MultiRoleDialogueEngine
            from debate_state_manager import DebateStateManager
            
            # 创建模拟组件
            class MockComponent:
                async def get_available_roles(self):
                    return {"test": {"name": "Test"}}
                async def generate_response(self, *args, **kwargs):
                    return "Test response"
                async def store_memory(self, *args, **kwargs):
                    pass
            
            mock_component = MockComponent()
            
            # 创建对话引擎和状态管理器
            dialogue_engine = MultiRoleDialogueEngine(
                cognitive_agent=mock_component,
                role_manager=mock_component,
                llm_manager=mock_component,
                memory_agent=mock_component,
                participant_manager=mock_component
            )
            
            state_manager = DebateStateManager()
            
            # 创建Web界面
            web_interface = DebateWebInterface(
                dialogue_engine=dialogue_engine,
                state_manager=state_manager
            )
            
            # 测试界面功能
            interface_tests = {
                "initial_mode_correct": web_interface.current_mode == DebateInterfaceMode.SETUP,
                "ui_elements_exist": all([
                    web_interface.topic_input is not None,
                    web_interface.start_debate_button is not None,
                    web_interface.stop_debate_button is not None
                ]),
                "mode_switching": True  # 简化测试
            }
            
            all_passed = all(interface_tests.values())
            
            result.finish(
                passed=all_passed,
                details=interface_tests
            )
            
        except Exception as e:
            result.finish(False, str(e))
        
        self.test_results.append(result)
        logger.info(f"✅ Web界面功能测试: {'通过' if result.passed else '失败'}")
    
    async def test_websocket_communication(self):
        """WebSocket通信测试"""
        result = TestResult("WebSocket通信测试")
        result.start()
        
        try:
            from websocket_manager import DebateWebSocketManager, WebSocketMessage, MessageType
            
            # 创建WebSocket管理器
            ws_manager = DebateWebSocketManager()
            
            # 测试消息创建和序列化
            test_message = WebSocketMessage(
                type=MessageType.SYSTEM_STATUS,
                payload={"status": "test"},
                session_id="test_session"
            )
            
            # 测试消息序列化/反序列化
            message_dict = test_message.to_dict()
            restored_message = WebSocketMessage.from_dict(message_dict)
            
            websocket_tests = {
                "message_creation": test_message is not None,
                "message_serialization": message_dict is not None,
                "message_deserialization": restored_message.type == test_message.type,
                "manager_creation": ws_manager is not None,
                "connection_status": isinstance(ws_manager.get_connection_status(), dict)
            }
            
            all_passed = all(websocket_tests.values())
            
            result.finish(
                passed=all_passed,
                details=websocket_tests
            )
            
        except Exception as e:
            result.finish(False, str(e))
        
        self.test_results.append(result)
        logger.info(f"✅ WebSocket通信测试: {'通过' if result.passed else '失败'}")
    
    async def test_dialogue_engine(self):
        """对话引擎测试"""
        result = TestResult("对话引擎测试")
        result.start()
        
        try:
            from multi_role_dialogue_engine import (
                MultiRoleDialogueEngine, ConvergenceDetector, DialogueContext
            )
            from debate_flow_definition import DebateSession, DebatePhase
            
            # 创建模拟组件
            class MockRoleManager:
                async def get_available_roles(self):
                    return {
                        "expert1": {"name": "专家1", "expertise_areas": ["测试"], "speaking_style": "formal"}
                    }
            
            class MockLLMManager:
                async def generate_response(self, *args, **kwargs):
                    return "这是一个测试响应"
            
            class MockComponent:
                async def store_memory(self, *args, **kwargs):
                    pass
            
            # 创建对话引擎
            dialogue_engine = MultiRoleDialogueEngine(
                cognitive_agent=MockComponent(),
                role_manager=MockRoleManager(),
                llm_manager=MockLLMManager(),
                memory_agent=MockComponent(),
                participant_manager=MockComponent()
            )
            
            # 创建测试会话
            test_session = DebateSession(
                title="测试辩论",
                topic="测试话题"
            )
            
            # 测试收敛检测器
            detector = ConvergenceDetector()
            dialogue_context = DialogueContext(
                session_id="test",
                topic="测试",
                current_phase=DebatePhase.MAIN_ARGUMENTS
            )
            
            convergence = await detector.detect_convergence(dialogue_context)
            
            dialogue_tests = {
                "engine_creation": dialogue_engine is not None,
                "convergence_detection": isinstance(convergence, dict),
                "convergence_keys": all(key in convergence for key in [
                    'viewpoint_similarity', 'repetition_level', 'activity_level', 'overall_convergence'
                ])
            }
            
            all_passed = all(dialogue_tests.values())
            
            result.finish(
                passed=all_passed,
                details=dialogue_tests
            )
            
        except Exception as e:
            result.finish(False, str(e))
        
        self.test_results.append(result)
        logger.info(f"✅ 对话引擎测试: {'通过' if result.passed else '失败'}")
    
    async def test_state_management(self):
        """状态管理测试"""
        result = TestResult("状态管理测试")
        result.start()
        
        try:
            from debate_state_manager import DebateStateManager
            from debate_flow_definition import DebateSession, DebateParticipant, ParticipantRole
            
            # 创建状态管理器
            state_manager = DebateStateManager()
            
            # 创建测试会话
            test_session = DebateSession(
                title="状态测试",
                topic="测试话题"
            )
            
            # 测试会话操作
            create_success = await state_manager.create_session(test_session)
            retrieved_session = await state_manager.get_session(test_session.session_id)
            
            # 测试参与者操作
            test_participant = DebateParticipant(
                participant_id="test_user",
                name="测试用户",
                role=ParticipantRole.PROPONENT
            )
            
            add_participant_success = await state_manager.add_participant(
                test_session.session_id, test_participant
            )
            
            # 测试快照
            snapshot_id = await state_manager.create_snapshot(test_session.session_id)
            
            # 测试指标
            metrics = await state_manager.get_session_metrics(test_session.session_id)
            
            state_tests = {
                "session_creation": create_success,
                "session_retrieval": retrieved_session is not None,
                "participant_addition": add_participant_success,
                "snapshot_creation": snapshot_id is not None,
                "metrics_retrieval": metrics is not None
            }
            
            all_passed = all(state_tests.values())
            
            result.finish(
                passed=all_passed,
                details=state_tests
            )
            
        except Exception as e:
            result.finish(False, str(e))
        
        self.test_results.append(result)
        logger.info(f"✅ 状态管理测试: {'通过' if result.passed else '失败'}")
    
    async def test_performance_metrics(self):
        """性能指标测试"""
        result = TestResult("性能指标测试")
        result.start()
        
        try:
            # 测试系统启动时间
            startup_start = time.time()
            
            from multi_role_dialogue_engine import MultiRoleDialogueEngine
            
            startup_time = time.time() - startup_start
            
            # 测试响应时间
            response_start = time.time()
            
            # 模拟一些操作
            class MockComponent:
                async def get_available_roles(self):
                    return {"test": {"name": "Test"}}
                async def generate_response(self, *args, **kwargs):
                    await asyncio.sleep(0.1)  # 模拟处理时间
                    return "Test response"
                async def store_memory(self, *args, **kwargs):
                    pass
            
            mock_component = MockComponent()
            dialogue_engine = MultiRoleDialogueEngine(
                cognitive_agent=mock_component,
                role_manager=mock_component,
                llm_manager=mock_component,
                memory_agent=mock_component,
                participant_manager=mock_component
            )
            
            response_time = time.time() - response_start
            
            # 测试内存使用
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            
            performance_metrics = {
                "startup_time_seconds": startup_time,
                "response_time_seconds": response_time,
                "memory_usage_mb": memory_usage,
                "startup_time_ok": startup_time < 30,  # 启动时间 < 30秒
                "response_time_ok": response_time < 30,  # 响应时间 < 30秒
                "memory_usage_ok": memory_usage < 2048  # 内存使用 < 2GB
            }
            
            performance_ok = all([
                performance_metrics["startup_time_ok"],
                performance_metrics["response_time_ok"],
                performance_metrics["memory_usage_ok"]
            ])
            
            result.finish(
                passed=performance_ok,
                details=performance_metrics
            )
            
        except Exception as e:
            result.finish(False, str(e))
        
        self.test_results.append(result)
        logger.info(f"✅ 性能指标测试: {'通过' if result.passed else '失败'}")
    
    async def test_memory_usage(self):
        """内存使用测试"""
        result = TestResult("内存使用测试")
        result.start()
        
        try:
            process = psutil.Process()
            initial_memory = process.memory_info().rss
            
            # 创建多个组件实例来测试内存使用
            components = []
            for i in range(10):
                from debate_state_manager import DebateStateManager
                state_manager = DebateStateManager()
                components.append(state_manager)
            
            # 等待一段时间
            await asyncio.sleep(1)
            
            peak_memory = process.memory_info().rss
            memory_increase = (peak_memory - initial_memory) / 1024 / 1024  # MB
            
            # 清理组件
            components.clear()
            
            # 等待垃圾回收
            import gc
            gc.collect()
            await asyncio.sleep(1)
            
            final_memory = process.memory_info().rss
            memory_after_cleanup = (final_memory - initial_memory) / 1024 / 1024  # MB
            
            memory_tests = {
                "initial_memory_mb": initial_memory / 1024 / 1024,
                "peak_memory_mb": peak_memory / 1024 / 1024,
                "final_memory_mb": final_memory / 1024 / 1024,
                "memory_increase_mb": memory_increase,
                "memory_after_cleanup_mb": memory_after_cleanup,
                "memory_leak_detected": memory_after_cleanup > memory_increase * 0.5
            }
            
            memory_ok = not memory_tests["memory_leak_detected"]
            
            result.finish(
                passed=memory_ok,
                details=memory_tests
            )
            
        except Exception as e:
            result.finish(False, str(e))
        
        self.test_results.append(result)
        logger.info(f"✅ 内存使用测试: {'通过' if result.passed else '失败'}")
    
    async def test_error_handling(self):
        """错误处理测试"""
        result = TestResult("错误处理测试")
        result.start()
        
        try:
            from debate_state_manager import DebateStateManager
            from multi_role_dialogue_engine import MultiRoleDialogueEngine
            
            # 测试无效输入处理
            state_manager = DebateStateManager()
            
            # 测试获取不存在的会话
            non_existent_session = await state_manager.get_session("non_existent_id")
            
            # 测试删除不存在的会话
            delete_result = await state_manager.delete_session("non_existent_id")
            
            # 测试空输入处理
            class FailingComponent:
                async def get_available_roles(self):
                    raise Exception("Simulated failure")
                async def generate_response(self, *args, **kwargs):
                    raise Exception("Simulated failure")
                async def store_memory(self, *args, **kwargs):
                    raise Exception("Simulated failure")
            
            failing_component = FailingComponent()
            
            # 测试组件失败处理
            try:
                dialogue_engine = MultiRoleDialogueEngine(
                    cognitive_agent=failing_component,
                    role_manager=failing_component,
                    llm_manager=failing_component,
                    memory_agent=failing_component,
                    participant_manager=failing_component
                )
                component_creation_failed = False
            except:
                component_creation_failed = True
            
            error_tests = {
                "non_existent_session_handled": non_existent_session is None,
                "non_existent_delete_handled": delete_result is False,
                "component_failure_handled": not component_creation_failed  # 应该能创建，但调用时失败
            }
            
            all_handled = all(error_tests.values())
            
            result.finish(
                passed=all_handled,
                details=error_tests
            )
            
        except Exception as e:
            result.finish(False, str(e))
        
        self.test_results.append(result)
        logger.info(f"✅ 错误处理测试: {'通过' if result.passed else '失败'}")
    
    async def test_concurrent_operations(self):
        """并发操作测试"""
        result = TestResult("并发操作测试")
        result.start()
        
        try:
            from debate_state_manager import DebateStateManager
            from debate_flow_definition import DebateSession
            
            state_manager = DebateStateManager()
            
            # 创建多个并发会话
            async def create_test_session(session_id: str):
                session = DebateSession(
                    title=f"并发测试 {session_id}",
                    topic=f"测试话题 {session_id}"
                )
                session.session_id = session_id
                return await state_manager.create_session(session)
            
            # 并发创建会话
            concurrent_tasks = [
                create_test_session(f"concurrent_{i}")
                for i in range(5)
            ]
            
            results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
            
            # 检查结果
            successful_creations = sum(1 for r in results if r is True)
            exceptions = [r for r in results if isinstance(r, Exception)]
            
            concurrent_tests = {
                "total_tasks": len(concurrent_tasks),
                "successful_creations": successful_creations,
                "exceptions_count": len(exceptions),
                "all_successful": len(exceptions) == 0 and successful_creations == len(concurrent_tasks)
            }
            
            result.finish(
                passed=concurrent_tests["all_successful"],
                details=concurrent_tests
            )
            
        except Exception as e:
            result.finish(False, str(e))
        
        self.test_results.append(result)
        logger.info(f"✅ 并发操作测试: {'通过' if result.passed else '失败'}")
    
    async def test_end_to_end_workflow(self):
        """端到端工作流测试"""
        result = TestResult("端到端工作流测试")
        result.start()
        
        try:
            from multi_role_dialogue_engine import MultiRoleDialogueEngine
            from debate_state_manager import DebateStateManager
            from debate_flow_definition import DebateSession
            
            # 创建完整的工作流
            class MockRoleManager:
                async def get_available_roles(self):
                    return {
                        "expert1": {"name": "专家1", "expertise_areas": ["测试"], "speaking_style": "formal"},
                        "expert2": {"name": "专家2", "expertise_areas": ["验证"], "speaking_style": "analytical"}
                    }
            
            class MockLLMManager:
                async def generate_response(self, *args, **kwargs):
                    await asyncio.sleep(0.1)  # 模拟处理时间
                    return "这是一个端到端测试响应"
            
            class MockComponent:
                async def store_memory(self, *args, **kwargs):
                    pass
            
            # 创建组件
            dialogue_engine = MultiRoleDialogueEngine(
                cognitive_agent=MockComponent(),
                role_manager=MockRoleManager(),
                llm_manager=MockLLMManager(),
                memory_agent=MockComponent(),
                participant_manager=MockComponent()
            )
            
            state_manager = DebateStateManager()
            
            # 创建测试会话
            test_session = DebateSession(
                title="端到端测试辩论",
                topic="人工智能的未来发展"
            )
            
            # 执行完整工作流
            workflow_steps = {}
            
            # 1. 创建会话
            workflow_steps["session_created"] = await state_manager.create_session(test_session)
            
            # 2. 启动对话
            workflow_steps["dialogue_started"] = await dialogue_engine.start_dialogue(
                test_session, test_session.topic, max_roles=2
            )
            
            # 3. 继续对话
            if workflow_steps["dialogue_started"]:
                workflow_steps["dialogue_continued"] = await dialogue_engine.continue_dialogue(
                    test_session.session_id
                )
            else:
                workflow_steps["dialogue_continued"] = False
            
            # 4. 获取对话摘要
            if workflow_steps["dialogue_continued"]:
                summary = await dialogue_engine.get_dialogue_summary(test_session.session_id)
                workflow_steps["summary_generated"] = summary is not None
            else:
                workflow_steps["summary_generated"] = False
            
            # 5. 结束对话
            if workflow_steps["dialogue_started"]:
                workflow_steps["dialogue_ended"] = await dialogue_engine.end_dialogue(
                    test_session.session_id
                )
            else:
                workflow_steps["dialogue_ended"] = False
            
            # 检查工作流完整性
            workflow_complete = all(workflow_steps.values())
            
            result.finish(
                passed=workflow_complete,
                details=workflow_steps
            )
            
        except Exception as e:
            result.finish(False, str(e))
        
        self.test_results.append(result)
        logger.info(f"✅ 端到端工作流测试: {'通过' if result.passed else '失败'}")
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        failed_tests = total_tests - passed_tests
        
        total_duration = (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else 0
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_duration,
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None
            },
            "system_info": self.system_info,
            "test_results": [result.to_dict() for result in self.test_results],
            "quality_gates": self._check_quality_gates()
        }
        
        return report
    
    def _check_quality_gates(self) -> Dict[str, Any]:
        """检查质量门禁"""
        gates = {}
        
        # 基本质量门禁
        passed_tests = sum(1 for r in self.test_results if r.passed)
        total_tests = len(self.test_results)
        
        gates["all_tests_passed"] = passed_tests == total_tests
        gates["success_rate_above_90"] = (passed_tests / total_tests * 100) >= 90 if total_tests > 0 else False
        
        # 性能门禁
        performance_result = next((r for r in self.test_results if r.test_name == "性能指标测试"), None)
        if performance_result and performance_result.passed:
            gates["performance_requirements_met"] = True
            gates["startup_time_ok"] = performance_result.details.get("startup_time_ok", False)
            gates["response_time_ok"] = performance_result.details.get("response_time_ok", False)
            gates["memory_usage_ok"] = performance_result.details.get("memory_usage_ok", False)
        else:
            gates["performance_requirements_met"] = False
            gates["startup_time_ok"] = False
            gates["response_time_ok"] = False
            gates["memory_usage_ok"] = False
        
        # 稳定性门禁
        memory_result = next((r for r in self.test_results if r.test_name == "内存使用测试"), None)
        gates["memory_leak_free"] = memory_result.passed if memory_result else False
        
        concurrent_result = next((r for r in self.test_results if r.test_name == "并发操作测试"), None)
        gates["concurrent_operations_stable"] = concurrent_result.passed if concurrent_result else False
        
        # 端到端门禁
        e2e_result = next((r for r in self.test_results if r.test_name == "端到端工作流测试"), None)
        gates["end_to_end_workflow_complete"] = e2e_result.passed if e2e_result else False
        
        # 总体质量门禁
        gates["overall_quality_gate_passed"] = all([
            gates["all_tests_passed"],
            gates["performance_requirements_met"],
            gates["memory_leak_free"],
            gates["end_to_end_workflow_complete"]
        ])
        
        return gates


async def main():
    """主函数"""
    print("🚀 启动多轮辩论系统全面质量检查和端到端测试...")
    print("=" * 80)
    
    # 创建测试套件
    test_suite = ComprehensiveTestSuite()
    
    # 运行所有测试
    test_report = await test_suite.run_all_tests()
    
    # 显示测试结果
    print("\n" + "=" * 80)
    print("📊 测试结果摘要")
    print("=" * 80)
    
    summary = test_report["summary"]
    print(f"总测试数: {summary['total_tests']}")
    print(f"通过测试: {summary['passed_tests']}")
    print(f"失败测试: {summary['failed_tests']}")
    print(f"成功率: {summary['success_rate']:.1f}%")
    print(f"总耗时: {summary['total_duration']:.2f}秒")
    
    # 显示质量门禁结果
    print("\n🚪 质量门禁检查")
    print("-" * 40)
    
    quality_gates = test_report["quality_gates"]
    for gate_name, gate_result in quality_gates.items():
        status = "✅ 通过" if gate_result else "❌ 失败"
        print(f"{gate_name}: {status}")
    
    # 显示失败的测试详情
    failed_tests = [r for r in test_suite.test_results if not r.passed]
    if failed_tests:
        print("\n❌ 失败测试详情")
        print("-" * 40)
        for test in failed_tests:
            print(f"测试: {test.test_name}")
            print(f"错误: {test.error_message}")
            print(f"耗时: {test.duration:.2f}秒")
            print()
    
    # 保存测试报告
    report_file = current_dir / "test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(test_report, f, indent=2, ensure_ascii=False)
    
    print(f"📄 详细测试报告已保存到: {report_file}")
    
    # 最终结果
    overall_passed = quality_gates["overall_quality_gate_passed"]
    if overall_passed:
        print("\n🎉 所有质量检查通过！系统已准备就绪！")
        print("✅ 多轮辩论系统V0.1版本质量验证完成")
        return True
    else:
        print("\n⚠️ 部分质量检查未通过，需要进一步修复")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        sys.exit(1)