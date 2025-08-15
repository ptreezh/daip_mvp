#!/usr/bin/env python3
"""真实多轮辩论系统端到端测试

完整测试用户从启动系统到完成辩论的整个流程，
确保所有组件协同工作，用户体验流畅。
"""

import asyncio
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EndToEndTestResult:
    """端到端测试结果"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = False
        self.duration = 0.0
        self.error_message = ""
        self.details = {}
        self.start_time = None
        self.end_time = None
        self.user_experience_score = 0.0  # 用户体验评分 (0-10)
    
    def start(self):
        """开始测试"""
        self.start_time = datetime.now()
    
    def finish(self, passed: bool, error_message: str = "", details: dict = None, ux_score: float = 0.0):
        """结束测试"""
        self.end_time = datetime.now()
        self.passed = passed
        self.error_message = error_message
        self.details = details or {}
        self.user_experience_score = ux_score
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()


class EndToEndTester:
    """端到端测试器"""
    
    def __init__(self):
        self.test_results: list[EndToEndTestResult] = []
        self.start_time = None
        self.end_time = None
    
    async def run_complete_test_suite(self) -> dict[str, Any]:
        """运行完整的端到端测试套件"""
        self.start_time = datetime.now()
        
        print("🚀 启动真实多轮辩论系统端到端测试")
        print("=" * 80)
        print("测试目标: 验证完整用户体验流程")
        print("测试范围: 从系统启动到辩论完成的全流程")
        print("=" * 80)
        
        # 测试套件
        test_methods = [
            self.test_system_startup,
            self.test_role_management,
            self.test_llm_integration,
            self.test_debate_creation,
            self.test_debate_execution,
            self.test_state_management,
            self.test_error_handling,
            self.test_user_experience_flow,
            self.test_performance_requirements,
            self.test_data_persistence
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
    
    async def test_system_startup(self):
        """测试系统启动"""
        result = EndToEndTestResult("系统启动测试")
        result.start()
        
        try:
            startup_start = time.time()
            
            # 导入核心组件
            from src.core_services.role_manager import RoleManager
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            
            startup_time = time.time() - startup_start
            
            # 创建组件
            llm_integrator = RealLLMIntegrator()
            role_manager = RoleManager()
            debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
            
            # 验证组件状态
            startup_checks = {
                "import_time_ok": startup_time < 5.0,  # 导入时间 < 5秒
                "llm_integrator_ready": llm_integrator is not None,
                "role_manager_ready": role_manager is not None,
                "debate_system_ready": debate_system is not None,
                "roles_loaded": len(role_manager._roles) > 0
            }
            
            all_passed = all(startup_checks.values())
            ux_score = 9.0 if startup_time < 2.0 else 7.0 if startup_time < 5.0 else 5.0
            
            result.finish(
                passed=all_passed,
                details={
                    "startup_time": startup_time,
                    "roles_count": len(role_manager._roles),
                    **startup_checks
                },
                ux_score=ux_score
            )
            
        except Exception as e:
            result.finish(False, str(e), ux_score=0.0)
        
        self.test_results.append(result)
        print(f"✓ 系统启动测试: {'通过' if result.passed else '失败'} (UX: {result.user_experience_score}/10)")
    
    async def test_role_management(self):
        """测试角色管理"""
        result = EndToEndTestResult("角色管理测试")
        result.start()
        
        try:
            from src.core_services.role_manager import RoleManager
            
            role_manager = RoleManager()
            
            # 测试角色加载和获取
            test_roles = ["AI Ethics", "Business Ethics", "Data Governance Expert"]
            role_tests = {}
            
            for role_id in test_roles:
                role = role_manager.get_role(role_id)
                role_tests[f"{role_id}_exists"] = role is not None
                if role:
                    role_tests[f"{role_id}_has_name"] = hasattr(role, 'name') and role.name
                    role_tests[f"{role_id}_has_description"] = hasattr(role, 'description') and role.description
            
            # 测试角色数据完整性
            total_roles = len(role_manager._roles)
            role_tests["sufficient_roles"] = total_roles >= 10
            role_tests["no_duplicate_ids"] = len(set(role_manager._roles.keys())) == total_roles
            
            all_passed = all(role_tests.values())
            ux_score = 9.0 if all_passed and total_roles > 100 else 7.0 if all_passed else 3.0
            
            result.finish(
                passed=all_passed,
                details={
                    "total_roles": total_roles,
                    **role_tests
                },
                ux_score=ux_score
            )
            
        except Exception as e:
            result.finish(False, str(e), ux_score=0.0)
        
        self.test_results.append(result)
        print(f"✓ 角色管理测试: {'通过' if result.passed else '失败'} (UX: {result.user_experience_score}/10)")
    
    async def test_llm_integration(self):
        """测试LLM集成"""
        result = EndToEndTestResult("LLM集成测试")
        result.start()
        
        try:
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            
            llm_integrator = RealLLMIntegrator()
            
            # 测试LLM调用
            test_prompt = "请简单回答：什么是人工智能？"
            call_start = time.time()
            
            record = await llm_integrator.call_llm(
                prompt=test_prompt,
                metadata={"test": "end_to_end"}
            )
            
            call_duration = time.time() - call_start
            
            # 验证LLM响应
            llm_tests = {
                "call_successful": record.success,
                "response_not_empty": bool(record.response.strip()),
                "response_time_ok": call_duration < 30.0,  # 响应时间 < 30秒
                "has_metadata": record.metadata is not None,
                "proper_encoding": isinstance(record.response, str)
            }
            
            all_passed = all(llm_tests.values())
            ux_score = 9.0 if call_duration < 10.0 else 7.0 if call_duration < 20.0 else 5.0 if call_duration < 30.0 else 2.0
            
            result.finish(
                passed=all_passed,
                details={
                    "call_duration": call_duration,
                    "response_length": len(record.response),
                    "provider": record.provider,
                    "model": record.model,
                    **llm_tests
                },
                ux_score=ux_score
            )
            
        except Exception as e:
            result.finish(False, str(e), ux_score=0.0)
        
        self.test_results.append(result)
        print(f"✓ LLM集成测试: {'通过' if result.passed else '失败'} (UX: {result.user_experience_score}/10)")
    
    async def test_debate_creation(self):
        """测试辩论创建"""
        result = EndToEndTestResult("辩论创建测试")
        result.start()
        
        try:
            from src.core_services.role_manager import RoleManager
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            
            # 创建系统组件
            llm_integrator = RealLLMIntegrator()
            role_manager = RoleManager()
            debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
            
            # 测试辩论创建
            creation_start = time.time()
            
            debate_result = await debate_system.start_debate(
                debate_topic="人工智能在教育中的应用：机遇与挑战",
                participating_roles=["AI Ethics", "Business Ethics"],
                debate_format="structured",
                time_limit_minutes=30
            )
            
            creation_time = time.time() - creation_start
            
            # 验证辩论创建结果
            creation_tests = {
                "debate_created": debate_result is not None,
                "has_debate_id": "debate_id" in debate_result if debate_result else False,
                "has_topic": "topic" in debate_result if debate_result else False,
                "has_participants": "participating_roles" in debate_result if debate_result else False,
                "creation_time_ok": creation_time < 60.0,  # 创建时间 < 60秒
                "participants_loaded": len(debate_result.get("participating_roles", [])) == 2 if debate_result else False
            }
            
            all_passed = all(creation_tests.values())
            ux_score = 9.0 if creation_time < 10.0 else 7.0 if creation_time < 30.0 else 5.0 if creation_time < 60.0 else 2.0
            
            result.finish(
                passed=all_passed,
                details={
                    "creation_time": creation_time,
                    "debate_id": debate_result.get("debate_id") if debate_result else None,
                    "cognitive_diversity": debate_result.get("cognitive_diversity_score") if debate_result else None,
                    **creation_tests
                },
                ux_score=ux_score
            )
            
        except Exception as e:
            result.finish(False, str(e), ux_score=0.0)
        
        self.test_results.append(result)
        print(f"✓ 辩论创建测试: {'通过' if result.passed else '失败'} (UX: {result.user_experience_score}/10)")
    
    async def test_debate_execution(self):
        """测试辩论执行"""
        result = EndToEndTestResult("辩论执行测试")
        result.start()
        
        try:
            from src.core_services.role_manager import RoleManager
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            
            # 创建系统组件
            llm_integrator = RealLLMIntegrator()
            role_manager = RoleManager()
            debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
            
            # 创建辩论
            debate_result = await debate_system.start_debate(
                debate_topic="远程工作的未来发展趋势",
                participating_roles=["AI Ethics", "Business Ethics"],
                debate_format="structured"
            )
            
            if not debate_result or "debate_id" not in debate_result:
                raise Exception("Failed to create debate for execution test")
            
            debate_id = debate_result["debate_id"]
            
            # 测试辩论状态获取
            status = debate_system.get_debate_status(debate_id)
            
            # 验证辩论执行功能
            execution_tests = {
                "status_retrievable": status is not None,
                "has_phase": "phase" in status if status else False,
                "debate_in_active_list": debate_id in debate_system.active_debates,
                "session_data_complete": bool(debate_system.active_debates.get(debate_id)) if debate_id in debate_system.active_debates else False
            }
            
            all_passed = all(execution_tests.values())
            ux_score = 8.0 if all_passed else 4.0
            
            result.finish(
                passed=all_passed,
                details={
                    "debate_id": debate_id,
                    "status": status,
                    "active_debates_count": len(debate_system.active_debates),
                    **execution_tests
                },
                ux_score=ux_score
            )
            
        except Exception as e:
            result.finish(False, str(e), ux_score=0.0)
        
        self.test_results.append(result)
        print(f"✓ 辩论执行测试: {'通过' if result.passed else '失败'} (UX: {result.user_experience_score}/10)")
    
    async def test_state_management(self):
        """测试状态管理"""
        result = EndToEndTestResult("状态管理测试")
        result.start()
        
        try:
            from src.debate_system.debate_flow_definition import DebateSession
            from src.debate_system.debate_state_manager import DebateStateManager
            
            # 创建状态管理器
            state_manager = DebateStateManager()
            
            # 创建测试会话
            test_session = DebateSession(
                title="状态管理测试辩论",
                topic="测试状态持久化功能"
            )
            
            # 测试状态操作
            state_tests = {}
            
            # 创建会话
            created = await state_manager.create_session(test_session)
            state_tests["session_created"] = created
            
            # 获取会话
            retrieved = await state_manager.get_session(test_session.session_id)
            state_tests["session_retrieved"] = retrieved is not None
            state_tests["session_data_intact"] = retrieved.title == test_session.title if retrieved else False
            
            # 更新会话
            if retrieved:
                retrieved.topic = "更新后的测试话题"
                updated = await state_manager.update_session(retrieved)
                state_tests["session_updated"] = updated
            
            # 创建快照
            snapshot = await state_manager.create_snapshot(test_session.session_id)
            state_tests["snapshot_created"] = snapshot is not None
            
            all_passed = all(state_tests.values())
            ux_score = 8.0 if all_passed else 4.0
            
            result.finish(
                passed=all_passed,
                details={
                    "session_id": test_session.session_id,
                    **state_tests
                },
                ux_score=ux_score
            )
            
        except Exception as e:
            result.finish(False, str(e), ux_score=0.0)
        
        self.test_results.append(result)
        print(f"✓ 状态管理测试: {'通过' if result.passed else '失败'} (UX: {result.user_experience_score}/10)")
    
    async def test_error_handling(self):
        """测试错误处理"""
        result = EndToEndTestResult("错误处理测试")
        result.start()
        
        try:
            from src.core_services.role_manager import RoleManager
            from src.debate_system.debate_state_manager import DebateStateManager
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            
            # 创建组件
            llm_integrator = RealLLMIntegrator()
            role_manager = RoleManager()
            debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
            state_manager = DebateStateManager()
            
            error_tests = {}
            
            # 测试无效角色处理
            try:
                invalid_debate = await debate_system.start_debate(
                    debate_topic="测试无效角色",
                    participating_roles=["NonExistentRole1", "NonExistentRole2"]
                )
                error_tests["invalid_roles_handled"] = invalid_debate is None or "error" in invalid_debate
            except Exception:
                error_tests["invalid_roles_handled"] = True  # 异常也是正确的处理方式
            
            # 测试无效会话ID处理
            invalid_session = await state_manager.get_session("invalid_session_id")
            error_tests["invalid_session_handled"] = invalid_session is None
            
            # 测试无效辩论状态获取
            invalid_status = debate_system.get_debate_status("invalid_debate_id")
            error_tests["invalid_status_handled"] = invalid_status is None or "error" in str(invalid_status)
            
            all_passed = all(error_tests.values())
            ux_score = 8.0 if all_passed else 3.0
            
            result.finish(
                passed=all_passed,
                details=error_tests,
                ux_score=ux_score
            )
            
        except Exception as e:
            result.finish(False, str(e), ux_score=0.0)
        
        self.test_results.append(result)
        print(f"✓ 错误处理测试: {'通过' if result.passed else '失败'} (UX: {result.user_experience_score}/10)")
    
    async def test_user_experience_flow(self):
        """测试用户体验流程"""
        result = EndToEndTestResult("用户体验流程测试")
        result.start()
        
        try:
            # 模拟完整的用户使用流程
            flow_start = time.time()
            
            # 1. 用户启动系统
            from src.core_services.role_manager import RoleManager
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            
            startup_time = time.time()
            llm_integrator = RealLLMIntegrator()
            role_manager = RoleManager()
            debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
            startup_duration = time.time() - startup_time
            
            # 2. 用户浏览可用角色
            available_roles = list(role_manager._roles.keys())[:10]  # 获取前10个角色
            
            # 3. 用户创建辩论
            creation_time = time.time()
            debate_result = await debate_system.start_debate(
                debate_topic="数字化转型对传统行业的影响",
                participating_roles=available_roles[:2]
            )
            creation_duration = time.time() - creation_time
            
            # 4. 用户查看辩论状态
            if debate_result and "debate_id" in debate_result:
                status = debate_system.get_debate_status(debate_result["debate_id"])
            else:
                status = None
            
            total_flow_time = time.time() - flow_start
            
            # 评估用户体验
            ux_tests = {
                "startup_fast": startup_duration < 5.0,  # 启动快速
                "roles_available": len(available_roles) >= 5,  # 有足够的角色选择
                "creation_successful": debate_result is not None,  # 创建成功
                "creation_fast": creation_duration < 60.0,  # 创建快速
                "status_accessible": status is not None,  # 状态可访问
                "total_flow_reasonable": total_flow_time < 120.0  # 总流程时间合理
            }
            
            # 计算用户体验评分
            passed_count = sum(ux_tests.values())
            total_count = len(ux_tests)
            base_score = (passed_count / total_count) * 10
            
            # 根据时间性能调整评分
            if startup_duration < 2.0 and creation_duration < 30.0:
                ux_score = min(10.0, base_score + 1.0)
            elif startup_duration < 5.0 and creation_duration < 60.0:
                ux_score = base_score
            else:
                ux_score = max(0.0, base_score - 2.0)
            
            all_passed = all(ux_tests.values())
            
            result.finish(
                passed=all_passed,
                details={
                    "startup_duration": startup_duration,
                    "creation_duration": creation_duration,
                    "total_flow_time": total_flow_time,
                    "available_roles_count": len(available_roles),
                    **ux_tests
                },
                ux_score=ux_score
            )
            
        except Exception as e:
            result.finish(False, str(e), ux_score=0.0)
        
        self.test_results.append(result)
        print(f"✓ 用户体验流程测试: {'通过' if result.passed else '失败'} (UX: {result.user_experience_score}/10)")
    
    async def test_performance_requirements(self):
        """测试性能要求"""
        result = EndToEndTestResult("性能要求测试")
        result.start()
        
        try:
            import os

            import psutil
            
            # 获取当前进程信息
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 执行性能测试
            perf_start = time.time()
            
            # 创建多个系统实例测试内存使用
            from src.core_services.role_manager import RoleManager
            from src.real_demo_system.multi_role_debate_system import MultiRoleDebateSystem
            from src.real_demo_system.real_llm_integrator import RealLLMIntegrator
            
            instances = []
            for i in range(3):
                llm_integrator = RealLLMIntegrator()
                role_manager = RoleManager()
                debate_system = MultiRoleDebateSystem(llm_integrator, role_manager)
                instances.append((llm_integrator, role_manager, debate_system))
            
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = peak_memory - initial_memory
            
            # 清理实例
            instances.clear()
            import gc
            gc.collect()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            perf_duration = time.time() - perf_start
            
            # 性能要求检查
            perf_tests = {
                "memory_usage_reasonable": peak_memory < 500.0,  # 峰值内存 < 500MB
                "memory_increase_controlled": memory_increase < 200.0,  # 内存增长 < 200MB
                "performance_test_fast": perf_duration < 30.0,  # 性能测试 < 30秒
                "memory_cleanup_effective": (peak_memory - final_memory) > (memory_increase * 0.5)  # 内存清理有效
            }
            
            all_passed = all(perf_tests.values())
            ux_score = 9.0 if all_passed and peak_memory < 100.0 else 7.0 if all_passed else 4.0
            
            result.finish(
                passed=all_passed,
                details={
                    "initial_memory_mb": initial_memory,
                    "peak_memory_mb": peak_memory,
                    "final_memory_mb": final_memory,
                    "memory_increase_mb": memory_increase,
                    "performance_test_duration": perf_duration,
                    **perf_tests
                },
                ux_score=ux_score
            )
            
        except Exception as e:
            result.finish(False, str(e), ux_score=0.0)
        
        self.test_results.append(result)
        print(f"✓ 性能要求测试: {'通过' if result.passed else '失败'} (UX: {result.user_experience_score}/10)")
    
    async def test_data_persistence(self):
        """测试数据持久化"""
        result = EndToEndTestResult("数据持久化测试")
        result.start()
        
        try:
            from src.debate_system.debate_flow_definition import DebateSession
            from src.debate_system.debate_state_manager import DebateStateManager
            
            # 创建状态管理器
            state_manager = DebateStateManager()
            
            # 创建测试数据
            test_session = DebateSession(
                title="持久化测试辩论",
                topic="测试数据持久化和恢复功能"
            )
            
            # 测试数据持久化
            persistence_tests = {}
            
            # 保存数据
            saved = await state_manager.create_session(test_session)
            persistence_tests["data_saved"] = saved
            
            # 验证数据存在
            retrieved = await state_manager.get_session(test_session.session_id)
            persistence_tests["data_retrievable"] = retrieved is not None
            persistence_tests["data_integrity"] = retrieved.title == test_session.title if retrieved else False
            
            # 创建快照
            snapshot = await state_manager.create_snapshot(test_session.session_id)
            persistence_tests["snapshot_created"] = snapshot is not None
            
            # 验证快照数据
            if snapshot:
                persistence_tests["snapshot_has_data"] = bool(snapshot.session_state)
                persistence_tests["snapshot_has_checksum"] = bool(snapshot.checksum)
            
            all_passed = all(persistence_tests.values())
            ux_score = 8.0 if all_passed else 4.0
            
            result.finish(
                passed=all_passed,
                details={
                    "session_id": test_session.session_id,
                    "snapshot_id": snapshot.snapshot_id if snapshot else None,
                    **persistence_tests
                },
                ux_score=ux_score
            )
            
        except Exception as e:
            result.finish(False, str(e), ux_score=0.0)
        
        self.test_results.append(result)
        print(f"✓ 数据持久化测试: {'通过' if result.passed else '失败'} (UX: {result.user_experience_score}/10)")
    
    def _generate_test_report(self) -> dict[str, Any]:
        """生成测试报告"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        total_duration = (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0
        
        # 计算平均用户体验评分
        ux_scores = [r.user_experience_score for r in self.test_results if r.user_experience_score > 0]
        average_ux_score = sum(ux_scores) / len(ux_scores) if ux_scores else 0.0
        
        # 端到端测试质量门禁
        quality_gates = {
            "all_core_tests_passed": all(r.passed for r in self.test_results if "系统启动" in r.test_name or "辩论创建" in r.test_name or "LLM集成" in r.test_name),
            "user_experience_acceptable": average_ux_score >= 7.0,
            "performance_requirements_met": all(r.passed for r in self.test_results if "性能要求" in r.test_name),
            "error_handling_robust": all(r.passed for r in self.test_results if "错误处理" in r.test_name),
            "overall_success_rate_high": success_rate >= 90.0
        }
        
        quality_gates["end_to_end_quality_gate_passed"] = all(quality_gates.values())
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": success_rate,
                "total_duration": total_duration,
                "average_ux_score": average_ux_score
            },
            "quality_gates": quality_gates,
            "test_results": [
                {
                    "test_name": r.test_name,
                    "passed": r.passed,
                    "duration": r.duration,
                    "user_experience_score": r.user_experience_score,
                    "error_message": r.error_message,
                    "details": r.details
                }
                for r in self.test_results
            ],
            "timestamp": datetime.now().isoformat()
        }


