# P4 角色与工具管理 - 故障排除 (P4 Role & Tool Management - Troubleshooting)

## 🚨 常见问题

### 1. 工具执行失败
**症状**: 工具无法执行或返回错误
**可能原因**: 
- 参数验证失败
- 权限不足
- 工具实现错误

**解决方案**:
```python
# 检查工具可用性
async def check_tool_availability(tool_manager: ToolManager, tool_name: str):
    if tool_name not in tool_manager.list_available_tools():
        print(f"工具 {tool_name} 未注册")
        return False
    
    # 获取工具模式
    schema = tool_manager.get_tool_schema(tool_name)
    print(f"工具模式: {schema}")
    return True
```

### 2. 权限请求循环
**症状**: UI持续显示权限请求对话框
**可能原因**: 
- 未正确处理ToolPermissionRequest异常
- 确认标志未正确传递

**解决方案**:
```python
# 正确处理权限请求
async def safe_tool_execution(tool_manager: ToolManager, tool_name: str, args: Dict, context):
    try:
        return await tool_manager.execute_tool(tool_name, args, context)
    except ToolPermissionRequest as e:
        # 在UI中获取用户确认
        user_decision = await ui.get_permission_decision(e.tool_name, e.args)
        
        if user_decision == "allow":
            # 重新执行并确认
            return await tool_manager.execute_tool(
                e.tool_name, e.args, context, confirmation_granted=True
            )
        else:
            raise ToolPermissionError(f"用户拒绝执行工具: {e.tool_name}")
```

## 🔧 诊断工具

### 工具注册检查
```python
def debug_tool_registration(tool_manager: ToolManager):
    print("注册的工具:")
    for tool_name in tool_manager.list_available_tools():
        schema = tool_manager.get_tool_schema(tool_name)
        print(f"  - {tool_name}: {schema}")
```

### 权限配置验证
```python
def validate_permission_config(config: ToolPermissionConfig):
    print(f"默认策略: {config.default}")
    for tool, permission in config.tools.items():
        print(f"  {tool}: {permission}")
```

## ⚠️ 性能问题

### 工具执行延迟
- **检查**: 6阶段管道是否有瓶颈
- **解决方案**: 优化验证和权限检查

### 权限检查慢
- **检查**: 频繁的权限决策
- **解决方案**: 实现权限缓存

## 🔍 调试技巧

### 工具执行调试
```python
async def debug_tool_execution(tool_manager: ToolManager, name: str, args: Dict, context):
    print(f"执行工具: {name}")
    print(f"参数: {args}")
    
    try:
        result = await tool_manager.execute_tool(name, args, context)
        print(f"结果: {result}")
        return result
    except Exception as e:
        print(f"执行失败: {e}")
        raise
```

### 装饰器注册调试
```python
from daip_live.p4_role_manager_tools.decorators import tool

# 调试装饰器注册
def debug_tool_decorator():
    @tool
    def test_tool(x: int, y: str = "default") -> str:
        """测试工具"""
        return f"x={x}, y={y}"
    
    print("工具注册成功")
    print(f"工具模式: {test_tool._tool_schema}")
```

## 📞 支持信息
当寻求支持时，请提供：
1. 完整的错误消息和堆栈跟踪
2. 工具名称和参数
3. 权限配置信息
4. 涉及的代码示例

---
> **需要集成信息？** 查看 [P4_role_manager_tools_integration.md](P4_role_manager_tools_integration.md)  
> **需要API详情？** 查看 [P4_role_manager_tools_api.md](P4_role_manager_tools_api.md)