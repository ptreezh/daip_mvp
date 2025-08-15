#!/usr/bin/env python3
"""遗留系统兼容层

为现有系统提供向后兼容的接口，确保现有功能完全兼容。
主要适配PersonalAssistantService、ToolManager和WorkflowEngine。

设计原则：
- 保持原有接口不变
- 内部使用统一共识调度器
- 提供无缝的数据格式转换
- 确保性能和稳定性
"""

import logging
from datetime import datetime
<<<<<<< HEAD
from typing import Any, Dict, List, Optional
=======
from typing import Any, Optional
>>>>>>> feature/core-services-refactor

from bayesian_algorithm import BayesianAlgorithm
from consensus_models import ConsensusInput, ConsensusRequest, ConsensusResponse, QualityPriority, QualityRequirements
from simple_majority_algorithm import SimpleMajorityAlgorithm
from unified_consensus_dispatcher import UnifiedConsensusDispatcher
from weighted_voting_algorithm import WeightedVotingAlgorithm
from workflow_consensus_algorithm import WorkflowConsensusAlgorithm


class LegacyCompatibilityLayer:
    """遗留系统兼容层基类
    
    提供统一的兼容性接口，处理数据格式转换和错误处理。
    """
<<<<<<< HEAD

    def __init__(self, dispatcher: Optional[UnifiedConsensusDispatcher] = None):
        self.logger = logging.getLogger(f"legacy.{self.__class__.__name__}")
        self.dispatcher = dispatcher or get_global_dispatcher()

    async def _convert_legacy_to_unified(self,
                                        legacy_inputs: List[Dict[str, Any]],
                                        algorithm_preference: Optional[str] = None) -> ConsensusRequest:
        """将遗留格式转换为统一格式"""
        unified_inputs = []

=======
    
    def __init__(self, dispatcher: Optional[UnifiedConsensusDispatcher] = None):
        self.logger = logging.getLogger(f"legacy.{self.__class__.__name__}")
        self.dispatcher = dispatcher or get_global_dispatcher()
        
    async def _convert_legacy_to_unified(self, 
                                        legacy_inputs: list[dict[str, Any]],
                                        algorithm_preference: Optional[str] = None) -> ConsensusRequest:
        """将遗留格式转换为统一格式"""
        unified_inputs = []
        
>>>>>>> feature/core-services-refactor
        for legacy_input in legacy_inputs:
            # 处理不同的遗留输入格式
            if isinstance(legacy_input, dict):
                unified_input = ConsensusInput(
                    agent_id=legacy_input.get("agent_id", "unknown_agent"),
                    position=legacy_input.get("position", ""),
                    confidence=float(legacy_input.get("confidence", 0.5)),
                    reasoning=legacy_input.get("reasoning", ""),
                    evidence=legacy_input.get("evidence", []),
                    metadata=legacy_input.get("metadata", {}),
                    timestamp=datetime.now()
                )
                unified_inputs.append(unified_input)
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        return ConsensusRequest(
            inputs=unified_inputs,
            algorithm_preference=algorithm_preference,
            quality_requirements=QualityRequirements(
                priority=QualityPriority.BALANCED,
                min_confidence=0.5
            )
        )
<<<<<<< HEAD

    async def _convert_unified_to_legacy(self,
                                        unified_response: ConsensusResponse) -> Dict[str, Any]:
=======
    
    async def _convert_unified_to_legacy(self, 
                                        unified_response: ConsensusResponse) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """将统一格式转换为遗留格式"""
        if not unified_response.success:
            return {
                "error": unified_response.error,
                "success": False
            }
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
        result = unified_response.result
        return {
            "success": True,
            "consensus_value": result.consensus_value,
            "confidence": result.confidence,
            "algorithm_type": unified_response.algorithm_used,
            "participants": result.participants,
            "execution_time": unified_response.execution_time,
            "summary": self._generate_legacy_summary(result),
            "consensus_strength": result.confidence,  # 兼容旧字段名
            "reasoning_trace": result.reasoning_trace,
            "metadata": result.metadata
        }
