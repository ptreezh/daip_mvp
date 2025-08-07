# Personal Intelligence Hub - 测试验收标准

**文档状态:** 最终版 - 可用于实施
**版本:** 1.0
**日期:** 2025-08-06

## 📋 文档范围

本文档定义了Personal Intelligence Hub双入口系统的测试策略和验收标准，确保系统质量和功能完整性。

---

## 🎯 测试策略

### 测试层次
1. **单元测试**: 测试单个组件和函数
2. **集成测试**: 测试组件间交互
3. **端到端测试**: 测试完整用户流程
4. **性能测试**: 测试系统性能和稳定性
5. **安全测试**: 测试系统安全性

### 测试原则
- **测试驱动开发**: 先写测试再实现功能
- **持续测试**: 每次代码提交都运行测试
- **自动化**: 尽可能自动化测试流程
- **覆盖率**: 确保高测试覆盖率

---

## 🧪 单元测试

### 前端组件测试

#### Secretariat组件测试
```python
# test_secretariat_components.py
import pytest
from src.frontend.components.secretariat import SecretariatChatInterface

class TestSecretariatChatInterface:
    def test_initialization(self):
        """测试组件初始化"""
        component = SecretariatChatInterface()
        assert component.messages == []
        assert component.input_text == ""
        assert component.is_processing == False
        
    def test_handle_user_input(self):
        """测试用户输入处理"""
        component = SecretariatChatInterface()
        component.input_text = "测试消息"
        
        # 模拟输入事件
        component.handle_input("submit")
        
        assert len(component.messages) == 1
        assert component.messages[0]["content"] == "测试消息"
        assert component.input_text == ""
        
    def test_process_result(self):
        """测试结果处理"""
        component = SecretariatChatInterface()
        result = {
            "content": "测试结果",
            "metadata": {"workflow_id": "test_123"}
        }
        
        component.receive_result(result)
        
        assert len(component.messages) == 1
        assert component.messages[0]["content"] == "测试结果"
```

#### Forum组件测试
```python
# test_forum_components.py
import pytest
from src.frontend.components.forum import ForumChatInterface

class TestForumChatInterface:
    def test_forum_initialization(self):
        """测试Forum组件初始化"""
        component = ForumChatInterface()
        assert component.debate_messages == []
        assert component.user_input == ""
        assert component.selected_intent == "comment"
        
    def test_user_intervention(self):
        """测试用户干预"""
        component = ForumChatInterface()
        component.user_input = "用户建议"
        component.selected_intent = "suggestion"
        
        component.handle_user_intervention()
        
        assert len(component.debate_messages) == 1
        assert component.debate_messages[0]["content"] == "用户建议"
        assert component.debate_messages[0]["intent"] == "suggestion"
```

### 后端服务测试

#### PersonalAssistantService测试
```python
# test_personal_assistant_service.py
import pytest
from src.services.personal_assistant import PersonalAssistantService

class TestPersonalAssistantService:
    def test_secretariat_request_handling(self):
        """测试Secretariat请求处理"""
        service = PersonalAssistantService(mock_app_state)
        request = {
            "type": "secretariat",
            "message": "分析AI医疗应用",
            "user_id": "test_user"
        }
        
        result = await service.handle_secretariat_request(request)
        
        assert result["type"] == "secretariat_result"
        assert "content" in result
        assert "metadata" in result
        
    def test_forum_request_handling(self):
        """测试Forum请求处理"""
        service = PersonalAssistantService(mock_app_state)
        request = {
            "type": "forum",
            "message": "AI伦理讨论",
            "user_id": "test_user"
        }
        
        result = await service.handle_forum_request(request)
        
        assert result["type"] == "forum_session_created"
        assert "session_id" in result
```

#### WebSocket管理测试
```python
# test_websocket_manager.py
import pytest
from src.services.websocket_manager import WebSocketManager

class TestWebSocketManager:
    def test_connection_management(self):
        """测试连接管理"""
        manager = WebSocketManager()
        session_id = "test_session"
        
        # 模拟连接建立
        mock_websocket = MockWebSocket()
        manager.handle_connection(mock_websocket, session_id)
        
        assert session_id in manager.connections
        
        # 模拟连接断开
        manager.handle_disconnect(session_id)
        
        assert session_id not in manager.connections
        
    def test_message_processing(self):
        """测试消息处理"""
        manager = WebSocketManager()
        session_id = "test_session"
        
        # 测试消息处理
        message = {"type": "test", "data": "test_data"}
        result = manager.process_message(session_id, message)
        
        assert result is not None
```

---

## 🔗 集成测试

