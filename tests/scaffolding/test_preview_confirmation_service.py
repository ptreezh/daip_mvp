"""
测试预览确认服务
遵循TDD原则：先写测试，再实现功能
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

from daip_live.scaffolding.models import (
    ProjectFile,
    ProjectStructure,
    ValidationError,
    FileCreationError
)
from daip_live.scaffolding.preview_confirmation_service import (
    PreviewAction,
    ConfirmationResult,
    FilePreview,
    PreviewSummary,
    ConfirmationResponse
)


class TestPreviewAction:
    """测试预览动作"""

    def test_preview_action_values(self):
        """测试预览动作值"""
        # TC-2.5.1: 预览动作枚举值测试
        assert PreviewAction.CREATE.value == "create"
        assert PreviewAction.OVERWRITE.value == "overwrite"
        assert PreviewAction.BACKUP.value == "backup"
        assert PreviewAction.SKIP.value == "skip"
        assert PreviewAction.MERGE.value == "merge"

    def test_preview_action_from_string(self):
        """测试从字符串创建预览动作"""
        # TC-2.5.2: 字符串转换测试
        assert PreviewAction("create") == PreviewAction.CREATE
        assert PreviewAction("overwrite") == PreviewAction.OVERWRITE
        assert PreviewAction("backup") == PreviewAction.BACKUP
        assert PreviewAction("skip") == PreviewAction.SKIP
        assert PreviewAction("merge") == PreviewAction.MERGE


class TestConfirmationResult:
    """测试确认结果"""

    def test_confirmation_result_values(self):
        """测试确认结果值"""
        # TC-2.5.3: 确认结果枚举值测试
        assert ConfirmationResult.CONFIRMED.value == "confirmed"
        assert ConfirmationResult.CANCELLED.value == "cancelled"
        assert ConfirmationResult.MODIFIED.value == "modified"


class TestFilePreview:
    """测试文件预览"""

    def test_file_preview_creation(self):
        """测试文件预览创建"""
        # TC-2.5.4: 文件预览创建测试
        file = ProjectFile(path="test.py", content="print('hello')")
        preview = FilePreview(
            file=file,
            action=PreviewAction.CREATE
        )

        assert preview.file == file
        assert preview.action == PreviewAction.CREATE
        assert preview.exists == False
        assert preview.conflicts == []
        assert preview.metadata == {}

    def test_file_preview_with_conflicts(self):
        """测试带冲突的文件预览"""
        # TC-2.5.5: 冲突预览测试
        file = ProjectFile(path="existing.py", content="new content")
        preview = FilePreview(
            file=file,
            action=PreviewAction.OVERWRITE,
            exists=True,
            conflicts=["文件已存在", "内容冲突"]
        )

        assert preview.action == PreviewAction.OVERWRITE
        assert preview.exists == True
        assert len(preview.conflicts) == 2
        assert "文件已存在" in preview.conflicts
        assert "内容冲突" in preview.conflicts

    def test_file_preview_with_metadata(self):
        """测试带元数据的文件预览"""
        # TC-2.5.6: 元数据预览测试
        file = ProjectFile(path="data.json", content='{"key": "value"}')
        preview = FilePreview(
            file=file,
            action=PreviewAction.CREATE,
            metadata={"size": 21, "type": "json", "encoding": "utf-8"}
        )

        assert preview.metadata["size"] == 21
        assert preview.metadata["type"] == "json"
        assert preview.metadata["encoding"] == "utf-8"


class TestPreviewSummary:
    """测试预览摘要"""

    def test_preview_summary_creation(self):
        """测试预览摘要创建"""
        # TC-2.5.7: 预览摘要创建测试
        files = [
            FilePreview(
                file=ProjectFile(path="new.py", content="print('new')"),
                action=PreviewAction.CREATE
            ),
            FilePreview(
                file=ProjectFile(path="old.py", content="print('old')"),
                action=PreviewAction.OVERWRITE,
                exists=True
            )
        ]

        summary = PreviewSummary(
            files=files,
            directories=["src", "tests"],
            total_files=2,
            total_size=25,
            conflicts=1,
            new_files=1,
            modified_files=1
        )

        assert len(summary.files) == 2
        assert len(summary.directories) == 2
        assert summary.total_files == 2
        assert summary.total_size == 25
        assert summary.conflicts == 1
        assert summary.new_files == 1
        assert summary.modified_files == 1

    def test_preview_summary_calculated_fields(self):
        """测试预览摘要计算字段"""
        # TC-2.5.8: 摘要字段计算测试
        file1 = ProjectFile(path="test1.py", content="x" * 10)
        file2 = ProjectFile(path="test2.py", content="y" * 20)

        files = [
            FilePreview(file=file1, action=PreviewAction.CREATE),
            FilePreview(file=file2, action=PreviewAction.CREATE, exists=True)
        ]

        summary = PreviewSummary(
            files=files,
            directories=[],
            total_files=len(files),
            total_size=file1.size + file2.size,
            conflicts=1,
            new_files=1,
            modified_files=1
        )

        assert summary.total_files == 2
        assert summary.total_size == 30
        assert summary.conflicts == 1
        assert summary.new_files == 1
        assert summary.modified_files == 1


class TestConfirmationResponse:
    """测试确认响应"""

    def test_confirmation_response_creation(self):
        """测试确认响应创建"""
        # TC-2.5.9: 确认响应创建测试
        response = ConfirmationResponse(
            result=ConfirmationResult.CONFIRMED,
            message="用户确认操作"
        )

        assert response.result == ConfirmationResult.CONFIRMED
        assert response.message == "用户确认操作"
        assert response.selected_files == []
        assert response.rejected_files == []
        assert response.modifications == {}

    def test_confirmation_response_with_files(self):
        """测试带文件的确认响应"""
        # TC-2.5.10: 文件选择响应测试
        selected = [ProjectFile(path="keep.py", content="keep")]
        rejected = [ProjectFile(path="remove.py", content="remove")]
        modifications = {"output_dir": "/custom/path"}

        response = ConfirmationResponse(
            result=ConfirmationResult.MODIFIED,
            selected_files=selected,
            rejected_files=rejected,
            modifications=modifications,
            message="用户修改了操作"
        )

        assert response.result == ConfirmationResult.MODIFIED
        assert len(response.selected_files) == 1
        assert len(response.rejected_files) == 1
        assert response.modifications["output_dir"] == "/custom/path"
        assert response.message == "用户修改了操作"


# PreviewConfirmationService 测试将在实现后添加
# 预留测试类位置


class TestPreviewConfirmationService:
    """测试预览确认服务"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_generate_preview_success(self):
        """测试成功生成预览"""
        # TC-2.5.11: 成功预览生成测试
        from daip_live.scaffolding.preview_confirmation_service import PreviewConfirmationService

        service = PreviewConfirmationService()
        structure = ProjectStructure(
            description="Test project",
            files=[
                ProjectFile(path="src/main.py", content="def main(): pass"),
                ProjectFile(path="README.md", content="# Test")
            ]
        )

        preview = await service.generate_preview(structure, self.temp_dir)

        assert isinstance(preview, PreviewSummary)
        assert len(preview.files) == 2
        assert preview.total_files == 2
        assert len(preview.directories) > 0
        assert preview.total_size > 0

    @pytest.mark.asyncio
    async def test_generate_preview_with_existing_files(self):
        """测试生成带已存在文件的预览"""
        # TC-2.5.12: 已存在文件预览测试
        from daip_live.scaffolding.preview_confirmation_service import PreviewConfirmationService

        service = PreviewConfirmationService()

        # 先创建已存在的文件
        existing_file = os.path.join(self.temp_dir, "existing.py")
        with open(existing_file, 'w') as f:
            f.write("old content")

        structure = ProjectStructure(
            description="Test with existing files",
            files=[
                ProjectFile(path="existing.py", content="new content"),
                ProjectFile(path="new.py", content="print('new')")
            ]
        )

        preview = await service.generate_preview(structure, self.temp_dir)

        assert len(preview.files) == 2
        assert preview.conflicts >= 1
        assert preview.new_files >= 1
        assert preview.modified_files >= 1

        # 检查已存在文件的动作
        existing_preview = next(f for f in preview.files if f.file.path == "existing.py")
        assert existing_preview.exists == True
        assert existing_preview.action in [PreviewAction.OVERWRITE, PreviewAction.BACKUP]

    @pytest.mark.asyncio
    async def test_interactive_confirmation_success(self):
        """测试交互式确认成功"""
        # TC-2.5.13: 交互式确认成功测试
        from daip_live.scaffolding.preview_confirmation_service import PreviewConfirmationService

        service = PreviewConfirmationService()
        structure = ProjectStructure(
            description="Test project",
            files=[ProjectFile(path="test.py", content="print('test')")]
        )

        # Mock 用户输入为 'y'
        with patch('builtins.input', return_value='y'):
            response = await service.interactive_confirmation(structure, self.temp_dir)

        assert response.result == ConfirmationResult.CONFIRMED
        assert len(response.selected_files) == 1

    @pytest.mark.asyncio
    async def test_interactive_confirmation_cancel(self):
        """测试交互式确认取消"""
        # TC-2.5.14: 交互式确认取消测试
        from daip_live.scaffolding.preview_confirmation_service import PreviewConfirmationService

        service = PreviewConfirmationService()
        structure = ProjectStructure(
            description="Test project",
            files=[ProjectFile(path="test.py", content="print('test')")]
        )

        # Mock 用户输入为 'n'
        with patch('builtins.input', return_value='n'):
            response = await service.interactive_confirmation(structure, self.temp_dir)

        assert response.result == ConfirmationResult.CANCELLED
        assert len(response.selected_files) == 0

    @pytest.mark.asyncio
    async def test_non_interactive_confirmation(self):
        """测试非交互式确认"""
        # TC-2.5.15: 非交互式确认测试
        from daip_live.scaffolding.preview_confirmation_service import PreviewConfirmationService

        service = PreviewConfirmationService()
        structure = ProjectStructure(
            description="Test project",
            files=[ProjectFile(path="test.py", content="print('test')")]
        )

        response = await service.auto_confirmation(structure, self.temp_dir, auto_confirm=True)

        assert response.result == ConfirmationResult.CONFIRMED
        assert len(response.selected_files) == 1

        response = await service.auto_confirmation(structure, self.temp_dir, auto_confirm=False)

        assert response.result == ConfirmationResult.CANCELLED
        assert len(response.selected_files) == 0

    @pytest.mark.asyncio
    async def test_preview_with_validation_errors(self):
        """测试带验证错误的预览"""
        # TC-2.5.16: 验证错误预览测试
        from daip_live.scaffolding.preview_confirmation_service import PreviewConfirmationService

        service = PreviewConfirmationService()

        # 创建一个会触发验证错误的文件
        invalid_file = ProjectFile(path="", content="")  # 空路径应该触发错误

        structure = ProjectStructure(
            description="Invalid project",
            files=[invalid_file]
        )

        with pytest.raises(ValidationError):
            await service.generate_preview(structure, self.temp_dir)

    @pytest.mark.asyncio
    async def test_preview_large_structure(self):
        """测试大型结构预览"""
        # TC-2.5.17: 大型结构预览测试
        from daip_live.scaffolding.preview_confirmation_service import PreviewConfirmationService

        service = PreviewConfirmationService()

        # 创建大量文件
        files = []
        for i in range(50):  # 50个文件
            files.append(ProjectFile(
                path=f"file_{i}.py",
                content=f"# File {i}\nprint('File {i}')\n"
            ))

        structure = ProjectStructure(
            description="Large project",
            files=files
        )

        preview = await service.generate_preview(structure, self.temp_dir)

        assert len(preview.files) == 50
        assert preview.total_files == 50
        assert preview.total_size > 0
        assert preview.conflicts == 0  # 在空目录中应该没有冲突

    @pytest.mark.asyncio
    async def test_preview_with_different_conflict_strategies(self):
        """测试不同冲突策略的预览"""
        # TC-2.5.18: 冲突策略预览测试
        from daip_live.scaffolding.preview_confirmation_service import PreviewConfirmationService
        from daip_live.scaffolding.file_creation_service import FileConflictResolution

        # 测试备份策略
        backup_service = PreviewConfirmationService()
        backup_service.conflict_resolution = FileConflictResolution.BACKUP

        # 测试覆盖策略
        overwrite_service = PreviewConfirmationService()
        overwrite_service.conflict_resolution = FileConflictResolution.OVERWRITE

        # 创建已存在的文件
        existing_file = os.path.join(self.temp_dir, "test.py")
        with open(existing_file, 'w') as f:
            f.write("existing content")

        structure = ProjectStructure(
            description="Conflict test",
            files=[ProjectFile(path="test.py", content="new content")]
        )

        backup_preview = await backup_service.generate_preview(structure, self.temp_dir)
        overwrite_preview = await overwrite_service.generate_preview(structure, self.temp_dir)

        # 两个预览都应该显示冲突
        assert backup_preview.conflicts == 1
        assert overwrite_preview.conflicts == 1

        # 检查动作类型
        backup_file_preview = backup_preview.files[0]
        overwrite_file_preview = overwrite_preview.files[0]

        assert backup_file_preview.action == PreviewAction.BACKUP
        assert overwrite_file_preview.action == PreviewAction.OVERWRITE

    @pytest.mark.asyncio
    async def test_confirmation_with_file_selection(self):
        """测试文件选择的确认"""
        # TC-2.5.19: 文件选择确认测试
        from daip_live.scaffolding.preview_confirmation_service import PreviewConfirmationService

        service = PreviewConfirmationService()
        structure = ProjectStructure(
            description="Selection test",
            files=[
                ProjectFile(path="keep1.py", content="keep1"),
                ProjectFile(path="keep2.py", content="keep2"),
                ProjectFile(path="skip.py", content="skip")
            ]
        )

        # Mock用户选择只保留前两个文件
        with patch('builtins.input') as mock_input:
            mock_input.side_effect = ['s', '1', '2', '']  # 选择，选择文件1,2，空结束

            response = await service.interactive_confirmation(structure, self.temp_dir)

        assert response.result == ConfirmationResult.MODIFIED
        assert len(response.selected_files) == 2
        assert len(response.rejected_files) == 1

        selected_paths = [f.path for f in response.selected_files]
        assert "keep1.py" in selected_paths
        assert "keep2.py" in selected_paths
        assert "skip.py" not in selected_paths