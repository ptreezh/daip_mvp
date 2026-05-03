# P6 CLI/TUI界面 - 集成指南 (P6 CLI/TUI Interface - Integration Guide)

## 🔗 与其他模块的集成

### 与P5代理引擎集成
```python
# TUI消费P5的事件流
from daip_live.p5_agent_engine.executor import AgentExecutor

class DAIP_TUI:
    async def start_agent_session(self, goal: str):
        # 获取代理执行器
        agent_executor = container.agent_executor()
        
        # 运行代理并消费事件流
        async for event in agent_executor.chat_run(goal):
            await self.handle_agent_event(event)
```

### 与P4工具管理集成
```python
# TUI处理工具权限请求
from daip_live.p4_role_manager_tools.models import ToolPermissionRequest

class DAIP_TUI:
    async def handle_agent_event(self, event: AgentEvent):
        if event.type == "permission_request":
            # 显示权限请求对话框
            user_decision = await self.show_permission_dialog(
                event.tool_name, 
                event.args
            )
            
            # 通知代理关于用户决定
            await self.handle_permission_response(
                event.tool_name, 
                event.args, 
                user_decision
            )
```

## 🔄 事件流处理

### 事件类型处理
```python
# TUI事件处理模式
async def handle_different_event_types(tui: DAIP_TUI, event: AgentEvent):
    if isinstance(event, ThoughtEvent):
        tui.display_thought(event.content)
    elif isinstance(event, ToolCallEvent):
        tui.display_tool_call(event.tool_name, event.args)
    elif isinstance(event, FinalResponseEvent):
        tui.display_final_response(event.content)
    elif isinstance(event, ErrorEvent):
        tui.display_error(event.message)
```

## 🔌 使用示例

### 启动TUI应用
```python
from daip_live.p6_cli_tui.tui import DAIP_TUI

# 启动TUI
def main():
    tui = DAIP_TUI()
    tui.run()  # 阻塞运行

# 或异步运行
async def async_main():
    tui = DAIP_TUI()
    await tui.run_async()
```

### CLI命令实现
```python
from daip_live.p6_cli_tui.commands.debate import debate_start

@app.command("debate")
def debate_cli(
    topic: str = typer.Argument(..., help="辩论主题"),
    roles: str = typer.Option("pro_arguer,con_arguer", help="参与辩论的角色"),
    rounds: int = typer.Option(1, help="辩论轮次")
):
    """启动辩论功能"""
    # 集成P8辩论系统
    debate_manager = container.debate_manager()
    
    # 执行辩论并显示结果
    for event in debate_manager.run_debate(topic, roles, rounds):
        print(event)
```

### 复制功能实现
```python
class DAIP_TUI:
    def copy_to_clipboard(self, content: str = None):
        """复制内容到剪贴板"""
        import pyperclip
        
        if content is None:
            # 复制整个对话历史
            content = self.get_full_conversation_text()
        
        pyperclip.copy(content)
        self.notify("已复制到剪贴板")
    
    def copy_recent_lines(self, num_lines: int = 20):
        """复制最近的对话行"""
        recent_content = self.get_recent_conversation_lines(num_lines)
        self.copy_to_clipboard(recent_content)
```

## ⚡ 性能考虑
- **事件处理**: 优化事件显示性能
- **UI响应**: 遶免长时间操作阻塞UI
- **内存管理**: 清理旧的对话历史

## 🐛 常见集成问题
- **事件流中断**: 确保正确处理异步生成器
- **UI阻塞**: 遌意长操作的异步处理
- **状态同步**: 保持UI与后端状态一致

---
> **需要API详情？** 查看 [P6_cli_tui_api.md](P6_cli_tui_api.md)  
> **需要实现详情？** 查看 [P6_cli_tui_detailed.md](P6_cli_tui_detailed.md)