"""
PermissionManager - 权限管理器核心实现
基于KISS/YAGNI原则，专注于核心集成功能
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from daip_live.core.models import (
    PermissionRequestEvent,
    PermissionResponse,
    PermissionResult,
    PermissionInteraction,
    SessionContext,
    ToolPermissionConfig
)

from daip_live.permission.user_response_collector import (
    UserResponseCollector,
    ResponseProcessor
)

logger = logging.getLogger(__name__)


class PermissionManagerError(Exception):
    """权限管理器基础异常"""
    pass


class PermissionCheckError(PermissionManagerError):
    """权限检查异常"""
    pass


class PermissionRequestError(PermissionManagerError):
    """权限请求异常"""
    pass


class PermissionManager:
    """
    权限管理器 - 核心权限管理功能
    基于KISS原则，专注于基础权限检查和用户响应收集
    """
    
    def __init__(self, user_input_queue: asyncio.Queue, tui_interface):
        """
        初始化权限管理器
        
        Args:
            user_input_queue: 用户输入队列
            tui_interface: TUI界面接口
        """
        self.user_input_queue = user_input_queue
        self.tui_interface = tui_interface
        self.permission_config = ToolPermissionConfig(
            default="ask",
            tools={}
        )
        self._permission_cache: Dict[str, PermissionResponse] = {}
        self._interaction_history: Dict[str, PermissionInteraction] = {}
        
        # 初始化响应收集器 - KISS原则
        self.response_collector = UserResponseCollector(user_input_queue)
        self.response_processor = ResponseProcessor()
        
        logger.info("PermissionManager initialized with KISS/YAGNI design")
    
    async def check_permission(
        self,
        tool_name: str,
        args: Dict[str, Any],
        session_context: SessionContext,
        timeout: Optional[float] = None
    ) -> PermissionResult:
        """
        检查工具权限 - 核心功能
        
        Args:
            tool_name: 工具名称
            args: 工具参数
            session_context: 会话上下文
            timeout: 超时时间（秒）
            
        Returns:
            PermissionResult: 权限检查结果
        """
        logger.info(f"Checking permission for tool: {tool_name}")
        
        # 创建权限请求
        request = PermissionRequestEvent(
            tool_name=tool_name,
            args=args,
            timeout_seconds=timeout or 30.0
        )
        
        try:
            # 1. 检查缓存（KISS原则：简单的内存缓存）
            cached_response = self._check_cache(tool_name)
            if cached_response:
                logger.info(f"Using cached permission for {tool_name}: {cached_response}")
                return self._create_permission_result(cached_response, request, cached=True)
            
            # 2. 检查权限规则
            permission_status = self._get_permission_status(tool_name)
            
            if permission_status == "allow":
                # 直接允许
                return self._create_permission_result(PermissionResponse.GRANT, request)
            elif permission_status == "deny":
                # 直接拒绝
                return self._create_permission_result(PermissionResponse.DENY, request)
            elif permission_status == "ask":
                # 需要用户确认
                user_response = await self.request_permission(request, timeout)
                return self._create_permission_result(user_response, request)
            else:
                # 未知状态，默认拒绝（安全优先）
                logger.warning(f"Unknown permission status: {permission_status}, defaulting to deny")
                return self._create_permission_result(PermissionResponse.DENY, request)
                
        except Exception as e:
            logger.error(f"Error checking permission for {tool_name}: {e}")
            # 错误时默认拒绝（安全优先）
            return self._create_permission_result(PermissionResponse.DENY, request, error=str(e))
    
    async def request_permission(
        self,
        request: PermissionRequestEvent,
        timeout: Optional[float] = None
    ) -> PermissionResponse:
        """
        请求用户权限 - 用户交互功能
        
        Args:
            request: 权限请求事件
            timeout: 超时时间（秒）
            
        Returns:
            PermissionResponse: 用户响应
        """
        logger.info(f"Requesting permission for tool: {request.tool_name}")
        
        try:
            # 直接使用响应收集器收集用户响应（KISS原则）
            response = await self.response_collector.collect_response(request, timeout)
            
            # 处理特殊响应（记住选择）
            if response in [PermissionResponse.ALWAYS, PermissionResponse.NEVER]:
                self._cache_permission(request.tool_name, response)
                logger.info(f"Cached permission for {request.tool_name}: {response}")
            
            logger.info(f"User response for {request.tool_name}: {response}")
            return response
            
        except asyncio.TimeoutError:
            logger.warning(f"Permission request timed out for {request.tool_name}")
            # 超时默认拒绝（安全优先）
            return PermissionResponse.DENY
            
        except Exception as e:
            logger.error(f"Error requesting permission for {request.tool_name}: {e}")
            # 错误默认拒绝（安全优先）
            return PermissionResponse.DENY
    
    def get_permission_status(self, tool_name: str) -> str:
        """
        获取工具权限状态
        
        Args:
            tool_name: 工具名称
            
        Returns:
            str: 权限状态 (allow/deny/ask)
        """
        return self.permission_config.tools.get(tool_name, self.permission_config.default)
    
    def set_permission_rule(self, tool_name: str, permission: str) -> None:
        """
        设置权限规则 - 管理功能
        
        Args:
            tool_name: 工具名称
            permission: 权限设置 (allow/deny/ask)
        """
        if permission not in ["allow", "deny", "ask"]:
            raise ValueError(f"Invalid permission: {permission}. Must be allow/deny/ask")
        
        self.permission_config.tools[tool_name] = permission
        logger.info(f"Set permission rule for {tool_name}: {permission}")
    
    def _check_cache(self, tool_name: str) -> Optional[PermissionResponse]:
        """
        检查权限缓存 - KISS原则：简单的内存缓存
        
        Args:
            tool_name: 工具名称
            
        Returns:
            Optional[PermissionResponse]: 缓存的响应或None
        """
        return self._permission_cache.get(tool_name)
    
    def _cache_permission(self, tool_name: str, response: PermissionResponse) -> None:
        """
        缓存权限结果 - KISS原则
        
        Args:
            tool_name: 工具名称
            response: 权限响应
        """
        self._permission_cache[tool_name] = response
    
    def _get_permission_status(self, tool_name: str) -> str:
        """
        获取权限状态 - 内部方法
        
        Args:
            tool_name: 工具名称
            
        Returns:
            str: 权限状态
        """
        return self.permission_config.tools.get(tool_name, self.permission_config.default)
    
    def _create_permission_result(
        self,
        response: PermissionResponse,
        request: PermissionRequestEvent,
        cached: bool = False,
        error: Optional[str] = None
    ) -> PermissionResult:
        """
        创建权限结果 - 辅助方法
        
        Args:
            response: 权限响应
            request: 权限请求
            cached: 是否来自缓存
            error: 错误信息
            
        Returns:
            PermissionResult: 权限结果
        """
        granted = response in [PermissionResponse.GRANT, PermissionResponse.ALWAYS]
        
        return PermissionResult(
            granted=granted,
            response=response,
            request_id=request.request_id,
            reason=self._get_reason(response, request.tool_name),
            timeout=False,
            cached=cached,
            remembered=response in [PermissionResponse.ALWAYS, PermissionResponse.NEVER],
            error_message=error,
            timestamp=datetime.now(timezone.utc),
            response_time_seconds=0.0  # 简化实现，YAGNI原则
        )
    
    def _get_reason(self, response: PermissionResponse, tool_name: str) -> str:
        """
        获取权限结果原因 - 辅助方法
        
        Args:
            response: 权限响应
            tool_name: 工具名称
            
        Returns:
            str: 原因描述
        """
        reasons = {
            PermissionResponse.GRANT: f"Permission granted for {tool_name}",
            PermissionResponse.DENY: f"Permission denied for {tool_name}",
            PermissionResponse.ALWAYS: f"Permission always granted for {tool_name}",
            PermissionResponse.NEVER: f"Permission never granted for {tool_name}",
            PermissionResponse.CANCEL: f"Permission request cancelled for {tool_name}",
        }
        
        return reasons.get(response, f"Unknown response for {tool_name}")
    
    def clear_permission_cache(self) -> None:
        """
        清空权限缓存 - 管理功能
        """
        self._permission_cache.clear()
        logger.info("Permission cache cleared")
    
    def get_cached_permissions(self) -> Dict[str, PermissionResponse]:
        """
        获取缓存的权限 - 管理功能
        
        Returns:
            Dict[str, PermissionResponse]: 缓存的权限
        """
        return self._permission_cache.copy()


# 简化版本的PermissionManager，专注于核心功能
class SimplePermissionManager(PermissionManager):
    """
    简化权限管理器 - 极致KISS原则实现
    只包含最基础的权限检查功能
    """
    
    def __init__(self, user_input_queue: asyncio.Queue, tui_interface):
        super().__init__(user_input_queue, tui_interface)
        # 极简配置：只支持三种基本状态
        self._simple_rules = {
            "allow": PermissionResponse.GRANT,
            "deny": PermissionResponse.DENY,
            "ask": PermissionResponse.ALWAYS  # 使用ALWAYS代替ASK，因为ASK不存在
        }
        logger.info("SimplePermissionManager initialized with minimal design")