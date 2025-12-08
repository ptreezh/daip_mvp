# DAIP-LIVE命令系统优化规范

**文档版本**: 1.0  
**制定日期**: 2025-09-19  
**制定人**: iFlow CLI  
**置信度**: 0.96  

## 1. 文档目的

本规范定义DAIP-LIVE系统命令系统优化需求，解决当前存在的：
- 无效命令入口冗余问题
- 模型切换状态栏更新延迟问题  
- Token计算不一致问题
- 用户体验优化需求

## 2. 需求背景

### 2.1 当前问题

基于BMAD kiro's spec规范分析发现：

1. **命令系统冗余**: 存在大量无效/冗余命令入口，违反KISS原则
2. **状态同步延迟**: 模型切换后状态栏未能即时更新，影响用户体验
3. **数据不一致**: Token计算显示区与状态栏数据不匹配
4. **文档不匹配**: 帮助文档与实际实现存在差距

### 2.2 业务价值

- **提升用户体验**: 简化命令结构，减少用户困惑
- **增强系统可靠性**: 确保状态信息实时准确
- **降低维护成本**: 清理冗余代码，提高可维护性
- **符合设计原则**: 遵循KISS/YAGNI/SOLID原则

## 3. 功能需求

### 3.1 命令系统清理 (FR-CMD-001)

**需求描述**: 移除所有无效和冗余的命令入口

**具体要求**:
- 移除CLI中的shortcut命令: `daip pa`, `daip _0`, `daip debate`, `daip v`
- 移除TUI中未实现的命令: `/init`, `/run`
- 统一命令命名规范，避免单字符混淆
- 更新文档匹配实际实现

**验收标准**:
- 冗余命令完全移除，系统功能不受影响
- 剩余命令功能正常，用户可通过标准命令访问所有功能
- 文档与实际实现100%匹配

### 3.2 模型切换即时更新 (FR-MDL-002)

**需求描述**: 模型切换成功后立即更新状态栏信息

**具体要求**:
- 模型切换命令执行后立即刷新状态栏
- 状态栏显示新模型名称和对应Token限制
- Token使用量计数保持连续性（不重置）
- 提供模型切换成功反馈

**验收标准**:
- 模型切换完成后<100ms内状态栏更新
- Token限制准确反映新模型能力
- 用户可明确感知切换成功

### 3.3 Token计算一致性 (FR-TOK-003)

**需求描述**: 修复状态栏与显示区Token数据不一致问题

**具体要求**:
- 以显示区Token数据为准（更准确）
- 状态栏实时同步显示区Token计数
- 实现模型特定的Token限制检测
- 提供Token使用率警告机制

**验收标准**:
- 状态栏与显示区Token数据误差<1%
- Token限制根据当前模型动态调整
- Token使用率达到80%时提供警告

### 3.4 退出机制优化 (FR-EXT-004)

**需求描述**: 优化退出机制，支持Ctrl+E双按退出

**具体要求**:
- 第一次Ctrl+E显示退出确认
- 第二次Ctrl+E立即退出（2秒内有效）
- 提供退出倒计时提示
- 支持传统退出方式兼容性

**验收标准**:
- 退出机制响应时间<200ms
- 用户可明确感知退出流程
- 避免意外退出情况

## 4. 非功能需求

### 4.1 性能要求 (NFR-PERF-001)
- 命令响应时间: <100ms
- 状态栏更新延迟: <100ms
- Token计算精度: 99.9%

### 4.2 可靠性要求 (NFR-REL-002)
- 命令执行成功率: >99.5%
- 状态信息准确率: >99.9%
- 系统崩溃率: <0.1%

### 4.3 可维护性要求 (NFR-MAINT-003)
- 代码复杂度: 每个函数<50行
- 测试覆盖率: >90%
- 文档完整性: 100%

## 5. 技术方案

### 5.1 架构设计

```
用户输入 → 命令解析器 → 命令验证 → 功能执行 → 状态更新 → 显示反馈
     ↓           ↓           ↓           ↓           ↓           ↓
命令清理    有效性检查   权限验证   业务逻辑   实时同步   用户界面
```

### 5.2 核心组件

#### 5.2.1 命令管理器 (CommandManager)
- **职责**: 统一管理所有有效命令
- **接口**: 命令注册、验证、执行
- **实现**: 白名单机制，避免自动发现

#### 5.2.2 状态同步器 (StatusSynchronizer)
- **职责**: 确保状态栏与核心业务数据同步
- **机制**: 事件驱动 + 强制刷新
- **触发**: 模型切换、Token使用、系统状态变化

#### 5.2.3 Token管理器 (TokenManager)
- **职责**: 统一Token计算和限制管理
- **功能**: 模型特定限制、使用率监控、警告机制
- **数据源**: 模型提供商配置 + 实时使用统计

### 5.3 数据流设计

```
模型切换事件 → 配置更新 → 提供商重初始化 → 
Token限制更新 → 状态栏强制刷新 → 用户反馈
```

## 6. 实施计划

### 6.1 第一阶段：命令系统清理 (1-2天)
**任务清单**:
- [ ] 移除CLI冗余shortcut命令
- [ ] 清理TUI未实现命令处理函数
- [ ] 更新帮助文档匹配实际实现
- [ ] 实现命令白名单机制

**TDD测试用例**:
```python
def test_redundant_commands_removed():
    """验证冗余命令已被移除"""
    # 测试CLI命令不存在
    result = subprocess.run(["python", "-m", "daip_live.cli", "pa"], 
                          capture_output=True, text=True)
    assert result.returncode != 0
    assert "not found" in result.stderr.lower()

def test_valid_commands_functional():
    """验证有效命令功能正常"""
    # 测试标准命令仍然可用
    result = subprocess.run(["python", "-m", "daip_live.cli", "run", "--help"], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert "goal" in result.stdout.lower()
```

