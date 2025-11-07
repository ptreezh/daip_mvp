# 权限Ask模式TUI界面设计规范

## 设计目标

实现一个**用户友好、直观清晰、响应式**的TUI（文本用户界面）权限请求界面，为用户提供良好的权限确认体验，同时保持系统的安全性和可预测性。

## 设计原则

### 1. 用户体验优先
- **清晰易懂**: 界面信息层次分明，用户能快速理解请求内容
- **操作直观**: 选项明确，响应方式自然
- **反馈及时**: 用户操作后立即给出反馈
- **错误友好**: 输入错误时提供清晰指导

### 2. 安全性优先
- **风险可视化**: 清晰展示操作风险等级
- **默认安全**: 超时和异常情况下默认拒绝
- **确认明确**: 重要操作需要明确确认
- **审计友好**: 所有交互都可追溯

### 3. 一致性设计
- **界面统一**: 所有权限请求使用相同界面风格
- **交互一致**: 响应方式保持一致
- **术语标准**: 使用统一的权限相关术语

## 界面设计规范

### 1. 主界面布局

```
═══════════════════════════════════════════════════════════════
🔒 TOOL PERMISSION REQUEST
═══════════════════════════════════════════════════════════════

Tool: [tool_name]
Arguments: [formatted_args]
Description: [tool_description]
Risk Level: [low/medium/high] [risk_indicator]

⚠️  [risk_warning_if_applicable]

═══════════════════════════════════════════════════════════════
Options:
[Y] Yes, grant this permission
[N] No, deny this permission  
[A] Always grant for this tool
[V] Never grant for this tool
[C] Cancel operation

═══════════════════════════════════════════════════════════════

Your choice: [user_input_cursor]
```

### 2. 风险等级可视化

#### 低风险 (绿色)
```
Risk Level: [🟢 LOW]
```

#### 中风险 (黄色)
```
Risk Level: [🟡 MEDIUM]
⚠️  This tool will access system resources. Please review carefully.
```

#### 高风险 (红色)
```
Risk Level: [🔴 HIGH]
⚠️  WARNING: This tool performs sensitive operations that may affect system security.
⚠️  Please ensure you understand the implications before proceeding.
```

### 3. 特殊工具警告

#### 文件系统操作
```
⚠️  This tool will access file system resources at: [path]
⚠️  Ensure the path is safe and you have appropriate permissions.
```

#### 网络操作
```
⚠️  This tool will make network requests to: [url]
⚠️  Ensure the destination is trusted and secure.
```

#### 系统命令
```
⚠️  This tool will execute system commands: [command]
⚠️  Commands may have system-wide effects. Proceed with caution.
```

## 交互流程设计

### 1. 正常权限请求流程

```
1. 系统检测到权限为"ask"的工具调用
2. 生成PermissionRequestEvent
3. TUI界面显示权限请求
4. 用户输入响应（Y/N/A/V/C）
5. 系统解析并验证用户输入
6. 处理权限决策
7. 显示确认结果
8. 继续执行或跳过工具
```

### 2. 用户输入处理

#### 有效输入
- `Y` 或 `y` → 授予权限
- `N` 或 `n` → 拒绝权限
- `A` 或 `a` → 始终授予（记住选择）
- `V` 或 `v` → 永不授予（记住选择）
- `C` 或 `c` → 取消操作

#### 无效输入处理
```
Invalid input. Please enter one of: [Y]es, [N]o, [A]lways, [N]ever, [C]ancel
Your choice: 
```

#### 空输入处理
```
No input provided. Defaulting to [N]o (deny) for security.
```

### 3. 超时处理

#### 超时警告
```
⏰ Permission request timed out after 30 seconds.
Defaulting to [N]o (deny) for security.
```

#### 超时倒计时（可选）
```
Time remaining: 25s
Your choice: 
```

## 技术实现规范

### 1. TUI权限界面类

```python
class PermissionTUIInterface:
    """TUI权限界面接口"""
    
    def __init__(self, user_input_queue: asyncio.Queue):
        self.user_input_queue = user_input_queue
        self.current_request: Optional[PermissionRequestEvent] = None
        self.response_future: Optional[asyncio.Future] = None
        
    async def show_permission_request(self, request: PermissionRequestEvent) -> None:
        """显示权限请求界面"""
        self.current_request = request
        await self._render_permission_interface(request)
        
    async def get_user_response(self, timeout: float = 30.0) -> PermissionResponse:
        """获取用户响应"""
        self.response_future = asyncio.Future()
        
        try:
            # 启动响应收集任务
            response_task = asyncio.create_task(self._collect_user_response())
            
            # 等待用户响应或超时
            response = await asyncio.wait_for(response_task, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            logger.warning(f"Permission request timed out for {self.current_request.tool_name}")
            return PermissionResponse.DENY
            
        finally:
            self.response_future = None
            self.current_request = None
```

