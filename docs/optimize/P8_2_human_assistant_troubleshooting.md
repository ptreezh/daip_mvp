# P8.2 人类助手系统 - 故障排除 (P8.2 Human Assistant System - Troubleshooting)

## 🚨 常见问题

### 1. 任务分解失败
**症状**: 复杂任务无法正确分解
**可能原因**: 
- 请求表述不清晰
- 缺少必要的上下文
- 任务分解算法问题

**解决方案**:
```python
# 任务分解调试
def debug_task_decomposition(assistant: PersonalAssistant, request: str):
    print(f"原始请求: {request}")
    
    try:
        subtasks = assistant.decompose_task(request)
        print(f"分解结果: {len(subtasks)} 个子任务")
        for i, task in enumerate(subtasks):
            print(f"  {i+1}. {task.description}")
    except Exception as e:
        print(f"任务分解失败: {e}")
        # 尝试简化请求
        simplified_request = simplify_request(request)
        subtasks = assistant.decompose_task(simplified_request)
        return subtasks
```

### 2. 工具执行阻塞
**症状**: 助手在工具执行步骤挂起
**可能原因**: 
- 工具权限未确认
- 工具实现错误
- 参数验证失败

**解决方案**:
```python
import asyncio

async def safe_tool_execution(assistant: PersonalAssistant, tool_name: str, args: Dict):
    try:
        # 设置工具执行超时
        result = await asyncio.wait_for(
            assistant.tool_manager.execute_tool(tool_name, args, assistant.session_context),
            timeout=30
        )
        return result
    except asyncio.TimeoutError:
        print(f"工具 {tool_name} 执行超时")
        return None
    except ToolPermissionRequest as e:
        # 处理权限请求
        print(f"需要权限: {e.tool_name}")
        return await handle_permission_request(e)
```

## 🔧 诊断工具

### 助手功能检查
```python
async def check_assistant_capabilities(assistant: PersonalAssistant):
    capabilities = assistant.get_capabilities()
    print("助手能力:")
    for cap in capabilities:
        print(f"  - {cap}")
    
    # 测试基本功能
    try:
        async for event in assistant.handle_request("你好"):
            print(f"基本功能正常: {type(event).__name__}")
            break
    except Exception as e:
        print(f"基本功能异常: {e}")
```

### 任务执行监控
```python
async def monitor_task_execution(assistant: PersonalAssistant, request: str):
    print(f"开始处理请求: {request}")
    start_time = time.time()
    
    try:
        event_count = 0
        async for event in assistant.handle_request(request):
            event_count += 1
            print(f"事件 {event_count}: {event.type}")
            yield event
    except Exception as e:
        print(f"任务执行失败: {e}")
        raise
    finally:
        end_time = time.time()
        print(f"任务完成，耗时: {end_time - start_time:.2f}秒")
```

## ⚠️ 性能问题

### 响应慢
- **检查**: 复杂任务分解或大量工具调用
- **解决方案**: 优化任务分解算法或并行执行

### 高资源消耗
- **检查**: 长对话或复杂上下文
- **解决方案**: 实现上下文窗口管理

## 🔍 调试技巧

### 详细请求处理日志
```python
async def detailed_request_logging(assistant: PersonalAssistant, user_request: str):
    print(f"=== 开始处理请求 ===")
    print(f"用户请求: {user_request}")
    
    step = 0
    async for event in assistant.handle_request(user_request):
        step += 1
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] 步骤 {step}: {event.type}")
        
        if hasattr(event, 'subtasks'):
            print(f"  子任务: {len(event.subtasks)} 个")
        if hasattr(event, 'tool_name'):
            print(f"  工具: {event.tool_name}")
        if hasattr(event, 'final_response'):
            print(f"  响应长度: {len(event.final_response)} 字符")
        
        yield event
    
    print("=== 请求处理完成 ===")
```

## 📞 支持信息
当寻求支持时，请提供：
1. 完整的错误消息和堆栈跟踪
2. 用户请求内容
3. 相关的配置和上下文信息
4. 涉及的工具或模型信息

---
> **需要集成信息？** 查看 [P8_2_human_assistant_integration.md](P8_2_human_assistant_integration.md)  
> **需要API详情？** 查看 [P8_2_human_assistant_api.md](P8_2_human_assistant_api.md)