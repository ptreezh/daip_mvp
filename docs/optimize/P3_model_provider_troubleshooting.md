# P3 模型提供者 - 故障排除 (P3 Model Provider - Troubleshooting)

## 🚨 常见问题

### 1. 模型连接失败
**症状**: 无法连接到AI模型服务
**可能原因**: 
- API密钥错误
- 网络连接问题
- 模型名称拼写错误

**解决方案**:
```python
# 验证API密钥
def validate_api_key(api_key: str) -> bool:
    if not api_key or len(api_key) < 10:  # 最小长度检查
        print("API密钥格式不正确")
        return False
    return True

# 测试连接
async def test_model_connection(model_provider, test_prompt: str = "test"):
    try:
        async for chunk in model_provider.generate(test_prompt):
            return True  # 连接成功
    except Exception as e:
        print(f"连接失败: {e}")
        return False
```

### 2. 本地模型服务未运行
**症状**: 使用Ollama或LlamaCpp时连接失败
**可能原因**: 
- 本地服务未启动
- 端口配置错误

**解决方案**:
```bash
# 检查Ollama服务状态
curl http://localhost:11434/api/tags  # 应返回模型列表
```

## 🔧 诊断工具

### 模型可用性检查
```python
async def check_model_availability(provider, model_name: str):
    try:
        info = await provider.get_model_info(model_name)
        print(f"模型 {model_name} 可用")
        print(f"模型信息: {info}")
        return True
    except Exception as e:
        print(f"模型 {model_name} 不可用: {e}")
        return False
```

### 响应时间监控
```python
import time

async def monitor_response_time(provider, prompt: str):
    start_time = time.time()
    try:
        async for chunk in provider.generate(prompt):
            pass
        end_time = time.time()
        print(f"响应时间: {end_time - start_time:.2f}秒")
    except Exception as e:
        print(f"生成失败: {e}")
```

## ⚠️ 性能问题

### 高延迟响应
- **检查**: 网络连接质量或模型负载
- **解决方案**: 使用更快的模型或本地模型

### 内存使用过高
- **检查**: 长对话或大上下文
- **解决方案**: 实现上下文窗口管理

## 🔍 调试技巧

### 详细错误日志
```python
import logging
import litellm

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)
litellm.set_verbose = True  # 启用LiteLLM详细日志
```

### 请求/响应调试
```python
async def debug_model_request(provider, prompt: str):
    print(f"请求提示: {prompt}")
    print("开始接收响应...")
    
    response = ""
    async for chunk in provider.generate(prompt):
        response += chunk
        print(f"接收分块: {chunk[:50]}...")  # 打印前50个字符
    
    print(f"完整响应: {response}")
    return response
```

## 📞 支持信息
当寻求支持时，请提供：
1. 完整的错误消息和堆栈跟踪
2. 模型配置（去除敏感API密钥）
3. 请求的详细信息
4. 网络连接状态

---
> **需要集成信息？** 查看 [P3_model_provider_integration.md](P3_model_provider_integration.md)  
> **需要API详情？** 查看 [P3_model_provider_api.md](P3_model_provider_api.md)