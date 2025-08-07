#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-03 22:00:00
@Author  : DAIP-LIVE Team
@File    : service_integration_manager.py
@Description:
    新服务集成管理器 - 安全、渐进式集成新功能到现有系统
    
    设计原则：
    1. 完全向后兼容 - 现有功能不受影响
    2. 渐进式集成 - 可控的服务注册和激活
    3. 错误隔离 - 新服务失败不影响核心系统
    4. 状态监控 - 实时监控集成状态
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

# 确保项目根目录在路径中
project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

@dataclass
class ServiceIntegrationStatus:
    """服务集成状态"""
    service_name: str
    is_available: bool
    is_integrated: bool
    status: str  # "not_started", "initializing", "ready", "error"
    error_message: Optional[str] = None
    last_check: Optional[datetime] = None

@dataclass
class IntegrationConfig:
    """集成配置"""
    enable_prompt_building_service: bool = True
    enable_autonomous_role_creation: bool = True
    enable_enhanced_memory_management: bool = True
    enable_interactive_experience_optimizer: bool = True
    fallback_on_error: bool = True
    validate_before_integration: bool = True

class ServiceIntegrationManager:
    """
    新服务集成管理器
    
    负责安全地将新开发的服务集成到现有AppState中，
    确保向后兼容性和系统稳定性。
    """
    
    def __init__(self, app_state: Any, config: IntegrationConfig = None):
        self.app_state = app_state
        self.config = config or IntegrationConfig()
        self.integration_status: Dict[str, ServiceIntegrationStatus] = {}
        self.base_dir = getattr(app_state, 'base_dir', os.getcwd())
        
        # 初始化集成状态
        self._init_integration_status()
        
        logger.info("ServiceIntegrationManager 初始化完成")
    
    def _init_integration_status(self):
        """初始化集成状态记录"""
        services = [
            "prompt_building_service",
            "autonomous_role_creation_system", 
            "enhanced_memory_manager",
            "interactive_experience_optimizer"
        ]
        
        for service in services:
            self.integration_status[service] = ServiceIntegrationStatus(
                service_name=service,
                is_available=False,
                is_integrated=False,
                status="not_started"
            )
    
    async def safe_integrate_all_services(self) -> Dict[str, Any]:
        """
        安全集成所有新服务
        
        Returns:
            集成结果汇总
        """
        logger.info("开始安全集成所有新服务")
        
        integration_results = {
            "total_services": len(self.integration_status),
            "successful_integrations": 0,
            "failed_integrations": 0,
            "services": {},
            "overall_status": "unknown"
        }
        
        # 按优先级顺序集成服务
        integration_order = [
            ("prompt_building_service", self._integrate_prompt_building_service),
            ("autonomous_role_creation_system", self._integrate_autonomous_role_creation),
            ("enhanced_memory_manager", self._integrate_enhanced_memory_manager),
            ("interactive_experience_optimizer", self._integrate_interactive_experience_optimizer)
        ]
        
        for service_name, integration_func in integration_order:
            try:
                logger.info(f"正在集成服务: {service_name}")
                result = await integration_func()
                integration_results["services"][service_name] = result
                
                if result["success"]:
                    integration_results["successful_integrations"] += 1
                    logger.info(f"✅ {service_name} 集成成功")
                else:
                    integration_results["failed_integrations"] += 1
                    logger.warning(f"⚠️ {service_name} 集成失败: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                integration_results["failed_integrations"] += 1
                integration_results["services"][service_name] = {
                    "success": False,
                    "error": str(e),
                    "integrated": False
                }
                logger.error(f"❌ {service_name} 集成异常: {e}")
        
        # 计算总体状态
        if integration_results["failed_integrations"] == 0:
            integration_results["overall_status"] = "all_successful"
        elif integration_results["successful_integrations"] > 0:
            integration_results["overall_status"] = "partial_success"
        else:
            integration_results["overall_status"] = "all_failed"
        
        logger.info(f"集成完成: {integration_results['successful_integrations']}/{integration_results['total_services']} 成功")
        return integration_results
    
    async def _integrate_prompt_building_service(self) -> Dict[str, Any]:
        """集成提示词构建服务"""
        service_name = "prompt_building_service"
        status = self.integration_status[service_name]
        
        try:
            # 更新状态
            status.status = "initializing"
            status.last_check = datetime.now()
            
            # 检查配置
            if not self.config.enable_prompt_building_service:
                return {"success": False, "error": "Service disabled in config", "integrated": False}
            
            # 验证服务可用性
            if self.config.validate_before_integration:
                validation_result = await self._validate_prompt_building_service()
                if not validation_result["valid"]:
                    return {"success": False, "error": validation_result["error"], "integrated": False}
            
            # 安全导入
            from src.core_services.prompt_building_service import create_prompt_building_service
            
            # 创建服务实例
            templates_dir = os.path.join(self.base_dir, "data", "templates")
            os.makedirs(templates_dir, exist_ok=True)
            
            # 检查是否已存在（避免重复集成）
            if hasattr(self.app_state, 'prompt_building_service'):
                logger.info("提示词构建服务已存在，跳过集成")
                status.is_integrated = True
                status.status = "ready"
                return {"success": True, "message": "Already integrated", "integrated": True}
            
            # 创建服务实例
            prompt_service = create_prompt_building_service(
                templates_dir=templates_dir,
                enable_caching=True
            )
            
            # 验证服务健康状态
            health_status = await prompt_service.get_service_status()
            if health_status["status"] != "healthy":
                return {"success": False, "error": f"Service unhealthy: {health_status}", "integrated": False}
            
            # 安全注册到 app_state
            self.app_state.prompt_building_service = prompt_service
            
            # 更新状态
            status.is_available = True
            status.is_integrated = True
            status.status = "ready"
            
            return {
                "success": True,
                "message": "Prompt building service integrated successfully",
                "integrated": True,
                "service_status": health_status
            }
            
        except Exception as e:
            status.status = "error"
            status.error_message = str(e)
            logger.error(f"集成提示词构建服务失败: {e}")
            return {"success": False, "error": str(e), "integrated": False}
    
    async def _integrate_autonomous_role_creation(self) -> Dict[str, Any]:
        """集成自主角色创建系统"""
        service_name = "autonomous_role_creation_system"
        status = self.integration_status[service_name]
        
        try:
            status.status = "initializing"
            status.last_check = datetime.now()
            
            if not self.config.enable_autonomous_role_creation:
                return {"success": False, "error": "Service disabled in config", "integrated": False}
            
            # 验证服务
            if self.config.validate_before_integration:
                validation_result = await self._validate_autonomous_role_creation()
                if not validation_result["valid"]:
                    return {"success": False, "error": validation_result["error"], "integrated": False}
            
            from src.core_services.autonomous_role_creation_system import create_autonomous_role_creation_system
            
            # 准备存储目录
            roles_dir = os.path.join(self.base_dir, "data", "autonomous_roles")
            os.makedirs(roles_dir, exist_ok=True)
            
            # 检查是否已存在
            if hasattr(self.app_state, 'autonomous_role_creation_system'):
                logger.info("自主角色创建系统已存在，跳过集成")
                status.is_integrated = True
                status.status = "ready"
                return {"success": True, "message": "Already integrated", "integrated": True}
            
            # 创建服务实例
            role_system = create_autonomous_role_creation_system(
                storage_dir=roles_dir
            )
            
            # 验证服务健康状态
            health_status = await role_system.get_system_status()
            if health_status["status"] != "healthy":
                return {"success": False, "error": f"Service unhealthy: {health_status}", "integrated": False}
            
            # 安全注册
            self.app_state.autonomous_role_creation_system = role_system
            
            # 更新状态
            status.is_available = True
            status.is_integrated = True
            status.status = "ready"
            
            return {
                "success": True,
                "message": "Autonomous role creation system integrated successfully",
                "integrated": True,
                "service_status": health_status
            }
            
        except Exception as e:
            status.status = "error"
            status.error_message = str(e)
            logger.error(f"集成自主角色创建系统失败: {e}")
            return {"success": False, "error": str(e), "integrated": False}
    
    async def _integrate_enhanced_memory_manager(self) -> Dict[str, Any]:
        """集成增强记忆管理器"""
        service_name = "enhanced_memory_manager"
        status = self.integration_status[service_name]
        
        try:
            status.status = "initializing"
            status.last_check = datetime.now()
            
            if not self.config.enable_enhanced_memory_management:
                return {"success": False, "error": "Service disabled in config", "integrated": False}
            
            # 尝试导入（可能失败，因为是新功能）
            try:
                from src.core_services.enhanced_memory_management import EnhancedMemoryManager
            except ImportError as e:
                logger.warning(f"Enhanced memory manager not available: {e}")
                return {"success": False, "error": "Module not available", "integrated": False}
            
            # 检查是否已存在
            if hasattr(self.app_state, 'enhanced_memory_manager'):
                logger.info("增强记忆管理器已存在，跳过集成")
                status.is_integrated = True
                status.status = "ready"
                return {"success": True, "message": "Already integrated", "integrated": True}
            
            # 创建服务实例
            memory_manager = EnhancedMemoryManager()
            
            # 安全注册
            self.app_state.enhanced_memory_manager = memory_manager
            
            # 更新状态
            status.is_available = True
            status.is_integrated = True
            status.status = "ready"
            
            return {
                "success": True,
                "message": "Enhanced memory manager integrated successfully",
                "integrated": True
            }
            
        except Exception as e:
            status.status = "error"
            status.error_message = str(e)
            logger.error(f"集成增强记忆管理器失败: {e}")
            return {"success": False, "error": str(e), "integrated": False}
    
    async def _integrate_interactive_experience_optimizer(self) -> Dict[str, Any]:
        """集成交互体验优化器"""
        service_name = "interactive_experience_optimizer"
        status = self.integration_status[service_name]
        
        try:
            status.status = "initializing"
            status.last_check = datetime.now()
            
            if not self.config.enable_interactive_experience_optimizer:
                return {"success": False, "error": "Service disabled in config", "integrated": False}
            
            # 尝试导入
            try:
                from src.core_services.interactive_experience_optimizer import InteractiveExperienceOptimizer
            except ImportError as e:
                logger.warning(f"Interactive experience optimizer not available: {e}")
                return {"success": False, "error": "Module not available", "integrated": False}
            
            # 检查是否已存在
            if hasattr(self.app_state, 'interactive_experience_optimizer'):
                logger.info("交互体验优化器已存在，跳过集成")
                status.is_integrated = True
                status.status = "ready"
                return {"success": True, "message": "Already integrated", "integrated": True}
            
            # 创建服务实例
            experience_optimizer = InteractiveExperienceOptimizer()
            
            # 安全注册
            self.app_state.interactive_experience_optimizer = experience_optimizer
            
            # 更新状态
            status.is_available = True
            status.is_integrated = True
            status.status = "ready"
            
            return {
                "success": True,
                "message": "Interactive experience optimizer integrated successfully",
                "integrated": True
            }
            
        except Exception as e:
            status.status = "error"
            status.error_message = str(e)
            logger.error(f"集成交互体验优化器失败: {e}")
            return {"success": False, "error": str(e), "integrated": False}
    
    async def _validate_prompt_building_service(self) -> Dict[str, Any]:
        """验证提示词构建服务"""
        try:
            from src.core_services.prompt_building_service import create_prompt_building_service
            import tempfile
            
            # 创建临时实例进行验证
            temp_dir = tempfile.mkdtemp()
            test_service = create_prompt_building_service(templates_dir=temp_dir)
            status = await test_service.get_service_status()
            
            return {
                "valid": status["status"] == "healthy",
                "status": status,
                "error": None if status["status"] == "healthy" else f"Service status: {status['status']}"
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    async def _validate_autonomous_role_creation(self) -> Dict[str, Any]:
        """验证自主角色创建系统"""
        try:
            from src.core_services.autonomous_role_creation_system import create_autonomous_role_creation_system
            import tempfile
            
            # 创建临时实例进行验证
            temp_dir = tempfile.mkdtemp()
            test_system = create_autonomous_role_creation_system(storage_dir=temp_dir)
            status = await test_system.get_system_status()
            
            return {
                "valid": status["status"] == "healthy",
                "status": status,
                "error": None if status["status"] == "healthy" else f"System status: {status['status']}"
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def get_integration_status(self) -> Dict[str, Any]:
        """获取集成状态汇总"""
        return {
            "services": {
                name: {
                    "is_available": status.is_available,
                    "is_integrated": status.is_integrated,
                    "status": status.status,
                    "error_message": status.error_message,
                    "last_check": status.last_check.isoformat() if status.last_check else None
                }
                for name, status in self.integration_status.items()
            },
            "overall_integration_rate": sum(
                1 for status in self.integration_status.values() if status.is_integrated
            ) / len(self.integration_status) if self.integration_status else 0.0
        }
    
    async def health_check_integrated_services(self) -> Dict[str, Any]:
        """健康检查已集成的服务"""
        health_results = {}
        
        for service_name, status in self.integration_status.items():
            if not status.is_integrated:
                continue
            
            try:
                service = getattr(self.app_state, service_name, None)
                if service is None:
                    health_results[service_name] = {"status": "not_found"}
                    continue
                
                # 尝试调用健康检查方法
                if hasattr(service, 'get_service_status'):
                    health_status = await service.get_service_status()
                elif hasattr(service, 'get_system_status'):
                    health_status = await service.get_system_status()
                else:
                    health_status = {"status": "unknown", "message": "No health check method"}
                
                health_results[service_name] = health_status
                
            except Exception as e:
                health_results[service_name] = {"status": "error", "error": str(e)}
        
        return health_results

# 工厂函数
def create_service_integration_manager(app_state: Any, config: IntegrationConfig = None) -> ServiceIntegrationManager:
    """创建服务集成管理器实例"""
    return ServiceIntegrationManager(app_state, config)

# 快速集成函数
async def quick_integrate_new_services(app_state: Any) -> Dict[str, Any]:
    """快速集成新服务的便捷函数"""
    manager = create_service_integration_manager(app_state)
    return await manager.safe_integrate_all_services()