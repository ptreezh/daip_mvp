# 阶段 4 & 5: 高级角色管理、工作流、Wiki 导出、完善与文档 - 需求

## 阶段 4: 高级角色管理、工作流与 Wiki 导出 - 需求

*   用户能够通过 `daip-cli roles create <name> --description <desc> [--tags <tag1,tag2>]` 创建新 AI 角色。
*   用户能够通过 `daip-cli roles invite <role_id> --to-debate <debate_id>` 邀请角色参与辩论。
*   用户能够通过 `daip-cli roles manage <role_id> --update-description <new_desc>` 更新现有角色属性。
*   用户能够通过 `daip-cli workflow list` 列出所有可用工作流。
*   用户能够通过 `daip-cli workflow create <name> --definition <file_path>` 创建自定义工作流。
*   用户能够通过 `daip-cli workflow select <workflow_id> --for-scenario <scenario_type>` 为特定场景选择工作流。
*   用户能够通过 `daip-cli workflow execute <workflow_id> --params <json_string>` 执行指定工作流。
*   用户能够通过 `daip-cli wiki export <title_or_id> --format <format>` 导出 Wiki 页面。
*   用户能够通过 `daip-cli debate export-to-wiki <debate_id> --title <wiki_title>` 将辩论结果导出为 Wiki 页面。

## 阶段 5: 完善、错误处理与文档 - 需求

*   所有命令应有清晰的帮助信息和使用示例。
*   所有后端服务调用应包含健壮的错误处理机制，并向用户提供有意义的错误消息。
*   CLI 应该能够处理常见的用户输入错误（例如，无效的 ID、缺失的参数）。
*   提供全面的 CLI 使用文档。
*   集成 linting 和格式化工具到开发流程中。
