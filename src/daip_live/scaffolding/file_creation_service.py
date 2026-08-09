"""
文件创建服务
提供安全、可配置的文件创建功能
"""

import logging
import os
import shutil
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

from .models import ProjectFile, ProjectStructure, ValidationError

logger = logging.getLogger(__name__)


class FileOperationStatus(Enum):
    """文件操作状态枚举"""

    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"
    CONFLICT = "conflict"
    VALIDATION_FAILED = "validation_failed"

    @classmethod
    def from_string(cls, value: str) -> "FileOperationStatus":
        """从字符串获取状态"""
        status_map = {
            "success": cls.SUCCESS,
            "skipped": cls.SKIPPED,
            "failed": cls.FAILED,
            "conflict": cls.CONFLICT,
            "validation_failed": cls.VALIDATION_FAILED,
        }
        return status_map.get(value.lower(), cls.SUCCESS)


class FileConflictResolution(Enum):
    """文件冲突解决策略枚举"""

    FAIL = "fail"
    SKIP = "skip"
    OVERWRITE = "overwrite"
    BACKUP = "backup"
    MERGE = "merge"

    @classmethod
    def from_string(cls, value: str) -> "FileConflictResolution":
        """从字符串获取策略"""
        strategy_map = {
            "fail": cls.FAIL,
            "skip": cls.SKIP,
            "overwrite": cls.OVERWRITE,
            "backup": cls.BACKUP,
            "merge": cls.MERGE,
        }
        return strategy_map.get(value.lower(), cls.FAIL)


@dataclass
class ValidationRule:
    """验证规则"""

    name: str
    validator: Callable[[ProjectFile], bool]
    description: str = ""
    condition: Optional[Callable[[ProjectFile], bool]] = None  # 条件满足时才验证
    is_enabled: bool = True

    def validate(self) -> list[str]:
        """验证规则本身"""
        errors = []

        if not self.name.strip():
            errors.append("规则名称不能为空")

        if not callable(self.validator):
            errors.append("验证器必须是可调用对象")

        return errors

    def should_validate(self, file: ProjectFile) -> bool:
        """判断是否应该验证此文件"""
        if not self.is_enabled:
            return False

        if self.condition is None:
            return True

        try:
            return self.condition(file)
        except Exception:
            logger.warning(f"验证规则 {self.name} 条件检查失败，默认跳过验证")
            return False

    def validate_file(self, file: ProjectFile) -> tuple[bool, Optional[str]]:
        """验证文件"""
        try:
            if not self.should_validate(file):
                return True, None

            is_valid = self.validator(file)
            error_message = (
                None
                if is_valid
                else f"验证规则 '{self.description or self.name}' 未通过"
            )
            return is_valid, error_message

        except Exception as e:
            error_message = f"验证规则 '{self.name}' 执行失败: {str(e)}"
            logger.error(error_message)
            return False, error_message


@dataclass
class FileCreationConfig:
    """文件创建配置"""

    conflict_resolution: FileConflictResolution = FileConflictResolution.OVERWRITE
    create_directories: bool = True
    preserve_permissions: bool = False
    validation_enabled: bool = True
    validation_rules: list[ValidationRule] = field(default_factory=list)
    max_file_size: int = 1024 * 1024  # 1MB
    allowed_extensions: list[str] = field(default_factory=list)
    forbidden_extensions: list[str] = field(default_factory=list)
    allowed_directories: list[str] = field(default_factory=list)
    backup_suffix: str = ".backup"
    default_file_mode: int = 0o644
    default_dir_mode: int = 0o755
    dry_run: bool = False
    atomic_writes: bool = False

    def add_validation_rule(self, rule: ValidationRule) -> None:
        """添加验证规则"""
        self.validation_rules.append(rule)

    def remove_validation_rule(self, name: str) -> bool:
        """移除验证规则"""
        for i, rule in enumerate(self.validation_rules):
            if rule.name == name:
                del self.validation_rules[i]
                return True
        return False

    def get_validation_rule(self, name: str) -> Optional[ValidationRule]:
        """获取验证规则"""
        for rule in self.validation_rules:
            if rule.name == name:
                return rule
        return None


