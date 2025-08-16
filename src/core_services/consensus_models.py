#!/usr/bin/env python3
"""统一共识调度器核心数据模型

提供统一的数据模型类，用于标准化所有共识算法的输入输出格式。
解决当前系统中数据模型不一致的问题。

核心模型：
- ConsensusRequest: 统一的共识计算请求
- ConsensusResponse: 统一的共识计算响应  
- ConsensusInput: 标准化的共识输入
- AlgorithmMetadata: 算法元数据和配置
- ValidationResult: 数据验证结果

设计原则：
- 类型安全：使用Pydantic进行数据验证
- 向后兼容：支持现有系统的数据格式
- 可扩展性：支持未来新增字段和算法类型
- 序列化友好：支持JSON序列化和反序列化
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
<<<<<<< HEAD
from typing import Any, Dict, List, Optional, Union
=======
from typing import Any, Optional, Union
>>>>>>> feature/core-services-refactor

from pydantic import BaseModel, Field, validator


class AlgorithmType(str, Enum):
    """共识算法类型枚举"""
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    SIMPLE_MAJORITY = "simple_majority"
    WEIGHTED_VOTING = "weighted_voting"
    BAYESIAN_CONSENSUS = "bayesian_consensus"
    COGNITIVE_DIVERSITY_PRESERVING = "cognitive_diversity_preserving"
    WORKFLOW_CONSENSUS = "workflow_consensus"
    CUSTOM = "custom"


class QualityPriority(str, Enum):
    """质量优先级枚举"""
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    SPEED = "speed"
    ACCURACY = "accuracy"
    BALANCED = "balanced"


@dataclass
class QualityRequirements:
    """质量要求配置"""
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    priority: QualityPriority = QualityPriority.BALANCED
    min_confidence: float = 0.5
    max_execution_time: float = 30.0
    require_reasoning: bool = False
    require_evidence: bool = False


class ConsensusInput(BaseModel):
    """标准化的共识输入数据模型"""
<<<<<<< HEAD

    agent_id: str = Field(..., description="参与者ID")
    position: Union[str, float, Dict[str, Any]] = Field(..., description="立场或观点")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度 (0.0-1.0)")
    reasoning: Optional[str] = Field(None, description="推理过程")
    evidence: Optional[List[str]] = Field(default_factory=list, description="支持证据")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")

=======
    agent_id: str = Field(..., description="参与者ID")
    position: Union[str, float, dict[str, Any]] = Field(..., description="立场或观点")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度 (0.0-1.0)")
    reasoning: Optional[str] = Field(None, description="推理过程")
    evidence: Optional[list[str]] = Field(default_factory=list, description="支持证据")
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict, description="元数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    
>>>>>>> feature/core-services-refactor
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConsensusRequest(BaseModel):
    """统一的共识计算请求"""
<<<<<<< HEAD

    inputs: List[ConsensusInput] = Field(..., min_items=1, description="共识输入列表")
    algorithm_preference: Optional[str] = Field(None, description="首选算法ID")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="上下文信息")
    session_id: Optional[str] = Field(None, description="会话ID")
    timeout: float = Field(default=30.0, gt=0, description="超时时间(秒)")
    quality_requirements: Optional[QualityRequirements] = Field(None, description="质量要求")

=======
    inputs: list[ConsensusInput] = Field(..., min_items=1, description="共识输入列表")
    algorithm_preference: Optional[str] = Field(None, description="首选算法ID")
    context: Optional[dict[str, Any]] = Field(default_factory=dict, description="上下文信息")
    session_id: Optional[str] = Field(None, description="会话ID")
    timeout: float = Field(default=30.0, gt=0, description="超时时间(秒)")
    quality_requirements: Optional[QualityRequirements] = Field(None, description="质量要求")
    
>>>>>>> feature/core-services-refactor
    @validator('inputs')
    def validate_inputs_not_empty(cls, v):
        if not v:
            raise ValueError("输入列表不能为空")
        return v


class ConsensusResult(BaseModel):
    """共识计算结果"""
<<<<<<< HEAD

    consensus_value: Any = Field(..., description="共识结果值")
    confidence: float = Field(..., ge=0.0, le=1.0, description="结果置信度")
    participants: List[str] = Field(..., description="参与者ID列表")
    reasoning_trace: Dict[str, Any] = Field(default_factory=dict, description="推理轨迹")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="结果元数据")
=======
    consensus_value: Any = Field(..., description="共识结果值")
    confidence: float = Field(..., ge=0.0, le=1.0, description="结果置信度")
    participants: list[str] = Field(..., description="参与者ID列表")
    reasoning_trace: dict[str, Any] = Field(default_factory=dict, description="推理轨迹")
    metadata: dict[str, Any] = Field(default_factory=dict, description="结果元数据")
>>>>>>> feature/core-services-refactor


class ConsensusResponse(BaseModel):
    """统一的共识计算响应"""
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    success: bool = Field(..., description="是否成功")
    result: Optional[ConsensusResult] = Field(None, description="共识结果")
    algorithm_used: str = Field(..., description="使用的算法ID")
    execution_time: float = Field(..., ge=0, description="执行时间(秒)")
    error: Optional[str] = Field(None, description="错误信息")
    fallback_used: bool = Field(default=False, description="是否使用了降级算法")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AlgorithmMetadata(BaseModel):
    """算法元数据"""
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    name: str = Field(..., description="算法名称")
    version: str = Field(..., description="算法版本")
    description: str = Field(..., description="算法描述")
    algorithm_type: AlgorithmType = Field(..., description="算法类型")
<<<<<<< HEAD
    input_types: List[str] = Field(..., description="支持的输入类型")
    output_types: List[str] = Field(..., description="输出类型")
    complexity: str = Field(..., description="复杂度等级: low/medium/high")
    accuracy: float = Field(..., ge=0.0, le=1.0, description="准确性评分")
    performance: str = Field(..., description="性能等级: fast/medium/slow")
    requirements: List[str] = Field(default_factory=list, description="依赖要求")
    configuration_schema: Dict[str, Any] = Field(default_factory=dict, description="配置模式")
=======
    input_types: list[str] = Field(..., description="支持的输入类型")
    output_types: list[str] = Field(..., description="输出类型")
    complexity: str = Field(..., description="复杂度等级: low/medium/high")
    accuracy: float = Field(..., ge=0.0, le=1.0, description="准确性评分")
    performance: str = Field(..., description="性能等级: fast/medium/slow")
    requirements: list[str] = Field(default_factory=list, description="依赖要求")
    configuration_schema: dict[str, Any] = Field(default_factory=dict, description="配置模式")
>>>>>>> feature/core-services-refactor


class ValidationResult(BaseModel):
    """数据验证结果"""
<<<<<<< HEAD

    is_valid: bool = Field(..., description="是否有效")
    errors: List[str] = Field(default_factory=list, description="错误列表")
    warnings: List[str] = Field(default_factory=list, description="警告列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="验证元数据")
=======
    is_valid: bool = Field(..., description="是否有效")
    errors: list[str] = Field(default_factory=list, description="错误列表")
    warnings: list[str] = Field(default_factory=list, description="警告列表")
    metadata: dict[str, Any] = Field(default_factory=dict, description="验证元数据")
>>>>>>> feature/core-services-refactor


class AlgorithmSelection(BaseModel):
    """算法选择结果"""
<<<<<<< HEAD

    algorithm_id: str = Field(..., description="选中的算法ID")
    confidence: float = Field(..., ge=0.0, le=1.0, description="选择置信度")
    reasoning: str = Field(..., description="选择理由")
    alternatives: List[str] = Field(default_factory=list, description="备选算法")
=======
    algorithm_id: str = Field(..., description="选中的算法ID")
    confidence: float = Field(..., ge=0.0, le=1.0, description="选择置信度")
    reasoning: str = Field(..., description="选择理由")
    alternatives: list[str] = Field(default_factory=list, description="备选算法")
>>>>>>> feature/core-services-refactor
    selection_time: float = Field(..., ge=0, description="选择耗时(秒)")


class FailureContext(BaseModel):
    """失败上下文信息"""
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
    failed_algorithm: str = Field(..., description="失败的算法ID")
    error_type: str = Field(..., description="错误类型")
    error_message: str = Field(..., description="错误消息")
    execution_time: float = Field(..., ge=0, description="执行时间(秒)")
    retry_count: int = Field(default=0, ge=0, description="重试次数")
<<<<<<< HEAD
    context: Dict[str, Any] = Field(default_factory=dict, description="失败上下文")
=======
    context: dict[str, Any] = Field(default_factory=dict, description="失败上下文")
>>>>>>> feature/core-services-refactor