<<<<<<< HEAD

    def _generate_legacy_summary(self, result) -> str:
        """生成遗留系统期望的摘要格式"""
        return f"基于{len(result.participants)}个参与者的共识分析，置信度为{result.confidence:.2f}"

=======
    
    def _generate_legacy_summary(self, result) -> str:
        """生成遗留系统期望的摘要格式"""
        return f"基于{len(result.participants)}个参与者的共识分析，置信度为{result.confidence:.2f}"
    
>>>>>>> feature/core-services-refactor



class PersonalAssistantServiceCompatibility(LegacyCompatibilityLayer):
    """PersonalAssistantService兼容接口
    
    保持原有的字符串返回格式，内部使用统一共识调度器。
    """
<<<<<<< HEAD

    def __init__(self, dispatcher: Optional[UnifiedConsensusDispatcher] = None):
        super().__init__(dispatcher)
        self.logger = logging.getLogger("legacy.PersonalAssistant")

    async def execute_consensus(self,
                               inputs: List[Dict[str, Any]],
                               algorithm_type: str = "simple_majority_vote") -> Dict[str, Any]:
=======
    
    def __init__(self, dispatcher: Optional[UnifiedConsensusDispatcher] = None):
        super().__init__(dispatcher)
        self.logger = logging.getLogger("legacy.PersonalAssistant")
    
    async def execute_consensus(self, 
                               inputs: list[dict[str, Any]], 
                               algorithm_type: str = "simple_majority_vote") -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """为PersonalAssistantService提供共识计算接口
        
        Args:
            inputs: 遗留格式的输入数据
            algorithm_type: 算法类型（遗留命名）
            
        Returns:
            遗留格式的结果字典
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
        """
        try:
            # 映射遗留算法名称到统一名称
            algorithm_mapping = {
                "simple_majority_vote": "simple_majority",
<<<<<<< HEAD
                "weighted_voting": "weighted_voting",
                "bayesian_consensus": "bayesian_consensus",
                "workflow_consensus": "workflow_consensus"
            }

            unified_algorithm = algorithm_mapping.get(algorithm_type, "simple_majority")

=======
                "weighted_voting": "weighted_voting", 
                "bayesian_consensus": "bayesian_consensus",
                "workflow_consensus": "workflow_consensus"
            }
            
            unified_algorithm = algorithm_mapping.get(algorithm_type, "simple_majority")
            
>>>>>>> feature/core-services-refactor
            # 转换输入格式
            unified_request = await self._convert_legacy_to_unified(
                inputs, unified_algorithm
            )
<<<<<<< HEAD

            # 调用统一调度器
            unified_response = await self.dispatcher.calculate_consensus(unified_request)

            # 转换输出格式
            legacy_result = await self._convert_unified_to_legacy(unified_response)

            self.logger.info(f"共识计算完成: {algorithm_type} -> {unified_algorithm}")
            return legacy_result

=======
            
            # 调用统一调度器
            unified_response = await self.dispatcher.calculate_consensus(unified_request)
            
            # 转换输出格式
            legacy_result = await self._convert_unified_to_legacy(unified_response)
            
            self.logger.info(f"共识计算完成: {algorithm_type} -> {unified_algorithm}")
            return legacy_result
            
>>>>>>> feature/core-services-refactor
        except Exception as e:
            self.logger.error(f"共识计算失败: {e}")
            return {
                "error": str(e),
                "success": False,
                "algorithm_type": algorithm_type
            }
<<<<<<< HEAD

    async def calculate_local_consensus(self,
                                      inputs: List[Dict[str, Any]]) -> str:
=======
    
    async def calculate_local_consensus(self, 
                                      inputs: list[dict[str, Any]]) -> str:
