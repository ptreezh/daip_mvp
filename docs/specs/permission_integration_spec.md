# 权限系统集成规范文档

## 文档信息
- **文档编号**: DAIP-PERMISSION-INTEGRATION-001
- **版本**: v1.0
- **日期**: 2025-09-19
- **作者**: DAIP-LIVE Team
- **状态**: 草案

## 变更记录
| 版本 | 日期 | 作者 | 变更描述 |
|------|------|------|----------|
| 1.0 | 2025-09-19 | DAIP-LIVE Team | 初始版本，定义权限系统集成规范 |

## 1. 引言

### 1.1 目的
本文档定义了权限系统与DAIP-LIVE核心组件（AgentExecutor、TUI界面、工具管理器）的集成规范，确保权限ask模式能够无缝集成到现有架构中。

### 1.2 范围
- 权限系统与AgentExecutor的集成
- 权限系统与TUI界面的集成  
- 权限系统与工具管理器的集成
- 集成测试策略和验收标准

### 1.3 参考文档
- [权限用户响应规范](permission_user_response_spec.md)
- [系统架构文档](../SYSTEM_ARCHITECTURE.md)
- [主控需求文档](../MAIN_CONTROL_DOCUMENT.md)

## 2. 集成架构设计

### 2.1 总体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AgentExecutor                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                Permission Manager                    │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │           Permission Integration               │  │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────┐│  │  │
│  │  │  │Tool Manager │  │User Response│  │TUI      ││  │  │
│  │  │  │ Integration │  │  Collector  │  │Interface││  │  │
│  │  │  └─────────────┘  └─────────────┘  └─────────┘│  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │         Permission Rules Engine               │  │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────┐│  │  │
│  │  │  │ Rule Store  │  │  Decision   │  │  Cache  ││  │  │
│  │  │  │             │  │   Engine    │  │         ││  │  │
│  │  │  └─────────────┘  └─────────────┘  └─────────┘│  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Services                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Session   │  │   Memory    │  │   Config    │        │
│  │   Manager   │  │   Service   │  │   Service   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 集成接口定义

#### 2.2.1 PermissionManager接口
```python
class PermissionManager:
    """权限管理器 - 核心集成接口"""
    
    async def check_permission(
        self, 
        tool_name: str, 
        args: Dict[str, Any],
        session_context: SessionContext
    ) -> PermissionResult:
        """检查工具权限"""
        pass
    
    async def request_permission(
        self, 
        request: PermissionRequestEvent
    ) -> PermissionResponse:
        """请求用户权限"""
        pass
    
    def get_permission_status(self, tool_name: str) -> str:
        """获取工具权限状态"""
        pass
    
    def update_permission_rule(
        self, 
        tool_name: str, 
        permission: Literal["allow", "deny", "ask"]
    ) -> None:
        """更新权限规则"""
        pass
```

## 3. 组件集成规范

### 3.1 AgentExecutor集成

#### 3.1.1 集成点
- **工具调用前检查**: 在工具执行前调用权限检查
- **权限请求处理**: 处理用户权限请求和响应
- **状态管理**: 维护权限状态与会话状态同步

#### 3.1.2 集成流程
```python
# AgentExecutor中的权限检查流程
async def execute_tool_with_permission(self, tool_name: str, args: Dict[str, Any]):
    # 1. 检查权限
    permission_result = await self.permission_manager.check_permission(
        tool_name, args, self.session_context
    )
    
    if permission_result.granted:
        # 权限已授予，执行工具
        return await self.tool_manager.execute_tool(tool_name, args)
    elif permission_result.response == PermissionResponse.DENY:
        # 权限被拒绝
        raise ToolPermissionError(f"Permission denied for {tool_name}")
    elif permission_result.response == PermissionResponse.ASK:
        # 需要用户确认
        permission_response = await self.permission_manager.request_permission(
            PermissionRequestEvent(tool_name=tool_name, args=args)
        )
        # 根据用户响应决定是否执行工具
        if permission_response == PermissionResponse.GRANT:
            return await self.tool_manager.execute_tool(tool_name, args)
        else:
            raise ToolPermissionError(f"Permission denied by user for {tool_name}")
```

#### 3.1.3 TDD测试用例
```python
# 测试用例1: 权限允许的工具执行
async def test_tool_execution_with_permission_allowed():
    # Given: 工具权限设置为allow
    # When: 执行工具
    # Then: 工具成功执行

# 测试用例2: 权限拒绝的工具执行
async def test_tool_execution_with_permission_denied():
    # Given: 工具权限设置为deny
    # When: 执行工具
    # Then: 抛出ToolPermissionError

# 测试用例3: 权限询问模式
async def test_tool_execution_with_permission_ask():
    # Given: 工具权限设置为ask
    # When: 执行工具且用户授予权限
    # Then: 工具成功执行
    
# 测试用例4: 权限询问用户拒绝
async def test_tool_execution_with_permission_ask_user_denies():
    # Given: 工具权限设置为ask
    # When: 执行工具且用户拒绝权限
    # Then: 抛出ToolPermissionError
```

### 3.2 TUI界面集成

#### 3.2.1 集成点
- **权限请求显示**: 在TUI界面显示权限请求
- **用户输入收集**: 收集用户对权限请求的响应
- **状态反馈**: 显示权限处理状态和结果

#### 3.2.2 集成接口
```python
class PermissionTUIIntegration:
    """TUI权限集成"""
    
    def __init__(self, tui_interface: PermissionTUIInterface):
        self.tui_interface = tui_interface
    
    async def show_permission_request(self, request: PermissionRequestEvent) -> None:
        """显示权限请求"""
        await self.tui_interface.show_permission_request(request)
    
    async def get_user_response(self, timeout: float = 30.0) -> PermissionResponse:
        """获取用户响应"""
        return await self.tui_interface.get_user_response(timeout)
    
    async def show_permission_result(self, result: PermissionResult) -> None:
        """显示权限结果"""
        # 在TUI界面显示权限处理结果
        pass
```

