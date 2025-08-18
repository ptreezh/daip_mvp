# Unified Command-Line Interface - 阶段 2: 智能体助手 - 修订版详细需求规范

**文档状态:** 修订版详细需求规范
**版本:** 1.1
**日期:** 2025-08-18
**焦点:** CLI智能助手的详细需求规范，遵循TDD原则和kiro SPECS规范，根据用户故事反馈进行修订。

## 1. 全局需求 (Top-Level)

### REQ-GLOBAL-CLI-ASSISTANT-001: 提供基于工作流驱动的智能个人助手CLI界面。
**描述**: 系统应提供一个基于工作流驱动的智能个人助手CLI界面，能够根据用户意图智能选择入口类型（Secretariat/Forum），规划并执行复杂任务，同时提供透明度和状态跟踪。
**理由**: 实现CLI与Web端个人助手功能对齐，提供一致的用户体验。
**关键成果**: 提升CLI的智能化水平和任务执行能力。

## 2. 功能需求分解

### 2.1 意图识别与分类 (Intent Recognition & Classification)

#### REQ-CLI-ASSISTANT-INTENT-001: 智能意图识别
**描述**: 个人助手能够识别用户输入的意图（如闲聊、信息查询、任务请求），并根据意图调用相应的后端服务。
**设计原则**: 智能路由，精准服务。
**用户影响**: 助手响应更智能，任务处理更准确。

##### 原子任务 (TDD-style):
*   **TC-CLI-ASSISTANT-INTENT-001**: (测试) 输入"今天天气怎么样？"被识别为信息查询意图。
*   **TC-CLI-ASSISTANT-INTENT-002**: (测试) 输入"你叫什么名字？"被识别为闲聊意图。
*   **TC-CLI-ASSISTANT-INTENT-003**: (测试) 输入"帮我预订明天去上海的机票"被识别为任务请求意图。

### 2.2 入口选择服务 (Entrance Selection Service)

#### REQ-CLI-ASSISTANT-ENTRANCE-001: 智能入口选择
**描述**: 根据用户意图、上下文特征（时间敏感性、查询复杂性、用户专业水平等）智能选择最适合的入口类型（Secretariat/Forum）。
**设计原则**: 智能决策，个性化体验。
**用户影响**: 自动为用户提供最适合的服务入口。

##### 原子任务 (TDD-style):
*   **TC-CLI-ASSISTANT-ENTRANCE-001**: (测试) 用户偏好入口选择功能正常。
*   **TC-CLI-ASSISTANT-ENTRANCE-002**: (测试) 基于上下文特征的入口选择功能正常。
*   **TC-CLI-ASSISTANT-ENTRANCE-003**: (测试) 时间敏感性分析功能正常。
*   **TC-CLI-ASSISTANT-ENTRANCE-004**: (测试) 查询复杂性分析功能正常。
*   **TC-CLI-ASSISTANT-ENTRANCE-005**: (测试) 用户专业水平评估功能正常。
*   **TC-CLI-ASSISTANT-ENTRANCE-006**: (测试) 历史偏好分析功能正常。
*   **TC-CLI-ASSISTANT-ENTRANCE-007**: (测试) 交互模式分析功能正常。
*   **TC-CLI-ASSISTANT-ENTRANCE-008**: (测试) 最优入口预测功能正常。

### 2.3 工作流编排器 (Workflow Orchestrator)

#### REQ-CLI-ASSISTANT-WORKFLOW-001: 工作流规划与执行
**描述**: 根据用户意图规划相应的工作流，协调任务执行流程，并提供进度跟踪。
**设计原则**: 流程化控制，透明执行。
**用户影响**: 支持复杂任务的自动化执行和监控。

##### 原子任务 (TDD-style):
*   **TC-CLI-ASSISTANT-WORKFLOW-001**: (测试) 工作流规划功能正常。
*   **TC-CLI-ASSISTANT-WORKFLOW-002**: (测试) 不同类型意图的工作流模板功能正常。
*   **TC-CLI-ASSISTANT-WORKFLOW-003**: (测试) 执行时间估算功能正常。
*   **TC-CLI-ASSISTANT-WORKFLOW-004**: (测试) 所需Agent确定功能正常。
*   **TC-CLI-ASSISTANT-WORKFLOW-005**: (测试) 工作流启动功能正常。
*   **TC-CLI-ASSISTANT-WORKFLOW-006**: (测试) 工作流步骤执行功能正常。
*   **TC-CLI-ASSISTANT-WORKFLOW-007**: (测试) 工作流进度获取功能正常。
*   **TC-CLI-ASSISTANT-WORKFLOW-008**: (测试) 剩余时间计算功能正常。
*   **TC-CLI-ASSISTANT-WORKFLOW-009**: (测试) 工作流完成和失败处理功能正常。

