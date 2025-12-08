"""
测试文件创建服务
遵循TDD原则：先写测试，再实现功能
"""

import pytest
import asyncio
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from daip_live.scaffolding.file_creation_service import (
    FileCreationService,
    FileCreationConfig,
    FileCreationResult,
    FileOperationStatus,
    FileConflictResolution,
    ValidationRule,
    DirectoryStructure
)
from daip_live.scaffolding.models import (
    ProjectFile,
    ProjectStructure,
    FileCreationError,
    ValidationError
)


class TestFileOperationStatus:
    """测试文件操作状态枚举"""

    def test_file_operation_status_values(self):
        """测试文件操作状态枚举值"""
        # TC-2.4.1: 文件操作状态枚举测试
        assert FileOperationStatus.SUCCESS.value == "success"
        assert FileOperationStatus.SKIPPED.value == "skipped"
        assert FileOperationStatus.FAILED.value == "failed"
        assert FileOperationStatus.CONFLICT.value == "conflict"
        assert FileOperationStatus.VALIDATION_FAILED.value == "validation_failed"

    def test_file_operation_status_from_string(self):
        """测试从字符串获取状态"""
        # TC-2.4.2: 状态字符串解析测试
        assert FileOperationStatus.from_string("success") == FileOperationStatus.SUCCESS
        assert FileOperationStatus.from_string("skipped") == FileOperationStatus.SKIPPED
        assert FileOperationStatus.from_string("failed") == FileOperationStatus.FAILED
        assert FileOperationStatus.from_string("unknown") == FileOperationStatus.SUCCESS  # 默认值


class TestFileConflictResolution:
    """测试文件冲突解决策略"""

    def test_conflict_resolution_values(self):
        """测试冲突解决策略枚举值"""
        # TC-2.4.3: 冲突解决策略枚举测试
        assert FileConflictResolution.FAIL.value == "fail"
        assert FileConflictResolution.SKIP.value == "skip"
        assert FileConflictResolution.OVERWRITE.value == "overwrite"
        assert FileConflictResolution.BACKUP.value == "backup"
        assert FileConflictResolution.MERGE.value == "merge"

    def test_conflict_resolution_from_string(self):
        """测试从字符串获取策略"""
        # TC-2.4.4: 策略字符串解析测试
        assert FileConflictResolution.from_string("fail") == FileConflictResolution.FAIL
        assert FileConflictResolution.from_string("skip") == FileConflictResolution.SKIP
        assert FileConflictResolution.from_string("overwrite") == FileConflictResolution.OVERWRITE
        assert FileConflictResolution.from_string("unknown") == FileConflictResolution.FAIL  # 默认值


class TestValidationRule:
    """测试验证规则"""

    def test_validation_rule_creation(self):
        """测试验证规则创建"""
        # TC-2.4.5: 验证规则创建测试
        rule = ValidationRule(
            name="max_file_size",
            description="检查文件大小限制",
            validator=lambda file: len(file.content) <= 1000
        )

        assert rule.name == "max_file_size"
        assert rule.description == "检查文件大小限制"
        assert callable(rule.validator)

    def test_validation_rule_with_condition(self):
        """测试带条件的验证规则"""
        # TC-2.4.6: 条件验证规则测试
        rule = ValidationRule(
            name="python_files_only",
            description="只验证Python文件",
            validator=lambda file: len(file.content) <= 5000,
            condition=lambda file: file.path.endswith('.py')
        )

        # 测试条件匹配
        py_file = ProjectFile(path="test.py", content="")
        assert rule.should_validate(py_file) == True

        # 测试条件不匹配
        txt_file = ProjectFile(path="test.txt", content="")
        assert rule.should_validate(txt_file) == False

    def test_validation_rule_validation(self):
        """测试验证规则验证"""
        # TC-2.4.7: 规则验证测试
        # 有效规则
        valid_rule = ValidationRule(
            name="test_rule",
            validator=lambda file: True
        )
        errors = valid_rule.validate()
        assert len(errors) == 0

        # 无效规则 - 无名称
        invalid_rule = ValidationRule(
            name="",
            validator=lambda file: True
        )
        errors = invalid_rule.validate()
        assert len(errors) > 0
        assert any("规则名称不能为空" in error for error in errors)