@dataclass
class DirectoryStructure:
    """目录结构"""

    base_path: str
    files: list[ProjectFile] = field(default_factory=list)
    mode: int = 0o755
    created_at: float = field(default_factory=time.time)

    def add_file(self, file: ProjectFile) -> None:
        """添加文件到结构"""
        self.files.append(file)

    def get_file_by_path(self, path: str) -> Optional[ProjectFile]:
        """根据路径获取文件"""
        normalized_path = Path(path).as_posix()
        for file in self.files:
            if Path(file.path).as_posix() == normalized_path:
                return file
        return None

    def group_by_directory(self) -> dict[str, list[ProjectFile]]:
        """按目录分组文件"""
        groups = {}
        for file in self.files:
            file_path = Path(file.path)
            directory = str(file_path.parent) if file_path.parent != Path(".") else ""

            if directory not in groups:
                groups[directory] = []
            groups[directory].append(file)

        return groups

    def get_total_size(self) -> int:
        """获取总大小"""
        return sum(len(file.content) for file in self.files)


@dataclass
class FileCreationResult:
    """文件创建结果"""

    file: ProjectFile
    status: FileOperationStatus
    bytes_written: int = 0
    duration: float = 0.0
    error: Optional[str] = None
    error_code: Optional[str] = None
    existing_path: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """是否成功"""
        return self.status in [FileOperationStatus.SUCCESS, FileOperationStatus.SKIPPED]

    @property
    def is_created(self) -> bool:
        """是否实际创建了文件"""
        return self.status == FileOperationStatus.SUCCESS


class FileCreator(ABC):
    """文件创建器基类"""

    @abstractmethod
    async def create_file(
        self, file: ProjectFile, target_dir: str, config: FileCreationConfig
    ) -> FileCreationResult:
        """创建文件"""
        pass

    @abstractmethod
    def supports_atomic_write(self) -> bool:
        """是否支持原子写入"""
        pass


