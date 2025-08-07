# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 10:30:00
@Author  : DAIP-LIVE Team
@File    : exceptions.py
@Description:
    Centralized exception handling for DAIP backend.
    Defines all custom exception types and error handling utilities.
"""

from typing import Optional, Dict, Any, List
from enum import Enum
import logging
from datetime import datetime
import traceback


class ErrorCode(Enum):
    """错误代码枚举"""
    
    # 通用错误 (1000-1999)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    
    # 数据库错误 (2000-2999)
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"
    DATABASE_TIMEOUT = "DATABASE_TIMEOUT"
    DATABASE_CONSTRAINT_VIOLATION = "DATABASE_CONSTRAINT_VIOLATION"
    
    # 服务错误 (3000-3999)
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    SERVICE_TIMEOUT = "SERVICE_TIMEOUT"
    SERVICE_INITIALIZATION_ERROR = "SERVICE_INITIALIZATION_ERROR"
    
    # LLM错误 (4000-4999)
    LLM_ERROR = "LLM_ERROR"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    LLM_RATE_LIMIT = "LLM_RATE_LIMIT"
    LLM_MODEL_NOT_FOUND = "LLM_MODEL_NOT_FOUND"
    LLM_INVALID_REQUEST = "LLM_INVALID_REQUEST"
    
    # 会话错误 (5000-5999)
    SESSION_ERROR = "SESSION_ERROR"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
    SESSION_LIMIT_EXCEEDED = "SESSION_LIMIT_EXCEEDED"
    
    # 任务错误 (6000-6999)
    TASK_ERROR = "TASK_ERROR"
    TASK_TIMEOUT = "TASK_TIMEOUT"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    TASK_EXECUTION_ERROR = "TASK_EXECUTION_ERROR"
    TASK_QUEUE_FULL = "TASK_QUEUE_FULL"
    
    # 工作流错误 (7000-7999)
    WORKFLOW_ERROR = "WORKFLOW_ERROR"
    WORKFLOW_NOT_FOUND = "WORKFLOW_NOT_FOUND"
    WORKFLOW_VALIDATION_ERROR = "WORKFLOW_VALIDATION_ERROR"
    WORKFLOW_EXECUTION_ERROR = "WORKFLOW_EXECUTION_ERROR"
    
    # 配置错误 (8000-8999)
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    CONFIGURATION_INVALID = "CONFIGURATION_INVALID"
    CONFIGURATION_MISSING = "CONFIGURATION_MISSING"
    
    # WebSocket错误 (9000-9999)
    WEBSOCKET_ERROR = "WEBSOCKET_ERROR"
    WEBSOCKET_CONNECTION_ERROR = "WEBSOCKET_CONNECTION_ERROR"
    WEBSOCKET_MESSAGE_ERROR = "WEBSOCKET_MESSAGE_ERROR"
    WEBSOCKET_AUTHENTICATION_ERROR = "WEBSOCKET_AUTHENTICATION_ERROR"


class DAIPException(Exception):
    """DAIP系统基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.now()
        
        # 设置错误状态码
        self.status_code = self._get_status_code()
        
        super().__init__(self.message)
    
    def _get_status_code(self) -> int:
        """根据错误代码获取HTTP状态码"""
        code_ranges = {
            range(1000, 2000): 500,  # 通用错误
            range(2000, 3000): 500,  # 数据库错误
            range(3000, 4000): 503,  # 服务错误
            range(4000, 5000): 500,  # LLM错误
            range(5000, 6000): 400,  # 会话错误
            range(6000, 7000): 400,  # 任务错误
            range(7000, 8000): 400,  # 工作流错误
            range(8000, 9000): 500,  # 配置错误
            range(9000, 10000): 500,  # WebSocket错误
        }
        
        # Handle error codes that don't follow the number_pattern format
        error_value = self.error_code.value
        if '_' in error_value:
            try:
                code_prefix = error_value.split('_')[0]
                if code_prefix.isdigit():
                    code_num = int(code_prefix)
                    for code_range, status_code in code_ranges.items():
                        if code_num in code_range:
                            return status_code
            except ValueError:
                pass
        
        # Default fallback
        return 500
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "timestamp": self.timestamp.isoformat(),
                "status_code": self.status_code
            }
        }
        
        if self.details:
            result["error"]["details"] = self.details
        
        if self.cause:
            result["error"]["cause"] = str(self.cause)
        
        return result


