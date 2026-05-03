# 核心功能详解 (Core Functions Detailed)

## 🤖 多模型AI协作

### 功能描述
支持OpenAI、Claude、本地Ollama等多种AI模型，实现智能角色扮演和协作辩论。

### 详细说明
- **模型管理**: 通过 `daip model` 命令管理不同AI模型
- **角色分配**: 支持为不同角色分配不同AI模型
- **协作机制**: 多AI角色可以协同完成复杂任务

### 代码位置
- `src/daip_live/model_provider/provider.py` - 模型提供者接口
- `src/daip_live/p4_role_manager_tools/role_manager.py` - 角色管理器
- `src/daip_live/p3_model_provider/litellm_provider.py` - LiteLLM提供者

---

## 📝 Wiki协作系统

### 功能描述
多角色共同创建和编辑知识库，支持向量搜索和智能分类。

### 详细说明
- **知识存储**: 本地向量数据库存储
- **多用户协作**: 支持多AI角色同时编辑
- **版本控制**: 完整的修订历史追踪

### 代码位置
- `src/daip_live/p8_wiki_system/manager.py` - Wiki管理器
- `src/daip_live/p8_wiki_system/models.py` - Wiki数据模型
- `src/daip_live/p8_wiki_system/knowledge_integration.py` - 知识集成

---

## 🖥️ 现代化TUI界面

### 功能描述
直观的命令行界面，支持真实的复制功能和响应式设计。

### 详细说明
- **复制功能**:
  - `/copy` - 复制所有对话内容
  - `/copy_recent N` - 复制最近N行对话
  - 快捷键支持
- **界面布局**: 分为对话区域和系统状态区域

### 代码位置
- `src/daip_live/tui_modular.py` - 主TUI实现
- `src/daip_live/p6_cli_tui/tui_commands.py` - TUI命令处理

---

## 🏗️ 模块化架构

### 功能描述
P1-P8模块化设计，高内聚低耦合，易于扩展和维护。

### 详细说明
- **P0**: 核心接口
- **P1**: 数据持久化
- **P2**: 知识管理器
- **P3**: 模型提供者
- **P4**: 角色管理工具
- **P5**: Agent引擎
- **P6**: CLI/TUI界面
- **P7**: GUI界面
- **P8**: 辩论系统/人类助手/Wiki系统

### 代码位置
- `src/daip_live/p*/` - 各模块实现
- `src/daip_live/container.py` - 依赖注入容器

---

## 🎯 智能意图识别

### 功能描述
先进意图识别和上下文理解，支持多轮对话和会话管理。

### 详细说明
- **意图分类**:
  - 辩论开始 (`start_debate`)
  - 论文搜索 (`search_papers`)
  - 论文下载 (`download_paper`)
  - 一般对话 (`chat`)
- **上下文感知**: 根据对话历史提供相关功能

### 代码位置
- `src/daip_live/agent_engine/enhanced_intent_recognizer.py` - 增强意图识别器
- `src/daip_live/intent_recognition/contextual_intent_recognizer.py` - 情境意图识别器

---

## 🎭 多模型辩论系统

### 功能描述
不同AI角色扮演不同观点，进行深度分析和多角度讨论。

### 详细说明
- **角色管理**: 支持自定义辩论角色
- **辩论流程**: 结构化的多轮辩论
- **历史追踪**: 完整的辩论过程记录

### 代码位置
- `src/daip_live/p8_debate_system/enhanced_debate_manager.py` - 增强辩论管理器
- `src/daip_live/debate_module/simple_debate.py` - 简化辩论引擎

## 🔧 配置与扩展

### 功能描述
灵活的配置系统和插件机制。

### 详细说明
- **配置管理**: YAML配置文件支持
- **插件系统**: 可扩展的工具和功能模块

### 代码位置
- `src/daip_live/config.py` - 配置管理
- `src/daip_live/config_bridge.py` - 配置桥接