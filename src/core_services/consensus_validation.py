#!/usr/bin/env python3
"""共识数据验证和序列化工具

提供统一的数据验证、序列化和反序列化功能。
确保数据格式的一致性和完整性。

核心功能：
- 输入数据验证
- 配置参数验证  
- JSON序列化/反序列化
- 数据格式转换
- 兼容性检查

设计原则：
- 严格验证：确保数据完整性
- 向后兼容：支持旧版本数据格式
- 错误友好：提供详细的错误信息
- 性能优化：高效的验证和转换
"""

import json
import re
from datetime import datetime
from typing import Any

from consensus_models import (
    AlgorithmMetadata,
    ConsensusInput,
    ConsensusRequest,
    ValidationResult,
)
from pydantic import ValidationError


class ConsensusDataValidator:
    """共识数据验证器"""
    
    @staticmethod
    def validate_consensus_input(data: dict[str, Any]) -> ValidationResult:
        """验证共识输入数据"""
        errors = []
        warnings = []
        
        try:
            # 使用Pydantic验证
            ConsensusInput(**data)
        except ValidationError as e:
            for error in e.errors():
                field = ".".join(str(x) for x in error["loc"])
                message = error["msg"]
                errors.append(f"字段 '{field}': {message}")
        except Exception as e:
            errors.append(f"验证失败: {str(e)}")
            
        # 额外的业务逻辑验证
        if "confidence" in data:
            confidence = data["confidence"]
            if not isinstance(confidence, (int, float)):
                errors.append("置信度必须是数字")
            elif confidence < 0 or confidence > 1:
                errors.append("置信度必须在0-1之间")
                
        if "agent_id" in data:
            agent_id = data["agent_id"]
            if not isinstance(agent_id, str) or not agent_id.strip():
                errors.append("agent_id必须是非空字符串")
                
        # 检查position类型
        if "position" in data:
            position = data["position"]
            if position is None:
                errors.append("position不能为空")
            elif isinstance(position, str) and not position.strip():
                warnings.append("position为空字符串")
                
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
        
    @staticmethod
    def validate_consensus_request(data: dict[str, Any]) -> ValidationResult:
        """验证共识请求数据"""
        errors = []
        warnings = []
        
        try:
            # 使用Pydantic验证
            ConsensusRequest(**data)
        except ValidationError as e:
            for error in e.errors():
                field = ".".join(str(x) for x in error["loc"])
                message = error["msg"]
                errors.append(f"字段 '{field}': {message}")
        except Exception as e:
            errors.append(f"验证失败: {str(e)}")
            
        # 验证输入列表
        if "inputs" in data:
            inputs = data["inputs"]
            if not isinstance(inputs, list):
                errors.append("inputs必须是列表")
            elif len(inputs) == 0:
                errors.append("inputs不能为空")
            else:
                # 验证每个输入
                for i, input_data in enumerate(inputs):
                    if not isinstance(input_data, dict):
                        errors.append(f"inputs[{i}]必须是字典")
                        continue
                        
                    input_validation = ConsensusDataValidator.validate_consensus_input(input_data)
                    if not input_validation.is_valid:
                        for error in input_validation.errors:
                            errors.append(f"inputs[{i}].{error}")
                            
        # 验证超时时间
        if "timeout" in data:
            timeout = data["timeout"]
            if not isinstance(timeout, (int, float)):
                errors.append("timeout必须是数字")
            elif timeout <= 0:
                errors.append("timeout必须大于0")
            elif timeout > 300:  # 5分钟
                warnings.append("timeout过长，可能影响用户体验")
                
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
        
    @staticmethod
    def validate_algorithm_metadata(data: dict[str, Any]) -> ValidationResult:
        """验证算法元数据"""
        errors = []
        warnings = []
        
        try:
            AlgorithmMetadata(**data)
        except ValidationError as e:
            for error in e.errors():
                field = ".".join(str(x) for x in error["loc"])
                message = error["msg"]
                errors.append(f"字段 '{field}': {message}")
        except Exception as e:
            errors.append(f"验证失败: {str(e)}")
            
        # 验证版本格式
        if "version" in data:
            version = data["version"]
            if not re.match(r'^\d+\.\d+(\.\d+)?$', version):
                warnings.append("版本号建议使用语义化版本格式 (如: 1.0.0)")
                
        # 验证复杂度等级
        if "complexity" in data:
            complexity = data["complexity"]
            if complexity not in ["low", "medium", "high"]:
                errors.append("complexity必须是 'low', 'medium', 或 'high'")
                
        # 验证性能等级
        if "performance" in data:
            performance = data["performance"]
            if performance not in ["fast", "medium", "slow"]:
                errors.append("performance必须是 'fast', 'medium', 或 'slow'")
                
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class ConsensusDataSerializer:
    """共识数据序列化器"""
    
    @staticmethod
    def serialize_to_json(obj: Any) -> str:
        """序列化对象为JSON字符串"""
        def json_encoder(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, 'dict'):  # Pydantic模型
                return obj.dict()
            elif hasattr(obj, '__dict__'):  # 普通对象
                return obj.__dict__
            else:
                return str(obj)
                
        return json.dumps(obj, default=json_encoder, ensure_ascii=False, indent=2)
        
    @staticmethod
    def deserialize_from_json(json_str: str, target_type: type) -> Any:
        """从JSON字符串反序列化对象"""
        try:
            data = json.loads(json_str)
            
            # 处理datetime字段
            if isinstance(data, dict):
                data = ConsensusDataSerializer._convert_datetime_fields(data)
                
            # 使用目标类型创建对象
            if hasattr(target_type, 'parse_obj'):  # Pydantic模型
                return target_type.parse_obj(data)
            else:
                return target_type(**data)
                
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON格式错误: {str(e)}")
        except Exception as e:
            raise ValueError(f"反序列化失败: {str(e)}")
            
    @staticmethod
    def _convert_datetime_fields(data: dict[str, Any]) -> dict[str, Any]:
        """转换datetime字段"""
        datetime_fields = ["timestamp", "created_at", "updated_at"]
        
        for field in datetime_fields:
            if field in data and isinstance(data[field], str):
                try:
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                except ValueError:
                    pass  # 保持原值
                    
        return data
        
    @staticmethod
    def convert_legacy_format(legacy_data: dict[str, Any], 
                            source_format: str) -> dict[str, Any]:
        """转换旧版本数据格式"""
        if source_format == "debate_turn":
            # 转换DebateTurn格式到ConsensusInput
            return {
                "agent_id": legacy_data.get("role_id", "unknown"),
                "position": legacy_data.get("opinion", ""),
                "confidence": 0.8,  # 默认置信度
                "reasoning": legacy_data.get("opinion", ""),
                "evidence": [],
                "metadata": {
                    "round": legacy_data.get("round", 1),
                    "source_format": "debate_turn"
                },
                "timestamp": datetime.now()
            }
        elif source_format == "advanced_consensus_input":
            # 转换AdvancedConsensusAlgorithms的ConsensusInput格式
            return {
                "agent_id": legacy_data.get("agent_id", "unknown"),
                "position": legacy_data.get("position"),
                "confidence": legacy_data.get("confidence", 0.5),
                "reasoning": legacy_data.get("reasoning"),
                "evidence": legacy_data.get("evidence", []),
                "metadata": {
                    "cognitive_profile": legacy_data.get("cognitive_profile"),
                    "source_format": "advanced_consensus_input"
                },
                "timestamp": legacy_data.get("timestamp", datetime.now())
            }
        else:
            raise ValueError(f"不支持的源格式: {source_format}")


