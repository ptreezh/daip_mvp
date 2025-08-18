# Unified Command-Line Interface - 用户需求规范

**文档状态:** 初始草案
**版本:** 0.1
**日期:** 2025-08-17
**焦点:** CLI用户交互设计与核心功能映射。
**目标受众:** LLM Agents, 系统架构师, CLI开发者。
**原则:** 金字塔原则 - 先概述，再详细分解。

## 1. 全局需求 (Top-Level)

### REQ-GLOBAL-CLI-001: 提供统一、强大且可脚本化的CLI界面。
**描述**: 系统应提供一个单一的、功能全面的命令行界面，作为DAIP-LIVE系统的主要交互入口，满足开发者、高级用户和自动化脚本的需求。
**理由**: 整合现有CLI原型，消除功能碎片化，提升用户体验和自动化能力。
**关键成果**: 提升CLI使用效率，降低自动化集成成本。

### REQ-GLOBAL-CLI-002: CLI功能应与Web端核心场景对齐。
**描述**: CLI应支持Web端已定义的核心业务场景（如专家咨询、学术研究、Wiki管理、工作流执行），确保用户可以通过命令行完成与Web端同等重要的操作。
**理由**: 提供一致的用户体验，无论通过何种界面，核心功能均可访问。
**关键成果**: 提升CLI的业务价值和覆盖范围。

## 2. CLI入口: 核心命令 (Global View)

### REQ-CLI-CORE-001: 系统状态检查。
**描述**: 用户可以通过CLI命令快速检查DAIP-LIVE系统各组件的健康状态和配置信息。
**设计原则**: 快速反馈，清晰诊断。
**用户影响**: 提升系统可观测性，便于故障排查。

#### 原子任务 (TDD-style):
*   **TC-CLI-STATUS-001**: (测试) `daip-cli status` 在系统健康时返回成功状态和所有组件的正常信息。
*   **TC-CLI-STATUS-002**: (测试) `daip-cli status` 在LLM服务不可用时，能准确报告LLM组件的错误状态。
*   **TC-CLI-STATUS-003**: (测试) `daip-cli status` 在配置错误时，能清晰指出配置问题。

### REQ-CLI-CORE-002: 辩论启动。
**描述**: 用户可以通过CLI命令启动一个新的AI辩论，并指定辩论主题、参与角色、回合数和共识策略。
**设计原则**: 参数化配置，灵活启动。
**用户影响**: 快速发起AI辩论，支持自动化辩论场景。

#### 原子任务 (TDD-style):
*   **TC-CLI-START-001**: (测试) `daip-cli start "AI伦理"` 成功启动默认参数的辩论。
*   **TC-CLI-START-002**: (测试) `daip-cli start "气候变化" --role "科学家" --rounds 5` 成功启动指定参数的辩论。
*   **TC-CLI-START-003**: (测试) `daip-cli start "主题" --rounds 0` (无效回合数) 返回错误提示。

### REQ-CLI-CORE-003: 角色列表。
**描述**: 用户可以通过CLI命令列出所有可用的AI角色及其描述。
**设计原则**: 信息清晰，易于查阅。
**用户影响**: 帮助用户了解可用的AI角色，便于选择。

#### 原子任务 (TDD-style):
*   **TC-CLI-ROLES-001**: (测试) `daip-cli roles` 成功列出所有已注册的角色。
*   **TC-CLI-ROLES-002**: (测试) `daip-cli roles` 在无角色时返回友好提示。

### REQ-CLI-CORE-004: 帮助信息。
**描述**: 用户可以通过CLI命令获取详细的命令使用说明和示例。
**设计原则**: 自解释性，易于学习。
**用户影响**: 降低CLI学习成本，提升使用效率。
**LLM Prompting**: “设计一套CLI命令，用于提供上下文敏感的帮助信息，包括命令用法、参数说明和示例。考虑如何集成到现有CLI框架中。”

#### 原子任务 (TDD-style):
*   **TC-CLI-HELP-001**: (测试) `daip-cli help` 显示所有顶级命令的帮助信息。
*   **TC-CLI-HELP-002**: (测试) `daip-cli start --help` 显示 `start` 命令的详细帮助。

