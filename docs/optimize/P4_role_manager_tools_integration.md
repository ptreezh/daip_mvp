# P4 角色与工具管理 - 集成指南 (P4 Role & Tool Management - Integration Guide)

## 🔗 与其他模块的集成

### 与P5代理引擎集成
```python
# P5使用P4的工具执行功能
from daip_live.p4_role_manager_tools.tool_manager import ToolManager

class AgentExecutor:
    def __init__(self, tool_manager: ToolManager):
        self.tool_manager = tool_manager
    
    async def execute_agent_action(self, action_name: str, action_args: Dict):
        # 通过6阶段管道安全执行工具
        result = await self.tool_manager.execute_tool(
            name=action_name,
            args=action_args,
            session_context=self.session_context
        )
        return result
```

### 与P6 CLI/TUI界面集成
```python
# P6处理工具权限请求
from daip_live.p4_role_manager_tools.models import ToolPermissionRequest

async def handle_permission_request(tui_app, tool_request: ToolPermissionRequest):
    # 在UI中显示权限请求
    user_response = await tui_app.show_permission_dialog(
        tool_name=tool_request.tool_name,
        args=tool_request.args
    )
    
    # 重新调用工具执行（带确认）
    if user_response == "allow":
        result = await tool_manager.execute_tool(
            name=tool_request.tool_name,
            args=tool_request.args,
            session_context=session_context,
            confirmation_granted=True
        )
```

## 🔄 工具执行流程

### 标准工具执行
```python
# 完整的工具执行流程
async def complete_tool_execution(tool_manager: ToolManager, session_context: SessionContext):
    # 1. 验证工具可用性
    available_tools = tool_manager.list_available_tools()
    print(f"可用工具: {available_tools}")
    
    # 2. 执行工具（通过6阶段管道）
    result = await tool_manager.execute_tool(
        name="file_operation",
        args={"path": "/tmp/test.txt", "operation": "read"},
        session_context=session_context
    )
    
    return result
```

## 🔌 使用示例

### 工具注册
```python
from daip_live.p4_role_manager_tools.decorators import tool
from daip_live.p4_role_manager_tools.tool_manager import ToolManager

# 注册新工具
@tool
def search_web(query: str, num_results: int = 5) -> List[Dict]:
    """
    搜索网页
    :param query: 搜索查询
    :param num_results: 结果数量
    """
    # 实现搜索功能
    return [{"title": "Example", "url": "http://example.com"}]

# 获取工具管理器实例
tool_manager = container.tool_manager()

# 工具已自动注册
print(tool_manager.list_available_tools())
```

### 角色配置
```yaml
# roles/pro_arguer.yaml
name: "pro_arguer"
persona: "你是一个支持观点的辩论者..."
tools:
  - web_search
  - document_analysis
system_prompt: "当参与辩论时，你应当..."
model_config:
  model: "gpt-4o"
  temperature: 0.8
```

### 权限配置
```python
from daip_live.p4_role_manager_tools.models import ToolPermissionConfig

permission_config = ToolPermissionConfig(
    default="ask",  # 默认需要询问
    tools={
        "file_operation": "ask",    # 文件操作需要询问
        "web_search": "allow",      # Web搜索允许
        "shell_command": "deny"     # Shell命令拒绝
    }
)
```

## ⚡ 性能考虑
- **工具发现**: 缓存工具注册表
- **权限检查**: 缓存权限决策
- **参数验证**: 预编译验证模式

## 🐛 常见集成问题
- **循环导入**: 使用依赖注入避免
- **权限阻塞**: 确保UI能处理权限请求
- **工具执行超时**: 设置适当的超时值

---
> **需要API详情？** 查看 [P4_role_manager_tools_api.md](P4_role_manager_tools_api.md)  
> **需要实现详情？** 查看 [P4_role_manager_tools_detailed.md](P4_role_manager_tools_detailed.md)