# Personal Intelligence Hub - Secretariat 规范

**文档状态:** 最终版 - 可用于实施
**版本:** 1.0
**日期:** 2025-08-06

## 📋 文档范围

本文档详细定义了**The Secretariat**入口的技术规范和实现要求。Secretariat是面向效率型用户的简化界面，专注于快速任务执行和结果交付。

---

## 🎯 设计理念

### 核心原则
- **极简主义**: 干净、无干扰的聊天界面
- **自动化**: 后台自动执行所有必要的工作流
- **结果导向**: 专注最终结果，隐藏过程复杂性
- **按需透明**: 用户可选择查看执行过程

### 用户画像
- **效率型用户**: 追求快速结果
- **任务导向**: 明确目标，最小化交互
- **信任系统**: 愿意委托AI执行复杂任务
- **时间敏感**: 重视任务完成时间

---

## 🏗️ 技术架构

### 组件结构
```
Secretariat/
├── Frontend/
│   ├── ChatInterface/          # 主聊天界面
│   ├── TransparencyMonitor/    # 透明度监控器
│   └── WebSocketClient/        # WebSocket客户端
└── Backend/
    ├── PersonalAssistantService/ # 个人助手服务
    ├── WorkflowOrchestrator/    # 工作流编排器
    └── ProcessMonitor/          # 过程监控器
```

### 关键依赖
- **DAIP Services**: WorkflowEngine, SynthesisEngine
- **Communication**: WebSocket双向通信
- **Storage**: Session状态管理
- **UI Framework**: Lona Web Application

---

## 🎨 UI/UX 规范

### 界面布局
```css
.secretariat-container {
  display: grid;
  grid-template-rows: 1fr auto;
  height: 100vh;
  background: #f8f9fa;
}

.chat-messages {
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-input-container {
  padding: 20px;
  background: white;
  border-top: 1px solid #e9ecef;
}
```

### 消息样式
```css
.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  margin: 4px 0;
}

.user-message {
  background: #007bff;
  color: white;
  margin-left: auto;
}

.assistant-message {
  background: white;
  color: #333;
  border: 1px solid #e9ecef;
  margin-right: auto;
}

.process-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #6c757d;
  font-size: 0.9em;
}
```

### 透明度按钮
```css
.show-process-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9em;
  margin-top: 8px;
}

.show-process-btn:hover {
  background: #218838;
}
```

---

## 🔧 技术实现

### 前端组件 (Lona)

#### ChatInterface 主组件
```python
class SecretariatChatInterface(lona.Component):
    def __init__(self):
        self.messages = []
        self.input_text = ""
        self.is_processing = False
        self.show_transparency = False
        
    def handle_input(self, input_event):
        """处理用户输入"""
        if not self.input_text.strip() or self.is_processing:
            return
            
        user_message = {
            "type": "user",
            "content": self.input_text,
            "timestamp": datetime.now()
        }
        
        self.messages.append(user_message)
        self.input_text = ""
        self.is_processing = True
        
        # 发送到后端
        self.send_to_backend(user_message)
        
    def send_to_backend(self, message):
        """发送消息到后端"""
        websocket_client.send({
            "type": "secretariat_task",
            "message": message["content"],
            "session_id": self.session_id
        })
        
    def receive_result(self, result):
        """接收后端结果"""
        self.is_processing = False
        
        assistant_message = {
            "type": "assistant",
            "content": result["content"],
            "timestamp": datetime.now(),
            "metadata": result.get("metadata", {})
        }
        
        self.messages.append(assistant_message)
        self.show_transparency = True  # 显示透明度按钮
```

#### TransparencyMonitor 透明度组件
```python
class SecretariatTransparencyMonitor(lona.Component):
    def __init__(self):
        self.process_data = None
        self.is_visible = False
        
    def show_process(self, process_data):
        """显示执行过程"""
        self.process_data = process_data
        self.is_visible = True
        
    def hide_process(self):
        """隐藏执行过程"""
        self.is_visible = False
        
    def render(self):
        """渲染透明度信息"""
        if not self.is_visible or not self.process_data:
            return html.DIV()
            
        return html.DIV(
            html.H3("任务执行过程"),
            html.DIV(
                *[self._render_workflow_step(step) 
                  for step in self.process_data.get("workflow_steps", [])]
            ),
            html.DIV(
                html.H4("AI Agent 活动"),
                *[self._render_agent_activity(activity) 
                  for activity in self.process_data.get("agent_activities", [])]
            )
        )
```

### 后端服务

