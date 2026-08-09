"""
测试脚手架数据模型
遵循TDD原则：先写测试，再实现功能
"""

import pytest
from datetime import datetime
from pathlib import Path

# Import models to be tested
from daip_live.scaffolding.models import (
    ProjectFile,
    ProjectStructure,
    ScaffoldResult,
    RetryConfig,
    InputType,
    ScaffoldCommand,
    ValidationError,
    GenerationError,
    FileCreationError
)


class TestProjectFile:
    """测试ProjectFile数据模型"""

    def test_project_file_creation_with_manual_size(self):
        """测试手动指定大小的ProjectFile创建"""
        # TC-1.1.1: 基本创建测试
        file = ProjectFile(
            path="roles/project_manager.yaml",
            content="name: Project Manager\npersona: Managing project tasks",
            size=50
        )

        assert file.path == "roles/project_manager.yaml"
        assert file.content == "name: Project Manager\npersona: Managing project tasks"
        assert file.size == 50
        assert isinstance(file.created_at, datetime)

    def test_project_file_auto_size_calculation(self):
        """测试自动计算文件大小"""
        # TC-1.1.2: 自动大小计算测试
        content = "Hello, World! 你好，世界！"
        file = ProjectFile(
            path="test.txt",
            content=content
        )

        # 计算UTF-8编码的字节长度
        expected_size = len(content.encode('utf-8'))
        assert file.size == expected_size

    def test_project_file_empty_content(self):
        """测试空内容的ProjectFile"""
        # TC-1.1.3: 边界条件测试
        file = ProjectFile(
            path="empty.txt",
            content=""
        )

        assert file.content == ""
        assert file.size == 0

    def test_project_file_unicode_content(self):
        """测试包含Unicode字符的内容"""
        # TC-1.1.4: Unicode支持测试
        content = "🏗️ 项目脚手架 AI助手 αβγ"
        file = ProjectFile(
            path="unicode.txt",
            content=content
        )

        assert file.content == content
        assert file.size > 0

    def test_project_file_path_validation(self):
        """测试路径验证"""
        # TC-1.1.5: 路径格式验证
        valid_paths = [
            "roles/dev.yaml",
            "workflows/main.yaml",
            "config.yaml",
            "nested/dir/file.yaml"
        ]

        for path in valid_paths:
            file = ProjectFile(path=path, content="test")
            assert file.path == path

    def test_project_file_consistency(self):
        """测试数据一致性"""
        # TC-1.1.6: 数据一致性测试
        file = ProjectFile(
            path="test.yaml",
            content="test content"
        )

        # 修改内容后大小应该相应变化
        original_size = file.size
        file.content = "modified content"
        assert file.size != original_size
        assert file.size == len("modified content".encode('utf-8'))


class TestProjectStructure:
    """测试ProjectStructure数据模型"""

    def test_project_structure_creation(self):
        """测试ProjectStructure创建"""
        # TC-1.1.7: 基本创建测试
        files = [
            ProjectFile("roles/pm.yaml", "role: pm"),
            ProjectFile("workflows/main.yaml", "workflow: main")
        ]
        structure = ProjectStructure(
            files=files,
            description="Test project"
        )

        assert len(structure.files) == 2
        assert structure.description == "Test project"
        assert structure.file_count == 2
        assert structure.total_size > 0
        assert isinstance(structure.generated_at, datetime)

    def test_project_structure_empty_files(self):
        """测试空文件列表的ProjectStructure"""
        # TC-1.1.8: 空列表边界测试
        structure = ProjectStructure(
            files=[],
            description="Empty project"
        )

        assert structure.file_count == 0
        assert structure.total_size == 0

    def test_project_structure_calculations(self):
        """测试统计计算的正确性"""
        # TC-1.1.9: 统计计算测试
        files = [
            ProjectFile("a.txt", "hello"),      # 5 bytes
            ProjectFile("b.txt", "world"),      # 5 bytes
            ProjectFile("c.txt", "test")        # 4 bytes
        ]
        structure = ProjectStructure(
            files=files,
            description="Calculation test"
        )

        assert structure.file_count == 3
        assert structure.total_size == 14  # 5 + 5 + 4

    def test_project_structure_file_types(self):
        """测试不同文件类型的处理"""
        # TC-1.1.10: 文件类型多样性测试
        files = [
            ProjectFile("config.yaml", "key: value"),
            ProjectFile("README.md", "# Project Title"),
            ProjectFile("main.py", "print('hello')")
        ]
        structure = ProjectStructure(files, description="Multi-type project")

        assert len(structure.files) == 3
        assert any(f.path.endswith('.yaml') for f in structure.files)
        assert any(f.path.endswith('.md') for f in structure.files)
        assert any(f.path.endswith('.py') for f in structure.files)


