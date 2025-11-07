# DAIP-LIVE系统命令清理与状态同步规范

**文档版本**: v1.0  
**制定日期**: 2025-09-19  
**制定人**: iFlow CLI  
**遵循规范**: BMAD kiro's spec, TDD, KISS/YAGNI/SOLID  

## 📋 文档目的

本文档规范了DAIP-LIVE系统中命令结构清理和状态栏同步功能的详细需求、技术方案和实施计划。旨在解决当前系统中存在的命令入口冗余、模型切换状态更新延迟、Token计算不一致等问题。

## 🎯 核心需求

### 1. 命令结构优化需求

#### 1.1 清理无效命令入口
- **需求ID**: CMD-CLEAN-001
- **描述**: 移除所有冗余、无效或未实现的命令入口
- **业务价值**: 简化用户界面，降低学习成本，提升系统可维护性
- **验收标准**: 
  - CLI中无冗余shortcut命令
  - TUI中无未实现命令占位符
  - 文档与实际实现100%匹配

#### 1.2 统一命令命名规范
- **需求ID**: CMD-CLEAN-002
- **描述**: 建立一致的命令命名和分类体系
- **业务价值**: 提升用户体验一致性，便于功能扩展
- **验收标准**:
  - 所有命令遵循描述性命名（避免单字符）
  - 命令分类清晰（系统/模型/知识库/会话/角色）
  - 自动完成建议准确且有序

### 2. 状态栏同步需求

#### 2.1 模型切换即时更新
- **需求ID**: STATUS-SYNC-001
- **描述**: 模型切换成功后立即更新状态栏显示
- **业务价值**: 提供实时、准确的系统状态反馈
- **性能要求**: 状态更新延迟 < 100ms
- **验收标准**:
  - 模型名称立即更新
  - Token限制同步更新
  - 状态指示器正确反映

#### 2.2 Token计算一致性
- **需求ID**: STATUS-SYNC-002
- **描述**: 确保状态栏Token数据与显示区完全一致
- **业务价值**: 提供可靠的系统监控信息
- **精度要求**: Token计数误差 = 0
- **验收标准**:
  - 状态栏与显示区Token数据实时同步
  - 模型切换时Token限制准确更新
  - Token使用率计算精确

## 🏗️ 技术架构规范

### 3. 命令结构架构

#### 3.1 命令分类体系
```
系统命令 (System)
├── /help          - 显示帮助信息
├── /quit          - 退出应用
├── /clear         - 清空输出区域
└── /status        - 显示系统状态

模型命令 (Model)
├── /model list    - 列出可用模型
├── /model switch  - 切换模型
├── /model info    - 显示当前模型信息
└── /model metrics - 显示模型性能指标

知识库命令 (Knowledge)
├── /knowledge sync   - 同步知识库
├── /knowledge search - 搜索知识库
└── /knowledge info   - 显示知识库状态

会话命令 (Session)
├── /session list   - 列出会话
├── /session view   - 查看会话详情
├── /session clear  - 清除当前会话
└── /session reset  - 重置会话上下文

角色命令 (Role)
├── /role list      - 列出可用角色
├── /role view      - 查看角色详情
└── /role switch    - 切换角色

个人助手 (Assistant)
└── /pa <goal>      - 启动个人助手会话

辩论系统 (Debate)
└── /debate start   - 启动辩论模式
```

#### 3.2 命令注册机制
```python
# 统一命令注册表
COMMAND_REGISTRY = {
    "system": {
        "help": {"handler": "_handle_help_command", "description": "显示帮助信息"},
        "quit": {"handler": "_handle_quit_command", "description": "退出应用"},
        "clear": {"handler": "_handle_clear_command", "description": "清空输出区域"},
        "status": {"handler": "_handle_status_command", "description": "显示系统状态"}
    },
    "model": {
        "list": {"handler": "_handle_model_list_command", "description": "列出可用模型"},
        "switch": {"handler": "_handle_model_switch_command", "description": "切换模型"},
        "info": {"handler": "_handle_model_info_command", "description": "显示当前模型信息"}
    }
    # ... 其他分类
}
```

### 4. 状态栏同步架构

#### 4.1 状态数据模型
```python
@dataclass
class StatusBarData:
    current_model: str
    token_used: int
    token_total: int
    token_percentage: float
    request_count: int
    avg_latency: float
    system_status: str
    debate_participants: Dict[str, str]  # participant -> model mapping
```