### Secretariat集成测试
```python
# test_secretariat_integration.py
import pytest
import asyncio
from src.services.personal_assistant import PersonalAssistantService

class TestSecretariatIntegration:
    @pytest.mark.asyncio
    async def test_end_to_end_secretariat_workflow(self):
        """测试端到端Secretariat工作流"""
        # 1. 创建会话
        service = PersonalAssistantService(app_state)
        session_id = await service.session_manager.create_secretariat_session(
            "test_user", "分析AI医疗应用"
        )
        
        # 2. 发送任务
        task_request = {
            "session_id": session_id,
            "message": "分析AI在医疗领域的应用趋势",
            "type": "secretariat"
        }
        
        result = await service.handle_secretariat_request(task_request)
        
        # 3. 验证结果
        assert result["type"] == "secretariat_result"
        assert "AI医疗应用" in result["content"]
        assert result["metadata"]["workflow_id"] is not None
        
        # 4. 验证透明度数据
        transparency_data = await service.get_transparency_data(
            result["metadata"]["workflow_id"]
        )
        
        assert "workflow_steps" in transparency_data
        assert "agent_activities" in transparency_data
```

### Forum集成测试
```python
# test_forum_integration.py
import pytest
import asyncio
from src.services.forum_service import ForumService

class TestForumIntegration:
    @pytest.mark.asyncio
    async def test_forum_collaboration_workflow(self):
        """测试Forum协作工作流"""
        # 1. 创建Forum会话
        forum_service = ForumService(app_state)
        session_config = {
            "session_id": "forum_test_123",
            "topic": "AI在医疗领域的伦理考量",
            "participants": ["medical_expert", "ethics_expert"]
        }
        
        session = await forum_service.start_forum_session(session_config)
        
        # 2. 用户干预
        user_intervention = {
            "session_id": session["session_id"],
            "message": {
                "content": "我认为隐私保护很重要",
                "intent": "comment"
            }
        }
        
        result = await forum_service.handle_user_intervention(user_intervention)
        
        # 3. 验证结果
        assert result["status"] == "integrated"
        assert "optimized_input" in result
        
        # 4. 验证上下文更新
        context = await forum_service.get_session_context(session["session_id"])
        
        assert context["topic"] == "AI在医疗领域的伦理考量"
        assert context["status"] == "active"
        assert len(context["active_agents"]) > 0
```

### WebSocket集成测试
```python
# test_websocket_integration.py
import pytest
import websockets
import json

class TestWebSocketIntegration:
    @pytest.mark.asyncio
    async def test_secretariat_websocket_flow(self):
        """测试Secretariat WebSocket流程"""
        uri = "ws://localhost:8000/ws/secretariat/test_session"
        
        async with websockets.connect(uri) as websocket:
            # 1. 认证
            auth_message = {
                "type": "auth",
                "token": "test_token",
                "session_id": "test_session"
            }
            await websocket.send(json.dumps(auth_message))
            
            # 2. 发送任务
            task_message = {
                "type": "secretariat_task",
                "message": "测试任务",
                "session_id": "test_session"
            }
            await websocket.send(json.dumps(task_message))
            
            # 3. 接收结果
            response = await websocket.recv()
            result = json.loads(response)
            
            assert result["type"] == "secretariat_result"
            assert "content" in result
            
    @pytest.mark.asyncio
    async def test_forum_websocket_flow(self):
        """测试Forum WebSocket流程"""
        uri = "ws://localhost:8000/ws/forum/test_session"
        
        async with websockets.connect(uri) as websocket:
            # 1. 认证
            auth_message = {
                "type": "auth",
                "token": "test_token",
                "session_id": "test_session"
            }
            await websocket.send(json.dumps(auth_message))
            
            # 2. 用户干预
            intervention_message = {
                "type": "user_intervention",
                "message": {
                    "content": "用户意见",
                    "intent": "comment"
                },
                "session_id": "test_session"
            }
            await websocket.send(json.dumps(intervention_message))
            
            # 3. 接收Agent响应
            response = await websocket.recv()
            result = json.loads(response)
            
            assert result["type"] == "agent_message"
            assert "content" in result
```

---

## 🚀 端到端测试

### Secretariat端到端测试
```python
# test_e2e_secretariat.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestSecretariatE2E:
    def setup_method(self):
        """设置测试环境"""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/secretariat")
        
    def teardown_method(self):
        """清理测试环境"""
        self.driver.quit()
        
    def test_secretariat_complete_workflow(self):
        """测试Secretariat完整工作流"""
        # 1. 等待页面加载
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "secretariat-container"))
        )
        
        # 2. 输入消息
        input_field = self.driver.find_element(By.CLASS_NAME, "chat-input")
        input_field.send_keys("分析AI在医疗领域的应用趋势")
        
        # 3. 发送消息
        send_button = self.driver.find_element(By.CLASS_NAME, "send-button")
        send_button.click()
        
        # 4. 等待处理状态
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "processing-indicator"))
        )
        
        # 5. 等待结果
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "assistant-message"))
        )
        
        # 6. 验证结果
        messages = self.driver.find_elements(By.CLASS_NAME, "assistant-message")
        assert len(messages) > 0
        
        # 7. 测试透明度功能
        transparency_button = self.driver.find_element(By.CLASS_NAME, "show-process-btn")
        transparency_button.click()
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "transparency-monitor"))
        )
        
        # 8. 验证透明度信息
        transparency_info = self.driver.find_element(By.CLASS_NAME, "transparency-monitor")
        assert "工作流步骤" in transparency_info.text
```

