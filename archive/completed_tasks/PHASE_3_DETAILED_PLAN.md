# 阶段 3: 聊天室与基础知识管理 (Wiki) - 详细计划 (更新版 - 基于KISS/YAGNI/SOLID/TDD原则)

基于更新后的需求、设计文档和全局API字典，进一步细化任务清单并制定实施计划，严格遵循 KISS, YAGNI, SOLID, TDD 原则。

## 研究 (Research)

### 1. 现有服务分析
- **ChatRoomManager (`src/virtual_role_chat/chat_room_manager.py`)**:
  - 已完整实现聊天室的创建、配置、更新、删除、归档、激活等生命周期管理功能。
  - 支持通过 `ChatRoomConfig` 配置聊天室，包括名称、主题、模式、角色列表、交互规则等。
  - 包含角色验证和配置验证逻辑。
  - 支持持久化存储（可选）。
  - 可以扩展以支持更复杂的聊天室规则配置。

- **ChatService (`src/core_services/chat_service.py`)**:
  - **严重警告**: 全局API字典指出，此服务严重依赖一个名为 `MultiRoleChatEngine` 的核心类，但该类在代码库中完全缺失。
  - 当前实现仅包含一个 `handle_simple_multi_role_chat` 的模拟方法，其他方法都是桩实现。
  - 无法直接用于实现 `chat message` 和 `chat history` 命令。

- **WikiService (`src/core_services/wiki_service.py`)**:
  - 已完整实现Wiki条目的创建、版本管理、检索、编辑提议和语义搜索功能。
  - 依赖文件系统和ChromaDB进行持久化存储。
  - 依赖Ollama提供嵌入模型支持语义搜索。

- **ChatSessionService (`src/virtual_role_chat/chat_session_service.py`)**:
  - 已实现并测试通过，提供会话和消息管理功能。

### 2. CLI现状分析
- 当前CLI在 `src/cli/main.py` 中已实现 `debate`, `pa` 等命令组。
- 需要添加 `chat` 和 `wiki` 两个新的Typer子命令组。
- 需要集成现有的后端服务。

### 3. 依赖与风险分析
- **高风险**: `ChatService` 的核心依赖 `MultiRoleChatEngine` 缺失，将严重影响 `chat message` 和 `chat history` 命令的实现。
  - **应对策略**: 
    - 选项1 (采用): 直接在 `virtual_role_chat/` 目录中进行复用和重构，利用已实现的 `ChatSessionService` 和 `ChatRoomManager`，并通过 `ChatCoordinator` 实现完整功能。
- **中风险**: `WikiService` 和 `ChatRoomManager` 都依赖外部服务（Ollama, ChromaDB, 文件系统），需要确保这些服务在运行时可用。
- **低风险**: CLI集成相对直接，主要是调用后端服务并处理用户输入输出。

## 创新 (Innovation)

### 1. 功能增强 (遵循YAGNI，优先核心功能)
- **聊天室角色智能匹配**:
  - 集成 `RoleManager`，在创建聊天室时根据主题自动推荐相关角色。
  - 允许用户在创建聊天室时从现有角色库查找和选择角色，或创建新角色。
- **聊天室规则灵活配置**:
  - 集成制度原语系统，允许用户选择已注册的聊天规则原语或创建新的规则原语。
- **文档支持**:
  - 实现文档上传功能，将文档作为虚拟角色讨论的参考资料。
- **共识与分歧查看**:
  - 集成已有的智能助手服务，允许在聊天室中直接查看当前讨论的共识和分歧。
- **Wiki内容优化**:
  - 在CLI中实现更友好的Wiki内容显示，如分页或截断长内容。
  - 支持从标准输入读取Wiki内容。

### 2. 用户体验优化 (遵循KISS)
- **命令行参数优化**:
  - 为 `chat start` 命令提供清晰的参数，如 `--room`, `--topic` 等。
  - 为 `wiki create` 命令提供从标准输入读取内容的选项。
- **错误处理与提示**:
  - 提供清晰、具体的错误信息和使用建议。
  - 在命令执行过程中提供必要的状态反馈。

## 计划 (Plan) - 严格遵循TDD原则

### 任务分解与优先级

#### 高优先级 (必须完成 - MVP核心功能)
1. **实现 `chat` Typer子命令组**
2. **实现 `wiki` Typer子命令组**
3. **实现 `daip-cli chat start` 命令**
4. **实现 `daip-cli chat message` 命令**
5. **实现 `daip-cli chat history` 命令**
6. **实现 `daip-cli chat clear` 命令**
7. **实现 `daip-cli chat close` 命令**
8. **实现 `daip-cli chat delete` 命令**
9. **实现 `daip-cli wiki create` 命令**
10. **实现 `daip-cli wiki view` 命令**

#### 中优先级 (应尽量完成 - 增强功能)
11. **实现聊天室增强功能 (角色、规则、文档、共识)**

#### 核心重构任务 (必须完成以支持聊天功能)
12. **完善 `ChatCoordinator`**

### TDD实施计划 (每个任务都遵循TDD循环)

对于每个要实现的CLI命令和服务类，都将严格遵循TDD循环：

1. **RED**: 编写测试用例，断言功能的行为（如输出、调用后端服务等）。测试用例应覆盖正常流程和各种异常情况。
2. **GREEN**: 实现功能的最小可行代码，使测试通过。此时代码可能不够优雅，但能工作。
3. **REFACTOR**: 优化代码结构和实现，确保代码符合SOLID原则，提高可读性和可维护性。重构后必须重新运行所有相关测试，确保没有引入回归错误。

### 技术选型与架构 (遵循SOLID和KISS原则)

- **CLI框架**: 继续使用 Typer 和 Rich，保持技术栈一致性。
- **后端服务集成**: 直接调用 `ChatRoomManager`, `ChatSessionService`, `WikiService` 以及新完善的 `ChatCoordinator`。
- **文件处理**: 使用Python标准库读取本地文件。
- **聊天功能**: 通过在 `virtual_role_chat/` 目录中的重构实现完整功能，确保模块职责清晰。

## 执行 (Execution) - 严格遵循TDD和SOLID原则

### 第一步: 实现基础CLI结构 (`chat` 和 `wiki` 子命令组) (TDD)

### 第二步: 完善 `ChatCoordinator` 并实现核心聊天室管理命令 (TDD)
- `daip-cli chat start`
- `daip-cli chat message`
- `daip-cli chat history`
- `daip-cli chat clear`
- `daip-cli chat close`
- `daip-cli chat delete`

### 第三步: 实现Wiki管理命令 (TDD)
- `daip-cli wiki create`
- `daip-cli wiki view`

### 第四步: 集成聊天室增强功能 (TDD)
- 角色推荐与选择
- 规则配置
- 文档上传
- 共识/分歧查看

## 回顾 (Review) - 持续进行

在实现过程中，需要不断回顾：
- 是否严格遵循了TDD原则（每个功能点都有对应的测试用例）。
- 代码是否符合KISS（保持简单）、YAGNI（不做不必要的功能）、SOLID（高内聚低耦合）原则。
- 是否需要调整计划以应对新发现的问题。
- 实现的功能是否满足用户需求（通过用户故事和流程图进行验证）。