class ConsensusDataConverter:
    """共识数据格式转换器"""
    
    @staticmethod
    def to_standard_format(data: Any, source_type: str = "auto") -> dict[str, Any]:
        """转换为标准格式"""
        if source_type == "auto":
            source_type = ConsensusDataConverter._detect_format(data)
            
        if source_type == "pydantic":
            return data.dict() if hasattr(data, 'dict') else data
        elif source_type == "dataclass":
            return data.__dict__ if hasattr(data, '__dict__') else data
        elif source_type == "dict":
            return data
        else:
            raise ValueError(f"不支持的源类型: {source_type}")
            
    @staticmethod
    def _detect_format(data: Any) -> str:
        """自动检测数据格式"""
        if hasattr(data, 'dict'):  # Pydantic模型
            return "pydantic"
        elif hasattr(data, '__dict__'):  # 数据类或普通对象
            return "dataclass"
        elif isinstance(data, dict):
            return "dict"
        else:
            return "unknown"
            
    @staticmethod
    def batch_convert(data_list: list[Any], 
                     target_type: type,
                     source_format: str = "auto") -> list[Any]:
        """批量转换数据"""
        results = []
        errors = []
        
        for i, item in enumerate(data_list):
            try:
                if source_format != "auto":
                    converted = ConsensusDataSerializer.convert_legacy_format(item, source_format)
                    result = target_type(**converted)
                else:
                    standard_data = ConsensusDataConverter.to_standard_format(item)
                    result = target_type(**standard_data)
                results.append(result)
            except Exception as e:
                errors.append(f"项目 {i}: {str(e)}")
                
        if errors:
            raise ValueError(f"批量转换失败: {'; '.join(errors)}")
            
        return results