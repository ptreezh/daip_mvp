"""
测试项目结构生成器
遵循TDD原则：先写测试，再实现功能
"""

import pytest
from pathlib import Path
from unittest.mock import patch
from daip_live.scaffolding.structure_generator import (
    ProjectStructureGenerator,
    TemplateEngine,
    TemplateType,
    TemplateConfig,
    GenerationStrategy,
    StructureGeneratorConfig
)
from daip_live.scaffolding.models import (
    ProjectStructure,
    ProjectFile,
    ValidationError,
    GenerationError
)


class TestTemplateType:
    """测试模板类型枚举"""

    def test_template_type_values(self):
        """测试模板类型枚举值"""
        # TC-2.2.1: 模板类型枚举测试
        assert TemplateType.BASIC.value == "basic"
        assert TemplateType.WEB_APP.value == "web_app"
        assert TemplateType.API.value == "api"
        assert TemplateType.CLI.value == "cli"
        assert TemplateType.LIBRARY.value == "library"
        assert TemplateType.MICROSERVICE.value == "microservice"


class TestTemplateConfig:
    """测试模板配置"""

    def test_template_config_creation(self):
        """测试模板配置创建"""
        # TC-2.2.2: 模板配置创建测试
        config = TemplateConfig(
            name="test_template",
            type=TemplateType.BASIC,
            description="Test template",
            file_patterns=["*.py", "*.md"],
            directory_structure={
                "src": ["main.py"],
                "tests": [],
                "docs": ["README.md"]
            }
        )

        assert config.name == "test_template"
        assert config.type == TemplateType.BASIC
        assert config.description == "Test template"
        assert "*.py" in config.file_patterns
        assert "src" in config.directory_structure

    def test_template_config_validation(self):
        """测试模板配置验证"""
        # TC-2.2.3: 模板配置验证测试
        # 有效配置
        config = TemplateConfig(
            name="valid_template",
            type=TemplateType.WEB_APP,
            description="Valid template"
        )
        assert config.validate() == []

        # 无效配置 - 空名称
        invalid_config = TemplateConfig(
            name="",
            type=TemplateType.BASIC,
            description="Invalid template"
        )
        errors = invalid_config.validate()
        assert len(errors) > 0
        assert any("模板名称不能为空" in error for error in errors)


class TestGenerationStrategy:
    """测试生成策略"""

    def test_generation_strategy_creation(self):
        """测试生成策略创建"""
        # TC-2.2.4: 生成策略创建测试
        strategy = GenerationStrategy(
            name="test_strategy",
            description="Test generation strategy",
            complexity_threshold=0.7,
            use_ai_generation=True,
            template_fallback=True
        )

        assert strategy.name == "test_strategy"
        assert strategy.complexity_threshold == 0.7
        assert strategy.use_ai_generation == True
        assert strategy.template_fallback == True

    def test_generation_strategy_should_use_ai(self):
        """测试AI生成判断"""
        # TC-2.2.5: AI生成判断测试
        strategy = GenerationStrategy(
            name="ai_strategy",
            complexity_threshold=0.5,
            use_ai_generation=True
        )

        # 高复杂度应该使用AI
        assert strategy.should_use_ai(0.8) == True

        # 低复杂度应该使用模板
        assert strategy.should_use_ai(0.3) == False

    def test_generation_strategy_should_use_template_fallback(self):
        """测试模板回退判断"""
        # TC-2.2.6: 模板回退判断测试
        strategy = GenerationStrategy(
            name="fallback_strategy",
            use_ai_generation=True,
            template_fallback=True
        )

        assert strategy.should_use_template_fallback() == True

        # 禁用回退的策略
        no_fallback_strategy = GenerationStrategy(
            name="no_fallback_strategy",
            use_ai_generation=True,
            template_fallback=False
        )

        assert no_fallback_strategy.should_use_template_fallback() == False


