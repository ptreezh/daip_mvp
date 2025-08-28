# DAIP-LIVE 项目上下文 (Qwen Code 使用说明)

## 项目概述

本项目是 **DAIP-LIVE (Dynamic AI Project - Live, Intelligent, Verifiable, Evolvable)** 的一个关键 MVP (Minimum Viable Product) 实现。其核心使命是通过模拟一个由多个AI专家角色组成的虚拟团队，利用社会化工程（如多角色审查、对抗性辩论、共识机制）来识别、挑战和抑制单一AI模型可能产生的幻觉，从而在复杂问题上生成更可靠、更全面、更高质量的解决方案。

主要应用场景包括：
*   虚拟多角色对话聊天
*   学术研究与决策支持
*   自动化敏捷项目执行

项目遵循 "CLI 优先，后端先行" 的开发哲学，所有核心功能都通过后端 API 暴露，并首先通过命令行界面 (CLI) 进行交互和测试。

## 技术栈

*   **语言**: Python 3.10+
*   **后端框架**: FastAPI
*   **Web 服务器**: Uvicorn
*   **AI/ML**: Langchain, LlamaIndex, Ollama (本地模型提供者)
*   **向量数据库**: ChromaDB
*   **配置管理**: Pydantic Settings
*   **CLI 工具**: Typer, Rich
*   **异步支持**: AsyncIO
*   **测试**: Pytest
*   **代码质量**: Black, Ruff (宽松规则), MyPy, Pylint
*   **包管理**: Poetry (首选), Pip (备选)

## 项目结构

项目结构复杂，包含多个核心目录和大量辅助文件。关键目录如下：

*   `src/`: 核心源代码。
    *   `src/main.py`: FastAPI 应用的主入口点。
    *   `src/cli/main.py`: 命令行界面 (CLI) 的主入口点。
    *   `src/config.py`: 使用 Pydantic 和 YAML 的统一配置系统。
    *   `src/api/`: FastAPI 路由和依赖注入。
    *   `src/protocols/`: 核心协议实现，如辩论协议。
*   `configs/`: 配置文件，如角色定义 (`roles.yaml`)。
*   `data/`: 数据存储，如 ChromaDB 向量数据库和用户配置文件。
*   `tests/`: 测试套件。
*   `docs/`: 项目文档。
*   `ui/`: 前端界面代码。
*   `scripts/`: 各类辅助脚本。
*   `roles/`: AI 角色的定义文件。

## 配置

项目配置主要通过 `config.yaml` 文件进行管理，该文件由 `src/config.py` 中定义的 Pydantic 模型加载和验证。

默认配置项包括：
*   LLM 提供者: Ollama (`llama3:instruct`, `nomic-embed-text:latest`)
*   向量数据库路径: `data/chroma_db`
*   日志级别: `INFO`
*   角色配置文件路径: `configs/roles.yaml`

## 构建、运行与测试

### 安装

1.  **使用 Poetry 安装依赖**: `poetry install`
2.  **或者使用 Pip**: `pip install -e .` (依赖项在 `requirements.txt` 和 `pyproject.toml` 中定义)
3.  **安装 Ollama**: 访问 [Ollama 官网](https://ollama.ai/) 并拉取所需模型 (`llama3:instruct`, `nomic-embed-text:latest`)。

### 运行 CLI

安装完成后，可以使用 `daip-cli` 命令与系统交互：
*   `daip-cli status`: 检查系统状态。
*   `daip-cli roles`: 查看可用角色。
*   `daip-cli start "话题"`: 启动一个辩论。
*   `daip-cli help`: 获取帮助。

### 启动 API 服务

使用 Uvicorn 启动 FastAPI 后端服务：
`uvicorn src.main:app --reload`

服务启动后，可通过 `http://127.0.0.1:8000` 访问 API，文档在 `http://127.0.0.1:8000/docs`。

### 测试

项目使用 Pytest 进行测试：
`pytest`

## 开发约定

*   **编码规范**: 遵循 `docs/CODING_STANDARDS.md` 中定义的规范。
*   **代码格式化**: 使用 Black。
*   **Linting**: 使用 Ruff，规则已放宽，主要用于检测代码间调用关系。
*   **类型检查**: 使用 MyPy。
*   **代码风格**: 遵循 PEP 8 和 Google Python Style Guide (部分)。
*   **CLI 优先**: 新功能优先通过后端 API 和 CLI 实现。
*   **测试驱动开发 (TDD)**: 所有新开发必须遵循 TDD 驱动的开发模式。
*   **Kiro SPECS 流程**: 所有新开发必须遵循 Kiro 的 SPECS 流程，确保需求、设计、实现和测试的完整性和一致性。