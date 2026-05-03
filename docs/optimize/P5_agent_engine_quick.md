# P5 代理引擎 - 快速概览 (P5 Agent Engine - Quick Overview)

## 🎯 核心功能
P5模块是DAIP-LIVE系统的核心，负责代理的执行和管理。

## 🔧 主要职责
- **代理执行**: `AgentExecutor` 状态机驱动
- **事件流**: 异步 `AgentEvent` 流
- **执行模式**: 任务导向模式和对话模式

## 📊 状态机概览
```
INIT → RUNNING → COMPLETED/FAILED
       ↓
    OBSERVING → THINKING → EXECUTING_TOOL → ...
```

## 🚀 快速启动
- **主要类**: `AgentExecutor`
- **核心方法**: `run()`, `chat_run()`, `get_status()`
- **事件类型**: `ThoughtEvent`, `ToolCallEvent`, `FinalResponseEvent` 等

## 📁 相关资源
- [详细设计](P5_agent_engine_detailed.md) - 完整的架构和实现细节
- [API参考](P5_agent_engine_api.md) - 详细API文档
- [集成指南](P5_agent_engine_integration.md) - 与其他模块的集成方式
- [故障排除](P5_agent_engine_troubleshooting.md) - 常见问题和解决方案

---
> **需要更详细的信息？** 请查看上述相关资源链接。