# AgentExecutor权限集成规范文档

## 文档信息
- **文档编号**: DAIP-AGENT-PERMISSION-INTEGRATION-001
- **版本**: v1.0
- **日期**: 2025-09-19
- **作者**: DAIP-LIVE Team
- **状态**: 草案
- **遵循原则**: 文档先行、规范先行、契约先行、TDD驱动

## 变更记录
| 版本 | 日期 | 作者 | 变更描述 |
|------|------|------|----------|
| 1.0 | 2025-09-19 | DAIP-LIVE Team | 初始版本，定义AgentExecutor权限集成规范 |

## 1. 引言

### 1.1 目的
本文档严格遵循工作纪律，定义AgentExecutor与PermissionManager的实际集成规范，确保权限ask模式能够无缝集成到Agent执行流程中。

### 1.2 范围
- AgentExecutor中权限检查的具体集成点
- ToolPermissionRequest异常的精确定义和处理
- 权限检查与工具执行流程的完整集成
- 端到端集成测试的详细规范

### 1.3 遵循原则
- **文档先行**: 先有规范文档，后有代码实现
- **规范先行**: 严格按照BMAD kiro's spec规范
- **契约先行**: 明确的接口契约和行为定义
- **TDD驱动**: 测试用例定义在实现之前

## 2. 集成架构设计

### 2.1 集成点分析

```
AgentExecutor.execute_tool() 调用流程:
┌─────────────────────────────────────────────────────────────┐
│                    AgentExecutor                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              execute_tool_with_permission()         │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ 1. PermissionManager.check_permission()       │  │  │
│  │  │    ├── 检查缓存                                │  │  │
│  │  │    ├── 规则引擎判断                            │  │  │
│  │  │    └── 用户交互处理                            │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │                                                      │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ 2. 权限结果处理                                │  │  │
│  │  │    ├── granted=True → 执行工具                 │  │  │
│  │  │    ├── granted=False → 抛出异常                │  │  │
│  │  │    └── 需要用户确认 → 处理交互                 │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    工具实际执行或异常抛出
```

### 2.2 集成接口定义

#### 2.2.1 AgentExecutor修改接口

```python
class AgentExecutor:
    """Agent执行器 - 权限集成版本"""
    
    def __init__(self, permission_manager: PermissionManager):
        self.permission_manager = permission_manager
        self._current_permission_request: Optional[PermissionRequestEvent] = None
    
    async def execute_tool_with_permission(
        self, 
        tool_name: str, 
        args: Dict[str, Any],
        session_context: SessionContext,
        confirmation_granted: bool = False
    ) -> Any:
        """
        带权限检查的工具执行
        
        Args:
            tool_name: 工具名称
            args: 工具参数
            session_context: 会话上下文
            confirmation_granted: 是否已经获得用户确认
            
        Returns:
            Any: 工具执行结果
            
        Raises:
            ToolPermissionError: 权限被拒绝
            ToolPermissionRequest: 需要用户权限确认
        """
        pass
```

#### 2.2.2 权限检查流程契约

```python
# 权限检查前置条件
PRECONDITIONS = {
    "tool_exists": "工具必须在工具管理器中注册",
    "args_valid": "工具参数必须通过输入验证",
    "session_active": "会话必须处于活动状态"
}

# 权限检查后置条件  
POSTCONDITIONS = {
    "result_valid": "返回的PermissionResult必须有效",
    "state_consistent": "权限状态必须与工具执行状态一致",
    "cache_updated": "权限缓存必须正确更新"
}

# 异常处理契约
EXCEPTION_CONTRACTS = {
    "ToolPermissionError": "权限被拒绝时抛出，包含明确的拒绝原因",
    "ToolPermissionRequest": "需要用户确认时抛出，包含完整的请求信息",
    "TimeoutError": "权限请求超时时的处理策略"
}
```

## 3. 详细集成规范

### 3.1 权限检查前置流程

#### 3.1.1 工具发现阶段
```python
# 契约：工具必须存在且有效
if tool_name not in self.tool_manager._registry:
    raise ToolNotFoundError(f"Tool '{tool_name}' not found in registry")
```

#### 3.1.2 输入验证阶段  
```python
# 契约：输入必须符合工具模式定义
if input_schema:
    try:
        validated_args = input_schema.model_validate(args)
        args_to_execute = validated_args.model_dump()
    except ValidationError as e:
        raise ToolInputError(f"Input validation failed: {e}")
```