### REQ-CLI-CORE-005: 角色管理 (创建/更新)。
**描述**: 用户可以通过CLI命令创建新的AI角色，并管理（如更新描述）现有角色。
**LLM Prompting**: “设计一套CLI命令，用于AI角色的创建和基本管理。考虑如何输入角色名称、描述和标签。”
**设计原则**: 角色可编程，管理便捷。
**用户影响**: 方便开发者和管理员快速定义和调整AI角色。

#### 原子任务 (TDD-style):
*   **TC-CLI-ROLES-MANAGE-001**: (测试) `daip-cli roles create "新角色" --description "这是一个新角色"` 成功创建角色。
*   **TC-CLI-ROLES-MANAGE-002**: (测试) `daip-cli roles update "旧角色" --description "更新后的描述"` 成功更新角色描述。

### REQ-CLI-CORE-006: 角色自定义工作流。
**描述**: 用户可以为特定AI角色设置简单的工作流，例如定义角色在接收到任务后的处理流程（如意图识别、任务分解、社会分工、任务分配、反馈综合）。
**LLM Prompting**: “设计一套CLI命令，允许用户为AI角色定义一个由制度原语组成的简单工作流。考虑如何指定角色ID和工作流序列。”
**设计原则**: 角色行为可编程，灵活适应。
**用户影响**: 提升AI角色的自动化和专业化水平。

#### 原子任务 (TDD-style):
*   **TC-CLI-ROLE-WORKFLOW-001**: (测试) `daip-cli roles set-workflow "分析师" --workflow "intent_recognize, task_decompose, social_division, assign_task, synthesize_feedback"` 成功设置角色工作流。
*   **TC-CLI-ROLE-WORKFLOW-002**: (测试) `daip-cli roles get-workflow "分析师"` 查看角色当前工作流。

## 3. CLI入口: 个人助手 (Global View)

### REQ-CLI-ASSISTANT-001: 单轮助手交互。
**描述**: 用户可以通过CLI命令向个人助手发送单次查询，并接收直接的回复。此功能将整合 `interactive_cli.py` 中的基础交互逻辑。
**LLM Prompting**: “设计一个CLI命令，允许用户输入文本，并由AI助手进行单次处理和回复。考虑如何处理用户输入、调用后端服务以及格式化输出。”
**设计原则**: 简洁高效，快速响应。**闲聊风格应符合交互助手中定义的友好、对话式风格。**
**用户影响**: 快速获取助手帮助，支持自动化查询。

#### 原子任务 (TDD-style):
*   **TC-CLI-ASSISTANT-CHAT-001**: (测试) `daip-cli assistant chat "你好"` 返回友好的问候。
*   **TC-CLI-ASSISTANT-CHAT-002**: (测试) `daip-cli assistant chat "总结一下最近的AI研究进展"` 触发意图识别并返回相关摘要。
*   **TC-CLI-ASSISTANT-CHAT-003**: (测试) `daip-cli assistant chat "帮我创建一个旅行计划"` 触发复杂任务意图，并返回初步响应。

### REQ-CLI-ASSISTANT-002: 意图识别与分类。
**描述**: 个人助手能够识别用户输入的意图（如闲聊、信息查询、任务请求），并根据意图调用相应的后端服务。
**LLM Prompting**: “如何设计一个CLI助手的意图分类机制，使其能区分用户是进行闲聊、查询信息还是请求执行复杂任务？请提供分类后的处理流程。”
**设计原则**: 智能路由，精准服务。**特别是对于闲聊，应保持自然、流畅的对话风格。**
**用户影响**: 助手响应更智能，任务处理更准确。

#### 原子任务 (TDD-style):
*   **TC-CLI-ASSISTANT-INTENT-001**: (测试) 输入“今天天气怎么样？”被识别为信息查询意图。
*   **TC-CLI-ASSISTANT-INTENT-002**: (测试) 输入“你叫什么名字？”被识别为闲聊意图。
*   **TC-CLI-ASSISTANT-INTENT-003**: (测试) 输入“帮我预订明天去上海的机票”被识别为任务请求意图。

### REQ-CLI-ASSISTANT-003: (未来) 多轮对话与上下文管理。
**描述**: 个人助手能够维护对话上下文，支持多轮交互，并在后续对话中利用历史信息。
**设计原则**: 连贯性，智能记忆。
**用户影响**: 提升助手交互的自然度和效率。