class StandardFileCreator(FileCreator):
    """标准文件创建器"""

    async def create_file(
        self, file: ProjectFile, target_dir: str, config: FileCreationConfig
    ) -> FileCreationResult:
        """创建文件"""
        start_time = time.time()
        full_path = os.path.join(target_dir, file.path)

        try:
            # 验证文件路径
            self._validate_file_path(full_path, file, config)

            # 检查文件是否存在
            backup_path = None
            if os.path.exists(full_path):
                if config.conflict_resolution == FileConflictResolution.SKIP:
                    return FileCreationResult(
                        file=file,
                        status=FileOperationStatus.SKIPPED,
                        error="文件已存在，跳过创建",
                        error_code="file_exists_skipped",
                    )
                elif config.conflict_resolution == FileConflictResolution.FAIL:
                    return FileCreationResult(
                        file=file,
                        status=FileOperationStatus.FAILED,
                        error=f"文件已存在: {full_path}",
                        error_code="file_exists_conflict",
                    )
                elif config.conflict_resolution == FileConflictResolution.BACKUP:
                    # 创建备份
                    backup_path = self._create_backup(full_path, config)
                elif config.conflict_resolution == FileConflictResolution.OVERWRITE:
                    # 直接覆盖，继续执行
                    pass
                elif config.conflict_resolution == FileConflictResolution.MERGE:
                    # 合并内容
                    try:
                        with open(full_path, encoding="utf-8") as f:
                            existing_content = f.read()
                        file.content = existing_content + "\n" + file.content
                    except Exception as e:
                        return FileCreationResult(
                            file=file,
                            status=FileOperationStatus.FAILED,
                            error=f"合并文件失败: {e}",
                            error_code="merge_failed",
                        )

            # 创建目录（如果需要）
            if config.create_directories:
                await self._create_directories(full_path, config)

            # 写入文件
            bytes_written = await self._write_file_content(
                full_path, file.content, config
            )

            # 设置权限（如果需要）
            if config.preserve_permissions:
                await self._set_file_permissions(full_path, config)

            duration = time.time() - start_time

            # 构建结果，包含备份路径信息
            # 更新文件的路径为绝对路径，以便测试验证
            file_with_full_path = ProjectFile(
                path=full_path,  # 使用绝对路径
                content=file.content,
                size=file.size,
                created_at=file.created_at,
            )

            result_kwargs = {
                "file": file_with_full_path,
                "status": FileOperationStatus.SUCCESS,
                "bytes_written": bytes_written,
                "duration": duration,
            }

            if backup_path:
                result_kwargs["existing_path"] = backup_path
                result_kwargs["metadata"] = {"backup_path": backup_path}

            return FileCreationResult(**result_kwargs)

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"创建文件失败 {full_path}: {str(e)}")
            return FileCreationResult(
                file=file,
                status=FileOperationStatus.FAILED,
                duration=duration,
                error=str(e),
                error_code="creation_error",
            )

    def supports_atomic_write(self) -> bool:
        """标准创建器支持原子写入"""
        return True

    def _validate_file_path(
        self, file_path: str, file: "ProjectFile", config: FileCreationConfig
    ) -> None:
        """验证文件路径"""
        # 检查扩展名
        if config.allowed_extensions:
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in config.allowed_extensions:
                raise ValidationError(f"不允许的文件扩展名: {file_ext}")

        if config.forbidden_extensions:
            file_ext = Path(file_path).suffix.lower()
            if file_ext in config.forbidden_extensions:
                raise ValidationError(f"禁止的文件扩展名: {file_ext}")

        # 检查目录
        if config.allowed_directories:
            # 使用原始的相对路径进行目录检查
            # file.path 是相对路径 (如 "src/main.py")
            original_path = file.path
            path_parts = [
                part for part in original_path.replace("\\", "/").split("/") if part
            ]

            # 获取父目录
            if len(path_parts) >= 2:
                parent_dir = path_parts[-2]  # 文件的直接父目录
            else:
                parent_dir = ""  # 根目录

            if parent_dir not in config.allowed_directories:
                raise ValidationError(f"不允许的目录: {parent_dir}")

    async def _handle_existing_file(
        self, file_path: str, file: ProjectFile, config: FileCreationConfig
    ) -> FileCreationResult:
        """处理已存在的文件"""
        if config.conflict_resolution == FileConflictResolution.SKIP:
            return FileCreationResult(
                file=file,
                status=FileOperationStatus.SKIPPED,
                error=f"文件已存在: {file_path}",
                error_code="file_exists",
            )

        elif config.conflict_resolution == FileConflictResolution.OVERWRITE:
            # 覆盖时不需要额外处理，继续创建
            return FileCreationResult(file=file, status=FileOperationStatus.SUCCESS)

        elif config.conflict_resolution == FileConflictResolution.BACKUP:
            # 创建备份
            backup_path = self._create_backup(file_path, config)
            # 继续创建新文件 (after creating backup, fall through to normal creation)
            # Return a special result that indicates backup was created but continue
            return FileCreationResult(
                file=file,
                status=FileOperationStatus.SUCCESS,
                existing_path=backup_path,
                metadata={"backup_created": True, "backup_path": backup_path},
            )

        elif config.conflict_resolution == FileConflictResolution.FAIL:
            return FileCreationResult(
                file=file,
                status=FileOperationStatus.FAILED,
                error=f"文件已存在: {file_path}",
                error_code="file_exists_conflict",
            )

        elif config.conflict_resolution == FileConflictResolution.MERGE:
            # 简化的合并处理 - 可以根据需要扩展
            try:
                with open(file_path, encoding="utf-8") as f:
                    existing_content = f.read()

                # 简单合并：在文件末尾添加新内容
                merged_content = existing_content + "\n" + file.content
                file.content = merged_content

                return FileCreationResult(file=file, status=FileOperationStatus.SUCCESS)

            except Exception as e:
                return FileCreationResult(
                    file=file,
                    status=FileOperationStatus.FAILED,
                    error=f"合并文件失败: {str(e)}",
                    error_code="merge_error",
                )

        else:
            return FileCreationResult(
                file=file,
                status=FileOperationStatus.FAILED,
                error="未知的冲突解决策略",
                error_code="unknown_strategy",
            )

    def _create_backup(self, file_path: str, config: FileCreationConfig) -> str:
        """创建备份文件"""
        backup_path = file_path + config.backup_suffix
        counter = 1

        # 如果备份文件已存在，添加数字后缀
        while os.path.exists(backup_path):
            backup_path = f"{file_path}{config.backup_suffix}.{counter}"
            counter += 1

        shutil.copy2(file_path, backup_path)
        return backup_path

    async def _create_directories(
        self, file_path: str, config: FileCreationConfig
    ) -> None:
        """创建目录"""
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, mode=config.default_dir_mode, exist_ok=True)

    async def _write_file_content(
        self, file_path: str, content: str, config: FileCreationConfig
    ) -> int:
        """写入文件内容"""
        if config.atomic_writes:
            return await self._atomic_write(file_path, content)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return len(content.encode("utf-8"))

    async def _atomic_write(self, file_path: str, content: str) -> int:
        """原子写入"""
        temp_path = f"{file_path}.tmp.{int(time.time())}"

        try:
            # 写入临时文件
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(content)

            # 原子重命名
            os.replace(temp_path, file_path)

            return len(content.encode("utf-8"))

        except Exception:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    async def _set_file_permissions(
        self, file_path: str, config: FileCreationConfig
    ) -> None:
        """设置文件权限"""
        try:
            os.chmod(file_path, config.default_file_mode)
        except Exception as e:
            logger.warning(f"设置文件权限失败 {file_path}: {str(e)}")


