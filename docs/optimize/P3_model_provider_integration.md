# P3 模型提供者 - 集成指南 (P3 Model Provider - Integration Guide)

## 🔗 与其他模块的集成

### 与P5代理引擎集成
```python
# P5使用P3进行AI模型调用
from daip_live.p3_model_provider.provider import LiteLLMProvider

class AgentExecutor:
    def __init__(self, model_provider: LiteLLMProvider):
        self.model_provider = model_provider
    
    async def call_model(self, prompt: str):
        async for chunk in self.model_provider.generate(prompt):
            yield chunk
```

### 与P2知识管理集成
```python
# P2使用P3进行文本嵌入
class KnowledgeManager:
    def __init__(self, model_provider: LiteLLMProvider):
        self.model_provider = model_provider
    
    async def embed_document(self, text: str):
        return await self.model_provider.embed(text)
```

## 🔄 模型调用模式

### 同步嵌入调用
```python
# 文本嵌入示例
async def embed_example(model_provider: LiteLLMProvider):
    text = "这是一个示例文本"
    embedding = await model_provider.embed(text)
    print(f"嵌入维度: {len(embedding)}")
```

### 流式生成调用
```python
# 流式生成示例
async def stream_generation_example(model_provider: LiteLLMProvider):
    prompt = "请解释什么是AI"
    
    full_response = ""
    async for chunk in model_provider.generate(prompt):
        full_response += chunk
        print(chunk, end="", flush=True)  # 实时输出
    
    return full_response
```

## 🔌 使用示例

### 基础模型调用
```python
from daip_live.p3_model_provider.provider import LiteLLMProvider
from daip_live.p3_model_provider.models import ModelConfig

# 创建模型配置
config = ModelConfig(
    model="gpt-4o",
    api_key="your-api-key",
    temperature=0.7
)

# 初始化模型提供者
model_provider = LiteLLMProvider(config)

# 调用模型
async for response_chunk in model_provider.generate("你好，请介绍自己"):
    print(response_chunk)
```

### 模型切换
```python
# 配置切换示例
def switch_model_provider(provider_name: str, config: ModelConfig):
    if provider_name == "openai":
        return LiteLLMProvider(config)
    elif provider_name == "ollama":
        from daip_live.p3_model_provider.providers.ollama import OllamaProvider
        return OllamaProvider(config)
    else:
        raise ValueError(f"不支持的模型提供者: {provider_name}")
```

### 本地模型配置
```python
# 本地Ollama配置
ollama_config = ModelConfig(
    model="llama3:8b",
    base_url="http://localhost:11434/v1"
)
ollama_provider = LiteLLMProvider(ollama_config)
```

## ⚡ 性能考虑
- **连接池**: 为HTTP客户端配置连接池
- **流式处理**: 使用流式响应避免内存积压
- **缓存策略**: 实现适当的响应缓存

## 🐛 常见集成问题
- **API密钥错误**: 检查API密钥配置
- **模型不可用**: 验证模型名称和可用性
- **网络超时**: 调整超时参数

---
> **需要API详情？** 查看 [P3_model_provider_api.md](P3_model_provider_api.md)  
> **需要实现详情？** 查看 [P3_model_provider_detailed.md](P3_model_provider_detailed.md)