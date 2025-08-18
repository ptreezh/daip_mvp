# Unified Command-Line Interface - 命令参考大全

**文档状态:** 初始草案
**版本:** 0.1
**日期:** 2025-08-17
**焦点:** CLI命令语法、参数和功能描述。
**目标受众:** CLI用户, 开发者, 自动化脚本。
**原则:** 清晰、准确、易于查阅。

## 1. 概述

本文档提供了DAIP-LIVE统一命令行界面（`daip-cli`）所有可用命令的详细参考。每个命令都包含其用途、语法、参数和选项的说明，并提供简短的使用示例。

## 2. 命令列表

*   [核心命令](#3-核心命令)
*   [个人助手命令](#4-个人助手命令)
*   [场景命令](#5-场景命令)
*   [系统监控与配置命令](#6-系统监控与配置命令)

## 3. 核心命令

### `daip-cli status`
*   **用途**: 检查DAIP-LIVE系统各组件的健康状态和配置信息。
*   **语法**: `daip-cli status`
*   **示例**: `daip-cli status`

### `daip-cli roles`
*   **用途**: 列出所有可用的AI角色及其描述。
*   **语法**: `daip-cli roles`
*   **示例**: `daip-cli roles`

### `daip-cli roles create <name>`
*   **用途**: 创建一个新的AI角色。
*   **语法**: `daip-cli roles create <name> --description <desc> [--tags <tag1,tag2,...>]`
*   **参数**:
    *   `<name>` (必填): 新角色的名称。
*   **选项**:
    *   `--description <desc>` (必填): 角色的详细描述。
    *   `--tags <tag1,tag2,...>` (可选): 角色的标签列表，用逗号分隔。
*   **示例**: `daip-cli roles create "AI伦理学家" --description "专注于AI伦理和道德" --tags "伦理,专家"`

### `daip-cli roles update <name>`
*   **用途**: 更新现有AI角色的信息。
*   **语法**: `daip-cli roles update <name> [--description <desc>] [--add-tags <tag1,tag2,...>] [--remove-tags <tag1,tag2,...>]`
*   **参数**:
    *   `<name>` (必填): 要更新的角色的名称。
*   **选项**:
    *   `--description <desc>` (可选): 角色的新描述。
    *   `--add-tags <tag1,tag2,...>` (可选): 要添加的标签列表。
    *   `--remove-tags <tag1,tag2,...>` (可选): 要移除的标签列表。
*   **示例**: `daip-cli roles update "AI伦理学家" --description "更新后的描述" --add-tags "新标签"`

### `daip-cli roles set-workflow <name>`
*   **用途**: 为特定AI角色设置自定义工作流。
*   **语法**: `daip-cli roles set-workflow <name> --workflow <workflow_primitive_sequence>`
*   **参数**:
    *   `<name>` (必填): 要设置工作流的角色的名称。
*   **选项**:
    *   `--workflow <workflow_primitive_sequence>` (必填): 由制度原语组成的序列，用逗号分隔。
*   **示例**: `daip-cli roles set-workflow "分析师" --workflow "intent_recognize,task_decompose,social_division"`

### `daip-cli roles get-workflow <name>`
*   **用途**: 查看特定AI角色的当前工作流。
*   **语法**: `daip-cli roles get-workflow <name>`
*   **参数**:
    *   `<name>` (必填): 要查看工作流的角色的名称。
*   **示例**: `daip-cli roles get-workflow "分析师"`

### `daip-cli start <topic>`
*   **用途**: 启动一个新的AI辩论。
*   **语法**: `daip-cli start <topic> [--role <role_name>] [--rounds <num>] [--consensus <strategy>] [--verbose] [--save] [--output <file>]`
*   **参数**:
    *   `<topic>` (必填): 辩论的主题。
*   **选项**:
    *   `--role <role_name>` (可选，可重复): 参与辩论的AI角色名称。
    *   `--rounds <num>` (可选): 辩论的回合数 (默认: 3)。
    *   `--consensus <strategy>` (可选): 共识策略 (默认: `simple_majority_vote`)。
    *   `--verbose` (可选): 启用详细输出。
    *   `--save` (可选): 将辩论结果保存到文件。
    *   `--output <file>` (可选): 保存结果的文件路径 (默认: `debate_results.txt`)。
*   **示例**: `daip-cli start "AI伦理" --role "AI伦理学家" --rounds 5`

### `daip-cli help`
*   **用途**: 显示DAIP-LIVE CLI的详细帮助信息和使用示例。
*   **语法**: `daip-cli help`
*   **示例**: `daip-cli help`

## 4. 个人助手命令

### `daip-cli assistant chat <query>`
*   **用途**: 向个人助手发送单次查询，并接收回复。
*   **语法**: `daip-cli assistant chat <query>`
*   **参数**:
    *   `<query>` (必填): 发送给助手的文本查询。
*   **示例**: `daip-cli assistant chat "你好，今天天气怎么样？"`

## 5. 场景命令

### `daip-cli consult start <topic>`
*   **用途**: 启动一个新的专家咨询场景。
*   **语法**: `daip-cli consult start <topic> [--roles <role1,role2,...>] [--output <file>]`
*   **参数**:
    *   `<topic>` (必填): 咨询的主题。
*   **选项**:
    *   `--roles <role1,role2,...>` (可选): 指定参与咨询的专家角色。
    *   `--output <file>` (可选): 保存咨询结果的文件路径。
*   **示例**: `daip-cli consult start "如何提升AI模型性能"`

### `daip-cli consult status <consult_id>`
*   **用途**: 查看指定专家咨询的当前状态和进度。
*   **语法**: `daip-cli consult status <consult_id>`
*   **参数**:
    *   `<consult_id>` (必填): 专家咨询的唯一ID。
*   **示例**: `daip-cli consult status abc-123`

### `daip-cli consult get-report <consult_id>`
*   **用途**: 获取指定专家咨询的最终报告。
*   **语法**: `daip-cli consult get-report <consult_id> [--format <format>] [--output <file>]`
*   **参数**:
    *   `<consult_id>` (必填): 专家咨询的唯一ID。
*   **选项**:
    *   `--format <format>` (可选): 报告的输出格式 (如: `markdown`, `pdf`)。
    *   `--output <file>` (可选): 保存报告的文件路径。
*   **示例**: `daip-cli consult get-report abc-123 --format pdf`

### `daip-cli research start <topic>`
*   **用途**: 启动一个新的学术研究场景。
*   **语法**: `daip-cli research start <topic> [--depth <level>] [--output <file>]`
*   **参数**:
    *   `<topic>` (必填): 研究的主题。
*   **选项**:
    *   `--depth <level>` (可选): 研究的深度 (如: `basic`, `detailed`)。
    *   `--output <file>` (可选): 保存研究报告的文件路径。
*   **示例**: `daip-cli research start "量子计算在金融领域的应用"`

### `daip-cli research get-report <research_id>`
*   **用途**: 获取指定学术研究的最终报告。
*   **语法**: `daip-cli research get-report <research_id> [--format <format>] [--output <file>]`
*   **参数**:
    *   `<research_id>` (必填): 学术研究的唯一ID。
*   **选项**:
    *   `--format <format>` (可选): 报告的输出格式 (如: `markdown`, `pdf`)。
    *   `--output <file>` (可选): 保存报告的文件路径。
*   **示例**: `daip-cli research get-report xyz-456 --format markdown`

### `daip-cli wiki create <title>`
*   **用途**: 创建一个新的Wiki页面。
*   **语法**: `daip-cli wiki create <title> --content-file <file_path>`
*   **参数**:
    *   `<title>` (必填): Wiki页面的标题。
*   **选项**:
    *   `--content-file <file_path>` (必填): 包含Wiki页面内容的本地文件路径。
*   **示例**: `daip-cli wiki create "新概念" --content-file "./docs/new_concept.md"`

### `daip-cli wiki view <title>`
*   **用途**: 查看指定Wiki页面的内容。
*   **语法**: `daip-cli wiki view <title>`
*   **参数**:
    *   `<title>` (必填): Wiki页面的标题。
*   **示例**: `daip-cli wiki view "新概念"`

### `daip-cli wiki edit <title>`
*   **用途**: 编辑指定Wiki页面的内容。
*   **语法**: `daip-cli wiki edit <title> --content-file <file_path>`
*   **参数**:
    *   `<title>` (必填): Wiki页面的标题。
*   **选项**:
    *   `--content-file <file_path>` (必填): 包含更新内容的本地文件路径。
*   **示例**: `daip-cli wiki edit "新概念" --content-file "./docs/updated_concept.md"`

### `daip-cli wiki export <title>`
*   **用途**: 导出指定Wiki页面的内容到本地文件。
*   **语法**: `daip-cli wiki export <title> [--format <format>] [--output <file>]`
*   **参数**:
    *   `<title>` (必填): Wiki页面的标题。
*   **选项**:
    *   `--format <format>` (可选): 导出格式 (如: `markdown`, `html`, `pdf`)。
    *   `--output <file>` (可选): 导出文件路径。
*   **示例**: `daip-cli wiki export "新概念" --format pdf --output "./exports/new_concept.pdf"`

### `daip-cli workflow list`
*   **用途**: 列出所有可用的工作流（制度原语）。
*   **语法**: `daip-cli workflow list`
*   **示例**: `daip-cli workflow list`

### `daip-cli workflow execute <name>`
*   **用途**: 执行指定的工作流。
*   **语法**: `daip-cli workflow execute <name> [--params <json_string>]`
*   **参数**:
    *   `<name>` (必填): 要执行的工作流的名称。
*   **选项**:
    *   `--params <json_string>` (可选): 工作流所需的参数，以JSON字符串形式提供。
*   **示例**: `daip-cli workflow execute "ExpertConsultation" --params '{"topic": "AI安全"}'`

### `daip-cli workflow create <name>`
*   **用途**: 从文件创建新的工作流定义。
*   **语法**: `daip-cli workflow create <name> --definition-file <file_path>`
*   **参数**:
    *   `<name>` (必填): 新工作流的名称。
*   **选项**:
    *   `--definition-file <file_path>` (必填): 包含工作流定义的本地文件路径 (如: JSON, YAML)。
*   **示例**: `daip-cli workflow create "MyCustomWorkflow" --definition-file "./workflows/my_workflow.json"`

### `daip-cli workflow define-nl <description>`
*   **用途**: 通过自然语言描述来定义新的工作流。
*   **语法**: `daip-cli workflow define-nl <description>`
*   **参数**:
    *   `<description>` (必填): 工作流的自然语言描述。
*   **示例**: `daip-cli workflow define-nl "创建一个工作流，用于分析市场趋势，然后生成一份报告"`

### `daip-cli debate intervene <debate_id>`
*   **用途**: 在AI辩论过程中进行干预。
*   **语法**: `daip-cli debate intervene <debate_id> [--add-argument <argument>] [--ask-role <role_name> <question>] [--guide-focus <focus_topic>]`
*   **参数**:
    *   `<debate_id>` (必填): 辩论的唯一ID。
*   **选项**:
    *   `--add-argument <argument>` (可选): 要添加到辩论中的论点。
    *   `--ask-role <role_name> <question>` (可选): 向特定角色提问。
    *   `--guide-focus <focus_topic>` (可选): 引导辩论的焦点。
*   **示例**: `daip-cli debate intervene abc-123 --add-argument "我认为经济因素更重要"`

### `daip-cli debate set-rules <debate_id>`
*   **用途**: 为指定辩论设置议事规则。
*   **语法**: `daip-cli debate set-rules <debate_id> --rule <rule_primitive_name>`
*   **参数**:
    *   `<debate_id>` (必填): 辩论的唯一ID。
*   **选项**:
    *   `--rule <rule_primitive_name>` (必填): 议事规则原语的名称 (如: `weighted_vote`, `simple_majority_vote`)。
*   **示例**: `daip-cli debate set-rules abc-123 --rule "weighted_vote"`

### `daip-cli chatroom set-rules <room_id>`
*   **用途**: 为指定聊天室设置议事规则。
*   **语法**: `daip-cli chatroom set-rules <room_id> --rule <rule_primitive_name>`
*   **参数**:
    *   `<room_id>` (必填): 聊天室的唯一ID。
*   **选项**:
    *   `--rule <rule_primitive_name>` (必填): 议事规则原语的名称 (如: `round_robin_speaking`)。
*   **示例**: `daip-cli chatroom set-rules xyz-456 --rule "round_robin_speaking"`

### `daip-cli consensus status <process_id>`
*   **用途**: 查看共识形成过程的当前状态和冲突点。
*   **语法**: `daip-cli consensus status <process_id>`
*   **参数**:
    *   `<process_id>` (必填): 共识过程的唯一ID。
*   **示例**: `daip-cli consensus status con-789`

### `daip-cli consensus arbitrate <process_id>`
*   **用途**: 对共识过程中的某个观点进行仲裁（如投票）。
*   **语法**: `daip-cli consensus arbitrate <process_id> --vote <view_id>`
*   **参数**:
    *   `<process_id>` (必填): 共识过程的唯一ID。
*   **选项**:
    *   `--vote <view_id>` (必填): 要投票的观点的ID。
*   **示例**: `daip-cli consensus arbitrate con-789 --vote "view-A"`

### `daip-cli conflict resolve <conflict_id>`
*   **用途**: 解决AI角色之间的冲突。
*   **语法**: `daip-cli conflict resolve <conflict_id> --adopt-view <view_id>`
*   **参数**:
    *   `<conflict_id>` (必填): 冲突的唯一ID。
*   **选项**:
    *   `--adopt-view <view_id>` (必填): 要采纳的观点的ID。
*   **示例**: `daip-cli conflict resolve conf-101 --adopt-view "expert-B-view"`

## 6. 系统监控与配置命令

### `daip-cli monitor llm-usage`
*   **用途**: 查看AI模型（LLM）的调用情况和Tokens消耗统计。
*   **语法**: `daip-cli monitor llm-usage [--model <model_name>] [--last-24h] [--last-7d]`
*   **选项**:
    *   `--model <model_name>` (可选): 按模型名称过滤。
    *   `--last-24h` (可选): 显示过去24小时的数据。
    *   `--last-7d` (可选): 显示过去7天的数据。
*   **示例**: `daip-cli monitor llm-usage --model "gpt-4" --last-24h`

### `daip-cli monitor context-optimization <session_id>`
*   **用途**: 查看AI系统内部上下文优化（如压缩、摘要）的过程和效果。
*   **语法**: `daip-cli monitor context-optimization <session_id> [--step <step_num>]`
*   **参数**:
    *   `<session_id>` (必填): 会话的唯一ID。
*   **选项**:
    *   `--step <step_num>` (可选): 显示特定优化步骤的详细信息。
*   **示例**: `daip-cli monitor context-optimization sess-abc --step 3`

### `daip-cli monitor knowledge-generation <knowledge_id>`
*   **用途**: 查看AI系统生成新知识的过程和来源。
*   **语法**: `daip-cli monitor knowledge-generation <knowledge_id> [--source <source_id>]`
*   **参数**:
    *   `<knowledge_id>` (必填): 知识的唯一ID。
*   **选项**:
    *   `--source <source_id>` (可选): 按知识来源ID过滤。
*   **示例**: `daip-cli monitor knowledge-generation know-xyz --source "debate_id_123"`

### `daip-cli config llm set-provider <provider_name>`
*   **用途**: 设置LLM提供者和默认模型。
*   **语法**: `daip-cli config llm set-provider <provider_name> [--model <model_name>]`
*   **参数**:
    *   `<provider_name>` (必填): LLM提供者名称 (如: `ollama`, `openai`)。
*   **选项**:
    *   `--model <model_name>` (可选): 默认模型名称。
*   **示例**: `daip-cli config llm set-provider "ollama" --model "llama2"`

### `daip-cli config llm set-api-key <provider_name> <api_key>`
*   **用途**: 安全地设置LLM服务的API密钥。
*   **语法**: `daip-cli config llm set-api-key <provider_name> <api_key>`
*   **参数**:
    *   `<provider_name>` (必填): LLM提供者名称。
    *   `<api_key>` (必填): API密钥。
*   **示例**: `daip-cli config llm set-api-key "openai" "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"`

### `daip-cli config llm list`
*   **用途**: 列出当前配置的LLM提供者和模型信息（不显示密钥）。
*   **语法**: `daip-cli config llm list`
*   **示例**: `daip-cli config llm list`

---
