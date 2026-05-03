# P6 CLI/TUI界面 - API参考 (P6 CLI/TUI Interface - API Reference)

## 📋 核心类与方法

### DAIP_TUI
```python
class DAIP_TUI(App):
    def run(self) -> None:
        """启动TUI应用"""
    
    async def run_async(self) -> None:
        """异步启动TUI应用"""
    
    def add_event_consumer(self, consumer: AsyncGenerator[AgentEvent, None]) -> None:
        """添加事件消费者"""
    
    def handle_user_input(self, input_text: str) -> None:
        """处理用户输入"""
```

### CLI命令结构
```python
import typer

app = typer.Typer()

@app.command("run")
def run_tui():
    """启动TUI界面"""
    pass

@debate_app.command("start")
def debate_start(topic: str, roles: str, rounds: int):
    """启动辩论"""
    pass
```

## 🔧 TUI组件

### 核心组件
- `RichLog`: 用于显示对话内容
- `Input`: 用于用户输入
- `Footer`: 显示快捷键信息
- `Header`: 显示应用标题

### 事件处理
```python
class DAIP_TUI(App):
    def on_input_submitted(self, message: Input.Submitted) -> None:
        """处理输入提交事件"""
    
    async def handle_agent_events(self, agent_events: AsyncGenerator[AgentEvent, None]) -> None:
        """处理代理事件流"""
```

## 🧩 数据模型

### TUI特定模型
```python
from pydantic import BaseModel

class TUIState(BaseModel):
    current_mode: str  # NORMAL, ASSISTANT_ACTIVE等
    clipboard_content: str
    last_command: str
    system_status: str
```

## 🔌 复用的外部接口

### 依赖的外部组件
- `Textual`: TUI框架
- `Typer`: CLI框架
- `P5 AgentExecutor`: 代理引擎
- `P4 ToolManager`: 工具管理

## 📡 事件处理
- **用户输入**: 处理命令和文本输入
- **代理事件**: 响应AgentEvent流
- **系统事件**: 处理状态变化和通知

---
> **需要实现详情？** 查看 [P6_cli_tui_detailed.md](P6_cli_tui_detailed.md)  
> **需要集成指南？** 查看 [P6_cli_tui_integration.md](P6_cli_tui_integration.md)