### 2. 界面渲染方法

```python
def _render_permission_interface(self, request: PermissionRequestEvent) -> str:
    """渲染权限请求界面"""
    lines = []
    
    # 顶部边框
    lines.append("=" * 70)
    lines.append("🔒 TOOL PERMISSION REQUEST")
    lines.append("=" * 70)
    lines.append("")
    
    # 工具信息
    lines.append(f"Tool: {request.tool_name}")
    lines.append(f"Arguments: {self._format_arguments(request.args)}")
    
    if request.description:
        lines.append(f"Description: {request.description}")
    
    # 风险等级
    risk_indicator = self._get_risk_indicator(request.risk_level)
    lines.append(f"Risk Level: {risk_indicator} {request.risk_level.upper()}")
    
    # 风险警告
    warning = self._get_risk_warning(request.tool_name, request.args, request.risk_level)
    if warning:
        lines.append("")
        lines.append(warning)
    
    # 底部边框
    lines.append("")
    lines.append("=" * 70)
    lines.append("Options:")
    lines.append("[Y] Yes, grant this permission")
    lines.append("[N] No, deny this permission")
    lines.append("[A] Always grant for this tool")
    lines.append("[V] Never grant for this tool")
    lines.append("[C] Cancel operation")
    lines.append("=" * 70)
    lines.append("")
    lines.append("Your choice: ")
    
    return "\n".join(lines)
```

### 3. 用户响应收集

```python
async def _collect_user_response(self) -> PermissionResponse:
    """收集用户响应"""
    while True:
        try:
            # 等待用户输入
            user_input = await self.user_input_queue.get()
            
            # 解析用户输入
            response = self._parse_user_input(user_input)
            
            if response:
                # 确认用户选择
                if await self._confirm_user_choice(response):
                    return response
                else:
                    # 用户取消，重新显示界面
                    await self._render_permission_interface(self.current_request)
                    continue
            else:
                # 无效输入，显示错误信息
                await self._show_invalid_input_error()
                
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Error collecting user response: {e}")
            return PermissionResponse.DENY
```

### 4. 输入解析和验证

```python
def _parse_user_input(self, user_input: str) -> Optional[PermissionResponse]:
    """解析用户输入"""
    if not user_input:
        return None
        
    input_clean = user_input.strip().lower()
    
    # 单字符响应
    if input_clean == 'y':
        return PermissionResponse.GRANT
    elif input_clean == 'n':
        return PermissionResponse.DENY
    elif input_clean == 'a':
        return PermissionResponse.ALWAYS
    elif input_clean == 'v':
        return PermissionResponse.NEVER
    elif input_clean == 'c':
        return PermissionResponse.CANCEL
        
    # 完整单词响应
    elif input_clean == 'yes':
        return PermissionResponse.GRANT
    elif input_clean == 'no':
        return PermissionResponse.DENY
    elif input_clean == 'always':
        return PermissionResponse.ALWAYS
    elif input_clean == 'never':
        return PermissionResponse.NEVER
    elif input_clean == 'cancel':
        return PermissionResponse.CANCEL
        
    # 无效输入
    return None
```

## 用户体验优化

### 1. 响应确认

```python
async def _confirm_user_choice(self, response: PermissionResponse) -> bool:
    """确认用户选择"""
    if response in [PermissionResponse.ALWAYS, PermissionResponse.NEVER]:
        # 记住选择需要额外确认
        confirmation_text = self._get_confirmation_text(response)
        await self._show_confirmation_dialog(confirmation_text)
        
        # 等待用户确认
        confirmation = await self._wait_for_confirmation()
        return confirmation
        
    return True
```

### 2. 进度指示

```python
async def _show_progress_indicator(self, remaining_time: float) -> None:
    """显示剩余时间指示器"""
    if remaining_time < 10:  # 最后10秒显示倒计时
        await self._render_countdown(int(remaining_time))
```

### 3. 结果反馈

```python
async def _show_permission_result(self, response: PermissionResponse, granted: bool) -> None:
    """显示权限结果反馈"""
    if granted:
        await self._show_success_message("Permission granted successfully.")
    else:
        await self._show_info_message("Permission denied. Continuing without tool execution.")
```

## 错误处理和恢复

### 1. 界面渲染错误

```python
async def _safe_render_interface(self, content: str) -> None:
    """安全渲染界面内容"""
    try:
        # 尝试渲染界面
        await self._render_to_screen(content)
    except Exception as e:
        logger.error(f"Failed to render permission interface: {e}")
        # 降级到简化界面
        await self._render_simplified_interface()
```

### 2. 用户输入错误

```python
async def _show_invalid_input_error(self) -> None:
    """显示无效输入错误"""
    error_message = """
Invalid input. Please enter one of:
[Y]es - Grant this permission
[N]o - Deny this permission
[A]lways - Always grant for this tool
[N]ever - Never grant for this tool
[C]ancel - Cancel the operation

Your choice: """
    await self._render_to_screen(error_message)
```

