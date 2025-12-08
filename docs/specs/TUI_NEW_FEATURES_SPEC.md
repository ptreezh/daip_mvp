# TUI新增功能测试规范

## 1. 功能需求

### 1.1 双击CTRL+E退出功能
- **行为**: 连续两次按下CTRL+E键退出应用
- **反馈**: 在状态栏显示提示信息
- **时间窗口**: 两次按键间隔应在合理时间内（如2秒）

### 1.2 /clear命令功能
- **命令**: `/clear`
- **功能**: 清理输出区域屏幕内容
- **效果**: 保留状态栏和输入框，清空主输出区域

### 1.3 输入历史持久化
- **存储**: 最近10条用户输入
- **位置**: 持久化到文件
- **功能**: 应用重启后仍可通过上下键浏览历史
- **格式**: 纯文本，每行一条记录

## 2. TDD测试用例

### 2.1 双击CTRL+E退出测试

```python
def test_double_ctrl_e_exit(self, tui_with_mocks):
    """测试连续两次CTRL+E退出应用"""
    tui = tui_with_mocks
    
    # Mock exit方法
    tui.exit = Mock()
    
    # 模拟第一次CTRL+E
    tui.on_key(Keys.ControlE)
    
    # 验证状态栏提示
    status_bar = tui.query_one("#status_bar")
    assert "再次按 CTRL+E 退出" in str(status_bar.renderable)
    
    # 模拟第二次CTRL+E
    tui.on_key(Keys.ControlE)
    
    # 验证调用了exit方法
    tui.exit.assert_called_once()
```

### 2.2 /clear命令测试

```python
def test_clear_command(self, tui_with_mocks):
    """测试/clear命令清理输出区域"""
    tui = tui_with_mocks
    
    # 获取输出区域
    log_view = tui.query_one("#main_log", RichLog)
    
    # 添加一些内容
    log_view.write("Test content 1")
    log_view.write("Test content 2")
    
    # 执行clear命令
    tui._handle_clear_command("")
    
    # 验证输出区域被清空（需要实现清空逻辑）
    # 注意：RichLog可能需要特殊处理来清空内容
```

### 2.3 输入历史持久化测试

```python
def test_input_history_persistence(self, tmp_path):
    """测试输入历史持久化"""
    history_file = tmp_path / "input_history.txt"
    
    # 创建TUI并设置历史文件路径
    with patch('daip_live.tui.Path') as mock_path:
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.read_text.return_value = "/role list\n/session view\n"
        
        tui = create_tui_with_history_file(history_file)
        
        # 验证历史记录被加载
        assert len(tui._input_history) >= 2
        assert "/role list" in tui._input_history
        assert "/session view" in tui._input_history
```

## 3. 技术实现考虑

### 3.1 双击检测逻辑
- 使用时间戳记录最后一次按键时间
- 检查两次按键间隔是否在阈值内
- 在状态栏显示友好的提示信息

### 3.2 RichLog清空方法
- Textual的RichLog组件可能没有直接的清空方法
- 可能需要通过创建新的RichLog实例或调用特定API

### 3.3 历史文件管理
- 使用JSON或纯文本格式存储
- 考虑文件路径的跨平台兼容性
- 处理文件读写异常

## 4. 验收标准

- [ ] 双击CTRL+E能正常退出应用
- [ ] 状态栏正确显示退出提示
- [ ] /clear命令能清空输出区域
- [ ] 输入历史能正确保存到文件
- [ ] 应用重启能正确加载历史记录
- [ ] 所有新功能都有对应的测试覆盖