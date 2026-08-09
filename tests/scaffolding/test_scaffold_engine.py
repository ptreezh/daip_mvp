"""
测试脚手架核心引擎
遵循TDD原则：先写测试，再实现功能
"""

import asyncio
from unittest.mock import patch

import pytest

from daip_live.scaffolding.config_manager import ScaffoldConfig
from daip_live.scaffolding.error_handler import ErrorHandler
from daip_live.scaffolding.models import (
    InputType,
    ProjectFile,
    ProjectStructure,
    ScaffoldCommand,
    ValidationError,
)
from daip_live.scaffolding.scaffold_engine import (
    GenerationContext,
    GenerationPhase,
    GenerationRequest,
    GenerationResult,
    ScaffoldEngine,
)


class TestGenerationPhase:
    """测试生成阶段枚举"""

    def test_generation_phase_values(self):
        """测试生成阶段枚举值"""
        # TC-2.1.1: 生成阶段枚举测试
        assert GenerationPhase.INITIALIZATION.value == "initialization"
        assert GenerationPhase.CONTENT_ANALYSIS.value == "content_analysis"
        assert GenerationPhase.STRUCTURE_GENERATION.value == "structure_generation"
        assert GenerationPhase.FILE_CREATION.value == "file_creation"
        assert GenerationPhase.VALIDATION.value == "validation"
        assert GenerationPhase.COMPLETION.value == "completion"

    def test_generation_phase_ordering(self):
        """测试生成阶段顺序"""
        # TC-2.1.2: 阶段顺序测试
        phases = list(GenerationPhase)
        order = [phase.value for phase in phases]

        expected_order = [
            "initialization",
            "content_analysis",
            "structure_generation",
            "file_creation",
            "validation",
            "completion",
        ]

        assert order == expected_order


class TestGenerationRequest:
    """测试生成请求"""

    def test_generation_request_creation(self):
        """测试生成请求创建"""
        # TC-2.1.3: 请求创建测试
        request = GenerationRequest(
            description="创建一个Web应用",
            input_type=InputType.TEXT,
            auto_confirm=False,
            output_directory="./test_project",
        )

        assert request.description == "创建一个Web应用"
        assert request.input_type == InputType.TEXT
        assert not request.auto_confirm
        assert request.output_directory == "./test_project"
        assert request.options == {}
        assert request.context is None

    def test_generation_request_with_options(self):
        """测试带选项的生成请求"""
        # TC-2.1.4: 选项请求测试
        options = {
            "framework": "react",
            "language": "typescript",
            "include_tests": True,
        }

        request = GenerationRequest(description="React应用", options=options)

        assert request.options == options
        assert request.options["framework"] == "react"
        assert request.options["include_tests"]

    def test_generation_request_validation(self):
        """测试生成请求验证"""
        # TC-2.1.5: 请求验证测试
        # 有效请求
        valid_request = GenerationRequest(
            description="有效的项目描述", output_directory="./valid_path"
        )
        assert valid_request.validate() == []

        # 无效请求 - 空描述
        invalid_request = GenerationRequest(description="")
        errors = invalid_request.validate()
        assert len(errors) > 0
        assert any("描述" in error for error in errors)

    def test_generation_request_from_command(self):
        """测试从命令创建请求"""
        # TC-2.1.6: 命令转换测试
        command = ScaffoldCommand(
            input_type=InputType.TEXT, description="创建一个API服务", auto_confirm=True
        )

        request = GenerationRequest.from_command(
            command, output_directory="./api_project"
        )

        assert request.description == "创建一个API服务"
        assert request.input_type == InputType.TEXT
        assert request.auto_confirm
        assert request.output_directory == "./api_project"


