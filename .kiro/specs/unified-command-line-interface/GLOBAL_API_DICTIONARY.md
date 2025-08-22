# 全局API文档字典 (Global API Dictionary)

**版本**: 1.0
**状态**: 分析中...

本文档是DAIP-LIVE系统后端API的唯一事实来源，旨在为CLI、TDD测试及其他客户端的开发提供一个明确、一致的接口契约。所有API都经过了实现逻辑审查。

---

## 模块 1: 角色管理 (Role Management)

### 服务: `src.core_services.role_manager.RoleManager`
- **描述**: 管理系统中的AI角色定义，通过文件系统（JSON文件）进行持久化。
- **审查备注**: 这是一个稳定、自洽且完全实现的模块，可直接用于生产。

| 方法签名 | 功能描述 | 实现状态 |
| --- | --- | --- |
| `__init__(self, roles_directory: Path = ROLES_DIR)` | 初始化管理器并从指定目录加载所有角色定义。 | **完整** |
| `get_role_by_id(self, role_id: str) -> Optional[Role]` | 根据ID检索单个角色。 | **完整** |
| `list_roles(self) -> list[Role]` | 返回所有可用角色的列表（为确保数据最新会重新从磁盘加载）。 | **完整** |
| `save_role(self, role: Role) -> bool` | 将一个角色对象保存或更新到对应的JSON文件中。 | **完整** |
| `delete_role(self, role_id: str) -> bool` | 根据ID删除一个角色的JSON文件并从内存中移除。 | **完整** |

---

## 模块 2: 知识维基 (Knowledge Wiki)

### 服务: `src.core_services.wiki_service.WikiService`
- **描述**: 管理版本化的知识库（Wiki），支持Markdown、版本控制、编辑提议和基于向量的语义搜索。
- **审查备注**: 这是一个功能完整的模块。它有外部依赖：需要一个正在运行的Ollama服务来提供嵌入模型，并依赖ChromaDB进行向量索引。
- **依赖**: `File System`, `Ollama`, `ChromaDB`

| 方法签名 | 功能描述 | 实现状态 |
| --- | --- | --- |
| `__init__(self, wiki_directory: str = ...)` | 初始化服务，设置wiki存储目录并连接到ChromaDB。 | **完整** |
| `create_entry(self, entry_name: str, content: str, ...)` | 创建一个新的wiki条目，包括其元数据和初始版本。 | **完整** |
| `get_entry(self, entry_name: str, version: Optional[str] = None)` | 根据名称和可选的版本号检索一个wiki条目。如果版本未指定，则返回最新版本。 | **完整** |
| `propose_edit(self, entry_name: str, new_content: str, ...)` | 为现有条目创建一个编辑提议，该提议需要后续被批准才能生效。 | **完整** |
| `search(self, query: str, top_k: int = 3) -> List[str]` | 对所有wiki条目执行语义搜索，返回最相关的结果片段。 | **完整** |

---

## 模块 3: 聊天室管理 (Chat Room Management)

### 服务: `src.virtual_role_chat.chat_room_manager.ChatRoomManager`
- **描述**: 负责聊天室的生命周期管理，包括创建、配置、更新、删除和列出。不处理实时消息。
- **审查备注**: 这是一个稳定且完全实现的模块。它可以配置为使用内存或文件持久化。
- **依赖**: `File System` (可选)

| 方法签名 | 功能描述 | 实现状态 |
| --- | --- | --- |
| `__init__(self, storage_path: Optional[str] = None, ...)` | 初始化管理器。如果提供了`storage_path`，则从文件加载/保存聊天室。 | **完整** |
| `create_chat_room(self, config: ChatRoomConfig) -> ChatRoomID` | 根据提供的配置创建一个新的聊天室。 | **完整** |
| `get_chat_room(self, room_id: ChatRoomID) -> ChatRoom` | 根据ID获取一个聊天室的完整信息。 | **完整** |
| `update_chat_room(self, room_id: ChatRoomID, config: ChatRoomConfig) -> bool` | 更新一个现有聊天室的配置。 | **完整** |
| `delete_chat_room(self, room_id: ChatRoomID) -> bool` | 删除一个聊天室。 | **完整** |
| `list_chat_rooms(self) -> List[ChatRoomSummary]` | 列出系统中所有聊天室的摘要信息。 | **完整** |
| `archive_chat_room(self, room_id: ChatRoomID) -> bool` | 归档一个聊天室（设置为非活动状态）。 | **完整** |

