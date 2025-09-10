# TUI实现指南 - 修正文档

## 问题分析：实现与测试不匹配的根本原因

### 1. 文档缺失的关键信息

#### 1.1 组件标识符规范缺失
**问题**：测试使用`#log_view`而实现使用`#output_text_area`
**根本原因**：
- TUI_REQUIREMENTS_SPEC.md未明确指定组件ID命名规范
- 测试用例与实现代码缺乏统一的组件标识符约定

#### 1.2 方法调用契约不明确
**问题**：create_session等方法调用方式与测试预期不符
**根本原因**：
- 未明确指定SessionManager.create_session的调用参数和返回值
- 缺乏方法调用时序图和参数规范

#### 1.3 输出消息格式规范缺失
**问题**：实际输出消息与测试断言不匹配
**根本原因**：
- 未定义标准的消息格式模板
- 缺乏国际化消息规范

### 2. 文档更新方案

#### 2.1 组件标识符规范
```yaml
# TUI组件ID规范
components:
  output_area:
    id: "output_text_area"
    type: "TextArea"
    description: "主输出显示区域"
  
  input_area:
    id: "user_input"
    type: "Input"
    description: "用户输入区域"
    
  status_bar:
    id: "status_bar"
    type: "Static"
    description: "状态信息显示"
```

#### 2.2 方法调用契约
```python
# SessionManager.create_session契约
class SessionManager:
    def create_session(
        self, 
        goal: str, 
        session_type: str, 
        participant_ids: List[str]
    ) -> Session:
        """
        创建新会话
        
        参数:
            goal: 会话目标字符串
            session_type: 会话类型("chat", "debate", etc.)
            participant_ids: 参与者ID列表
            
        返回:
            Session对象，包含session_id属性
            
        调用示例:
            session = session_manager.create_session(
                goal="write a project plan",
                session_type="chat", 
                participant_ids=["user", "pa"]
            )
        """
```

#### 2.3 消息格式规范
```python
# 标准消息格式模板
MESSAGE_TEMPLATES = {
    "session_created": "[bold green]> [/bold green]{command} session started with ID: {session_id}",
    "role_created": "[bold blue]> [/bold blue]Role '{role_name}' created successfully.",
    "search_result": "[bold yellow]> [/bold yellow]Searching {target} for: {query}",
    "error": "[bold red]> [/bold red]{message}",
    "info": "[bold cyan]> [/bold cyan]{message}"
}
```

### 3. 测试与实现同步规范

#### 3.1 测试用例设计规范
```python
# 测试用例模板
class TestTUICommandHandlers:
    def test_handle_command_template(self):
        """命令处理测试模板"""
        # 1. 准备mock对象
        mock_session = Mock()
        mock_session.session_id = "expected-session-id"
        
        # 2. 设置mock行为
        self.mock_session_manager.create_session.return_value = mock_session
        
        # 3. 执行命令
        self.tui._handle_command("test args", "", mock_log_view)
        
        # 4. 验证方法调用
        self.mock_session_manager.create_session.assert_called_once_with(
            goal="test args",
            session_type="expected-type",
            participant_ids=["expected", "participants"]
        )
        
        # 5. 验证输出消息
        call_args = mock_log_view.text
        self.assertIn("expected message", call_args)
```

#### 3.2 实现代码规范
```python
# TUI命令处理器实现规范
class DAIP_TUI:
    def _handle_command(self, args: str, current_log: str, log_view: TextArea) -> None:
        """
        命令处理标准实现
        
        参数规范:
            args: 命令参数字符串
            current_log: 当前日志内容
            log_view: TextArea组件实例，使用.text属性而非.update()
        
        实现要求:
            1. 使用log_view.text = ... 而非 log_view.update()
            2. 消息格式必须符合MESSAGE_TEMPLATES
            3. 方法调用必须符合契约规范
        """
```

### 4. 文档更新清单

#### 4.1 需要更新的文档
1. **TUI_REQUIREMENTS_SPEC.md**
   - 添加组件ID规范章节
   - 添加方法调用契约章节
   - 添加消息格式规范章节

2. **TUI_TEST_CASES.md** (新建)
   - 详细的测试用例规范
   - mock对象使用规范
   - 断言格式规范

3. **TUI_DEVELOPER_GUIDE.md** (新建)
   - 实现代码规范
   - 组件使用指南
   - 调试和测试指南

#### 4.2 新增文档
1. **TUI_COMPONENT_SPEC.md**
   - 所有UI组件的详细规范
   - 组件ID和类型定义
   - 事件处理规范

2. **TUI_MESSAGE_SPEC.md**
   - 标准消息格式定义
   - 国际化支持规范
   - 错误消息规范

### 5. 实施建议

#### 5.1 立即行动项
1. 更新TUI_REQUIREMENTS_SPEC.md，添加缺失的规范
2. 创建TUI_TEST_CASES.md，标准化测试用例
3. 修复现有实现以符合新规范

#### 5.2 长期改进
1. 建立代码审查流程，确保实现符合规范
2. 建立自动化测试，验证规范符合性
3. 定期更新文档，保持与实现同步