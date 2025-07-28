# Cline 执行协议

为确保严格遵守 `RIPER-5` 模式并杜绝流程错误，特制定本执行协议。

## 核心原则
1.  **模式即法律**：`RESEARCH`, `INNOVATE`, `PLAN`, `EXECUTE`, `REVIEW` 模式是不可逾越的硬性规定。
2.  **原子操作**：所有任务必须分解为原子操作，并在 `PLAN` 模式下生成编号清单。
3.  **执行前审查**：在进入 `EXECUTE` 模式前，必须向用户展示完整的实施计划并获得明确批准。

## 防错机制
-   **工具使用约束**：
    -   `RESEARCH` 模式：仅允许使用 `read_file`, `search_files`, `list_files`, `ask_followup_question`。
    -   `INNOVATE` 模式：仅允许使用 `plan_mode_respond` (若在PLAN MODE) 或 `ask_followup_question`。
    -   `PLAN` 模式：仅允许使用 `plan_mode_respond` (若在PLAN MODE) 或 `ask_followup_question`。
    -   `EXECUTE` 模式：仅允许使用 `replace_in_file`, `write_to_file`, `execute_command` (requires_approval=true)。
    -   `REVIEW` 模式：仅允许使用 `search_files`, `read_file`, `ask_followup_question`。
-   **执行前确认**：在任何代码修改操作前，必须输出一个包含所有步骤的 `Implementation Checklist`，并等待用户指令 "ENTER EXECUTE MODE"。

## 监督与审计
-   所有任务的 `lessons_learned.md` 文件必须包含对流程合规性的反思。
-   本协议文件将作为所有任务的最高行为准则。
