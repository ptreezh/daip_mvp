# 推荐的Ollama模型列表

## 已安装模型（当前可用）
- phi3:latest - Microsoft的Phi-3模型，性能出色但体积小（2.2GB）- **当前默认**
- llama3:latest - Meta的Llama 3模型（4.7GB）
- gemma2:latest - Google的Gemma 2模型（5.4GB）
- phi3:mini - Phi-3小型模型（2.2GB）
- llama3:instruct - Llama 3指令调优版本（4.7GB）

## 通用模型（适合大多数任务）
- llama3.1:latest - Llama 3.1最新版本，性能更好
- llama3.2:latest - Llama 3.2最新版本，性能更好
- mistral-nemo:latest - Mistral Nemo，性能和效率的平衡

## 轻量级模型（适合快速响应）
- phi3:latest - Microsoft的Phi-3模型，性能出色但体积小（推荐）
- gemma2:latest - Google的Gemma 2模型
- mistral:latest - Mistral模型
- neural-chat:latest - Intel神经网络聊天模型
- tinyllama:latest - 小型模型，适合快速测试

## 专业模型（适合特定任务）
- codellama:latest - 专门用于代码生成
- orca2:latest - Microsoft Orca 2模型，推理能力强
- wizardlm2:latest - 强大的对话模型

## 代码专用模型
- codegemma:latest - 专门用于代码任务的Gemma模型
- stargan:latest - 代码生成模型
- deepseek-coder:latest - 代码理解和生成模型

## 多语言模型
- nomic-embed-text - 用于文本嵌入
- mxbai-embed-large - 多语言嵌入模型
- nemotron:latest - 多语言模型

## 本地运行模型
- openchat:latest - 开源对话模型
- zephyr:latest - 合适的指令遵循模型
- neural-chat:latest - Intel神经网络聊天模型

### 推荐配置
- **默认选择**：phi3:latest (高效且性能好)
- **通用任务**：gemma2:latest 或 llama3.1:latest
- **代码任务**：codellama:latest 或 codegemma:latest
- **快速测试**：phi3:mini 或 tinyllama:latest

你可以使用 'ollama pull 模型名' 命令来下载这些模型