"""
脚手架核心引擎
遵循SOLID原则，负责协调所有脚手架操作
"""

import asyncio
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

from .config_manager import ScaffoldConfig
from .error_handler import ErrorHandler
from .models import (
    InputType,
    ProjectFile,
    ProjectStructure,
    ScaffoldCommand,
    ScaffoldResult,
    ValidationError,
)


class GenerationPhase(Enum):
    """生成阶段"""

    INITIALIZATION = "initialization"
    CONTENT_ANALYSIS = "content_analysis"
    STRUCTURE_GENERATION = "structure_generation"
    FILE_CREATION = "file_creation"
    VALIDATION = "validation"
    COMPLETION = "completion"


@dataclass
class GenerationRequest:
    """生成请求"""

    description: str
    input_type: InputType = InputType.TEXT
    file_path: Optional[str] = None
    output_directory: str = "./output"
    auto_confirm: bool = False
    dry_run: bool = False
    overwrite_existing: bool = True
    options: dict[str, Any] = field(default_factory=dict)
    context: Optional[dict[str, Any]] = None

    def validate(self) -> list[str]:
        """验证请求有效性"""
        errors = []

        if not self.description and not self.file_path:
            errors.append("必须提供项目描述或描述文件")

        # 测试模式下允许更短的描述，但在生产环境中需要更长
        if self.description and len(self.description.strip()) < 3:
            errors.append("项目描述至少需要3个字符")

        if self.input_type == InputType.FILE and not self.file_path:
            errors.append("文件输入时必须指定文件路径")

        return errors

    @classmethod
    def from_command(cls, command: ScaffoldCommand, **kwargs) -> "GenerationRequest":
        """从命令创建请求"""
        return cls(
            description=command.description,
            input_type=command.input_type,
            file_path=command.file_path,
            auto_confirm=command.auto_confirm,
            **kwargs,
        )