#### 3.1.3 权限检查阶段
```python
# 契约：权限检查必须完整执行
permission_result = await self.permission_manager.check_permission(
    tool_name=tool_name,
    args=args_to_execute,
    session_context=session_context
)
```

### 3.2 权限结果处理规范

#### 3.2.1 权限授予处理
```python
# 契约：权限授予时必须记录状态和原因
if permission_result.granted:
    logger.info(f"Permission granted for {tool_name}: {permission_result.reason}")
    # 继续工具执行流程
    return await self._execute_tool_internal(tool_name, args_to_execute)
```

#### 3.2.2 权限拒绝处理
```python
# 契约：权限拒绝时必须抛出明确的异常
if not permission_result.granted and permission_result.response == PermissionResponse.DENY:
    raise ToolPermissionError(
        f"Permission denied for tool '{tool_name}': {permission_result.reason}",
        tool_name=tool_name,
        args=args_to_execute,
        reason=permission_result.reason
    )
```

#### 3.2.3 权限询问处理
```python
# 契约：需要用户确认时必须抛出ToolPermissionRequest异常
if permission_result.response == PermissionResponse.ASK:
    self._current_permission_request = PermissionRequestEvent(
        tool_name=tool_name,
        args=args_to_execute,
        risk_level=self._assess_tool_risk(tool_name, args_to_execute)
    )
    raise ToolPermissionRequest(
        tool_name=tool_name,
        args=args_to_execute,
        request=self._current_permission_request
    )
```

### 3.3 异常处理规范

#### 3.3.1 ToolPermissionRequest异常定义
```python
class ToolPermissionRequest(DAIPError):
    """
    工具权限请求异常
    当工具需要用户权限确认时抛出
    """
    
    def __init__(self, tool_name: str, args: Dict[str, Any], request: PermissionRequestEvent):
        self.tool_name = tool_name
        self.args = args
        self.request = request
        super().__init__(
            f"Permission required for tool '{tool_name}' with args: {args}",
            tool_name=tool_name,
            args=args,
            request_id=request.request_id
        )
```

#### 3.3.2 异常处理流程
```python
# 异常处理契约
try:
    result = await self.execute_tool_with_permission(tool_name, args, session_context)
except ToolPermissionRequest as e:
    # 处理权限请求
    await self._handle_permission_request(e.request)
    # 重新执行（用户已确认）
    result = await self.execute_tool_with_permission(
        tool_name, args, session_context, confirmation_granted=True
    )
except ToolPermissionError as e:
    # 处理权限拒绝
    await self._handle_permission_denied(e)
    raise
```

## 4. TDD测试规范

### 4.1 测试策略
遵循TDD驱动原则，测试用例必须在实现之前定义。

### 4.2 核心集成测试用例

