# MVP 用户用例、用户故事和场景说明：多角色辩论

本文档详细描述了 DAIP-MVP 中“多角色辩论”功能的用户用例、用户故事和交互场景。

## 1. 用户画像 (User Personas)

*   **角色**: Alex，一名学术研究员
*   **背景**: Alex 正在研究一个复杂且充满争议的社会科学课题（例如：“人工智能对就业市场的长期影响”）。他需要从多个角度（经济、技术、社会、伦理）收集和验证信息，并形成一个全面、客观的观点。
*   **痛点**:
    *   单一信息源或单一AI模型往往存在偏见或“幻觉”。
    *   很难系统地组织和对比来自不同领域的观点。
    *   需要一个工具来帮助他进行批判性思维和深度分析。

*   **角色**: Sarah，一名企业战略决策者
*   **背景**: Sarah 所在的公司正在考虑是否要投资一项新兴技术。她需要评估这项技术的市场潜力、技术风险和潜在的投资回报率。
*   **痛点**:
    *   需要快速获得关于一个陌生领域的、经过多方验证的深度分析报告。
    *   团队内部可能存在意见分歧，需要一个中立的平台来促进讨论和达成共识。
    *   希望AI能扮演不同领域的专家（如技术专家、市场分析师、财务顾问），为决策提供支持。

## 2. 用户故事 (User Stories)

以 Alex 的视角：

*   **US-1**: 作为一个研究员，我希望能够发起一个多角色AI辩论，并指定一个明确的辩论主题（例如：“人工智能是否会在20年内导致大规模结构性失业？”）。
*   **US-2**: 作为一个研究员，我希望能够从预设的专家库中选择参与辩论的AI角色（例如：经济学家、技术未来学家、社会学家、伦理学家）。
*   **US-3**: 作为一个研究员，我希望能够观察AI角色之间轮流发言、相互诘问、补充论据的完整过程，以了解不同观点的碰撞。
*   **US-4**: 作为一个研究员，我希望系统能够明确标记出AI在辩论中可能出现的“幻觉”或不确定性陈述，以便我进行事实核查。
*   **US-5**: 作为一个研究员，我希望在辩论结束后，能收到一个由“系统综合师”生成的、结构化的综合意见，其中应包含关键论点、共识点、主要分歧以及对未来研究的建议。
*   **US-6**: 作为一个研究员，我希望能够通过简单的命令行界面（CLI）或API接口来启动和监控整个辩论过程。

## 3. 详细流程与序列图

```mermaid
sequenceDiagram
    participant User as Alex (CLI/API)
    participant Web_API as FastAPI
    participant WorkflowManager as 主状态机
    participant DebateProtocol as 辩论协议
    participant RoleManager as 角色管理器
    participant MemoryService as 记忆服务
    participant SynthesisEngine as 综合引擎

    User->>Web_API: POST /sessions/session123/command (发起辩论)
    Web_API->>WorkflowManager: 收到辩论请求 (主题, 角色)
    WorkflowManager->>WorkflowManager: 状态切换: IDLE -> DEBATE_IN_PROGRESS
    WorkflowManager->>DebateProtocol: 启动辩论(主题, 角色)
    DebateProtocol->>RoleManager: 加载指定角色
    RoleManager-->>DebateProtocol: 返回角色实例

    loop 辩论轮次 (例如 5 轮)
        DebateProtocol->>DebateProtocol: 选择下一个发言角色
        DebateProtocol->>MemoryService: 获取对话历史和知识
        MemoryService-->>DebateProtocol: 返回上下文
        DebateProtocol->>DebateProtocol: 构建Prompt (包含辩论指令)
        Note right of DebateProtocol: 调用LLM生成发言...
        DebateProtocol->>MemoryService: 保存新发言
        DebateProtocol->>Web_API: 通过SSE流发送新发言
        Web_API-->>User: 实时看到新发言
    end

    WorkflowManager->>WorkflowManager: 状态切换: DEBATE_IN_PROGRESS -> SYNTHESIS_GENERATION
    WorkflowManager->>SynthesisEngine: 请求生成综合意见
    SynthesisEngine->>MemoryService: 获取完整辩论历史
    MemoryService-->>SynthesisEngine: 返回历史记录
    Note right of SynthesisEngine: 调用LLM生成综合意见...
    SynthesisEngine-->>WorkflowManager: 返回结构化综合意见
    WorkflowManager->>Web_API: 通过SSE流发送综合意见
    Web_API-->>User: 收到最终的综合意见
```

## 4. 示例辩论场景

*   **用户输入**: `!debate --topic "人工智能是否会在20年内导致大规模结构性失业？" --roles "经济学家,技术未来学家,社会学家"`
*   **系统响应 (SSE Stream)**:
    *   `[EVENT: DEBATE_STARTED] 主题: "人工智能是否会在20年内导致大规模结构性失业？"`
    *   `[EVENT: TURN_START] 角色: 经济学家`
    *   `[EVENT: MESSAGE] 经济学家: 从历史角度看，技术进步在短期内会造成摩擦性失业，但长期来看会创造新的就业岗位...`
    *   `[EVENT: TURN_START] 角色: 技术未来学家`
    *   `[EVENT: MESSAGE] 技术未来学家: 我认为这次不同。通用人工智能（AGI）的出现可能会替代大量认知型工作，其替代速度将远超新岗位的创造速度...`
    *   `[EVENT: TURN_START] 角色: 社会学家`
    *   `[EVENT: MESSAGE] 社会学家: 我们需要关注的不仅是失业数量，还有财富分配的公平性。如果AI带来的巨大生产力收益只集中在少数人手中，将会引发严重的社会问题...`
    *   ... (辩论继续) ...
    *   `[EVENT: DEBATE_ENDED]`
    *   `[EVENT: SYNTHESIS_START]`
    *   `[EVENT: SYNTHESIS_RESULT]`
        ```markdown
        # 关于“人工智能对就业市场的长期影响”的综合意见

        ## 1. 核心共识
        *   所有参与者都认为，人工智能将深刻地重塑就业市场，而非简单地替代现有工作。
        *   短期内，特定行业的摩擦性失业不可避免。

        ## 2. 主要分歧点
        *   **替代速度 vs. 创造速度**: 技术未来学家认为替代速度将远超创造速度，而经济学家持更乐观的历史主义观点。
        *   **问题本质**: 社会学家认为核心问题是财富分配，而不仅仅是就业数量。

        ## 3. 潜在幻觉与不确定性
        *   **[UNCERTAINTY]**: 关于AGI出现的确切时间点和能力，目前所有预测都基于推测，缺乏实证依据。

        ## 4. 结论与建议
        *   建议政策制定者应提前布局，建立更完善的社会保障体系和终身学习计划...
