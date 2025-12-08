# 权限用户响应收集和处理机制规范

## 文档信息
- **文档版本**: v1.0
- **创建日期**: 2025年9月18日
- **作者**: DAIP开发团队
- **状态**: 草案
- **置信度**: 0.95

## 需求对齐检查

### 项目最高需求原则对齐
- ✅ **本地优先**: 所有用户响应在本地处理，不依赖云端
- ✅ **隐私保护**: 用户选择本地存储，不泄露隐私信息
- ✅ **用户控制**: 用户拥有完全的权限决策控制权
- ✅ **安全可信**: 默认安全策略，防止恶意操作
- ✅ **可预测性**: 响应处理流程可预测，不会意外阻塞

### TDD BMAD kiro's spec规范对齐
- ✅ **TDD驱动**: 测试先行，红-绿-重构循环
- ✅ **BMAD方法**: 行为驱动开发，明确业务价值
- ✅ **KIRO规范**: 知识、接口、角色、操作的清晰定义
- ✅ **契约先行**: 明确的接口契约和验收标准

## 1. 知识(Knowledge)定义

### 业务知识
- **用户响应收集**: 从TUI界面收集用户对权限请求的响应
- **响应验证**: 验证用户输入的有效性和安全性
- **响应处理**: 根据用户选择执行相应的权限决策
- **超时管理**: 处理用户响应超时情况
- **错误恢复**: 处理响应收集过程中的异常情况

### 技术知识
- **异步交互**: 非阻塞的用户响应收集机制
- **超时控制**: 响应收集的时间限制和管理
- **输入验证**: 用户输入的安全检查和验证
- **状态管理**: 响应状态的跟踪和管理
- **事件驱动**: 基于事件的响应处理架构

## 2. 接口(Interface)定义

### 核心接口
```python
class UserResponseCollectorInterface(ABC):
    """用户响应收集器接口"""
    
    @abstractmethod
    async def collect_response(self, request: PermissionRequestEvent, timeout: float) -> PermissionResponse:
        """收集用户对权限请求的响应"""
        pass
    
    @abstractmethod
    async def validate_response(self, raw_input: str) -> Optional[PermissionResponse]:
        """验证用户输入并转换为权限响应"""
        pass
    
    @abstractmethod
    def cancel_collection(self) -> None:
        """取消当前的响应收集"""
        pass
```

### 响应处理器接口
```python
class ResponseProcessorInterface(ABC):
    """响应处理器接口"""
    
    @abstractmethod
    async def process_response(self, response: PermissionResponse, request: PermissionRequestEvent) -> PermissionResult:
        """处理用户响应并返回结果"""
        pass
    
    @abstractmethod
    async def handle_confirmation(self, response: PermissionResponse) -> bool:
        """处理需要确认的特殊响应（如always/never）"""
        pass
```

## 3. 角色(Role)定义

### 核心角色
- **UserResponseCollector**: 用户响应收集器，负责收集和验证用户输入
- **ResponseProcessor**: 响应处理器，负责处理用户响应和生成结果
- **TimeoutManager**: 超时管理器，负责响应超时控制
- **ErrorRecoveryHandler**: 错误恢复处理器，负责异常情况的恢复

### 用户角色
- **EndUser**: 最终用户，进行权限决策
- **SystemOperator**: 系统操作员，监控响应处理流程

## 4. 操作(Operation)定义

### 核心操作序列

#### 操作1: 用户响应收集
```
触发条件: TUI界面显示权限请求后
前置条件: 权限请求事件已生成，用户界面已显示
操作序列:
  1. 启动响应收集任务
  2. 等待用户输入（带超时）
  3. 验证用户输入有效性
  4. 转换为用户权限响应
  5. 处理特殊响应（如确认）
  6. 返回最终响应结果
后置条件: 返回有效的PermissionResponse或超时错误
```

#### 操作2: 响应验证和处理
```
触发条件: 用户响应被成功收集
前置条件: 用户输入已通过验证
操作序列:
  1. 解析用户输入
  2. 验证响应类型
  3. 处理特殊响应（always/never）
  4. 生成权限结果
  5. 更新权限状态
后置条件: 返回PermissionResult对象
```

## 5. 功能需求 (Functional Requirements)

### FR1: 异步响应收集
- **描述**: 系统必须能够异步收集用户响应，不阻塞主流程
- **验收标准**: 
  - 响应收集必须在独立的异步任务中执行
  - 支持并发处理多个权限请求
  - 响应收集过程可被取消