### 6.2 第二阶段：模型切换即时更新 (2-3天)
**任务清单**:
- [ ] 实现模型切换事件监听
- [ ] 添加状态栏强制刷新机制
- [ ] 实现Token限制动态检测
- [ ] 提供切换成功反馈

**TDD测试用例**:
```python
@pytest.mark.asyncio
async def test_model_switch_immediate_status_update():
    """验证模型切换后状态栏立即更新"""
    # 模拟模型切换
    tui._handle_model_switch("llama3.1")
    
    # 验证状态栏在100ms内更新
    await asyncio.sleep(0.1)
    status_text = tui.get_enhanced_status_text("Ready")
    assert "llama3.1" in status_text
    
@pytest.mark.asyncio  
async def test_token_limits_updated_on_model_switch():
    """验证Token限制随模型切换更新"""
    # 切换到不同Token限制的模型
    tui._handle_model_switch("gpt-4")
    
    # 验证Token限制已更新
    current_used, current_total = tui._real_token_usage
    assert current_total == 8192  # GPT-4 token limit
```

### 6.3 第三阶段：Token计算一致性 (2-3天)
**任务清单**:
- [ ] 统一Token计算逻辑
- [ ] 实现模型特定Token限制映射
- [ ] 添加Token使用率警告
- [ ] 修复状态栏同步问题

**TDD测试用例**:
```python
def test_token_calculation_consistency():
    """验证Token计算一致性"""
    # 模拟Token使用事件
    usage_info = {"total_tokens": 100, "prompt_tokens": 60, "completion_tokens": 40}
    
    # 更新Token使用
    tui.update_token_usage(usage_info)
    
    # 验证状态栏与内部数据一致
    current_used, current_total = tui._real_token_usage
    assert current_used == 100
    assert abs(current_used - tui._display_token_count) < 1  # 误差<1

def test_token_limit_warning():
    """验证Token限制警告机制"""
    # 设置Token使用率达到80%
    tui._real_token_usage = (6554, 8192)  # 80%使用率
    
    # 验证警告被触发
    assert tui._should_show_token_warning() == True
```

### 6.4 第四阶段：退出机制优化 (1-2天)
**任务清单**:
- [ ] 实现Ctrl+E双按退出逻辑
- [ ] 添加退出倒计时提示
- [ ] 提供退出确认机制
- [ ] 保持传统退出方式兼容

**TDD测试用例**:
```python
def test_ctrl_e_double_press_exit():
    """验证Ctrl+E双按退出机制"""
    # 第一次按下Ctrl+E
    result1 = tui._handle_ctrl_e_exit()
    assert result1 == "confirm_exit"  # 显示确认
    
    # 2秒内第二次按下Ctrl+E
    time.sleep(0.5)
    result2 = tui._handle_ctrl_e_exit()
    assert result2 == "exit_immediately"  # 立即退出

def test_ctrl_e_exit_timeout():
    """验证Ctrl+E退出超时机制"""
    # 第一次按下Ctrl+E
    tui._handle_ctrl_e_exit()
    
    # 等待超时（2秒+缓冲）
    time.sleep(2.5)
    
    # 再次按下应重新计时
    result = tui._handle_ctrl_e_exit()
    assert result == "confirm_exit"  # 重新确认
```

## 7. 风险评估与缓解

### 7.1 技术风险
- **风险**: 模型切换时状态更新失败
- **概率**: 中等
- **影响**: 高
- **缓解**: 添加重试机制和降级处理

### 7.2 兼容性风险
- **风险**: 移除命令影响现有用户习惯
- **概率**: 低
- **影响**: 中等
- **缓解**: 提供迁移指导和过渡期支持

### 7.3 性能风险
- **风险**: 即时更新增加系统负载
- **概率**: 低
- **影响**: 中等
- **缓解**: 优化更新频率，使用事件驱动

## 8. 验收标准

### 8.1 功能验收
- ✅ 所有冗余命令已移除，系统功能完整
- ✅ 模型切换后<100ms内状态栏更新
- ✅ Token计算误差<1%
- ✅ Ctrl+E双按退出机制正常工作

### 8.2 质量验收
- ✅ 测试覆盖率>90%
- ✅ 代码审查通过
- ✅ 性能指标达标
- ✅ 文档完整准确

### 8.3 用户验收
- ✅ 命令结构简化，用户易于理解
- ✅ 状态信息实时准确
- ✅ 退出机制直观易用
- ✅ 整体体验显著提升

## 9. 后续规划

### 9.1 短期（1个月内）
- 命令系统插件化架构设计
- 用户自定义命令支持
- 命令执行统计分析

### 9.2 长期（3个月内）
- 命令智能推荐系统
- 多语言命令支持
- 命令执行性能优化

## 10. 附录

### 10.1 术语表
- **BMAD**: Behavior-Driven Analysis and Design
- **KISS**: Keep It Simple, Stupid
- **YAGNI**: You Aren't Gonna Need It
- **SOLID**: 面向对象设计五大原则
- **TDD**: Test-Driven Development

### 10.2 参考文档
- [BMAD kiro's spec规范](../specifications/BMAD_kiro_spec.md)
- [DAIP-LIVE系统架构](../SYSTEM_ARCHITECTURE.md)
- [主控需求文档](../MAIN_CONTROL_DOCUMENT.md)

---

**置信度评估**: 0.96  
**评审状态**: 待评审  
**下一步**: 基于本规范编写TDD测试用例并实施开发