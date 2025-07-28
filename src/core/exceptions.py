"""
系统异常类定义
定义所有系统级别的异常类和错误处理机制
"""

from typing import Optional, Dict, Any


class DAIPException(Exception):
    """DAIP系统基础异常类"""
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


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
    pass


class InputValidationError(ValidationError):
    """输入验证异常"""
    pass


class ParameterError(ValidationError):
    """参数异常"""
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