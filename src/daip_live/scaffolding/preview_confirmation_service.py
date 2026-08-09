"""
预览确认服务
提供项目结构预览和用户确认功能
"""

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from .file_creation_service import (
    FileConflictResolution,
    FileCreationConfig,
    FileCreationService,
)
from .models import ProjectFile, ProjectStructure, ValidationError

logger = logging.getLogger(__name__)


class PreviewAction(Enum):
    """预览动作"""

    CREATE = "create"
    OVERWRITE = "overwrite"
    BACKUP = "backup"
    SKIP = "skip"
    MERGE = "merge"


class ConfirmationResult(Enum):
    """确认结果"""

    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    MODIFIED = "modified"


@dataclass
class FilePreview:
    """文件预览信息"""

    file: ProjectFile
    action: PreviewAction
    exists: bool = False
    conflicts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.conflicts is None:
            self.conflicts = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PreviewSummary:
    """预览摘要"""

    files: list[FilePreview]
    directories: list[str]
    total_files: int
    total_size: int
    conflicts: int
    new_files: int
    modified_files: int


@dataclass
class ConfirmationResponse:
    """确认响应"""

    result: ConfirmationResult
    selected_files: list[ProjectFile] = field(default_factory=list)
    rejected_files: list[ProjectFile] = field(default_factory=list)
    modifications: dict[str, Any] = field(default_factory=dict)
    message: str = ""


