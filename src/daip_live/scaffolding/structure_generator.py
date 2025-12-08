"""
项目结构生成器
提供基于模板和AI的项目结构生成功能
"""

import re
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime

from .models import (
    ProjectStructure,
    ProjectFile,
    ValidationError,
    GenerationError
)


class TemplateType(Enum):
    """模板类型枚举"""
    BASIC = "basic"
    WEB_APP = "web_app"
    API = "api"
    CLI = "cli"
    LIBRARY = "library"
    MICROSERVICE = "microservice"


@dataclass
class TemplateConfig:
    """模板配置"""
    name: str
    type: TemplateType
    description: str = ""
    file_patterns: List[str] = field(default_factory=list)
    directory_structure: Dict[str, List[str]] = field(default_factory=dict)
    file_templates: Dict[str, str] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        """验证模板配置"""
        errors = []

        if not self.name.strip():
            errors.append("模板名称不能为空")

        if not self.type:
            errors.append("模板类型不能为空")

        # 验证目录结构
        for directory, files in self.directory_structure.items():
            if not isinstance(files, list):
                errors.append(f"目录 {directory} 的文件列表必须是数组")

        # 验证文件模板
        for file_path, template in self.file_templates.items():
            if not isinstance(template, str):
                errors.append(f"文件 {file_path} 的模板必须是字符串")

        return errors


@dataclass
class GenerationStrategy:
    """生成策略"""
    name: str
    description: str = ""
    complexity_threshold: float = 0.5
    use_ai_generation: bool = False
    template_fallback: bool = True
    max_attempts: int = 3
    retry_delay: float = 1.0

    def should_use_ai(self, complexity: float) -> bool:
        """判断是否应该使用AI生成"""
        return self.use_ai_generation and complexity >= self.complexity_threshold

    def should_use_template_fallback(self) -> bool:
        """判断是否应该使用模板回退"""
        return self.template_fallback


@dataclass
class StructureGeneratorConfig:
    """结构生成器配置"""
    default_strategy: GenerationStrategy = field(default_factory=lambda: GenerationStrategy("default"))
    strategies: List[GenerationStrategy] = field(default_factory=list)
    max_files: int = 1000
    max_directory_depth: int = 10
    enable_ai_generation: bool = False
    ai_model_config: Dict[str, Any] = field(default_factory=dict)

    def get_strategy_for_complexity(self, complexity: float) -> GenerationStrategy:
        """根据复杂度选择最适合的策略"""
        # 首先尝试找到匹配复杂度阈值的策略
        suitable_strategies = [
            s for s in self.strategies
            if complexity >= s.complexity_threshold
        ]

        if suitable_strategies:
            # 选择复杂度阈值最接近的策略
            return min(suitable_strategies, key=lambda s: abs(s.complexity_threshold - complexity))

        return self.default_strategy


class TemplateRenderer:
    """模板渲染器"""

    def __init__(self):
        self.default_context = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def render_template(self, template: str, context: Dict[str, Any]) -> str:
        """渲染模板"""
        # 合并默认上下文
        full_context = {**self.default_context, **context}

        result = template

        # 简单的变量替换 {variable}
        result = self._replace_variables(result, full_context)

        # 条件渲染 {#if condition#}...{#endif#}
        result = self._process_conditionals(result, full_context)

        # 循环渲染 {#for item in items#}...{#endfor#}
        result = self._process_loops(result, full_context)

        return result

    def _replace_variables(self, template: str, context: Dict[str, Any]) -> str:
        """替换变量"""
        def replace_var(match):
            var_name = match.group(1)
            value = context.get(var_name, match.group(0))  # 保持原样如果找不到变量

            if isinstance(value, (list, dict)):
                return str(value)
            return str(value)

        return re.sub(r'\{([^}]+)\}', replace_var, template)

    def _process_conditionals(self, template: str, context: Dict[str, Any]) -> str:
        """处理条件渲染"""
        pattern = r'\{#if\s+([^#]+)#\}(.*?)\{#endif#\}'

        def replace_conditional(match):
            condition = match.group(1).strip()
            content = match.group(2)

            # 简单的条件判断
            if self._evaluate_condition(condition, context):
                return content
            else:
                return ""

        return re.sub(pattern, replace_conditional, template, flags=re.DOTALL)

    def _process_loops(self, template: str, context: Dict[str, Any]) -> str:
        """处理循环渲染"""
        pattern = r'\{#for\s+(\w+)\s+in\s+(\w+)\#\}(.*?)\{#endfor#\}'

        def replace_loop(match):
            item_var = match.group(1)
            list_var = match.group(2)
            content = match.group(3)

            items = context.get(list_var, [])
            if not isinstance(items, (list, tuple)):
                return ""

            result_parts = []
            for item in items:
                loop_context = {**context, item_var: item}
                loop_content = self._replace_variables(content, loop_context)
                result_parts.append(loop_content)

            return "".join(result_parts)

        return re.sub(pattern, replace_loop, template, flags=re.DOTALL)

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """评估条件"""
        # 简单的条件评估
        condition = condition.strip()

        # 检查变量是否存在且为真值
        if condition in context:
            value = context[condition]
            return bool(value)

        # 检查布尔值
        if condition.lower() in ("true", "false"):
            return condition.lower() == "true"

        return False