class TestStructureGeneratorConfig:
    """测试结构生成器配置"""

    def test_structure_generator_config_creation(self):
        """测试结构生成器配置创建"""
        # TC-2.2.7: 结构生成器配置创建测试
        strategy = GenerationStrategy("test_strategy")
        config = StructureGeneratorConfig(
            default_strategy=strategy,
            max_files=1000,
            max_directory_depth=10
        )

        assert config.default_strategy == strategy
        assert config.max_files == 1000
        assert config.max_directory_depth == 10

    def test_structure_generator_config_get_strategy_for_complexity(self):
        """测试根据复杂度获取策略"""
        # TC-2.2.8: 复杂度策略选择测试
        simple_strategy = GenerationStrategy("simple", complexity_threshold=0.3)
        complex_strategy = GenerationStrategy("complex", complexity_threshold=0.7)

        config = StructureGeneratorConfig(
            default_strategy=simple_strategy,
            strategies=[simple_strategy, complex_strategy]
        )

        # 低复杂度应该选择简单策略
        selected = config.get_strategy_for_complexity(0.2)
        assert selected.name == "simple"

        # 高复杂度应该选择复杂策略
        selected = config.get_strategy_for_complexity(0.8)
        assert selected.name == "complex"


class TestTemplateEngine:
    """测试模板引擎"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.template_engine = TemplateEngine()

    def test_template_engine_creation(self):
        """测试模板引擎创建"""
        # TC-2.2.9: 模板引擎创建测试
        engine = TemplateEngine()
        assert len(engine.templates) == 0
        assert engine.default_template_type == TemplateType.BASIC

    def test_template_engine_add_template(self):
        """测试添加模板"""
        # TC-2.2.10: 添加模板测试
        config = TemplateConfig(
            name="test_template",
            type=TemplateType.WEB_APP,
            description="Test template"
        )

        self.template_engine.add_template(config)
        assert len(self.template_engine.templates) == 1
        assert "test_template" in self.template_engine.templates

    def test_template_engine_get_template(self):
        """测试获取模板"""
        # TC-2.2.11: 获取模板测试
        config = TemplateConfig(
            name="test_template",
            type=TemplateType.WEB_APP
        )

        self.template_engine.add_template(config)
        retrieved = self.template_engine.get_template("test_template")
        assert retrieved == config

        # 获取不存在的模板
        assert self.template_engine.get_template("nonexistent") is None

    def test_template_engine_get_template_by_type(self):
        """测试按类型获取模板"""
        # TC-2.2.12: 按类型获取模板测试
        web_config = TemplateConfig("web_template", TemplateType.WEB_APP)
        api_config = TemplateConfig("api_template", TemplateType.API)

        self.template_engine.add_template(web_config)
        self.template_engine.add_template(api_config)

        # 按类型获取
        web_templates = self.template_engine.get_templates_by_type(TemplateType.WEB_APP)
        assert len(web_templates) == 1
        assert web_templates[0].name == "web_template"

    def test_template_engine_apply_template(self):
        """测试应用模板"""
        # TC-2.2.13: 应用模板测试
        config = TemplateConfig(
            name="basic_template",
            type=TemplateType.BASIC,
            directory_structure={
                "src": ["main.py"],
                "tests": [],
                "docs": ["README.md"]
            },
            file_templates={
                "main.py": "def main():\n    print('Hello, World!')\n",
                "README.md": "# {project_name}\n\n{description}"
            }
        )

        self.template_engine.add_template(config)

        # 应用模板
        context = {
            "project_name": "test_project",
            "description": "Test project description"
        }

        structure = self.template_engine.apply_template(
            "basic_template",
            context,
            "./output"
        )

        assert structure.description == "Generated using template: basic_template"
        assert len(structure.files) == 2  # main.py and README.md

        # 检查文件内容 - 处理路径分隔符差异
        files = {f.path.replace("\\", "/"): f.content for f in structure.files}
        assert "def main():" in files.get("src/main.py", "")
        assert "# test_project" in files.get("docs/README.md", "")
        assert "Test project description" in files.get("docs/README.md", "")

    def test_template_engine_template_variables(self):
        """测试模板变量处理"""
        # TC-2.2.14: 模板变量测试
        template_content = """