### 3. 系统错误降级

```python
async def _handle_system_error(self, error: Exception) -> PermissionResponse:
    """处理系统错误"""
    logger.error(f"Permission UI system error: {error}")
    
    # 显示错误信息
    await self._show_system_error_message()
    
    # 安全降级：默认拒绝
    return PermissionResponse.DENY
```

## 可访问性设计

### 1. 键盘导航支持
- 支持Tab键在选项间切换
- 支持Enter键确认选择
- 支持Esc键取消操作

### 2. 屏幕阅读器友好
- 清晰的标题和描述
- 适当的空行分隔
- 明确的选项标识

### 3. 高对比度支持
- 使用标准ASCII字符
- 避免依赖颜色信息
- 提供文本替代符号

## 性能优化

### 1. 异步渲染
- 界面渲染不阻塞主流程
- 响应收集使用异步机制
- 超时保护所有用户交互

### 2. 内存使用优化
- 及时清理临时数据
- 限制界面历史记录
- 使用生成器处理大量文本

### 3. 响应时间优化
- 快速界面渲染
- 高效的用户输入处理
- 最小化界面切换延迟

## 测试策略

### 1. 界面渲染测试
```python
def test_permission_interface_rendering():
    """测试权限界面渲染"""
    ui = PermissionTUIInterface(user_input_queue)
    request = PermissionRequestEvent(tool_name="read_file", args={"path": "test.txt"})
    
    rendered = ui._render_permission_interface(request)
    
    assert "🔒 TOOL PERMISSION REQUEST" in rendered
    assert "read_file" in rendered
    assert "[Y] Yes" in rendered
```

### 2. 用户输入解析测试
```python
def test_user_input_parsing():
    """测试用户输入解析"""
    ui = PermissionTUIInterface(user_input_queue)
    
    assert ui._parse_user_input("y") == PermissionResponse.GRANT
    assert ui._parse_user_input("invalid") is None
    assert ui._parse_user_input("") is None
```

### 3. 超时处理测试
```python
@pytest.mark.asyncio
async def test_permission_timeout():
    """测试权限请求超时"""
    ui = PermissionTUIInterface(user_input_queue)
    request = PermissionRequestEvent(tool_name="test", args={})
    
    # 不放入任何用户输入，模拟超时
    response = await ui.get_user_response(timeout=0.1)
    
    assert response == PermissionResponse.DENY
```

## 配置和自定义

### 1. 界面主题配置
```python
@dataclass
class PermissionUITheme:
    border_char: str = "═"
    header_prefix: str = "🔒"
    warning_prefix: str = "⚠️"
    success_prefix: str = "✅"
    error_prefix: str = "❌"
    info_prefix: str = "ℹ️"
```

### 2. 超时配置
```python
@dataclass
class PermissionUITimeout:
    default_timeout: float = 30.0
    warning_threshold: float = 10.0
    countdown_interval: float = 1.0
```

### 3. 显示选项配置
```python
@dataclass
class PermissionUIDisplay:
    show_risk_level: bool = True
    show_arguments: bool = True
    show_description: bool = True
    show_countdown: bool = True
    show_confirmation: bool = True
```

## 实施计划

### 第一阶段：基础界面（2-3天）
1. 实现PermissionTUIInterface基础类
2. 实现界面渲染方法
3. 实现用户输入解析
4. 编写基础界面测试

### 第二阶段：交互增强（2-3天）
1. 实现响应收集和处理
2. 实现超时和错误处理
3. 实现确认对话框
4. 实现进度指示器

### 第三阶段：用户体验优化（2-3天）
1. 实现风险可视化
2. 实现特殊工具警告
3. 实现响应确认机制
4. 实现结果反馈

### 第四阶段：集成测试（2-3天）
1. 集成到AgentExecutor
2. 完整流程测试
3. 性能优化和调优
4. 用户验收测试

## 验收标准

### 功能验收
- [ ] 权限请求界面正确渲染
- [ ] 用户响应被正确收集和解析
- [ ] 超时机制正常工作
- [ ] 错误处理完整有效
- [ ] 风险信息清晰展示

### 用户体验验收
- [ ] 界面清晰易懂
- [ ] 操作响应及时
- [ ] 错误提示友好
- [ ] 特殊工具有适当警告

### 性能验收
- [ ] 界面渲染快速
- [ ] 用户交互响应及时
- [ ] 超时机制准确
- [ ] 内存使用合理

## 总结

本设计规范为TUI权限界面提供了完整的设计框架，确保用户能够获得良好的权限确认体验，同时保持系统的安全性和可靠性。界面设计遵循用户体验优先和安全性优先的原则，通过清晰的视觉设计和直观的交互方式，帮助用户做出明智的权限决策。