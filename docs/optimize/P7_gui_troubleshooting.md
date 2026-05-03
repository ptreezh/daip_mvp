# P7 GUI界面 - 故障排除 (P7 GUI Interface - Troubleshooting)

## 🚨 常见问题

### 1. Streamlit应用无法启动
**症状**: GUI应用无法启动或立即崩溃
**可能原因**: 
- 端口被占用
- 依赖项不兼容
- Streamlit配置问题

**解决方案**:
```bash
# 检查端口占用
netstat -an | grep 8501  # 检查Streamlit默认端口

# 使用不同端口
streamlit run app.py --server.port 8502
```

### 2. 会话状态丢失
**症状**: 刷新页面后对话历史丢失
**可能原因**: 
- Streamlit会话状态管理问题
- 缺少会话状态初始化

**解决方案**:
```python
import streamlit as st

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()

initialize_session_state()
```

## 🔧 诊断工具

### GUI状态检查
```python
def debug_gui_state():
    import streamlit as st
    print("Streamlit会话状态:")
    for key, value in st.session_state.items():
        print(f"  {key}: {type(value).__name__}")
```

### API连接测试
```python
import requests

def test_api_connection(base_url: str = "http://localhost:8000"):
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            print("API连接正常")
            return True
        else:
            print(f"API连接失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"API连接错误: {e}")
        return False
```

## ⚠️ 性能问题

### 响应慢
- **检查**: 大量数据传输或处理
- **解决方案**: 优化数据传输，使用分页

### 内存泄漏
- **检查**: 会话状态积累
- **解决方案**: 清理会话状态或限制历史记录

## 🔍 调试技巧

### Streamlit调试模式
```bash
# 启用Streamlit详细日志
streamlit run app.py --logger.level debug
```

### 流式响应调试
```python
async def debug_streaming_response(agent_executor, user_input: str):
    print(f"开始处理请求: {user_input}")
    
    async for event in agent_executor.chat_run(user_input):
        print(f"事件类型: {event.type}")
        if hasattr(event, 'delta'):
            print(f"事件数据: {event.delta[:50]}...")  # 限制输出长度
        yield event
```

## 📞 支持信息
当寻求支持时，请提供：
1. 完整的错误消息和堆栈跟踪
2. Streamlit和Python版本
3. 浏览器和操作系统信息
4. 相关的配置文件内容

---
> **需要集成信息？** 查看 [P7_gui_integration.md](P7_gui_integration.md)  
> **需要API详情？** 查看 [P7_gui_api.md](P7_gui_api.md)