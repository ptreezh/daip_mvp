# P5 代理引擎 - 故障排除 (P5 Agent Engine - Troubleshooting)

## 🚨 常见问题

### 1. 事件流中断
**症状**: 代理执行过程中事件流停止生成
**可能原因**: 
- 模型提供者调用超时
- 工具执行异常
- 代理状态机卡在某个状态

**解决方案**:
```python
# 检查代理状态
status = agent_executor.get_status()
if status.state == "error":
    # 重置或重启代理
    agent_executor.reset()
```

### 2. 状态机异常
**症状**: 代理状态异常或无法转换
**可能原因**: 
- 状态转换逻辑错误
- 外部依赖异常导致状态停滞

**诊断方法**:
- 检查`get_status()`返回的状态
- 查看日志中的状态转换记录

## 🔧 诊断工具

### 状态检查
```python
# 获取当前状态
status = agent_executor.get_status()
print(f"State: {status.state}, Model: {status.model_name}")
```

### 事件流调试
```python
# 启用详细事件日志
async for event in agent_executor.chat_run(goal):
    print(f"Event: {event.type}, Content: {getattr(event, 'content', 'N/A')}")
    if event.type == "error":
        print(f"Error: {event.message}")
```

## ⚠️ 性能问题

### 高延迟响应
- **检查模型提供者**: 确认模型服务响应正常
- **检查上下文长度**: 过长上下文可能导致模型响应变慢
- **检查工具调用**: 检查是否有耗时过长的工具调用

### 内存使用过高
- **清理长期记忆**: 定期清理不需要的会话历史
- **优化状态管理**: 避免在状态中存储过多数据

## 🔍 调试技巧

### 事件流监控
```python
# 创建事件监控器
class EventMonitor:
    def __init__(self):
        self.event_count = 0
        self.last_event_time = None
    
    async def monitor(self, agent_executor, goal):
        async for event in agent_executor.chat_run(goal):
            self.event_count += 1
            current_time = time.time()
            if self.last_event_time:
                print(f"Event interval: {current_time - self.last_event_time}s")
            self.last_event_time = current_time
            yield event
```

### 状态转换追踪
- 记录所有状态转换以便分析
- 监控状态转换时间

## 📞 支持信息
当寻求支持时，请提供：
1. 代理状态信息 (`get_status()` 输出)
2. 相关事件流日志
3. 错误消息和堆栈跟踪
4. 模型提供者配置

---
> **需要集成信息？** 查看 [P5_agent_engine_integration.md](P5_agent_engine_integration.md)  
> **需要API详情？** 查看 [P5_agent_engine_api.md](P5_agent_engine_api.md)