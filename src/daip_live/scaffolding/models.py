"""
脚手架功能数据模型定义
遵循SOLID原则，提供清晰的领域模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
import re


class InputType(Enum):
    """输入类型枚举"""
    TEXT = "text"
    FILE = "file"


@dataclass
class ProjectFile:
    """项目文件模型

    Attributes:
        path: 文件路径
        content: 文件内容
        size: 文件大小（字节，可选，会自动计算）
        created_at: 创建时间
    """
    path: str
    size: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)
    _content: str = field(repr=False, default="")

    def __init__(self, path: str, content: str = "", size: Optional[int] = None, created_at: Optional[datetime] = None):
        """初始化ProjectFile"""
        self.path = path
        self._content = content
        self.size = size
        self.created_at = created_at or datetime.now()

        # 自动计算大小
        if self.size is None:
            self.size = len(self._content.encode('utf-8'))

    def update_content(self, new_content: str) -> None:
        """更新文件内容并重新计算大小"""
        self.content = new_content
        self.size = len(new_content.encode('utf-8'))

    @property
    def content(self) -> str:
        """获取文件内容"""
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        """设置文件内容并自动重新计算大小"""
        self._content = value
        self.size = len(value.encode('utf-8'))

    def get_extension(self) -> str:
        """获取文件扩展名"""
        from pathlib import Path
        return Path(self.path).suffix.lower()

    def is_yaml_file(self) -> bool:
        """判断是否为YAML文件"""
        return self.get_extension() in ['.yaml', '.yml']

    def is_markdown_file(self) -> bool:
        """判断是否为Markdown文件"""
        return self.get_extension() == '.md'


@dataclass
class ProjectStructure:
    """项目结构模型

    Attributes:
        files: 文件列表
        description: 项目描述
        generated_at: 生成时间
        file_count: 文件数量（自动计算）
        total_size: 总大小（自动计算）
    """
    files: List[ProjectFile]
    description: str
    generated_at: datetime = field(default_factory=datetime.now)
    file_count: int = field(init=False)
    total_size: int = field(init=False)

    def __post_init__(self):
        """后置处理：计算统计信息"""
        self.file_count = len(self.files)
        self.total_size = sum(file.size for file in self.files)

    def get_file_by_path(self, path: str) -> Optional[ProjectFile]:
        """根据路径查找文件"""
        for file in self.files:
            if file.path == path:
                return file
        return None

    def get_files_by_extension(self, extension: str) -> List[ProjectFile]:
        """根据扩展名获取文件列表"""
        return [file for file in self.files if file.get_extension() == extension]

    def get_yaml_files(self) -> List[ProjectFile]:
        """获取所有YAML文件"""
        return [file for file in self.files if file.is_yaml_file()]

    def get_directory_structure(self) -> dict:
        """获取目录结构"""
        structure = {}
        for file in self.files:
            parts = file.path.split('/')
            current = structure
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            # 最后一个部分是文件名
            if parts[-1] not in current:
                current[parts[-1]] = file
        return structure


@dataclass
class ScaffoldResult:
    """脚手架操作结果

    Attributes:
        is_success: 是否成功
        project_structure: 项目结构（成功时）
        errors: 错误列表
        warnings: 警告列表
    """
    is_success: bool
    project_structure: Optional[ProjectStructure] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @classmethod
    def success(cls, project_structure: ProjectStructure, warnings: List[str] = None) -> 'ScaffoldResult':
        """创建成功结果"""
        return cls(
            is_success=True,
            project_structure=project_structure,
            warnings=warnings or []
        )

    @classmethod
    def failure(cls, errors: List[str], warnings: List[str] = None) -> 'ScaffoldResult':
        """创建失败结果"""
        return cls(
            is_success=False,
            errors=errors,
            warnings=warnings or []
        )

    def has_warnings(self) -> bool:
        """是否有警告"""
        return len(self.warnings) > 0

    def get_summary(self) -> str:
        """获取结果摘要"""
        if self.is_success:
            file_count = self.project_structure.file_count if self.project_structure else 0
            summary = f"成功生成项目结构，包含 {file_count} 个文件"
            if self.has_warnings():
                summary += f"，{len(self.warnings)} 个警告"
            return summary
        else:
            return f"操作失败，{len(self.errors)} 个错误"


@dataclass
class RetryConfig:
    """重试配置

    Attributes:
        max_retries: 最大重试次数
        delay_seconds: 初始延迟时间（秒）
        backoff_factor: 退避因子
    """
    max_retries: int = 3
    delay_seconds: float = 1.0
    backoff_factor: float = 2.0

    def __post_init__(self):
        """验证配置参数"""
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.delay_seconds <= 0:
            raise ValueError("delay_seconds must be positive")
        if self.backoff_factor < 1.0:
            raise ValueError("backoff_factor must be >= 1.0")

    def get_delay(self, attempt: int) -> float:
        """计算指定尝试次数的延迟时间"""
        if attempt <= 0:
            return self.delay_seconds
        return self.delay_seconds * (self.backoff_factor ** (attempt - 1))

    def should_retry(self, attempt: int) -> bool:
        """判断是否应该重试"""
        return attempt <= self.max_retries


@dataclass
class ScaffoldCommand:
    """脚手架命令

    Attributes:
        input_type: 输入类型
        description: 项目描述（文本输入时使用）
        file_path: 文件路径（文件输入时使用）
        auto_confirm: 是否自动确认
    """
    input_type: InputType
    description: str
    file_path: Optional[str] = None
    auto_confirm: bool = False

    def validate(self) -> List[str]:
        """验证命令有效性"""
        errors = []

        if self.input_type == InputType.TEXT:
            if not self.description or not self.description.strip():
                errors.append("文本输入时描述不能为空")
        elif self.input_type == InputType.FILE:
            if not self.file_path:
                errors.append("文件输入时文件路径不能为空")

        return errors

    def get_content_source(self) -> str:
        """获取内容来源描述"""
        if self.input_type == InputType.TEXT:
            return f"文本描述: {self.description[:50]}..."
        else:
            return f"文件: {self.file_path}"


# 自定义异常类
class ValidationError(Exception):
    """验证错误异常"""

    def __init__(self, errors: List[str]):
        self.validation_errors = errors
        error_message = "; ".join(errors)
        super().__init__(f"Validation failed: {error_message}")


class GenerationError(Exception):
    """生成错误异常"""
    pass


class FileCreationError(Exception):
    """文件创建错误异常"""

    def __init__(self, message: str):
        super().__init__(f"File creation failed: {message}")


class ScaffoldExecutionError(Exception):
    """脚手架执行错误异常"""
    pass


class ConfigurationError(Exception):
    """配置错误异常"""
    pass


class NetworkError(Exception):
    """网络错误异常"""
    pass


class TimeoutError(Exception):
    """超时错误异常"""
    pass


@dataclass
class FileOperationError:
    """文件操作错误

    Attributes:
        message: 错误消息
        error_code: 错误代码
        timestamp: 错误发生时间
    """
    message: str
    error_code: str
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"

    def __repr__(self) -> str:
        return f"FileOperationError(message='{self.message}', error_code='{self.error_code}', timestamp={self.timestamp})"


# 工具函数和常量
class ValidationConstants:
    """验证常量"""
    MIN_DESCRIPTION_LENGTH = 10
    MAX_DESCRIPTION_LENGTH = 5000
    MAX_FILE_SIZE = 1024 * 1024  # 1MB
    SUPPORTED_FILE_EXTENSIONS = {'.txt', '.md', '.docx'}

    # YAML文件命名规则
    YAML_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9_/-]+\.ya?ml$')

    # 路径安全规则
    SAFE_PATH_PATTERN = re.compile(r'^[a-zA-Z0-9_/-]+$')


class FileConstants:
    """文件常量"""
    DEFAULT_ROLES_DIR = "roles"
    DEFAULT_WORKFLOWS_DIR = "workflows"
    DEFAULT_CONFIG_FILE = "config.yaml"

    # 文件大小限制（字节）
    MAX_SINGLE_FILE_SIZE = 1024 * 100  # 100KB
    MAX_TOTAL_SIZE = 1024 * 1024 * 10  # 10MB


class ErrorMessages:
    """错误消息常量"""

    # 输入验证错误
    EMPTY_DESCRIPTION = "项目描述不能为空"
    DESCRIPTION_TOO_SHORT = f"项目描述至少需要{ValidationConstants.MIN_DESCRIPTION_LENGTH}个字符"
    DESCRIPTION_TOO_LONG = f"项目描述不能超过{ValidationConstants.MAX_DESCRIPTION_LENGTH}个字符"

    # 文件验证错误
    FILE_NOT_FOUND = "文件不存在"
    FILE_TOO_LARGE = f"文件大小不能超过{ValidationConstants.MAX_FILE_SIZE // (1024*1024)}MB"
    UNSUPPORTED_FILE_FORMAT = "不支持的文件格式"
    FILE_READ_ERROR = "文件读取失败"

    # 生成错误
    GENERATION_TIMEOUT = "生成超时"
    LLM_UNAVAILABLE = "模型服务不可用"
    YAML_FORMAT_ERROR = "YAML格式错误"
    INVALID_PROJECT_STRUCTURE = "无效的项目结构"

    # 文件操作错误
    PERMISSION_DENIED = "权限不足，无法创建文件"
    DISK_FULL = "磁盘空间不足"
    INVALID_PATH = "无效的文件路径"
    FILE_EXISTS = "文件已存在"

    # 配置错误
    INVALID_RETRY_CONFIG = "无效的重试配置"
    MISSING_REQUIRED_CONFIG = "缺少必需的配置项"