class TestFileCreationConfig:
    """测试文件创建配置"""

    def test_file_creation_config_creation(self):
        """测试文件创建配置创建"""
        # TC-2.4.8: 配置创建测试
        config = FileCreationConfig(
            conflict_resolution=FileConflictResolution.SKIP,
            create_directories=True,
            preserve_permissions=True,
            validation_enabled=True
        )

        assert config.conflict_resolution == FileConflictResolution.SKIP
        assert config.create_directories == True
        assert config.preserve_permissions == True
        assert config.validation_enabled == True

    def test_file_creation_config_with_rules(self):
        """测试带验证规则的配置"""
        # TC-2.4.9: 验证规则配置测试
        rule = ValidationRule(
            name="max_size",
            validator=lambda file: len(file.content) <= 100
        )

        config = FileCreationConfig(
            validation_rules=[rule],
            validation_enabled=True
        )

        assert len(config.validation_rules) == 1
        assert config.validation_rules[0] == rule

    def test_file_creation_config_defaults(self):
        """测试默认配置值"""
        # TC-2.4.10: 默认配置测试
        config = FileCreationConfig()

        assert config.conflict_resolution == FileConflictResolution.OVERWRITE
        assert config.create_directories == True
        assert config.preserve_permissions == False
        assert config.validation_enabled == True
        assert config.max_file_size == 1024 * 1024  # 1MB


class TestDirectoryStructure:
    """测试目录结构"""

    def test_directory_structure_creation(self):
        """测试目录结构创建"""
        # TC-2.4.11: 目录结构创建测试
        structure = DirectoryStructure(
            base_path="/test/project",
            mode=0o755
        )

        assert structure.base_path == "/test/project"
        assert structure.mode == 0o755

    def test_directory_structure_add_file(self):
        """测试添加文件到目录结构"""
        # TC-2.4.12: 添加文件测试
        structure = DirectoryStructure(base_path="/test")

        file1 = ProjectFile(path="src/main.py", content="print('hello')")
        file2 = ProjectFile(path="README.md", content="# Project")

        structure.add_file(file1)
        structure.add_file(file2)

        assert len(structure.files) == 2
        assert structure.files[0] == file1
        assert structure.files[1] == file2

    def test_directory_structure_get_by_path(self):
        """测试根据路径获取文件"""
        # TC-2.4.13: 路径查询测试
        structure = DirectoryStructure(base_path="/test")

        file1 = ProjectFile(path="src/main.py", content="print('hello')")
        structure.add_file(file1)

        # 存在的文件
        found = structure.get_file_by_path("src/main.py")
        assert found is file1

        # 不存在的文件
        not_found = structure.get_file_by_path("src/app.py")
        assert not_found is None

    def test_directory_structure_group_by_directory(self):
        """测试按目录分组文件"""
        # TC-2.4.14: 目录分组测试
        structure = DirectoryStructure(base_path="/test")

        structure.add_file(ProjectFile(path="src/main.py", content=""))
        structure.add_file(ProjectFile(path="src/utils.py", content=""))
        structure.add_file(ProjectFile(path="tests/test_main.py", content=""))
        structure.add_file(ProjectFile(path="README.md", content=""))

        groups = structure.group_by_directory()

        assert "src" in groups
        assert "tests" in groups
        assert "" in groups  # 根目录
        assert len(groups["src"]) == 2
        assert len(groups["tests"]) == 1


