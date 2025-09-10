# TUI组件规范文档

## 1. 组件标识符规范

### 1.1 主界面组件
| 组件名称 | 组件ID | 组件类型 | 用途说明 |
|----------|--------|----------|----------|
| 输出区域 | `#main_log` | RichLog | 显示所有命令输出和系统消息 |
| 输入框 | `#user_input` | Input | 用户命令和消息输入 |
| 状态栏 | `#status_bar` | Static | 显示系统状态信息 |
| 头部 | `#header` | Header | 应用标题栏 |
| 底部 | `#footer` | Footer | 快捷键提示 |

### 1.2 对话框组件
| 组件名称 | 组件ID | 组件类型 | 用途说明 |
|----------|--------|----------|----------|
| 权限对话框 | `#dialog` | Container | 权限请求对话框容器 |
| 权限标签 | `#permission-label` | Label | 显示权限请求信息 |
| 允许按钮 | `#allow` | Button | 权限允许按钮 |
| 拒绝按钮 | `#deny` | Button | 权限拒绝按钮 |

## 2. 组件访问规范

### 2.1 查询方法
```python
# 标准查询方法
log_view = self.query_one("#main_log", RichLog)
user_input = self.query_one("#user_input", Input)
status_bar = self.query_one("#status_bar", Static)
```

### 2.2 更新方法
```python
# 输出区域更新
log_view.write("新的文本内容")

# 状态栏更新
status_bar.update("新的状态信息")

# 输入框清空
user_input.value = ""
```

## 3. 消息格式规范

### 3.1 命令输出格式
所有命令输出必须使用以下格式（由RichLog自动处理）：
```
[颜色标签]> 消息内容
```

### 3.2 颜色标签规范
| 标签 | 颜色 | 用途 |
|------|------|------|
| `[bold green]>` | 绿色 | 成功消息 |
| `[bold red]>` | 红色 | 错误消息 |
| `[bold yellow]>` | 黄色 | 警告/提示消息 |
| `[bold blue]>` | 蓝色 | 信息消息 |
| `[bold cyan]>` | 青色 | 会话相关消息 |
| `[bold magenta]>` | 紫色 | 辩论相关消息 |

### 3.3 会话列表格式
```
[bold cyan]> Session History:
  1. session_id - goal (STATUS)
  2. session_id - goal (STATUS)
```

### 3.4 角色列表格式
```
[bold blue]> Available Roles:
  role_name: persona_description
```

## 4. 测试兼容性规范

### 4.1 Mock对象兼容性
所有命令处理器必须：
1. 使用 `query_one("#main_log", RichLog)` 获取输出组件
2. 使用 `.write()` 方法更新内容

### 4.2 测试断言兼容性
```python
# 正确的测试断言方式
mock_log_view.write.assert_called_with("期望的消息")

# 错误的方式（会导致测试失败）
self.assertIn("期望的消息", mock_text_area.text)
```

## 5. 实现检查清单

### 5.1 组件ID检查
- [ ] 所有组件使用正确的ID
- [ ] 查询方法使用正确的类型注解
- [ ] 更新方法使用正确的属性

### 5.2 消息格式检查
- [ ] 所有输出包含正确的颜色标签
- [ ] 会话列表格式符合规范
- [ ] 角色列表格式符合规范

### 5.3 测试兼容性检查
- [ ] 使用RichLog而不是TextArea
- [ ] 使用.write()方法而不是.text属性
- [ ] 消息格式与测试用例匹配
