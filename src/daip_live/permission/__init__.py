"""
权限管理模块
提供用户权限请求、响应收集和处理功能
基于KISS/YAGNI原则设计的核心权限管理系统
"""

from .user_response_collector import (
    UserResponseCollector,
    ResponseProcessor,
    UserResponseTimeoutError,
    UserResponseValidationError,
    ResponseCollectorConfig
)

from .tui_interface import (
    PermissionTUIInterface,
    PermissionUITheme,
    PermissionUITimeout,
    PermissionUIDisplay,
    PermissionUIError,
    PermissionUITimeoutError,
    PermissionUIValidationError
)

from .permission_manager import (
    PermissionManager,
    PermissionManagerError,
    PermissionCheckError,
    PermissionRequestError,
    SimplePermissionManager
)

from .rule_manager import (
    PermissionRuleManager,
    PermissionRuleManagerInterface,
    PermissionRuleManagerFactory
)

__all__ = [
    # 用户响应收集器
    'UserResponseCollector',
    'ResponseProcessor',
    'UserResponseTimeoutError',
    'UserResponseValidationError',
    'ResponseCollectorConfig',
    
    # TUI界面
    'PermissionTUIInterface',
    'PermissionUITheme',
    'PermissionUITimeout',
    'PermissionUIDisplay',
    'PermissionUIError',
    'PermissionUITimeoutError',
    'PermissionUIValidationError',
    
    # 权限管理器
    'PermissionManager',
    'PermissionManagerError',
    'PermissionCheckError',
    'PermissionRequestError',
    'SimplePermissionManager',
    
    # 权限规则管理器
    'PermissionRuleManager',
    'PermissionRuleManagerInterface',
    'PermissionRuleManagerFactory',
]