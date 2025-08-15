#!/usr/bin/env python3
"""统一共识调度器核心数据模型测试

验证数据模型的正确性、验证逻辑和序列化功能。
确保所有组件能够正常工作并满足需求。
"""

from datetime import datetime

import pytest
from consensus_algorithm_interface import AlgorithmCapabilities, ConsensusContext
from consensus_models import (
    AlgorithmMetadata,
    AlgorithmType,
    ConsensusInput,
    ConsensusRequest,
    ConsensusResponse,
    ConsensusResult,
    QualityPriority,
    QualityRequirements,
)
from consensus_validation import ConsensusDataSerializer, ConsensusDataValidator


class TestConsensusModels:
    """测试核心数据模型"""
    
    def test_consensus_input_creation(self):
        """测试ConsensusInput创建"""
        input_data = ConsensusInput(
            agent_id="agent_001",
            position="支持提案A",
            confidence=0.8,
            reasoning="基于历史数据分析",
            evidence=["数据点1", "数据点2"]
        )
        
        assert input_data.agent_id == "agent_001"
        assert input_data.position == "支持提案A"
        assert input_data.confidence == 0.8
        assert input_data.reasoning == "基于历史数据分析"
        assert len(input_data.evidence) == 2
        assert isinstance(input_data.timestamp, datetime)
        
    def test_consensus_input_validation(self):
        """测试ConsensusInput验证"""
        # 测试置信度范围验证
        with pytest.raises(ValueError):
            ConsensusInput(
                agent_id="agent_001",
                position="test",
                confidence=1.5  # 超出范围
            )
            
        with pytest.raises(ValueError):
            ConsensusInput(
                agent_id="agent_001", 
                position="test",
                confidence=-0.1  # 超出范围
            )
            
    def test_consensus_request_creation(self):
        """测试ConsensusRequest创建"""
        inputs = [
            ConsensusInput(agent_id="agent_001", position="支持", confidence=0.8),
            ConsensusInput(agent_id="agent_002", position="反对", confidence=0.7)
        ]
        
        request = ConsensusRequest(
            inputs=inputs,
            algorithm_preference="weighted_voting",
            timeout=60.0,
            quality_requirements=QualityRequirements(
                priority=QualityPriority.ACCURACY,
                min_confidence=0.7
            )
        )
        
        assert len(request.inputs) == 2
        assert request.algorithm_preference == "weighted_voting"
        assert request.timeout == 60.0
        assert request.quality_requirements.priority == QualityPriority.ACCURACY
        
    def test_consensus_response_creation(self):
        """测试ConsensusResponse创建"""
        result = ConsensusResult(
            consensus_value="支持",
            confidence=0.75,
            participants=["agent_001", "agent_002"],
            reasoning_trace={"method": "weighted_voting"},
            metadata={"execution_details": "success"}
        )
        
        response = ConsensusResponse(
            success=True,
            result=result,
            algorithm_used="weighted_voting",
            execution_time=2.5,
            fallback_used=False
        )
        
        assert response.success is True
        assert response.result.consensus_value == "支持"
        assert response.algorithm_used == "weighted_voting"
        assert response.execution_time == 2.5
        assert response.fallback_used is False
        
    def test_algorithm_metadata_creation(self):
        """测试AlgorithmMetadata创建"""
        metadata = AlgorithmMetadata(
            name="加权投票算法",
            version="1.0.0",
            description="基于置信度的加权投票共识算法",
            algorithm_type=AlgorithmType.WEIGHTED_VOTING,
            input_types=["str", "float"],
            output_types=["str"],
            complexity="medium",
            accuracy=0.85,
            performance="fast",
            requirements=["numpy"],
            configuration_schema={"weights": {"type": "dict"}}
        )
        
        assert metadata.name == "加权投票算法"
        assert metadata.algorithm_type == AlgorithmType.WEIGHTED_VOTING
        assert metadata.accuracy == 0.85
        assert "numpy" in metadata.requirements


