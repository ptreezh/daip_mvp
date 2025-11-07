# TUI权限规则配置命令规范

## 1. 功能概述

在TUI中添加权限规则配置命令，允许用户通过命令行界面查看、设置和管理工具权限规则。

## 2. 命令设计

### 2.1 命令结构
```
/permission <subcommand> [arguments...]
```

### 2.2 子命令

#### 2.2.1 list子命令
```
/permission list
```
- 功能：列出所有权限规则
- 输出：显示默认权限策略和所有工具的权限规则

#### 2.2.2 set子命令
```
/permission set <tool_name> <permission>
```
- 功能：设置工具的权限规则
- 参数：
  - tool_name：工具名称
  - permission：权限策略（allow/deny/ask）
- 输出：成功或失败消息

#### 2.2.3 reset子命令
```
/permission reset <tool_name>
```
- 功能：重置工具权限规则为默认值
- 参数：
  - tool_name：工具名称
- 输出：成功或失败消息

#### 2.2.4 default子命令
```
/permission default <permission>
```
- 功能：设置默认权限策略
- 参数：
  - permission：默认权限策略（allow/deny/ask）
- 输出：成功或失败消息

## 3. 用户界面设计

### 3.1 输出格式

#### 3.1.1 权限规则列表格式
```
Permission Rules:
  Default: ask
  Tool Permissions:
    read_file: allow
    write_file: ask
    execute_command: deny
```

#### 3.1.2 操作成功格式
```
[bold green]> Permission rule for 'tool_name' set to 'allow'[/bold green]
```

#### 3.1.3 操作失败格式
```
[bold red]> Error: Invalid permission value 'invalid'[/bold red]
```

### 3.2 交互设计

#### 3.2.1 参数自动补全
- 工具名称自动补全：根据已注册的工具提供补全建议
- 权限值自动补全：提供allow/deny/ask三个选项的补全

#### 3.2.2 错误处理
- 参数缺失时显示帮助信息
- 无效参数时显示错误信息和使用示例
- 操作失败时显示详细错误信息

## 4. 集成设计

### 4.1 依赖关系
- 权限规则管理器：使用PermissionRuleManager进行权限规则操作
- TUI应用：在DAIP_TUI类中添加命令处理器

### 4.2 数据流
1. 用户输入/permission命令
2. TUI解析命令和参数
3. 调用权限规则管理器执行相应操作
4. 权限规则管理器返回结果
5. TUI格式化并显示结果

## 5. 测试策略

### 5.1 功能测试
1. 命令解析测试
2. 参数验证测试
3. 权限规则操作测试
4. 输出格式测试

### 5.2 集成测试
1. TUI命令与权限规则管理器集成测试
2. 自动补全功能测试
3. 错误处理测试

## 6. 安全考虑

### 6.1 输入验证
- 验证工具名称的有效性
- 验证权限值的合法性
- 防止路径遍历攻击

### 6.2 默认安全
- 默认权限策略保持为"ask"
- 未知工具默认使用全局策略
- 操作失败时提供安全的错误信息

## 7. 性能要求

### 7.1 响应时间
- 命令解析：< 5ms
- 权限规则操作：< 50ms
- 输出显示：< 10ms

### 7.2 内存使用
- 命令处理：< 1MB
- 自动补全缓存：< 100KB