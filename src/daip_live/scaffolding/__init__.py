"""
DAIP-LIVE Scaffold 脚手架模块
提供AI驱动的项目结构生成功能
"""

from .models import (
    # 数据模型
    ProjectFile,
    ProjectStructure,
    ScaffoldResult,
    ScaffoldCommand,
    RetryConfig,
    InputType,
    FileOperationError,

    # 异常类
    ValidationError,
    GenerationError,
    FileCreationError,
    ScaffoldExecutionError,
    ConfigurationError,
    NetworkError,
    TimeoutError,

    # 常量
    ValidationConstants,
    FileConstants,
    ErrorMessages
)

from .command_parser import (
    # 命令解析
    ScaffoldCommandParser,
    CommandSuggestion,
    CommandHistory
)

from .file_system_adapter import (
    # 文件系统
    FileSystemAdapter,
    FileOperationResult
)

from .error_handler import (
    # 错误处理
    ErrorHandler,
    ErrorSeverity,
    ErrorCategory,
    ErrorContext,
    ErrorReport,
    RetryStrategy,
    ErrorRecoveryResult
)

from .config_manager import (
    # 配置管理
    ScaffoldConfig,
    ConfigSource,
    ConfigValidator,
    ConfigWatcher,
    ConfigFormat
)

from .scaffold_engine import (
    # 脚手架引擎
    ScaffoldEngine,
    GenerationRequest,
    GenerationContext,
    GenerationResult,
    GenerationPhase
)

from .structure_generator import (
    # 项目结构生成器
    ProjectStructureGenerator,
    TemplateEngine,
    TemplateType,
    TemplateConfig,
    GenerationStrategy,
    StructureGeneratorConfig,
    TemplateRenderer
)

from .llm_service import (
    # LLM服务接口
    LLMService,
    LLMProvider,
    LLMModelConfig,
    LLMRequest,
    LLMResponse,
    LLMServiceConfig,
    PromptTemplate,
    PromptVariable,
    ConversationContext,
    MessageRole,
    BaseLLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    LocalProvider,
    OllamaProvider
)

from .file_creation_service import (
    # 文件创建服务
    FileCreationService,
    FileCreationConfig,
    FileCreationResult,
    ValidationRule,
    DirectoryStructure,
    FileConflictResolution,
    FileOperationStatus
)

from .preview_confirmation_service import (
    # 预览确认服务
    PreviewConfirmationService,
    PreviewAction,
    ConfirmationResult,
    FilePreview,
    PreviewSummary,
    ConfirmationResponse
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
    "ConfirmationResponse"
]