#### 4.2 同步事件机制
```python
# 状态同步事件
class ModelSwitchedEvent(Message):
    """模型切换完成事件"""
    def __init__(self, old_model: str, new_model: str):
        self.old_model = old_model
        self.new_model = new_model

class TokenUsageUpdatedEvent(Message):
    """Token使用量更新事件"""
    def __init__(self, usage_info: dict):
        self.usage_info = usage_info

class StatusSyncEvent(Message):
    """状态栏强制同步事件"""
    pass
```

#### 4.3 同步流程规范
```
模型切换触发 → 配置更新 → 提供商重新初始化 → 
状态数据更新 → 同步事件发布 → 状态栏立即刷新 → 
用户界面更新完成
```

## 🔧 详细技术方案

### 5. 命令清理实施方案

#### 5.1 CLI命令清理
**目标文件**: `src/daip_live/cli.py`
**清理范围**: 行号350-385

**移除函数**:
```python
# 删除这些冗余函数
@app.command("pa")
def pa(goal: str = typer.Argument(..., help="Goal for the agent")):
    """Personal assistant shortcut - REDUNDANT with 'run'"""
    
@app.command("_0") 
def _0(query: str = typer.Argument(None, help="Query for knowledge base")):
    """Knowledge shortcut - INCOMPLETE implementation"""
    
@app.command("debate")
def debate(topic: str = typer.Argument(..., help="Debate topic")):
    """Debate shortcut - REDUNDANT with 'debate start'"""
    
@app.command("v")
def v(query: str = typer.Argument(None, help="Session query")):
    """Session shortcut - INCOMPLETE implementation"""
```

**保留函数**:
```python
# 保留核心功能函数
@app.command("run")
def run(goal: str = typer.Argument(..., help="Goal for the agent")):
    # 标准个人助手启动
    
@app.command("knowledge")
def knowledge():
    # 知识库管理主命令
    
@app.command("debate")
def debate():
    # 辩论系统主命令
```

#### 5.2 TUI命令清理
**目标文件**: `src/daip_live/tui.py`
**清理范围**: 未实现命令处理函数

**移除函数**:
```python
# 删除未实现或重复的功能
async def _handle_init_command(self, args: List[str]) -> None:
    """配置初始化 - 未实现"""
    # 完全删除此函数
    
async def _handle_run_command(self, args: List[str]) -> None:
    """运行代理 - 与_handle_pa_command重复"""
    # 删除此函数，统一使用/pa
```

**清理自动完成机制**:
```python
# 替换动态发现为明确白名单
_AVAILABLE_COMMANDS = [
    ("/help", "Display help information"),
    ("/quit", "Exit the application"),
    ("/clear", "Clear the output area"),
    ("/pa", "Start personal assistant"),
    ("/model list", "List available models"),
    ("/model switch", "Switch to a different model"),
    ("/model info", "Show current model information"),
    ("/knowledge sync", "Sync knowledge base"),
    ("/knowledge search", "Search knowledge base"),
    ("/session list", "List sessions"),
    ("/session view", "View session details"),
    ("/session clear", "Clear current session"),
    ("/role list", "List available roles"),
    ("/role view", "View role details"),
    ("/debate start", "Start a debate"),
]
```

### 6. 状态栏同步实施方案

#### 6.1 模型切换即时更新
**目标文件**: `src/daip_live/tui.py`
**目标方法**: `_handle_model_switch()`

**增强实现**:
```python
async def _handle_model_switch(self, args: List[str]) -> None:
    """Enhanced model switching with immediate status update."""
    if not args:
        self._update_log_view("[red]请指定要切换的模型名称[/red]")
        return
        
    model_name = args[0]
    
    # 执行模型切换
    success = await self._perform_model_switch(model_name)
    
    if success:
        # 立即更新状态栏 - 关键修复
        self._update_current_model(f"{self._model_provider.config.model}")
        
        # 强制状态栏刷新
        self._force_status_bar_refresh()
        
        # 发布同步事件
        self.post_message(ModelSwitchedEvent(
            old_model=self._previous_model,
            new_model=model_name
        ))
        
        self._update_log_view(f"[green]✅ 模型已切换至: {model_name}[/green]")
    else:
        self._update_log_view(f"[red]❌ 模型切换失败: {model_name}[/red]")

def _force_status_bar_refresh(self) -> None:
    """Force immediate status bar refresh with current data."""
    # 更新所有状态数据
    self._update_model_metrics()
    self._update_token_display()
    
    # 强制刷新显示
    self._update_status_bar("Ready")
    
    # 确保UI线程同步
    self.call_later(self._refresh_status_bar_display)
```