# ============================================================================
# 认知代理相关异常
# ============================================================================

class CognitiveAgentError(DAIPException):
    """认知代理相关异常基类"""
    pass


class AgentNotFoundError(CognitiveAgentError):
    """代理未找到异常"""
    pass


class AgentInitializationError(CognitiveAgentError):
    """代理初始化异常"""
    pass


class CognitiveDiversityError(CognitiveAgentError):
    """认知多样性不足异常"""
    pass


class AgentCommunicationError(CognitiveAgentError):
    """代理通信异常"""
    pass


# ============================================================================
# 工作流相关异常
# ============================================================================

class WorkflowError(DAIPException):
    """工作流相关异常基类"""
    pass


class WorkflowDefinitionError(WorkflowError):
    """工作流定义异常"""
    pass


class WorkflowExecutionError(WorkflowError):
    """工作流执行异常"""
    pass


class PrimitiveNotFoundError(WorkflowError):
    """制度原语未找到异常"""
    pass


class WorkflowValidationError(WorkflowError):
    """工作流验证异常"""
    pass


class WorkflowTimeoutError(WorkflowError):
    """工作流超时异常"""
    pass


# ============================================================================
# 记忆和知识相关异常
# ============================================================================

class MemoryError(DAIPException):
    """记忆系统相关异常基类"""
    pass


class MemoryStorageError(MemoryError):
    """记忆存储异常"""
    pass


class MemoryRetrievalError(MemoryError):
    """记忆检索异常"""
    pass


class KnowledgeError(DAIPException):
    """知识系统相关异常基类"""
    pass


class KnowledgeConflictError(KnowledgeError):
    """知识冲突异常"""
    pass


class WikiError(DAIPException):
    """Wiki系统相关异常基类"""
    pass


class WikiPageNotFoundError(WikiError):
    """Wiki页面未找到异常"""
    pass


class WikiVersionConflictError(WikiError):
    """Wiki版本冲突异常"""
    pass


# ============================================================================
# 集体智慧涌现相关异常
# ============================================================================

class EmergenceError(DAIPException):
    """集体智慧涌现相关异常基类"""
    pass


class EmergenceCalculationError(EmergenceError):
    """涌现计算异常"""
    pass


class ConsensusError(DAIPException):
    """共识相关异常基类"""
    pass


class ConsensusCalculationError(ConsensusError):
    """共识计算异常"""
    pass


class InsufficientDataError(EmergenceError):
    """数据不足异常"""
    pass


# ============================================================================
# 辩论相关异常
# ============================================================================

class DebateError(DAIPException):
    """辩论相关异常基类"""
    pass


class DebateSetupError(DebateError):
    """辩论设置异常"""
    pass


class ArgumentValidationError(DebateError):
    """论证验证异常"""
    pass


class DebateFlowError(DebateError):
    """辩论流程异常"""
    pass


# ============================================================================
# LLM和外部服务相关异常
# ============================================================================

class LLMError(DAIPException):
    """LLM相关异常基类"""
    pass


class LLMConnectionError(LLMError):
    """LLM连接异常"""
    pass


class LLMRateLimitError(LLMError):
    """LLM速率限制异常"""
    pass


class LLMTokenLimitError(LLMError):
    """LLM token限制异常"""
    pass


class LLMResponseError(LLMError):
    """LLM响应异常"""
    pass


# ============================================================================
# 数据库和存储相关异常
# ============================================================================

class DatabaseError(DAIPException):
    """数据库相关异常基类"""
    pass


class DatabaseConnectionError(DatabaseError):
    """数据库连接异常"""
    pass


class DataValidationError(DatabaseError):
    """数据验证异常"""
    pass


class DataIntegrityError(DatabaseError):
    """数据完整性异常"""
    pass


# ============================================================================
# 配置和系统相关异常
# ============================================================================

