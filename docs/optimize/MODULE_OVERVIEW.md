# 模块化系统概述 (Modular System Overview)

## 📦 模块划分

DAIP-LIVE 系统采用模块化单体架构，按功能职责划分为以下模块：

### P0: Core Interfaces & Types (核心接口与类型)
- **职责**: 定义跨模块共享的数据契约(Pydantic模型)和接口契约(抽象基类)
- **关键组件**:
  - 数据模型: TodoItem, Role, Session, Message 等
  - 事件模型: AgentEvent 及其子类型
  - 接口定义: IModelProvider, IKnowledgeManager, ITool 等
  - 异常体系: DAIPError 及其子类型
- **文档位置**: `docs/p0_core_interfaces/`

### P1: Data Persistence (数据持久化)
- **职责**: 数据库操作、文件I/O和序列化
- **关键组件**: 
  - 数据库管理器
  - 会话持久化
  - 配置文件管理
- **文档位置**: `docs/p1_data_persistence/`

### P2: Knowledge Manager (知识管理器)
- **职责**: 本地知识库管理、向量化和检索
- **关键组件**:
  - 知识摄取系统
  - 向量化服务
  - 语义搜索功能
- **文档位置**: `docs/p2_knowledge_manager/`

### 智能体记忆与学习系统 (Agent Memory & Learning System)
- **职责**: 智能体记忆管理、学习和经验积累
- **关键组件**:
  - 多层记忆架构（短期、长期、经验记忆）
  - 模式识别与学习机制
  - 记忆检索与应用系统
- **文档位置**: `docs/specs_agent_memory/`
  - 该系统与P5代理引擎紧密集成

### P3: Model Provider (模型提供者)
- **职责**: AI模型接口统一和模型调用管理
- **关键组件**:
  - 本地模型支持 (Ollama, LlamaCpp)
  - 云端模型支持 (OpenAI, Claude)
  - 统一模型调用接口
- **文档位置**: `docs/p3_model_provider/`

### P4: Role & Tool Management (角色与工具管理)
- **职责**: AI角色配置、管理和工具安全执行
- **关键组件**:
  - RoleManager: 角色加载与配置
  - ToolManager: 6阶段安全执行管道
  - 权限控制系统
- **文档位置**: `docs/p4_role_manager_tools/`

### P5: Agent Engine (代理引擎)
- **职责**: 任务执行、流程控制和意图处理
- **关键组件**:
  - AgentExecutor: 状态机驱动的代理执行器
  - 执行模式: 任务导向模式和对话模式
  - 状态监控API
- **文档位置**: `docs/p5_agent_engine/`

### P6: CLI/TUI Interface (命令行/终端界面)
- **职责**: 命令行界面和终端用户界面
- **关键组件**:
  - 命令解析与路由
  - 交互式界面(TUI)
  - 复制功能实现
- **文档位置**: `docs/p6_cli_tui/`

### P7: GUI Interface (图形界面)
- **职责**: 图形用户界面
- **关键组件**:
  - Web UI实现
  - 流式响应处理
- **文档位置**: `docs/p7_gui/`

### P8: Advanced Systems (高级功能系统)
- **职责**: 复杂业务逻辑实现
- **子模块**:
  - **P8.1 Debate System**: 结构化多角色辩论系统
  - **P8.2 Human Assistant**: 人类助手系统
  - **P8.3 Wiki System**: 维基协作系统
- **文档位置**: 
  - `docs/p8_debate_system/`
  - `docs/p8_human_assistant/`
  - `docs/p8_wiki_system/`

## 🔗 模块依赖关系

```
     ┌─────────────────┐
     │     P0 Core     │
     │  Interfaces     │
     └─────────┬───────┘
               │
     ┌─────────▼─────────┐
     │     P1 Data       │
     │  Persistence      │
     └─────────┬─────────┘
               │
     ┌─────────▼─────────┐
     │     P2 Knowledge  │
     │  Manager          │
     └─────────┬─────────┘
               │
     ┌─────────▼─────────┐
     │     P3 Model      │
     │  Provider         │
     └─────────┬─────────┘
               │
     ┌─────────▼─────────┐
     │     P4 Role &     │
     │  Tool Management  │
     └─────────┬─────────┘
               │
     ┌─────────▼─────────┐
     │     P5 Agent      │
     │  Engine           │
     └─────────┬─────────┘
               │
     ┌─────────▼─────────┐
     │     P6 CLI/TUI    │
     │  Interface        │
     └─────────┬─────────┘
               │
     ┌─────────▼─────────┐
     │     P8 Advanced   │
     │  Systems          │
     └───────────────────┘
```

## 🏗️ 统一开发规范

### 数据契约 (Data Contracts)
- 所有数据模型继承自 `pydantic.BaseModel`
- 通过 `I/O` 层进行数据验证
- 采用类型安全的设计

### 接口契约 (Interface Contracts)
- 使用 `abc.ABC` 定义抽象基类
- 确保接口实现的一致性
- 支持依赖注入和测试

### 异常体系 (Exception Hierarchy)
- 统一的异常基类 `DAIPError`
- 按组件分层的异常类型
- 可预测的错误处理

### 事件流 (Event Stream)
- 通过 `AgentEvent` 及其子类型实现异步事件流
- 支持UI/UX的实时响应
- 事件驱动的架构模式

## 🧩 扩展性设计

系统采用插件化设计，支持：
- 新模型提供者的集成
- 新工具的注册和执行
- 新角色的配置和管理
- 新业务功能模块的扩展