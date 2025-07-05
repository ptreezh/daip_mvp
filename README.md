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

## 快速开始 (后端服务)

> **注意**: 详细的安装和配置步骤将在后续开发中完善。

1.  **克隆项目**:
    ```bash
    git clone [repository-url]
    cd daip_mvp_project
    ```

2.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **配置环境**:
    *   复制 `.env.example` 为 `.env`。
    *   在 `.env` 文件中配置必要的API密钥和模型路径。

4.  **启动后端服务**:
    ```bash
    python scripts/start_backend.py
    ```

5.  **通过 CLI/API 进行测试**:
    *   服务启动后，您可以使用 `curl` 或简单的 Python `requests` 脚本来调用API。
    *   **示例：获取系统状态**
        ```bash
        curl http://127.0.0.1:8000/sessions/some_session_id/status
        ```
    *   **示例：发起聊天**
        ```bash
        curl -X POST http://127.0.0.1:8000/sessions/some_session_id/chat \
        -H "Content-Type: application/json" \
        -d '{"message": "你好"}'
        ```

## 项目规范

本项目严格遵守在 `docs/CODING_STANDARDS.md` 中定义的编码规范、文件头规范和最佳实践。所有贡献者必须严格遵守这些规范。

## 架构概览

详细的系统架构请参见 `docs/CORE_MISSION_AND_ARCHITECTURE.md`。
