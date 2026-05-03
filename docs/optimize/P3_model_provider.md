# P3 模型提供者 (Model Provider)

## 📋 概述

P3模块是DAIP-LIVE系统的关键抽象层，封装了与不同LLM交互的复杂性，为上层模块提供统一、简单的调用接口。该模块支持本地和云端模型，并允许用户在不同模型提供者间轻松切换。

## 🔧 核心功能

### 统一接口
- **标准化调用**: 定义统一的`generate(prompt, params)`和`embed(text)`接口
- **参数映射**: 将通用参数映射到特定模型的参数格式
- **响应处理**: 标准化不同模型的响应格式

### 本地模型支持
- **OllamaProvider**: 通过HTTP请求与本地Ollama服务通信
- **LlamaCppProvider**: 通过Python绑定直接调用llama.cpp库加载GGUF等格式的模型文件
- **本地优先**: 优先使用本地模型以保护数据隐私

### 云端模型支持
- **OpenAIProvider**: 调用OpenAI的API
- **AnthropicProvider**: 调用Anthropic的Claude API
- **GoogleProvider**: 调用Google的Gemini API
- **其他提供商**: 通过LiteLLM支持其他模型提供商

### 模型切换
- **配置驱动**: 用户可在配置文件中切换`provider: ollama`或`provider: openai`
- **运行时切换**: 支持运行时动态切换模型提供者
- **模型参数配置**: 支持不同模型的特定参数配置

## 🏗️ 系统架构

### 模型提供者层次
```
┌─────────────────────────────────────────┐
│           Model Provider Layer          │
├─────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐│
│  │  Local Models   │ │  Cloud Models   ││
│  │                 │ │                 ││
│  │  OllamaProvider │ │  OpenAIProvider ││
│  │LlamaCppProvider │ │AnthropicProvider││
│  │                 │ │ GoogleProvider  ││
│  └─────────────────┘ └─────────────────┘│
├─────────────────────────────────────────┤
│         LiteLLM Abstraction             │
├─────────────────────────────────────────┤
│        IModelProvider Interface         │
└─────────────────────────────────────────┘
```

### 核心组件
- **IModelProvider**: 统一模型提供者接口
- **LiteLLMProvider**: 基于LiteLLM的通用提供者
- **ProviderFactory**: 模型提供者工厂，根据配置创建合适的提供者实例

## 🧠 支持的模型

### 本地模型
- **Ollama**: 支持所有Ollama支持的模型
- **Llama.cpp**: 支持GGUF、GGML等格式的模型文件
- **本地OpenAI兼容API**: 支持遵循OpenAI API规范的本地模型服务

### 云端模型
- **OpenAI**: GPT-3.5, GPT-4系列
- **Anthropic**: Claude 2, Claude 3系列
- **Google**: Gemini系列
- **其他**: 通过LiteLLM支持的其他提供商

## 🛠️ 实现细节

### 异常处理
- **连接错误**: 处理模型服务连接失败
- **认证错误**: 处理API密钥或认证失败
- **模型错误**: 处理模型响应错误或超时

### 性能优化
- **连接池**: 管理到模型服务的连接
- **请求缓存**: 缓存重复的请求以提高性能
- **并发控制**: 控制并发请求的数量

### 流式响应
- **生成流**: 支持模型响应的实时流式传输
- **取消支持**: 支持中断正在进行的模型请求
- **进度监控**: 提供请求进度的监控接口

## 📁 代码结构

```
src/daip_live/p3_model_provider/
├── __init__.py
├── interfaces.py        # IModelProvider接口定义
├── provider.py          # LiteLLMProvider实现
├── factory.py           # ProviderFactory工厂
├── providers/           # 具体提供商实现
│   ├── base.py          # 基础提供者类
│   ├── ollama.py        # OllamaProvider
│   ├── llama_cpp.py     # LlamaCppProvider
│   ├── openai.py        # OpenAIProvider
│   └── anthropic.py     # AnthropicProvider
├── config.py            # 模型配置管理
└── models/              # 模型相关数据模型
    └── provider_config.py # 提供者配置模型
```

## 🔐 安全考虑

- **密钥管理**: 安全存储和传输API密钥
- **模型访问控制**: 控制对不同模型的访问权限
- **敏感数据保护**: 在发送到云端模型前过滤敏感信息

## 🧪 测试策略

- **接口兼容性**: 验证所有提供者实现统一接口
- **功能测试**: 测试各种模型的生成和嵌入功能
- **性能测试**: 测试不同提供商的响应时间和吞吐量
- **错误处理**: 测试各种异常情况下的处理能力

## 📄 相关规格文档

- `docs/specs/LLM_SCHEDULER_REQUIREMENTS.md` - LLM调度需求规格
- `docs/p3_model_provider/README.md` - P3模块具体实现文档