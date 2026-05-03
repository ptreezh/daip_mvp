# P3 模型提供者 - 快速概览 (P3 Model Provider - Quick Overview)

## 🎯 核心功能
P3模块是DAIP-LIVE系统的关键抽象层，封装了与不同LLM交互的复杂性。

## 🔧 主要职责
- **统一接口**: 定义统一的模型调用接口
- **本地模型**: 支持Ollama, LlamaCpp等本地模型
- **云端模型**: 支持OpenAI, Claude, Gemini等云端模型
- **模型切换**: 支持运行时动态切换模型

## 📊 核心组件
- **IModelProvider**: 统一模型提供者接口
- **LiteLLMProvider**: 基于LiteLLM的通用提供者
- **ProviderFactory**: 模型提供者工厂
- **模型管理**: 模型配置和管理

## 🚀 快速启动
- **接口**: `generate()`, `embed()` 方法
- **配置**: 通过配置文件切换模型
- **支持**: 本地和云端模型
- **扩展**: 易于添加新的模型提供者

## 📁 相关资源
- [详细设计](P3_model_provider_detailed.md) - 完整的架构和实现细节
- [API参考](P3_model_provider_api.md) - 详细API文档
- [集成指南](P3_model_provider_integration.md) - 与其他模块的集成方式
- [故障排除](P3_model_provider_troubleshooting.md) - 常见问题和解决方案

---
> **需要更详细的信息？** 请查看上述相关资源链接。