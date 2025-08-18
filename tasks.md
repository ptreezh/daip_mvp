**TODO 任务清单：**

**阶段 1: 核心 CLI 增强**
*   **任务 1.1: 个人助手集成**
    *   命令: `daip-cli assistant chat <query>`
    *   对应 API: `personal_assistant_chat`
*   **任务 1.2: 辩论大厅 - 查看分歧点**
    *   命令: `daip-cli debate view-disagreements <debate_id>`
    *   对应 API: `debate_view_disagreements`
*   **任务 1.3: 辩论大厅 - 选择共识算法**
    *   命令: `daip-cli debate select-consensus-algorithm <debate_id> <algorithm_name>`
    *   对应 API: `debate_select_consensus_algorithm`

**阶段 2: 聊天室功能**
*   **任务 2.1: 聊天室 - 启动**
    *   命令: `daip-cli chat start [--room <room_name>]`
    *   对应 API: `chat_start`
*   **任务 2.2: 聊天室 - 发送消息**
    *   命令: `daip-cli chat message <room_id> <message>`
    *   对应 API: `chat_send_message`
*   **任务 2.3: 聊天室 - 查看历史记录**
    *   命令: `daip-cli chat history <room_id>`
    *   对应 API: `chat_view_history`

**阶段 3: 知识创建 / Wiki**
*   **任务 3.1: Wiki - 创建页面**
    *   命令: `daip-cli wiki create <title> --content <file_path>`
    *   对应 API: `wiki_create_page`
*   **任务 3.2: Wiki - 查看页面**
    *   命令: `daip-cli wiki view <title_or_id>`
    *   对应 API: `wiki_view_page`
*   **任务 3.3: Wiki - 导出页面**
    *   命令: `daip-cli wiki export <title_or_id> --format <format>`
    *   对应 API: `wiki_export_page`
*   **任务 3.4: 辩论 - 导出到 Wiki**
    *   命令: `daip-cli debate export-to-wiki <debate_id> --title <wiki_title>`
    *   对应 API: `debate_export_to_wiki`

**阶段 4: 角色管理 / 创建**
*   **任务 4.1: 角色 - 创建角色**
    *   命令: `daip-cli roles create <name> --description <desc> [--tags <tag1,tag2>]`
    *   对应 API: `roles_create_role`
*   **任务 4.2: 角色 - 邀请参与辩论**
    *   命令: `daip-cli roles invite <role_id> --to-debate <debate_id>`
    *   对应 API: `roles_invite_to_debate`
*   **任务 4.3: 角色 - 管理角色**
    *   命令: `daip-cli roles manage <role_id> --update-description <new_desc>`
    *   对应 API: `roles_manage_role`

**阶段 5: 工作流管理 (制度原语)**
*   **任务 5.1: 工作流 - 列出**
    *   命令: `daip-cli workflow list`
    *   对应 API: `workflow_list`
*   **任务 5.2: 工作流 - 创建**
    *   命令: `daip-cli workflow create <name> --definition <file_path>`
    *   对应 API: `workflow_create`
*   **任务 5.3: 工作流 - 选择**
    *   命令: `daip-cli workflow select <workflow_id> --for-scenario <scenario_type>`
    *   对应 API: `workflow_select`
*   **任务 5.4: 工作流 - 执行**
    *   命令: `daip-cli workflow execute <workflow_id> --params <json_string>`
    *   对应 API: `workflow_execute`
