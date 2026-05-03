# P4 角色与工具管理 - API参考 (P4 Role & Tool Management - API Reference)

## 📋 核心类与方法

### RoleManager
```python
class RoleManager:
    def get_role_by_name(self, role_name: str) -> Optional[Role]:
        """根据名称获取角色"""
    
    def load_roles_from_directory(self, directory: str) -> List[Role]:
        """从目录加载角色"""
    
    def validate_role_config(self, config: Dict) -> bool:
        """验证角色配置"""
```

### ToolManager
```python
class ToolManager:
    async def execute_tool(self, name: str, args: Dict, session_context: SessionContext, 
                          confirmation_granted: bool = False) -> Any:
        """执行工具（6阶段安全管道）"""
    
    def register_tool(self, func: Callable, name: str = None) -> None:
        """注册工具"""
    
    def get_tool_schema(self, name: str) -> Dict:
        """获取工具模式"""
    
    def list_available_tools(self) -> List[str]:
        """列出可用工具"""
```

## 🔧 @tool 装饰器

### 工具注册
```python
from daip_live.p4_role_manager_tools.decorators import tool

@tool
def file_operation(path: str, operation: str) -> str:
    """
    执行文件操作
    :param path: 文件路径
    :param operation: 操作类型
    """
    # 实现工具功能
    pass
```

### 权限配置
```python
@tool(permission="ask")  # 需要用户确认
def shell_command(command: str) -> str:
    """执行shell命令"""
    pass
```

## 🧩 数据模型

### 角色模型
```python
from pydantic import BaseModel
from typing import List

class Role(BaseModel):
    name: str
    persona: str
    tools: List[str]
    system_prompt: str
    model_config: Dict[str, Any]
```

### 工具权限配置
```python
class ToolPermissionConfig(BaseModel):
    default: Literal["allow", "deny", "ask"] = "ask"
    tools: Dict[str, Literal["allow", "deny", "ask"]] = {}
```

### 会话上下文
```python
class SessionContext(BaseModel):
    session_id: str
    recently_read_resources: Set[str] = set()
    user_preferences: Dict[str, Any] = {}
```

## 🔒 6阶段安全执行管道

1. **发现阶段**: 查找工具
2. **输入验证**: 验证参数
3. **前置条件检查**: Write-After-Read检查
4. **权限检查**: 根据配置决定执行策略
5. **执行阶段**: 执行工具
6. **结果格式化**: 格式化结果

---
> **需要实现详情？** 查看 [P4_role_manager_tools_detailed.md](P4_role_manager_tools_detailed.md)  
> **需要集成指南？** 查看 [P4_role_manager_tools_integration.md](P4_role_manager_tools_integration.md)