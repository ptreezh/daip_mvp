# P7 GUI界面 - 集成指南 (P7 GUI Interface - Integration Guide)

## 🔗 与其他模块的集成

### 与P5代理引擎集成
```python
# GUI调用P5代理引擎
from daip_live.p5_agent_engine.executor import AgentExecutor

async def stream_agent_response_to_gui(goal: str, gui_component):
    agent_executor = container.agent_executor()
    
    # 流式显示代理响应
    async for event in agent_executor.chat_run(goal):
        if event.type == "response_chunk":
            gui_component.update_content(event.delta)
        elif event.type == "final_response":
            gui_component.complete_response(event.content)
```

### 与P6 CLI接口集成
```python
# GUI复用CLI命令逻辑
from daip_live.p6_cli_tui.commands.debate import debate_start

async def gui_debate_handler(topic: str, roles: List[str], rounds: int):
    # 复用CLI命令的实现
    debate_generator = debate_start(topic, ",".join(roles), rounds)
    
    # 在GUI中显示结果
    for event in debate_generator:
        update_gui_with_event(event)
```

## 🔄 流式响应处理

### Streamlit流式显示
```python
import streamlit as st

async def display_streaming_response(agent_executor: AgentExecutor, user_input: str):
    # 初始化显示组件
    response_container = st.container()
    response_text = st.empty()
    
    full_response = ""
    
    async for event in agent_executor.chat_run(user_input):
        if event.type == "response_chunk":
            full_response += event.delta
            response_text.markdown(full_response + "▌")
        elif event.type == "final_response":
            response_text.markdown(full_response)
    
    # 保存到对话历史
    st.session_state.messages.append({"role": "assistant", "content": full_response})
```

## 🔌 使用示例

### 启动GUI应用
```python
from daip_live.p7_gui.app import DAIP_GUI

# 启动GUI
def main():
    gui = DAIP_GUI()
    gui.run()  # 启动Streamlit应用

# 作为服务器运行
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("daip_live.p7_gui.api:app", host="0.0.0.0", port=8000)
```

### 对话界面实现
```python
import streamlit as st
from daip_live.p5_agent_engine.executor import AgentExecutor

def render_chat_interface():
    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 用户输入
    if prompt := st.chat_input("输入您的消息"):
        # 显示用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 获取AI响应
        with st.chat_message("assistant"):
            agent_executor = container.agent_executor()
            response_placeholder = st.empty()
            full_response = ""
            
            async for event in agent_executor.chat_run(prompt):
                if event.type == "response_chunk":
                    full_response += event.delta
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
```

## ⚡ 性能考虑
- **流式处理**: 使用流式响应避免长时间等待
- **状态管理**: 有效管理会话状态
- **异步操作**: 使用异步操作避免UI阻塞

## 🐛 常见集成问题
- **跨域问题**: 配置适当的CORS策略
- **会话状态**: Streamlit会话状态管理
- **异步兼容**: Streamlit与异步代码集成

---
> **需要API详情？** 查看 [P7_gui_api.md](P7_gui_api.md)  
> **需要实现详情？** 查看 [P7_gui_detailed.md](P7_gui_detailed.md)