async def main():
    """主函数"""
    print("🚀 真实多轮辩论系统端到端测试")
    print("=" * 80)
    print("目标: 验证完整用户体验，确保系统可以发布")
    print("=" * 80)
    
    # 创建端到端测试器
    tester = EndToEndTester()
    
    # 运行完整测试套件
    test_report = await tester.run_complete_test_suite()
    
    # 显示测试结果
    print("\n" + "=" * 80)
    print("📊 端到端测试结果摘要")
    print("=" * 80)
    
    summary = test_report["summary"]
    print(f"总测试数: {summary['total_tests']}")
    print(f"通过测试: {summary['passed_tests']}")
    print(f"失败测试: {summary['failed_tests']}")
    print(f"成功率: {summary['success_rate']:.1f}%")
    print(f"平均用户体验评分: {summary['average_ux_score']:.1f}/10")
    print(f"总耗时: {summary['total_duration']:.2f}秒")
    
    # 显示质量门禁结果
    print("\n🚪 端到端质量门禁检查")
    print("-" * 40)
    
    quality_gates = test_report["quality_gates"]
    for gate_name, gate_result in quality_gates.items():
        status = "✅ 通过" if gate_result else "❌ 失败"
        print(f"{gate_name}: {status}")
    
    # 显示失败的测试详情
    failed_tests = [r for r in tester.test_results if not r.passed]
    if failed_tests:
        print("\n❌ 失败测试详情")
        print("-" * 40)
        for test in failed_tests:
            print(f"测试: {test.test_name}")
            print(f"错误: {test.error_message}")
            print(f"用户体验评分: {test.user_experience_score}/10")
            print(f"耗时: {test.duration:.2f}秒")
            print()
    
    # 保存测试报告
    import json
    report_file = Path("end_to_end_test_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(test_report, f, indent=2, ensure_ascii=False)
    
    print(f"📄 详细测试报告已保存到: {report_file}")
    
    # 最终结果
    overall_passed = quality_gates["end_to_end_quality_gate_passed"]
    if overall_passed:
        print("\n🎉 端到端测试全部通过！系统可以发布！")
        print("✅ 用户体验流畅，性能达标，功能完整")
        print(f"✅ 平均用户体验评分: {summary['average_ux_score']:.1f}/10")
        return True
    else:
        print("\n⚠️ 端到端测试未完全通过，建议修复后再发布")
        print("❌ 请检查失败的测试项目并进行修复")
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