class TemplateEngine:
    """模板引擎"""

    def __init__(self):
        self.templates: Dict[str, TemplateConfig] = {}
        self.renderer = TemplateRenderer()
        self.default_template_type = TemplateType.BASIC

    def add_template(self, config: TemplateConfig) -> None:
        """添加模板"""
        errors = config.validate()
        if errors:
            raise ValidationError(f"模板配置无效: {', '.join(errors)}")

        self.templates[config.name] = config

    def get_template(self, name: str) -> Optional[TemplateConfig]:
        """获取模板"""
        return self.templates.get(name)

    def get_templates_by_type(self, template_type: TemplateType) -> List[TemplateConfig]:
        """按类型获取模板"""
        return [
            config for config in self.templates.values()
            if config.type == template_type
        ]

    def apply_template(self, template_name: str, context: Dict[str, Any], output_path: str) -> ProjectStructure:
        """应用模板生成项目结构"""
        template = self.get_template(template_name)
        if not template:
            raise ValidationError(f"模板不存在: {template_name}")

        files = []

        # 生成目录结构和文件
        for directory, file_list in template.directory_structure.items():
            for file_name in file_list:
                file_path = str(Path(directory) / file_name)

                # 获取文件模板内容
                template_content = template.file_templates.get(file_name, "")
                rendered_content = self.renderer.render_template(template_content, context)

                file = ProjectFile(
                    path=file_path,
                    content=rendered_content
                )
                files.append(file)

        return ProjectStructure(
            description=f"Generated using template: {template_name}",
            files=files
        )

    def render_template(self, template: str, context: Dict[str, Any]) -> str:
        """渲染单个模板"""
        return self.renderer.render_template(template, context)

    def _detect_file_type(self, file_name: str) -> str:
        """检测文件类型"""
        extension = Path(file_name).suffix.lower()

        type_mapping = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".html": "html",
            ".css": "css",
            ".md": "markdown",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".xml": "xml",
            ".txt": "text"
        }

        return type_mapping.get(extension, "unknown")