Project: {project_name}
Author: {author}
Date: {date}
Language: {language}
Features: {features}
"""

        context = {
            "project_name": "my_app",
            "author": "Developer",
            "date": "2025-01-01",
            "language": "Python",
            "features": "web, api, database"
        }

        rendered = self.template_engine.render_template(template_content, context)

        assert "Project: my_app" in rendered
        assert "Author: Developer" in rendered
        assert "Date: 2025-01-01" in rendered
        assert "Language: Python" in rendered
        assert "web, api, database" in rendered

    def test_template_engine_missing_variables(self):
        """测试缺失变量处理"""
        # TC-2.2.15: 缺失变量测试
        template_content = "Hello {name}, welcome to {project}!"

        # 不完整的上下文
        context = {"name": "User"}

        rendered = self.template_engine.render_template(template_content, context)

        # 缺失的变量应该保持原样或使用默认值
        assert "Hello User" in rendered
        assert "{project}" in rendered  # 保持原样

    def test_template_engine_conditionals(self):
        """测试条件渲染"""
        # TC-2.2.16: 条件渲染测试
        template_content = """
{#if has_auth#}
Authentication module enabled
{#endif#}

{#if database#}
Database: {database_type}
{#endif#}
"""

        # 有认证的上下文
        auth_context = {"has_auth": True}
        rendered = self.template_engine.render_template(template_content, auth_context)
        assert "Authentication module enabled" in rendered

        # 无认证的上下文
        no_auth_context = {"has_auth": False}
        rendered = self.template_engine.render_template(template_content, no_auth_context)
        assert "Authentication module enabled" not in rendered

    def test_template_engine_loops(self):
        """测试循环渲染"""
        # TC-2.2.17: 循环渲染测试
        template_content = """
Features:
{#for feature in features#}
- {feature}
{#endfor#}
"""

        context = {
            "features": ["authentication", "database", "api"]
        }

        rendered = self.template_engine.render_template(template_content, context)

        assert "- authentication" in rendered
        assert "- database" in rendered
        assert "- api" in rendered


class TestProjectStructureGenerator:
    """测试项目结构生成器"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.config = StructureGeneratorConfig()
        self.generator = ProjectStructureGenerator(config=self.config)

    def test_generator_creation(self):
        """测试生成器创建"""
        # TC-2.2.18: 生成器创建测试
        generator = ProjectStructureGenerator()
        assert generator.config is not None
        assert generator.template_engine is not None

    def test_generator_with_custom_config(self):
        """测试使用自定义配置创建生成器"""
        # TC-2.2.19: 自定义配置生成器测试
        strategy = GenerationStrategy("custom_strategy")
        config = StructureGeneratorConfig(
            default_strategy=strategy,
            max_files=500
        )

        generator = ProjectStructureGenerator(config=config)
        assert generator.config.default_strategy == strategy
        assert generator.config.max_files == 500

    @pytest.mark.asyncio
    async def test_generate_structure_with_template(self):
        """测试使用模板生成结构"""
        # TC-2.2.20: 模板结构生成测试
        # 设置模板
        template_config = TemplateConfig(
            name="simple_template",
            type=TemplateType.WEB_APP,  # 使用不同类型避免冲突
            directory_structure={
                "src": ["main.py"],
                "tests": ["test_main.py"]
            },
            file_templates={
                "main.py": "def main():\n    pass\n",
                "test_main.py": "def test_main():\n    assert True\n"
            }
        )

        self.generator.template_engine.add_template(template_config)

        # 生成请求
        analysis = {
            "content": "Simple Python application",
            "keywords": ["python", "simple", "web"],
            "project_type": "web_app",
            "features": [],
            "complexity": 0.3
        }

        context = {
            "project_name": "test_app",
            "description": "Test application"
        }

        structure = await self.generator.generate_structure(analysis, context)

        assert structure.description is not None
        assert len(structure.files) == 2  # main.py and test_main.py

        # 检查文件路径 - 处理路径分隔符差异
        file_paths = [f.path.replace("\\", "/") for f in structure.files]
        assert "src/main.py" in file_paths
        assert "tests/test_main.py" in file_paths

    @pytest.mark.asyncio
    async def test_generate_structure_with_ai(self):
        """测试使用AI生成结构"""
        # TC-2.2.21: AI结构生成测试
        # 配置AI策略
        ai_strategy = GenerationStrategy(
            name="ai_strategy",
            complexity_threshold=0.5,
            use_ai_generation=True
        )

        config = StructureGeneratorConfig(default_strategy=ai_strategy)
        generator = ProjectStructureGenerator(config=config)

        # 高复杂度分析
        analysis = {
            "content": "Complex web application with microservices architecture",
            "keywords": ["web", "microservices", "api", "database", "auth"],
            "project_type": "web_app",
            "features": ["authentication", "database", "api"],
            "complexity": 0.8
        }

        context = {
            "project_name": "complex_app",
            "description": "Complex web application"
        }

        # Mock AI生成
        expected_structure = ProjectStructure(
            description="AI generated complex web app",
            files=[
                ProjectFile(path="src/app.py", content=""),
                ProjectFile(path="src/auth.py", content=""),
                ProjectFile(path="src/api.py", content="")
            ]
        )

        with patch.object(generator, '_generate_with_ai', return_value=expected_structure):
            structure = await generator.generate_structure(analysis, context)

            assert structure.description == "AI generated complex web app"
            assert len(structure.files) == 3

    @pytest.mark.asyncio
    async def test_generate_structure_with_fallback(self):
        """测试回退机制"""
        # TC-2.2.22: 回退机制测试
        # 配置带回退的策略
        fallback_strategy = GenerationStrategy(
            name="fallback_strategy",
            use_ai_generation=True,
            template_fallback=True
        )

        config = StructureGeneratorConfig(default_strategy=fallback_strategy)
        generator = ProjectStructureGenerator(config=config)

        # 添加简单模板
        template_config = TemplateConfig(
            name="fallback_template",
            type=TemplateType.BASIC,
            directory_structure={"src": ["main.py"]},
            file_templates={"main.py": "# Fallback template\n"}
        )

        generator.template_engine.add_template(template_config)

        analysis = {
            "content": "Simple project",
            "complexity": 0.6  # 触发AI生成
        }

        context = {"project_name": "fallback_test"}

        # Mock AI失败，模板成功
        with patch.object(generator, '_generate_with_ai', side_effect=GenerationError("AI failed")):
            structure = await generator.generate_structure(analysis, context)

            # 应该回退到模板生成
            assert len(structure.files) == 1
            assert structure.files[0].path.replace("\\", "/") == "src/main.py"

    @pytest.mark.asyncio
    async def test_generate_structure_validation(self):
        """测试生成结构验证"""
        # TC-2.2.23: 结构验证测试
        # 创建会导致验证失败的请求
        analysis = {
            "content": "x" * 10000,  # 超长内容
            "complexity": 0.9
        }

        context = {"project_name": "test"}

        # 限制文件数量的配置
        config = StructureGeneratorConfig(max_files=1)
        generator = ProjectStructureGenerator(config=config)

        with pytest.raises(ValidationError):
            await generator.generate_structure(analysis, context)

    def test_get_recommended_template_type(self):
        """测试推荐模板类型"""
        # TC-2.2.24: 模板类型推荐测试
        # Web应用
        analysis = {
            "project_type": "web",
            "keywords": ["web", "frontend", "backend"]
        }
        template_type = self.generator.get_recommended_template_type(analysis)
        assert template_type == TemplateType.WEB_APP

        # API项目
        analysis = {
            "project_type": "api",
            "keywords": ["api", "rest", "endpoint"]
        }
        template_type = self.generator.get_recommended_template_type(analysis)
        assert template_type == TemplateType.API

        # CLI项目
        analysis = {
            "project_type": "cli",
            "keywords": ["cli", "command", "tool"]
        }
        template_type = self.generator.get_recommended_template_type(analysis)
        assert template_type == TemplateType.CLI

    def test_validate_generation_request(self):
        """测试生成请求验证"""
        # TC-2.2.25: 请求验证测试
        # 有效请求
        analysis = {
            "content": "Valid content",
            "complexity": 0.5
        }
        context = {"project_name": "valid_project"}

        errors = self.generator.validate_generation_request(analysis, context)
        assert len(errors) == 0

        # 无效请求 - 缺少必需字段
        invalid_analysis = {"content": ""}  # 缺少complexity
        invalid_context = {}  # 缺少project_name

        errors = self.generator.validate_generation_request(invalid_analysis, invalid_context)
        assert len(errors) > 0
        assert any("缺少必需的分析字段" in error for error in errors)

    @pytest.mark.asyncio
    async def test_custom_template_creation(self):
        """测试自定义模板创建"""
        # TC-2.2.26: 自定义模板创建测试
        # 基于分析创建自定义模板
        analysis = {
            "content": "Python project with tests and docs",
            "keywords": ["python", "testing", "documentation"],
            "features": ["tests", "docs"],
            "complexity": 0.4
        }

        context = {
            "project_name": "custom_project",
            "author": "Developer"
        }

        template = await self.generator.create_custom_template(analysis, context)

        assert template.name is not None
        assert template.type == TemplateType.BASIC
        assert len(template.directory_structure) > 0
        assert len(template.file_templates) > 0

        # 验证模板可以应用
        self.generator.template_engine.add_template(template)
        structure = self.generator.template_engine.apply_template(
            template.name,
            context,
            "./output"
        )

        assert len(structure.files) > 0


if __name__ == "__main__":
    # Run tests when this file is executed directly
    pytest.main([__file__, "-v"])