class TestGenerationContext:
    """测试生成上下文"""

    def test_generation_context_creation(self):
        """测试生成上下文创建"""
        # TC-2.1.7: 上下文创建测试
        request = GenerationRequest(description="测试项目", output_directory="./test")

        context = GenerationContext(request)

        assert context.request == request
        assert context.phase == GenerationPhase.INITIALIZATION
        assert context.created_files == []
        assert context.errors == []
        assert context.warnings == []
        assert context.metadata == {}
        assert isinstance(context.start_time, float)

    def test_generation_context_phase_progression(self):
        """测试生成阶段推进"""
        # TC-2.1.8: 阶段推进测试
        context = GenerationContext(GenerationRequest("测试", "./test"))

        assert context.phase == GenerationPhase.INITIALIZATION

        context.advance_phase(GenerationPhase.CONTENT_ANALYSIS)
        assert context.phase == GenerationPhase.CONTENT_ANALYSIS

        context.advance_phase(GenerationPhase.STRUCTURE_GENERATION)
        assert context.phase == GenerationPhase.STRUCTURE_GENERATION

    def test_generation_context_file_tracking(self):
        """测试文件跟踪"""
        # TC-2.1.9: 文件跟踪测试
        context = GenerationContext(GenerationRequest("测试", "./test"))

        file1 = ProjectFile("src/main.py", "print('Hello')")
        file2 = ProjectFile("README.md", "# Test Project")

        context.add_file(file1)
        context.add_file(file2)

        assert len(context.created_files) == 2
        assert file1 in context.created_files
        assert file2 in context.created_files

    def test_generation_context_error_handling(self):
        """测试错误处理"""
        # TC-2.1.10: 错误处理测试
        context = GenerationContext(GenerationRequest("测试", "./test"))

        error = ValidationError("测试错误")
        context.add_error(error)

        assert len(context.errors) == 1
        assert error in context.errors
        assert context.has_errors()

    def test_generation_context_warning_handling(self):
        """测试警告处理"""
        # TC-2.1.11: 警告处理测试
        context = GenerationContext(GenerationRequest("测试", "./test"))

        context.add_warning("测试警告")
        context.add_warning("另一个警告")

        assert len(context.warnings) == 2
        assert "测试警告" in context.warnings
        assert context.has_warnings()

    def test_generation_context_metadata(self):
        """测试元数据管理"""
        # TC-2.1.12: 元数据测试
        context = GenerationContext(GenerationRequest("测试", "./test"))

        context.set_metadata("framework", "react")
        context.set_metadata("language", "typescript")

        assert context.get_metadata("framework") == "react"
        assert context.get_metadata("language") == "typescript"
        assert context.get_metadata("nonexistent") is None

    def test_generation_context_duration(self):
        """测试持续时间计算"""
        # TC-2.1.13: 持续时间测试
        context = GenerationContext(GenerationRequest("测试", "./test"))

        # 模拟时间流逝
        import time

        time.sleep(0.1)

        duration = context.get_duration()
        assert duration >= 0.1  # 至少100ms


class TestGenerationResult:
    """测试生成结果"""

    def test_generation_result_success(self):
        """测试成功生成结果"""
        # TC-2.1.14: 成功结果测试
        project_structure = ProjectStructure(
            files=[ProjectFile("test.py", "content")], description="测试项目"
        )

        result = GenerationResult.success(
            project_structure=project_structure,
            duration=5.0,
            metadata={"files_created": 1},
        )

        assert result.success
        assert result.project_structure == project_structure
        assert result.duration == 5.0
        assert result.metadata["files_created"] == 1
        assert len(result.errors) == 0

    def test_generation_result_failure(self):
        """测试失败生成结果"""
        # TC-2.1.15: 失败结果测试
        error = ValidationError("生成失败")

        result = GenerationResult.failure(errors=[error], duration=2.5)

        assert not result.success
        assert result.project_structure is None
        assert result.duration == 2.5
        assert len(result.errors) == 1
        assert error in result.errors

    def test_generation_result_with_warnings(self):
        """测试带警告的生成结果"""
        # TC-2.1.16: 警告结果测试
        project_structure = ProjectStructure(files=[], description="测试项目")

        result = GenerationResult.success(
            project_structure=project_structure,
            duration=5.0,
            warnings=["路径已存在", "某些文件被跳过"],
        )

        assert result.success
        assert len(result.warnings) == 2
        assert "路径已存在" in result.warnings

    def test_generation_result_to_scaffold_result(self):
        """测试转换为脚手架结果"""
        # TC-2.1.17: 结果转换测试
        project_structure = ProjectStructure(
            files=[ProjectFile("test.py", "content")], description="测试项目"
        )

        gen_result = GenerationResult.success(
            project_structure=project_structure, duration=3.0, warnings=["测试警告"]
        )

        scaffold_result = gen_result.to_scaffold_result()

        assert scaffold_result.is_success
        assert scaffold_result.project_structure == project_structure
        assert len(scaffold_result.warnings) == 1


