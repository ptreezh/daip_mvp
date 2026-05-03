# P0 核心接口与类型 - 快速概览 (P0 Core Interfaces & Types - Quick Overview)

## 🎯 核心功能
P0模块是DAIP-LIVE系统的基石，定义跨模块共享的数据契约和接口契约。

## 🔧 主要职责
- **数据契约**: 定义Pydantic数据模型
- **接口契约**: 定义抽象基类接口
- **异常体系**: 统一异常处理层次
- **事件系统**: 定义AgentEvent事件流

## 📊 核心组件
- **数据模型**: `TodoItem`, `Role`, `Session`, `Message` 等
- **事件模型**: `AgentEvent` 及其子类型
- **接口定义**: `IModelProvider`, `IKnowledgeManager`, `ITool` 等
- **异常体系**: `DAIPError` 及其子类型

## 🚀 快速启动
- **数据模型**: 继承 `pydantic.BaseModel`
- **接口定义**: 继承 `abc.ABC`
- **事件流**: 使用 `AgentEvent` 联合类型
- **异常处理**: 扩展 `DAIPError` 基类

## 📁 相关资源
- [详细设计](P0_core_interfaces_detailed.md) - 完整的架构和实现细节
- [API参考](P0_core_interfaces_api.md) - 详细API文档
- [集成指南](P0_core_interfaces_integration.md) - 与其他模块的集成方式
- [故障排除](P0_core_interfaces_troubleshooting.md) - 常见问题和解决方案

---
> **需要更详细的信息？** 请查看上述相关资源链接。