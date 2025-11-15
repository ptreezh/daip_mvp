"""
CLI错误类型定义模块
遵循TDD原则 - 基于测试需求实现
"""

import asyncio
from enum import Enum
from typing import Optional, Dict, Any


class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """错误类别"""
    NETWORK = "network"
    DATABASE = "database"
    VALIDATION = "validation"
    BUSINESS = "business"
    SYSTEM = "system"
    USER_INPUT = "user_input"


class CLIError(Exception):
    """CLI专用错误基类"""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        self.message = message
        self.category = category
        self.severity = severity
        self.error_code = error_code
        self.details = details or {}
        self.original_exception = original_exception
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'category': self.category.value,
            'severity': self.severity.value,
            'error_code': self.error_code,
            'details': self.details,
            'timestamp': asyncio.get_event_loop().time()
        }


class NetworkError(CLIError):
    """网络相关错误"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class DatabaseError(CLIError):
    """数据库相关错误"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class ValidationError(CLIError):
    """验证相关错误"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class BusinessError(CLIError):
    """业务逻辑相关错误"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.BUSINESS,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class SystemError(CLIError):
    """系统相关错误"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class UserInputError(CLIError):
    """用户输入相关错误"""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.USER_INPUT,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )