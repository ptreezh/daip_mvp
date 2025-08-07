#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-03 22:10:00
@Author  : DAIP-LIVE Team  
@File    : app_state_v2.py
@Description:
    AppState增强版本 - 安全集成新服务
    
    在原有AppState基础上增加新服务的安全集成，
    保持完全向后兼容性。
"""

import os
import logging
from typing import Any, Optional

# 导入原有AppState
from src.app_state import AppState as OriginalAppState
from src.integration.service_integration_manager import (
    create_service_integration_manager, 
    IntegrationConfig
)

logger = logging.getLogger(__name__)

class EnhancedAppState(OriginalAppState):
    """
    增强版AppState - 安全集成新服务
    
    继承自原有AppState，增加新服务的安全集成功能，
    确保向后兼容性和系统稳定性。
    """
    
    def __init__(self):
        # 首先初始化原有AppState
        logger.info("正在初始化原有AppState...")
        super().__init__()
        
        # 初始化集成管理器
        self.integration_config = IntegrationConfig(
            enable_prompt_building_service=True,
            enable_autonomous_role_creation=True, 
            enable_enhanced_memory_management=True,
            enable_interactive_experience_optimizer=True,
            fallback_on_error=True,
            validate_before_integration=True
        )
        
        self.service_integration_manager = create_service_integration_manager(
            self, self.integration_config
        )
        
        # 新服务占位符（集成后会被填充）
        self.prompt_building_service: Optional[Any] = None
        self.autonomous_role_creation_system: Optional[Any] = None
        self.enhanced_memory_manager: Optional[Any] = None
        self.interactive_experience_optimizer: Optional[Any] = None
        
        # 集成状态
        self.new_services_integrated = False
        self.integration_results: Optional[dict] = None
        
        logger.info("EnhancedAppState 初始化完成")
    
    async def integrate_new_services(self) -> dict:
        """
        异步集成新服务
        
        Returns:
            集成结果字典
        """
        if self.new_services_integrated:
            logger.info("新服务已经集成，返回缓存结果")
            return self.integration_results or {"status": "already_integrated"}
        
        logger.info("开始集成新服务...")
        
        try:
            # 执行安全集成
            integration_results = await self.service_integration_manager.safe_integrate_all_services()
            
            # 保存集成结果
            self.integration_results = integration_results
            
            # 更新集成状态
            if integration_results["successful_integrations"] > 0:
                self.new_services_integrated = True
                logger.info(f"新服务集成完成: {integration_results['successful_integrations']}/{integration_results['total_services']} 成功")
            else:
                logger.warning("所有新服务集成失败")
            
            return integration_results
            
        except Exception as e:
            logger.error(f"集成新服务时发生异常: {e}")
            return {
                "total_services": 0,
                "successful_integrations": 0,
                "failed_integrations": 1,
                "overall_status": "error",
                "error": str(e)
            }
    
    def get_service_status(self) -> dict:
        """
        获取所有服务状态（包括新服务）
        
        Returns:
            服务状态字典
        """
        status = {
            "original_services": self._get_original_services_status(),
            "new_services": self.service_integration_manager.get_integration_status(),
            "integration_completed": self.new_services_integrated
        }
        
        return status
    
    def _get_original_services_status(self) -> dict:
        """获取原有服务状态"""
        original_services = [
            "memory_service", "wiki_service", "synthesis_engine", 
            "expert_service", "user_profile_service", "session_management_service",
            "universal_context_service", "fact_extraction_service",
            "intent_analysis_service", "personal_context_service",
            "prompt_optimization_service", "interaction_manager",
            "protocol_service", "collaboration_service", "chat_service"
        ]
        
        status = {}
        for service_name in original_services:
            service = getattr(self, service_name, None)
            status[service_name] = {
                "available": service is not None,
                "type": type(service).__name__ if service else None
            }
        
        return status
    
    async def health_check_all_services(self) -> dict:
        """
        对所有服务进行健康检查
        
        Returns:
            健康检查结果
        """
        results = {
            "timestamp": "2025-08-03T22:00:00",
            "original_services": {},
            "new_services": {},
            "overall_health": "unknown"
        }
        
        # 检查原有服务
        original_services = ["memory_service", "wiki_service", "synthesis_engine"]
        healthy_original = 0
        
        for service_name in original_services:
            service = getattr(self, service_name, None)
            if service is not None:
                results["original_services"][service_name] = {"status": "available"}
                healthy_original += 1
            else:
                results["original_services"][service_name] = {"status": "unavailable"}
        
        # 检查新服务
        if self.new_services_integrated:
            new_service_health = await self.service_integration_manager.health_check_integrated_services()
            results["new_services"] = new_service_health
            healthy_new = sum(1 for status in new_service_health.values() if status.get("status") == "healthy")
        else:
            results["new_services"] = {"message": "Not integrated yet"}
            healthy_new = 0
        
        # 计算总体健康状态
        total_expected = len(original_services) + (4 if self.new_services_integrated else 0)
        total_healthy = healthy_original + healthy_new
        
        if total_healthy == total_expected:
            results["overall_health"] = "excellent"
        elif total_healthy >= total_expected * 0.8:
            results["overall_health"] = "good"
        elif total_healthy >= total_expected * 0.5:
            results["overall_health"] = "degraded"
        else:
            results["overall_health"] = "poor"
        
        return results
    
    # 便捷访问方法
    def has_prompt_building_service(self) -> bool:
        """检查是否有提示词构建服务"""
        return self.prompt_building_service is not None
    
    def has_autonomous_role_creation(self) -> bool:
        """检查是否有自主角色创建系统"""
        return self.autonomous_role_creation_system is not None
    
    def has_enhanced_memory_management(self) -> bool:
        """检查是否有增强记忆管理"""
        return self.enhanced_memory_manager is not None
    
    def has_interactive_experience_optimizer(self) -> bool:
        """检查是否有交互体验优化器"""
        return self.interactive_experience_optimizer is not None

# 工厂函数
def create_enhanced_app_state() -> EnhancedAppState:
    """创建增强版AppState实例"""
    return EnhancedAppState()

# 向后兼容的AppState（默认使用原版）
def create_app_state(enhanced: bool = False) -> OriginalAppState:
    """
    创建AppState实例
    
    Args:
        enhanced: 是否使用增强版本
        
    Returns:
        AppState实例
    """
    if enhanced:
        return create_enhanced_app_state()
    else:
        return OriginalAppState()