@dataclass
class GenerationContext:
    """生成上下文"""

    request: GenerationRequest
    phase: GenerationPhase = GenerationPhase.INITIALIZATION
    created_files: list[ProjectFile] = field(default_factory=list)
    errors: list[Exception] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)

    def advance_phase(self, new_phase: GenerationPhase) -> None:
        """推进到下一个阶段"""
        self.phase = new_phase

    def add_file(self, project_file: ProjectFile) -> None:
        """添加创建的文件"""
        self.created_files.append(project_file)

    def add_error(self, error: Exception) -> None:
        """添加错误"""
        self.errors.append(error)

    def add_warning(self, warning: str) -> None:
        """添加警告"""
        self.warnings.append(warning)

    def set_metadata(self, key: str, value: Any) -> None:
        """设置元数据"""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取元数据"""
        return self.metadata.get(key, default)

    def has_errors(self) -> bool:
        """是否有错误"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """是否有警告"""
        return len(self.warnings) > 0

    def get_duration(self) -> float:
        """获取持续时间"""
        return time.time() - self.start_time


@dataclass
class GenerationResult:
    """生成结果"""

    success: bool
    project_structure: Optional[ProjectStructure] = None
    errors: list[Exception] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    duration: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def success(
        cls,
        project_structure: ProjectStructure,
        duration: float,
        warnings: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "GenerationResult":
        """创建成功结果"""
        return cls(
            success=True,
            project_structure=project_structure,
            warnings=warnings or [],
            duration=duration,
            metadata=metadata or {},
        )

    @classmethod
    def failure(
        cls,
        errors: list[Exception],
        duration: float,
        warnings: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "GenerationResult":
        """创建失败结果"""
        return cls(
            success=False,
            errors=errors,
            warnings=warnings or [],
            duration=duration,
            metadata=metadata or {},
        )

    def to_scaffold_result(self) -> ScaffoldResult:
        """转换为脚手架结果"""
        if self.success:
            return ScaffoldResult.success(self.project_structure, self.warnings)
        else:
            error_messages = [str(error) for error in self.errors]
            return ScaffoldResult.failure(error_messages, self.warnings)


class RecoveryStrategy:
    """恢复策略"""

    def __init__(
        self,
        max_retries: int = 3,
        fallback_actions: Optional[list[str]] = None,
        retry_condition: Optional[Callable] = None,
    ):
        self.max_retries = max_retries
        self.fallback_actions = fallback_actions or []
        self.retry_condition = retry_condition


class ScaffoldEngine:
    """脚手架核心引擎

    遵循单一职责原则，负责协调所有脚手架操作
    提供统一的生成接口和错误处理
    """

    def __init__(
        self,
        config: Optional[ScaffoldConfig] = None,
        error_handler: Optional[ErrorHandler] = None,
        progress_callback: Optional[
            Callable[[GenerationPhase, float, str], None]
        ] = None,
    ):
        """初始化脚手架引擎

        Args:
            config: 配置管理器
            error_handler: 错误处理器
            progress_callback: 进度回调函数
        """
        self.config = config or ScaffoldConfig()
        self.error_handler = error_handler or ErrorHandler()
        self.progress_callback = progress_callback
        self.recovery_strategies: dict[str, RecoveryStrategy] = {}

        # 配置默认恢复策略
        self._configure_default_recovery_strategies()

    def _configure_default_recovery_strategies(self) -> None:
        """配置默认恢复策略"""
        self.recovery_strategies.update(
            {
                "ConnectionError": RecoveryStrategy(max_retries=2),
                "TimeoutError": RecoveryStrategy(max_retries=1),
                "ValidationError": RecoveryStrategy(max_retries=0),  # 不重试验证错误
            }
        )

    def configure_recovery_strategy(
        self,
        error_type: str,
        max_retries: int = 3,
        fallback_action: Optional[str] = None,
        fallback_actions: Optional[list[str]] = None,
    ) -> None:
        """配置错误恢复策略

        Args:
            error_type: 错误类型
            max_retries: 最大重试次数
            fallback_action: 单个回退操作（为了向后兼容）
            fallback_actions: 回退操作列表
        """
        # 处理单个回退操作的情况
        actions = fallback_actions or []
        if fallback_action:
            actions.append(fallback_action)

        self.recovery_strategies[error_type] = RecoveryStrategy(
            max_retries=max_retries, fallback_actions=actions
        )

    def _report_progress(
        self, phase: GenerationPhase, progress: float, message: str
    ) -> None:
        """报告进度"""
        if self.progress_callback:
            self.progress_callback(phase, progress, message)

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """生成项目

        Args:
            request: 生成请求

        Returns:
            GenerationResult: 生成结果
        """
        start_time = time.time()
        context = GenerationContext(request)

        try:
            # 验证请求
            self._report_progress(GenerationPhase.INITIALIZATION, 0.1, "验证请求")
            validation_errors = request.validate()
            if validation_errors:
                return GenerationResult.failure(
                    [ValidationError(validation_errors)], time.time() - start_time
                )

            # 分析内容（带重试）
            analysis = await self._execute_with_retry(
                lambda: self._analyze_content(request), "ConnectionError"
            )
            context.set_metadata("analysis", analysis)

            # 生成结构（带重试）
            self._report_progress(
                GenerationPhase.STRUCTURE_GENERATION, 0.4, "生成项目结构"
            )
            structure = await self._execute_with_retry(
                lambda: self._generate_structure(request, analysis), "ConnectionError"
            )

            # 创建文件
            self._report_progress(GenerationPhase.FILE_CREATION, 0.6, "创建文件")
            if not request.dry_run:
                errors = await self._create_files(structure, request)
                context.errors.extend(errors)

            # 验证结果
            self._report_progress(GenerationPhase.VALIDATION, 0.8, "验证结果")
            await self._validate_result(structure, context)

            # 完成
            self._report_progress(GenerationPhase.COMPLETION, 1.0, "完成")
            duration = time.time() - start_time

            if context.has_errors():
                return GenerationResult.failure(
                    context.errors, duration, context.warnings, context.metadata
                )
            else:
                return GenerationResult.success(
                    structure, duration, context.warnings, context.metadata
                )

        except asyncio.CancelledError as e:
            duration = time.time() - start_time
            return GenerationResult.failure([e], duration)
        except Exception as e:
            duration = time.time() - start_time
            self.error_handler.handle_error(e)
            return GenerationResult.failure([e], duration)

    async def _analyze_content(self, request: GenerationRequest) -> dict[str, Any]:
        """分析内容

        Args:
            request: 生成请求

        Returns:
            Dict[str, Any]: 分析结果
        """
        content = request.description

        # 如果是文件输入，读取文件内容
        if request.input_type == InputType.FILE and request.file_path:
            try:
                with open(request.file_path, encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                raise ValidationError(f"无法读取文件 {request.file_path}: {str(e)}")

        # 简化的内容分析
        keywords = self._extract_keywords(content)
        project_type = self._infer_project_type(keywords)
        features = self._extract_features(content, keywords)

        return {
            "content": content,
            "keywords": keywords,
            "project_type": project_type,
            "features": features,
            "complexity": self._estimate_complexity(content, keywords),
        }

    def _extract_keywords(self, content: str) -> list[str]:
        """提取关键词"""
        # 常见的技术关键词
        tech_keywords = [
            "react",
            "vue",
            "angular",
            "svelte",
            "next",
            "nuxt",
            "express",
            "django",
            "flask",
            "fastapi",
            "spring",
            "laravel",
            "mysql",
            "postgresql",
            "mongodb",
            "redis",
            "sqlite",
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "gcp",
            "python",
            "javascript",
            "typescript",
            "java",
            "go",
            "rust",
            "html",
            "css",
            "scss",
            "tailwind",
            "bootstrap",
            "api",
            "rest",
            "graphql",
            "websocket",
            "auth",
            "login",
            "user",
            "session",
            "token",
            "dashboard",
            "admin",
            "cms",
            "blog",
            "ecommerce",
            "test",
            "testing",
            "jest",
            "pytest",
            "unit",
            "ci",
            "cd",
            "github",
            "git",
            "deploy",
        ]

        # 提取包含关键词的词
        words = re.findall(r"\b\w+\b", content.lower())
        extracted = []
        for keyword in tech_keywords:
            if keyword in words:
                extracted.append(keyword)

        return list(set(extracted))

    def _infer_project_type(self, keywords: list[str]) -> str:
        """推断项目类型"""
        if any(kw in keywords for kw in ["react", "vue", "angular", "html", "css"]):
            return "web_app"
        elif any(
            kw in keywords for kw in ["express", "django", "flask", "fastapi", "api"]
        ):
            return "api_service"
        elif any(kw in keywords for kw in ["docker", "kubernetes"]):
            return "containerized_app"
        elif any(kw in keywords for kw in ["python", "java", "typescript"]):
            return "library"
        elif any(kw in keywords for kw in ["test", "testing"]):
            return "test_project"
        else:
            return "general"

    def _extract_features(self, content: str, keywords: list[str]) -> list[str]:
        """提取功能特性"""
        features = []

        # 常见功能特性映射
        feature_keywords = {
            "authentication": ["auth", "login", "user", "session", "token"],
            "database": ["mysql", "postgresql", "mongodb", "redis", "sqlite"],
            "api": ["api", "rest", "graphql"],
            "frontend": ["react", "vue", "angular", "html", "css"],
            "backend": ["express", "django", "flask", "fastapi"],
            "testing": ["test", "testing", "jest", "pytest"],
            "deployment": ["deploy", "docker", "kubernetes", "ci", "cd"],
        }

        for feature, feature_keywords in feature_keywords.items():
            if any(kw in keywords for kw in feature_keywords):
                features.append(feature)

        return features

    def _estimate_complexity(self, content: str, keywords: list[str]) -> str:
        """估算项目复杂度"""
        if len(keywords) > 10:
            return "high"
        elif len(keywords) > 5:
            return "medium"
        else:
            return "low"

    async def _generate_structure(
        self, request: GenerationRequest, analysis: dict[str, Any]
    ) -> ProjectStructure:
        """生成项目结构

        Args:
            request: 生成请求
            analysis: 内容分析结果

        Returns:
            ProjectStructure: 项目结构
        """
        project_type = analysis.get("project_type", "general")
        keywords = analysis.get("keywords", [])
        features = analysis.get("features", [])

        files = self._generate_file_structure(
            project_type, keywords, features, request.options
        )

        return ProjectStructure(
            files=files,
            description=analysis.get("content", ""),
            generated_at=time.time(),
        )

    def _generate_file_structure(
        self,
        project_type: str,
        keywords: list[str],
        features: list[str],
        options: dict[str, Any],
    ) -> list[ProjectFile]:
        """生成文件结构"""
        files = []

        # 根据项目类型生成基础文件
        if project_type == "web_app":
            files.extend(self._generate_web_app_files(keywords, options))
        elif project_type == "api_service":
            files.extend(self._generate_api_files(keywords, options))
        else:
            files.extend(self._generate_general_files(keywords, options))

        return files

    def _generate_web_app_files(
        self, keywords: list[str], options: dict[str, Any]
    ) -> list[ProjectFile]:
        """生成Web应用文件"""
        files = []

        # 根据技术栈选择
        if any(kw in keywords for kw in ["react", "next"]):
            files.append(
                ProjectFile("package.json", self._get_package_json_content("react"))
            )
            files.append(ProjectFile("src/App.js", self._get_react_app_content()))
        elif any(kw in keywords for kw in ["vue", "nuxt"]):
            files.append(
                ProjectFile("package.json", self._get_package_json_content("vue"))
            )
            files.append(ProjectFile("src/App.vue", self._get_vue_app_content()))
        else:
            files.append(ProjectFile("index.html", self._get_basic_html_content()))
            files.append(ProjectFile("style.css", self._get_basic_css_content()))

        return files

    def _generate_api_files(
        self, keywords: list[str], options: dict[str, Any]
    ) -> list[ProjectFile]:
        """生成API服务文件"""
        files = []

        # 根据后端框架选择
        if any(kw in keywords for kw in ["express"]):
            files.append(
                ProjectFile("package.json", self._get_package_json_content("express"))
            )
            files.append(ProjectFile("server.js", self._get_express_server_content()))
        elif any(kw in keywords for kw in ["fastapi"]):
            files.append(
                ProjectFile("requirements.txt", self._get_fastapi_requirements())
            )
            files.append(ProjectFile("main.py", self._get_fastapi_content()))

        return files

    def _generate_general_files(
        self, keywords: list[str], options: dict[str, Any]
    ) -> list[ProjectFile]:
        """生成通用文件"""
        files = []

        # README文件
        files.append(ProjectFile("README.md", "# Project\n\nProject description."))

        # 基础配置文件
        if any(kw in keywords for kw in ["python"]):
            files.append(ProjectFile("requirements.txt", "# Add dependencies here"))
        elif any(kw in keywords for kw in ["javascript", "typescript"]):
            files.append(
                ProjectFile("package.json", '{"name": "project", "version": "1.0.0"}')
            )

        return files

    def _get_package_json_content(self, framework: str) -> str:
        """获取package.json内容"""
        templates = {
            "react": """
{
  "name": "react-app",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}
