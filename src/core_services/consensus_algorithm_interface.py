#!/usr/bin/env python3
"""统一共识算法接口定义

定义所有共识算法必须实现的统一接口，确保算法间的一致性和可互换性。

核心接口：
- ConsensusAlgorithm: 抽象基类，定义统一接口
- ConsensusContext: 算法执行上下文
- AlgorithmCapabilities: 算法能力描述

设计原则：
- 接口统一：所有算法实现相同接口
- 上下文隔离：算法执行环境独立
- 能力声明：算法明确声明自身能力
- 异步支持：支持异步执行模式
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from consensus_models import AlgorithmMetadata, ConsensusInput, ConsensusRequest, ConsensusResult, ValidationResult


class ConsensusContext:
    """共识算法执行上下文"""
    
    def __init__(self, 
                 session_id: Optional[str] = None,
                 services: Optional[dict[str, Any]] = None,
                 configuration: Optional[dict[str, Any]] = None):
        self.session_id = session_id or f"session_{datetime.now().timestamp()}"
        self.services = services or {}
        self.configuration = configuration or {}
        self.state = {}
        self.metrics = {}
        self.start_time = datetime.now()
        
    def get_service(self, service_name: str) -> Optional[Any]:
        """获取服务实例"""
        return self.services.get(service_name)
        
    def set_metric(self, key: str, value: Any) -> None:
        """设置指标"""
        self.metrics[key] = value
        
    def get_metric(self, key: str, default: Any = None) -> Any:
        """获取指标"""
        return self.metrics.get(key, default)
        
    def get_execution_time(self) -> float:
        """获取执行时间"""
        return (datetime.now() - self.start_time).total_seconds()


class AlgorithmCapabilities:
    """算法能力描述"""
    
    def __init__(self,
                 supported_input_types: set[str],
                 supported_output_types: set[str],
                 requires_reasoning: bool = False,
                 requires_evidence: bool = False,
                 supports_async: bool = True,
                 min_participants: int = 1,
                 max_participants: Optional[int] = None):
        self.supported_input_types = supported_input_types
        self.supported_output_types = supported_output_types
        self.requires_reasoning = requires_reasoning
        self.requires_evidence = requires_evidence
        self.supports_async = supports_async
        self.min_participants = min_participants
        self.max_participants = max_participants
        
    def can_handle_request(self, request: ConsensusRequest) -> bool:
        """检查是否能处理请求"""
        # 检查参与者数量
        participant_count = len(request.inputs)
        if participant_count < self.min_participants:
            return False
        if self.max_participants and participant_count > self.max_participants:
            return False
            
        # 检查输入类型
        for input_item in request.inputs:
            input_type = type(input_item.position).__name__
            if input_type not in self.supported_input_types:
                return False
                
        # 检查推理要求
        if self.requires_reasoning:
            if not all(input_item.reasoning for input_item in request.inputs):
                return False
                
        # 检查证据要求
        if self.requires_evidence:
            if not all(input_item.evidence for input_item in request.inputs):
                return False
                
        return True

class ConsensusAlgorithm(ABC):
    """统一共识算法抽象基类
    
    所有共识算法必须继承此类并实现其抽象方法。
    提供统一的接口确保算法间的一致性和可互换性。
    """
    
    def __init__(self, algorithm_id: str, configuration: Optional[dict[str, Any]] = None):
        self.algorithm_id = algorithm_id
        self.configuration = configuration or {}
        self._metadata = None
        self._capabilities = None
        
    @abstractmethod
    async def calculate(self, 
                       inputs: list[ConsensusInput], 
                       context: ConsensusContext) -> ConsensusResult:
        """执行共识计算
        
        Args:
            inputs: 共识输入列表
            context: 执行上下文
            
        Returns:
            共识计算结果
            
        Raises:
            ValueError: 输入数据无效
            RuntimeError: 算法执行失败
        """
        pass
        
    @abstractmethod
    def get_metadata(self) -> AlgorithmMetadata:
        """获取算法元数据
        
        Returns:
            算法元数据信息
        """
        pass
        
    @abstractmethod
    def get_capabilities(self) -> AlgorithmCapabilities:
        """获取算法能力描述
        
        Returns:
            算法能力信息
        """
        pass
        
    @abstractmethod
    def validate_inputs(self, inputs: list[ConsensusInput]) -> ValidationResult:
        """验证输入数据
        
        Args:
            inputs: 待验证的输入数据
            
        Returns:
            验证结果
        """
        pass
        
    def get_configuration(self) -> dict[str, Any]:
        """获取算法配置"""
        return self.configuration.copy()
        
    def set_configuration(self, config: dict[str, Any]) -> bool:
        """设置算法配置
        
        Args:
            config: 新的配置参数
            
        Returns:
            是否设置成功
        """
        try:
            # 验证配置
            validation_result = self.validate_configuration(config)
            if not validation_result.is_valid:
                return False
                
            # 更新配置
            self.configuration.update(config)
            return True
        except Exception:
            return False
            
    def validate_configuration(self, config: dict[str, Any]) -> ValidationResult:
        """验证配置参数
        
        Args:
            config: 待验证的配置
            
        Returns:
            验证结果
        """
        # 默认实现，子类可以重写
        return ValidationResult(is_valid=True)
        
    def can_handle_request(self, request: ConsensusRequest) -> bool:
        """检查是否能处理请求
        
        Args:
            request: 共识请求
            
        Returns:
            是否能处理
        """
        capabilities = self.get_capabilities()
        return capabilities.can_handle_request(request)
        
    def estimate_execution_time(self, request: ConsensusRequest) -> float:
        """估算执行时间
        
        Args:
            request: 共识请求
            
        Returns:
            预估执行时间(秒)
        """
        # 默认实现，基于输入数量的简单估算
        base_time = 1.0
        input_factor = len(request.inputs) * 0.1
        return base_time + input_factor
        
    def get_health_status(self) -> dict[str, Any]:
        """获取算法健康状态
        
        Returns:
            健康状态信息
        """
        return {
            "algorithm_id": self.algorithm_id,
            "status": "healthy",
            "last_check": datetime.now().isoformat(),
            "configuration_valid": True
        }
        
    def __str__(self) -> str:
        return f"ConsensusAlgorithm(id={self.algorithm_id})"
        
    def __repr__(self) -> str:
        return f"ConsensusAlgorithm(id='{self.algorithm_id}', config={self.configuration})"