#### 6.2 Token计算一致性修复
**目标文件**: `src/daip_live/tui.py`
**目标方法**: `update_token_usage()`, `get_enhanced_status_text()`

**增强实现**:
```python
def update_token_usage(self, usage_info: dict) -> None:
    """Enhanced token usage tracking with consistency guarantees."""
    if not usage_info:
        return
        
    # 提取准确的Token使用数据
    prompt_tokens = usage_info.get('prompt_tokens', 0)
    completion_tokens = usage_info.get('completion_tokens', 0)
    total_tokens = usage_info.get('total_tokens', prompt_tokens + completion_tokens)
    
    # 获取当前模型的Token限制
    current_limit = self._get_current_model_token_limit()
    
    # 更新真实Token使用数据
    self._real_token_usage = (total_tokens, current_limit)
    
    # 确保显示区数据同步
    self._sync_display_token_data(total_tokens, current_limit)
    
    # 强制状态栏更新
    self._update_status_bar("Token updated")

def _get_current_model_token_limit(self) -> int:
    """Get token limit for current model from provider or config."""
    # 模型特定的Token限制映射
    model_limits = {
        "llama3": 8192,
        "llama3.1": 128000,
        "llama3:8b": 8192,
        "llama3:70b": 8192,
        "gpt-4": 8192,
        "gpt-3.5-turbo": 4096,
        "claude-3": 200000,
    }
    
    current_model = self._current_model or "llama3"
    base_model = current_model.split(":")[0].lower()
    
    return model_limits.get(base_model, 8192)  # 默认回退值

def _sync_display_token_data(self, used: int, total: int) -> None:
    """Synchronize token data between display and status bar."""
    # 更新显示区的Token数据
    if hasattr(self, '_display_token_tracker'):
        self._display_token_tracker.update(used, total)
    
    # 更新内部跟踪变量
    self._token_usage = (used, total)
    self._real_token_usage = (used, total)
```

## 🧪 测试策略

### 7. TDD测试用例设计

#### 7.1 命令清理测试
**测试文件**: `tests/test_command_cleanup.py`

```python
class TestCommandCleanup:
    """测试命令清理功能"""
    
    def test_redundant_cli_commands_removed(self):
        """验证CLI冗余命令已被移除"""
        # 测试daip pa命令不存在
        result = subprocess.run(["python", "-m", "daip", "pa", "test"], 
                              capture_output=True, text=True)
        assert result.returncode != 0
        assert "pa" not in result.stdout
        
    def test_unimplemented_tui_commands_removed(self):
        """验证TUI未实现命令已被移除"""
        # 测试/init命令不存在
        tui = DAIP_TUI()
        result = tui._handle_command("/init")
        assert result is False  # 命令不存在
        
    def test_command_naming_consistency(self):
        """验证命令命名一致性"""
        # 所有命令应使用描述性名称
        commands = tui._get_available_commands()
        for cmd, _ in commands:
            assert len(cmd) > 2  # 避免单字符命令
            assert "_" not in cmd  # 避免内部命名
```

#### 7.2 状态栏同步测试
**测试文件**: `tests/test_status_bar_sync.py`

```python
class TestStatusBarSync:
    """测试状态栏同步功能"""
    
    @pytest.mark.asyncio
    async def test_model_switch_immediate_update(self):
        """测试模型切换立即更新状态栏"""
        tui = DAIP_TUI()
        old_model = tui._current_model
        
        # 执行模型切换
        await tui._handle_model_switch(["llama3:8b"])
        
        # 验证状态栏立即更新
        assert tui._current_model == "llama3:8b"
        assert tui._status_bar_updated_immediately is True
        
    def test_token_calculation_consistency(self):
        """测试Token计算一致性"""
        tui = DAIP_TUI()
        
        # 模拟Token使用事件
        usage_info = {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        tui.update_token_usage(usage_info)
        
        # 验证状态栏与显示区数据一致
        status_tokens = tui._get_status_bar_token_data()
        display_tokens = tui._get_display_token_data()
        
        assert status_tokens == display_tokens
        assert status_tokens["used"] == 150
        
    def test_model_specific_token_limits(self):
        """测试模型特定Token限制"""
        tui = DAIP_TUI()
        
        # 测试不同模型的Token限制
        test_cases = [
            ("llama3", 8192),
            ("llama3.1", 128000),
            ("gpt-4", 8192),
        ]
        
        for model, expected_limit in test_cases:
            tui._update_token_limits_for_model(model)
            _, limit = tui._real_token_usage
            assert limit == expected_limit
```

