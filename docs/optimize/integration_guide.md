# 集成指南 (Integration Guide)

## 🔌 系统集成 (System Integration)

### 与外部AI模型集成

#### 1. 通过LiteLLM集成新模型
```python
# 示例: 添加新模型到LiteLLM配置
from daip_live.model_provider.provider import LiteLLMProvider

# 在配置文件中添加新模型
model_config = {
    "model": "your-custom-model",
    "api_base": "https://your-api-endpoint.com/v1",
    "api_key": "your-api-key"
}

provider = LiteLLMProvider(model_config)
```

**相关文件**:
- `src/daip_live/model_provider/provider.py`

#### 2. 直接API集成
如果模型不支持LiteLLM，可实现自定义模型提供者：
```python
from daip_live.core.interfaces import ModelProvider

class CustomModelProvider(ModelProvider):
    def __init__(self, config):
        self.config = config

    async def generate(self, prompt: str, **kwargs):
        # 实现模型调用逻辑
        pass
```

### 与外部服务集成

#### 1. 数据库集成
```python
# 示例: 添加新的向量数据库
from daip_live.core.interfaces import VectorDatabase

class CustomVectorDB(VectorDatabase):
    def __init__(self, config):
        self.config = config

    async def search(self, query_vector, top_k=5):
        # 实现向量搜索逻辑
        pass
```

**相关文件**:
- `src/daip_live/p1_data_persistence/database.py`

#### 2. 工具集成
```python
# 示例: 添加新工具到系统
from daip_live.basic_tools.core import Tool

class CustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="A custom tool for specific functionality",
            parameters={
                "param1": {"type": "string", "description": "First parameter"}
            }
        )

    async def execute(self, **kwargs):
        # 实现工具逻辑
        return {"result": "success"}
```

**相关文件**:
- `src/daip_live/basic_tools/core.py`

## 🧩 模块扩展 (Module Extension)

### 新功能模块开发

#### 1. 创建新模块
在 `src/daip_live/` 目录下创建新模块目录，例如 `p9_custom_module/`：

```
src/daip_live/p9_custom_module/
├── __init__.py
├── core.py          # 核心功能实现
├── models.py        # 数据模型
├── interfaces.py    # 接口定义
└── integration.py   # 与其他模块的集成
```

#### 2. 遵循模块化原则
- 使用接口隔离依赖
- 保持单一职责原则
- 通过容器进行依赖注入

### 与现有模块集成

#### 1. 依赖注入容器配置
```python
# 在 container.py 中添加新组件
from dependency_injector import containers, providers
from .p9_custom_module.core import CustomModule

class Container(containers.DeclarativeContainer):
    # ... 其他组件
    
    custom_module = providers.Factory(
        CustomModule,
        # 传入依赖
        dependency=your_dependency
    )
```

**相关文件**:
- `src/daip_live/container.py`

#### 2. 意图识别扩展
```python
# 在意图识别器中添加新意图
from daip_live.agent_engine.enhanced_intent_recognizer import Intent

# 添加新意图类型
CUSTOM_TOOL_INTENT = "custom_tool_action"

# 扩展意图识别逻辑
def recognize_custom_intent(text: str) -> Intent:
    # 实现自定义意图识别
    pass
```

**相关文件**:
- `src/daip_live/agent_engine/enhanced_intent_recognizer.py`

## 🌐 API集成 (API Integration)

### REST API端点
默认REST API通过FastAPI提供，可扩展：

```python
from fastapi import FastAPI, APIRouter
from daip_live.container import Container

# 创建自定义路由
custom_router = APIRouter()

@custom_router.get("/custom-endpoint")
async def custom_endpoint():
    # 实现自定义API逻辑
    pass

# 将路由添加到主应用
app = FastAPI()
app.include_router(custom_router)
```

**相关文件**:
- `src/daip_live/web_api/main.py`

### WebSocket连接
对于实时功能，可以使用WebSocket：

```python
from fastapi import WebSocket
import json

@custom_router.websocket("/ws/custom")
async def websocket_custom_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # 处理WebSocket消息
            response = process_custom_data(data)
            await websocket.send_text(json.dumps(response))
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()
```

## 🧪 测试集成 (Testing Integration)

### 单元测试
为新功能编写单元测试：

```python
# 示例测试文件: tests/unit/test_custom_module.py
import pytest
from daip_live.p9_custom_module.core import CustomModule

@pytest.mark.asyncio
async def test_custom_module():
    module = CustomModule()
    result = await module.execute("test input")
    assert result is not None
```

### 集成测试
测试模块间的交互：

```python
# 示例集成测试
async def test_custom_module_integration():
    # 通过容器获取组件
    container = Container()
    custom_module = container.custom_module()
    other_module = container.other_module()
    
    # 验证集成
    result = await custom_module.process_with_other(other_module)
    assert result.success
```

## 🔄 持续集成 (Continuous Integration)

### 配置CI/CD
在 `.github/workflows/` 中添加工作流：

```yaml
name: Test Custom Module

on:
  push:
    paths:
      - 'src/daip_live/p9_custom_module/**'
      - 'tests/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest pytest-asyncio
    - name: Run tests
      run: pytest tests/unit/test_custom_module.py
```

## 📊 监控集成 (Monitoring Integration)

### 性能监控
集成性能监控：

```python
from daip_live.cli.utils.performance_monitor import monitor

@monitor("custom_module", ["execution_time", "resource_usage"])
async def monitored_custom_function():
    # 实现监控的函数
    pass
```

**相关文件**:
- `src/daip_live/cli/utils/performance_monitor.py`

### 日志集成
统一日志记录：

```python
import logging

logger = logging.getLogger(__name__)

async def custom_function():
    logger.info("Starting custom function execution")
    try:
        result = await execute_logic()
        logger.info("Custom function completed successfully")
        return result
    except Exception as e:
        logger.error(f"Custom function failed: {e}")
        raise
```