---

## 模块 4: 聊天消息服务 (Chat Messaging Service)

### 服务: `src.core_services.chat_service.ChatService`
- **描述**: 旨在处理聊天室内的实时消息和多角色对话。
- **审查备注**: **严重警告**: 此服务是围绕一个名为 `MultiRoleChatEngine` 的核心类构建的，但该类在代码库中完全缺失。因此，除了一个简单的模拟方法外，所有相关功能都无法实现。**该服务已被标记为"待重构"，计划通过集成 `virtual_role_chat` 模块的新组件来完善功能。**
- **依赖**: `MultiRoleChatEngine` (不存在), `virtual_role_chat.ChatRoomManager` (待集成), `virtual_role_chat.ChatSessionService` (待实现)

| 方法签名 | 功能描述 | 实现状态 |
| --- | --- | --- |
| `handle_simple_multi_role_chat(self, ...)` | 处理一个简化的、多角色的聊天模拟。 | **Mock** |
| `create_chat_engine(self, ...)` | 创建一个新的聊天引擎实例。 | **桩 (依赖缺失)** |
| `send_message_to_room(self, ...)` | 向指定的聊天室发送消息。 | **桩 (依赖缺失)** |
| `generate_responses_for_room(self, ...)` | 在聊天室中为一个或多个AI角色生成响应。 | **桩 (依赖缺失)** |
| `get_room_details(self, ...)` | 检索特定聊天室的详细信息。 | **桩 (依赖缺失)** |
| `list_all_rooms(self, ...)` | 列出指定引擎中的所有聊天室。 | **桩 (依赖缺失)** |

### 服务: `src.virtual_role_chat.chat_room_manager.ChatRoomManager`
- **描述**: 管理聊天室的生命周期，包括创建、配置、更新、删除和列出。不处理实时消息。
- **审查备注**: 这是一个稳定且完全实现的模块。它可以配置为使用内存或文件持久化。
- **依赖**: `File System` (可选)

| 方法签名 | 功能描述 | 实现状态 |
| --- | --- | --- |
| `__init__(self, storage_path: Optional[str] = None, ...)` | 初始化管理器。如果提供了`storage_path`，则从文件加载/保存聊天室。 | **完整** |
| `create_chat_room(self, config: ChatRoomConfig) -> ChatRoomID` | 根据提供的配置创建一个新的聊天室。 | **完整** |
| `get_chat_room(self, room_id: ChatRoomID) -> ChatRoom` | 根据ID获取一个聊天室的完整信息。 | **完整** |
| `update_chat_room(self, room_id: ChatRoomID, config: ChatRoomConfig) -> bool` | 更新一个现有聊天室的配置。 | **完整** |
| `delete_chat_room(self, room_id: ChatRoomID) -> bool` | 删除一个聊天室。 | **完整** |
| `list_chat_rooms(self) -> List[ChatRoomSummary]` | 列出系统中所有聊天室的摘要信息。 | **完整** |
| `archive_chat_room(self, room_id: ChatRoomID) -> bool` | 归档一个聊天室（设置为非活动状态）。 | **完整** |

### 服务: `src.virtual_role_chat.chat_session_service.ChatSessionService` (计划中)
- **描述**: 管理聊天会话的生命周期和消息处理。
- **审查备注**: **即将实现**: 此服务将实现 `ChatSessionServiceInterface` 接口，提供会话管理、消息存储和检索功能。
- **依赖**: `ChatRoomManager` (用于验证聊天室存在), `ChatStorage` (用于消息持久化)

