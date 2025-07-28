#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personal Intelligence Hub - Backend Integration Service

集成现有DAIP-LIVE后端服务的统一接口层
"""

import logging
import httpx
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """服务状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNAVAILABLE = "unavailable"


@dataclass
class BackendServiceConfig:
    """后端服务配置"""
    base_url: str = "http://localhost:8000"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


@dataclass
class ServiceHealthStatus:
    """服务健康状态"""
    service_name: str
    status: ServiceStatus
    response_time: float
    last_check: datetime
    details: Optional[str] = None


class BackendIntegrationService:
    """后端集成服务主类"""
    
    def __init__(self, config: BackendServiceConfig = None):
        self.config = config or BackendServiceConfig()
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout
        )
        self.service_status: Dict[str, ServiceHealthStatus] = {}
        logger.info(f"Backend Integration Service initialized with base URL: {self.config.base_url}")
    
    async def check_backend_health(self) -> Dict[str, ServiceHealthStatus]:
        """检查后端服务健康状态"""
        try:
            start_time = datetime.now()
            response = await self.client.get("/status")
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            if response.status_code == 200:
                status_data = response.json()
                overall_status = status_data.get("overall_status", "unknown")
                
                # 映射状态
                status_mapping = {
                    "healthy": ServiceStatus.HEALTHY,
                    "degraded": ServiceStatus.DEGRADED,
                    "unhealthy": ServiceStatus.UNHEALTHY
                }
                
                backend_status = ServiceHealthStatus(
                    service_name="DAIP-LIVE Backend",
                    status=status_mapping.get(overall_status, ServiceStatus.UNAVAILABLE),
                    response_time=response_time,
                    last_check=datetime.now(),
                    details=f"Components: {len(status_data.get('components', {}))}"
                )
                
                self.service_status["backend"] = backend_status
                logger.info(f"Backend health check successful: {overall_status}")
                
            else:
                self.service_status["backend"] = ServiceHealthStatus(
                    service_name="DAIP-LIVE Backend",
                    status=ServiceStatus.UNHEALTHY,
                    response_time=response_time,
                    last_check=datetime.now(),
                    details=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"Backend health check failed: {e}")
            self.service_status["backend"] = ServiceHealthStatus(
                service_name="DAIP-LIVE Backend",
                status=ServiceStatus.UNAVAILABLE,
                response_time=0.0,
                last_check=datetime.now(),
                details=str(e)
            )
        
        return self.service_status
    
    async def get_available_roles(self) -> List[Dict[str, Any]]:
        """获取可用的认知代理角色"""
        try:
            response = await self.client.get("/api/roles/")
            if response.status_code == 200:
                roles_data = response.json()
                logger.info(f"Retrieved {len(roles_data)} roles from backend")
                return roles_data
            else:
                logger.error(f"Failed to get roles: HTTP {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting roles: {e}")
            return []
    
    async def analyze_intent(self, user_input: str, user_id: str, context: List[Dict] = None) -> Dict[str, Any]:
        """调用意图分析服务"""
        try:
            payload = {
                "user_input": user_input,
                "user_id": user_id,
                "context": context or []
            }
            
            response = await self.client.post("/api/advanced/analyze-intent", json=payload)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Intent analysis successful for input: {user_input[:50]}...")
                return result
            else:
                logger.error(f"Intent analysis failed: HTTP {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error in intent analysis: {e}")
            return {"error": str(e)}
    
    async def start_workflow(self, workflow_type: str, participants: List[str], topic: str) -> Dict[str, Any]:
        """启动工作流执行"""
        try:
            payload = {
                "workflow_type": workflow_type,
                "participants": participants,
                "topic": topic,
                "user_id": "default_user"  # TODO: 从会话中获取真实用户ID
            }
            
            response = await self.client.post("/api/collaboration/start-workflow", json=payload)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Workflow started successfully: {workflow_type}")
                return result
            else:
                logger.error(f"Workflow start failed: HTTP {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error starting workflow: {e}")
            return {"error": str(e)}
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流状态"""
        try:
            response = await self.client.get(f"/api/collaboration/workflow/{workflow_id}/status")
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"Retrieved workflow status for {workflow_id}")
                return result
            else:
                logger.error(f"Failed to get workflow status: HTTP {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {"error": str(e)}
    
    async def execute_consensus(self, inputs: List[Dict[str, Any]], algorithm_type: str = "simple_majority_vote") -> Dict[str, Any]:
        """执行共识计算"""
        try:
            payload = {
                "inputs": inputs,
                "algorithm_type": algorithm_type
            }
            
            response = await self.client.post("/api/protocols/consensus", json=payload)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Consensus calculation completed using {algorithm_type}")
                return result
            else:
                logger.error(f"Consensus calculation failed: HTTP {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error in consensus calculation: {e}")
            return {"error": str(e)}
    
    async def search_wiki(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索Wiki知识库"""
        try:
            params = {"query": query, "limit": limit}
            response = await self.client.get("/api/documents/search", params=params)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Wiki search completed for query: {query}")
                return result.get("results", [])
            else:
                logger.error(f"Wiki search failed: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error in wiki search: {e}")
            return []
    
    async def get_memory_context(self, user_id: str, topic: str) -> Dict[str, Any]:
        """获取记忆上下文"""
        try:
            params = {"user_id": user_id, "topic": topic}
            response = await self.client.get("/api/advanced/memory-context", params=params)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Memory context retrieved for user {user_id}")
                return result
            else:
                logger.error(f"Memory context retrieval failed: HTTP {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error getting memory context: {e}")
            return {"error": str(e)}
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()
        logger.info("Backend integration service closed")


# 全局实例
_backend_service: Optional[BackendIntegrationService] = None


async def get_backend_service() -> BackendIntegrationService:
    """获取后端服务实例（单例模式）"""
    global _backend_service
    if _backend_service is None:
        _backend_service = BackendIntegrationService()
        # 启动时检查后端健康状态
        await _backend_service.check_backend_health()
    return _backend_service


async def cleanup_backend_service():
    """清理后端服务实例"""
    global _backend_service
    if _backend_service:
        await _backend_service.close()
        _backend_service = None