# 聊天功能重构计划 (更新版)

## 目标
1. 在现有的 `virtual_role_chat/` 目录中进行复用和重构。
2. 实现缺失的聊天会话服务和消息处理功能。
3. 为CLI和未来的Web UI提供统一的基础服务接口。
4. 消除代码冗余，提高可维护性和可扩展性。

## 当前状态分析

### 已识别的聊天相关组件
1. **核心服务层**
   - `src/core_services/chat_service.py` (依赖缺失的 `MultiRoleChatEngine`)
   - `src/virtual_role_chat/chat_room_manager.py` (功能完整)
   - `src/virtual_role_chat/models.py` (数据模型)
   - `src/virtual_role_chat/interfaces.py` (接口定义)

2. **CLI层**
   - `src/cli/main.py` (包含CLI命令定义)

3. **测试**
   - `src/virtual_role_chat/test_*.py` (针对 `chat_room_manager` 等的测试)

### 问题识别
1. **依赖缺失**: `ChatService` 严重依赖缺失的 `MultiRoleChatEngine`。
2. **实现缺失**: `ChatSessionServiceInterface`, `RoleInteractionEngineInterface`, `ChatAnalyticsServiceInterface` 等接口缺少实现。
3. **功能不完整**: 缺少会话管理和消息处理的完整实现。

## 重构计划

### 第一阶段：实现聊天会话服务
1. 在 `src/virtual_role_chat/` 目录下创建 `chat_session_service.py` 文件。
2. 创建 `ChatSessionService` 类，实现 `ChatSessionServiceInterface` 接口。
3. 实现简单的消息存储（内存或文件）。
4. 实现基本的会话管理（开始、结束、暂停、恢复）。
5. 实现消息的添加和检索 (`add_message`, `get_messages`)。

### 第一阶段产物
- `src/virtual_role_chat/chat_session_service.py`
- `src/virtual_role_chat/chat_storage.py` (可选，用于抽象消息存储)

### 第二阶段：创建简化的消息处理协调器
1. 在 `src/virtual_role_chat/` 目录下创建 `chat_coordinator.py` 文件。
2. 创建 `ChatCoordinator` 类，作为 `ChatRoomManager` 和 `ChatSessionService` 之间的协调者。
3. 实现CLI所需的基本功能接口，如 `send_message_to_room`, `get_room_messages` 等。

### 第二阶段产物
- `src/virtual_role_chat/chat_coordinator.py`

### 第三阶段：更新CLI依赖
1. 修改 `src/cli/main.py`:
   - 移除对旧 `ChatService` 的依赖。
   - 引入新的 `ChatSessionService` 和 `ChatCoordinator` 实例。
   - 更新聊天相关的CLI命令以使用新的接口。

### 第四阶段：增强可扩展性
1. **设计插件化的消息存储**:
   - 定义消息存储接口，允许未来轻松替换为数据库或其他存储方案。

2. **为角色交互逻辑预留接口**:
   - 在 `ChatCoordinator` 的设计中预留未来集成复杂角色交互逻辑的可能性。

## 预期成果
1. 在 `virtual_role_chat/` 目录中实现完整的聊天功能。
2. 一套可重用的聊天模型、会话管理和消息处理组件。
3. 为CLI和未来Web UI提供一致的基础服务。
4. 消除代码冗余，提高可维护性。