## 📊 性能基准

### 8. 性能要求

#### 8.1 响应时间基准
- **命令识别**: < 50ms
- **状态栏更新**: < 100ms
- **模型切换完成**: < 500ms
- **Token数据同步**: < 10ms

#### 8.2 资源使用基准
- **内存增量**: < 5MB
- **CPU使用率峰值**: < 10%
- **磁盘I/O**: 最小化配置文件读写

### 9. 兼容性要求

#### 9.1 向后兼容性
- 保留所有有效现有命令的功能
- 维护现有的命令参数格式
- 确保用户脚本和自动化工具继续工作

#### 9.2 向前扩展性
- 命令注册机制支持插件化扩展
- 状态栏架构支持新指标添加
- 配置格式支持未来功能扩展

## 🔍 风险评估与缓解

### 10. 技术风险

#### 10.1 高风险项
1. **状态栏更新性能影响**
   - 风险：频繁更新可能影响UI响应性
   - 缓解：实现批量更新和节流机制
   - 置信度：0.92

2. **命令清理影响现有工作流**
   - 风险：用户可能依赖被移除的命令
   - 缓解：提供迁移指南和兼容性警告
   - 置信度：0.89

#### 10.2 中风险项
1. **Token限制映射准确性**
   - 风险：模型Token限制映射可能不准确
   - 缓解：建立动态检测机制，定期更新映射
   - 置信度：0.85

2. **多模型环境下的状态同步**
   - 风险：辩论模式下多模型状态管理复杂
   - 缓解：实现专门的辩论状态管理逻辑
   - 置信度：0.88

## 📈 实施计划

### 11. 分阶段实施

#### 阶段1：命令清理（优先级：高，预计：2天）
- [ ] 移除CLI冗余shortcut命令
- [ ] 清理TUI未实现命令
- [ ] 更新命令文档
- [ ] 编写命令清理测试用例

#### 阶段2：状态栏同步框架（优先级：高，预计：3天）
- [ ] 实现状态同步事件机制
- [ ] 增强模型切换即时更新
- [ ] 建立Token计算一致性框架
- [ ] 编写状态同步测试用例

#### 阶段3：Token计算修复（优先级：中，预计：2天）
- [ ] 实现动态Token限制检测
- [ ] 修复Token使用事件处理
- [ ] 优化显示区数据同步
- [ ] 性能测试和优化

#### 阶段4：集成测试（优先级：中，预计：1天）
- [ ] 端到端功能测试
- [ ] 性能基准测试
- [ ] 用户体验测试
- [ ] 文档最终更新

### 12. 验收标准

#### 12.1 功能验收
- ✅ 所有冗余命令已移除且无功能回归
- ✅ 模型切换后状态栏在100ms内更新
- ✅ Token计算误差为0
- ✅ 所有测试用例通过

#### 12.2 性能验收
- ✅ 命令响应时间 < 50ms
- ✅ 状态更新延迟 < 100ms
- ✅ 内存使用增量 < 5MB
- ✅ CPU使用率峰值 < 10%

#### 12.3 质量验收
- ✅ 代码覆盖率 > 90%
- ✅ 无Pylint警告
- ✅ 通过mypy类型检查
- ✅ 符合SOLID设计原则

## 📋 任务清单

基于本规范，制定以下可执行任务：

### 立即执行任务（置信度 > 0.95）
1. **移除CLI冗余命令** - 置信度：0.98
2. **清理TUI未实现命令** - 置信度：0.97
3. **实现状态栏即时更新机制** - 置信度：0.94
4. **修复Token计算一致性** - 置信度：0.92

### 后续优化任务（置信度 > 0.90）
1. **统一命令命名规范** - 置信度：0.91
2. **增强自动完成机制** - 置信度：0.89
3. **优化辩论模式状态管理** - 置信度：0.88

## 🎯 总结

本规范文档基于BMAD kiro's spec原则，详细定义了DAIP-LIVE系统命令清理与状态同步的完整需求。通过严格的TDD驱动开发流程，确保实施过程中无歧义、高置信度，最终交付符合KISS、YAGNI、SOLID设计原则的高质量代码。

**整体实施置信度：0.94**

每个任务都有明确的上下文、验收标准和实施路径，确保开发团队能够高效、准确地完成所有需求。