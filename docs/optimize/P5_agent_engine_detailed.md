# P5 代理引擎 - 详细设计 (P5 Agent Engine - Detailed Design)

## 📋 概述
P5模块是DAIP-LIVE系统的核心，包含代理执行器(`AgentExecutor`)，它是一个驱动代理理解目标、规划、执行工具并响应用户的有限状态机。该模块实现了动态的、事件驱动的代理执行循环。

## 🔧 核心功能详解

### AgentExecutor (代理执行器)
- **状态机驱动**: 实现代理的完整生命周期管理
- **异步事件流**: 输出`AsyncGenerator[AgentEvent, None]`事件流
- **实时状态监控**: 提供`get_status()` API用于实时监控
- **多模式执行**: 支持任务导向模式和对话模式

### 执行模式对比
| 模式 | 方法 | 用途 | 生命周期 |
|------|------|------|----------|
| 任务导向 | `run()` | 执行预定义任务序列 | 完成后终止 |
| 对话模式 | `chat_run()` | 交互式对话 | 持续运行直至显式终止 |

## 🏗️ 系统架构详情

### AgentExecutor 状态机
```
┌─────────────────┐
│     INIT        │
└─────────┬───────┘
          │
┌─────────▼───────┐
│    RUNNING      │◄─────────────────────┐
└─────────┬───────┘                      │
          │                               │
    ┌─────▼─────┐    ┌──────────────┐    │
    │ OBSERVING │───►│ THINKING     │    │
    └───────────┘    └──────────────┘    │
          │                   │          │
    ┌─────▼─────┐    ┌────────▼──────┐   │
    │ EVALUATING│───►│ EXECUTING_TOOL│   │
    └───────────┘    └───────────────┘   │
          │                   │          │
    ┌─────▼─────┐    ┌────────▼──────┐   │
    │ REFLECTING│◄───┤ RESPONDING    │   │
    └───────────┘    └───────────────┘   │
          │                   │          │
    ┌─────▼─────┐    ┌────────▼──────┐   │
    │ FINALIZING│◄───┤ SYNTHESIZING  │   │
    └───────────┘    └───────────────┘   │
          │                   │          │
    ┌─────▼───────────────────▼───────────┤
    │            COMPLETED                │
    └─────────────────────────────────────┘
          │          │
    ┌─────▼──────┐   │
    │   FAILED   │   │
    └────────────┘   │
                     │
    ┌────────────────▼─────────────────┐
    │            ERROR                 │
    └──────────────────────────────────┘
```

### AgentEvent 事件流详解
- **ThoughtEvent**: 代理内部思考或推理步骤
- **ToolCallEvent**: 代理决定调用工具
- **ToolOutputEvent**: 工具执行结果
- **FinalResponseEvent**: 代理的最终回复
- **ErrorEvent**: 代理执行过程中的错误
- **PermissionRequestEvent**: 工具执行权限请求
- **ResponseChunkEvent**: 流式响应块

## 🛠️ 实现细节

### 状态监控API
```python
def get_status() -> AgentStatus:
    """返回代理执行器的实时状态快照"""
    return AgentStatus(
        state=self.state,
        model_name=self.model_provider.config.model,
        tokens_used=self.tokens_used,
        tokens_total=self.get_context_window_size()
    )
```

### 执行模式实现
- **任务导向模式** (`run`): 基于`todo_list`或`workflow_definition`执行任务序列
- **对话模式** (`chat_run`): 基于`user_input_queue`的持续循环

## 📁 代码结构
```
src/daip_live/p5_agent_engine/
├── __init__.py
├── executor.py          # AgentExecutor主类，状态机实现
├── enhanced_executor.py # 增强版执行器
├── intent_recognizer.py # 意图识别器
├── workflow_executor.py # 工作流执行器
├── orchestrator.py      # 代理编排器
├── models.py            # 代理相关数据模型
├── interfaces.py        # 代理相关接口
├── services/            # 代理服务组件
│   ├── state_manager.py # 状态管理器
│   ├── context_manager.py # 上下文管理器
│   └── memory_service.py # 记忆服务
├── utils/               # 工具函数
│   ├── state_transitions.py # 状态转换工具
│   └── event_generators.py # 事件生成工具
└── config.py            # 代理配置管理
```

## 🔐 安全与集成
- **与P4工具管理集成**: 通过安全执行管道执行工具
- **与P3模型提供者集成**: 调用AI模型进行推理
- **与P0接口标准兼容**: 符合统一数据契约

---
> **需要API详情？** 查看 [P5_agent_engine_api.md](P5_agent_engine_api.md)  
> **需要集成信息？** 查看 [P5_agent_engine_integration.md](P5_agent_engine_integration.md)