#!/usr/bin/env python3
"""协议执行引擎
实现完整的协议执行功能
"""

import logging
import time
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ProtocolStep(BaseModel):
    """协议步骤定义"""

    id: str = Field(..., description="步骤ID")
    name: str = Field(..., description="步骤名称")
    type: str = Field(..., description="步骤类型")
    inputs: dict[str, Any] = Field(default_factory=dict, description="输入参数")
    outputs: dict[str, Any] = Field(default_factory=dict, description="输出参数")
    dependencies: list[str] = Field(default_factory=list, description="依赖步骤")
    timeout: int = Field(default=300, description="超时时间(秒)")
    retry_count: int = Field(default=3, description="重试次数")


class ProtocolDefinition(BaseModel):
    """协议定义"""

    id: str = Field(..., description="协议ID")
    name: str = Field(..., description="协议名称")
    version: str = Field(default="1.0", description="协议版本")
    description: str = Field(default="", description="协议描述")
    steps: list[ProtocolStep] = Field(default_factory=list, description="协议步骤")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class ExecutionResult(BaseModel):
    """执行结果"""

    step_id: str = Field(..., description="步骤ID")
    success: bool = Field(..., description="是否成功")
    output: dict[str, Any] = Field(default_factory=dict, description="输出结果")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: float = Field(..., description="执行时间")
    start_time: float = Field(..., description="开始时间")
    end_time: float = Field(..., description="结束时间")


