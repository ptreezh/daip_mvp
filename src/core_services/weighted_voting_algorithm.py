#!/usr/bin/env python3
"""加权投票共识算法适配器

适配现有的WeightedVotingConsensus算法到统一共识调度器接口。
保持原有的认知多样性计算逻辑，支持专家权重、置信度权重和多样性权重。

算法特点：
- 多维权重：考虑专家度、置信度和认知多样性
- 认知多样性：保护少数派观点，促进创新思维
- 自适应权重：根据上下文动态调整权重分配
- 高精度：适用于需要精确决策的复杂场景

适用场景：
- 专家评审和决策
- 需要考虑多样性的团队决策
- 复杂问题的多角度分析
- 创新和创意评估
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from advanced_consensus_algorithms import ConsensusInput as LegacyConsensusInput
from advanced_consensus_algorithms import ConsensusResult as LegacyConsensusResult

# 导入现有的WeightedVotingConsensus实现
from advanced_consensus_algorithms import WeightedVotingConsensus
from consensus_algorithm_interface import AlgorithmCapabilities, ConsensusAlgorithm, ConsensusContext
from consensus_models import AlgorithmMetadata, AlgorithmType, ConsensusInput, ConsensusResult, ValidationResult


class WeightedVotingAlgorithm(ConsensusAlgorithm):
    """加权投票共识算法适配器
    
    包装现有的WeightedVotingConsensus实现，提供统一接口。
    保持原有的认知多样性计算和多维权重逻辑。
    """

    def __init__(self, configuration: Optional[Dict[str, Any]] = None):
        super().__init__("weighted_voting", configuration)

        # 从配置中获取权重参数
        self.expertise_weight = self.configuration.get("expertise_weight", 0.3)
        self.confidence_weight = self.configuration.get("confidence_weight", 0.4)
        self.diversity_weight = self.configuration.get("diversity_weight", 0.3)

        # 创建底层算法实例
        self._legacy_algorithm = WeightedVotingConsensus(
            expertise_weight=self.expertise_weight,
            confidence_weight=self.confidence_weight,
            diversity_weight=self.diversity_weight
        )

    async def calculate(self,
                       inputs: List[ConsensusInput],
                       context: ConsensusContext) -> ConsensusResult:
        """执行加权投票共识计算
        
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

        # 转换输入格式到遗留格式
        legacy_inputs = self._convert_inputs_to_legacy(inputs)

        # 构建上下文信息
        legacy_context = self._build_legacy_context(context)

        try:
            # 调用遗留算法
            legacy_result = self._legacy_algorithm.calculate_consensus(
                legacy_inputs, legacy_context
            )

            # 转换结果格式
            result = self._convert_result_from_legacy(legacy_result, inputs)

            # 更新执行指标
            context.set_metric("algorithm_end", datetime.now())
            context.set_metric("legacy_algorithm_used", "WeightedVotingConsensus")

            return result

        except Exception as e:
            context.set_metric("algorithm_error", str(e))
            raise RuntimeError(f"加权投票算法执行失败: {e}")

    def _convert_inputs_to_legacy(self, inputs: List[ConsensusInput]) -> List[LegacyConsensusInput]:
        """将统一格式输入转换为遗留格式"""
        legacy_inputs = []

        for inp in inputs:
            # 构建认知档案（如果存在）
            cognitive_profile = None
            if inp.metadata and "cognitive_profile" in inp.metadata:
                cognitive_profile = inp.metadata["cognitive_profile"]

            # 创建遗留格式输入
            legacy_input = LegacyConsensusInput(
                agent_id=inp.agent_id,
                position=inp.position,
                confidence=inp.confidence,
                reasoning=inp.reasoning,
                evidence=inp.evidence or [],
                cognitive_profile=cognitive_profile,
                timestamp=inp.timestamp
            )

            legacy_inputs.append(legacy_input)

        return legacy_inputs

    def _build_legacy_context(self, context: ConsensusContext) -> Optional[Dict[str, Any]]:
        """构建遗留算法的上下文信息"""
        legacy_context = {}

        # 传递配置信息
        if context.configuration:
            legacy_context.update(context.configuration)

        # 传递领域信息（用于专家权重计算）
        if "domain" in context.configuration:
            legacy_context["domain"] = context.configuration["domain"]

        return legacy_context if legacy_context else None

    def _convert_result_from_legacy(self,
                                   legacy_result: LegacyConsensusResult,
                                   original_inputs: List[ConsensusInput]) -> ConsensusResult:
        """将遗留格式结果转换为统一格式"""
        # 构建推理轨迹
        reasoning_trace = {
            "algorithm": "weighted_voting",
            "legacy_algorithm": "WeightedVotingConsensus",
            "weights": legacy_result.reasoning_trace.get("weights", []),
            "method": legacy_result.reasoning_trace.get("method", "weighted_voting"),
            "expertise_weight": self.expertise_weight,
            "confidence_weight": self.confidence_weight,
            "diversity_weight": self.diversity_weight
        }

        # 构建元数据
        metadata = {
            "diversity_score": legacy_result.diversity_score,
            "emergent_insights": legacy_result.emergent_insights,
            "participant_count": legacy_result.participant_count,
            "algorithm_config": self.get_configuration(),
            "cognitive_diversity_preserved": legacy_result.diversity_score > 0.3
        }

        return ConsensusResult(
            consensus_value=legacy_result.consensus_value,
            confidence=legacy_result.confidence_level,
            participants=[inp.agent_id for inp in original_inputs],
            reasoning_trace=reasoning_trace,
            metadata=metadata
        )

    def get_metadata(self) -> AlgorithmMetadata:
        """获取算法元数据"""
        return AlgorithmMetadata(
            name="Weighted Voting Consensus",
            version="1.0.0",
            description="基于多维权重的共识算法，考虑专家度、置信度和认知多样性",
            algorithm_type=AlgorithmType.WEIGHTED_VOTING,
            input_types=["str", "int", "float", "dict", "list"],
            output_types=["str", "float", "dict"],
            complexity="medium",
            accuracy=0.85,
            performance="medium",
            requirements=["cognitive_profile"],
            configuration_schema={
                "expertise_weight": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.3,
                    "description": "专家权重系数"
                },
                "confidence_weight": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.4,
                    "description": "置信度权重系数"
                },
                "diversity_weight": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.3,
                    "description": "多样性权重系数"
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
            min_participants=2,  # 需要至少2个参与者才能计算多样性
            max_participants=None
        )

    def validate_inputs(self, inputs: List[ConsensusInput]) -> ValidationResult:
        """验证输入数据"""
        errors = []
        warnings = []

        if not inputs:
            errors.append("输入列表不能为空")
            return ValidationResult(is_valid=False, errors=errors)

        if len(inputs) < 2:
            warnings.append("参与者少于2个，无法充分发挥多样性权重的作用")

        # 检查置信度
        for i, inp in enumerate(inputs):
            if not (0.0 <= inp.confidence <= 1.0):
                errors.append(f"输入{i}的置信度必须在0.0-1.0之间")

        # 检查认知档案
        cognitive_profile_count = 0
        for inp in inputs:
            if inp.metadata and "cognitive_profile" in inp.metadata:
                cognitive_profile_count += 1

        if cognitive_profile_count == 0:
            warnings.append("没有认知档案信息，将使用默认专家权重和多样性权重")
        elif cognitive_profile_count < len(inputs):
            warnings.append(f"只有{cognitive_profile_count}/{len(inputs)}个输入包含认知档案")

        # 检查权重配置
        weight_sum = self.expertise_weight + self.confidence_weight + self.diversity_weight
        if abs(weight_sum - 1.0) > 0.01:
            warnings.append(f"权重总和({weight_sum:.3f})不等于1.0，将进行归一化")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={
                "total_inputs": len(inputs),
                "cognitive_profiles": cognitive_profile_count,
                "weight_sum": weight_sum
            }
        )

    def validate_configuration(self, config: Dict[str, Any]) -> ValidationResult:
        """验证配置参数"""
        errors = []
        warnings = []

        # 验证权重参数
        weight_params = ["expertise_weight", "confidence_weight", "diversity_weight"]
        weights = []

        for param in weight_params:
            if param in config:
                weight = config[param]
                if not isinstance(weight, (int, float)) or not (0.0 <= weight <= 1.0):
                    errors.append(f"{param}必须是0.0-1.0之间的数值")
                else:
                    weights.append(weight)

        # 检查权重总和
        if len(weights) == 3:
            weight_sum = sum(weights)
            if abs(weight_sum - 1.0) > 0.01:
                warnings.append(f"权重总和({weight_sum:.3f})不等于1.0，建议调整")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def estimate_execution_time(self, request) -> float:
        """估算执行时间"""
        # 加权投票算法需要计算认知距离，时间复杂度较高
        base_time = 0.5  # 基础时间500ms
        input_count = len(request.inputs)

        # 认知多样性计算是O(n²)复杂度
        diversity_factor = (input_count * (input_count - 1)) * 0.01

        # 权重计算因子
        weight_factor = input_count * 0.05

        return base_time + diversity_factor + weight_factor

    def get_health_status(self) -> Dict[str, Any]:
        """获取算法健康状态"""
        base_status = super().get_health_status()

        # 添加特定的健康检查
        base_status.update({
            "legacy_algorithm_available": self._legacy_algorithm is not None,
            "weight_configuration": {
                "expertise_weight": self.expertise_weight,
                "confidence_weight": self.confidence_weight,
                "diversity_weight": self.diversity_weight,
                "sum": self.expertise_weight + self.confidence_weight + self.diversity_weight
            }
        })

        return base_status
