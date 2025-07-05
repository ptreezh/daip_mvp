"""协议驱动的多角色协作编排器
实现真正的流程驱动多AI角色协作调度
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from fastapi import APIRouter, Body, HTTPException

from src.multi_role_chat import MultiRoleChat
from src.protocol_scheduler import ProtocolScheduler
from src.sskg import SSKG
from src.unified_tool_manager import get_unified_tool_manager


class StageStatus(Enum):
    """阶段状态枚举"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class StageResult:
    """阶段执行结果"""

    stage_name: str
    status: StageStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    participants: list[str] = None
    duration: Optional[float] = None


# 全局人工验收队列
pending_acceptance: dict[str, dict[str, Any]] = {}
acceptance_router = APIRouter()


class ProtocolDrivenOrchestrator:
    """协议驱动的多角色协作编排器

    核心功能：
    1. 解析流程协议
    2. 自动调度AI角色
    3. 协调多角色协作
    4. 管理数据流转
    5. 监控协作状态
    """

    def __init__(self, sskg_instance: SSKG, config: Optional[dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        self.sskg_instance = sskg_instance
        self.config = config or {}

        # 核心组件
        self.tool_manager = get_unified_tool_manager(sskg_instance, config)
        self.multi_role_chat = MultiRoleChat(sskg_instance)
        self.protocol_scheduler = None

        # 协作状态
        self.current_protocol = None
        self.stage_results: dict[str, StageResult] = {}
        self.collaboration_history: list[dict[str, Any]] = []

        # 配置参数
        self.max_concurrent_stages = self.config.get("max_concurrent_stages", 3)
        self.stage_timeout = self.config.get("stage_timeout", 300)  # 5分钟
        self.retry_count = self.config.get("retry_count", 3)

    async def execute_protocol(
        self,
        protocol: dict[str, Any],
        external_inputs: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """执行流程协议

        Args:
        ----
            protocol: 流程协议定义
            external_inputs: 外部输入数据

        Returns:
        -------
            执行结果

        """
        try:
            self.logger.info(f"开始执行协议: {protocol.get('workflow_id', 'unknown')}")
            self.current_protocol = protocol
            external_inputs = external_inputs or {}

            # 1. 验证协议
            validation_result = self._validate_protocol(protocol)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "message": "协议验证失败",
                    "errors": validation_result["errors"],
                }

            # 2. 初始化协议调度器
            self.protocol_scheduler = ProtocolScheduler(
                protocol=protocol,
                ai_executor=self._ai_executor,
                human_acceptance_callback=self._human_acceptance_callback,
            )

            # 3. 执行协议
            success = await self._execute_protocol_async(external_inputs)

            if success:
                return {
                    "status": "success",
                    "message": "协议执行完成",
                    "results": self.stage_results,
                    "history": self.collaboration_history,
                }
            else:
                return {
                    "status": "failed",
                    "message": "协议执行失败",
                    "results": self.stage_results,
                    "history": self.collaboration_history,
                }

        except Exception as e:
            self.logger.error(f"协议执行异常: {e}")
            return {"status": "error", "message": f"协议执行异常: {e!s}", "error": str(e)}

    async def _execute_protocol_async(self, external_inputs: dict[str, Any]) -> bool:
        """异步执行协议"""
        try:
            # 使用事件循环执行同步的协议调度器
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                self.protocol_scheduler.run,
                external_inputs,
            )
        except Exception as e:
            self.logger.error(f"异步协议执行失败: {e}")
            return False

    def _validate_protocol(self, protocol: dict[str, Any]) -> dict[str, Any]:
        """验证协议格式和逻辑"""
        errors = []

        # 检查必需字段
        required_fields = ["workflow_id", "description", "stages"]
        for field in required_fields:
            if field not in protocol:
                errors.append(f"缺少必需字段: {field}")

        if "stages" in protocol:
            stages = protocol["stages"]
            if not isinstance(stages, list) or len(stages) == 0:
                errors.append("stages必须是非空列表")
            else:
                # 检查每个阶段
                stage_names = set()
                for i, stage in enumerate(stages):
                    stage_errors = self._validate_stage(stage, i)
                    errors.extend(stage_errors)

                    # 检查阶段名称唯一性
                    stage_name = stage.get("stage_name")
                    if stage_name:
                        if stage_name in stage_names:
                            errors.append(f"阶段名称重复: {stage_name}")
                        stage_names.add(stage_name)

        return {"valid": len(errors) == 0, "errors": errors}

    def _validate_stage(self, stage: dict[str, Any], index: int) -> list[str]:
        """验证单个阶段"""
        errors = []

        # 检查必需字段
        required_fields = ["stage_name", "role", "prompt_template"]
        for field in required_fields:
            if field not in stage:
                errors.append(f"阶段 {index}: 缺少必需字段 {field}")

        # 检查角色格式
        if "role" in stage:
            role = stage["role"]
            if not isinstance(role, str) or not role.strip():
                errors.append(f"阶段 {index}: 角色定义无效")

        return errors

    def _ai_executor(
        self,
        stage: dict[str, Any],
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """AI执行器 - 协议调度器的AI接口

        实现真正的多角色协作：
        1. 解析阶段角色
        2. 分配任务给角色
        3. 协调角色协作
        4. 返回结构化结果
        """
        try:
            stage_name = stage["stage_name"]
            role_description = stage["role"]
            prompt_template = stage["prompt_template"]

            self.logger.info(f"执行阶段: {stage_name}, 角色: {role_description}")

            # 记录阶段开始
            stage_result = StageResult(
                stage_name=stage_name,
                status=StageStatus.RUNNING,
                start_time=datetime.now(),
                participants=[],
            )
            self.stage_results[stage_name] = stage_result

            # 1. 解析角色列表
            roles = self._parse_roles(role_description)
            stage_result.participants = roles

            # 2. 准备输入数据
            formatted_prompt = self._format_prompt(prompt_template, inputs)

            # 3. 执行多角色协作
            collaboration_result = self._execute_multi_role_collaboration(
                stage_name,
                roles,
                formatted_prompt,
                inputs,
            )

            # 4. 记录阶段完成
            stage_result.status = StageStatus.COMPLETED
            stage_result.end_time = datetime.now()
            stage_result.result = collaboration_result
            stage_result.duration = (
                stage_result.end_time - stage_result.start_time
            ).total_seconds()

            # 5. 记录协作历史
            self.collaboration_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "stage": stage_name,
                    "roles": roles,
                    "input": inputs,
                    "result": collaboration_result,
                    "duration": stage_result.duration,
                },
            )

            return {"status": "success", "result": collaboration_result}

        except Exception as e:
            self.logger.error(f"AI执行器异常: {e}")

            # 记录失败状态
            if stage_name in self.stage_results:
                stage_result = self.stage_results[stage_name]
                stage_result.status = StageStatus.FAILED
                stage_result.end_time = datetime.now()
                stage_result.error = str(e)

            return {"status": "error", "error": str(e)}

    def _parse_roles(self, role_description: str) -> list[str]:
        """解析角色描述，支持多角色"""
        # 支持多种分隔符：逗号、顿号、and、&
        import re

        # 清理角色描述
        role_description = role_description.strip()

        # 分割角色
        roles = re.split(r"[,，、]|\s+and\s+|\s*&\s*", role_description)

        # 清理每个角色
        roles = [role.strip() for role in roles if role.strip()]

        return roles

    def _format_prompt(self, prompt_template: str, inputs: dict[str, Any]) -> str:
        """格式化提示模板"""
        try:
            # 简单的字符串格式化
            return prompt_template.format(**inputs)
        except KeyError as e:
            self.logger.warning(f"提示模板格式化失败，缺少变量: {e}")
            return prompt_template
        except Exception as e:
            self.logger.error(f"提示模板格式化异常: {e}")
            return prompt_template

    def _execute_multi_role_collaboration(
        self,
        stage_name: str,
        roles: list[str],
        prompt: str,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """执行多角色协作

        实现真正的流程驱动协作：
        1. 角色能力匹配
        2. 任务分配
        3. 协作协调
        4. 结果聚合
        """
        try:
            self.logger.info(f"开始多角色协作: {stage_name}, 角色: {roles}")

            # 1. 角色能力匹配和加载
            available_roles = self._match_roles(roles)

            if not available_roles:
                # 如果没有找到匹配的角色，使用通用角色
                self.logger.warning("未找到匹配的角色，使用通用角色")
                available_roles = [{"name": "通用专家", "description": "通用AI专家"}]

            # 2. 创建协作会话
            collaboration_session = self.multi_role_chat.create_session(
                session_id=f"{stage_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                roles=available_roles,
                initial_prompt=prompt,
            )

            # 3. 执行协作
            collaboration_result = self.multi_role_chat.execute_collaboration(
                session_id=collaboration_session["session_id"],
                user_input=prompt,
                max_rounds=self.config.get("max_collaboration_rounds", 5),
            )

            # 4. 结构化结果
            structured_result = self._structure_collaboration_result(
                collaboration_result,
                stage_name,
                roles,
            )

            return structured_result

        except Exception as e:
            self.logger.error(f"多角色协作执行失败: {e}")
            raise

    def _match_roles(self, role_names: list[str]) -> list[dict[str, Any]]:
        """匹配角色能力"""
        matched_roles = []

        for role_name in role_names:
            # 从SSKG中搜索角色
            try:
                role_definition = self.sskg_instance.search_role_by_name(role_name)
                if role_definition:
                    matched_roles.append(role_definition)
                else:
                    # 创建临时角色定义
                    matched_roles.append(
                        {
                            "name": role_name,
                            "description": f"临时角色: {role_name}",
                            "capabilities": ["通用分析", "协作讨论"],
                            "expertise": ["通用领域"],
                        },
                    )
            except Exception as e:
                self.logger.warning(f"角色匹配失败 {role_name}: {e}")
                # 创建默认角色
                matched_roles.append(
                    {
                        "name": role_name,
                        "description": f"默认角色: {role_name}",
                        "capabilities": ["通用分析", "协作讨论"],
                        "expertise": ["通用领域"],
                    },
                )

        return matched_roles

    def _structure_collaboration_result(
        self,
        collaboration_result: dict[str, Any],
        stage_name: str,
        roles: list[str],
    ) -> dict[str, Any]:
        """结构化协作结果"""
        return {
            "stage_name": stage_name,
            "participants": roles,
            "collaboration_summary": collaboration_result.get("summary", ""),
            "key_insights": collaboration_result.get("insights", []),
            "recommendations": collaboration_result.get("recommendations", []),
            "consensus": collaboration_result.get("consensus", ""),
            "raw_discussion": collaboration_result.get("discussion", []),
            "timestamp": datetime.now().isoformat(),
        }

    def _human_acceptance_callback(
        self,
        stage_name: str,
        result: dict[str, Any],
    ) -> bool:
        """人工验收回调：流程暂停，等待外部API提交验收结果"""
        self.logger.info(f"人工验收节点: {stage_name}")
        # 生成唯一key
        key = f"{self.current_protocol.get('workflow_id', 'unknown')}::{stage_name}"
        # 挂起到全局队列
        pending_acceptance[key] = {
            "stage_name": stage_name,
            "result": result,
            "accepted": None,
        }
        self.logger.info(f"等待人工验收: {key}")
        # 轮询等待外部验收（可优化为事件/异步通知）
        for _ in range(600):  # 最多等待600秒
            if pending_acceptance[key]["accepted"] is not None:
                accepted = pending_acceptance[key]["accepted"]
                del pending_acceptance[key]
                return accepted
            time.sleep(1)
        self.logger.warning(f"人工验收超时: {key}")
        del pending_acceptance[key]
        return False

    def get_collaboration_status(self) -> dict[str, Any]:
        """获取协作状态"""
        return {
            "current_protocol": self.current_protocol.get("workflow_id")
            if self.current_protocol
            else None,
            "stage_results": {
                name: {
                    "status": result.status.value,
                    "start_time": result.start_time.isoformat(),
                    "end_time": result.end_time.isoformat()
                    if result.end_time
                    else None,
                    "duration": result.duration,
                    "participants": result.participants,
                    "error": result.error,
                }
                for name, result in self.stage_results.items()
            },
            "collaboration_history": self.collaboration_history,
            "total_stages": len(self.stage_results),
            "completed_stages": len(
                [
                    r
                    for r in self.stage_results.values()
                    if r.status == StageStatus.COMPLETED
                ],
            ),
            "failed_stages": len(
                [
                    r
                    for r in self.stage_results.values()
                    if r.status == StageStatus.FAILED
                ],
            ),
        }

    def reset_collaboration(self):
        """重置协作状态"""
        self.current_protocol = None
        self.stage_results.clear()
        self.collaboration_history.clear()
        self.protocol_scheduler = None
        self.logger.info("协作状态已重置")


# 创建全局实例
protocol_orchestrator_instance = None


def get_protocol_orchestrator(
    sskg_instance: SSKG,
    config: Optional[dict[str, Any]] = None,
) -> ProtocolDrivenOrchestrator:
    """获取全局协议编排器实例"""
    global protocol_orchestrator_instance
    if protocol_orchestrator_instance is None:
        protocol_orchestrator_instance = ProtocolDrivenOrchestrator(
            sskg_instance,
            config,
        )
    return protocol_orchestrator_instance


# FastAPI路由：提交人工验收结果
@acceptance_router.post("/accept_stage")
def accept_stage(
    workflow_id: str = Body(...),
    stage_name: str = Body(...),
    accept: bool = Body(...),
):
    key = f"{workflow_id}::{stage_name}"
    if key not in pending_acceptance:
        raise HTTPException(status_code=404, detail="未找到待验收节点")
    pending_acceptance[key]["accepted"] = accept
    return {"success": True, "message": f"验收结果已提交: {accept}"}


# FastAPI路由：查询待验收节点
@acceptance_router.get("/pending_acceptance")
def get_pending_acceptance():
    return {"pending": list(pending_acceptance.keys())}
