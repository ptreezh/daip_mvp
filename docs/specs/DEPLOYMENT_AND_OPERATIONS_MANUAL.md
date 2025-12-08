# 本地安装与运行指南

## 1. 概述

本文档描述了如何在您的个人电脑（Windows, macOS, Linux）上安装和运行DAIP-LIVE（单机版）。本系统作为一个标准的本地Python应用运行，无需复杂的服务器或容器环境。

## 2. 环境要求

### 2.1 硬件要求
- **内存 (RAM)**: 至少 8GB。如果运行本地大语言模型，建议 16GB 或更多。
- **存储**: 至少 5GB 可用磁盘空间，用于存放应用、依赖、模型和数据。
- **CPU**: 现代多核CPU即可。
- **GPU (可选但推荐)**: 如果要运行本地大语言模型，一块拥有至少 8GB VRAM 的NVIDIA GPU会提供最佳体验。

### 2.2 软件要求
- **Python**: 版本 **3.9** 至 **3.11**。可以通过官网 `python.org` 或 `pyenv` 等工具安装。
- **Git**: 用于从代码库下载项目。
- **(可选) Ollama**: 如果您希望使用本地大模型，推荐预先安装并运行Ollama (ollama.com)。

## 3. 安装步骤

### 3.1 第一步：下载项目代码

打开您的终端（Terminal, PowerShell, or Command Prompt），使用`git`克隆项目代码库到本地：

```bash
git clone https://github.com/ptreezh/daip_mvp.git
cd daip_mvp_project
```

### 3.2 第二步：安装项目依赖

本项目使用 [Poetry](https://python-poetry.org/) 管理依赖，这是推荐的安装方式。

1.  **安装Poetry** (如果尚未安装):
    ```bash
    pip install poetry
    ```

2.  **使用Poetry安装项目依赖**:
    在项目根目录下运行以下命令，Poetry会自动创建虚拟环境并安装所有必需的库。
    ```bash
    poetry install
    ```

**备选方案：使用pip**
如果您不想使用Poetry，也可以通过`requirements.txt`文件安装，但这可能无法保证依赖版本的完全一致。

```bash
# (建议) 首先创建一个虚拟环境
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`

# 安装依赖
pip install -r requirements.txt
```

### 3.3 第三步：配置应用程序

1.  **创建配置文件**: 
    项目根目录下有一个`config.yaml.example`文件。请复制它并重命名为`config.yaml`。

2.  **编辑配置文件 (`config.yaml`)**: 
    打开`config.yaml`文件，根据您的需求进行编辑。最重要的配置是**模型提供者**。

    **示例1：使用本地Ollama模型**
    ```yaml
    # config.yaml
    model_provider:
      # 使用ollama作为提供者
      default_provider: ollama
      
      providers:
        ollama:
          # 您在Ollama中运行的模型名称
          model_name: "llama3:8b"
          # Ollama服务的地址
          api_base: "http://localhost:11434/api"
    ```

    **示例2：使用云端OpenAI模型**
    ```yaml
    # config.yaml
    model_provider:
      # 切换为openai作为提供者
      default_provider: openai
      
      providers:
        openai:
          model_name: "gpt-4-turbo"
          # 建议通过环境变量设置API Key，而不是写在这里
          api_key: "sk-YourSecretKey..."
    ```
    **安全提示**: 强烈建议将API密钥（API Key）存储在环境变量中（例如`OPENAI_API_KEY`），而不是直接写在配置文件里。

## 4. 运行应用程序

确保您已经激活了Poetry的虚拟环境。

```bash
poetry shell
```

### 4.1 运行CLI (命令行界面)

您可以通过命令行与DAIP-LIVE进行交互。

```bash
# 查看所有可用命令
daip --help

# 与个人助理开始一个简单的聊天
daip pa chat "你好！"

# 启动一个关于“人工智能”的辩论
daip debate start "人工智能的未来"

# 查询知识库
daip knowledge search "关于Python异步编程的资料"
```
*(注：以上`daip`命令是基于`pyproject.toml`中脚本配置的示例，实际命令可能需要确认为`python -m src.cli.main`)*

### 4.2 运行Web UI (图形界面)

系统提供一个基于Streamlit的本地Web界面，用于更直观的操作。

```bash
streamlit run src/web_ui/app.py
```

运行后，终端会显示一个本地URL（通常是`http://localhost:8501`）。在您的浏览器中打开此地址即可访问图形界面。

## 5. 故障排除

- **问题：`command not found: poetry`**
  - **原因**: Poetry未正确安装或其路径未添加到系统的PATH环境变量中。
  - **解决**: 重新按照官方文档安装Poetry，并确保其安装路径在PATH中。

- **问题：依赖安装失败**
  - **原因**: 网络问题或某些库需要系统级的编译工具。
  - **解决**: 检查您的网络连接。对于编译失败，根据错误信息安装相应的构建工具（如在Ubuntu上安装`build-essential`，或在Windows上安装Visual Studio Build Tools）。

- **问题：连接本地LLM失败**
  - **原因**: 本地LLM服务（如Ollama）未启动，或`config.yaml`中的地址配置错误。
  - **解决**: 确保Ollama等服务正在运行，并检查配置文件中的`api_base`地址是否正确。
