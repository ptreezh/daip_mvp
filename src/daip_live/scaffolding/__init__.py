"""
DAIP-LIVE Scaffold 脚手架模块
提供AI驱动的项目结构生成功能
"""

from .command_parser import (
    CommandHistory,
    CommandSuggestion,
    # 命令解析
    ScaffoldCommandParser,
)
from .config_manager import (
    ConfigFormat,
    ConfigSource,
    ConfigValidator,
    ConfigWatcher,
    # 配置管理
    ScaffoldConfig,
)
from .error_handler import (
    ErrorCategory,
    ErrorContext,
    # 错误处理
    ErrorHandler,
    ErrorRecoveryResult,
    ErrorReport,
    ErrorSeverity,
    RetryStrategy,
)
from .file_creation_service import (
    DirectoryStructure,
    FileConflictResolution,
    FileCreationConfig,
    FileCreationResult,
    # 文件创建服务
    FileCreationService,
    FileOperationStatus,
    ValidationRule,
)
from .file_system_adapter import (
    FileOperationResult,
    # 文件系统
    FileSystemAdapter,
)
from .llm_service import (
    AnthropicProvider,
    BaseLLMProvider,
    ConversationContext,
    LLMModelConfig,
    LLMProvider,
    LLMRequest,
    LLMResponse,
    # LLM服务接口
    LLMService,
    LLMServiceConfig,
    LocalProvider,
    MessageRole,
    OllamaProvider,
    OpenAIProvider,
    PromptTemplate,
    PromptVariable,
)
from .models import (
    ConfigurationError,
    ErrorMessages,
    FileConstants,
    FileCreationError,
    FileOperationError,
    GenerationError,
    InputType,
    NetworkError,
    # 数据模型
    ProjectFile,
    ProjectStructure,
    RetryConfig,
    ScaffoldCommand,
    ScaffoldExecutionError,
    ScaffoldResult,
    TimeoutError,
    # 常量
    ValidationConstants,
    # 异常类
    ValidationError,
)
from .preview_confirmation_service import (
    ConfirmationResponse,
    ConfirmationResult,
    FilePreview,
    PreviewAction,
    # 预览确认服务
    PreviewConfirmationService,
    PreviewSummary,
)
from .scaffold_engine import (
    GenerationContext,
    GenerationPhase,
    GenerationRequest,
    GenerationResult,
    # 脚手架引擎
    ScaffoldEngine,
)
from .structure_generator import (
    GenerationStrategy,
    # 项目结构生成器
    ProjectStructureGenerator,
    StructureGeneratorConfig,
    TemplateConfig,
    TemplateEngine,
    TemplateRenderer,
    TemplateType,
)

__version__ = "2.0.0"
__author__ = "DAIP-LIVE Team"

__all__ = [
    # 数据模型
    "ProjectFile",
    "ProjectStructure",
    "ScaffoldResult",
    "ScaffoldCommand",
    "RetryConfig",
    "InputType",
    "FileOperationError",
    # 异常类
    "ValidationError",
    "GenerationError",
    "FileCreationError",
    "ScaffoldExecutionError",
    "ConfigurationError",
    "NetworkError",
    "TimeoutError",
    # 常量
    "ValidationConstants",
    "FileConstants",
    "ErrorMessages",
    # 命令解析
    "ScaffoldCommandParser",
    "CommandSuggestion",
    "CommandHistory",
    # 文件系统
    "FileSystemAdapter",
    "FileOperationResult",
    # 错误处理
    "ErrorHandler",
    "ErrorSeverity",
    "ErrorCategory",
    "ErrorContext",
    "ErrorReport",
    "RetryStrategy",
    "ErrorRecoveryResult",
    # 配置管理
    "ScaffoldConfig",
    "ConfigSource",
    "ConfigValidator",
    "ConfigWatcher",
    "ConfigFormat",
    # 脚手架引擎
    "ScaffoldEngine",
    "GenerationRequest",
    "GenerationContext",
    "GenerationResult",
    "GenerationPhase",
    # 项目结构生成器
    "ProjectStructureGenerator",
    "TemplateEngine",
    "TemplateType",
    "TemplateConfig",
    "GenerationStrategy",
    "StructureGeneratorConfig",
    "TemplateRenderer",
    # LLM服务接口
    "LLMService",
    "LLMProvider",
    "LLMModelConfig",
    "LLMRequest",
    "LLMResponse",
    "LLMServiceConfig",
    "PromptTemplate",
    "PromptVariable",
    "ConversationContext",
    "MessageRole",
    "BaseLLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "LocalProvider",
    "OllamaProvider",
    # 文件创建服务
    "FileCreationService",
    "FileCreationConfig",
    "FileCreationResult",
    "ValidationRule",
    "DirectoryStructure",
    "FileConflictResolution",
    "FileOperationStatus",
    # 预览确认服务
    "PreviewConfirmationService",
    "PreviewAction",
    "ConfirmationResult",
    "FilePreview",
    "PreviewSummary",
    "ConfirmationResponse",
]