class ConfigurationError(DAIPException):
    """配置相关异常"""
    pass


class SystemResourceError(DAIPException):
    """系统资源异常"""
    pass


class AuthenticationError(DAIPException):
    """认证异常"""
    pass


class AuthorizationError(DAIPException):
    """授权异常"""
    pass


# ============================================================================
# 用户输入和验证相关异常
# ============================================================================

class ValidationError(DAIPException):
    """验证异常基类"""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            details={"field": field, **(details or {})}
        )


class InputValidationError(ValidationError):
    """输入验证异常"""
    pass


class ParameterError(ValidationError):
    """参数异常"""
    pass


class NotFoundError(DAIPException):
    """资源未找到错误"""
    
    def __init__(self, resource_type: str, resource_id: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            error_code=ErrorCode.NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": resource_id, **(details or {})}
        )


class ConflictError(DAIPException):
    """冲突错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.CONFLICT,
            details=details
        )


class AuthenticationError(DAIPException):
    """认证错误"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHENTICATION_ERROR,
            details=details
        )


class AuthorizationError(DAIPException):
    """授权错误"""
    
    def __init__(self, message: str = "Authorization failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHORIZATION_ERROR,
            details=details
        )


class ServiceUnavailableError(DAIPException):
    """服务不可用错误"""
    
    def __init__(self, service_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Service unavailable: {service_name}",
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            details={"service_name": service_name, **(details or {})}
        )


class SessionError(DAIPException):
    """会话错误"""
    
    def __init__(self, message: str, session_id: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.SESSION_ERROR,
            details={"session_id": session_id, **(details or {})}
        )


class TaskError(DAIPException):
    """任务错误"""
    
    def __init__(self, message: str, task_id: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.TASK_ERROR,
            details={"task_id": task_id, **(details or {})}
        )


class WebSocketError(DAIPException):
    """WebSocket错误"""
    
    def __init__(self, message: str, connection_id: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.WEBSOCKET_ERROR,
            details={"connection_id": connection_id, **(details or {})}
        )


class ForumServiceError(DAIPException):
    """Forum服务错误"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.SERVICE_UNAVAILABLE,
            details=details
        )


class DebateOrchestrationError(DebateError):
    """辩论编排错误"""
    pass


# ============================================================================
# 异常处理工具函数
# ============================================================================

def handle_exception(exception: Exception) -> Dict[str, Any]:
    """统一异常处理函数"""
    if isinstance(exception, DAIPException):
        return exception.to_dict()
    else:
        return {
            "error_type": "UnhandledException",
            "error_code": "UNKNOWN_ERROR",
            "message": str(exception),
            "details": {"exception_type": type(exception).__name__}
        }


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.error_stats = {
            "total_errors": 0,
            "errors_by_code": {},
            "errors_by_service": {},
            "recent_errors": []
        }
    
    def handle_exception(self, exception: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """处理异常"""
        self.error_stats["total_errors"] += 1
        
        # 如果是DAIPException，直接使用
        if isinstance(exception, DAIPException):
            error_dict = exception.to_dict()
            error_code = exception.error_code
        else:
            # 转换为DAIPException
            daip_exception = DAIPException(
                message=str(exception),
                error_code=ErrorCode.INTERNAL_ERROR,
                details={"original_type": type(exception).__name__},
                cause=exception
            )
            error_dict = daip_exception.to_dict()
            error_code = ErrorCode.INTERNAL_ERROR
        
        # 添加上下文信息
        if context:
            error_dict["error"]["context"] = context
        
        # 更新统计信息
        self._update_error_stats(error_code, context)
        
        # 记录错误日志
        self._log_error(exception, error_dict, context)
        
        return error_dict
    
    def _update_error_stats(self, error_code: ErrorCode, context: Optional[Dict[str, Any]] = None):
        """更新错误统计"""
        # 按错误代码统计
        if error_code.value not in self.error_stats["errors_by_code"]:
            self.error_stats["errors_by_code"][error_code.value] = 0
        self.error_stats["errors_by_code"][error_code.value] += 1
        
        # 按服务统计
        if context and "service" in context:
            service = context["service"]
            if service not in self.error_stats["errors_by_service"]:
                self.error_stats["errors_by_service"][service] = 0
            self.error_stats["errors_by_service"][service] += 1
        
        # 记录最近错误
        self.error_stats["recent_errors"].append({
            "code": error_code.value,
            "timestamp": datetime.now().isoformat(),
            "context": context
        })
        
        # 保持最近错误列表在合理大小
        if len(self.error_stats["recent_errors"]) > 100:
            self.error_stats["recent_errors"] = self.error_stats["recent_errors"][-100:]
    
    def _log_error(self, exception: Exception, error_dict: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
        """记录错误日志"""
        error_info = error_dict["error"]
        
        # 基本错误信息
        log_message = f"Error: {error_info['message']} (Code: {error_info['code']})"
        
        # 添加上下文信息
        if context:
            log_message += f" Context: {context}"
        
        # 根据错误级别选择日志级别
        if error_info["code"] in [
            ErrorCode.AUTHENTICATION_ERROR.value,
            ErrorCode.AUTHORIZATION_ERROR.value,
            ErrorCode.VALIDATION_ERROR.value
        ]:
            self.logger.warning(log_message)
        else:
            self.logger.error(log_message, exc_info=exception)
    
    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计"""
        return self.error_stats.copy()
    
    def clear_error_stats(self):
        """清空错误统计"""
        self.error_stats = {
            "total_errors": 0,
            "errors_by_code": {},
            "errors_by_service": {},
            "recent_errors": []
        }


