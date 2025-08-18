# 阶段 3: 聊天室与基础知识管理 (Wiki) - 设计

*   **子命令组:** 为聊天相关命令创建 `chat` 子命令组，为 Wiki 相关命令创建 `wiki` 子命令组。
*   **后端集成:**
    *   `chat` 命令将调用 `src/core_services/chat_service.py` 和 `src/virtual_role_chat/chat_room_manager.py` 中的现有逻辑。
    *   **聊天室规则:** `ChatRoomManager` 的 `create_chat_room` 方法将扩展以接受包含发言规则（如轮流发言、随机发言、话题兴趣匹配激活发言等）的配置（例如，一个 `ChatRulesConfig` 对象，该配置可由 `ChatRulePrimitive` 定义）。
    *   **虚拟角色管理:** 默认匹配或创建聊天室的虚拟角色，并支持新增角色。
    *   **上下文传递:** 聊天历史记录将作为上下文传递给虚拟角色，以支持连贯的对话。
    *   `wiki` 命令将调用 `src/core_services/wiki_service.py` 和 `src/real_demo_system/wiki_knowledge_system.py` 中的现有逻辑。
*   **文件处理:** CLI 需要能够读取本地文件内容并将其作为参数传递给后端服务。
