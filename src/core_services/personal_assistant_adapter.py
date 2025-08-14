#!/usr/bin/env python3
"""PersonalAssistantService适配器

为PersonalAssistantService提供统一共识调度器的集成，
保持原有接口不变，内部使用新的共识系统。

设计原则：
- 完全向后兼容
- 保持原有字符串返回格式
- 无缝集成统一共识调度器
- 提供性能和稳定性改进
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from legacy_compatibility_layer import get_personal_assistant_compatibility


class PersonalAssistantServiceAdapter:
    """PersonalAssistantService适配器
    
    提供与原有PersonalAssistantService完全兼容的接口，
    内部使用统一共识调度器进行共识计算。
    """

    def __init__(self):
        self.logger = logging.getLogger("adapter.PersonalAssistant")
        self.compatibility_layer = get_personal_assistant_compatibility()

    async def _local_consensus_calculation(self, inputs: List[Dict[str, Any]]) -> str:
        """本地共识计算实现 - 适配器版本
        
        这个方法替换PersonalAssistantService中的同名方法，
        使用统一共识调度器而不是直接调用高级共识算法。
        
        Args:
            inputs: 共识输入数据列表
            
        Returns:
            格式化的共识结果字符串

        """
        try:
            self.logger.info(f"开始共识计算，输入数量: {len(inputs)}")

            if not inputs:
                return "没有足够的输入数据进行共识计算"

            # 使用兼容层进行共识计算
            result = await self.compatibility_layer.calculate_local_consensus(inputs)

            self.logger.info("共识计算完成")
            return result

        except Exception as e:
            self.logger.error(f"共识计算失败: {e}")
            return f"共识计算失败：{str(e)}"

    async def execute_consensus_for_backend(self,
                                          inputs: List[Dict[str, Any]],
                                          algorithm_type: str) -> Dict[str, Any]:
        """为后端服务提供共识计算接口
        
        这个方法用于替换PersonalAssistantService中通过backend_service调用的共识计算。
        
        Args:
            inputs: 共识输入数据
            algorithm_type: 算法类型
            
        Returns:
            共识计算结果字典

        """
        try:
            self.logger.info(f"后端共识计算: {algorithm_type}, 输入数量: {len(inputs)}")

            # 使用兼容层执行共识计算
            result = await self.compatibility_layer.execute_consensus(inputs, algorithm_type)

            self.logger.info(f"后端共识计算完成: {result.get('success', False)}")
            return result

        except Exception as e:
            self.logger.error(f"后端共识计算失败: {e}")
            return {
                "error": str(e),
                "success": False,
                "algorithm_type": algorithm_type
            }

    def get_supported_algorithms(self) -> List[str]:
        """获取支持的算法列表"""
        return self.compatibility_layer.get_supported_algorithms()

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 测试基本的共识计算功能
            test_inputs = [
                {
                    "agent_id": "test_agent",
                    "position": "test_position",
                    "confidence": 0.8,
                    "reasoning": "health check test"
                }
            ]

            result = await self.compatibility_layer.execute_consensus(
                test_inputs, "simple_majority_vote"
            )

            return {
                "status": "healthy" if result.get("success", False) else "degraded",
                "adapter_available": True,
                "compatibility_layer_available": True,
                "supported_algorithms": len(self.get_supported_algorithms()),
                "last_check": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"健康检查失败: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "adapter_available": False,
                "last_check": datetime.now().isoformat()
            }


# 全局适配器实例
_personal_assistant_adapter = None


def get_personal_assistant_adapter() -> PersonalAssistantServiceAdapter:
    """获取PersonalAssistantService适配器实例"""
    global _personal_assistant_adapter
    if _personal_assistant_adapter is None:
        _personal_assistant_adapter = PersonalAssistantServiceAdapter()
    return _personal_assistant_adapter


def patch_personal_assistant_service():
    """为PersonalAssistantService打补丁，使其使用统一共识调度器
    
    这个函数可以在系统启动时调用，将PersonalAssistantService的
    共识计算方法替换为使用统一调度器的版本。
    """
    try:
        import personal_intelligence_hub.services.personal_assistant as pas_module

        # 获取适配器实例
        adapter = get_personal_assistant_adapter()

        # 替换_local_consensus_calculation方法
        original_method = getattr(pas_module.PersonalAssistantService, '_local_consensus_calculation', None)
        if original_method:
            # 保存原始方法作为备份
            pas_module.PersonalAssistantService._original_local_consensus_calculation = original_method

            # 替换为适配器方法
            pas_module.PersonalAssistantService._local_consensus_calculation = adapter._local_consensus_calculation

            logging.getLogger("adapter.PersonalAssistant").info(
                "PersonalAssistantService._local_consensus_calculation 已替换为统一调度器版本"
            )

        # 如果有backend_service的execute_consensus方法，也进行替换
        # 这需要在运行时动态处理，因为backend_service是异步初始化的

        return True

    except Exception as e:
        logging.getLogger("adapter.PersonalAssistant").error(f"补丁应用失败: {e}")
        return False


def unpatch_personal_assistant_service():
    """移除PersonalAssistantService的补丁，恢复原始方法
    """
    try:
        import personal_intelligence_hub.services.personal_assistant as pas_module

        # 恢复原始方法
        original_method = getattr(pas_module.PersonalAssistantService, '_original_local_consensus_calculation', None)
        if original_method:
            pas_module.PersonalAssistantService._local_consensus_calculation = original_method
            delattr(pas_module.PersonalAssistantService, '_original_local_consensus_calculation')

            logging.getLogger("adapter.PersonalAssistant").info(
                "PersonalAssistantService._local_consensus_calculation 已恢复为原始版本"
            )

        return True

    except Exception as e:
        logging.getLogger("adapter.PersonalAssistant").error(f"补丁移除失败: {e}")
        return False


class BackendServiceAdapter:
    """后端服务适配器
    
    为PersonalAssistantService的backend_service提供共识计算接口。
    """

    def __init__(self):
        self.logger = logging.getLogger("adapter.BackendService")
        self.compatibility_layer = get_personal_assistant_compatibility()

    async def execute_consensus(self,
                               inputs: List[Dict[str, Any]],
                               algorithm_type: str) -> Dict[str, Any]:
        """执行共识计算 - 后端服务接口
        
        这个方法模拟backend_service.execute_consensus的接口。
        """
        try:
            self.logger.info(f"后端服务共识计算: {algorithm_type}")

            # 使用兼容层执行共识计算
            result = await self.compatibility_layer.execute_consensus(inputs, algorithm_type)

            # 确保返回格式符合backend_service的期望
            if result.get("success", False):
                return {
                    "algorithm_type": result.get("algorithm_type", algorithm_type),
                    "consensus_strength": result.get("confidence", 0.0),
                    "summary": result.get("summary", "共识计算已完成"),
                    "confidence": result.get("confidence", 0.0),
                    "consensus_value": result.get("consensus_value", ""),
                    "participants": result.get("participants", []),
                    "execution_time": result.get("execution_time", 0.0)
                }
            else:
                return {
                    "error": result.get("error", "共识计算失败"),
                    "algorithm_type": algorithm_type
                }

        except Exception as e:
            self.logger.error(f"后端服务共识计算失败: {e}")
            return {
                "error": str(e),
                "algorithm_type": algorithm_type
            }


# 全局后端服务适配器实例
_backend_service_adapter = None


def get_backend_service_adapter() -> BackendServiceAdapter:
    """获取后端服务适配器实例"""
    global _backend_service_adapter
    if _backend_service_adapter is None:
        _backend_service_adapter = BackendServiceAdapter()
    return _backend_service_adapter
