# Requirements Document: Personal Intelligence Hub - Core User Experience

## Introduction

本需求文档定义了统一的对话界面"Personal Intelligence Hub"，用户通过与单一的智能个人助手交互，该助手将自然语言指令转换为强大的底层"社会制度"(工作流)的执行，使复杂的AI协作变得直观和易于访问。

该系统基于现有DAIP-LIVE项目已实现的强大后端功能，专注于用户体验优化和界面设计，而不重新实现底层功能。

**Epic: E01 - Personal Intelligence Hub核心用户体验**

**Phase 1: 引导式体验 - 助手驱动的协作**
目标：建立核心交互循环，用户能够通过与个人助手的引导式自然语言交互，成功启动、监控并受益于预定义的复杂AI协作工作流。

**Phase 2: 创意体验 - 用户定义的协作**  
目标：赋能用户超越预定义流程，成为自己"社会制度"的"立法者"，通过自然语言定义新颖的协作工作流。

## Requirements

### Requirement 1: Hub Interface & Real-time Transparency (F1.1)

**User Story:** 作为用户，我希望通过一个基础的用户界面进行交互，包括中央聊天对话和提供系统内部认知过程实时可见性的"透明度监控器"。

#### Acceptance Criteria

**REQ-1.1.1: Central Dialogue Interface**

1. WHEN 用户启动系统 THEN 系统SHALL提供一个以持久聊天对话为中心的主要UI，用于所有用户-助手交互

**REQ-1.1.2: Real-time Transparency Monitor**  
2. WHEN 系统运行时 THEN UI SHALL具有专用的实时流式面板("透明度监控器")，显示内部操作的结构化日志
3. WHEN CognitiveAgent激活 THEN 透明度监控器MUST显示哪个CognitiveAgent处于活跃状态
4. WHEN 推理框架应用 THEN 透明度监控器MUST指明正在应用的ReasoningFramework或Epistemology
5. WHEN MemAgent检索或整合记忆 THEN 透明度监控器MUST指示MemAgent的活动
6. WHEN LLM后端调用 THEN 透明度监控器MUST显示被调用的LLM后端(model_id)

**REQ-1.1.3: Integrated WIKI & Task Panels**
7. WHEN 系统运行时 THEN UI SHALL包含WIKI和任务的辅助面板，随着工作流执行和产生新知识或任务而自动实时更新
8. WHEN ConsensusNode确定事实 THEN 该事实MUST立即出现在WIKI面板中
9. WHEN TaskDecompositionNode运行 THEN 新的子任务MUST立即填充到任务面板中

### Requirement 2: Assistant-Initiated Debates & Workflows (F1.2)

**User Story:** 作为用户，我希望个人助手能够解释我的请求，智能地设置辩论或知识综合任务，并以对话方式管理其执行。

#### Acceptance Criteria

**REQ-1.2.1: Intent-to-Workflow Mapping**

1. WHEN 用户提供自然语言提示(如"我需要可靠的分析...") THEN 助手SHALL使用IntentAnalysisService选择适当的预定义工作流(CriticalReviewWorkflow或MultiPerspectiveSynthesisWorkflow)

**REQ-1.2.2: Automated Heterogeneous Team Assembly**
2. WHEN 基于话题 THEN 助手SHALL自动查询CognitiveAgent注册表并提议一个AI专家团队
3. WHEN 组建团队 THEN 提议的团队MUST展现认知多样性(例如，至少包含一个具有"falsification"认识论的代理)
4. WHEN 团队确定 THEN 助手SHALL在执行前向用户展示提议的团队和工作流以供确认(例如，"好的，我将让Critic-AI和Analyst-AI使用我们的批判性审查流程来审查这个。继续吗？")

**REQ-1.2.3: Conversational Process Management**
5. WHEN 工作流执行 THEN 工作流的执行SHALL在主聊天对话中表示为一系列消息
6. WHEN 角色产生重要输出 THEN 每个角色的重要输出SHALL作为来自该角色的消息出现
7. WHEN 用户输入"/consensus now" THEN 用户SHALL能够动态触发当前辩论状态的共识计算，结果将发布回聊天中

### Requirement 3: Natural Language Workflow Creation (F2.1)

**User Story:** 作为用户，我希望个人助手能够将我对流程的对话式描述"编译"为正式的、可执行的工作流。

#### Acceptance Criteria

**REQ-2.1.1: NL-to-YAML Translation**