# 全局错误处理器实例
_error_handler: Optional[ErrorHandler] = None


def get_error_handler(logger: logging.Logger = None) -> ErrorHandler:
    """获取错误处理器实例"""
    global _error_handler
    
    if _error_handler is None:
        if logger is None:
            logger = logging.getLogger(__name__)
        _error_handler = ErrorHandler(logger)
    
    return _error_handler


def handle_exception(exception: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """处理异常的便捷函数"""
    handler = get_error_handler()
    return handler.handle_exception(exception, context)


def create_validation_error(message: str, field: str = None, **kwargs) -> ValidationError:
    """创建验证错误的便捷函数"""
    return ValidationError(message, field, kwargs)


def create_not_found_error(resource_type: str, resource_id: str, **kwargs) -> NotFoundError:
    """创建未找到错误的便捷函数"""
    return NotFoundError(resource_type, resource_id, kwargs)


def create_authentication_error(message: str = "Authentication failed", **kwargs) -> AuthenticationError:
    """创建认证错误的便捷函数"""
    return AuthenticationError(message, kwargs)


def create_authorization_error(message: str = "Authorization failed", **kwargs) -> AuthorizationError:
    """创建授权错误的便捷函数"""
    return AuthorizationError(message, kwargs)


def create_service_unavailable_error(service_name: str, **kwargs) -> ServiceUnavailableError:
    """创建服务不可用错误的便捷函数"""
    return ServiceUnavailableError(service_name, kwargs)


def create_llm_error(message: str, model: str = "", **kwargs) -> LLMError:
    """创建LLM错误的便捷函数"""
    return LLMError(message, model, kwargs)


def create_task_error(message: str, task_id: str = "", **kwargs) -> TaskError:
    """创建任务错误的便捷函数"""
    return TaskError(message, task_id, kwargs)


def create_workflow_error(message: str, workflow_name: str = "", **kwargs) -> WorkflowError:
    """创建工作流错误的便捷函数"""
    return WorkflowError(message, workflow_name, kwargs)


def create_configuration_error(message: str, config_key: str = "", **kwargs) -> ConfigurationError:
    """创建配置错误的便捷函数"""
    return ConfigurationError(message, config_key, kwargs)


def create_websocket_error(message: str, connection_id: str = "", **kwargs) -> WebSocketError:
    """创建WebSocket错误的便捷函数"""
    return WebSocketError(message, connection_id, kwargs)


def create_error_response(
    error_type: str,
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """创建标准错误响应"""
    return {
        "success": False,
        "error": {
            "error_type": error_type,
            "error_code": error_code or error_type,
            "message": message,
            "details": details or {}
        }
    }