### 2.4 用户干预服务 (User Intervention Service)

#### REQ-CLI-ASSISTANT-INTERVENTION-001: 用户输入优化与集成
**描述**: 优化用户输入内容，分析干预影响，并生成集成建议。
**设计原则**: 建设性交互，智能优化。
**用户影响**: 提升用户输入的质量和有效性。

##### 原子任务 (TDD-style):
*   **TC-CLI-ASSISTANT-INTERVENTION-001**: (测试) 用户输入优化功能正常。
*   **TC-CLI-ASSISTANT-INTERVENTION-002**: (测试) 不同类型意图的输入优化功能正常。
*   **TC-CLI-ASSISTANT-INTERVENTION-003**: (测试) 用户干预集成功能正常。
*   **TC-CLI-ASSISTANT-INTERVENTION-004**: (测试) 干预影响分析功能正常。
*   **TC-CLI-ASSISTANT-INTERVENTION-005**: (测试) 集成建议生成功能正常。
*   **TC-CLI-ASSISTANT-INTERVENTION-006**: (测试) 影响分数计算功能正常。
*   **TC-CLI-ASSISTANT-INTERVENTION-007**: (测试) 优化历史记录功能正常。
*   **TC-CLI-ASSISTANT-INTERVENTION-008**: (测试) 优化统计信息获取功能正常。

### 2.5 共识跟踪服务 (Consensus Tracking Service)

#### REQ-CLI-ASSISTANT-CONSENSUS-001: 共识水平计算与跟踪
**描述**: 实时计算和跟踪辩论或讨论中的共识水平，并提取关键论点。
**设计原则**: 透明决策，智能分析。
**用户影响**: 提升用户对AI决策过程的理解和信任。

##### 原子任务 (TDD-style):
*   **TC-CLI-ASSISTANT-CONSENSUS-001**: (测试) 共识水平计算功能正常。
*   **TC-CLI-ASSISTANT-CONSENSUS-002**: (测试) 简单多数共识算法功能正常。
*   **TC-CLI-ASSISTANT-CONSENSUS-003**: (测试) 加权投票共识算法功能正常。
*   **TC-CLI-ASSISTANT-CONSENSUS-004**: (测试) 情感分析共识算法功能正常。
*   **TC-CLI-ASSISTANT-CONSENSUS-005**: (测试) Agent观点添加功能正常。
*   **TC-CLI-ASSISTANT-CONSENSUS-006**: (测试) 消息添加功能正常。
*   **TC-CLI-ASSISTANT-CONSENSUS-007**: (测试) 关键论点提取功能正常。
*   **TC-CLI-ASSISTANT-CONSENSUS-008**: (测试) 辩论摘要获取功能正常。

### 2.6 PersonalAssistantService核心功能

#### REQ-CLI-ASSISTANT-SERVICE-001: 核心服务功能
**描述**: 实现PersonalAssistantService的核心功能，包括服务初始化、会话管理、用户输入处理、状态跟踪等。
**设计原则**: 功能完整，稳定可靠。
**用户影响**: 提供完整的个人助手服务体验。

##### 原子任务 (TDD-style):
*   **TC-CLI-ASSISTANT-SERVICE-001**: (测试) 服务初始化功能正常。
*   **TC-CLI-ASSISTANT-SERVICE-002**: (测试) 会话创建功能正常。
*   **TC-CLI-ASSISTANT-SERVICE-003**: (测试) 用户输入处理功能正常。
*   **TC-CLI-ASSISTANT-SERVICE-004**: (测试) Secretariat输入处理功能正常。
*   **TC-CLI-ASSISTANT-SERVICE-005**: (测试) Forum输入处理功能正常。
*   **TC-CLI-ASSISTANT-SERVICE-006**: (测试) 输入意图分析功能正常。
*   **TC-CLI-ASSISTANT-SERVICE-007**: (测试) 会话状态获取功能正常。
*   **TC-CLI-ASSISTANT-SERVICE-008**: (测试) 任务状态获取功能正常。
*   **TC-CLI-ASSISTANT-SERVICE-009**: (测试) 透明度数据获取功能正常。
*   **TC-CLI-ASSISTANT-SERVICE-010**: (测试) 入口切换功能正常。
*   **TC-CLI-ASSISTANT-SERVICE-011**: (测试) 入口切换建议获取功能正常。
*   **TC-CLI-ASSISTANT-SERVICE-012**: (测试) 系统健康状态获取功能正常。
*   **TC-CLI-ASSISTANT-SERVICE-013**: (测试) 过期会话清理功能正常。
*   **TC-CLI-ASSISTANT-SERVICE-014**: (测试) 用户统计信息获取功能正常。

