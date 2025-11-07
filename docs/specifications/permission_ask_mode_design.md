# 权限Ask模式交互流程设计规范

## 设计目标

实现一个完整的权限Ask模式交互系统，允许用户在工具执行前进行确认，提供良好的用户体验和安全的工具调用控制。

## 当前状态分析

### ✅ 已实现功能
- PermissionRequestEvent事件生成
- ToolPermissionRequest异常处理
- 权限拒绝时的优雅降级

### ❌ 缺失功能
- 用户响应处理机制
- 权限确认状态管理
- 交互式权限确认流程
- 权限决策持久化

## 设计方案

### 1. 交互流程设计

```
工具调用请求 → 权限检查(ask) → 生成PermissionRequestEvent → 用户确认 → 执行/拒绝 → 结果反馈
                    ↓
                权限拒绝 → 优雅降级 → 继续执行
```

### 2. 用户响应处理机制

#### 2.1 响应类型定义
```python
class PermissionResponse(Enum):
    GRANT = "grant"      # 授予权限
    DENY = "deny"        # 拒绝权限  
    ALWAYS = "always"    # 始终授予（记住选择）
    NEVER = "never"      # 永不授予（记住选择）
```

#### 2.2 响应收集机制
- **TUI界面**：通过用户输入队列收集响应
- **CLI界面**：命令行交互式确认
- **GUI界面**：图形界面确认对话框
- **配置文件**：预设权限规则

### 3. 状态管理设计

#### 3.1 会话状态扩展
```python
class PermissionState(Enum):
    PENDING = "pending"      # 等待用户确认
    GRANTED = "granted"      # 已授予
    DENIED = "denied"        # 已拒绝
    REMEMBERED = "remembered" # 已记住选择
```

#### 3.2 权限上下文管理
- 当前权限请求状态
- 用户响应历史
- 记住的选择
- 临时权限授予

### 4. 用户界面设计

#### 4.1 TUI界面展示
```
═══════════════════════════════════════════════════════════════
🔒 TOOL PERMISSION REQUEST
═══════════════════════════════════════════════════════════════

Tool: read_file
Arguments: {'path': 'sensitive_data.txt'}
Description: Read file contents from the specified path

⚠️  This tool will access file system resources.

═══════════════════════════════════════════════════════════════
Options:
[Y] Yes, grant this permission
[N] No, deny this permission  
[A] Always grant for this tool
[V] Never grant for this tool
[C] Cancel operation
═══════════════════════════════════════════════════════════════

Your choice: 
```

#### 4.2 命令行交互
```bash
$ daip agent run "analyze my data"
🔒 Permission required for tool 'read_file' with args: {'path': 'data.csv'}
Grant permission? [Y/n/a/v/c]: y
✅ Permission granted. Executing tool...
```

### 5. 权限决策持久化

#### 5.1 记住选择机制
- 用户选择存储在本地配置文件
- 基于工具名称和参数模式匹配
- 支持通配符和正则表达式
- 可手动编辑和管理

#### 5.2 权限规则格式
```yaml
permission_rules:
  - tool: "read_file"
    pattern: "*.txt"
    decision: "always"
    description: "Always allow reading text files"
    
  - tool: "write_file" 
    pattern: "sensitive_*"
    decision: "never"
    description: "Never allow writing to sensitive files"
    
  - tool: "execute_command"
    pattern: ".*"
    decision: "ask"
    description: "Always ask for command execution"
```

### 6. 安全考虑

#### 6.1 权限提升保护
- 防止恶意工具绕过权限系统
- 敏感操作需要额外确认
- 权限变更需要用户明确授权
- 审计日志记录所有权限决策

#### 6.2 默认安全策略
- 默认权限为 "ask"（最严格）
- 新工具首次使用必须确认
- 危险操作特殊标记和处理
- 权限规则变更通知用户

### 7. 实现计划

#### 阶段1：基础框架（当前）
- [ ] PermissionResponse枚举定义
- [ ] 权限响应处理逻辑
- [ ] 用户输入队列集成

#### 阶段2：TUI界面（下一步）
- [ ] 权限请求界面设计
- [ ] 用户响应收集机制
- [ ] 选项解析和处理

#### 阶段3：持久化（后续）
- [ ] 权限规则存储
- [ ] 记住选择实现
- [ ] 配置文件管理

#### 阶段4：高级功能（扩展）
- [ ] 权限规则编辑器
- [ ] 审计日志系统
- [ ] 权限继承和分组

## 验收标准

### 功能验收
- [ ] 权限请求正确显示给用户
- [ ] 用户响应被正确收集和处理
- [ ] 权限决策影响工具执行结果
- [ ] 记住选择功能正常工作
- [ ] 权限规则持久化有效

### 性能验收
- [ ] 权限确认不阻塞系统响应
- [ ] 权限检查快速完成（<100ms）
- [ ] 大量权限规则高效匹配
- [ ] 内存使用合理，无泄漏

### 用户体验验收
- [ ] 界面清晰易懂
- [ ] 操作流程直观
- [ ] 错误信息友好
- [ ] 帮助信息完整

## 风险评估

### 技术风险
- **复杂度**：多界面支持增加系统复杂度
- **兼容性**：不同平台用户输入处理差异
- **性能**：权限规则匹配可能影响性能

### 缓解措施
- 模块化设计，逐步实施
- 充分测试，确保稳定性
- 性能监控和优化
- 用户反馈收集和改进

## 总结

本设计旨在建立一个完整、安全、用户友好的权限Ask模式交互系统，通过多层次的确认机制和灵活的规则配置，实现既安全又便利的工具调用控制。系统设计考虑了可扩展性、可维护性和用户体验，为DAIP-LIVE平台提供可靠的权限管理基础。