#### 原子任务 (TDD-style):
*   **TC-CLI-ASSISTANT-MULTI-001**: (测试) 用户提问“北京天气”，接着问“那上海呢？”，助手能理解“上海”是关于天气的后续提问。

## 4. CLI入口: Web场景对齐 (Global View)

### REQ-CLI-SCENARIO-001: 专家咨询场景。
**描述**: 用户可以通过CLI命令启动、管理和获取专家咨询场景的结果，与Web端 `TC_SCENARIO_001` (专家咨询场景测试) 对齐。
**LLM Prompting**: “设计一套CLI命令，用于模拟Web端专家咨询场景的各个阶段：问题输入、专家选择、讨论过程、建议生成。考虑如何通过命令行参数传递复杂信息。”
**设计原则**: 场景化操作，参数化控制。
**用户影响**: 自动化执行专家咨询流程，便于集成到脚本。

#### 原子任务 (TDD-style):
*   **TC-CLI-EXPERT-CONSULT-001**: (测试) `daip-cli consult start "如何提升AI模型性能"` 启动咨询。
*   **TC-CLI-EXPERT-CONSULT-002**: (测试) `daip-cli consult status <consult_id>` 查看咨询进度。
*   **TC-CLI-EXPERT-CONSULT-003**: (测试) `daip-cli consult get-report <consult_id>` 获取咨询报告。

### REQ-CLI-SCENARIO-002: 学术研究场景。
**描述**: 用户可以通过CLI命令启动、管理和获取学术研究场景的结果，与Web端 `TC_SCENARIO_002` (学术研究场景测试) 对齐。
**LLM Prompting**: “设计一套CLI命令，用于模拟Web端学术研究场景的各个阶段：主题输入、研究框架生成、多角度分析、报告生成。考虑如何通过命令行参数传递复杂信息。”
**设计原则**: 流程化控制，结果可导出。
**用户影响**: 自动化执行学术研究流程，便于批量处理。

#### 原子任务 (TDD-style):
*   **TC-CLI-RESEARCH-001**: (测试) `daip-cli research start "量子计算在金融领域的应用"` 启动研究。
*   **TC-CLI-RESEARCH-002**: (测试) `daip-cli research get-report <research_id> --format pdf` 获取研究报告。

### REQ-CLI-SCENARIO-003: Wiki知识管理。
**描述**: 用户可以通过CLI命令创建、查看、**编辑、贡献**、导出Wiki页面，实现知识的命令行管理。
**LLM Prompting**: “设计一套CLI命令，用于Wiki知识库的创建、查看、编辑、贡献和导出功能。考虑如何处理文件路径、内容输入和格式转换。”
**设计原则**: 知识可编程，管理便捷。
**用户影响**: 方便开发者和自动化脚本管理知识库。

#### 原子任务 (TDD-style):
*   **TC-CLI-WIKI-001**: (测试) `daip-cli wiki create "新概念" --content-file "concept.md"` 创建Wiki页面。
*   **TC-CLI-WIKI-002**: (测试) `daip-cli wiki view "新概念"` 查看Wiki页面内容。
*   **TC-CLI-WIKI-003**: (测试) `daip-cli wiki edit "新概念" --content-file "updated_concept.md"` 编辑Wiki页面。
*   **TC-CLI-WIKI-WIKI-004**: (测试) `daip-cli wiki export "新概念" --format markdown --output "concept.md"` 导出Wiki页面。

### REQ-CLI-SCENARIO-004: 工作流执行。
**描述**: 用户可以通过CLI命令列出、创建和执行DAIP系统中的工作流（制度原语）。
**LLM Prompting**: “设计一套CLI命令，用于列出可用工作流、创建新工作流定义以及执行指定工作流。考虑如何传递工作流参数。”
**设计原则**: 流程可控，参数灵活。
**用户影响**: 自动化执行复杂业务流程，提升系统集成度。

#### 原子任务 (TDD-style):
*   **TC-CLI-WORKFLOW-001**: (测试) `daip-cli workflow list` 列出所有可用工作流。
*   **TC-CLI-WORKFLOW-002**: (测试) `daip-cli workflow execute "ExpertConsultation" --params '{"topic": "AI安全"}'` 执行指定工作流。
*   **TC-CLI-WORKFLOW-003**: (测试) `daip-cli workflow create "MyCustomWorkflow" --definition-file "workflow_def.json"` 创建新工作流。