| 方法签名 | 功能描述 | 实现状态 |
| --- | --- | --- |
| `start_session(self, room_id: ChatRoomID) -> SessionID` | 在指定聊天室启动一个新的会话。 | **计划中** |
| `end_session(self, session_id: SessionID) -> bool` | 结束一个会话。 | **计划中** |
| `add_message(self, session_id: SessionID, message: ChatMessage) -> bool` | 向会话中添加一条消息。 | **计划中** |
| `get_messages(self, session_id: SessionID, limit: int = 50, offset: int = 0) -> List[ChatMessage]` | 获取会话中的消息历史。 | **计划中** |
| `get_session_summary(self, session_id: SessionID) -> SessionSummary` | 获取会话摘要。 | **计划中** |

---

## 模块 5: 辩論引擎 (Debate Engine)

### 服务: `src.debate_system.multi_role_dialogue_engine.MultiRoleDialogueEngine`
- **描述**: 负责管理多角色辩论的完整流程，包括角色选择、对话轮次、上下文维护和收敛检测。
- **审查备注**: 引擎的内部工作流和算法逻辑是**完整**的。其核心依赖 `IntegratedLLMManager` 已被验证为功能完整。
- **依赖**: `RoleManager`, `IntegratedLLMManager`

| 方法签名 | 功能描述 | 实现状态 |
| --- | --- | --- |
| `__init__(self, cognitive_agent, role_manager, ...)` | 初始化引擎并注入所有必要的依赖服务。 | **完整** |
| `start_dialogue(self, session: DebateSession, topic: str, ...)` | 基于一个主题开始一场新的多角色对话/辩论。 | **完整** |
| `continue_dialogue(self, session_id: str)` | 继续现有对话，执行下一轮发言或进入总结阶段。 | **完整** |
| `get_dialogue_summary(self, session_id: str)` | 获取指定对话的当前状态、统计数据和摘要。 | **完整** |
| `end_dialogue(self, session_id: str)` | 结束一场对话，并生成最终的讨论总结。 | **完整** |

---

## 模块 6: LLM 调用管理 (LLM Call Management)

### 服务: `src.core_services.integrated_llm_manager.IntegratedLLMManager`
- **描述**: 提供一个统一的、带智能上下文优化的接口来调用大语言模型（LLM）。
- **审查备注**: 该管理器的编排逻辑是**完整**的。其核心依赖 `RealLLMClient` 已被验证为可以对本地Ollama服务进行真实的HTTP调用。
- **依赖**: `RealLLMClient`, `Ollama Service (http://localhost:11434)`

| 方法签名 | 功能描述 | 实现状态 |
| --- | --- | --- |
| `call_llm_for_role(self, role_id: str, user_input: str, ...)` | 为单个指定角色生成LLM响应，此过程包含自动的上下文优化。 | **完整** |
| `call_llm_for_multi_role_debate(self, participating_roles: list, ...)` | 为一场辩论中的多个角色分别生成LLM响应。 | **完整** |
| `get_role_performance_analytics(self, role_id: str)` | 获取特定角色的LLM调用性能分析数据。 | **完整** |
| `get_system_wide_analytics(self)` | 获取整个LLM调用系统的宏观性能分析数据。 | **完整** |

---

## 模块 7: 工作流与制度原语 (Workflows & Primitives)

### 服务: `src.institutional_primitives.registry.PrimitiveRegistry`
- **描述**: 一个内存中的注册表，用于管理、发现和实例化"制度原语"（即可复用的工作流节点）。
- **审查备注**: 这是一个基础性的、完全实现的模块。它本身是完整的，但它的价值取决于是否有实际的`InstitutionalPrimitive`类被注册进来。
- **依赖**: None

