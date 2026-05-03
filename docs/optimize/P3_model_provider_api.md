# P3 模型提供者 - API参考 (P3 Model Provider - API Reference)

## 📋 核心类与方法

### IModelProvider 接口
```python
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, List

class IModelProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, params: Dict) -> AsyncGenerator[str, None]:
        """生成文本响应的异步生成器"""
        pass
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """将文本转换为嵌入向量"""
        pass
```

### LiteLLMProvider
```python
class LiteLLMProvider(IModelProvider):
    def __init__(self, config: ModelConfig):
        self.config = config
    
    async def generate(self, prompt: str, params: Dict = None) -> AsyncGenerator[str, None]:
        """生成文本响应"""
    
    def embed(self, text: str) -> List[float]:
        """生成文本嵌入"""
    
    async def get_model_info(self, model_name: str) -> Dict:
        """获取模型信息"""
    
    def list_models(self) -> List[str]:
        """列出可用模型"""
```

## 🧩 配置模型

### 模型配置
```python
from pydantic import BaseModel
from typing import Optional

class ModelConfig(BaseModel):
    model: str  # 模型名称
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    timeout: Optional[int] = 30
```

## 🔧 本地模型支持

### OllamaProvider
```python
class OllamaProvider(IModelProvider):
    async def generate(self, prompt: str, params: Dict) -> AsyncGenerator[str, None]:
        """使用Ollama生成文本"""
    
    def embed(self, text: str) -> List[float]:
        """使用Ollama生成嵌入"""
```

### LlamaCppProvider
```python
class LlamaCppProvider(IModelProvider):
    async def generate(self, prompt: str, params: Dict) -> AsyncGenerator[str, None]:
        """使用LlamaCpp生成文本"""
    
    def embed(self, text: str) -> List[float]:
        """使用LlamaCpp生成嵌入"""
```

## 📡 流式响应
- **AsyncGenerator**: 支持流式文本生成
- **Token流**: 实时返回生成的token
- **中断支持**: 支持中断生成过程

---
> **需要实现详情？** 查看 [P3_model_provider_detailed.md](P3_model_provider_detailed.md)  
> **需要集成指南？** 查看 [P3_model_provider_integration.md](P3_model_provider_integration.md)