class FileCreationService:
    """文件创建服务"""

    def __init__(self, config: Optional[FileCreationConfig] = None):
        self.config = config or FileCreationConfig()
        self.creator = StandardFileCreator()
        self._setup_default_validation_rules()

    def _setup_default_validation_rules(self) -> None:
        """设置默认验证规则"""
        # 文件大小验证
        size_rule = ValidationRule(
            name="max_file_size",
            validator=lambda file: len(file.content) <= self.config.max_file_size,
            description=f"文件大小超过限制 ({self.config.max_file_size} 字节)",
        )
        self.config.add_validation_rule(size_rule)

        # 文件名验证
        name_rule = ValidationRule(
            name="valid_filename",
            validator=lambda file: self._is_valid_filename(file.path),
            description="文件名包含无效字符",
        )
        self.config.add_validation_rule(name_rule)

        # 内容验证（如果有禁止的扩展名）
        if self.config.forbidden_extensions:
            forbidden_rule = ValidationRule(
                name="forbidden_content",
                validator=lambda file: self._check_forbidden_content(
                    file.content, self.config.forbidden_extensions
                ),
                description="文件内容包含禁止的扩展名引用",
            )
            self.config.add_validation_rule(forbidden_rule)

    def _is_valid_filename(self, path: str) -> bool:
        """检查文件名是否有效"""
        # 检查无效字符
        invalid_chars = ["<", ">", ":", '"', "|", "?", "*", "\x00"]
        filename = os.path.basename(path)
        return not any(char in filename for char in invalid_chars)

    def _check_forbidden_content(
        self, content: str, forbidden_extensions: list[str]
    ) -> bool:
        """检查内容是否包含禁止的扩展名引用"""
        content_lower = content.lower()
        for ext in forbidden_extensions:
            if f".{ext.lstrip('.')}" in content_lower:
                return False
        return True

    async def create_file(
        self,
        file: ProjectFile,
        target_dir: str,
        config: Optional[FileCreationConfig] = None,
    ) -> FileCreationResult:
        """创建单个文件"""
        effective_config = config or self.config

        # 验证文件
        if effective_config.validation_enabled:
            validation_result = self._validate_file(file)
            if not validation_result[0]:
                return FileCreationResult(
                    file=file,
                    status=FileOperationStatus.VALIDATION_FAILED,
                    error=validation_result[1],
                    error_code="validation_failed",
                )

        # 干运行模式
        if effective_config.dry_run:
            return FileCreationResult(
                file=file,
                status=FileOperationStatus.SUCCESS,
                bytes_written=len(file.content.encode("utf-8")),
            )

        return await self.creator.create_file(file, target_dir, effective_config)

    async def create_project_structure(
        self,
        structure: ProjectStructure,
        target_dir: str,
        config: Optional[FileCreationConfig] = None,
    ) -> list[FileCreationResult]:
        """创建项目结构"""
        effective_config = config or self.config
        results = []

        # 创建根目录（如果需要）
        # ProjectStructure doesn't have base_path, so use target_dir directly
        if effective_config.create_directories:
            root_path = target_dir
            os.makedirs(
                root_path, mode=effective_config.default_dir_mode, exist_ok=True
            )

        # 按目录分组创建文件
        grouped_files = DirectoryStructure(
            base_path=target_dir, files=structure.files
        ).group_by_directory()

        for directory, files in grouped_files.items():
            dir_path = os.path.join(target_dir, directory) if directory else target_dir

            # 创建目录
            if effective_config.create_directories and directory:
                os.makedirs(
                    dir_path, mode=effective_config.default_dir_mode, exist_ok=True
                )

            # 创建文件
            for file in files:
                result = await self.create_file(file, target_dir, effective_config)
                results.append(result)

        return results

    def get_creation_summary(self, results: list[FileCreationResult]) -> dict[str, Any]:
        """获取创建摘要"""
        total_files = len(results)
        successful_files = sum(1 for r in results if r.success)
        failed_files = total_files - successful_files
        total_bytes = sum(r.bytes_written for r in results)
        total_duration = sum(r.duration for r in results)

        return {
            "total_files": total_files,
            "successful_files": successful_files,
            "failed_files": failed_files,
            "total_bytes": total_bytes,
            "total_duration": total_duration,
            "success_rate": successful_files / total_files if total_files > 0 else 0.0,
            "average_file_size": total_bytes / successful_files
            if successful_files > 0
            else 0,
            "files_by_status": {
                status.value: [r for r in results if r.status == status]
                for status in FileOperationStatus
            },
        }

    def add_validation_rule(self, rule: ValidationRule) -> None:
        """添加验证规则"""
        self.config.add_validation_rule(rule)

    def remove_validation_rule(self, name: str) -> bool:
        """移除验证规则"""
        return self.config.remove_validation_rule(name)

    def get_validation_rule(self, name: str) -> Optional[ValidationRule]:
        """获取验证规则"""
        return self.config.get_validation_rule(name)

    def enable_validation_rule(self, name: str) -> None:
        """启用验证规则"""
        rule = self.get_validation_rule(name)
        if rule:
            rule.is_enabled = True

    def disable_validation_rule(self, name: str) -> None:
        """禁用验证规则"""
        rule = self.get_validation_rule(name)
        if rule:
            rule.is_enabled = False

    def _validate_file(self, file: ProjectFile) -> tuple[bool, Optional[str]]:
        """验证文件"""
        if not self.config.validation_enabled:
            return True, None

        for rule in self.config.validation_rules:
            if not rule.is_enabled:
                continue

            # 首先验证规则本身
            rule_errors = rule.validate()
            if rule_errors:
                logger.warning(f"验证规则 {rule.name} 无效: {', '.join(rule_errors)}")
                continue

            is_valid, error_message = rule.validate_file(file)
            if not is_valid:
                return False, error_message

        return True, None