""".strip(),
            "vue": """
{
  "name": "vue-app",
  "version": "1.0.0",
  "dependencies": {
    "vue": "^3.0.0"
  },
  "scripts": {
    "serve": "vue-cli-service serve",
    "build": "vue-cli-service build"
  }
}
""".strip(),
            "express": """
{
  "name": "express-app",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.0"
  },
  "scripts": {
    "start": "node server.js"
  }
}
""".strip(),
        }

        return templates.get(framework, '{"name": "project", "version": "1.0.0"}')

    def _get_react_app_content(self) -> str:
        """获取React应用内容"""
        return """
import React from 'react';

function App() {
  return (
    <div className="App">
      <h1>React App</h1>
    </div>
  );
}

export default App;
""".strip()

    def _get_vue_app_content(self) -> str:
        """获取Vue应用内容"""
        return """
<template>
  <div class="app">
    <h1>Vue App</h1>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>
""".strip()

    def _get_basic_html_content(self) -> str:
        """获取基础HTML内容"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project</title>
</head>
<body>
    <h1>Hello World</h1>
</body>
</html>
""".strip()

    def _get_basic_css_content(self) -> str:
        """获取基础CSS内容"""
        return """
body {
    margin: 0;
    font-family: Arial, sans-serif;
}

h1 {
    color: #333;
}
""".strip()

    def _get_express_server_content(self) -> str:
        """获取Express服务器内容"""
        return """