class ProtocolExecutor:
    """协议执行引擎"""

    def __init__(self):
        self.protocols_dir = Path("protocols")
        self.execution_history: dict[str, list[ExecutionResult]] = {}
        self.active_executions: dict[str, dict[str, Any]] = {}

    async def execute_protocol(
        self,
        protocol_id: str,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """执行协议的主入口"""
        try:
            # 1. 加载协议定义
            protocol = await self.load_protocol(protocol_id)

            # 2. 验证输入参数
            validated_inputs = self.validate_inputs(protocol, inputs)

            # 3. 执行协议步骤
            results = await self.execute_steps(protocol, validated_inputs)

            # 4. 生成执行报告
            success_count = sum(1 for r in results if r.success)
            total_time = sum(r.execution_time for r in results)

            # 5. 返回执行结果
            return {
                "success": success_count == len(results),
                "protocol_id": protocol_id,
                "protocol_name": protocol.name,
                "total_steps": len(results),
                "successful_steps": success_count,
                "failed_steps": len(results) - success_count,
                "total_execution_time": total_time,
                "results": [result.dict() for result in results],
                "execution_time": time.time(),
            }

        except Exception as e:
            logger.error(f"协议执行失败: {e}")
            return {
                "success": False,
                "protocol_id": protocol_id,
                "error": str(e),
                "execution_time": time.time(),
            }

    async def load_protocol(self, protocol_id: str) -> ProtocolDefinition:
        """加载协议定义"""
        try:
            # 查找协议文件
            protocol_file = None
            for file_path in self.protocols_dir.rglob("*.yaml"):
                if protocol_id in file_path.name:
                    protocol_file = file_path
                    break

            if not protocol_file:
                raise FileNotFoundError(f"协议文件未找到: {protocol_id}")

            # 读取协议定义
            with open(protocol_file, encoding="utf-8") as f:
                protocol_data = yaml.safe_load(f)

            # 验证协议定义
            protocol = ProtocolDefinition(**protocol_data)
            logger.info(f"成功加载协议: {protocol.name} (ID: {protocol.id})")
            return protocol

        except Exception as e:
            logger.error(f"加载协议失败: {e}")
            raise

    def validate_inputs(
        self,
        protocol: ProtocolDefinition,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """验证输入参数"""
        validated_inputs = {}

        for step in protocol.steps:
            step_inputs = step.inputs
            for param_name, param_config in step_inputs.items():
                if param_name in inputs:
                    # 验证参数类型和值
                    if self._validate_parameter(param_config, inputs[param_name]):
                        validated_inputs[param_name] = inputs[param_name]
                    else:
                        raise ValueError(f"参数验证失败: {param_name}")
                elif param_config.get("required", False):
                    raise ValueError(f"缺少必需参数: {param_name}")
                else:
                    # 使用默认值
                    validated_inputs[param_name] = param_config.get("default")

        return validated_inputs

    def _validate_parameter(self, param_config: dict[str, Any], value: Any) -> bool:
        """验证单个参数"""
        param_type = param_config.get("type", "string")

        if param_type == "string":
            return isinstance(value, str)
        elif param_type == "number":
            return isinstance(value, (int, float))
        elif param_type == "boolean":
            return isinstance(value, bool)
        elif param_type == "array":
            return isinstance(value, list)
        elif param_type == "object":
            return isinstance(value, dict)
        else:
            return True  # 未知类型，跳过验证

    async def execute_steps(
        self,
        protocol: ProtocolDefinition,
        inputs: dict[str, Any],
    ) -> list[ExecutionResult]:
        """执行协议步骤"""
        results = []
        execution_id = f"{protocol.id}_{int(time.time())}"

        # 初始化执行状态
        self.active_executions[execution_id] = {
            "protocol": protocol,
            "inputs": inputs,
            "status": "running",
            "start_time": time.time(),
        }

        try:
            # 按依赖关系排序步骤
            sorted_steps = self._topological_sort(protocol.steps)

            # 执行每个步骤
            for step in sorted_steps:
                result = await self._execute_single_step(step, inputs, results)
                results.append(result)

                if not result.success:
                    logger.error(f"步骤执行失败: {step.id} - {result.error}")
                    break

            # 更新执行状态
            self.active_executions[execution_id]["status"] = "completed"
            self.active_executions[execution_id]["end_time"] = time.time()

        except Exception as e:
            logger.error(f"协议执行失败: {e}")
            self.active_executions[execution_id]["status"] = "failed"
            self.active_executions[execution_id]["error"] = str(e)

        # 保存执行历史
        self.execution_history[execution_id] = results

        return results

    def _topological_sort(self, steps: list[ProtocolStep]) -> list[ProtocolStep]:
        """拓扑排序，确保依赖步骤先执行"""
        # 构建依赖图
        graph = {step.id: step for step in steps}
        in_degree = {step.id: 0 for step in steps}

        for step in steps:
            for dep in step.dependencies:
                if dep in in_degree:
                    in_degree[step.id] += 1

        # 拓扑排序
        sorted_steps = []
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]

        while queue:
            step_id = queue.pop(0)
            sorted_steps.append(graph[step_id])

            for step in steps:
                if step_id in step.dependencies:
                    in_degree[step.id] -= 1
                    if in_degree[step.id] == 0:
                        queue.append(step.id)

        return sorted_steps

    async def _execute_single_step(
        self,
        step: ProtocolStep,
        inputs: dict[str, Any],
        previous_results: list[ExecutionResult],
    ) -> ExecutionResult:
        """执行单个步骤"""
        start_time = time.time()

        try:
            # 准备步骤输入
            step_inputs = self._prepare_step_inputs(step, inputs, previous_results)

            # 根据步骤类型执行
            if step.type == "llm_call":
                output = await self._execute_llm_step(step, step_inputs)
            elif step.type == "tool_call":
                output = await self._execute_tool_step(step, step_inputs)
            elif step.type == "data_processing":
                output = await self._execute_data_step(step, step_inputs)
            elif step.type == "condition":
                output = await self._execute_condition_step(step, step_inputs)
            else:
                raise ValueError(f"不支持的步骤类型: {step.type}")

            end_time = time.time()

            return ExecutionResult(
                step_id=step.id,
                success=True,
                output=output,
                execution_time=end_time - start_time,
                start_time=start_time,
                end_time=end_time,
            )

        except Exception as e:
            end_time = time.time()
            logger.error(f"步骤执行失败: {step.id} - {e}")

            return ExecutionResult(
                step_id=step.id,
                success=False,
                output={},
                error=str(e),
                execution_time=end_time - start_time,
                start_time=start_time,
                end_time=end_time,
            )

    def _prepare_step_inputs(
        self,
        step: ProtocolStep,
        global_inputs: dict[str, Any],
        previous_results: list[ExecutionResult],
    ) -> dict[str, Any]:
        """准备步骤输入参数"""
        step_inputs = {}

        # 从全局输入获取参数
        for param_name, param_config in step.inputs.items():
            if param_name in global_inputs:
                step_inputs[param_name] = global_inputs[param_name]

        # 从之前步骤的输出获取参数
        for result in previous_results:
            if result.success:
                for output_key, output_value in result.output.items():
                    param_name = f"{result.step_id}.{output_key}"
                    if param_name in step.inputs:
                        step_inputs[param_name] = output_value

        return step_inputs

    async def _execute_llm_step(
        self,
        step: ProtocolStep,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """执行LLM调用步骤"""
        try:
            from src.llm import LLMInteractionModule

            llm = LLMInteractionModule()
            prompt = inputs.get("prompt", "")

            # 调用LLM
            response = await llm.get_llm_response(prompt)

            return {
                "response": response.get("content", ""),
                "type": response.get("type", "text"),
            }

        except Exception as e:
            logger.error(f"LLM步骤执行失败: {e}")
            raise

    async def _execute_tool_step(
        self,
        step: ProtocolStep,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """执行工具调用步骤"""
        try:
            from src.unified_tool_manager import UnifiedToolManager

            tool_manager = UnifiedToolManager()
            tool_name = inputs.get("tool_name", "")
            tool_args = inputs.get("tool_args", {})

            # 调用工具
            result = await tool_manager.execute_tool(tool_name, tool_args)

            return {"result": result, "tool_name": tool_name}

        except Exception as e:
            logger.error(f"工具步骤执行失败: {e}")
            raise

    async def _execute_data_step(
        self,
        step: ProtocolStep,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """执行数据处理步骤"""
        try:
            data = inputs.get("data", {})
            operation = inputs.get("operation", "transform")

            if operation == "transform":
                # 数据转换
                transformed_data = self._transform_data(
                    data,
                    inputs.get("transformation", {}),
                )
                return {"transformed_data": transformed_data}

            elif operation == "filter":
                # 数据过滤
                filtered_data = self._filter_data(
                    data,
                    inputs.get("filter_condition", {}),
                )
                return {"filtered_data": filtered_data}

            elif operation == "aggregate":
                # 数据聚合
                aggregated_data = self._aggregate_data(
                    data,
                    inputs.get("aggregation", {}),
                )
                return {"aggregated_data": aggregated_data}

            else:
                raise ValueError(f"不支持的数据操作: {operation}")

        except Exception as e:
            logger.error(f"数据处理步骤执行失败: {e}")
            raise

    async def _execute_condition_step(
        self,
        step: ProtocolStep,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        """执行条件判断步骤"""
        try:
            condition = inputs.get("condition", "")
            value = inputs.get("value", None)

            # 简单的条件判断
            if condition == "equals":
                result = value == inputs.get("expected", None)
            elif condition == "not_equals":
                result = value != inputs.get("expected", None)
            elif condition == "greater_than":
                result = value > inputs.get("threshold", 0)
            elif condition == "less_than":
                result = value < inputs.get("threshold", 0)
            elif condition == "contains":
                result = inputs.get("expected", "") in str(value)
            else:
                raise ValueError(f"不支持的条件: {condition}")

            return {"condition_result": result, "condition": condition, "value": value}

        except Exception as e:
            logger.error(f"条件步骤执行失败: {e}")
            raise

    def _transform_data(self, data: Any, transformation: dict[str, Any]) -> Any:
        """数据转换"""
        # 简单的数据转换实现
        if isinstance(data, dict):
            return {
                k: v
                for k, v in data.items()
                if k in transformation.get("include_fields", [])
            }
        elif isinstance(data, list):
            return [
                item
                for item in data
                if self._evaluate_filter(item, transformation.get("filter", {}))
            ]
        else:
            return data

    def _filter_data(self, data: Any, filter_condition: dict[str, Any]) -> Any:
        """数据过滤"""
        if isinstance(data, list):
            return [
                item for item in data if self._evaluate_filter(item, filter_condition)
            ]
        else:
            return data if self._evaluate_filter(data, filter_condition) else None

    def _aggregate_data(self, data: Any, aggregation: dict[str, Any]) -> Any:
        """数据聚合"""
        if isinstance(data, list) and data:
            operation = aggregation.get("operation", "count")
            field = aggregation.get("field", None)

            if operation == "count":
                return len(data)
            elif operation == "sum" and field:
                return sum(
                    item.get(field, 0) for item in data if isinstance(item, dict)
                )
            elif operation == "average" and field:
                values = [item.get(field, 0) for item in data if isinstance(item, dict)]
                return sum(values) / len(values) if values else 0
            elif operation == "max" and field:
                return max(
                    item.get(field, 0) for item in data if isinstance(item, dict)
                )
            elif operation == "min" and field:
                return min(
                    item.get(field, 0) for item in data if isinstance(item, dict)
                )

        return data

    def _evaluate_filter(self, item: Any, filter_condition: dict[str, Any]) -> bool:
        """评估过滤条件"""
        if not filter_condition:
            return True

        for field, condition in filter_condition.items():
            if isinstance(item, dict) and field in item:
                value = item[field]
                if not self._evaluate_condition(value, condition):
                    return False

        return True

    def _evaluate_condition(self, value: Any, condition: dict[str, Any]) -> bool:
        """评估单个条件"""
        operator = condition.get("operator", "equals")
        expected = condition.get("value")

        if operator == "equals":
            return value == expected
        elif operator == "not_equals":
            return value != expected
        elif operator == "greater_than":
            return value > expected
        elif operator == "less_than":
            return value < expected
        elif operator == "contains":
            return expected in str(value)
        elif operator == "in":
            return value in expected
        else:
            return True

    def get_execution_status(self, execution_id: str) -> dict[str, Any]:
        """获取执行状态"""
        if execution_id in self.active_executions:
            return self.active_executions[execution_id]
        else:
            return {"status": "not_found"}

    def get_execution_history(self, execution_id: str) -> list[ExecutionResult]:
        """获取执行历史"""
        return self.execution_history.get(execution_id, [])


# 全局协议执行器实例
protocol_executor = ProtocolExecutor()
