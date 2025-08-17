# 03 - 聊天室 - 需求文档 (TDD重构版)

## 1. 简介
该模块允许用户管理聊天室的生命周期。**注意**: 根据API分析，核心的消息传递引擎尚未实现。因此，此模块当前仅支持聊天室的管理功能。

## 2. 用户故事
- **As a user**, I want to create a new chat room with a specific name and topic.
- **As a user**, I want to see a list of all available chat rooms.
- **As a user**, I want to delete a chat room.
- **As a user**, I want to be informed that the messaging feature is not yet available if I try to join a room.

## 3. 功能性需求
- **FR-CR-01**: **必须**提供一个聊天室子菜单，包含以下选项：
    - `[1]` 创建新聊天室
    - `[2]` 查看聊天室列表
    - `[3]` 删除聊天室
    - `[4]` 加入聊天室 (显示功能未实现消息)
    - `[0]` 返回主菜单
- **FR-CR-02**: **创建新聊天室**:
    - **必须**提示用户输入聊天室的名称和主题。
    - **必须**调用 `ChatRoomManager.create_chat_room` API。
    - **必须**向用户显示成功创建的消息和 `room_id`。
- **FR-CR-03**: **查看聊天室列表**:
    - **必须**调用 `ChatRoomManager.list_chat_rooms` API。
    - **必须**将返回的聊天室摘要列表以表格形式展示。
- **FR-CR-04**: **删除聊天室**:
    - **必须**提示用户输入要删除的 `room_id`。
    - **必须**调用 `ChatRoomManager.delete_chat_room` API。
- **FR-CR-05**: **加入聊天室**:
    - 当用户选择此选项并输入 `room_id` 时，系统**必须**显示一条明确的消息，例如：“错误：聊天消息功能后端尚未实现，无法加入房间。”

## 4. 验收测试用例
- **ATC-CR-01: 成功创建聊天室**
    - **Given**: 用户在聊天室子菜单。
    - **When**: 用户选择 "创建新聊天室" 并输入所需信息。
    - **Then**: `ChatRoomManager.create_chat_room` **必须**被以正确的参数调用。
    - **And**: 终端**必须**显示成功消息。
- **ATC-CR-02: 成功列出聊天室**
    - **Given**: 后端有两个已创建的聊天室。
    - **When**: 用户选择 "查看聊天室列表"。
    - **Then**: `ChatRoomManager.list_chat_rooms` **必须**被调用。
    - **And**: 终端**必须**显示一个包含两行数据的表格。
- **ATC-CR-03: 尝试加入聊天室**
    - **Given**: 用户在聊天室子菜单。
    - **When**: 用户选择 "加入聊天室"。
    - **Then**: 终端**必须**显示一条指出功能未实现的消息。
    - **And**: `ChatService` 或 `MultiRoleChatEngine` 的任何消息传递相关方法**绝不能**被调用。