进入下面一个阶段前，请务必遵循 研究 创想 计划 执行 回顾的原则，基于TDD测试驱动开放的规范，对每个阶段的specs规范文档进行进一步的细化分解和补充。specs规范是kiro的开发规范，生成更具体的需求文档、设计文档和tasks清单。需要对原规范文档进行再详细的研究，结合项目实际和全局API参考，进一步细化需求，细化设计和细化任务清单。
全局API参考  D:\DAIP\daipMVPbackup\daip_mvp_project\.kiro\specs\unified-command-line-interface\GLOBAL_API_DICTIONARY.md    务必不要轻易增加和修改后端API，除非非常有必要时，也需要得到我的同意再增加后端服务。   

# 阶段 3: 聊天室与基础知识管理 (Wiki) - 任务清单

*   **3.1 实现 `daip-cli chat start` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟 `chat_room_manager` 成功创建聊天室，并断言 CLI 输出新创建聊天室的 ID。**测试包含不同发言规则（如轮流、随机）的聊天室创建。**
        *   **GREEN:** 在 `src/cli/main.py` 中创建 `chat` Typer 子命令组，并添加 `start` 命令，调用 `chat_room_manager`。**扩展 `create_chat_room` 以接受并应用 `ChatRulesConfig`。**
        *   **REFACTOR:** 优化房间名称的默认生成逻辑和用户提示。
*   **3.2 实现 `daip-cli chat message` 命令**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟 `chat_service` 成功发送消息，并断言 CLI 输出消息发送成功的确认信息。**测试虚拟角色根据聊天历史上下文进行响应。**
        *   **GREEN:** 在 `chat` 子命令组中添加 `message` 命令，接收 `room_id` 和 `message`，调用 `chat_service`。**确保聊天历史作为上下文传递给虚拟角色。**
        *   **REFACTOR:** 优化消息发送后的用户反馈。
*   **3.3 实现聊天室虚拟角色匹配与创建**
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，验证聊天室能根据规则匹配默认虚拟角色，并支持新增创建角色。
        *   **GREEN:** 实现聊天室创建时，根据配置自动匹配或创建虚拟角色的逻辑，并集成 `RoleManager`。
        *   **REFACTOR:** 优化角色匹配算法和新角色创建的流程。
*   **3.4 实现 `daip-cli chat history` 命令** (原 3.3)
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟 `chat_service` 返回指定聊天室的历史消息，并断言 CLI 输出能正确显示这些消息。
        *   **GREEN:** 在 `chat` 子命令组中添加 `history` 命令，接收 `room_id`，调用 `chat_service`。
        *   **REFACTOR:** 优化历史消息的显示格式（例如，包含时间戳和发送者）。
*   **3.5 实现 `daip-cli wiki create` 命令** (原 3.4)
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟 `wiki_service` 成功创建 Wiki 页面，并断言 CLI 输出确认信息。测试从本地文件读取内容并传递给后端。
        *   **GREEN:** 在 `src/cli/main.py` 中创建 `wiki` Typer 子命令组，并添加 `create` 命令，接收 `title` 和 `file_path`，调用 `wiki_service`。
        *   **REFACTOR:** 优化文件路径验证和文件读取的错误处理。
*   **3.6 实现 `daip-cli wiki view` 命令** (原 3.5)
    *   **TDD Cycle:**
        *   **RED:** 编写测试用例，模拟 `wiki_service` 返回指定 Wiki 页面的内容，并断言 CLI 输出能正确显示该内容。
        *   **GREEN:** 在 `wiki` 子命令组中添加 `view` 命令，接收 `title_or_id`，调用 `wiki_service`。
        *   **REFACTOR:** 优化长文本内容的显示方式，考虑分页或截断。