class TestScaffoldResult:
    """测试ScaffoldResult数据模型"""

    def test_scaffold_result_success(self):
        """测试成功的ScaffoldResult"""
        # TC-1.1.11: 成功结果测试
        structure = ProjectStructure([], "test")
        result = ScaffoldResult.success(structure)

        assert result.is_success == True
        assert result.project_structure == structure
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_scaffold_result_failure(self):
        """测试失败的ScaffoldResult"""
        # TC-1.1.12: 失败结果测试
        errors = ["File not found", "Invalid format"]
        result = ScaffoldResult.failure(errors)

        assert result.is_success == False
        assert result.project_structure is None
        assert result.errors == errors
        assert len(result.warnings) == 0

    def test_scaffold_result_with_warnings(self):
        """测试包含警告的ScaffoldResult"""
        # TC-1.1.13: 警告信息测试
        structure = ProjectStructure([], "test")
        warnings = ["File already exists"]
        result = ScaffoldResult(
            is_success=True,
            project_structure=structure,
            warnings=warnings
        )

        assert result.is_success == True
        assert result.warnings == warnings

    def test_scaffold_result_mixed(self):
        """测试同时有错误和警告的情况"""
        # TC-1.1.14: 混合状态测试
        errors = ["Critical error"]
        warnings = ["Minor warning"]
        result = ScaffoldResult(
            is_success=False,
            errors=errors,
            warnings=warnings
        )

        assert result.is_success == False
        assert result.errors == errors
        assert result.warnings == warnings


class TestRetryConfig:
    """测试RetryConfig配置模型"""

    def test_retry_config_default_values(self):
        """测试RetryConfig默认值"""
        # TC-1.1.15: 默认配置测试
        config = RetryConfig()

        assert config.max_retries == 3
        assert config.delay_seconds == 1.0
        assert config.backoff_factor == 2.0

    def test_retry_config_custom_values(self):
        """测试自定义RetryConfig值"""
        # TC-1.1.16: 自定义配置测试
        config = RetryConfig(
            max_retries=5,
            delay_seconds=2.0,
            backoff_factor=1.5
        )

        assert config.max_retries == 5
        assert config.delay_seconds == 2.0
        assert config.backoff_factor == 1.5

    def test_retry_config_validation(self):
        """测试RetryConfig参数验证"""
        # TC-1.1.17: 参数验证测试
        # 测试负数重试次数
        with pytest.raises(ValueError):
            RetryConfig(max_retries=-1)

        # 测试负数延迟时间
        with pytest.raises(ValueError):
            RetryConfig(delay_seconds=-1.0)

        # 测试小于1的退避因子
        with pytest.raises(ValueError):
            RetryConfig(backoff_factor=0.5)


class TestInputType:
    """测试InputType枚举"""

    def test_input_type_values(self):
        """测试InputType枚举值"""
        # TC-1.1.18: 枚举值测试
        assert InputType.TEXT.value == "text"
        assert InputType.FILE.value == "file"

    def test_input_type_comparison(self):
        """测试InputType比较操作"""
        # TC-1.1.19: 枚举比较测试
        assert InputType.TEXT == InputType.TEXT
        assert InputType.TEXT != InputType.FILE

    def test_input_type_iteration(self):
        """测试InputType枚举迭代"""
        # TC-1.1.20: 枚举迭代测试
        types = list(InputType)
        assert len(types) == 2
        assert InputType.TEXT in types
        assert InputType.FILE in types


class TestScaffoldCommand:
    """测试ScaffoldCommand数据模型"""

    def test_scaffold_command_text_input(self):
        """测试文本输入的ScaffoldCommand"""
        # TC-1.1.21: 文本命令测试
        command = ScaffoldCommand(
            input_type=InputType.TEXT,
            description="A web application project"
        )

        assert command.input_type == InputType.TEXT
        assert command.description == "A web application project"
        assert command.file_path is None
        assert command.auto_confirm == False

    def test_scaffold_command_file_input(self):
        """测试文件输入的ScaffoldCommand"""
        # TC-1.1.22: 文件命令测试
        command = ScaffoldCommand(
            input_type=InputType.FILE,
            description="",
            file_path="project_desc.txt",
            auto_confirm=False
        )

        assert command.input_type == InputType.FILE
        assert command.file_path == "project_desc.txt"

    def test_scaffold_command_auto_confirm(self):
        """测试自动确认选项"""
        # TC-1.1.23: 自动确认测试
        command = ScaffoldCommand(
            input_type=InputType.TEXT,
            description="Test",
            auto_confirm=True
        )

        assert command.auto_confirm == True

    def test_scaffold_command_empty_description_for_file(self):
        """测试文件输入时描述可以为空"""
        # TC-1.1.24: 文件描述测试
        command = ScaffoldCommand(
            input_type=InputType.FILE,
            description="",  # 文件输入时描述可以为空
            file_path="desc.txt"
        )

        assert command.input_type == InputType.FILE
        assert command.description == ""


class TestCustomExceptions:
    """测试自定义异常类"""

    def test_validation_error(self):
        """测试ValidationError异常"""
        # TC-1.1.25: 验证错误测试
        errors = ["Invalid input", "Missing required field"]
        error = ValidationError(errors)

        assert str(error) == "Validation failed: Invalid input; Missing required field"
        assert error.validation_errors == errors

    def test_generation_error(self):
        """测试GenerationError异常"""
        # TC-1.1.26: 生成错误测试
        error = GenerationError("YAML format is invalid")

        assert str(error) == "YAML format is invalid"
        assert isinstance(error, Exception)

    def test_file_creation_error(self):
        """测试FileCreationError异常"""
        # TC-1.1.27: 文件创建错误测试
        error = FileCreationError("Permission denied")

        assert str(error) == "File creation failed: Permission denied"
        assert isinstance(error, Exception)

    def test_exception_inheritance(self):
        """测试异常继承关系"""
        # TC-1.1.28: 异常继承测试
        assert issubclass(ValidationError, Exception)
        assert issubclass(GenerationError, Exception)
        assert issubclass(FileCreationError, Exception)


if __name__ == "__main__":
    # Run tests when this file is executed directly
    pytest.main([__file__, "-v"])