#!/usr/bin/env python3
"""工作流共识算法适配器

适配现有的ConsensusNode工作流算法到统一共识调度器接口。
保持与工作流引擎的兼容性，支持加权平均和多数投票逻辑。

算法特点：
- 工作流集成：与现有工作流引擎无缝集成
- 多种方法：支持加权平均、多数投票和综合分析
- 可信度阈值：支持动态配置可信度阈值
- 证据聚合：专门处理聚合证据的共识计算

适用场景：
- 工作流节点中的共识计算
- 事实核查和可信度评估
- 证据聚合后的决策
- 需要与现有工作流兼容的场景
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from consensus_algorithm_interface import AlgorithmCapabilities, ConsensusAlgorithm, ConsensusContext
from consensus_models import AlgorithmMetadata, AlgorithmType, ConsensusInput, ConsensusResult, ValidationResult

from institutional_primitives.base import ExecutionContext

# 导入现有的ConsensusNode实现
from institutional_primitives.consensus_node import ConsensusNode


class WorkflowConsensusAlgorithm(ConsensusAlgorithm):
    """工作流共识算法适配器
    
    包装现有的ConsensusNode实现，提供统一接口。
    保持与工作流引擎的兼容性和现有的共识计算逻辑。
    """

    def __init__(self, configuration: Optional[Dict[str, Any]] = None):
        super().__init__("workflow_consensus", configuration)

        # 从配置中获取参数
        self.consensus_method = self.configuration.get("consensus_method", "weighted_average")
        self.credibility_threshold = self.configuration.get("credibility_threshold", 0.6)
        self.use_synthesis_engine = self.configuration.get("use_synthesis_engine", False)

        # 创建底层ConsensusNode实例
        self._consensus_node = ConsensusNode(
            primitive_id="unified_consensus_adapter",
            config={
                "consensus_method": self.consensus_method,
                "credibility_threshold": self.credibility_threshold,
                "use_synthesis_engine": self.use_synthesis_engine
            }
        )

    async def calculate(self,
                       inputs: List[ConsensusInput],
                       context: ConsensusContext) -> ConsensusResult:
        """执行工作流共识计算
        
        Args:
            inputs: 统一格式的共识输入列表
            context: 执行上下文
            
        Returns:
            统一格式的共识计算结果

        """
        context.set_metric("algorithm_start", datetime.now())

        # 验证输入
        validation = self.validate_inputs(inputs)
        if not validation.is_valid:
            raise ValueError(f"输入验证失败: {validation.errors}")

        # 转换输入格式到工作流格式
        workflow_inputs = self._convert_inputs_to_workflow(inputs)

        # 创建工作流执行上下文
        aggregated_evidence = workflow_inputs.get("aggregated_evidence", {})
        workflow_context = self._create_workflow_context(context, aggregated_evidence)

        try:
            # 调用工作流共识节点
            workflow_result = await self._consensus_node.execute(
                workflow_inputs, workflow_context
            )

            # 转换结果格式
            result = self._convert_result_from_workflow(workflow_result, inputs)

            # 更新执行指标
            context.set_metric("algorithm_end", datetime.now())
            context.set_metric("workflow_algorithm_used", "ConsensusNode")
            context.set_metric("consensus_method", self.consensus_method)

            return result

        except Exception as e:
            context.set_metric("algorithm_error", str(e))
            raise RuntimeError(f"工作流共识算法执行失败: {e}")

    def _convert_inputs_to_workflow(self, inputs: List[ConsensusInput]) -> Dict[str, Any]:
        """将统一格式输入转换为工作流格式"""
        # 检查输入是否已经是聚合证据格式
        if len(inputs) == 1 and isinstance(inputs[0].position, dict) and "aggregated_evidence" in inputs[0].position:
            # 直接使用聚合证据
            return inputs[0].position

        # 否则，将输入转换为聚合证据格式
        aggregated_evidence = {}

        # 根据输入类型处理
        if self._is_fact_evidence_format(inputs):
            # 输入是事实-证据格式
            aggregated_evidence = self._aggregate_fact_evidence(inputs)
        else:
            # 输入是简单共识格式，创建单一事实
            aggregated_evidence = self._create_single_fact_evidence(inputs)

        return {"aggregated_evidence": aggregated_evidence}

    def _is_fact_evidence_format(self, inputs: List[ConsensusInput]) -> bool:
        """检查输入是否为事实-证据格式"""
        # 检查是否有fact_id和evidence_type等字段
        for inp in inputs:
            if isinstance(inp.metadata, dict):
                if "fact_id" in inp.metadata and "evidence_type" in inp.metadata:
                    return True
        return False

    def _aggregate_fact_evidence(self, inputs: List[ConsensusInput]) -> Dict[str, Any]:
        """聚合事实-证据格式的输入"""
        facts = {}

        for inp in inputs:
            fact_id = inp.metadata.get("fact_id", "default_fact")
            evidence_type = inp.metadata.get("evidence_type", "neutral")

            if fact_id not in facts:
                facts[fact_id] = {
                    "fact_content": inp.metadata.get("fact_content", str(inp.position)),
                    "supporting_count": 0,
                    "challenging_count": 0,
                    "neutral_count": 0,
                    "supporting_score": 0.0,
                    "challenging_score": 0.0,
                    "neutral_score": 0.0,
                    "evidence_summary": []
                }

            # 累积证据
            if evidence_type == "supporting":
                facts[fact_id]["supporting_count"] += 1
                facts[fact_id]["supporting_score"] += inp.confidence
            elif evidence_type == "challenging":
                facts[fact_id]["challenging_count"] += 1
                facts[fact_id]["challenging_score"] += inp.confidence
            else:
                facts[fact_id]["neutral_count"] += 1
                facts[fact_id]["neutral_score"] += inp.confidence

            # 添加证据摘要
            if inp.reasoning:
                facts[fact_id]["evidence_summary"].append(f"{evidence_type}: {inp.reasoning}")

        # 转换证据摘要为字符串
        for fact_id in facts:
            facts[fact_id]["evidence_summary"] = "; ".join(facts[fact_id]["evidence_summary"])

        return facts

    def _create_single_fact_evidence(self, inputs: List[ConsensusInput]) -> Dict[str, Any]:
        """为简单共识输入创建单一事实证据"""
        fact_id = "consensus_fact"

        # 分析输入的立场分布
        position_counts = {}
        position_scores = {}

        for inp in inputs:
            position = str(inp.position)
            if position not in position_counts:
                position_counts[position] = 0
                position_scores[position] = 0.0

            position_counts[position] += 1
            position_scores[position] += inp.confidence

        # 确定主要立场和对立立场
        sorted_positions = sorted(position_counts.items(), key=lambda x: x[1], reverse=True)

        if len(sorted_positions) >= 2:
            # 有对立观点
            main_position = sorted_positions[0][0]
            opposing_position = sorted_positions[1][0]

            supporting_count = position_counts[main_position]
            challenging_count = position_counts[opposing_position]
            neutral_count = sum(count for pos, count in sorted_positions[2:])

            supporting_score = position_scores[main_position]
            challenging_score = position_scores[opposing_position]
            neutral_score = sum(position_scores[pos] for pos, _ in sorted_positions[2:])
        else:
            # 只有一种观点
            main_position = sorted_positions[0][0] if sorted_positions else "unknown"
            supporting_count = len(inputs)
            challenging_count = 0
            neutral_count = 0

            supporting_score = sum(inp.confidence for inp in inputs)
            challenging_score = 0.0
            neutral_score = 0.0

        # 创建证据摘要
        evidence_summary = []
        for inp in inputs:
            if inp.reasoning:
                evidence_summary.append(f"{inp.agent_id}: {inp.reasoning}")

        # 创建聚合证据和提取事实
        aggregated_evidence = {
            fact_id: {
                "fact_content": main_position,  # 直接使用主要立场作为事实内容
                "supporting_count": supporting_count,
                "challenging_count": challenging_count,
                "neutral_count": neutral_count,
                "supporting_score": supporting_score,
                "challenging_score": challenging_score,
                "neutral_score": neutral_score,
                "evidence_summary": "; ".join(evidence_summary)
            }
        }

        return aggregated_evidence

    def _create_workflow_context(self, context: ConsensusContext, aggregated_evidence: Dict[str, Any] = None) -> ExecutionContext:
        """创建工作流执行上下文"""
        workflow_context = ExecutionContext(
            execution_id=f"consensus_{context.session_id}",
            workflow_id="unified_consensus_workflow",
            node_id="consensus_adapter"
        )

        # 传递服务
        if context.services:
            workflow_context.services = context.services

        # 传递配置
        if context.configuration:
            workflow_context.config = context.configuration

        # 创建提取事实信息，以便ConsensusNode能正确获取fact_content
        if aggregated_evidence:
            extracted_facts = []
            for fact_id, evidence_data in aggregated_evidence.items():
                extracted_facts.append({
                    "id": fact_id,
                    "content": evidence_data.get("fact_content", fact_id)
                })
            workflow_context.state["extracted_facts"] = extracted_facts

        return workflow_context

    def _convert_result_from_workflow(self,
                                     workflow_result: Dict[str, Any],
                                     original_inputs: List[ConsensusInput]) -> ConsensusResult:
        """将工作流格式结果转换为统一格式"""
        if not workflow_result.get("success", False):
            raise RuntimeError(f"工作流执行失败: {workflow_result.get('error', 'Unknown error')}")

        credibility_scores = workflow_result.get("credibility_scores", {})
        consensus_results = workflow_result.get("consensus_results", {})

        # 确定最终共识值
        if len(credibility_scores) == 1:
            # 单一事实，返回事实内容而不是可信度分数
            fact_id = list(credibility_scores.keys())[0]
            best_fact_result = consensus_results.get(fact_id, {})
            consensus_value = best_fact_result.get("fact_content", fact_id)
            confidence = credibility_scores[fact_id]
        else:
            # 多个事实，返回最高可信度的事实
            best_fact_id = max(credibility_scores, key=credibility_scores.get)
            best_fact_result = consensus_results.get(best_fact_id, {})
            consensus_value = best_fact_result.get("fact_content", best_fact_id)
            confidence = credibility_scores[best_fact_id]

        # 构建推理轨迹
        reasoning_trace = {
            "algorithm": "workflow_consensus",
            "workflow_algorithm": "ConsensusNode",
            "consensus_method": self.consensus_method,
            "credibility_threshold": self.credibility_threshold,
            "facts_processed": len(credibility_scores),
            "facts_needing_revision": len(workflow_result.get("facts_needing_revision", []))
        }

        # 构建元数据
        metadata = {
            "credibility_scores": credibility_scores,
            "consensus_results": consensus_results,
            "facts_needing_revision": workflow_result.get("facts_needing_revision", []),
            "facts_processed": len(credibility_scores),
            "algorithm_config": self.get_configuration(),
            "workflow_compatible": True,
            "evidence_aggregated": True
        }

        return ConsensusResult(
            consensus_value=consensus_value,
            confidence=confidence,
            participants=[inp.agent_id for inp in original_inputs],
            reasoning_trace=reasoning_trace,
            metadata=metadata
        )

    def get_metadata(self) -> AlgorithmMetadata:
        """获取算法元数据"""
        return AlgorithmMetadata(
            name="Workflow Consensus",
            version="1.0.0",
            description="基于工作流的共识算法，支持加权平均和多数投票，与现有工作流引擎兼容",
            algorithm_type=AlgorithmType.WORKFLOW_CONSENSUS,
            input_types=["str", "int", "float", "dict", "list"],
            output_types=["str", "float", "dict"],
            complexity="medium",
            accuracy=0.82,
            performance="medium",
            requirements=["workflow_engine"],
            configuration_schema={
                "consensus_method": {
                    "type": "string",
                    "enum": ["weighted_average", "majority_vote", "synthesis"],
                    "default": "weighted_average",
                    "description": "共识计算方法"
                },
                "credibility_threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.6,
                    "description": "可信度阈值"
                },
                "use_synthesis_engine": {
                    "type": "boolean",
                    "default": False,
                    "description": "是否使用综合分析引擎"
                }
            }
        )

    def get_capabilities(self) -> AlgorithmCapabilities:
        """获取算法能力描述"""
        return AlgorithmCapabilities(
            supported_input_types={"str", "int", "float", "dict", "list"},
            supported_output_types={"str", "float", "dict"},
            requires_reasoning=False,
            requires_evidence=False,
            supports_async=True,
            min_participants=1,
            max_participants=None
        )

    def validate_inputs(self, inputs: List[ConsensusInput]) -> ValidationResult:
        """验证输入数据"""
        errors = []
        warnings = []

        if not inputs:
            errors.append("输入列表不能为空")
            return ValidationResult(is_valid=False, errors=errors)

        # 检查置信度
        for i, inp in enumerate(inputs):
            if not (0.0 <= inp.confidence <= 1.0):
                errors.append(f"输入{i}的置信度必须在0.0-1.0之间")

        # 检查是否为事实-证据格式
        fact_evidence_format = self._is_fact_evidence_format(inputs)
        if fact_evidence_format:
            # 验证事实-证据格式的完整性
            fact_ids = set()
            for inp in inputs:
                if isinstance(inp.metadata, dict):
                    fact_id = inp.metadata.get("fact_id")
                    evidence_type = inp.metadata.get("evidence_type")

                    if not fact_id:
                        warnings.append("某些输入缺少fact_id，将使用默认值")
                    else:
                        fact_ids.add(fact_id)

                    if evidence_type not in ["supporting", "challenging", "neutral"]:
                        warnings.append(f"未知的证据类型: {evidence_type}")

            if len(fact_ids) > 10:
                warnings.append(f"事实数量较多({len(fact_ids)})，可能影响性能")

        # 检查综合分析引擎要求
        if self.use_synthesis_engine:
            warnings.append("启用了综合分析引擎，需要确保synthesis_engine服务可用")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={
                "total_inputs": len(inputs),
                "fact_evidence_format": fact_evidence_format,
                "unique_facts": len(set(inp.metadata.get("fact_id", "default")
                                      for inp in inputs if isinstance(inp.metadata, dict))),
                "consensus_method": self.consensus_method
            }
        )

    def validate_configuration(self, config: Dict[str, Any]) -> ValidationResult:
        """验证配置参数"""
        errors = []
        warnings = []

        # 验证共识方法
        if "consensus_method" in config:
            method = config["consensus_method"]
            valid_methods = ["weighted_average", "majority_vote", "synthesis"]
            if method not in valid_methods:
                errors.append(f"consensus_method必须是{valid_methods}之一")

        # 验证可信度阈值
        if "credibility_threshold" in config:
            threshold = config["credibility_threshold"]
            if not isinstance(threshold, (int, float)) or not (0.0 <= threshold <= 1.0):
                errors.append("credibility_threshold必须是0.0-1.0之间的数值")

        # 验证综合分析引擎设置
        if "use_synthesis_engine" in config:
            use_synthesis = config["use_synthesis_engine"]
            if not isinstance(use_synthesis, bool):
                errors.append("use_synthesis_engine必须是布尔值")
            elif use_synthesis:
                warnings.append("启用综合分析引擎需要额外的服务依赖")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def estimate_execution_time(self, request) -> float:
        """估算执行时间"""
        # 工作流算法需要更多时间进行证据聚合和分析
        base_time = 0.8  # 基础时间800ms
        input_count = len(request.inputs)

        # 证据聚合因子
        aggregation_factor = input_count * 0.03

        # 方法复杂度因子
        method_factors = {
            "weighted_average": 1.0,
            "majority_vote": 0.8,
            "synthesis": 2.0  # 综合分析需要更多时间
        }
        method_factor = method_factors.get(self.consensus_method, 1.0)

        return (base_time + aggregation_factor) * method_factor

    def get_health_status(self) -> Dict[str, Any]:
        """获取算法健康状态"""
        base_status = super().get_health_status()

        # 添加特定的健康检查
        base_status.update({
            "consensus_node_available": self._consensus_node is not None,
            "workflow_configuration": {
                "consensus_method": self.consensus_method,
                "credibility_threshold": self.credibility_threshold,
                "use_synthesis_engine": self.use_synthesis_engine
            },
            "workflow_compatible": True
        })

        return base_status
