#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贝叶斯共识算法适配器

适配现有的BayesianConsensus算法到统一共识调度器接口。
保持贝叶斯更新的数学逻辑，支持先验强度的配置化。

算法特点：
- 贝叶斯更新：基于证据强度更新信念
- 先验知识：支持先验强度配置
- 精度加权：使用置信度作为精度权重
- 概率推理：提供概率性的共识结果

适用场景：
- 不确定性决策
- 证据累积分析
- 概率推理问题
- 需要考虑先验知识的场景
"""

import asyncio
import math
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime

from consensus_algorithm_interface import (
    ConsensusAlgorithm, ConsensusContext, AlgorithmCapabilities
)
from consensus_models import (
    ConsensusInput, ConsensusResult, AlgorithmMetadata, 
    ValidationResult, AlgorithmType
)

# 导入现有的BayesianConsensus实现
from advanced_consensus_algorithms import (
    BayesianConsensus, ConsensusInput as LegacyConsensusInput,
    ConsensusResult as LegacyConsensusResult
)


class BayesianAlgorithm(ConsensusAlgorithm):
    """
    贝叶斯共识算法适配器
    
    包装现有的BayesianConsensus实现，提供统一接口。
    保持贝叶斯更新的数学逻辑和先验强度配置。
    """
    
    def __init__(self, configuration: Optional[Dict[str, Any]] = None):
        super().__init__("bayesian_consensus", configuration)
        
        # 从配置中获取先验强度参数
        self.prior_strength = self.configuration.get("prior_strength", 1.0)
        
        # 创建底层算法实例
        self._legacy_algorithm = BayesianConsensus(
            prior_strength=self.prior_strength
        )
        
    async def calculate(self, 
                       inputs: List[ConsensusInput], 
                       context: ConsensusContext) -> ConsensusResult:
        """
        执行贝叶斯共识计算
        
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
            context.set_metric("legacy_algorithm_used", "BayesianConsensus")
            context.set_metric("prior_strength", self.prior_strength)
            
            return result
            
        except Exception as e:
            context.set_metric("algorithm_error", str(e))
            raise RuntimeError(f"贝叶斯共识算法执行失败: {e}")
    
    def _convert_inputs_to_legacy(self, inputs: List[ConsensusInput]) -> List[LegacyConsensusInput]:
        """将统一格式输入转换为遗留格式"""
        legacy_inputs = []
        
        for inp in inputs:
            # 创建遗留格式输入
            legacy_input = LegacyConsensusInput(
                agent_id=inp.agent_id,
                position=inp.position,
                confidence=inp.confidence,
                reasoning=inp.reasoning,
                evidence=inp.evidence or [],
                cognitive_profile=None,  # 贝叶斯算法不需要认知档案
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
        
        # 传递先验强度信息
        legacy_context["prior_strength"] = self.prior_strength
        
        return legacy_context if legacy_context else None
    
    def _convert_result_from_legacy(self, 
                                   legacy_result: LegacyConsensusResult,
                                   original_inputs: List[ConsensusInput]) -> ConsensusResult:
        """将遗留格式结果转换为统一格式"""
        
        # 构建推理轨迹
        reasoning_trace = {
            "algorithm": "bayesian_consensus",
            "legacy_algorithm": "BayesianConsensus",
            "method": legacy_result.reasoning_trace.get("method", "bayesian_updating"),
            "prior_strength": self.prior_strength,
            "bayesian_update_applied": True
        }
        
        # 构建元数据
        metadata = {
            "diversity_score": legacy_result.diversity_score,
            "emergent_insights": legacy_result.emergent_insights,
            "participant_count": legacy_result.participant_count,
            "algorithm_config": self.get_configuration(),
            "bayesian_properties": {
                "prior_strength": self.prior_strength,
                "evidence_based": True,
                "probabilistic": True
            }
        }
        
        # 添加数据类型特定的元数据
        if original_inputs:
            first_position = original_inputs[0].position
            if isinstance(first_position, (int, float)):
                metadata["consensus_type"] = "numerical_bayesian"
                metadata["precision_weighted"] = True
            else:
                metadata["consensus_type"] = "categorical_bayesian"
                metadata["evidence_aggregated"] = True
        
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
            name="Bayesian Consensus",
            version="1.0.0",
            description="基于贝叶斯更新的共识算法，支持证据累积和先验知识",
            algorithm_type=AlgorithmType.BAYESIAN_CONSENSUS,
            input_types=["str", "int", "float", "dict"],
            output_types=["str", "float", "dict"],
            complexity="medium",
            accuracy=0.88,
            performance="medium",
            requirements=["confidence_scores"],
            configuration_schema={
                "prior_strength": {
                    "type": "number",
                    "minimum": 0.1,
                    "maximum": 10.0,
                    "default": 1.0,
                    "description": "先验强度，控制先验知识的影响程度"
                }
            }
        )
    
    def get_capabilities(self) -> AlgorithmCapabilities:
        """获取算法能力描述"""
        return AlgorithmCapabilities(
            supported_input_types={"str", "int", "float", "dict"},
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
        
        # 检查置信度（贝叶斯算法特别依赖置信度）
        low_confidence_count = 0
        for i, inp in enumerate(inputs):
            if not (0.0 <= inp.confidence <= 1.0):
                errors.append(f"输入{i}的置信度必须在0.0-1.0之间")
            elif inp.confidence < 0.3:
                low_confidence_count += 1
        
        if low_confidence_count > len(inputs) * 0.5:
            warnings.append(f"超过一半的输入置信度较低(<0.3)，可能影响贝叶斯更新效果")
        
        # 检查数据类型一致性（贝叶斯算法对类型敏感）
        position_types = set(type(inp.position).__name__ for inp in inputs)
        if len(position_types) > 1:
            warnings.append(f"输入包含多种数据类型: {position_types}，将使用分类方法处理")
        
        # 检查数值范围（对于数值输入）
        if inputs and isinstance(inputs[0].position, (int, float)):
            positions = [inp.position for inp in inputs if isinstance(inp.position, (int, float))]
            if positions:
                value_range = max(positions) - min(positions)
                if value_range == 0:
                    warnings.append("所有数值输入相同，贝叶斯更新效果有限")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metadata={
                "total_inputs": len(inputs),
                "low_confidence_inputs": low_confidence_count,
                "position_types": list(position_types),
                "prior_strength": self.prior_strength
            }
        )
    
    def validate_configuration(self, config: Dict[str, Any]) -> ValidationResult:
        """验证配置参数"""
        errors = []
        warnings = []
        
        # 验证先验强度
        if "prior_strength" in config:
            prior_strength = config["prior_strength"]
            if not isinstance(prior_strength, (int, float)):
                errors.append("prior_strength必须是数值类型")
            elif prior_strength <= 0:
                errors.append("prior_strength必须大于0")
            elif prior_strength > 10:
                warnings.append("prior_strength过大(>10)可能导致先验知识过度影响结果")
            elif prior_strength < 0.1:
                warnings.append("prior_strength过小(<0.1)可能导致结果不稳定")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def estimate_execution_time(self, request) -> float:
        """估算执行时间"""
        # 贝叶斯算法需要进行精度计算和概率更新
        base_time = 0.3  # 基础时间300ms
        input_count = len(request.inputs)
        
        # 贝叶斯更新的计算复杂度
        bayesian_factor = input_count * 0.02
        
        # 先验强度影响计算时间
        prior_factor = self.prior_strength * 0.01
        
        return base_time + bayesian_factor + prior_factor
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取算法健康状态"""
        base_status = super().get_health_status()
        
        # 添加特定的健康检查
        base_status.update({
            "legacy_algorithm_available": self._legacy_algorithm is not None,
            "prior_strength": self.prior_strength,
            "bayesian_properties": {
                "supports_numerical": True,
                "supports_categorical": True,
                "evidence_based": True,
                "probabilistic_output": True
            }
        })
        
        return base_status
    
    def get_convergence_info(self, inputs: List[ConsensusInput]) -> Dict[str, Any]:
        """获取贝叶斯收敛信息"""
        if not inputs:
            return {"convergence_possible": False, "reason": "no_inputs"}
        
        # 分析收敛可能性
        confidence_variance = 0
        if len(inputs) > 1:
            confidences = [inp.confidence for inp in inputs]
            mean_confidence = sum(confidences) / len(confidences)
            confidence_variance = sum((c - mean_confidence) ** 2 for c in confidences) / len(confidences)
        
        # 计算有效样本大小
        effective_sample_size = sum(inp.confidence for inp in inputs)
        
        return {
            "convergence_possible": effective_sample_size > self.prior_strength,
            "effective_sample_size": effective_sample_size,
            "confidence_variance": confidence_variance,
            "prior_influence": self.prior_strength / (effective_sample_size + self.prior_strength),
            "data_influence": effective_sample_size / (effective_sample_size + self.prior_strength)
        }