#### 4.2.1 基础权限集成测试
```python
class TestAgentExecutorPermissionIntegration:
    """AgentExecutor权限集成测试 - TDD规范"""
    
    @pytest.mark.asyncio
    async def test_agent_executor_permission_allowed(self):
        """
        测试AgentExecutor权限允许场景
        
        Given: 工具权限设置为allow
        When: AgentExecutor执行工具
        Then: 工具成功执行，无异常抛出
        """
        # Given: 设置工具权限为allow
        permission_manager = PermissionManager(user_queue)
        permission_manager.set_permission_rule("test_tool", "allow")
        
        agent_executor = AgentExecutor(permission_manager)
        
        # When: 执行工具
        result = await agent_executor.execute_tool_with_permission(
            "test_tool", {"param": "value"}, SessionContext()
        )
        
        # Then: 工具成功执行
        assert result is not None
        assert "success" in str(result).lower()
    
    @pytest.mark.asyncio
    async def test_agent_executor_permission_denied(self):
        """
        测试AgentExecutor权限拒绝场景
        
        Given: 工具权限设置为deny
        When: AgentExecutor执行工具
        Then: 抛出ToolPermissionError异常
        """
        # Given: 设置工具权限为deny
        permission_manager = PermissionManager(user_queue)
        permission_manager.set_permission_rule("dangerous_tool", "deny")
        
        agent_executor = AgentExecutor(permission_manager)
        
        # When/Then: 执行被拒绝的工具应抛出异常
        with pytest.raises(ToolPermissionError) as exc_info:
            await agent_executor.execute_tool_with_permission(
                "dangerous_tool", {"command": "rm -rf /"}, SessionContext()
            )
        
        # 验证异常信息
        assert "permission denied" in str(exc_info.value).lower()
        assert exc_info.value.tool_name == "dangerous_tool"
    
    @pytest.mark.asyncio
    async def test_agent_executor_permission_ask_user_grants(self):
        """
        测试AgentExecutor权限询问场景 - 用户授予
        
        Given: 工具权限设置为ask，用户授予权限
        When: AgentExecutor执行工具
        Then: 工具成功执行，权限被正确记录
        """
        # Given: 设置工具权限为ask，模拟用户授予
        permission_manager = PermissionManager(user_queue)
        permission_manager.set_permission_rule("moderate_risk_tool", "ask")
        
        # 模拟用户授予权限
        await user_queue.put("y")
        
        agent_executor = AgentExecutor(permission_manager)
        
        # When: 执行需要询问的工具
        result = await agent_executor.execute_tool_with_permission(
            "moderate_risk_tool", {"param": "value"}, SessionContext()
        )
        
        # Then: 工具成功执行
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_agent_executor_permission_ask_user_denies(self):
        """
        测试AgentExecutor权限询问场景 - 用户拒绝
        
        Given: 工具权限设置为ask，用户拒绝权限
        When: AgentExecutor执行工具
        Then: 抛出ToolPermissionError异常
        """
        # Given: 设置工具权限为ask，模拟用户拒绝
        permission_manager = PermissionManager(user_queue)
        permission_manager.set_permission_rule("moderate_risk_tool", "ask")
        
        # 模拟用户拒绝权限
        await user_queue.put("n")
        
        agent_executor = AgentExecutor(permission_manager)
        
        # When/Then: 执行需要询问的工具，用户拒绝
        with pytest.raises(ToolPermissionError) as exc_info:
            await agent_executor.execute_tool_with_permission(
                "moderate_risk_tool", {"param": "value"}, SessionContext()
            )
        
        # 验证权限被拒绝
        assert "permission denied" in str(exc_info.value).lower()
```

#### 4.2.2 异常处理测试
```python
    @pytest.mark.asyncio
    async def test_agent_executor_tool_permission_request_exception(self):
        """
        测试ToolPermissionRequest异常抛出
        
        Given: 工具权限设置为ask
        When: AgentExecutor执行工具（无用户确认）
        Then: 抛出ToolPermissionRequest异常
        """
        # Given: 设置工具权限为ask
        permission_manager = PermissionManager(user_queue)
        permission_manager.set_permission_rule("test_tool", "ask")
        
        agent_executor = AgentExecutor(permission_manager)
        
        # When/Then: 执行需要询问的工具应抛出ToolPermissionRequest
        with pytest.raises(ToolPermissionRequest) as exc_info:
            await agent_executor.execute_tool_with_permission(
                "test_tool", {"param": "value"}, SessionContext()
            )
        
        # 验证异常包含完整的权限请求信息
        assert exc_info.value.tool_name == "test_tool"
        assert exc_info.value.args == {"param": "value"}
        assert exc_info.value.request is not None
        assert exc_info.value.request.tool_name == "test_tool"
    
    @pytest.mark.asyncio
    async def test_agent_executor_permission_request_retry(self):
        """
        测试权限请求重试机制
        
        Given: 工具权限设置为ask，第一次抛出ToolPermissionRequest
        When: 捕获异常，用户确认后重新执行
        Then: 第二次执行成功
        """
        # Given: 设置工具权限为ask
        permission_manager = PermissionManager(user_queue)
        permission_manager.set_permission_rule("test_tool", "ask")
        
        agent_executor = AgentExecutor(permission_manager)
        
        # 第一次执行：应该抛出ToolPermissionRequest
        with pytest.raises(ToolPermissionRequest):
            await agent_executor.execute_tool_with_permission(
                "test_tool", {"param": "value"}, SessionContext()
            )
        
        # 用户确认后重新执行
        result = await agent_executor.execute_tool_with_permission(
            "test_tool", {"param": "value"}, SessionContext(), confirmation_granted=True
        )
        
        # Then: 第二次执行成功
        assert result is not None
```