class TestFileCreationResult:
    """测试文件创建结果"""

    def test_file_creation_result_success(self):
        """测试成功创建结果"""
        # TC-2.4.15: 成功结果测试
        file = ProjectFile(path="test.py", content="print('hello')")
        result = FileCreationResult(
            file=file,
            status=FileOperationStatus.SUCCESS,
            bytes_written=13,
            duration=0.1
        )

        assert result.file == file
        assert result.status == FileOperationStatus.SUCCESS
        assert result.bytes_written == 13
        assert result.duration == 0.1
        assert result.success == True
        assert result.error is None

    def test_file_creation_result_failure(self):
        """测试失败创建结果"""
        # TC-2.4.16: 失败结果测试
        file = ProjectFile(path="test.py", content="")
        result = FileCreationResult(
            file=file,
            status=FileOperationStatus.FAILED,
            error="Permission denied"
        )

        assert result.status == FileOperationStatus.FAILED
        assert result.error == "Permission denied"
        assert result.success == False

    def test_file_creation_result_conflict(self):
        """测试冲突结果"""
        # TC-2.4.17: 冲突结果测试
        file = ProjectFile(path="existing.py", content="")
        result = FileCreationResult(
            file=file,
            status=FileOperationStatus.CONFLICT,
            error="File already exists",
            existing_path="backup_existing.py"
        )

        assert result.status == FileOperationStatus.CONFLICT
        assert result.error == "File already exists"
        assert result.existing_path == "backup_existing.py"
        assert result.success == False