1. WHEN 用户提供多步骤指令(如"首先，两轮辩论，然后是静默反思期，每个代理写一个总结，然后最终投票") THEN 助手SHALL生成有效的、结构化的工作流定义文件(如PocketFlow YAML)
2. WHEN 生成过程 THEN 生成过程MUST使用专门的LLM调用，提示包含可用"制度原语"(Institutional Primitives)的完整模式
3. WHEN 工作流生成 THEN 生成的工作流必须在语法上正确且逻辑合理

**REQ-2.1.2: Workflow Dry-Run & Confirmation**
4. WHEN 执行前 THEN 助手SHALL向用户展示自定义工作流的摘要以供确认(例如，"好的，我创建了一个新的4步流程。它是这样工作的...准备运行吗？")

### Requirement 4: Interactive Prompt & Context Optimization (F2.2)

**User Story:** 作为用户，我希望个人助手能够主动与我协作，完善和优化初始提示和上下文，确保在启动工作流之前实现最大的任务聚焦。

#### Acceptance Criteria

**REQ-2.2.1: Proactive Clarification**

1. WHEN 用户的初始请求模糊(如"分析这个文档") THEN 助手SHALL询问澄清问题以缩小任务焦点(如"我应该专注于财务风险、竞争分析，还是总结关键要点？")

**REQ-2.2.2: Context Co-creation**
2. WHEN 需要额外上下文 THEN 助手SHALL能够向用户请求额外上下文。例如："这个话题在我们的WIKI中是新的。您有任何背景文档或关键原则需要我提供给专家团队吗？"用户的响应将动态添加到工作流执行的上下文中

### Requirement 5: Multi-Agent Collaboration Display

**User Story:** 作为用户，我希望能够清楚地看到多个AI代理的协作过程，包括它们的独立分析和集体智慧涌现。

#### Acceptance Criteria

1. WHEN 多代理协作开始 THEN 界面SHALL显示参与的每个代理及其认知档案
2. WHEN 代理进行分析 THEN 每个代理的输出SHALL以独特的视觉样式显示
3. WHEN 代理间产生分歧 THEN 系统SHALL高亮显示分歧点和不同观点
4. WHEN 集体智慧涌现 THEN 系统SHALL使用现有的EmergentInsightDetector显示涌现洞察
5. WHEN 共识形成 THEN 系统SHALL使用现有的共识算法显示共识结果和强度

### Requirement 6: Memory and Knowledge Management Integration

**User Story:** 作为用户，我希望系统能够智能地管理对话记忆和知识，并让我能够查看和管理这些信息。

#### Acceptance Criteria

1. WHEN 对话进行 THEN 系统SHALL使用现有的MemAgent系统智能管理记忆
2. WHEN 产生新知识 THEN 系统SHALL使用现有的FactExtractionService提取事实
3. WHEN 事实需要验证 THEN 系统SHALL使用现有的FactValidationService进行验证
4. WHEN 知识存储 THEN 系统SHALL使用现有的SSKG进行结构化存储
5. WHEN 用户查询记忆 THEN 系统SHALL提供记忆检索和浏览界面

### Requirement 7: Advanced Analytics and Reporting

**User Story:** 作为用户，我希望能够查看详细的分析报告，了解对话质量、代理表现、知识增长等指标。

#### Acceptance Criteria

1. WHEN 会话结束 THEN 系统SHALL使用现有的分析服务生成会话质量报告
2. WHEN 代理参与协作 THEN 系统SHALL评估每个代理的贡献度和表现
3. WHEN 知识库更新 THEN 系统SHALL跟踪知识增长和质量变化
4. WHEN 工作流执行 THEN 系统SHALL记录执行效率和token消耗
5. WHEN 用户请求报告 THEN 系统SHALL提供可视化的分析仪表板

### Requirement 8: System Integration and User Experience

**User Story:** 作为用户，我希望所有已实现的功能模块能够无缝集成，提供统一、流畅的用户体验。

#### Acceptance Criteria

1. WHEN 系统启动 THEN 所有现有服务SHALL正确初始化并准备就绪
2. WHEN 功能切换 THEN 用户SHALL能够在不同功能间无缝切换而不丢失上下文
3. WHEN 数据流转 THEN 各现有模块间的数据SHALL实时同步和更新
4. WHEN 错误发生 THEN 系统SHALL使用现有的错误处理机制提供友好的错误信息
5. WHEN 会话结束 THEN 系统SHALL使用现有的持久化机制保存所有重要数据
6. WHEN 性能监控 THEN 系统SHALL维持响应时间在2秒以内，准确率不低于95%