### FR2: 输入验证和清洗
- **描述**: 系统必须验证用户输入的有效性，并进行安全清洗
- **验收标准**:
  - 支持大小写不敏感输入
  - 自动去除输入前后的空白字符
  - 过滤无效和恶意输入
  - 提供清晰的错误反馈

### FR3: 超时管理
- **描述**: 系统必须实现完善的超时管理机制
- **验收标准**:
  - 默认30秒响应超时
  - 超时前10秒开始倒计时警告
  - 超时后自动使用默认安全响应
  - 支持动态调整超时时间

### FR4: 特殊响应处理
- **描述**: 系统必须妥善处理特殊响应类型（always/never）
- **验收标准**:
  - "always"响应需要用户二次确认
  - "never"响应需要用户二次确认
  - 确认过程也有超时保护
  - 确认失败时回退到标准响应

### FR5: 错误恢复机制
- **描述**: 系统必须具备完善的错误恢复能力
- **验收标准**:
  - 输入错误时提供重新输入机会
  - 系统错误时优雅降级
  - 异常情况下的安全默认响应
  - 详细的错误日志记录

## 6. 非功能需求 (Non-Functional Requirements)

### NFR1: 性能要求
- **响应时间**: 用户输入处理 < 100ms
- **超时精度**: 超时误差 < 1秒
- **并发支持**: 支持至少10个并发权限请求
- **内存使用**: 响应收集过程内存占用 < 1MB

### NFR2: 安全要求
- **输入安全**: 防止注入攻击和恶意输入
- **超时安全**: 超时情况下默认拒绝权限
- **错误安全**: 异常情况下默认安全响应
- **审计安全**: 所有响应决策可审计追踪

### NFR3: 可用性要求
- **操作直观**: 用户界面清晰，操作简单
- **反馈及时**: 用户操作后立即给出反馈
- **错误友好**: 错误信息清晰，指导性强
- **恢复容易**: 错误发生后容易恢复

## 7. 技术设计规范

### 7.1 架构设计

```python
class RobustUserResponseCollector:
    """健壮的用户响应收集器"""
    
    def __init__(self, user_input_queue: asyncio.Queue):
        self.user_input_queue = user_input_queue
        self.current_collection_task: Optional[asyncio.Task] = None
        self.response_timeout = 30.0
        self.confirmation_timeout = 10.0
        self.max_retry_attempts = 3
        
    async def collect_response(self, request: PermissionRequestEvent, timeout: float) -> PermissionResponse:
        """收集用户响应"""
        try:
            # 启动响应收集任务
            collection_task = asyncio.create_task(self._do_collect_response(request, timeout))
            self.current_collection_task = collection_task
            
            # 等待结果或超时
            response = await asyncio.wait_for(collection_task, timeout=timeout)
            return response
            
        except asyncio.TimeoutError:
            logger.warning(f"Response collection timed out for {request.tool_name}")
            return PermissionResponse.DENY
            
        except Exception as e:
            logger.error(f"Response collection failed: {e}")
            return PermissionResponse.DENY
            
        finally:
            self.current_collection_task = None
    
    async def _do_collect_response(self, request: PermissionRequestEvent, timeout: float) -> PermissionResponse:
        """执行响应收集"""
        start_time = datetime.utcnow()
        remaining_time = timeout
        
        while remaining_time > 0:
            # 显示倒计时（最后10秒）
            if remaining_time < 10:
                await self._show_countdown(int(remaining_time))
            
            # 等待用户输入
            try:
                wait_timeout = min(1.0, remaining_time)
                user_input = await asyncio.wait_for(
                    self.user_input_queue.get(),
                    timeout=wait_timeout
                )
                
                # 验证和解析输入
                response = await self._validate_and_parse_input(user_input)
                if response:
                    # 处理需要确认的特殊响应
                    if response in [PermissionResponse.ALWAYS, PermissionResponse.NEVER]:
                        confirmed = await self._handle_confirmation(response, request)
                        if confirmed:
                            return response
                        else:
                            # 确认被取消，重新显示界面
                            continue
                    else:
                        # 标准响应，直接返回
                        return response
                else:
                    # 无效输入，显示错误并重试
                    await self._show_invalid_input_error()
                    continue
                    
            except asyncio.TimeoutError:
                # 单次等待超时，继续循环
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                remaining_time = timeout - elapsed
                continue
                
            except Exception as e:
                logger.error(f"Error during response collection: {e}")
                # 错误恢复：提供重新输入机会
                await self._show_error_and_retry()
                continue
        
        # 总体超时
        raise asyncio.TimeoutError()
```

