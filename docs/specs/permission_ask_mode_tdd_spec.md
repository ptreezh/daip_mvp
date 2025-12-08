# 权限Ask模式TDD规范文档

## 文档信息
- **文档名称**: 权限Ask模式TDD规范
- **版本**: 1.0
- **作者**: DAIP开发团队
- **创建日期**: 2025年9月18日
- **状态**: 草案

## 1. 需求概述 (Requirements)

### 1.1 业务价值 (Business Value)
实现完整的权限Ask模式交互系统，提供用户友好的工具权限确认机制，确保系统安全性的同时保持良好的用户体验。

### 1.2 功能需求 (Functional Requirements)

#### FR1: 权限请求生成
- 当工具权限配置为"ask"时，系统必须生成权限请求事件
- 权限请求必须包含工具名称、参数和描述信息
- 权限请求事件必须能够被用户界面正确显示

#### FR2: 用户响应处理
- 系统必须能够接收和处理用户的权限响应
- 支持多种响应类型：授予、拒绝、始终授予、永不授予
- 用户响应必须影响工具执行结果

#### FR3: 权限状态管理
- 系统必须维护权限请求的状态（等待、已授予、已拒绝、已记住）
- 权限状态必须在会话期间保持一致
- 支持权限状态的查询和更新

#### FR4: 记住选择功能
- 用户可以选择"始终授予"或"永不授予"
- 记住的选择必须持久化存储
- 后续相同工具调用必须应用记住的选择

### 1.3 非功能需求 (Non-Functional Requirements)

#### NFR1: 性能要求
- 权限检查必须在100ms内完成
- 权限确认流程不能阻塞系统响应超过5秒
- 权限规则匹配必须高效，支持大量规则

#### NFR2: 安全要求
- 权限系统必须防止绕过和注入攻击
- 权限决策必须记录审计日志
- 敏感操作需要额外确认

#### NFR3: 可用性要求
- 权限请求界面必须清晰易懂
- 用户响应收集必须直观便捷
- 错误处理必须友好并提供帮助

## 2. 技术规范 (Technical Specification)

### 2.1 接口定义 (Interface Definition)

#### 2.1.1 PermissionResponse枚举
```python
class PermissionResponse(Enum):
    GRANT = "grant"      # 授予此权限
    DENY = "deny"        # 拒绝此权限  
    ALWAYS = "always"    # 始终授予此工具
    NEVER = "never"      # 永不授予此工具
    CANCEL = "cancel"    # 取消操作
```

#### 2.1.2 PermissionState枚举
```python
class PermissionState(Enum):
    PENDING = "pending"      # 等待用户响应
    GRANTED = "granted"      # 权限已授予
    DENIED = "denied"        # 权限已拒绝
    REMEMBERED = "remembered" # 用户选择已记住
    CANCELLED = "cancelled"  # 操作已取消
```

#### 2.1.3 PermissionInteraction类
```python
class PermissionInteraction(BaseModel):
    request_id: str
    tool_name: str
    args: Dict[str, Any]
    state: PermissionState
    response: Optional[PermissionResponse] = None
    timestamp: datetime
    user_choice: Optional[str] = None
```

### 2.2 状态管理 (State Management)

#### 2.2.1 PermissionManager类
负责权限交互的整体管理，包括：
- 权限请求创建和处理
- 用户响应收集和验证
- 权限状态维护和更新
- 权限规则应用和管理

#### 2.2.2 PermissionInteractionManager类
负责具体的交互流程管理，包括：
- 用户界面展示和交互
- 响应收集和解析
- 权限决策执行
- 结果反馈和处理

### 2.3 用户界面 (User Interface)

#### 2.3.1 TUI界面规范
```
═══════════════════════════════════════════════════════════════
🔒 TOOL PERMISSION REQUEST
═══════════════════════════════════════════════════════════════

Tool: [tool_name]
Arguments: [formatted_args]
Description: [tool_description]
Risk Level: [low/medium/high]

⚠️  [risk_warning_if_applicable]

═══════════════════════════════════════════════════════════════
Options:
[Y] Yes, grant this permission
[N] No, deny this permission  
[A] Always grant for this tool
[V] Never grant for this tool
[C] Cancel operation
═══════════════════════════════════════════════════════════════

Your choice: [user_input]
```

#### 2.3.2 响应解析规则
- Y/y → GRANT
- N/n → DENY  
- A/a → ALWAYS
- V/v → NEVER
- C/c → CANCEL
- 空输入 → 默认DENY（安全优先）

