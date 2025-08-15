#!/usr/bin/env python3
"""简单多数投票算法适配器

实现简单多数投票共识算法，适配统一共识调度器接口。
这是最基础的共识算法，基于"少数服从多数"的原则。

算法特点：
- 简单快速：O(n)时间复杂度
- 适用于分类决策：支持字符串和数值投票
- 无权重考虑：每个参与者权重相等
- 高可用性：最少1个参与者即可工作

适用场景：
- 简单的是/否决策
- 分类选择问题
- 快速决策需求
- 参与者权重相等的场景
"""

from collections import Counter
from datetime import datetime
from typing import Any, Optional

from consensus_algorithm_interface import AlgorithmCapabilities, ConsensusAlgorithm, ConsensusContext
from consensus_models import AlgorithmMetadata, AlgorithmType, ConsensusInput, ConsensusResult, ValidationResult


class SimpleMajorityAlgorithm(ConsensusAlgorithm):
    """简单多数投票算法实现
    
    基于"少数服从多数"原则的共识算法。
    对于分类问题，选择得票最多的选项；
    对于数值问题，计算简单平均值。
    """
    
    def __init__(self, configuration: Optional[dict[str, Any]] = None):
        super().__init__("simple_majority", configuration)
        
        # 配置参数
        self.tie_breaking_method = self.configuration.get("tie_breaking_method", "first")
        self.min_confidence_threshold = self.configuration.get("min_confidence_threshold", 0.0)
        self.numerical_aggregation = self.configuration.get("numerical_aggregation", "mean")
        
    async def calculate(self, 
                       inputs: list[ConsensusInput], 
                       context: ConsensusContext) -> ConsensusResult:
        """执行简单多数投票共识计算
        
        Args:
            inputs: 共识输入列表
            context: 执行上下文
            
        Returns:
            共识计算结果
        """
        context.set_metric("algorithm_start", datetime.now())
        
        # 验证输入
        validation = self.validate_inputs(inputs)
        if not validation.is_valid:
            raise ValueError(f"输入验证失败: {validation.errors}")
        
        # 过滤低置信度输入
        filtered_inputs = [
            inp for inp in inputs 
            if inp.confidence >= self.min_confidence_threshold
        ]
        
        if not filtered_inputs:
            raise ValueError("没有满足最低置信度要求的输入")
        
        # 根据输入类型选择处理方法
        first_position = filtered_inputs[0].position
        
        if isinstance(first_position, str):
            consensus_value, confidence = await self._calculate_categorical_consensus(
                filtered_inputs, context
            )
        elif isinstance(first_position, (int, float)):
            consensus_value, confidence = await self._calculate_numerical_consensus(
                filtered_inputs, context
            )
        else:
            # 复杂类型，转换为字符串处理
            consensus_value, confidence = await self._calculate_complex_consensus(
                filtered_inputs, context
            )
        
        # 构建推理轨迹
        reasoning_trace = {
            "algorithm": "simple_majority",
            "method": self._get_method_name(first_position),
            "total_inputs": len(inputs),
            "filtered_inputs": len(filtered_inputs),
            "tie_breaking": self.tie_breaking_method,
            "confidence_threshold": self.min_confidence_threshold
        }
        
        # 构建结果元数据
        metadata = {
            "execution_time": context.get_execution_time(),
            "algorithm_config": self.get_configuration(),
            "input_types": [type(inp.position).__name__ for inp in filtered_inputs]
        }
        
        context.set_metric("algorithm_end", datetime.now())
        
        return ConsensusResult(
            consensus_value=consensus_value,
            confidence=confidence,
            participants=[inp.agent_id for inp in filtered_inputs],
            reasoning_trace=reasoning_trace,
            metadata=metadata
        )
    
    async def _calculate_categorical_consensus(self, 
                                             inputs: list[ConsensusInput],
                                             context: ConsensusContext) -> tuple[str, float]:
        """计算分类共识"""
        # 统计每个选项的票数
        vote_counts = Counter()
        confidence_sums = {}
        
        for inp in inputs:
            position = str(inp.position)
            vote_counts[position] += 1
            
            if position in confidence_sums:
                confidence_sums[position] += inp.confidence
            else:
                confidence_sums[position] = inp.confidence
        
        # 找到得票最多的选项
        max_votes = max(vote_counts.values())
        winners = [pos for pos, votes in vote_counts.items() if votes == max_votes]
        
        # 处理平票情况
        if len(winners) > 1:
            consensus_value = self._break_tie(winners, confidence_sums, inputs)
        else:
            consensus_value = winners[0]
        
        # 计算置信度
        winner_votes = vote_counts[consensus_value]
        total_votes = len(inputs)
        vote_confidence = winner_votes / total_votes
        
        # 考虑参与者的平均置信度
        winner_inputs = [inp for inp in inputs if str(inp.position) == consensus_value]
        avg_participant_confidence = sum(inp.confidence for inp in winner_inputs) / len(winner_inputs)
        
        # 综合置信度
        final_confidence = (vote_confidence + avg_participant_confidence) / 2
        
        context.set_metric("categorical_stats", {
            "vote_counts": dict(vote_counts),
            "winner_votes": winner_votes,
            "total_votes": total_votes,
            "tie_occurred": len(winners) > 1
        })
        
        return consensus_value, final_confidence
    
    async def _calculate_numerical_consensus(self, 
                                           inputs: list[ConsensusInput],
                                           context: ConsensusContext) -> tuple[float, float]:
        """计算数值共识"""
        values = [float(inp.position) for inp in inputs]
        confidences = [inp.confidence for inp in inputs]
        
        if self.numerical_aggregation == "mean":
            consensus_value = sum(values) / len(values)
        elif self.numerical_aggregation == "median":
            sorted_values = sorted(values)
            n = len(sorted_values)
            if n % 2 == 0:
                consensus_value = (sorted_values[n//2-1] + sorted_values[n//2]) / 2
            else:
                consensus_value = sorted_values[n//2]
        elif self.numerical_aggregation == "weighted_mean":
            # 使用置信度作为权重
            weighted_sum = sum(v * c for v, c in zip(values, confidences, strict=False))
            weight_sum = sum(confidences)
            consensus_value = weighted_sum / weight_sum if weight_sum > 0 else sum(values) / len(values)
        else:
            consensus_value = sum(values) / len(values)  # 默认使用均值
        
        # 计算置信度（基于数值分散程度）
        variance = sum((v - consensus_value) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5
        
        # 标准化标准差到0-1范围（假设合理的数值范围）
        value_range = max(values) - min(values) if len(set(values)) > 1 else 1.0
        normalized_std = min(std_dev / (value_range + 1e-6), 1.0)
        
        # 置信度与分散程度成反比
        dispersion_confidence = 1.0 - normalized_std
        
        # 考虑参与者平均置信度
        avg_participant_confidence = sum(confidences) / len(confidences)
        
        # 综合置信度
        final_confidence = (dispersion_confidence + avg_participant_confidence) / 2
        
        context.set_metric("numerical_stats", {
            "consensus_value": consensus_value,
            "variance": variance,
            "std_dev": std_dev,
            "value_range": value_range,
            "aggregation_method": self.numerical_aggregation
        })
        
        return consensus_value, final_confidence
    
    async def _calculate_complex_consensus(self, 
                                         inputs: list[ConsensusInput],
                                         context: ConsensusContext) -> tuple[Any, float]:
        """计算复杂类型共识"""
        # 将复杂类型转换为字符串进行处理
        string_inputs = []
        for inp in inputs:
            string_input = ConsensusInput(
                agent_id=inp.agent_id,
                position=str(inp.position),
                confidence=inp.confidence,
                reasoning=inp.reasoning,
                evidence=inp.evidence,
                metadata=inp.metadata,
                timestamp=inp.timestamp
            )
            string_inputs.append(string_input)
        
        # 使用分类方法处理
        consensus_str, confidence = await self._calculate_categorical_consensus(
            string_inputs, context
        )
        
        # 尝试恢复原始类型
        try:
            # 找到原始输入中匹配的项
            for inp in inputs:
                if str(inp.position) == consensus_str:
                    return inp.position, confidence
        except:
            pass
        
        # 如果无法恢复，返回字符串
        return consensus_str, confidence
    
    def _break_tie(self, 
                   tied_options: list[str], 
                   confidence_sums: dict[str, float],
                   inputs: list[ConsensusInput]) -> str:
        """处理平票情况"""
        if self.tie_breaking_method == "first":
            # 返回第一个出现的选项
            for inp in inputs:
                if str(inp.position) in tied_options:
                    return str(inp.position)
        
        elif self.tie_breaking_method == "highest_confidence":
            # 返回总置信度最高的选项
            return max(tied_options, key=lambda x: confidence_sums.get(x, 0))
        
        elif self.tie_breaking_method == "random":
            # 随机选择（为了确定性，使用第一个）
            return tied_options[0]
        
        # 默认返回第一个
        return tied_options[0]
    
    def _get_method_name(self, position: Any) -> str:
        """获取处理方法名称"""
        if isinstance(position, str):
            return "categorical"
        elif isinstance(position, (int, float)):
            return "numerical"
        else:
            return "complex"
    
    def get_metadata(self) -> AlgorithmMetadata:
        """获取算法元数据"""
        return AlgorithmMetadata(
            name="Simple Majority Voting",
            version="1.0.0",
            description="基于简单多数投票的共识算法，支持分类和数值决策",
            algorithm_type=AlgorithmType.SIMPLE_MAJORITY,
            input_types=["str", "int", "float", "dict", "list"],
            output_types=["str", "float", "dict"],
            complexity="low",
            accuracy=0.7,
            performance="fast",
            requirements=[],
            configuration_schema={
                "tie_breaking_method": {
                    "type": "string",
                    "enum": ["first", "highest_confidence", "random"],
                    "default": "first",
                    "description": "平票时的处理方法"
                },
                "min_confidence_threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.0,
                    "description": "最低置信度阈值"
                },
                "numerical_aggregation": {
                    "type": "string",
                    "enum": ["mean", "median", "weighted_mean"],
                    "default": "mean",
                    "description": "数值聚合方法"
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
    
    def validate_inputs(self, inputs: list[ConsensusInput]) -> ValidationResult:
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
        
        # 检查位置数据类型一致性
        position_types = set(type(inp.position).__name__ for inp in inputs)
        if len(position_types) > 1:
            warnings.append(f"输入包含多种数据类型: {position_types}")
        
        # 检查是否有足够的有效输入
        valid_inputs = [inp for inp in inputs if inp.confidence >= self.min_confidence_threshold]
        if not valid_inputs:
            errors.append(f"没有满足最低置信度要求({self.min_confidence_threshold})的输入")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={
                "total_inputs": len(inputs),
                "valid_inputs": len(valid_inputs),
                "position_types": list(position_types)
            }
        )
    
    def validate_configuration(self, config: dict[str, Any]) -> ValidationResult:
        """验证配置参数"""
        errors = []
        warnings = []
        
        # 验证tie_breaking_method
        if "tie_breaking_method" in config:
            valid_methods = ["first", "highest_confidence", "random"]
            if config["tie_breaking_method"] not in valid_methods:
                errors.append(f"tie_breaking_method必须是{valid_methods}之一")
        
        # 验证min_confidence_threshold
        if "min_confidence_threshold" in config:
            threshold = config["min_confidence_threshold"]
            if not isinstance(threshold, (int, float)) or not (0.0 <= threshold <= 1.0):
                errors.append("min_confidence_threshold必须是0.0-1.0之间的数值")
        
        # 验证numerical_aggregation
        if "numerical_aggregation" in config:
            valid_methods = ["mean", "median", "weighted_mean"]
            if config["numerical_aggregation"] not in valid_methods:
                errors.append(f"numerical_aggregation必须是{valid_methods}之一")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def estimate_execution_time(self, request) -> float:
        """估算执行时间"""
        # 简单多数投票算法执行时间很短
        base_time = 0.1  # 基础时间100ms
        input_factor = len(request.inputs) * 0.01  # 每个输入增加10ms
        return base_time + input_factor