### 7.2 输入验证逻辑

```python
async def _validate_and_parse_input(self, raw_input: str) -> Optional[PermissionResponse]:
    """验证和解析用户输入"""
    if not raw_input:
        return None
        
    # 安全清洗
    cleaned_input = self._sanitize_input(raw_input)
    
    # 基本验证
    if not self._is_valid_input(cleaned_input):
        return None
        
    # 解析为权限响应
    response = self._parse_to_response(cleaned_input)
    return response

def _sanitize_input(self, raw_input: str) -> str:
    """安全清洗输入"""
    # 去除前后空白
    cleaned = raw_input.strip()
    
    # 限制输入长度
    if len(cleaned) > 100:
        cleaned = cleaned[:100]
        
    # 转换为小写进行统一处理
    return cleaned.lower()

def _is_valid_input(self, cleaned_input: str) -> bool:
    """验证输入有效性"""
    if not cleaned_input:
        return False
        
    # 检查是否只包含有效字符
    valid_chars = set('ynavc')
    return all(char in valid_chars for char in cleaned_input)

def _parse_to_response(self, cleaned_input: str) -> Optional[PermissionResponse]:
    """解析为权限响应"""
    # 完整单词匹配（优先）
    word_mapping = {
        'yes': PermissionResponse.GRANT,
        'no': PermissionResponse.DENY,
        'always': PermissionResponse.ALWAYS,
        'never': PermissionResponse.NEVER,
        'cancel': PermissionResponse.CANCEL
    }
    
    if cleaned_input in word_mapping:
        return word_mapping[cleaned_input]
    
    # 单字符匹配（回退）
    if len(cleaned_input) == 1:
        char_mapping = {
            'y': PermissionResponse.GRANT,
            'n': PermissionResponse.DENY,
            'a': PermissionResponse.ALWAYS,
            'v': PermissionResponse.NEVER,
            'c': PermissionResponse.CANCEL
        }
        return char_mapping.get(cleaned_input[0])
    
    # 无效输入
    return None
```

### 7.3 超时和错误处理

```python
async def _show_countdown(self, remaining_seconds: int) -> None:
    """显示倒计时"""
    countdown_msg = f"⏰ Time remaining: {remaining_seconds}s\n"
    # 发送到TUI显示
    await self._send_to_ui(countdown_msg)

async def _show_invalid_input_error(self) -> None:
    """显示无效输入错误"""
    error_msg = """
❌ Invalid input. Please enter one of:
[Y]es - Grant this permission
[N]o - Deny this permission
[A]lways - Always grant for this tool
[N]ever - Never grant for this tool
[C]ancel - Cancel the operation

Your choice: """
    await self._send_to_ui(error_msg)

async def _show_error_and_retry(self) -> None:
    """显示错误并提供重试机会"""
    error_msg = """
⚠️ An error occurred. Please try again.
Your choice: """
    await self._send_to_ui(error_msg)
```

## 8. 测试策略

### 8.1 单元测试
```python
def test_valid_input_parsing():
    """测试有效输入解析"""
    collector = UserResponseCollector(mock_queue)
    
    test_cases = [
        ("y", PermissionResponse.GRANT),
        ("Y", PermissionResponse.GRANT),
        ("yes", PermissionResponse.GRANT),
        ("n", PermissionResponse.DENY),
        ("N", PermissionResponse.DENY),
        ("no", PermissionResponse.DENY),
        ("a", PermissionResponse.ALWAYS),
        ("A", PermissionResponse.ALWAYS),
        ("always", PermissionResponse.ALWAYS),
        ("v", PermissionResponse.NEVER),
        ("V", PermissionResponse.NEVER),
        ("never", PermissionResponse.NEVER),
        ("c", PermissionResponse.CANCEL),
        ("C", PermissionResponse.CANCEL),
        ("cancel", PermissionResponse.CANCEL),
    ]
    
    for input_str, expected_response in test_cases:
        response = collector._parse_to_response(input_str.lower())
        assert response == expected_response

def test_invalid_input_handling():
    """测试无效输入处理"""
    collector = UserResponseCollector(mock_queue)
    
    invalid_inputs = [
        "",           # 空输入
        "invalid",    # 无效输入
        "123",        # 数字输入
        "xyz",        # 无效字符
        "yess",       # 拼写错误
        "\x00\x01",   # 二进制数据
    ]
    
    for invalid_input in invalid_inputs:
        response = collector._parse_to_response(invalid_input)
        assert response is None

def test_whitespace_input_handling():
    """测试空白字符输入处理"""
    collector = UserResponseCollector(mock_queue)
    
    whitespace_cases = [
        (" y ", PermissionResponse.GRANT),
        ("\t\n", PermissionResponse.DENY),  # 特殊字符但包含'n'
        ("  a  ", PermissionResponse.ALWAYS),
    ]
    
    for input_str, expected_response in whitespace_cases:
        response = collector._validate_and_parse_input(input_str)
        assert response == expected_response

@pytest.mark.asyncio
async def test_timeout_handling():
    """测试超时处理"""
    collector = UserResponseCollector(mock_queue)
    request = PermissionRequestEvent(tool_name="test", args={})
    
    # 不放入任何输入，模拟超时
    response = await collector.collect_response(request, timeout=0.1)
    
    assert response == PermissionResponse.DENY
    assert response.timeout is True
```