class TestFileCreationService:
    """测试文件创建服务"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = FileCreationConfig(
            conflict_resolution=FileConflictResolution.SKIP,
            create_directories=True,
            validation_enabled=True,
            max_file_size=1024
        )
        self.service = FileCreationService(config=self.config)

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_service_creation(self):
        """测试服务创建"""
        # TC-2.4.18: 服务创建测试
        service = FileCreationService()
        assert service.config is not None
        assert service.config.conflict_resolution == FileConflictResolution.OVERWRITE

    def test_service_with_custom_config(self):
        """测试使用自定义配置创建服务"""
        # TC-2.4.19: 自定义配置服务测试
        custom_config = FileCreationConfig(
            conflict_resolution=FileConflictResolution.OVERWRITE,
            create_directories=False
        )
        service = FileCreationService(config=custom_config)

        assert service.config.conflict_resolution == FileConflictResolution.OVERWRITE
        assert service.config.create_directories == False

    @pytest.mark.asyncio
    async def test_create_single_file_success(self):
        """测试成功创建单个文件"""
        # TC-2.4.20: 单文件创建成功测试
        file = ProjectFile(
            path=os.path.join(self.temp_dir, "test.py"),
            content="print('Hello, World!')"
        )

        result = await self.service.create_file(file, self.temp_dir)

        assert result.success == True
        assert result.status == FileOperationStatus.SUCCESS
        assert os.path.exists(file.path)

        # 验证文件内容
        with open(file.path, 'r') as f:
            content = f.read()
            assert "Hello, World!" in content

    @pytest.mark.asyncio
    async def test_create_file_with_directory_creation(self):
        """测试创建文件并创建目录"""
        # TC-2.4.21: 目录创建测试
        file = ProjectFile(
            path=os.path.join(self.temp_dir, "src", "main.py"),
            content="def main(): pass"
        )

        result = await self.service.create_file(file, self.temp_dir)

        assert result.success == True
        assert os.path.exists(file.path)
        assert os.path.exists(os.path.dirname(file.path))

    @pytest.mark.asyncio
    async def test_create_file_skip_existing(self):
        """测试跳过已存在文件"""
        # TC-2.4.22: 跳过现有文件测试
        # 先创建文件
        file_path = os.path.join(self.temp_dir, "existing.txt")
        with open(file_path, 'w') as f:
            f.write("original content")

        file = ProjectFile(path=file_path, content="new content")

        result = await self.service.create_file(file, self.temp_dir)

        assert result.status == FileOperationStatus.SKIPPED
        assert result.success == True  # 跳过被视为成功

        # 验证原文件内容未被修改
        with open(file_path, 'r') as f:
            assert f.read() == "original content"

    @pytest.mark.asyncio
    async def test_create_file_overwrite(self):
        """测试覆盖已存在文件"""
        # TC-2.4.23: 覆盖现有文件测试
        # 创建支持覆盖的服务
        overwrite_service = FileCreationService(
            config=FileCreationConfig(
                conflict_resolution=FileConflictResolution.OVERWRITE
            )
        )

        file_path = os.path.join(self.temp_dir, "overwrite.txt")
        with open(file_path, 'w') as f:
            f.write("original")

        file = ProjectFile(path=file_path, content="overwritten")
        result = await overwrite_service.create_file(file, self.temp_dir)

        assert result.success == True
        assert result.status == FileOperationStatus.SUCCESS

        # 验证内容被覆盖
        with open(file_path, 'r') as f:
            assert f.read() == "overwritten"

    @pytest.mark.asyncio
    async def test_create_file_backup_existing(self):
        """测试备份已存在文件"""
        # TC-2.4.24: 备份现有文件测试
        backup_service = FileCreationService(
            config=FileCreationConfig(
                conflict_resolution=FileConflictResolution.BACKUP
            )
        )

        file_path = os.path.join(self.temp_dir, "backup.txt")
        with open(file_path, 'w') as f:
            f.write("original")

        file = ProjectFile(path=file_path, content="backup version")
        result = await backup_service.create_file(file, self.temp_dir)

        assert result.success == True
        assert result.status == FileOperationStatus.SUCCESS
        assert result.existing_path is not None
        assert os.path.exists(result.existing_path)

        # 验证备份文件内容
        with open(result.existing_path, 'r') as f:
            assert f.read() == "original"

        # 验证新文件内容
        with open(file_path, 'r') as f:
            assert f.read() == "backup version"

    @pytest.mark.asyncio
    async def test_create_file_validation_failure(self):
        """测试文件验证失败"""
        # TC-2.4.25: 验证失败测试
        # 创建带大小验证规则的服务
        rule = ValidationRule(
            name="max_content",
            validator=lambda file: len(file.content) <= 10,
            description="内容长度限制"
        )

        validation_service = FileCreationService(
            config=FileCreationConfig(
                validation_rules=[rule],
                validation_enabled=True
            )
        )

        # 创建超过限制的文件
        file = ProjectFile(
            path=os.path.join(self.temp_dir, "large.txt"),
            content="x" * 100  # 超过10字符限制
        )

        result = await validation_service.create_file(file, self.temp_dir)

        assert result.success == False
        assert result.status == FileOperationStatus.VALIDATION_FAILED
        assert "内容长度限制" in result.error

    @pytest.mark.asyncio
    async def test_create_project_structure_success(self):
        """测试成功创建项目结构"""
        # TC-2.4.26: 项目结构创建成功测试
        structure = ProjectStructure(
            description="Test project",
            files=[
                ProjectFile(path="src/main.py", content="def main(): pass"),
                ProjectFile(path="src/utils.py", content="def helper(): pass"),
                ProjectFile(path="README.md", content="# Test Project")
            ]
        )

        results = await self.service.create_project_structure(structure, self.temp_dir)

        assert len(results) == 3
        assert all(result.success for result in results)
        assert all(os.path.exists(result.file.path) for result in results)

    @pytest.mark.asyncio
    async def test_create_project_structure_with_validation(self):
        """测试带验证的项目结构创建"""
        # TC-2.4.27: 项目结构验证测试
        # 添加Python文件验证规则
        py_rule = ValidationRule(
            name="python_syntax",
            validator=lambda file: not file.path.endswith('.py') or 'pass' in file.content,
            condition=lambda file: file.path.endswith('.py')
        )

        validation_service = FileCreationService(
            config=FileCreationConfig(
                validation_rules=[py_rule],
                validation_enabled=True
            )
        )

        structure = ProjectStructure(
            description="Test project",
            files=[
                ProjectFile(path="src/main.py", content="def main(): pass"),  # 通过
                ProjectFile(path="src/invalid.py", content="invalid content")  # 失败
            ]
        )

        results = await validation_service.create_project_structure(structure, self.temp_dir)

        assert len(results) == 2
        assert results[0].success == True  # main.py通过验证
        assert results[1].success == False  # invalid.py验证失败
        assert "python_syntax" in results[1].error

    @pytest.mark.asyncio
    async def test_create_project_structure_partial_failure(self):
        """测试部分失败的项目结构创建"""
        # TC-2.4.28: 部分失败测试
        # 创建只允许特定目录的服务
        allowed_dirs_service = FileCreationService(
            config=FileCreationConfig(
                allowed_directories=["src", "tests"]
            )
        )

        structure = ProjectStructure(
            description="Test project",
            files=[
                ProjectFile(path="src/main.py", content="pass"),      # 允许
                ProjectFile(path="tests/test.py", content="pass"),   # 允许
                ProjectFile(path="temp/cache.py", content="pass")     # 不允许
            ]
        )

        results = await allowed_dirs_service.create_project_structure(structure, self.temp_dir)

        assert len(results) == 3
        assert results[0].success == True   # src/main.py
        assert results[1].success == True   # tests/test.py
        assert results[2].success == False  # temp/cache.py

    @pytest.mark.asyncio
    async def test_get_creation_summary(self):
        """测试获取创建摘要"""
        # TC-2.4.29: 创建摘要测试
        structure = ProjectStructure(
            description="Test project",
            files=[
                ProjectFile(path="src/main.py", content="def main(): pass"),
                ProjectFile(path="README.md", content="# Test")
            ]
        )

        # 先创建文件
        results = await self.service.create_project_structure(structure, self.temp_dir)

        # 获取摘要
        summary = self.service.get_creation_summary(results)

        assert summary['total_files'] == 2
        assert summary['successful_files'] == 2
        assert summary['failed_files'] == 0
        assert summary['total_bytes'] > 0
        assert summary['success_rate'] == 1.0

    @pytest.mark.asyncio
    async def test_backup_file_generation(self):
        """测试备份文件生成"""
        # TC-2.4.30: 备份文件生成测试
        backup_service = FileCreationService(
            config=FileCreationConfig(
                conflict_resolution=FileConflictResolution.BACKUP,
                backup_suffix=".backup"
            )
        )

        # 创建原文件
        file_path = os.path.join(self.temp_dir, "important.txt")
        with open(file_path, 'w') as f:
            f.write("important data")

        file = ProjectFile(path=file_path, content="new data")
        result = await backup_service.create_file(file, self.temp_dir)

        assert result.success == True
        assert result.existing_path.endswith(".backup")

        # 验证备份文件存在且包含原内容
        with open(result.existing_path, 'r') as f:
            assert f.read() == "important data"

    @pytest.mark.asyncio
    async def test_dry_run_mode(self):
        """测试干运行模式"""
        # TC-2.4.31: 干运行模式测试
        dry_run_service = FileCreationService(
            config=FileCreationConfig(
                dry_run=True
            )
        )

        file = ProjectFile(
            path=os.path.join(self.temp_dir, "dry_run.txt"),
            content="test content"
        )

        result = await dry_run_service.create_file(file, self.temp_dir)

        # 干运行应该成功但不实际创建文件
        assert result.status == FileOperationStatus.SUCCESS
        assert result.success == True
        assert not os.path.exists(file.path)  # 文件不应该存在

    @pytest.mark.asyncio
    async def test_file_permission_handling(self):
        """测试文件权限处理"""
        # TC-2.4.32: 文件权限测试
        permission_service = FileCreationService(
            config=FileCreationConfig(
                preserve_permissions=True,
                default_file_mode=0o644
            )
        )

        file = ProjectFile(
            path=os.path.join(self.temp_dir, "chmod_test.py"),
            content="print('test')"
        )

        result = await permission_service.create_file(file, self.temp_dir)

        assert result.success == True
        # 验证文件权限 - 在Windows上权限处理不同
        assert os.path.exists(file.path)
        file_stat = os.stat(file.path)
        # 在Unix系统上检查权限位，Windows上跳过这个检查
        import platform
        if platform.system() != 'Windows':
            assert file_stat.st_mode & 0o777 == 0o644  # 检查权限位

    @pytest.mark.asyncio
    async def test_error_handling_missing_directory(self):
        """测试缺少目录的错误处理"""
        # TC-2.4.33: 目录缺失错误处理测试
        no_dir_service = FileCreationService(
            config=FileCreationConfig(
                create_directories=False  # 不创建目录
            )
        )

        file = ProjectFile(
            path=os.path.join(self.temp_dir, "nonexistent", "file.py"),
            content="test"
        )

        result = await no_dir_service.create_file(file, self.temp_dir)

        assert result.success == False
        assert result.status == FileOperationStatus.FAILED
        assert result.error is not None


if __name__ == "__main__":
    # Run tests when this file is executed directly
    pytest.main([__file__, "-v"])