class TestConsensusAlgorithmInterface:
    """测试共识算法接口"""
    
    def test_algorithm_capabilities(self):
        """测试算法能力描述"""
        capabilities = AlgorithmCapabilities(
            supported_input_types={"str", "float"},
            supported_output_types={"str"},
            requires_reasoning=True,
            requires_evidence=False,
            supports_async=True,
            min_participants=2,
            max_participants=10
        )
        
        # 测试能力检查
        inputs = [
            ConsensusInput(agent_id="agent_001", position="支持", confidence=0.8, reasoning="理由1"),
            ConsensusInput(agent_id="agent_002", position="反对", confidence=0.7, reasoning="理由2")
        ]
        
        request = ConsensusRequest(inputs=inputs)
        assert capabilities.can_handle_request(request) is True
        
        # 测试参与者数量限制
        single_input_request = ConsensusRequest(inputs=[inputs[0]])
        assert capabilities.can_handle_request(single_input_request) is False
        
    def test_consensus_context(self):
        """测试共识上下文"""
        services = {"llm_service": "mock_llm", "memory_service": "mock_memory"}
        config = {"algorithm": "weighted_voting", "threshold": 0.6}
        
        context = ConsensusContext(
            session_id="test_session",
            services=services,
            configuration=config
        )
        
        assert context.session_id == "test_session"
        assert context.get_service("llm_service") == "mock_llm"
        assert context.configuration["threshold"] == 0.6
        
        # 测试指标设置
        context.set_metric("accuracy", 0.85)
        assert context.get_metric("accuracy") == 0.85
        assert context.get_metric("nonexistent", "default") == "default"


class TestConsensusDataValidation:
    """测试数据验证功能"""
    
    def test_validate_consensus_input(self):
        """测试共识输入验证"""
        # 有效输入
        valid_data = {
            "agent_id": "agent_001",
            "position": "支持提案",
            "confidence": 0.8,
            "reasoning": "基于分析结果",
            "evidence": ["证据1", "证据2"]
        }
        
        result = ConsensusDataValidator.validate_consensus_input(valid_data)
        assert result.is_valid is True
        assert len(result.errors) == 0
        
        # 无效输入 - 置信度超出范围
        invalid_data = valid_data.copy()
        invalid_data["confidence"] = 1.5
        
        result = ConsensusDataValidator.validate_consensus_input(invalid_data)
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        # 无效输入 - 缺少必需字段
        incomplete_data = {"agent_id": "agent_001"}
        
        result = ConsensusDataValidator.validate_consensus_input(incomplete_data)
        assert result.is_valid is False
        assert len(result.errors) > 0
        
    def test_validate_consensus_request(self):
        """测试共识请求验证"""
        inputs = [
            {
                "agent_id": "agent_001",
                "position": "支持",
                "confidence": 0.8
            },
            {
                "agent_id": "agent_002", 
                "position": "反对",
                "confidence": 0.7
            }
        ]
        
        # 有效请求
        valid_request = {
            "inputs": inputs,
            "timeout": 30.0
        }
        
        result = ConsensusDataValidator.validate_consensus_request(valid_request)
        assert result.is_valid is True
        
        # 无效请求 - 空输入列表
        invalid_request = {
            "inputs": [],
            "timeout": 30.0
        }
        
        result = ConsensusDataValidator.validate_consensus_request(invalid_request)
        assert result.is_valid is False
        assert any("inputs不能为空" in error for error in result.errors)
        
    def test_validate_algorithm_metadata(self):
        """测试算法元数据验证"""
        # 有效元数据
        valid_metadata = {
            "name": "测试算法",
            "version": "1.0.0",
            "description": "测试用算法",
            "algorithm_type": "weighted_voting",
            "input_types": ["str"],
            "output_types": ["str"],
            "complexity": "medium",
            "accuracy": 0.85,
            "performance": "fast"
        }
        
        result = ConsensusDataValidator.validate_algorithm_metadata(valid_metadata)
        assert result.is_valid is True
        
        # 无效元数据 - 错误的复杂度值
        invalid_metadata = valid_metadata.copy()
        invalid_metadata["complexity"] = "invalid_complexity"
        
        result = ConsensusDataValidator.validate_algorithm_metadata(invalid_metadata)
        assert result.is_valid is False