#### 3.2.3 TDD测试用例
```python
# 测试用例1: 权限请求界面显示
async def test_permission_request_display():
    # Given: 权限请求事件
    # When: 显示权限请求界面
    # Then: 界面正确显示权限信息

# 测试用例2: 用户响应收集
async def test_user_response_collection():
    # Given: 权限请求界面已显示
    # When: 用户输入有效响应
    # Then: 正确收集用户响应

# 测试用例3: 超时处理
async def test_permission_request_timeout():
    # Given: 权限请求界面显示
    # When: 用户超时未响应
    # Then: 返回默认拒绝响应
```

### 3.3 工具管理器集成

#### 3.3.1 集成点
- **权限检查前置**: 在工具执行前进行权限检查
- **权限异常处理**: 处理权限相关的异常情况
- **规则同步**: 与权限规则存储同步

#### 3.3.2 集成修改
```python
# 在ToolManager中的修改
class ToolManager:
    def __init__(self, permission_manager: PermissionManager):
        self.permission_manager = permission_manager
    
    def execute_tool(self, name: str, args: Dict[str, Any], 
                    session_context: SessionContext, 
                    confirmation_granted: bool = False) -> Any:
        
        # 新增：权限检查前置
        permission_status = self.permission_manager.check_tool_permission(name, args)
        
        if permission_status == "deny":
            raise ToolPermissionError(f"Tool '{name}' is denied by policy.")
        elif permission_status == "ask" and not confirmation_granted:
            raise ToolPermissionRequest(tool_name=name, args=args)
        
        # 原有工具执行逻辑...
```

## 4. 数据流设计

### 4.1 权限检查流程
```
AgentExecutor → PermissionManager.check_permission() → 
├── 规则引擎检查 → 返回结果
├── 需要用户确认 → PermissionManager.request_permission() →
│   ├── TUI界面显示 → 用户输入收集 → 响应处理 → 结果返回
│   └── 超时处理 → 默认拒绝
└── 缓存更新 → 结果存储
```

### 4.2 用户响应流程
```
用户输入 → TUI界面 → PermissionTUIInterface → 
UserResponseCollector → ResponseProcessor → 
PermissionResult → PermissionManager → AgentExecutor
```

## 5. 错误处理

### 5.1 异常类型
```python
class PermissionIntegrationError(DAIPError):
    """权限集成基础异常"""
    pass

class PermissionCheckError(PermissionIntegrationError):
    """权限检查失败"""
    pass

class PermissionRequestError(PermissionIntegrationError):
    """权限请求处理失败"""
    pass

class PermissionTimeoutError(PermissionIntegrationError):
    """权限请求超时"""
    pass
```

### 5.2 错误恢复策略
- **超时恢复**: 默认拒绝，记录日志
- **网络错误**: 重试机制，最大重试次数
- **用户输入错误**: 重新显示界面，错误提示
- **系统错误**: 降级到安全模式，默认拒绝

## 6. 性能要求

### 6.1 响应时间
- 权限检查: < 100ms
- 权限请求显示: < 500ms
- 用户响应处理: < 200ms
- 超时检测精度: ±100ms

### 6.2 资源使用
- 内存使用: < 10MB (100个并发请求)
- CPU使用: < 5% (空闲状态)
- 并发支持: 100个并发权限请求

## 7. 安全要求

### 7.1 权限安全
- 默认拒绝策略
- 权限规则持久化
- 权限变更审计
- 会话隔离

### 7.2 输入安全
- 输入验证和清理
- 防止注入攻击
- 长度限制
- 字符过滤

## 8. 测试策略

### 8.1 单元测试
- 每个集成点的独立测试
- 模拟外部依赖
- 边界条件测试
- 错误场景测试

### 8.2 集成测试
- 端到端权限流程测试
- 多组件协作测试
- 并发场景测试
- 性能基准测试

### 8.3 验收标准
- 所有TDD测试用例通过
- 代码覆盖率 > 90%
- 性能指标达标
- 安全扫描通过

## 9. 实施计划

### 9.1 第一阶段：核心集成
1. PermissionManager基础实现
2. AgentExecutor集成
3. 基础TDD测试用例

### 9.2 第二阶段：界面集成
1. TUI界面集成
2. 用户响应收集
3. 显示和交互测试

### 9.3 第三阶段：高级功能
1. 并发处理
2. 性能优化
3. 高级错误处理

### 9.4 第四阶段：完善和优化
1. 完整测试覆盖
2. 性能调优
3. 文档完善

## 10. 风险评估

### 10.1 技术风险
- **异步处理复杂性**: 中风险，需要仔细处理并发
- **性能瓶颈**: 低风险，可通过优化解决
- **集成兼容性**: 中风险，需要与现有系统协调

### 10.2 缓解措施
- 充分的单元测试和集成测试
- 渐进式实施，分阶段验证
- 性能监控和基准测试
- 代码审查和安全审计

## 11. 附录

### 11.1 术语表
- **PermissionManager**: 权限管理器
- **TUI**: 文本用户界面
- **AgentExecutor**: 代理执行器
- **TDD**: 测试驱动开发

### 11.2 相关文档
- [权限系统设计文档](permission_design.md)
- [TUI界面规范](../tui_cli_specification.md)
- [AgentExecutor架构](../p5_agent_engine/agent_executor_design.md)