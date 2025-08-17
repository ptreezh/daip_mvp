# 03 - 聊天室 - 设计文档 (TDD重构版)

## 1. 技术方法
聊天室功能将由 `start_chat_room()` 函数入口进行管理。该模块将严格遵循“仅实现有可靠后端的功能”的原则。

- **API依赖**: 此模块将严格且仅依赖 `ChatRoomManager` 提供的API。所有方法的调用都必须参照 `documentation/GLOBAL_API_DICTIONARY.md`。**严禁**调用 `ChatService` 或任何与 `MultiRoleChatEngine` 相关的方法。
- **状态管理**: CLI不维护任何聊天室状态。所有信息都直接通过 `ChatRoomManager` API获取。
- **用户反馈**: 对于未实现的功能（加入聊天室），提供清晰、直接的反馈是设计的关键部分。

## 2. 组件交互
- **`start_chat_room()`**:
    - 初始化 `ChatRoomManager` 的一个实例。
    - 显示聊天室管理子菜单。
- **`handle_create_chat_room()`**:
    - 提示用户输入 `name`, `topic` 等创建房间所需的信息。
    - 构造一个 `ChatRoomConfig` 对象。
    - 调用 `chat_room_manager.create_chat_room(config)`。
    - 打印成功信息和返回的 `room_id`。
- **`handle_list_chat_rooms()`**:
    - 调用 `chat_room_manager.list_chat_rooms()`。
    - 使用 `rich.table` 格式化并显示返回的摘要列表。
- **`handle_delete_chat_room()`**:
    - 提示用户输入 `room_id`。
    - 调用 `chat_room_manager.delete_chat_room(room_id)`。
    - 打印成功或失败信息。
- **`handle_join_chat_room()`**:
    - 此函数**不会**调用任何后端API。
    - 它将直接使用 `rich.print` 打印一条 `[bold red]错误: 聊天消息功能后端尚未实现，无法加入房间。[/bold red]` 的消息。

## 3. CLI流程 / 用户界面
**子菜单:**
```
--- 聊天室管理 ---
[1] 创建新聊天室
[2] 查看聊天室列表
[3] 删除聊天室
[4] 加入聊天室
[0] 返回主菜单
>
```
**当用户选择 [4]:**
```
> 请输入要加入的房间ID: room-12345
[bold red]错误: 聊天消息功能后端尚未实现，无法加入房间。[/bold red]
```

## 4. 测试策略
- **单元测试 (`tests/test_chat_room.py`)**:
    - **目标**: 独立测试聊天室管理CLI的UI和流程逻辑。
    - **Mock**:
        - `ChatRoomManager` 将被完全mock。
        - `create_chat_room` 将返回一个固定的 `room_id`。
        - `list_chat_rooms` 将返回一个固定的摘要列表。
        - `delete_chat_room` 将返回 `True`。
    - **断言**:
        - 验证当用户创建、列出、删除聊天室时，对应的 `ChatRoomManager` 方法被以正确的参数调用。
        - 验证 `list_chat_rooms` 的返回结果被正确地格式化为表格并打印到 `stdout`。
        - **关键测试**: 编写一个测试 `test_join_room_shows_error`，模拟用户选择 "加入聊天室"，并断言 `stdout` 打印了预期的错误消息，同时**断言没有任何 `ChatService` 或 `ChatRoomManager` 的方法被调用**（除了初始化）。