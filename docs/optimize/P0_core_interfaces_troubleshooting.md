# P0 核心接口与类型 - 故障排除 (P0 Core Interfaces & Types - Troubleshooting)

## 🚨 常见问题

### 1. 接口实现错误
**症状**: 实现接口时出现 `TypeError: Can't instantiate abstract class`
**可能原因**: 
- 未实现接口中的所有抽象方法
- 方法签名不匹配

**解决方案**:
```python
# 确保实现所有接口方法
from daip_live.core.interfaces import IModelProvider

class MyModelProvider(IModelProvider):
    async def generate(self, prompt: str, params: Dict) -> AsyncGenerator[str, None]:
        # 必须实现此方法
        pass
    
    def embed(self, text: str) -> List[float]:
        # 必须实现此方法
        pass
```

### 2. 模型验证失败
**症状**: Pydantic模型验证错误
**可能原因**: 
- 字段类型不匹配
- 必需字段缺失
- 验证约束未满足

**解决方案**:
```python
from pydantic import BaseModel, validator

class MyModel(BaseModel):
    name: str
    age: int
    
    @validator('age')
    def age_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Age must be positive')
        return v
```

## 🔧 诊断工具

### 事件类型检查
```python
from daip_live.core.models import AgentEvent

def debug_event(event: AgentEvent):
    print(f"Event type: {event.type}")
    print(f"Event dict: {event.dict()}")
    print(f"Event JSON: {event.json()}")
```

### 接口兼容性验证
```python
from daip_live.core.interfaces import IModelProvider

def validate_provider(provider: IModelProvider):
    # 验证接口方法是否可用
    assert hasattr(provider, 'generate')
    assert hasattr(provider, 'embed')
```

## ⚠️ 性能问题

### 高内存使用
- **检查**: 大量事件对象的创建
- **解决方案**: 优化事件生成频率和大小

### 序列化慢
- **检查**: 复杂模型的序列化
- **解决方案**: 简化模型结构或使用更高效的序列化方法

## 🔍 调试技巧

### Pydantic模型调试
```python
from pydantic import ValidationError

try:
    model = MyModel(**data)
except ValidationError as e:
    print(e.json())
    print(e.errors())
```

### 事件流调试
```python
# 调试事件流
async def debug_event_stream(executor, goal):
    async for event in executor.chat_run(goal):
        print(f"Event: {type(event).__name__}")
        yield event
```

## 📞 支持信息
当寻求支持时，请提供：
1. 完整的错误消息和堆栈跟踪
2. 相关模型或接口的定义
3. 输入数据的示例
4. 所使用的Python和Pydantic版本

---
> **需要集成信息？** 查看 [P0_core_interfaces_integration.md](P0_core_interfaces_integration.md)  
> **需要API详情？** 查看 [P0_core_interfaces_api.md](P0_core_interfaces_api.md)