#### 4.2.3 边界条件测试
```python
    @pytest.mark.asyncio
    async def test_agent_executor_permission_timeout(self):
        """
        测试权限请求超时处理
        
        Given: 工具权限设置为ask，用户超时未响应
        When: AgentExecutor执行工具
        Then: 抛出ToolPermissionError异常（超时视为拒绝）
        """
        # Given: 设置工具权限为ask，不放入用户响应（模拟超时）
        permission_manager = PermissionManager(user_queue)
        permission_manager.set_permission_rule("test_tool", "ask")
        
        agent_executor = AgentExecutor(permission_manager)
        
        # When/Then: 执行需要询问的工具，用户超时
        with pytest.raises(ToolPermissionError) as exc_info:
            await agent_executor.execute_tool_with_permission(
                "test_tool", {"param": "value"}, SessionContext(), timeout=0.1
            )
        
        # 验证超时被视为权限拒绝
        assert "timeout" in str(exc_info.value).lower() or "denied" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_agent_executor_invalid_tool_permission(self):
        """
        测试无效工具权限处理
        
        Given: 请求不存在的工具权限
        When: AgentExecutor执行工具
        Then: 抛出ToolNotFoundError异常
        """
        # Given: AgentExecutor
        permission_manager = PermissionManager(user_queue)
        agent_executor = AgentExecutor(permission_manager)
        
        # When/Then: 执行不存在的工具
        with pytest.raises(ToolNotFoundError) as exc_info:
            await agent_executor.execute_tool_with_permission(
                "nonexistent_tool", {}, SessionContext()
            )
        
        # 验证异常信息
        assert "not found" in str(exc_info.value).lower()
        assert "nonexistent_tool" in str(exc_info.value)
```

### 4.3 性能测试规范

```python
    @pytest.mark.asyncio
    async def test_agent_executor_permission_performance(self):
        """
        测试权限检查性能
        
        Given: 预定义权限规则的工具
        When: 连续执行权限检查
        Then: 性能满足要求（< 100ms）
        """
        # Given: 设置一些权限规则
        permission_manager = PermissionManager(user_queue)
        for i in range(10):
            permission_manager.set_permission_rule(f"tool_{i}", "allow")
        
        agent_executor = AgentExecutor(permission_manager)
        
        # When: 连续执行权限检查
        start_time = time.time()
        
        results = []
        for i in range(100):
            result = await agent_executor.execute_tool_with_permission(
                f"tool_{i % 10}", {"param": i}, SessionContext()
            )
            results.append(result)
        
        end_time = time.time()
        
        # Then: 验证性能达标
        execution_time = end_time - start_time
        assert execution_time < 10.0  # 100次检查应在10秒内完成
        assert len(results) == 100
        assert all(result is not None for result in results)
```

## 5. 实施计划（基于TDD原则）

### 5.1 第一阶段：基础集成测试（必须先实现测试）
1. **编写所有TDD测试用例**（当前阶段）✅
2. **运行测试确认红阶段**（测试应该失败）
3. **实现最小功能使测试通过**（绿阶段）
4. **重构优化代码结构**（重构阶段）

### 5.2 第二阶段：核心功能实现
1. **实现ToolPermissionRequest异常类**
2. **修改AgentExecutor.execute_tool()方法**
3. **实现权限检查前置逻辑**
4. **集成PermissionManager调用**

### 5.3 第三阶段：集成验证
1. **运行所有TDD测试**
2. **编写端到端集成测试**
3. **性能基准测试**
4. **代码审查和文档更新"

### 5.4 验收标准
- [ ] 所有TDD测试用例通过
- [ ] 代码覆盖率 > 90%
- [ ] 性能指标达标（< 100ms）
- [ ] 错误处理完整
- [ ] 文档同步更新
- [ ] 代码审查通过

## 6. 风险评估与缓解

### 6.1 高风险项
1. **异步处理复杂性**: AgentExecutor的异步流程与权限检查集成
2. **状态一致性**: 权限状态与工具执行状态的同步
3. **性能影响**: 权限检查对工具执行性能的影响

### 6.2 缓解措施
1. **充分的单元测试**: 每个集成点都有完整的测试覆盖
2. **渐进式实施**: 分阶段实现，每阶段都有验证点
3. **性能监控**: 集成性能基准测试，确保性能达标
4. **代码审查**: 强制代码审查，确保架构一致性

## 7. 结论

本规范严格遵循工作纪律，确保在实际编码之前：
1. ✅ 完整的规范文档
2. ✅ 详细的TDD测试用例  
3. ✅ 明确的集成接口和契约
4. ✅ 完整的错误处理和边界条件
5. ✅ 性能要求和验收标准

**下一步**: 严格按照TDD原则，先实现测试用例，再实现功能代码，确保红-绿-重构循环的完整执行。