### Forum端到端测试
```python
# test_e2e_forum.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestForumE2E:
    def setup_method(self):
        """设置测试环境"""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/forum")
        
    def teardown_method(self):
        """清理测试环境"""
        self.driver.quit()
        
    def test_forum_complete_workflow(self):
        """测试Forum完整工作流"""
        # 1. 等待页面加载
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "forum-container"))
        )
        
        # 2. 创建论坛会话
        topic_input = self.driver.find_element(By.CLASS_NAME, "topic-input")
        topic_input.send_keys("AI在医疗领域的伦理考量")
        
        create_button = self.driver.find_element(By.CLASS_NAME, "create-forum-btn")
        create_button.click()
        
        # 3. 等待论坛界面加载
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "debate-stream"))
        )
        
        # 4. 等待Agent消息
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "agent-message"))
        )
        
        # 5. 用户干预
        user_input = self.driver.find_element(By.CLASS_NAME, "user-input")
        user_input.send_keys("我认为隐私保护很重要")
        
        intent_select = self.driver.find_element(By.CLASS_NAME, "intent-select")
        intent_select.click()
        
        comment_option = self.driver.find_element(By.XPATH, "//option[@value='comment']")
        comment_option.click()
        
        send_button = self.driver.find_element(By.CLASS_NAME, "send-intervention-btn")
        send_button.click()
        
        # 6. 等待用户消息显示
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "user-message"))
        )
        
        # 7. 验证上下文面板更新
        context_panel = self.driver.find_element(By.CLASS_NAME, "context-panel")
        assert "共识度" in context_panel.text
        
        # 8. 测试暂停功能
        pause_button = self.driver.find_element(By.CLASS_NAME, "pause-btn")
        pause_button.click()
        
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "paused-indicator"))
        )
```

---

## ⚡ 性能测试

### 负载测试
```python
# test_performance.py
import pytest
import asyncio
import aiohttp
from locust import HttpUser, task, between

class SecretariatUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """用户开始测试"""
        # 认证
        response = self.client.post("/api/auth", json={
            "username": "test_user",
            "password": "test_password"
        })
        self.token = response.json()["token"]
        
    @task
    def secretariat_task(self):
        """Secretariat任务测试"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # 创建会话
        response = self.client.post("/api/sessions", json={
            "entrance_type": "secretariat",
            "user_id": "test_user"
        }, headers=headers)
        
        session_id = response.json()["session_id"]
        
        # 发送任务
        self.client.post(f"/api/sessions/{session_id}/tasks", json={
            "message": "性能测试任务",
            "type": "secretariat"
        }, headers=headers)

class ForumUser(HttpUser):
    wait_time = between(2, 5)
    
    def on_start(self):
        """用户开始测试"""
        # 认证
        response = self.client.post("/api/auth", json={
            "username": "test_user",
            "password": "test_password"
        })
        self.token = response.json()["token"]
        
    @task
    def forum_task(self):
        """Forum任务测试"""
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # 创建论坛会话
        response = self.client.post("/api/sessions", json={
            "entrance_type": "forum",
            "user_id": "test_user",
            "topic": "性能测试话题"
        }, headers=headers)
        
        session_id = response.json()["session_id"]
        
        # 用户干预
        self.client.post(f"/api/sessions/{session_id}/interventions", json={
            "message": "性能测试意见",
            "intent": "comment"
        }, headers=headers)
```