### REQ-CLI-SCENARIO-005: 辩论过程用户干预。
**描述**: 用户可以通过CLI命令在AI辩论过程中进行干预，例如添加论点、提出问题或引导讨论方向。此功能与Web端“Forum模式”的用户干预能力对齐。
**LLM Prompting**: “设计一套CLI命令，允许用户在AI辩论进行中插入自己的论点、向特定AI角色提问或改变辩论焦点。考虑如何识别辩论ID和干预类型。”
**设计原则**: 实时影响，过程可控。
**用户影响**: 提升用户在AI协作过程中的参与度和影响力。

#### 原子任务 (TDD-style):
*   **TC-CLI-DEBATE-INTERVENE-001**: (测试) `daip-cli debate intervene <debate_id> --add-argument "我的论点"` 在辩论中添加论点。
*   **TC-CLI-DEBATE-INTERVENE-002**: (测试) `daip-cli debate intervene <debate_id> --ask-role "AI伦理学家" "你对这个观点怎么看？"` 向特定角色提问。
*   **TC-CLI-DEBATE-INTERVENE-003**: (测试) `daip-cli debate intervene <debate_id> --guide-focus "请关注经济影响"` 引导辩论焦点。

### REQ-CLI-SCENARIO-006: 共识与冲突仲裁。
**描述**: 用户可以通过CLI命令参与AI系统内部的共识形成过程，并在AI角色之间出现冲突时进行仲裁或引导解决。
**LLM Prompting**: “设计一套CLI命令，允许用户查看AI共识的当前状态、识别冲突点，并提供仲裁机制（如投票、强制采纳某个观点）来解决AI之间的分歧。”
**设计原则**: 透明决策，用户主导。
**用户影响**: 提升AI决策的透明度和用户对最终结果的信任度。

#### 原子任务 (TDD-style):
*   **TC-CLI-CONSENSUS-ARBITRATE-001**: (测试) `daip-cli consensus status <process_id>` 查看共识过程状态和冲突点。
*   **TC-CLI-CONSENSUS-ARBITRATE-002**: (测试) `daip-cli consensus arbitrate <process_id> --vote "观点A"` 对共识中的某个观点进行投票。
*   **TC-CLI-CONSENSUS-ARBITRATE-003**: (测试) `daip-cli conflict resolve <conflict_id> --adopt-view "专家B的观点"` 仲裁并采纳某个专家的观点。

## 5. CLI入口: 系统透明度与配置 (Global View)

### REQ-CLI-MONITOR-001: 模型调用与Tokens消耗监控。
**描述**: 用户可以通过CLI命令查看AI模型（LLM）的调用情况和Tokens消耗统计，以便进行成本控制和性能分析。
**LLM Prompting**: “设计一套CLI命令，用于实时或历史查询AI模型调用次数、每次调用的Tokens消耗以及总消耗。考虑如何按时间范围、模型类型进行过滤。”
**设计原则**: 成本透明，性能可查。
**用户影响**: 便于用户监控AI资源使用情况。

#### 原子任务 (TDD-style):
*   **TC-CLI-MONITOR-LLM-001**: (测试) `daip-cli monitor llm-usage` 显示总模型调用次数和Tokens消耗。
*   **TC-CLI-MONITOR-LLM-002**: (测试) `daip-cli monitor llm-usage --model "gpt-4" --last-24h` 显示特定模型在过去24小时的消耗。

### REQ-CLI-MONITOR-002: 上下文优化过程透明化。
**描述**: 用户可以通过CLI命令查看AI系统内部上下文优化（如压缩、摘要、重构）的过程和效果，了解AI如何处理和利用信息。
**LLM Prompting**: “设计一套CLI命令，用于展示AI系统如何对对话或任务上下文进行优化处理的详细步骤和结果。考虑如何可视化优化前后的上下文差异。”
**设计原则**: 过程透明，智能可信。
**用户影响**: 提升用户对AI内部工作机制的理解和信任。