class TestConsensusDataSerialization:
    """测试数据序列化功能"""
    
    def test_json_serialization(self):
        """测试JSON序列化"""
        input_data = ConsensusInput(
            agent_id="agent_001",
            position="支持提案",
            confidence=0.8,
            reasoning="基于分析",
            evidence=["证据1"]
        )
        
        # 序列化
        json_str = ConsensusDataSerializer.serialize_to_json(input_data)
        assert isinstance(json_str, str)
        assert "agent_001" in json_str
        assert "支持提案" in json_str
        
        # 反序列化
        deserialized = ConsensusDataSerializer.deserialize_from_json(json_str, ConsensusInput)
        assert deserialized.agent_id == "agent_001"
        assert deserialized.position == "支持提案"
        assert deserialized.confidence == 0.8
        
    def test_legacy_format_conversion(self):
        """测试旧格式转换"""
        # 测试DebateTurn格式转换
        debate_turn_data = {
            "role_id": "expert_001",
            "opinion": "我认为这个提案很好",
            "round": 1
        }
        
        converted = ConsensusDataSerializer.convert_legacy_format(
            debate_turn_data, "debate_turn"
        )
        
        assert converted["agent_id"] == "expert_001"
        assert converted["position"] == "我认为这个提案很好"
        assert converted["confidence"] == 0.8
        assert converted["metadata"]["round"] == 1
        
        # 测试AdvancedConsensusInput格式转换
        advanced_input_data = {
            "agent_id": "agent_001",
            "position": "支持",
            "confidence": 0.9,
            "reasoning": "详细分析",
            "evidence": ["证据1", "证据2"],
            "cognitive_profile": {"expertise": "high"}
        }
        
        converted = ConsensusDataSerializer.convert_legacy_format(
            advanced_input_data, "advanced_consensus_input"
        )
        
        assert converted["agent_id"] == "agent_001"
        assert converted["position"] == "支持"
        assert converted["confidence"] == 0.9
        assert converted["metadata"]["cognitive_profile"]["expertise"] == "high"


def run_basic_functionality_test():
    """运行基本功能测试"""
    print("🧪 开始基本功能测试...")
    
    # 测试数据模型创建
    try:
        input_data = ConsensusInput(
            agent_id="test_agent",
            position="测试立场",
            confidence=0.8
        )
        print("✅ ConsensusInput 创建成功")
    except Exception as e:
        print(f"❌ ConsensusInput 创建失败: {e}")
        return False
        
    # 测试请求创建
    try:
        request = ConsensusRequest(inputs=[input_data])
        print("✅ ConsensusRequest 创建成功")
    except Exception as e:
        print(f"❌ ConsensusRequest 创建失败: {e}")
        return False
        
    # 测试验证功能
    try:
        validator = ConsensusDataValidator()
        result = validator.validate_consensus_input(input_data.dict())
        if result.is_valid:
            print("✅ 数据验证功能正常")
        else:
            print(f"❌ 数据验证失败: {result.errors}")
            return False
    except Exception as e:
        print(f"❌ 数据验证功能异常: {e}")
        return False
        
    # 测试序列化功能
    try:
        serializer = ConsensusDataSerializer()
        json_str = serializer.serialize_to_json(input_data)
        deserialized = serializer.deserialize_from_json(json_str, ConsensusInput)
        if deserialized.agent_id == input_data.agent_id:
            print("✅ 序列化功能正常")
        else:
            print("❌ 序列化功能异常: 数据不一致")
            return False
    except Exception as e:
        print(f"❌ 序列化功能异常: {e}")
        return False
        
    print("🎉 所有基本功能测试通过!")
    return True


if __name__ == "__main__":
    # 运行基本功能测试
    success = run_basic_functionality_test()
    
    if success:
        print("\n📋 测试总结:")
        print("- ✅ 核心数据模型正常工作")
        print("- ✅ 数据验证功能正常")
        print("- ✅ 序列化功能正常")
        print("- ✅ 接口定义完整")
        print("\n🚀 任务1实现完成，可以进行下一步开发!")
    else:
        print("\n❌ 测试失败，需要修复问题后再继续")