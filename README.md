# DAIP-LIVE: 协同扩展模块与幻觉抑制 MVP

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: Pylint](https://img.shields.io/badge/linter-pylint-yellowgreen.svg)](https://github.com/pycqa/pylint)
[![Types: Mypy](https://img.shields.io/badge/types-mypy-blue.svg)](http://mypy-lang.org/)

本项目是 DAIP-LIVE (Dynamic AI Project - Live, Intelligent, Verifiable, Evolvable) 的一个关键 MVP (Minimum Viable Product) 实现。

## 核心使命与价值

**本项目聚焦于“MVP：基于本地小模型的社会化工程幻觉抑制”。**

我们的核心价值在于，通过模拟一个由多个AI专家角色组成的虚拟团队，利用社会化工程（如多角色审查、对抗性辩论、共识机制）来识别、挑战和抑制单一AI模型可能产生的幻觉，从而在复杂问题上生成更可靠、更全面、更高质量的解决方案。

## 核心应用场景

*   **虚拟多角色对话聊天**: 用户可以与一个由多个AI角色组成的虚拟团队进行对话，每个角色都有独特的专长和视角。
*   **学术研究与决策支持**: 针对复杂或有争议的话题，发起一场多角色AI辩论，观察AI角色如何相互质疑、补充和达成共识，并最终获得由“系统综合师”生成的结构化综合意见。
*   **自动化敏捷项目执行**: 利用引导式任务分解和版本化的知识库，实现敏捷项目的自动化管理和执行。

## MVP 开发哲学：CLI 优先，后端先行

在当前MVP阶段，我们严格遵循“CLI优先，后端先行”的开发哲学。这意味着：

1.  **所有核心功能都将首先通过后端API暴露**，并确保其工程可用性。
2.  **命令行界面 (CLI) 是与系统交互和测试的主要方式**。
3.  前端界面 (`ui/`) 的开发将在后端功能稳定且经过充分验证后才开始。

## 快速开始

### 安装

1.  **克隆项目**:
    ```bash
    git clone [repository-url]
    cd daip_mvp_project
    ```

2.  **使用 Poetry 安装依赖**:
    ```bash
    # 安装 Poetry（如果尚未安装）
    pip install poetry

    # 安装项目依赖
    poetry install
    ```

    或者使用 pip 安装:
    ```bash
    pip install -e .
    ```

3.  **配置系统**:
    * 项目默认使用 `config.yaml` 文件进行配置
    * 如果文件不存在，系统会使用默认配置
    * 创建或修改 `config.yaml` 文件以自定义配置:
    
    ```yaml
    llm:
      provider: "ollama"
      ollama:
        generation_model: "llama3:instruct"
        embedding_model: "nomic-embed-text:latest"
        host: "http://localhost:11434"
        timeout: 30

    vector_store:
      chroma_db_path: "data/chroma_db"
      role_collection_name: "roles"

    logging:
      level: "INFO"
      format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    roles_config_path: "configs/roles.yaml"
    log_level: "INFO"
    allowed_origins: ["*"]
    ```

### 使用命令行界面 (CLI)

安装后，您可以使用 `daip-cli` 命令与系统交互:

1.  **检查系统状态**:
    ```bash
    daip-cli status
    ```

2.  **查看可用角色**:
    ```bash
    daip-cli roles
    ```

3.  **启动辩论**:
    ```bash
    # 基本用法
    daip-cli start "人工智能的伦理问题"
    
    # 指定角色
    daip-cli start "气候变化解决方案" --role "环境科学家" --role "经济学家"
    
    # 高级选项
    daip-cli start "未来工作趋势" --role "未来学家" --role "劳工专家" --rounds 5 --verbose --save --output "debate_results.txt"
    ```

4.  **获取帮助**:
    ```bash
    daip-cli help
    ```

### 启动 API 服务

1.  **启动 FastAPI 后端服务**:
    ```bash
    uvicorn src.main:app --reload
    ```

2.  **通过 API 进行测试**:
    * 服务启动后，您可以使用 `curl` 或 Python `requests` 库调用 API
    * API 文档可在 http://127.0.0.1:8000/docs 访问
    
    **示例：检查服务状态**
    ```bash
    curl http://127.0.0.1:8000/health
    ```
    
    **示例：获取详细系统状态**
    ```bash
    curl http://127.0.0.1:8000/status
    ```
    
    **示例：获取可用角色**
    ```bash
    curl http://127.0.0.1:8000/roles
    ```
    
    **示例：启动辩论**
    ```bash
    curl -X POST http://127.0.0.1:8000/protocols/debate/start \
    -H "Content-Type: application/json" \
    -d '{"topic": "人工智能的未来", "roles": ["技术专家", "伦理学家"], "rounds": 3}'
    ```

## 常见问题与故障排除

### 安装问题

1. **依赖安装失败**
   * 确保您使用的是 Python 3.10 或更高版本
   * 尝试更新 pip: `pip install --upgrade pip`
   * 如果使用 Poetry，尝试: `poetry update`

2. **CLI 命令未找到**
   * 确保项目已正确安装: `pip install -e .`
   * 检查 PATH 环境变量是否包含 Python 脚本目录

### 运行时问题

1. **LLM 连接错误**
   * 确保 Ollama 服务已启动并运行在默认端口 (11434)
   * 验证 config.yaml 中的 LLM 配置是否正确
   * 检查网络连接和防火墙设置

2. **内存不足**
   * 减少辩论轮次 (`--rounds 2`)
   * 使用更少的角色
   * 关闭其他内存密集型应用程序

3. **API 服务无法启动**
   * 检查端口是否被占用
   * 验证配置文件格式是否正确
   * 查看日志获取详细错误信息

4. **角色加载失败**
   * 运行 `daip-cli status` 检查系统状态
   * 确保角色配置文件存在且格式正确

## 项目规范

本项目严格遵守在 `docs/CODING_STANDARDS.md` 中定义的编码规范、文件头规范和最佳实践。所有贡献者必须严格遵守这些规范。

## 架构概览

详细的系统架构请参见 `docs/CORE_MISSION_AND_ARCHITECTURE.md`。