### 2.7 会话管理功能

#### REQ-CLI-ASSISTANT-SESSION-001: 会话管理
**描述**: 提供会话管理功能，包括默认最近会话、历史会话选择、智能主题生成等。
**设计原则**: 简洁易用，智能管理。
**用户影响**: 提升用户交互体验，方便会话管理。

##### 原子任务 (TDD-style):
*   **TC-CLI-ASSISTANT-SESSION-001**: (测试) 默认最近会话功能正常。
*   **TC-CLI-ASSISTANT-SESSION-002**: (测试) 历史会话列表功能正常。
*   **TC-CLI-ASSISTANT-SESSION-003**: (测试) 会话选择功能正常。
*   **TC-CLI-ASSISTANT-SESSION-004**: (测试) 智能主题生成功能正常。

### 2.8 精简指令功能

#### REQ-CLI-ASSISTANT-SHORTCMD-001: 精简指令支持
**描述**: 支持精简指令，提高操作效率。
**设计原则**: 高效便捷，易于记忆。
**用户影响**: 提升熟练用户的操作效率。

##### 原子任务 (TDD-style):
*   **TC-CLI-ASSISTANT-SHORTCMD-001**: (测试) 精简指令"assist"功能正常。
*   **TC-CLI-ASSISTANT-SHORTCMD-002**: (测试) 精简指令"intv"功能正常。
*   **TC-CLI-ASSISTANT-SHORTCMD-003**: (测试) 精简指令"cons"功能正常。
*   **TC-CLI-ASSISTANT-SHORTCMD-004**: (测试) 精简指令"disag"功能正常。
*   **TC-CLI-ASSISTANT-SHORTCMD-005**: (测试) 精简指令"sess"功能正常。

### 2.9 CLI命令实现

#### REQ-CLI-ASSISTANT-COMMAND-001: CLI命令功能
**描述**: 实现CLI命令，提供用户与个人助手交互的接口。
**设计原则**: 易用性强，功能完整。
**用户影响**: 用户可以通过CLI与个人助手进行交互。

##### 原子任务 (TDD-style):
*   **TC-CLI-ASSISTANT-COMMAND-001**: (测试) assistant chat命令功能正常。
*   **TC-CLI-ASSISTANT-COMMAND-002**: (测试) 输入验证功能正常。
*   **TC-CLI-ASSISTANT-COMMAND-003**: (测试) 响应显示功能正常。
*   **TC-CLI-ASSISTANT-COMMAND-004**: (测试) 错误处理功能正常。
*   **TC-CLI-ASSISTANT-COMMAND-005**: (测试) 异步执行功能正常。
*   **TC-CLI-ASSISTANT-COMMAND-006**: (测试) 会话管理命令功能正常。
*   **TC-CLI-ASSISTANT-COMMAND-007**: (测试) 精简指令功能正常。

## 3. 非功能性需求

### 3.1 性能需求
*   响应时间：单轮闲聊响应时间不超过2秒，复杂任务响应时间不超过5秒
*   并发处理：支持至少10个并发用户会话（虽然CLI是单用户，但系统应具备扩展性）

### 3.2 可靠性需求
*   系统可用性：99.5%
*   错误恢复：具备自动错误恢复机制

### 3.3 安全性需求
*   数据加密：敏感数据传输和存储需加密
*   访问控制：具备基本的用户身份验证机制

### 3.4 可用性需求
*   默认会话管理：自动使用最近会话，无需每次都指定会话ID
*   精简指令：支持4字母精简指令，提高操作效率
*   智能主题：自动生成有意义的会话主题

## 4. 验收标准

* 所有测试用例通过
* 代码覆盖率 >= 90%
* 有明确的文档说明
* 符合TDD开发原则
* 符合kiro SPECS规范
* 满足用户故事中的所有场景需求