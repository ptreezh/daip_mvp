# P6 CLI/TUI界面 - 故障排除 (P6 CLI/TUI Interface - Troubleshooting)

## 🚨 常见问题

### 1. TUI启动失败
**症状**: TUI应用无法启动或立即崩溃
**可能原因**: 
- 终端不支持ANSI颜色
- Textual依赖问题
- 配置文件错误

**解决方案**:
```bash
# 检查终端支持
echo $TERM  # 应显示支持的颜色终端类型
```

```python
# 检查Textual安装
import textual
print(textual.__version__)
```

### 2. 事件流处理中断
**症状**: 代理事件流突然停止
**可能原因**: 
- 异步生成器关闭
- 后端连接断开

**解决方案**:
```python
# 事件流错误处理
async def robust_event_handling(tui: DAIP_TUI, event_stream):
    try:
        async for event in event_stream:
            await tui.handle_agent_event(event)
    except Exception as e:
        print(f"事件流中断: {e}")
        await tui.display_error("连接已断开")
```

## 🔧 诊断工具

### TUI状态检查
```python
def debug_tui_state(tui: DAIP_TUI):
    print(f"TUI状态: {tui.state}")
    print(f"主题: {tui.theme}")
    print(f"当前模式: {tui.current_mode}")
```

### CLI参数验证
```python
def validate_cli_args(**kwargs):
    print("CLI参数验证:")
    for key, value in kwargs.items():
        print(f"  {key}: {value} ({type(value)})")
```

## ⚠️ 性能问题

### UI响应慢
- **检查**: 事件处理逻辑复杂度
- **解决方案**: 优化事件显示和处理

### 高内存使用
- **检查**: 对话历史积累
- **解决方案**: 实现历史清理机制

## 🔍 调试技巧

### TUI调试模式
```python
# 启用TUI调试
import os
os.environ["TEXTUAL"] = "debug"  # 启用Textual调试模式
```

### 事件流调试
```python
async def debug_event_stream(agent_executor, goal: str):
    print(f"开始执行目标: {goal}")
    
    async for event in agent_executor.chat_run(goal):
        print(f"接收事件: {type(event).__name__}")
        print(f"事件内容: {str(event)[:100]}...")  # 限制输出长度
        yield event
```

### 复制功能调试
```python
def debug_copy_functionality(tui: DAIP_TUI):
    try:
        # 测试剪贴板访问
        import pyperclip
        original_content = pyperclip.paste()
        
        test_content = "DAIP-LIVE Copy Test"
        pyperclip.copy(test_content)
        
        pasted_content = pyperclip.paste()
        if pasted_content == test_content:
            print("剪贴板功能正常")
        else:
            print("剪贴板功能异常")
            
        # 恢复原始内容
        pyperclip.copy(original_content)
    except Exception as e:
        print(f"剪贴板功能不可用: {e}")
```

## 📞 支持信息
当寻求支持时，请提供：
1. 完整的错误消息和堆栈跟踪
2. 终端类型和操作系统信息
3. Textual和Python版本
4. 相关的配置文件内容

---
> **需要集成信息？** 查看 [P6_cli_tui_integration.md](P6_cli_tui_integration.md)  
> **需要API详情？** 查看 [P6_cli_tui_api.md](P6_cli_tui_api.md)