#### PersonalAssistantService 集成
```python
class SecretariatService:
    def __init__(self, app_state):
        self.app_state = app_state
        self.workflow_engine = app_state.workflow_engine
        self.synthesis_engine = app_state.synthesis_engine
        self.process_monitor = ProcessMonitor()
        
    async def handle_secretariat_task(self, task_request):
        """处理Secretariat任务"""
        try:
            # 1. 解析意图
            intent = await self._interpret_intent(task_request["message"])
            
            # 2. 自动执行工作流
            workflow_result = await self._execute_workflow(intent)
            
            # 3. 生成报告
            final_result = await self._generate_report(workflow_result)
            
            # 4. 返回结果
            return {
                "content": final_result["content"],
                "metadata": {
                    "workflow_id": workflow_result["workflow_id"],
                    "execution_time": workflow_result["execution_time"],
                    "agent_count": workflow_result["agent_count"]
                }
            }
            
        except Exception as e:
            logger.error(f"Secretariat task failed: {e}")
            return {
                "content": f"任务执行失败: {str(e)}",
                "metadata": {"error": str(e)}
            }
            
    async def _interpret_intent(self, message):
        """解析用户意图"""
        # 调用DAIP的InterpretIntent原语
        return await self.app_state.interpret_intent_primitive(message)
        
    async def _execute_workflow(self, intent):
        """执行工作流"""
        # 调用DAIP的ExecuteWorkflow原语
        return await self.workflow_engine.execute_workflow(intent)
        
    async def _generate_report(self, workflow_result):
        """生成最终报告"""
        # 调用DAIP的GenerateReport原语
        return await self.synthesis_engine.generate_report(workflow_result)
```

#### ProcessMonitor 过程监控
```python
class SecretariatProcessMonitor:
    def __init__(self):
        self.active_processes = {}
        self.process_history = {}
        
    def start_monitoring(self, process_id, workflow_data):
        """开始监控过程"""
        self.active_processes[process_id] = {
            "start_time": datetime.now(),
            "workflow_data": workflow_data,
            "steps": [],
            "agent_activities": []
        }
        
    def record_step(self, process_id, step_data):
        """记录工作流步骤"""
        if process_id in self.active_processes:
            self.active_processes[process_id]["steps"].append({
                "timestamp": datetime.now(),
                "step_data": step_data
            })
            
    def record_agent_activity(self, process_id, activity_data):
        """记录Agent活动"""
        if process_id in self.active_processes:
            self.active_processes[process_id]["agent_activities"].append({
                "timestamp": datetime.now(),
                "activity_data": activity_data
            })
            
    def get_process_data(self, process_id):
        """获取过程数据"""
        if process_id in self.active_processes:
            return self.active_processes[process_id]
        return None
```

---

## 🔄 工作流程

### 1. 用户输入处理
```
用户输入 → ChatInterface → WebSocket → PersonalAssistantService
```

### 2. 自动化执行
```
PersonalAssistantService → InterpretIntent → FormTeam → ExecuteWorkflow → GenerateReport
```

### 3. 结果返回
```
GenerateReport → PersonalAssistantService → WebSocket → ChatInterface → 用户界面
```

### 4. 透明度展示
```
用户点击"显示过程" → ProcessMonitor → TransparencyMonitor → 用户界面
```

---

## 📡 WebSocket 消息协议

### 消息格式
```json
{
  "type": "secretariat_task",
  "message": "分析AI在医疗领域的应用趋势",
  "session_id": "session_123",
  "timestamp": "2025-08-06T10:30:00Z"
}
```

### 响应格式
```json
{
  "type": "secretariat_result",
  "content": "AI在医疗领域的应用趋势分析报告...",
  "metadata": {
    "workflow_id": "workflow_456",
    "execution_time": 45.2,
    "agent_count": 5
  },
  "timestamp": "2025-08-06T10:30:45Z"
}
```

### 透明度数据格式
```json
{
  "type": "process_data",
  "process_id": "process_789",
  "workflow_steps": [
    {
      "step": "intent_analysis",
      "description": "分析用户意图",
      "duration": 2.1,
      "status": "completed"
    }
  ],
  "agent_activities": [
    {
      "agent": "medical_expert",
      "activity": "分析医疗数据",
      "duration": 15.3,
      "contribution": "关键发现"
    }
  ]
}
```

---

## 🧪 测试要求

### 单元测试
- [ ] ChatInterface组件渲染测试
- [ ] WebSocket连接测试
- [ ] PersonalAssistantService集成测试
- [ ] ProcessMonitor数据记录测试

### 集成测试
- [ ] 端到端任务执行测试
- [ ] 透明度功能测试
- [ ] 错误处理测试
- [ ] 性能测试

### 验收标准
- [ ] 用户可以提交任务并获得结果
- [ ] 任务执行过程透明度可查看
- [ ] 响应时间 < 3秒
- [ ] 界面响应流畅，无卡顿

---

## 📊 性能指标

### 响应时间
- **界面响应**: <100ms
- **任务执行**: <30秒 (简单任务)
- **透明度加载**: <500ms

### 资源使用
- **内存占用**: <50MB per session
- **CPU使用**: <30% per task
- **网络带宽**: <1MB per task

---

## 🔗 相关文档

- [技术架构规范](./TECHNICAL_ARCHITECTURE.md)
- [API接口规范](./API_SPECIFICATION.md)
- [实施计划规范](./IMPLEMENTATION_PLAN.md)
- [测试验收标准](./TESTING_ACCEPTANCE.md)

---

**版本历史**
- v1.0 (2025-08-06): 初始版本 - Secretariat规范定义