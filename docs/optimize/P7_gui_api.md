# P7 GUI界面 - API参考 (P7 GUI Interface - API Reference)

## 📋 核心类与方法

### GUI应用主类
```python
class DAIP_GUI:
    def run(self) -> None:
        """启动GUI应用"""
    
    def run_server(self, host: str = "127.0.0.1", port: int = 8501) -> None:
        """启动GUI服务器"""
```

### API端点
```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """聊天接口"""
    pass

@app.get("/api/status")
async def status_endpoint():
    """系统状态接口"""
    pass

@app.post("/api/debate/start")
async def start_debate_endpoint(request: DebateRequest):
    """启动辩论接口"""
    pass
```

## 🔧 Streamlit组件

### UI组件
- `st.chat_message`: 聊天消息组件
- `st.chat_input`: 聊天输入组件
- `st.sidebar`: 侧边栏组件
- `st.status`: 状态显示组件

### 会话状态管理
```python
import streamlit as st

def get_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_status" not in st.session_state:
        st.session_state.agent_status = "idle"
    return st.session_state
```

## 🧩 数据模型

### 请求/响应模型
```python
from pydantic import BaseModel
from typing import List, Dict, Optional

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    content: str
    session_id: str
    timestamp: datetime

class DebateRequest(BaseModel):
    topic: str
    roles: List[str]
    rounds: int
```

## 🔌 复用的外部接口

### 依赖的外部组件
- `Streamlit`: Web UI框架
- `FastAPI`: API框架
- `P5 AgentExecutor`: 代理引擎
- `P6 CLI`: 命令行接口

## 📡 流式响应
- **SSE**: Server-Sent Events支持
- **WebSocket**: 实时通信支持
- **异步生成器**: 流式数据传输

---
> **需要实现详情？** 查看 [P7_gui_detailed.md](P7_gui_detailed.md)  
> **需要集成指南？** 查看 [P7_gui_integration.md](P7_gui_integration.md)