### 响应时间测试
```python
# test_response_time.py
import pytest
import time
import requests

class TestResponseTime:
    def test_secretariat_response_time(self):
        """测试Secretariat响应时间"""
        # 认证
        auth_response = requests.post("http://localhost:8000/api/auth", json={
            "username": "test_user",
            "password": "test_password"
        })
        token = auth_response.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 创建会话
        start_time = time.time()
        response = requests.post("http://localhost:8000/api/sessions", json={
            "entrance_type": "secretariat",
            "user_id": "test_user"
        }, headers=headers)
        session_creation_time = time.time() - start_time
        
        assert session_creation_time < 1.0  # 会话创建 < 1秒
        
        session_id = response.json()["session_id"]
        
        # 发送任务
        start_time = time.time()
        response = requests.post(f"http://localhost:8000/api/sessions/{session_id}/tasks", json={
            "message": "响应时间测试",
            "type": "secretariat"
        }, headers=headers)
        task_submission_time = time.time() - start_time
        
        assert task_submission_time < 0.5  # 任务提交 < 0.5秒
        
        # 等待结果
        start_time = time.time()
        while True:
            response = requests.get(f"http://localhost:8000/api/sessions/{session_id}/tasks", headers=headers)
            tasks = response.json()["tasks"]
            
            if tasks and tasks[-1]["status"] == "completed":
                break
                
            if time.time() - start_time > 60:  # 超时60秒
                pytest.fail("Task completion timeout")
                
            time.sleep(1)
            
        task_completion_time = time.time() - start_time
        assert task_completion_time < 30.0  # 任务完成 < 30秒
```

---

## 🔒 安全测试

### 认证测试
```python
# test_security.py
import pytest
import requests
import jwt

class TestSecurity:
    def test_authentication(self):
        """测试认证功能"""
        # 测试有效登录
        response = requests.post("http://localhost:8000/api/auth", json={
            "username": "test_user",
            "password": "test_password"
        })
        
        assert response.status_code == 200
        assert "token" in response.json()
        
        # 测试无效登录
        response = requests.post("http://localhost:8000/api/auth", json={
            "username": "invalid_user",
            "password": "invalid_password"
        })
        
        assert response.status_code == 401
        
    def test_authorization(self):
        """测试授权功能"""
        # 获取有效token
        auth_response = requests.post("http://localhost:8000/api/auth", json={
            "username": "test_user",
            "password": "test_password"
        })
        token = auth_response.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 测试有权限的访问
        response = requests.get("http://localhost:8000/api/users/test_user", headers=headers)
        assert response.status_code == 200
        
        # 测试无权限的访问
        response = requests.get("http://localhost:8000/api/users/other_user", headers=headers)
        assert response.status_code == 403
        
    def test_token_validation(self):
        """测试Token验证"""
        # 获取有效token
        auth_response = requests.post("http://localhost:8000/api/auth", json={
            "username": "test_user",
            "password": "test_password"
        })
        token = auth_response.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 测试有效token
        response = requests.get("http://localhost:8000/api/system/status", headers=headers)
        assert response.status_code == 200
        
        # 测试无效token
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get("http://localhost:8000/api/system/status", headers=headers)
        assert response.status_code == 401
        
    def test_input_validation(self):
        """测试输入验证"""
        # 获取有效token
        auth_response = requests.post("http://localhost:8000/api/auth", json={
            "username": "test_user",
            "password": "test_password"
        })
        token = auth_response.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # 测试SQL注入
        malicious_input = "'; DROP TABLE users; --"
        response = requests.post("http://localhost:8000/api/sessions", json={
            "entrance_type": "secretariat",
            "user_id": malicious_input
        }, headers=headers)
        
        assert response.status_code == 400
        
        # 测试XSS攻击
        xss_input = "<script>alert('xss')</script>"
        response = requests.post("http://localhost:8000/api/sessions", json={
            "entrance_type": "secretariat",
            "user_id": "test_user",
            "initial_context": {"topic": xss_input}
        }, headers=headers)
        
        assert response.status_code == 400
```

---

## 📊 验收标准

### 功能验收标准
- [ ] 所有用户场景都能正常工作
- [ ] 边界情况处理正确
- [ ] 错误处理机制完善
- [ ] 数据一致性保证
- [ ] 用户体验流畅

### 性能验收标准
- [ ] 响应时间 < 500ms
- [ ] 并发用户数 > 100
- [ ] 系统可用性 > 99.9%
- [ ] 内存使用合理
- [ ] CPU使用率 < 80%

### 质量验收标准
- [ ] 代码覆盖率 > 80%
- [ ] 所有测试通过
- [ ] 代码质量达标
- [ ] 文档完整准确
- [ ] 安全测试通过

### 部署验收标准
- [ ] 生产环境配置正确
- [ ] 部署脚本正常工作
- [ ] 监控系统正常运行
- [ ] 备份策略有效
- [ ] 回滚机制可用

---

## 📈 测试报告

### 测试覆盖率报告
```bash
# 生成测试覆盖率报告
pytest --cov=src --cov-report=html --cov-report=term-missing
```

### 性能测试报告
```bash
# 运行性能测试
locust -f test_performance.py --host=http://localhost:8000 --users=100 --spawn-rate=10 --run-time=5m
```

### 安全测试报告
```bash
# 运行安全扫描
bandit -r src/
safety check
```

---

**版本历史**
- v1.0 (2025-08-06): 初始版本 - 测试验收标准定义