### 8.2 集成测试
```python
@pytest.mark.asyncio
async def test_complete_response_collection_flow():
    """测试完整的响应收集流程"""
    user_queue = asyncio.Queue()
    collector = UserResponseCollector(user_queue)
    
    request = PermissionRequestEvent(
        tool_name="read_file",
        args={"path": "test.txt"},
        risk_level="low"
    )
    
    # 模拟用户输入序列
    async def simulate_user_input():
        await asyncio.sleep(0.1)
        await user_queue.put("y")  # 用户选择授予权限
    
    # 启动模拟输入
    input_task = asyncio.create_task(simulate_user_input())
    
    # 收集响应
    response = await collector.collect_response(request, timeout=5.0)
    
    # 等待模拟任务完成
    await input_task
    
    # 验证结果
    assert response == PermissionResponse.GRANT
    assert response.timeout is False
```

## 9. 实施计划

### 第一阶段：基础响应收集（2-3天）
1. 实现UserResponseCollector基础类
2. 实现基本的输入验证和解析
3. 实现异步响应收集机制
4. 编写基础单元测试

### 第二阶段：超时和错误处理（2-3天）
1. 实现超时管理机制
2. 实现倒计时警告系统
3. 实现错误处理和恢复机制
4. 实现特殊输入处理
5. 编写超时和错误处理测试

### 第三阶段：特殊响应处理（2-3天）
1. 实现always/never响应的确认机制
2. 实现确认对话框和二次验证
3. 实现确认超时处理
4. 实现确认失败回退机制
5. 编写特殊响应处理测试

### 第四阶段：集成和优化（2-3天）
1. 集成到TUI界面系统
2. 集成到AgentExecutor
3. 完整流程测试和优化
4. 性能调优和边界测试
5. 用户验收测试

## 10. 验收标准

### 功能验收
- [ ] 用户响应被正确收集和验证
- [ ] 超时机制正常工作，精度达标
- [ ] 特殊响应（always/never）正确处理
- [ ] 错误恢复机制有效工作
- [ ] 输入验证和清洗功能完整

### 性能验收
- [ ] 响应收集时间 < 100ms
- [ ] 超时精度误差 < 1秒
- [ ] 并发处理能力达标
- [ ] 内存使用在合理范围内

### 质量验收
- [ ] 代码覆盖率 > 90%
- [ ] 所有测试通过
- [ ] 代码符合SOLID原则
- [ ] 遵循KISS和YAGNI原则

## 11. 风险评估与缓解

### 技术风险
- **并发复杂性**: 异步处理可能引入竞态条件
  - **缓解**: 使用适当的同步机制，充分测试并发场景
- **超时精度**: 系统负载可能影响超时精度
  - **缓解**: 使用高精度定时器，考虑系统负载影响

### 用户体验风险
- **响应延迟**: 网络或系统延迟可能影响用户体验
  - **缓解**: 优化响应路径，提供及时反馈
- **输入歧义**: 用户输入可能存在歧义
  - **缓解**: 提供清晰的指导和确认机制

## 12. 成功标准

项目成功的衡量标准：
1. **功能完整性**: 所有需求功能100%实现并通过测试
2. **性能达标**: 满足所有性能指标要求
3. **用户体验**: 用户交互流畅，操作直观
4. **代码质量**: 遵循最佳实践，代码可维护性强
5. **系统稳定性**: 在各种异常情况下都能保持稳定运行

---

**文档状态**: ✅ 已完成  
**审查状态**: 待审查  
**实施状态**: 准备开始TDD实现

**下一步**: 基于本规范，开始实现用户响应收集和处理机制的核心功能