## 3. 测试策略 (Test Strategy)

### 3.1 测试原则 (Testing Principles)
- **测试先行**：先写测试，再实现功能
- **红绿重构**：遵循红-绿-重构循环
- **边界覆盖**：覆盖所有边界条件和异常情况
- **行为验证**：验证行为而非实现细节

### 3.2 单元测试 (Unit Tests)

#### 3.2.1 PermissionResponse测试
```python
def test_permission_response_values():
    """验证PermissionResponse枚举值正确"""
    assert PermissionResponse.GRANT.value == "grant"
    assert PermissionResponse.DENY.value == "deny"
    assert PermissionResponse.ALWAYS.value == "always"
    assert PermissionResponse.NEVER.value == "never"
    assert PermissionResponse.CANCEL.value == "cancel"

def test_permission_response_parsing():
    """验证用户输入到PermissionResponse的转换"""
    assert parse_permission_response("y") == PermissionResponse.GRANT
    assert parse_permission_response("n") == PermissionResponse.DENY
    assert parse_permission_response("a") == PermissionResponse.ALWAYS
    assert parse_permission_response("v") == PermissionResponse.NEVER
    assert parse_permission_response("c") == PermissionResponse.CANCEL
```

#### 3.2.2 PermissionManager测试
```python
def test_create_permission_request():
    """验证权限请求创建正确"""
    manager = PermissionManager()
    request = manager.create_request("read_file", {"path": "test.txt"})
    
    assert request.tool_name == "read_file"
    assert request.args == {"path": "test.txt"}
    assert request.state == PermissionState.PENDING
    assert request.response is None

def test_grant_permission():
    """验证权限授予处理正确"""
    manager = PermissionManager()
    request = manager.create_request("read_file", {"path": "test.txt"})
    
    result = manager.process_response(request.id, PermissionResponse.GRANT)
    
    assert result is True
    assert request.state == PermissionState.GRANTED
    assert request.response == PermissionResponse.GRANT

def test_deny_permission():
    """验证权限拒绝处理正确"""
    manager = PermissionManager()
    request = manager.create_request("read_file", {"path": "test.txt"})
    
    result = manager.process_response(request.id, PermissionResponse.DENY)
    
    assert result is False
    assert request.state == PermissionState.DENIED
    assert request.response == PermissionResponse.DENY
```

### 3.3 集成测试 (Integration Tests)

#### 3.3.1 完整权限流程测试
```python
@pytest.mark.asyncio
async def test_complete_permission_ask_flow():
    """验证完整的权限ask模式流程"""
    # Arrange
    agent = create_agent_with_permission_ask()
    
    # Act - 模拟用户授予权限
    events = []
    async for event in agent.run("read my file"):
        events.append(event)
        if isinstance(event, PermissionRequestEvent):
            # 模拟用户响应
            await agent.process_permission_response(
                event.request_id, 
                PermissionResponse.GRANT
            )
    
    # Assert
    permission_events = [e for e in events if isinstance(e, PermissionRequestEvent)]
    assert len(permission_events) == 1
    
    tool_call_events = [e for e in events if isinstance(e, ToolCallEvent)]
    assert len(tool_call_events) == 1  # 权限授予后工具被执行

def test_permission_remember_always():
    """验证记住选择功能（始终授予）"""
    # Arrange
    manager = PermissionManager()
    
    # Act - 第一次选择"始终授予"
    request1 = manager.create_request("read_file", {"path": "test1.txt"})
    manager.process_response(request1.id, PermissionResponse.ALWAYS)
    
    # Assert - 后续相同工具应该自动授予
    request2 = manager.create_request("read_file", {"path": "test2.txt"})
    decision = manager.check_permission("read_file", {"path": "test2.txt"})
    
    assert decision == PermissionResponse.GRANT
    assert request2.state == PermissionState.REMEMBERED
```

#### 3.3.2 TUI界面测试
```python
def test_permission_ui_rendering():
    """验证权限请求界面正确渲染"""
    ui = PermissionTUI()
    request = PermissionRequestEvent(
        tool_name="read_file",
        args={"path": "sensitive.txt"}
    )
    
    rendered = ui.render_permission_request(request)
    
    assert "🔒 TOOL PERMISSION REQUEST" in rendered
    assert "read_file" in rendered
    assert "sensitive.txt" in rendered
    assert "[Y] Yes" in rendered
    assert "[N] No" in rendered

def test_permission_response_parsing():
    """验证用户响应解析正确"""
    ui = PermissionTUI()
    
    assert ui.parse_response("y") == PermissionResponse.GRANT
    assert ui.parse_response("Y") == PermissionResponse.GRANT
    assert ui.parse_response("n") == PermissionResponse.DENY
    assert ui.parse_response("invalid") == PermissionResponse.DENY  # 默认安全
```