>>>>>>> feature/core-services-refactor
        """为PersonalAssistantService提供本地共识计算
        
        保持原有的字符串返回格式，用于_local_consensus_calculation方法。
        """
        try:
            # 使用加权投票算法作为默认
            result = await self.execute_consensus(inputs, "weighted_voting")
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
            if result.get("success", False):
                return f"""**高级共识计算完成** 🎯

**算法类型：** {result.get('algorithm_type', 'weighted_voting')}
**共识强度：** {result.get('confidence', 0.0):.2f}
**参与代理：** {len(inputs)}个

**结果摘要：**
{result.get('summary', '基于统一共识调度器的分析已完成')}

**共识值：** {result.get('consensus_value', 'N/A')}
**置信度：** {result.get('confidence', 0.0):.2f}

*使用统一共识调度器计算*"""
            else:
                return f"共识计算失败：{result.get('error', '未知错误')}"
<<<<<<< HEAD

        except Exception as e:
            self.logger.error(f"本地共识计算失败: {e}")
            return f"共识计算失败：{str(e)}"

    def get_supported_algorithms(self) -> List[str]:
        """获取支持的算法列表"""
        return [
            "simple_majority_vote",
            "weighted_voting",
=======
                
        except Exception as e:
            self.logger.error(f"本地共识计算失败: {e}")
            return f"共识计算失败：{str(e)}"
    
    def get_supported_algorithms(self) -> list[str]:
        """获取支持的算法列表"""
        return [
            "simple_majority_vote",
            "weighted_voting", 
>>>>>>> feature/core-services-refactor
            "bayesian_consensus",
            "workflow_consensus"
        ]


class ToolManagerCompatibility(LegacyCompatibilityLayer):
    """ToolManager兼容接口
    
    适配工具管理器的调用接口，保持现有的工具注册机制。
    """
<<<<<<< HEAD

=======
    
>>>>>>> feature/core-services-refactor
    def __init__(self, dispatcher: Optional[UnifiedConsensusDispatcher] = None):
        super().__init__(dispatcher)
        self.logger = logging.getLogger("legacy.ToolManager")
        self.registered_tools = {}
<<<<<<< HEAD

    async def register_consensus_tool(self,
=======
    
    async def register_consensus_tool(self, 
>>>>>>> feature/core-services-refactor
                                    tool_name: str,
                                    algorithm_type: str = "simple_majority") -> bool:
        """注册共识工具
        
        Args:
            tool_name: 工具名称
            algorithm_type: 默认算法类型
            
        Returns:
            是否注册成功
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
        """
        try:
            self.registered_tools[tool_name] = {
                "algorithm_type": algorithm_type,
                "registered_at": datetime.now(),
                "call_count": 0
            }
<<<<<<< HEAD

            self.logger.info(f"共识工具已注册: {tool_name} -> {algorithm_type}")
            return True

        except Exception as e:
            self.logger.error(f"工具注册失败: {e}")
            return False

    async def execute_tool(self,
                          tool_name: str,
                          inputs: List[Dict[str, Any]],
                          parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
=======
            
            self.logger.info(f"共识工具已注册: {tool_name} -> {algorithm_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"工具注册失败: {e}")
            return False
    
    async def execute_tool(self, 
                          tool_name: str,
                          inputs: list[dict[str, Any]],
                          parameters: Optional[dict[str, Any]] = None) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """执行工具
        
        Args:
            tool_name: 工具名称
            inputs: 输入数据
            parameters: 执行参数
            
        Returns:
            执行结果
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
        """
        try:
            if tool_name not in self.registered_tools:
                return {
                    "error": f"工具未注册: {tool_name}",
                    "success": False
                }
<<<<<<< HEAD

            tool_info = self.registered_tools[tool_name]
            parameters = parameters or {}
            algorithm_type = parameters.get("algorithm_type", tool_info["algorithm_type"])

            # 转换输入格式
            unified_request = await self._convert_legacy_to_unified(inputs, algorithm_type)

            # 调用统一调度器
            unified_response = await self.dispatcher.calculate_consensus(unified_request)

            # 转换输出格式
            legacy_result = await self._convert_unified_to_legacy(unified_response)

            # 更新调用统计
            tool_info["call_count"] += 1
            tool_info["last_called"] = datetime.now()

            # 添加工具特定的元数据
            legacy_result["tool_name"] = tool_name
            legacy_result["call_count"] = tool_info["call_count"]

            self.logger.info(f"工具执行完成: {tool_name}")
            return legacy_result

=======
            
            tool_info = self.registered_tools[tool_name]
            parameters = parameters or {}
            algorithm_type = parameters.get("algorithm_type", tool_info["algorithm_type"])
            
            # 转换输入格式
            unified_request = await self._convert_legacy_to_unified(inputs, algorithm_type)
            
            # 调用统一调度器
            unified_response = await self.dispatcher.calculate_consensus(unified_request)
            
            # 转换输出格式
            legacy_result = await self._convert_unified_to_legacy(unified_response)
            
            # 更新调用统计
            tool_info["call_count"] += 1
            tool_info["last_called"] = datetime.now()
            
            # 添加工具特定的元数据
            legacy_result["tool_name"] = tool_name
            legacy_result["call_count"] = tool_info["call_count"]
            
            self.logger.info(f"工具执行完成: {tool_name}")
            return legacy_result
            
>>>>>>> feature/core-services-refactor
        except Exception as e:
            self.logger.error(f"工具执行失败: {e}")
            return {
                "error": str(e),
                "success": False,
                "tool_name": tool_name
            }
<<<<<<< HEAD

    def get_registered_tools(self) -> Dict[str, Dict[str, Any]]:
=======
    
    def get_registered_tools(self) -> dict[str, dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """获取已注册的工具列表"""
        return self.registered_tools.copy()


class WorkflowEngineCompatibility(LegacyCompatibilityLayer):
    """WorkflowEngine兼容接口
    
    适配工作流引擎的节点接口，保持ExecutionContext的兼容性。
    """
<<<<<<< HEAD

    def __init__(self, dispatcher: Optional[UnifiedConsensusDispatcher] = None):
        super().__init__(dispatcher)
        self.logger = logging.getLogger("legacy.WorkflowEngine")

    async def execute_consensus_node(self,
                                   inputs: Dict[str, Any],
                                   execution_context: Any) -> Dict[str, Any]:
=======
    
    def __init__(self, dispatcher: Optional[UnifiedConsensusDispatcher] = None):
        super().__init__(dispatcher)
        self.logger = logging.getLogger("legacy.WorkflowEngine")
    
    async def execute_consensus_node(self,
                                   inputs: dict[str, Any],
                                   execution_context: Any) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """执行共识节点
        
        Args:
            inputs: 节点输入数据
            execution_context: 工作流执行上下文
            
        Returns:
            节点执行结果
<<<<<<< HEAD

=======
>>>>>>> feature/core-services-refactor
        """
        try:
            # 从工作流输入中提取共识数据
            consensus_inputs = []
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
            if "aggregated_evidence" in inputs:
                # 处理聚合证据格式
                evidence_data = inputs["aggregated_evidence"]
                for fact_id, evidence in evidence_data.items():
                    consensus_input = ConsensusInput(
                        agent_id=f"evidence_{fact_id}",
                        position=evidence.get("fact_content", fact_id),
                        confidence=self._calculate_evidence_confidence(evidence),
                        reasoning=evidence.get("evidence_summary", ""),
                        metadata={
                            "fact_id": fact_id,
                            "evidence_type": "aggregated",
                            "supporting_score": evidence.get("supporting_score", 0.0),
                            "challenging_score": evidence.get("challenging_score", 0.0)
                        }
                    )
                    consensus_inputs.append(consensus_input)
            else:
                # 处理直接输入格式
                for key, value in inputs.items():
                    if isinstance(value, dict) and "position" in value:
                        consensus_input = ConsensusInput(
                            agent_id=value.get("agent_id", key),
                            position=value["position"],
                            confidence=value.get("confidence", 0.5),
                            reasoning=value.get("reasoning", ""),
                            metadata=value.get("metadata", {})
                        )
                        consensus_inputs.append(consensus_input)
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
            if not consensus_inputs:
                return {
                    "success": False,
                    "error": "没有有效的共识输入数据",
                    "credibility_scores": {},
                    "consensus_results": {},
                    "facts_needing_revision": []
                }
<<<<<<< HEAD

=======
            
>>>>>>> feature/core-services-refactor
            # 创建统一请求
            unified_request = ConsensusRequest(
                inputs=consensus_inputs,
                algorithm_preference="workflow_consensus",
                quality_requirements=QualityRequirements(
                    priority=QualityPriority.ACCURACY,
                    min_confidence=0.6
                )
            )
<<<<<<< HEAD

            # 调用统一调度器
            unified_response = await self.dispatcher.calculate_consensus(unified_request)

=======
            
            # 调用统一调度器
            unified_response = await self.dispatcher.calculate_consensus(unified_request)
            
>>>>>>> feature/core-services-refactor
            # 转换为工作流节点期望的格式
            if unified_response.success:
                result = unified_response.result
                return {
                    "success": True,
                    "credibility_scores": {
<<<<<<< HEAD
                        inp.metadata.get("fact_id", inp.agent_id): result.confidence
=======
                        inp.metadata.get("fact_id", inp.agent_id): result.confidence 
>>>>>>> feature/core-services-refactor
                        for inp in consensus_inputs
                    },
                    "consensus_results": {
                        inp.metadata.get("fact_id", inp.agent_id): {
                            "fact_id": inp.metadata.get("fact_id", inp.agent_id),
                            "fact_content": str(inp.position),
                            "credibility_score": result.confidence,
                            "consensus_method": unified_response.algorithm_used,
                            "needs_revision": result.confidence < 0.6,
                            "evidence_summary": inp.reasoning,
                            "consensus_details": result.reasoning_trace
                        }
                        for inp in consensus_inputs
                    },
                    "facts_needing_revision": [
<<<<<<< HEAD
                        inp.metadata.get("fact_id", inp.agent_id)
                        for inp in consensus_inputs
=======
                        inp.metadata.get("fact_id", inp.agent_id) 
                        for inp in consensus_inputs 
>>>>>>> feature/core-services-refactor
                        if result.confidence < 0.6
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": unified_response.error,
                    "credibility_scores": {},
                    "consensus_results": {},
                    "facts_needing_revision": []
                }
<<<<<<< HEAD

=======
                
>>>>>>> feature/core-services-refactor
        except Exception as e:
            self.logger.error(f"工作流共识节点执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "credibility_scores": {},
                "consensus_results": {},
                "facts_needing_revision": []
            }
<<<<<<< HEAD

    def _calculate_evidence_confidence(self, evidence: Dict[str, Any]) -> float:
=======
    
    def _calculate_evidence_confidence(self, evidence: dict[str, Any]) -> float:
>>>>>>> feature/core-services-refactor
        """从证据数据计算置信度"""
        supporting = evidence.get("supporting_score", 0.0)
        challenging = evidence.get("challenging_score", 0.0)
        neutral = evidence.get("neutral_score", 0.0)
<<<<<<< HEAD

        total = supporting + challenging + neutral
        if total == 0:
            return 0.5

=======
        
        total = supporting + challenging + neutral
        if total == 0:
            return 0.5
        
>>>>>>> feature/core-services-refactor
        # 支持证据增加置信度，质疑证据降低置信度
        weighted_score = (supporting - challenging) / total
        return min(max(0.5 + weighted_score * 0.5, 0.0), 1.0)


# 全局调度器实例（单例）
_global_dispatcher = None

def get_global_dispatcher() -> UnifiedConsensusDispatcher:
    """获取全局统一调度器实例"""
    global _global_dispatcher
    if _global_dispatcher is None:
        _global_dispatcher = _create_initialized_dispatcher()
    return _global_dispatcher

def _create_initialized_dispatcher() -> UnifiedConsensusDispatcher:
    """创建并初始化统一共识调度器"""
    logger = logging.getLogger("legacy.GlobalDispatcher")
    try:
        # 创建调度器
        dispatcher = UnifiedConsensusDispatcher()
<<<<<<< HEAD

        # 注册所有可用的算法
        registry = dispatcher.registry

        # 注册简单多数投票算法
        simple_majority = SimpleMajorityAlgorithm()
        registry.register("simple_majority", simple_majority)

        # 注册加权投票算法
        weighted_voting = WeightedVotingAlgorithm()
        registry.register("weighted_voting", weighted_voting)

        # 注册贝叶斯共识算法
        bayesian = BayesianAlgorithm()
        registry.register("bayesian_consensus", bayesian)

        # 注册工作流共识算法
        workflow = WorkflowConsensusAlgorithm()
        registry.register("workflow_consensus", workflow)

=======
        
        # 注册所有可用的算法
        registry = dispatcher.registry
        
        # 注册简单多数投票算法
        simple_majority = SimpleMajorityAlgorithm()
        registry.register("simple_majority", simple_majority)
        
        # 注册加权投票算法
        weighted_voting = WeightedVotingAlgorithm()
        registry.register("weighted_voting", weighted_voting)
        
        # 注册贝叶斯共识算法
        bayesian = BayesianAlgorithm()
        registry.register("bayesian_consensus", bayesian)
        
        # 注册工作流共识算法
        workflow = WorkflowConsensusAlgorithm()
        registry.register("workflow_consensus", workflow)
        
>>>>>>> feature/core-services-refactor
        # 验证注册结果
        registered_ids = registry.get_algorithm_ids()
        logger.info(f"全局统一共识调度器初始化完成，已注册{len(registered_ids)}个算法: {registered_ids}")
        return dispatcher
<<<<<<< HEAD

=======
        
>>>>>>> feature/core-services-refactor
    except Exception as e:
        logger.error(f"全局调度器初始化失败: {e}")
        # 返回基本调度器
        return UnifiedConsensusDispatcher()

# 全局兼容层实例
_personal_assistant_compatibility = None
_tool_manager_compatibility = None
_workflow_engine_compatibility = None


def get_personal_assistant_compatibility() -> PersonalAssistantServiceCompatibility:
    """获取PersonalAssistantService兼容层实例"""
    global _personal_assistant_compatibility
    if _personal_assistant_compatibility is None:
        _personal_assistant_compatibility = PersonalAssistantServiceCompatibility(get_global_dispatcher())
    return _personal_assistant_compatibility


def get_tool_manager_compatibility() -> ToolManagerCompatibility:
    """获取ToolManager兼容层实例"""
    global _tool_manager_compatibility
    if _tool_manager_compatibility is None:
        _tool_manager_compatibility = ToolManagerCompatibility(get_global_dispatcher())
    return _tool_manager_compatibility


def get_workflow_engine_compatibility() -> WorkflowEngineCompatibility:
    """获取WorkflowEngine兼容层实例"""
    global _workflow_engine_compatibility
    if _workflow_engine_compatibility is None:
        _workflow_engine_compatibility = WorkflowEngineCompatibility(get_global_dispatcher())
<<<<<<< HEAD
    return _workflow_engine_compatibility
=======
    return _workflow_engine_compatibility
>>>>>>> feature/core-services-refactor
