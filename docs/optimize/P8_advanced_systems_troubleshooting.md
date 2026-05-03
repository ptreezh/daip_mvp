# P8 高级功能系统 - 故障排除 (P8 Advanced Systems - Troubleshooting)

## 🚨 常见问题

### 1. 辩论系统启动失败
**症状**: 辩论无法启动或立即失败
**可能原因**: 
- 角色配置不正确
- 模型服务不可用
- 参数验证失败

**解决方案**:
```python
# 检查辩论参数
def validate_debate_params(topic: str, roles: List[str], rounds: int):
    if not topic.strip():
        raise ValueError("辩论主题不能为空")
    
    if len(roles) < 2:
        raise ValueError("至少需要两个角色参与辩论")
    
    if rounds <= 0:
        raise ValueError("辩论轮数必须大于0")
```

### 2. 助手任务执行超时
**症状**: 任务长时间未完成
**可能原因**: 
- 复杂任务分解不当
- 模型响应慢
- 网络问题

**解决方案**:
```python
import asyncio

async def execute_with_timeout(assistant, request: str, timeout: int = 300):
    try:
        result = await asyncio.wait_for(
            assistant.handle_request(request), 
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        print("任务执行超时")
        return None
```

## 🔧 诊断工具

### 系统状态检查
```python
async def check_advanced_systems_status():
    # 检查辩论系统
    debate_manager = container.debate_manager()
    debate_status = debate_manager.get_status()
    print(f"辩论系统状态: {debate_status}")
    
    # 检查助手系统
    assistant = container.personal_assistant()
    assistant_status = assistant.get_status()
    print(f"助手系统状态: {assistant_status}")
    
    # 检查维基系统
    wiki_manager = container.wiki_manager()
    wiki_status = wiki_manager.get_status()
    print(f"维基系统状态: {wiki_status}")
```

### 事件流监控
```python
async def monitor_event_stream(system, *args, **kwargs):
    print("开始监控事件流...")
    start_time = time.time()
    
    event_count = 0
    async for event in system.execute(*args, **kwargs):
        event_count += 1
        print(f"事件 {event_count}: {type(event).__name__}")
        yield event
    
    end_time = time.time()
    print(f"事件流完成，共 {event_count} 个事件，耗时 {end_time - start_time:.2f} 秒")
```

## ⚠️ 性能问题

### 高延迟响应
- **检查**: 模型调用或网络延迟
- **解决方案**: 优化模型配置或使用本地模型

### 内存使用过高
- **检查**: 长对话或大量历史数据
- **解决方案**: 实现历史清理机制

## 🔍 调试技巧

### 辩论系统调试
```python
async def debug_debate_system(debate_manager, topic: str, roles: List[str]):
    print(f"准备辩论: {topic}")
    print(f"参与角色: {roles}")
    
    async for event in debate_manager.run_debate(topic, roles, rounds=1):
        print(f"辩论事件: {type(event).__name__}")
        if hasattr(event, 'participant'):
            print(f"参与者: {event.participant}")
        if hasattr(event, 'content_preview'):
            print(f"内容预览: {event.content_preview[:50]}...")
        yield event
```

### 助手系统调试
```python
async def debug_assistant_system(assistant, request: str):
    print(f"处理请求: {request}")
    
    async for event in assistant.handle_request(request):
        print(f"助手事件: {type(event).__name__}")
        if hasattr(event, 'content'):
            print(f"内容: {event.content[:100]}...")
        yield event
```

## 📞 支持信息
当寻求支持时，请提供：
1. 完整的错误消息和堆栈跟踪
2. 系统参数和配置信息
3. 涉及的代码示例
4. 相关模块的状态信息

---
> **需要集成信息？** 查看 [P8_advanced_systems_integration.md](P8_advanced_systems_integration.md)  
> **需要API详情？** 查看 [P8_advanced_systems_api.md](P8_advanced_systems_api.md)