class PreviewConfirmationService:
    """预览确认服务"""

    def __init__(self, config: Optional[FileCreationConfig] = None):
        """初始化预览确认服务"""
        self.config = config or FileCreationConfig()
        self.file_service = FileCreationService(config=self.config)
        self.conflict_resolution = self.config.conflict_resolution

    async def generate_preview(
        self,
        structure: ProjectStructure,
        target_dir: str,
        config: Optional[FileCreationConfig] = None,
    ) -> PreviewSummary:
        """生成项目结构预览"""
        if not structure or not structure.files:
            raise ValidationError("项目结构不能为空")

        if not target_dir:
            raise ValidationError("目标目录不能为空")

        # 如果没有提供配置，使用实例的配置（包括可能修改的冲突解决策略）
        if config is None:
            effective_config = FileCreationConfig(
                conflict_resolution=self.conflict_resolution,
                create_directories=self.config.create_directories,
                preserve_permissions=self.config.preserve_permissions,
                validation_enabled=self.config.validation_enabled,
                validation_rules=self.config.validation_rules,
                max_file_size=self.config.max_file_size,
                allowed_extensions=self.config.allowed_extensions,
                forbidden_extensions=self.config.forbidden_extensions,
                allowed_directories=self.config.allowed_directories,
                backup_suffix=self.config.backup_suffix,
                default_file_mode=self.config.default_file_mode,
                default_dir_mode=self.config.default_dir_mode,
                dry_run=self.config.dry_run,
                atomic_writes=self.config.atomic_writes,
            )
        else:
            effective_config = config
        files_preview = []
        directories = set()
        total_size = 0
        conflicts = 0
        new_files = 0
        modified_files = 0

        # 验证每个文件并生成预览
        for file in structure.files:
            try:
                preview = await self._generate_file_preview(
                    file, target_dir, effective_config
                )
                files_preview.append(preview)

                # 统计信息
                total_size += file.size or 0
                directories.update(self._extract_directories(file.path))

                if preview.exists:
                    conflicts += 1
                    if preview.action in [
                        PreviewAction.OVERWRITE,
                        PreviewAction.BACKUP,
                        PreviewAction.MERGE,
                    ]:
                        modified_files += 1
                else:
                    new_files += 1

            except Exception as e:
                logger.error(f"生成文件预览失败 {file.path}: {e}")
                raise ValidationError(f"文件预览生成失败: {file.path}, 错误: {e}")

        return PreviewSummary(
            files=files_preview,
            directories=sorted(directories),
            total_files=len(files_preview),
            total_size=total_size,
            conflicts=conflicts,
            new_files=new_files,
            modified_files=modified_files,
        )

    async def _generate_file_preview(
        self, file: ProjectFile, target_dir: str, config: FileCreationConfig
    ) -> FilePreview:
        """生成单个文件预览"""
        if not file.path:
            raise ValidationError("文件路径不能为空")

        full_path = os.path.join(target_dir, file.path)
        exists = os.path.exists(full_path)
        conflicts = []
        metadata = {}

        # 确定动作
        if exists:
            action = self._determine_action_for_existing_file(full_path, file, config)
            conflicts.append("文件已存在")

            # 检查内容是否相同
            if self._files_have_same_content(full_path, file.content):
                conflicts.append("内容相同")
            else:
                conflicts.append("内容冲突")

        else:
            action = PreviewAction.CREATE

        # 检查路径冲突
        path_conflicts = self._check_path_conflicts(file, target_dir, config)
        conflicts.extend(path_conflicts)

        # 添加元数据
        metadata.update(
            {
                "size": file.size or len(file.content.encode("utf-8")),
                "type": Path(file.path).suffix.lower() or "unknown",
                "full_path": full_path,
                "relative_path": file.path,
            }
        )

        if exists:
            stat = os.stat(full_path)
            metadata.update(
                {
                    "existing_size": stat.st_size,
                    "modified_time": stat.st_mtime,
                    "created_time": stat.st_ctime,
                }
            )

        return FilePreview(
            file=file,
            action=action,
            exists=exists,
            conflicts=conflicts,
            metadata=metadata,
        )

    def _determine_action_for_existing_file(
        self, full_path: str, file: ProjectFile, config: FileCreationConfig
    ) -> PreviewAction:
        """确定对已存在文件的动作"""
        if config.conflict_resolution == FileConflictResolution.SKIP:
            return PreviewAction.SKIP
        elif config.conflict_resolution == FileConflictResolution.FAIL:
            return PreviewAction.SKIP  # 在预览中视为跳过
        elif config.conflict_resolution == FileConflictResolution.OVERWRITE:
            return PreviewAction.OVERWRITE
        elif config.conflict_resolution == FileConflictResolution.BACKUP:
            return PreviewAction.BACKUP
        elif config.conflict_resolution == FileConflictResolution.MERGE:
            return PreviewAction.MERGE
        else:
            return PreviewAction.OVERWRITE  # 默认覆盖

    def _files_have_same_content(self, existing_path: str, new_content: str) -> bool:
        """检查文件内容是否相同"""
        try:
            with open(existing_path, encoding="utf-8") as f:
                existing_content = f.read()
            return existing_content == new_content
        except Exception:
            return False

    def _check_path_conflicts(
        self, file: ProjectFile, target_dir: str, config: FileCreationConfig
    ) -> list[str]:
        """检查路径冲突"""
        conflicts = []

        # 检查扩展名限制
        if config.allowed_extensions:
            ext = Path(file.path).suffix.lower()
            if ext not in config.allowed_extensions:
                conflicts.append(f"不允许的扩展名: {ext}")

        if config.forbidden_extensions:
            ext = Path(file.path).suffix.lower()
            if ext in config.forbidden_extensions:
                conflicts.append(f"禁止的扩展名: {ext}")

        # 检查目录限制
        if config.allowed_directories:
            path_parts = [
                part for part in file.path.replace("\\", "/").split("/") if part
            ]
            if len(path_parts) >= 2:
                parent_dir = path_parts[-2]
                if parent_dir not in config.allowed_directories:
                    conflicts.append(f"不允许的目录: {parent_dir}")

        return conflicts

    def _extract_directories(self, file_path: str) -> list[str]:
        """提取文件路径中的目录"""
        path_parts = Path(file_path).parts
        directories = []

        for i in range(len(path_parts) - 1):  # 排除文件名
            if path_parts[i]:
                directories.append(os.path.join(*path_parts[: i + 1]))

        return directories

    async def interactive_confirmation(
        self,
        structure: ProjectStructure,
        target_dir: str,
        config: Optional[FileCreationConfig] = None,
    ) -> ConfirmationResponse:
        """交互式确认"""
        try:
            # 生成预览
            preview = await self.generate_preview(structure, target_dir, config)

            # 显示预览
            self._display_preview(preview)

            # 获取用户确认
            response = await self._get_user_confirmation(preview)

            return response

        except Exception as e:
            logger.error(f"交互式确认失败: {e}")
            return ConfirmationResponse(
                result=ConfirmationResult.CANCELLED, message=f"确认过程出错: {e}"
            )

    def _display_preview(self, preview: PreviewSummary) -> None:
        """显示预览信息"""

        if preview.directories:
            for directory in preview.directories:
                pass

        for i, file_preview in enumerate(preview.files, 1):
            self._get_status_icon(file_preview)
            self._get_action_text(file_preview.action)
            file_preview.metadata.get("size", 0)

            if file_preview.conflicts:
                for conflict in file_preview.conflicts:
                    pass

    def _get_status_icon(self, preview: FilePreview) -> str:
        """获取状态图标"""
        if preview.exists:
            if preview.action == PreviewAction.SKIP:
                return "⏭️ "
            elif preview.action == PreviewAction.BACKUP:
                return "💾 "
            elif preview.action == PreviewAction.OVERWRITE:
                return "🔄 "
            elif preview.action == PreviewAction.MERGE:
                return "🔀 "
            else:
                return "❓ "
        else:
            return "➕ "

    def _get_action_text(self, action: PreviewAction) -> str:
        """获取动作文本"""
        action_map = {
            PreviewAction.CREATE: "创建",
            PreviewAction.OVERWRITE: "覆盖",
            PreviewAction.BACKUP: "备份后创建",
            PreviewAction.SKIP: "跳过",
            PreviewAction.MERGE: "合并",
        }
        return action_map.get(action, "未知操作")

    async def _get_user_confirmation(
        self, preview: PreviewSummary
    ) -> ConfirmationResponse:
        """获取用户确认"""
        try:
            while True:
                choice = input("请选择: ").lower().strip()

                if choice == "y" or choice == "yes":
                    return ConfirmationResponse(
                        result=ConfirmationResult.CONFIRMED,
                        selected_files=[
                            f.file
                            for f in preview.files
                            if f.action != PreviewAction.SKIP
                        ],
                        message="用户确认创建所有文件",
                    )
                elif choice == "n" or choice == "no":
                    return ConfirmationResponse(
                        result=ConfirmationResult.CANCELLED, message="用户取消操作"
                    )
                elif choice == "s" or choice == "select":
                    return await self._selective_confirmation(preview)
                elif choice == "v" or choice == "view":
                    self._display_detailed_preview(preview)
                elif choice == "h" or choice == "help":
                    self._display_help()
                else:
                    pass

        except KeyboardInterrupt:
            return ConfirmationResponse(
                result=ConfirmationResult.CANCELLED, message="用户中断操作"
            )

    async def _selective_confirmation(
        self, preview: PreviewSummary
    ) -> ConfirmationResponse:
        """选择性确认"""

        # 显示文件列表
        for i, file_preview in enumerate(preview.files, 1):
            self._get_status_icon(file_preview)

        selected_indices = []
        try:
            while True:
                choice = input("选择文件 (例: 1 3 5): ").strip()
                if not choice:
                    break

                indices = []
                for part in choice.split():
                    try:
                        idx = int(part)
                        if 1 <= idx <= len(preview.files):
                            indices.append(idx - 1)  # 转换为0-based索引
                        else:
                            pass
                    except ValueError:
                        pass

                selected_indices.extend(indices)

        except KeyboardInterrupt:
            return ConfirmationResponse(
                result=ConfirmationResult.CANCELLED, message="用户中断选择"
            )

        # 构建响应
        selected_files = []
        rejected_files = []

        for i, file_preview in enumerate(preview.files):
            if i in selected_indices:
                selected_files.append(file_preview.file)
            elif file_preview.action != PreviewAction.SKIP:
                rejected_files.append(file_preview.file)

        if selected_files:
            return ConfirmationResponse(
                result=ConfirmationResult.MODIFIED,
                selected_files=selected_files,
                rejected_files=rejected_files,
                message=f"用户选择了 {len(selected_files)} 个文件",
            )
        else:
            return ConfirmationResponse(
                result=ConfirmationResult.CANCELLED, message="用户未选择任何文件"
            )

    def _display_detailed_preview(self, preview: PreviewSummary) -> None:
        """显示详细预览"""

        for i, file_preview in enumerate(preview.files, 1):
            if file_preview.conflicts:
                for conflict in file_preview.conflicts:
                    pass

            # 显示文件内容预览 (如果不太大的话)
            content = file_preview.file.content
            if content and len(content) <= 200:
                pass
            elif content:
                pass

    def _display_help(self) -> None:
        """显示帮助信息"""

    async def auto_confirmation(
        self,
        structure: ProjectStructure,
        target_dir: str,
        auto_confirm: bool = True,
        config: Optional[FileCreationConfig] = None,
    ) -> ConfirmationResponse:
        """自动确认"""
        try:
            preview = await self.generate_preview(structure, target_dir, config)

            if auto_confirm:
                return ConfirmationResponse(
                    result=ConfirmationResult.CONFIRMED,
                    selected_files=[
                        f.file for f in preview.files if f.action != PreviewAction.SKIP
                    ],
                    message="自动确认创建所有文件",
                )
            else:
                return ConfirmationResponse(
                    result=ConfirmationResult.CANCELLED, message="自动取消操作"
                )

        except Exception as e:
            logger.error(f"自动确认失败: {e}")
            return ConfirmationResponse(
                result=ConfirmationResult.CANCELLED, message=f"自动确认失败: {e}"
            )


# 添加格式化大小的方法到PreviewSummary
def _format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


# 动态添加方法到类
PreviewSummary._format_size = staticmethod(_format_size)
