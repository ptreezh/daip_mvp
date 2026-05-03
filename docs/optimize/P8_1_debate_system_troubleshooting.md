# P8.1 辩论系统 - 故障排除 (P8.1 Debate System - Troubleshooting)

## 🚨 常见问题

### 1. 辩论角色加载失败
**症状**: 指定的角色无法加载或识别
**可能原因**: 
- 角色配置文件不存在
- 角色名称拼写错误
- 角色YAML格式错误

**解决方案**:
```python
# 检查可用角色
def debug_available_roles(debate_manager: DebateManager):
    available_roles = debate_manager.get_available_roles()
    print(f"可用角色: {available_roles}")
    
    # 尝试加载特定角色
    for role_name in available_roles:
        try:
            role = debate_manager.role_manager.get_role_by_name(role_name)
            print(f"✓ 角色 '{role_name}' 加载成功")
        except Exception as e:
            print(f"✗ 角色 '{role_name}' 加载失败: {e}")
```

### 2. 模型调用失败
**症状**: 辩论过程中模型调用失败或超时
**可能原因**: 
- API密钥错误
- 模型服务不可用
- 网络连接问题

**解决方案**:
```python
# 检查模型连接
async def test_model_connection(debate_manager: DebateManager):
    try:
        # 尝试简单模型调用
        async for chunk in debate_manager.model_provider.generate("test", {"model": "gpt-4o"}):
            print(f"模型连接正常: {chunk}")
            break
    except Exception as e:
        print(f"模型连接失败: {e}")
```

## 🔧 诊断工具

### 辩论流程监控
```python
async def monitor_debate_progress(debate_manager: DebateManager, topic: str, roles: List[str]):
    print(f"启动辩论监控: {topic}")
    print(f"角色: {roles}")
    
    start_time = time.time()
    event_count = 0
    
    try:
        async for event in debate_manager.run_debate(topic, roles, rounds=1):
            event_count += 1
            print(f"事件 {event_count}: {event.type}")
            if hasattr(event, 'participant'):
                print(f"  参与者: {event.participant}")
            yield event
    except Exception as e:
        print(f"辩论过程中出现错误: {e}")
        raise
    finally:
        end_time = time.time()
        print(f"辩论监控完成，耗时: {end_time - start_time:.2f}秒，事件数: {event_count}")
```

### 配置验证
```python
def validate_debate_configuration(debate_manager: DebateManager, roles: List[str]):
    # 验证角色配置
    for role_name in roles:
        role = debate_manager.role_manager.get_role_by_name(role_name)
        if not role:
            print(f"错误: 角色 '{role_name}' 不存在")
            return False
        
        print(f"角色 '{role_name}' 验证通过")
        print(f"  工具: {role.tools}")
        print(f"  模型配置: {role.model_config}")
    
    return True
```

## ⚠️ 性能问题

### 辩论响应慢
- **检查**: 模型响应时间或网络延迟
- **解决方案**: 使用更快的模型或本地模型

### 高资源消耗
- **检查**: 多角色或多轮次辩论
- **解决方案**: 优化并发处理或限制辩论复杂度

## 🔍 调试技巧

### 详细辩论日志
```python
async def detailed_debate_logging(debate_manager: DebateManager, topic: str, roles: List[str]):
    print(f"=== 辩论开始: {topic} ===")
    print(f"角色: {roles}")
    
    async for event in debate_manager.run_debate(topic, roles, rounds=1):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {event.type.upper()}")
        
        if hasattr(event, 'participant'):
            print(f"  参与者: {event.participant}")
        if hasattr(event, 'content_preview'):
            print(f"  预览: {event.content_preview[:60]}...")
        if hasattr(event, 'token_count'):
            print(f"  Token数: {event.token_count}")
            
        yield event
    
    print("=== 辩论结束 ===")
```

## 📞 支持信息
当寻求支持时，请提供：
1. 完整的错误消息和堆栈跟踪
2. 辩论主题和角色配置
3. 相关的模型配置信息
4. 网络连接状态

---
> **需要集成信息？** 查看 [P8_1_debate_system_integration.md](P8_1_debate_system_integration.md)  
> **需要API详情？** 查看 [P8_1_debate_system_api.md](P8_1_debate_system_api.md)