class TestScaffoldEngine:
    """测试脚手架核心引擎"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.config = ScaffoldConfig()
        self.error_handler = ErrorHandler()
        self.engine = ScaffoldEngine(
            config=self.config, error_handler=self.error_handler
        )

    def test_engine_creation(self):
        """测试引擎创建"""
        # TC-2.1.18: 引擎创建测试
        engine = ScaffoldEngine()

        assert engine.config is not None
        assert engine.error_handler is not None
        assert isinstance(engine.config, ScaffoldConfig)
        assert isinstance(engine.error_handler, ErrorHandler)

    def test_engine_with_custom_components(self):
        """测试带自定义组件的引擎"""
        # TC-2.1.19: 自定义组件测试
        custom_config = ScaffoldConfig()
        custom_config.set("test.value", "custom")

        custom_error_handler = ErrorHandler()

        engine = ScaffoldEngine(
            config=custom_config, error_handler=custom_error_handler
        )

        assert engine.config.get("test.value") == "custom"
        assert engine.error_handler == custom_error_handler

    @pytest.mark.asyncio
    async def test_generate_project_success(self):
        """测试成功生成项目"""
        # TC-2.1.20: 成功生成测试
        request = GenerationRequest(
            description="创建一个简单的Python应用", output_directory="./test_output"
        )

        # Mock dependencies
        with (
            patch.object(self.engine, "_analyze_content") as mock_analyze,
            patch.object(self.engine, "_generate_structure") as mock_generate,
            patch.object(self.engine, "_create_files") as mock_create,
        ):
            # 设置mock返回值
            mock_analyze.return_value = {"project_type": "python_app"}
            mock_generate.return_value = ProjectStructure(
                files=[ProjectFile("main.py", "print('Hello')")],
                description="Python应用",
            )
            mock_create.return_value = []

            result = await self.engine.generate(request)

            assert result.success
            assert result.project_structure is not None
            assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_generate_project_with_validation_error(self):
        """测试生成项目时的验证错误"""
        # TC-2.1.21: 验证错误测试
        request = GenerationRequest(
            description="", input_type=InputType.TEXT
        )  # 空描述，无文件路径

        result = await self.engine.generate(request)

        assert not result.success
        assert len(result.errors) > 0
        assert any(
            "必须提供项目描述或描述文件" in str(error) for error in result.errors
        )

    @pytest.mark.asyncio
    async def test_generate_project_with_file_input(self):
        """测试从文件生成项目"""
        # TC-2.1.22: 文件输入测试
        # 创建临时文件
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("创建一个包含用户认证的Web应用")
            temp_file = f.name

        try:
            request = GenerationRequest(
                description="",
                input_type=InputType.FILE,
                file_path=temp_file,
                output_directory="./test_output",
            )

            with (
                patch.object(self.engine, "_analyze_content") as mock_analyze,
                patch.object(self.engine, "_generate_structure") as mock_generate,
                patch.object(self.engine, "_create_files") as mock_create,
            ):
                mock_analyze.return_value = {"project_type": "web_app"}
                mock_generate.return_value = ProjectStructure(
                    files=[], description="Web应用"
                )
                mock_create.return_value = []

                result = await self.engine.generate(request)

                assert result.success
                mock_analyze.assert_called_once()

        finally:
            import os

            if os.path.exists(temp_file):
                os.unlink(temp_file)

    @pytest.mark.asyncio
    async def test_content_analysis(self):
        """测试内容分析"""
        # TC-2.1.23: 内容分析测试
        request = GenerationRequest(
            description="创建一个React应用，包含用户登录和仪表板功能"
        )

        analysis = await self.engine._analyze_content(request)

        assert analysis is not None
        assert isinstance(analysis, dict)
        assert "keywords" in analysis
        assert "project_type" in analysis
        assert "features" in analysis

    @pytest.mark.asyncio
    async def test_structure_generation(self):
        """测试结构生成"""
        # TC-2.1.24: 结构生成测试
        analysis = {
            "project_type": "web_app",
            "keywords": ["react", "login", "dashboard"],
            "features": ["authentication", "dashboard"],
        }

        request = GenerationRequest(
            description="React应用", options={"framework": "react"}
        )

        structure = await self.engine._generate_structure(request, analysis)

        assert isinstance(structure, ProjectStructure)
        assert structure.description is not None
        assert isinstance(structure.files, list)

    @pytest.mark.asyncio
    async def test_file_creation_dry_run(self):
        """测试文件创建（干运行）"""
        # TC-2.1.25: 干运行测试
        structure = ProjectStructure(
            files=[
                ProjectFile("src/main.py", "print('Hello')"),
                ProjectFile("README.md", "# Project"),
            ],
            description="测试项目",
        )

        request = GenerationRequest(
            description="测试", output_directory="./test_output", dry_run=True
        )

        errors = await self.engine._create_files(structure, request)

        # 干运行不应该实际创建文件，也不应该有错误
        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_file_creation_with_overwrite_protection(self):
        """测试文件创建时的覆盖保护"""
        # TC-2.1.26: 覆盖保护测试
        structure = ProjectStructure(
            files=[ProjectFile("test.py", "content")], description="测试项目"
        )

        request = GenerationRequest(
            description="测试",
            output_directory="./test_output",
            overwrite_existing=False,
        )

        # 创建临时目录和文件
        import os
        import tempfile

        temp_dir = tempfile.mkdtemp()
        try:
            test_dir = os.path.join(temp_dir, "test_output")
            os.makedirs(test_dir)

            # 创建已存在的文件
            existing_file = os.path.join(test_dir, "test.py")
            with open(existing_file, "w") as f:
                f.write("existing content")

            request.output_directory = test_dir

            errors = await self.engine._create_files(structure, request)

            # 文件已存在且不允许覆盖，应该有错误
            assert len(errors) > 0
            assert any("already exists" in str(error) for error in errors)

        finally:
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_engine_progress_callback(self):
        """测试进度回调"""
        # TC-2.1.27: 进度回调测试
        progress_calls = []

        def progress_callback(phase, progress, message):
            progress_calls.append((phase, progress, message))

        engine = ScaffoldEngine(progress_callback=progress_callback)

        # 模拟进度更新
        engine._report_progress(GenerationPhase.CONTENT_ANALYSIS, 0.5, "分析中")

        assert len(progress_calls) == 1
        phase, progress, message = progress_calls[0]
        assert phase == GenerationPhase.CONTENT_ANALYSIS
        assert progress == 0.5
        assert message == "分析中"

    @pytest.mark.asyncio
    async def test_engine_cancellation(self):
        """测试引擎取消操作"""
        # TC-2.1.28: 取消操作测试
        GenerationRequest(description="测试项目", output_directory="./test_output")

        # 测试引擎对CancelledError的处理
        result = GenerationResult.failure(
            [asyncio.CancelledError("Test cancellation")], 0.1
        )

        assert not result.success
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], asyncio.CancelledError)

    @pytest.mark.asyncio
    async def test_engine_with_retry_mechanism(self):
        """测试引擎重试机制"""
        # TC-2.1.29: 重试机制测试
        request = GenerationRequest(
            description="这是一个测试项目用于验证重试机制",
            output_directory="./test_output",
        )

        call_count = 0

        async def mock_generate_with_failure(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return ProjectStructure(files=[], description="Success")

        with patch.object(
            self.engine, "_generate_structure", side_effect=mock_generate_with_failure
        ):
            result = await self.engine.generate(request)

            assert result.success
            assert call_count == 3  # 重试了3次

    @pytest.mark.asyncio
    async def test_engine_error_recovery(self):
        """测试引擎错误恢复"""
        # TC-2.1.30: 错误恢复测试
        GenerationRequest(description="测试项目", output_directory="./test_output")

        # 设置可恢复的错误策略
        self.engine.configure_recovery_strategy("ConnectionError", max_retries=2)

        call_count = 0

        async def mock_operation():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Recoverable error")
            return "success"

        result = await self.engine._execute_with_recovery(
            mock_operation, "ConnectionError"
        )

        assert result == "success"
        assert call_count == 2  # 失败一次后重试成功

    def test_engine_configuration_validation(self):
        """测试引擎配置验证"""
        # TC-2.1.31: 配置验证测试
        # 测试有效配置
        valid_config = ScaffoldConfig()
        valid_config.set("scaffold.max_files", 100)

        engine = ScaffoldEngine(config=valid_config)
        assert engine.config.get("scaffold.max_files") == 100

        # 测试无效配置
        invalid_config = ScaffoldConfig()
        invalid_config.set("scaffold.max_files", -1)  # 无效值

        # 应该能够处理无效配置
        engine = ScaffoldEngine(config=invalid_config)
        assert engine is not None

    @pytest.mark.asyncio
    async def test_engine_performance_monitoring(self):
        """测试引擎性能监控"""
        # TC-2.1.32: 性能监控测试
        request = GenerationRequest(
            description="测试项目", output_directory="./test_output"
        )

        # Mock快速操作
        with (
            patch.object(self.engine, "_analyze_content"),
            patch.object(self.engine, "_generate_structure"),
            patch.object(self.engine, "_create_files"),
        ):
            result = await self.engine.generate(request)

            # 检查性能指标
            assert result.duration is not None
            assert result.duration >= 0
            assert result.metadata is not None


if __name__ == "__main__":
    # Run tests when this file is executed directly
    pytest.main([__file__, "-v"])
