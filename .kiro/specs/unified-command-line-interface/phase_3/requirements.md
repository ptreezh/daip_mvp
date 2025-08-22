# 阶段 3: 聊天室与基础知识管理 (Wiki) - 需求 (更新版 - 重构后)

*   **核心功能 - 聊天室基础操作**:
    *   用户能够通过 `daip-cli chat start [--room <room_name>] [--topic <topic>]` 启动新的聊天室。
        *   系统支持基于主题的智能角色推荐。
        *   用户可从现有角色库查找和选择角色加入聊天室。
        *   若找不到合适角色，支持用户创建新角色（角色将持久化存储）。
        *   用户可选择聊天规则（基于已注册的制度原语）或创建新的规则原语。
        *   支持上传文档作为虚拟角色讨论的参考资料。
        *   聊天室名称可以缺省，系统将自动生成一个临时名称。用户也可以显式指定名称。
    *   用户能够通过 `daip-cli chat message <message>` 在当前聊天室发送消息。
        *   用户也可以通过 `daip-cli chat message --room <room_id> <message>` 在指定聊天室发送消息。
    *   用户能够通过 `daip-cli chat history` 查看当前聊天室的历史消息。
        *   用户也可以通过 `daip-cli chat history --room <room_id>` 查看指定聊天室的历史消息。

*   **核心功能 - 聊天室管理**:
    *   用户能够通过 `daip-cli chat clear` 清除当前聊天室的消息历史。
        *   用户也可以通过 `daip-cli chat clear --room <room_id>` 清除指定聊天室的消息历史。
    *   用户能够通过 `daip-cli chat close` 关闭当前聊天室。
        *   关闭聊天室后，系统回到个人助手对话场景。
    *   用户能够通过 `daip-cli chat delete <room_id>` 删除指定的聊天室。
        *   删除操作需要用户确认。

*   **增强功能 - 场景内信息交互**:
    *   用户能够在聊天室中使用特殊指令（如 `/consensus`, `/disagreement`）直接查看当前讨论的共识和分歧。
    *   （YAGNI）当前版本暂不实现复杂的聊天室切换和自动存档逻辑，简化交互流程。

*   **核心功能 - Wiki管理**:
    *   用户能够通过 `daip-cli wiki create <title> [--content <content>] [--tags <tags>]` 创建新的 Wiki 页面。
    *   用户能够通过 `daip-cli wiki view <title_or_id>` 查看 Wiki 页面内容。
    *   用户能够通过 `daip-cli wiki edit <title_or_id> [--content <content>] [--tags <tags>]` 编辑 Wiki 页面内容。
    *   用户能够通过 `daip-cli wiki delete <title_or_id> [--force]` 删除 Wiki 页面。
    *   用户能够通过 `daip-cli wiki search <keywords> [--scope <scope>]` 搜索 Wiki 页面。
    *   用户能够通过 `daip-cli wiki list [--filter <filter>] [--sort <sort>]` 列出 Wiki 页面。