| 方法签名 | 功能描述 | 实现状态 |
| --- | --- | --- |
| `register_primitive(self, primitive_type: str, ...)` | 向注册表里注册一个新的原语类型和它对应的类。 | **完整** |
| `get_primitive(self, primitive_type: str)` | 根据类型名称获取一个原语的类定义。 | **完整** |
| `list_primitives(self) -> List[PrimitiveInfo]` | 列出所有已注册的原语及其元数据（名称、描述、输入/输出模式等）。 | **完整** |
| `validate_primitive(self, primitive_def: dict)` | 验证一个原语的定义是否符合规范。 | **完整** |
| `instantiate_primitive(self, primitive_def: dict)` | 根据一个定义来创建一个原语的实例对象。 | **完整** |

### 服务: `src.institutional_primitives.workflow_engine.WorkflowEngine`
- **描述**: 负责编排和执行由制度原语组成的复杂工作流。
- **审查备注**: 引擎的编排、图执行和状态管理逻辑是**完整**的。但是，暂停/恢复/取消功能是**桩实现**。引擎的实际能力完全取决于注册到`PrimitiveRegistry`中的具体原语。
- **依赖**: `PrimitiveRegistry`, Concrete `InstitutionalPrimitive` classes

| 方法签名 | 功能描述 | 实现状态 |
| --- | --- | --- |
| `__init__(self, primitive_registry: PrimitiveRegistry)` | 初始化引擎，并注入一个原语注册表实例。 | **完整** |
| `execute_workflow(self, workflow_def: WorkflowDefinition, ...)` | 异步地执行一个完整的工作流定义。 | **完整** |
| `get_workflow_status(self, execution_id: str)` | 获取一个正在运行或已完成的工作流的当前状态和进度。 | **完整** |
| `pause_workflow(self, execution_id: str)` | 暂停一个正在运行的工作流。 | **桩** |
| `resume_workflow(self, execution_id: str)` | 恢复一个已暂停的工作流。 | **桩** |
| `cancel_workflow(self, execution_id: str)` | 取消一个正在运行或已暂停的工作流。 | **桩** |

---

## 模块 8: 个人助手服务 (Personal Assistant Service) - 重构中

### 服务: `src.application.personal_assistant_service.PersonalAssistantService`
- **描述**: 统一AI助手服务，协调不同入口类型并提供智能用户支持。
- **审查备注**: **重构中**: 此服务已完整实现(90%+)，但正在进行重构以提高灵活性和可维护性。CLI将直接调用底层服务而非通过此服务，但Web界面和其他客户端仍依赖此服务。短期内保持兼容，长期可能变更。

| 方法签名 | 功能描述 | 实现状态 |
| --- | --- | --- |
| `__init__(self)` | 初始化服务并创建核心组件实例。 | **完整** |
| `initialize(self)` | 初始化服务配置和默认用户。 | **完整** |
| `create_session(self, user_id: str, context: dict[str, Any] = None)` | 创建新会话并选择合适的入口类型。 | **完整** |
| `process_user_input(self, session_id: str, user_input: dict[str, Any])` | 处理用户输入并路由到相应处理方法。 | **完整** |
| `_process_secretariat_input(self, session_aggregate: SessionAggregate, user_input: dict[str, Any])` | 处理Secretariat入口的用户输入。 | **完整** |
| `_process_forum_input(self, session_aggregate: SessionAggregate, user_input: dict[str, Any])` | 处理Forum入口的用户输入。 | **完整** |
| `_analyze_input_intent(self, content: str)` | 分析用户输入意图。 | **完整** |
| `get_session_status(self, session_id: str)` | 获取会话状态信息。 | **完整** |
| `get_task_status(self, task_id: str)` | 获取任务状态信息。 | **完整** |
| `get_transparency_data(self, session_id: str)` | 获取透明度数据。 | **完整** |
| `switch_entrance(self, session_id: str, target_entrance: str)` | 切换会话入口类型。 | **完整** |
| `get_entrance_suggestions(self, session_id: str)` | 获取入口切换建议。 | **完整** |
| `get_system_health(self)` | 获取系统健康状态。 | **完整** |
| `cleanup_expired_sessions(self, timeout_hours: int = 24)` | 清理过期会话。 | **完整** |
| `get_user_statistics(self, user_id: str)` | 获取用户统计数据。 | **完整** |

---