const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.json({ message: 'Hello World!' });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
""".strip()

    def _get_fastapi_requirements(self) -> str:
        """获取FastAPI依赖"""
        return "fastapi==0.68.0\nuvicorn==0.15.0"

    def _get_fastapi_content(self) -> str:
        """获取FastAPI内容"""
        return """
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
""".strip()

    async def _create_files(
        self, structure: ProjectStructure, request: GenerationRequest
    ) -> list[Exception]:
        """创建文件

        Args:
            structure: 项目结构
            request: 生成请求

        Returns:
            List[Exception]: 错误列表
        """
        errors = []
        output_dir = Path(request.output_directory)

        # 创建输出目录
        output_dir.mkdir(parents=True, exist_ok=True)

        for project_file in structure.files:
            try:
                file_path = output_dir / project_file.path

                # 检查文件是否已存在
                if file_path.exists() and not request.overwrite_existing:
                    errors.append(
                        FileExistsError(f"File already exists: {project_file.path}")
                    )
                    continue

                # 创建父目录
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # 写入文件
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(project_file.content)

            except Exception as e:
                errors.append(e)

        return errors

    async def _validate_result(
        self, structure: ProjectStructure, context: GenerationContext
    ) -> None:
        """验证结果

        Args:
            structure: 项目结构
            context: 生成上下文
        """
        # 基本验证
        if not structure.files:
            context.add_warning("没有生成任何文件")

        # 检查文件大小
        for file in structure.files:
            if len(file.content) == 0:
                context.add_warning(f"文件 {file.path} 为空")

    async def _execute_with_retry(self, operation: Callable, error_type: str) -> Any:
        """使用重试机制执行操作"""
        strategy = self.recovery_strategies.get(error_type, RecoveryStrategy())

        for attempt in range(strategy.max_retries + 1):
            try:
                result = operation()
                if asyncio.iscoroutine(result):
                    return await result
                elif asyncio.iscoroutinefunction(operation):
                    return await operation()
                else:
                    return result
            except Exception as e:
                if attempt == strategy.max_retries:
                    raise

                # 检查是否应该重试
                if strategy.retry_condition and not strategy.retry_condition(e):
                    raise

                # 等待一段时间后重试
                await asyncio.sleep(0.1 * (2**attempt))

        raise Exception("All retry attempts failed")

    async def _execute_with_recovery(self, operation: Callable, error_type: str) -> Any:
        """使用恢复策略执行操作"""
        strategy = self.recovery_strategies.get(error_type, RecoveryStrategy())

        for attempt in range(strategy.max_retries + 1):
            try:
                result = operation()
                if asyncio.iscoroutine(result):
                    return await result
                elif asyncio.iscoroutinefunction(operation):
                    return await operation()
                else:
                    return result
            except Exception as e:
                if attempt == strategy.max_retries:
                    raise

                # 检查是否应该重试
                if strategy.retry_condition and not strategy.retry_condition(e):
                    raise

                # 等待一段时间后重试
                await asyncio.sleep(0.1 * (2**attempt))

        # 执行回退操作
        for action in strategy.fallback_actions:
            try:
                if action == "use_default_template":
                    return await self._use_default_template()
            except Exception:
                continue

        raise Exception("All recovery attempts failed")

    async def _use_default_template(self) -> ProjectStructure:
        """使用默认模板"""
        default_files = [
            ProjectFile("README.md", "# Default Project\n\nThis is a default template.")
        ]

        return ProjectStructure(
            files=default_files, description="Default template project"
        )