#### 原子任务 (TDD-style):
*   **TC-CLI-MONITOR-CONTEXT-001**: (测试) `daip-cli monitor context-optimization <session_id>` 显示指定会话的上下文优化历史。
*   **TC-CLI-MONITOR-CONTEXT-002**: (测试) `daip-cli monitor context-optimization <session_id> --step 3` 显示特定优化步骤的详细信息。

### REQ-CLI-MONITOR-003: 知识生成过程透明化。
**描述**: 用户可以通过CLI命令查看AI系统生成新知识（如从辩论中提炼观点、从研究中总结发现）的过程和来源。
**LLM Prompting**: “设计一套CLI命令，用于展示AI系统如何从原始数据或对话中提炼、整合并生成新知识的详细过程。考虑如何追溯知识来源和生成路径。”
**设计原则**: 知识溯源，智能可信。
**用户影响**: 提升用户对AI生成知识的信任度和可验证性。

#### 原子任务 (TDD-style):
*   **TC-CLI-MONITOR-KNOWLEDGE-001**: (测试) `daip-cli monitor knowledge-generation <knowledge_id>` 显示指定知识的生成过程。
*   **TC-CLI-MONITOR-KNOWLEDGE-002**: (测试) `daip-cli monitor knowledge-generation --source "debate_id_xyz"` 显示从特定辩论中生成的所有知识。

### REQ-CLI-CONFIG-001: 模型配置管理。
**描述**: 用户可以通过CLI命令配置DAIP-LIVE系统使用的AI模型（LLM），包括设置提供者、模型名称和API密钥等。
**LLM Prompting**: “设计一套CLI命令，用于管理AI模型的配置，包括列出可用模型、设置默认模型、配置API密钥。考虑安全性（如API密钥不直接显示）。”
**设计原则**: 配置灵活，安全便捷。
**用户影响**: 方便用户根据需求切换和管理AI模型。

#### 原子任务 (TDD-style):
*   **TC-CLI-CONFIG-LLM-001**: (测试) `daip-cli config llm set-provider "ollama" --model "llama2"` 设置LLM提供者和模型。
*   **TC-CLI-CONFIG-LLM-002**: (测试) `daip-cli config llm set-api-key "openai" "sk-xxxxxxxx"` 安全地设置API密钥。
*   **TC-CLI-CONFIG-LLM-003**: (测试) `daip-cli config llm list` 列出当前配置的LLM信息（不显示密钥）。

### REQ-CLI-WORKFLOW-004: 自然语言工作流定义。
**描述**: 用户可以通过自然语言描述来定义新的工作流（制度原语），系统能够理解并将其转化为可执行的工作流定义。
**LLM Prompting**: “设计一套CLI命令，允许用户输入自然语言描述来创建工作流。AI系统应能解析描述，生成工作流定义，并提供确认机制。”
**设计原则**: 智能创建，降低门槛。
**用户影响**: 极大简化工作流创建过程，使非技术用户也能定义复杂流程。

#### 原子任务 (TDD-style):
*   **TC-CLI-WORKFLOW-NL-001**: (测试) `daip-cli workflow define-nl "创建一个工作流，用于分析市场趋势，然后生成一份报告"` 成功生成工作流定义。
*   **TC-CLI-WORKFLOW-NL-002**: (测试) 系统在生成定义后，提供确认或修改的选项。

### REQ-CLI-DEBATE-CONFIG-001: 辩论/聊天室议事规则设置。
**描述**: 用户可以通过CLI命令为特定的辩论或聊天室设置议事规则，这些规则以制度原语的形式存在，例如投票机制、发言顺序、冲突解决策略等。
**LLM Prompting**: “设计一套CLI命令，允许用户为辩论或聊天室设置特定的议事规则。考虑如何指定房间ID和规则原语的名称及参数。”
**设计原则**: 规则可控，场景定制。
**用户影响**: 提升用户对AI协作环境的控制力，使其更符合特定需求。

#### 原子任务 (TDD-style):
*   **TC-CLI-DEBATE-RULES-001**: (测试) `daip-cli debate set-rules <debate_id> --rule "weighted_vote"` 为辩论设置加权投票规则。
*   **TC-CLI-DEBATE-RULES-002**: (测试) `daip-cli chatroom set-rules <room_id> --rule "round_robin_speaking"` 为聊天室设置轮流发言规则。

---