class ProjectStructureGenerator:
    """项目结构生成器"""

    def __init__(self, config: Optional[StructureGeneratorConfig] = None):
        self.config = config or StructureGeneratorConfig()
        self.template_engine = TemplateEngine()

        # 初始化默认模板
        self._initialize_default_templates()

    async def generate_structure(
        self,
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ProjectStructure:
        """生成项目结构"""
        # 验证请求
        errors = self.validate_generation_request(analysis, context)
        if errors:
            raise ValidationError(f"生成请求无效: {', '.join(errors)}")

        # 选择生成策略
        complexity = analysis.get("complexity", 0.5)
        strategy = self.config.get_strategy_for_complexity(complexity)

        try:
            # 尝试AI生成
            if strategy.should_use_ai(complexity):
                try:
                    return await self._generate_with_ai(analysis, context, strategy)
                except Exception as e:
                    if not strategy.should_use_template_fallback():
                        raise GenerationError(f"AI生成失败且无回退策略: {str(e)}")

                    # 回退到模板生成
                    return await self._generate_with_template(analysis, context)

            # 使用模板生成
            return await self._generate_with_template(analysis, context)

        except Exception as e:
            raise GenerationError(f"结构生成失败: {str(e)}")

    async def _generate_with_ai(
        self,
        analysis: Dict[str, Any],
        context: Dict[str, Any],
        strategy: GenerationStrategy
    ) -> ProjectStructure:
        """使用AI生成结构"""
        # 这里应该调用实际的AI服务
        # 目前返回一个模拟的AI生成结果
        project_type = analysis.get("project_type", "basic")
        features = analysis.get("features", [])

        files = []

        # 根据项目类型和特性生成文件
        if "web" in project_type or "api" in project_type:
            files.append(ProjectFile(
                path="src/main.py",
                content="# AI generated main application\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get(\"/\")\ndef read_root():\n    return {\"message\": \"Hello World\"}\n"
            ))
            files.append(ProjectFile(
                path="requirements.txt",
                content="fastapi>=0.68.0\nuvicorn>=0.15.0\n"
            ))

        if "auth" in features:
            files.append(ProjectFile(
                path="src/auth.py",
                content="# AI generated authentication module\nclass AuthManager:\n    def __init__(self):\n        pass\n"
            ))

        if "database" in features:
            files.append(ProjectFile(
                path="src/database.py",
                content="# AI generated database module\nclass DatabaseManager:\n    def __init__(self):\n        pass\n"
            ))

        return ProjectStructure(
            description=f"AI generated {project_type} project",
            files=files
        )

    async def _generate_with_template(
        self,
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> ProjectStructure:
        """使用模板生成结构"""
        template_type = self.get_recommended_template_type(analysis)
        templates = self.template_engine.get_templates_by_type(template_type)

        if not templates:
            # 如果没有找到合适模板，创建自定义模板
            template = await self.create_custom_template(analysis, context)
            self.template_engine.add_template(template)
            templates = [template]

        # 使用最后添加的模板（最新）
        template = templates[-1]
        return self.template_engine.apply_template(template.name, context, "./output")

    def get_recommended_template_type(self, analysis: Dict[str, Any]) -> TemplateType:
        """根据分析结果推荐模板类型"""
        content = analysis.get("content", "").lower()
        keywords = analysis.get("keywords", [])
        project_type = analysis.get("project_type", "")

        # 根据关键词和项目类型推荐
        if any(keyword in ["web", "frontend", "backend", "html", "css", "javascript"] for keyword in keywords):
            return TemplateType.WEB_APP

        if any(keyword in ["api", "rest", "graphql", "endpoint"] for keyword in keywords):
            return TemplateType.API

        if any(keyword in ["cli", "command", "tool", "utility"] for keyword in keywords):
            return TemplateType.CLI

        if any(keyword in ["library", "package", "module"] for keyword in keywords):
            return TemplateType.LIBRARY

        if any(keyword in ["microservice", "service", "distributed"] for keyword in keywords):
            return TemplateType.MICROSERVICE

        # 根据项目类型判断
        if "web" in project_type:
            return TemplateType.WEB_APP
        elif "api" in project_type:
            return TemplateType.API
        elif "cli" in project_type:
            return TemplateType.CLI
        elif "library" in project_type:
            return TemplateType.LIBRARY
        elif "basic" in project_type:
            return TemplateType.BASIC

        return TemplateType.BASIC

    def validate_generation_request(
        self,
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[str]:
        """验证生成请求"""
        errors = []

        # 验证分析结果
        required_analysis_fields = ["content", "complexity"]
        for field in required_analysis_fields:
            if field not in analysis:
                errors.append(f"缺少必需的分析字段: {field}")

        if analysis.get("complexity", 0) < 0 or analysis.get("complexity", 0) > 1:
            errors.append("复杂度值必须在0-1之间")

        # 验证上下文
        if not context.get("project_name"):
            errors.append("缺少项目名称")

        # 验证配置限制
        if len(analysis.get("content", "")) > 50000:  # 50KB限制
            errors.append("内容长度超过限制")

        # 验证配置限制（这里简化为检查高复杂度是否超过文件限制）
        complexity = analysis.get("complexity", 0)
        estimated_files = int(10 * complexity)  # 简单估算：复杂度 * 基础文件数
        if estimated_files > self.config.max_files:
            errors.append(f"预估文件数量({estimated_files})超过限制({self.config.max_files})")

        return errors

    async def create_custom_template(
        self,
        analysis: Dict[str, Any],
        context: Dict[str, Any]
    ) -> TemplateConfig:
        """创建自定义模板"""
        project_name = context.get("project_name", "project")
        project_type = analysis.get("project_type", "basic")
        features = analysis.get("features", [])

        # 基础目录结构
        directory_structure = {
            "src": ["main.py"],
            "tests": [],
            "docs": ["README.md"]
        }

        # 基础文件模板
        file_templates = {
            "main.py": f"""
# {project_name}
# Generated on {datetime.now().strftime('%Y-%m-%d')}

def main():
    \"\"\"
    Main entry point for {project_name}
    \"\"\"
    print("Hello from {project_name}!")

if __name__ == "__main__":
    main()
""",
            "README.md": """
# {project_name}

{description}

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```

## Features

{#for feature in features#}
- {feature}
{#endfor#}
"""
        }

        # 根据项目类型添加特定文件
        if "web" in project_type:
            directory_structure["src"].extend(["app.py", "routes.py"])
            file_templates["app.py"] = """
from flask import Flask
from routes import bp

app = Flask(__name__)
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)
"""
            file_templates["routes.py"] = """
from flask import Blueprint, jsonify

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return jsonify({'message': 'Hello World!'})
"""
            file_templates["requirements.txt"] = "Flask>=2.0.0\n"

        if "api" in project_type:
            directory_structure["src"].append("api.py")
            file_templates["api.py"] = """
# API module for {project_name}
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {{"message": "Hello World"}}
"""

        # 根据特性添加文件
        if "database" in features:
            directory_structure["src"].append("database.py")
            file_templates["database.py"] = """
# Database module for {project_name}
import sqlite3

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def connect(self):
        return sqlite3.connect(self.db_path)
"""

        template_config = TemplateConfig(
            name=f"custom_{project_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=self.get_recommended_template_type(analysis),
            description=f"Custom template for {project_name}",
            directory_structure=directory_structure,
            file_templates=file_templates,
            variables={"project_name": project_name}
        )

        return template_config

    def _initialize_default_templates(self):
        """初始化默认模板"""
        # 基础模板
        basic_template = TemplateConfig(
            name="basic_python",
            type=TemplateType.BASIC,
            description="基础Python项目模板",
            directory_structure={
                "src": ["main.py"],
                "tests": [],
                "docs": ["README.md"]
            },
            file_templates={
                "main.py": """
# {project_name}
# Generated on {date}

def main():
    \"\"\"
    Main entry point for {project_name}
    \"\"\"
    print("Hello, World!")

if __name__ == "__main__":
    main()
""",
                "README.md": """
# {project_name}

{description}

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```
"""
            }
        )

        # Web应用模板
        web_template = TemplateConfig(
            name="web_flask",
            type=TemplateType.WEB_APP,
            description="Flask Web应用模板",
            directory_structure={
                "src": ["app.py", "routes.py", "templates/"],
                "static": ["css/style.css"],
                "tests": [],
                "docs": ["README.md"]
            },
            file_templates={
                "app.py": """
from flask import Flask
from routes import main_bp

app = Flask(__name__)
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run(debug=True)
""",
                "routes.py": """
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')
""",
                "style.css": """
/* {project_name} Styles */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
}
""",
                "requirements.txt": "Flask>=2.0.0\nJinja2>=3.0.0\n"
            }
        )

        # CLI应用模板
        cli_template = TemplateConfig(
            name="cli_tool",
            type=TemplateType.CLI,
            description="命令行工具模板",
            directory_structure={
                "src": ["main.py", "commands/"],
                "tests": [],
                "docs": ["README.md"]
            },
            file_templates={
                "main.py": """
#!/usr/bin/env python3
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='{project_name}')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    args = parser.parse_args()
    print("Hello from {project_name}!")

if __name__ == '__main__':
    main()
""",
                "README.md": """
# {project_name}

{description}

## Installation

```bash
pip install -e .
```

## Usage

```bash
{project_name} --help
```
"""
            }
        )

        self.template_engine.add_template(basic_template)
        self.template_engine.add_template(web_template)
        self.template_engine.add_template(cli_template)