### 3.4 边界条件测试 (Edge Cases)

```python
def test_permission_timeout():
    """验证权限请求超时处理"""
    manager = PermissionManager(timeout=5.0)
    request = manager.create_request("read_file", {"path": "test.txt"})
    
    # 模拟超时
    time.sleep(5.1)
    
    result = manager.check_permission_status(request.id)
    assert result == PermissionResponse.DENY  # 超时默认拒绝

def test_invalid_permission_response():
    """验证无效权限响应处理"""
    manager = PermissionManager()
    request = manager.create_request("read_file", {"path": "test.txt"})
    
    # 无效响应应该被拒绝（安全优先）
    result = manager.process_response(request.id, "invalid_response")
    assert result is False
    assert request.state == PermissionState.DENIED

def test_concurrent_permission_requests():
    """验证并发权限请求处理"""
    manager = PermissionManager()
    
    # 创建多个权限请求
    request1 = manager.create_request("tool1", {"arg": "1"})
    request2 = manager.create_request("tool2", {"arg": "2"})
    
    # 并发处理响应
    async def process_responses():
        tasks = [
            manager.process_response_async(request1.id, PermissionResponse.GRANT),
            manager.process_response_async(request2.id, PermissionResponse.DENY)
        ]
        return await asyncio.gather(*tasks)
    
    results = asyncio.run(process_responses())
    
    assert results[0] is True  # tool1 granted
    assert results[1] is False  # tool2 denied
```

## 4. 实现计划 (Implementation Plan)

### 4.1 第一阶段：基础模型（1-2天）
- [ ] PermissionResponse枚举实现
- [ ] PermissionState枚举实现  
- [ ] PermissionInteraction模型实现
- [ ] 基础单元测试编写

### 4.2 第二阶段：权限管理器（2-3天）
- [ ] PermissionManager类实现
- [ ] 权限请求创建和处理逻辑
- [ ] 用户响应处理机制
- [ ] 权限状态管理功能
- [ ] 集成测试编写

### 4.3 第三阶段：用户界面（3-4天）
- [ ] TUI界面设计和实现
- [ ] 权限请求界面渲染
- [ ] 用户响应收集和解析
- [ ] 界面测试和优化

### 4.4 第四阶段：集成和优化（2-3天）
- [ ] AgentExecutor集成
- [ ] 完整流程测试
- [ ] 性能优化和调优
- [ ] 文档完善和验收

## 5. 验收标准 (Acceptance Criteria)

### 5.1 功能验收
- [ ] 权限请求事件正确生成和显示
- [ ] 用户响应被正确收集和解析
- [ ] 权限决策影响工具执行结果
- [ ] 记住选择功能正常工作
- [ ] 边界条件正确处理

### 5.2 性能验收
- [ ] 权限检查 < 100ms
- [ ] 界面响应 < 5秒
- [ ] 内存使用合理
- [ ] 无死锁和性能瓶颈

### 5.3 质量验收
- [ ] 代码覆盖率 > 90%
- [ ] 所有测试通过
- [ ] 文档完整准确
- [ ] 代码审查通过

## 6. 风险评估 (Risk Assessment)

### 6.1 技术风险
- **复杂度风险**：多组件交互增加复杂度
- **兼容性风险**：不同界面模式兼容性问题
- **性能风险**：权限检查可能影响整体性能

### 6.2 缓解措施
- **模块化设计**：降低组件耦合度
- **充分测试**：确保各组件独立可测试
- **性能监控**：实时监控和优化
- **渐进式实现**：分阶段实施，降低风险

## 7. 成功标准 (Success Criteria)

项目成功的衡量标准：
1. **功能完整性**：所有需求功能100%实现
2. **测试覆盖率**：代码覆盖率≥90%，所有测试通过
3. **性能指标**：满足性能要求，无性能退化
4. **用户体验**：界面友好，操作直观，错误率低
5. **代码质量**：遵循编码规范，通过代码审查
6. **文档完整性**：技术文档和用户文档完整准确

---

**文档状态**: ✅ 已完成  
**审查状态**: 待审查  
**实施状态**: 准备开始TDD实现