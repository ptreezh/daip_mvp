#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time    : 2025-08-06 14:30:00
@Author  : DAIP-LIVE Team
@File    : test_forum_api.py
@Description:
    Forum API端点测试 - 验证Forum模式的所有HTTP接口功能
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.main import app
from src.api.routers.forum import (
    ForumSessionRequest,
    UserInterventionRequest,
    SessionControlRequest
)
from src.core_services.forum_service import forum_service, ForumSession
from src.core.exceptions import ForumServiceError


class TestForumAPI:
    """Forum API测试类"""
    
    def setup_method(self):
        """设置测试环境"""
        self.client = TestClient(app)
        
        # 测试数据
        self.test_topic = "人工智能的未来发展"
        self.test_user_id = "test_user"
        self.test_session_id = "test_session_123"
        
    def test_create_forum_session_success(self):
        """测试创建Forum会话成功"""
        # 模拟Forum服务响应
        mock_session = ForumSession(
            session_id=self.test_session_id,
            topic=self.test_topic,
            start_time=datetime.now(),
            active_agents=["technical_expert", "business_analyst"]
        )
        
        with patch.object(forum_service, 'start_forum_session', new_callable=AsyncMock) as mock_start:
            mock_start.return_value = mock_session
            
            # 发送请求
            request_data = {
                "topic": self.test_topic,
                "user_id": self.test_user_id
            }
            
            response = self.client.post("/api/forum/session", json=request_data)
            
            # 验证响应
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == self.test_session_id
            assert data["topic"] == self.test_topic
            assert data["status"] == "active"
            assert len(data["active_agents"]) == 2
            
            # 验证服务调用
            mock_start.assert_called_once_with(
                topic=self.test_topic,
                user_id=self.test_user_id
            )
    
    def test_create_forum_session_service_error(self):
        """测试创建Forum会话服务错误"""
        with patch.object(forum_service, 'start_forum_session', new_callable=AsyncMock) as mock_start:
            mock_start.side_effect = ForumServiceError("Service unavailable")
            
            request_data = {
                "topic": self.test_topic,
                "user_id": self.test_user_id
            }
            
            response = self.client.post("/api/forum/session", json=request_data)
            
            assert response.status_code == 400
            assert "Service unavailable" in response.json()["detail"]
    
    def test_get_session_context_success(self):
        """测试获取会话上下文成功"""
        mock_context = {
            "session_id": self.test_session_id,
            "topic": self.test_topic,
            "status": "active",
            "consensus_level": 0.75,
            "active_agents": ["technical_expert", "business_analyst"],
            "key_arguments": [],
            "message_count": 10,
            "user_intervention_count": 2,
            "start_time": datetime.now().isoformat(),
            "duration": 300.0
        }
        
        with patch.object(forum_service, 'get_session_context', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_context
            
            response = self.client.get(f"/api/forum/session/{self.test_session_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == self.test_session_id
            assert data["consensus_level"] == 0.75
            assert data["message_count"] == 10
    
    def test_get_session_context_not_found(self):
        """测试获取不存在的会话上下文"""
        with patch.object(forum_service, 'get_session_context', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            
            response = self.client.get(f"/api/forum/session/nonexistent_session")
            
            assert response.status_code == 404
            assert "Session not found" in response.json()["detail"]
    
    def test_handle_user_intervention_success(self):
        """测试处理用户干预成功"""
        mock_result = {
            "status": "integrated",
            "optimized_input": "优化后的用户输入",
            "session_id": self.test_session_id
        }
        
        with patch.object(forum_service, 'handle_user_intervention', new_callable=AsyncMock) as mock_handle:
            mock_handle.return_value = mock_result
            
            request_data = {
                "session_id": self.test_session_id,
                "message": {
                    "content": "原始用户输入",
                    "intent": "comment"
                }
            }
            
            response = self.client.post("/api/forum/intervention", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "integrated"
            assert data["optimized_input"] == "优化后的用户输入"
            assert data["session_id"] == self.test_session_id
    
    def test_handle_user_intervention_service_error(self):
        """测试处理用户干预服务错误"""
        with patch.object(forum_service, 'handle_user_intervention', new_callable=AsyncMock) as mock_handle:
            mock_handle.side_effect = ForumServiceError("Session not found")
            
            request_data = {
                "session_id": "nonexistent_session",
                "message": {
                    "content": "测试输入",
                    "intent": "comment"
                }
            }
            
            response = self.client.post("/api/forum/intervention", json=request_data)
            
            assert response.status_code == 400
            assert "Session not found" in response.json()["detail"]
    
    def test_pause_session_success(self):
        """测试暂停会话成功"""
        with patch.object(forum_service, 'pause_session', new_callable=AsyncMock) as mock_pause:
            mock_pause.return_value = True
            
            request_data = {
                "session_id": self.test_session_id,
                "action": "pause"
            }
            
            response = self.client.post("/api/forum/control", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["action"] == "pause"
            assert data["session_id"] == self.test_session_id
    
    def test_resume_session_success(self):
        """测试恢复会话成功"""
        with patch.object(forum_service, 'resume_session', new_callable=AsyncMock) as mock_resume:
            mock_resume.return_value = True
            
            request_data = {
                "session_id": self.test_session_id,
                "action": "resume"
            }
            
            response = self.client.post("/api/forum/control", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["action"] == "resume"
    
    def test_end_session_success(self):
        """测试结束会话成功"""
        mock_result = {
            "session_id": self.test_session_id,
            "topic": self.test_topic,
            "duration": 600.0,
            "total_messages": 25,
            "user_interventions": 5,
            "final_consensus": {"consensus_level": 0.85}
        }
        
        with patch.object(forum_service, 'end_session', new_callable=AsyncMock) as mock_end:
            mock_end.return_value = mock_result
            
            request_data = {
                "session_id": self.test_session_id,
                "action": "end"
            }
            
            response = self.client.post("/api/forum/control", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["action"] == "end"
    
    def test_control_session_invalid_action(self):
        """测试无效的会话控制动作"""
        request_data = {
            "session_id": self.test_session_id,
            "action": "invalid_action"
        }
        
        response = self.client.post("/api/forum/control", json=request_data)
        
        assert response.status_code == 400
        assert "Invalid action" in response.json()["detail"]
    
    def test_control_session_not_found(self):
        """测试控制不存在的会话"""
        with patch.object(forum_service, 'pause_session', new_callable=AsyncMock) as mock_pause:
            mock_pause.return_value = False
            
            request_data = {
                "session_id": "nonexistent_session",
                "action": "pause"
            }
            
            response = self.client.post("/api/forum/control", json=request_data)
            
            assert response.status_code == 404
            assert "Session not found" in response.json()["detail"]
    
    def test_get_active_sessions(self):
        """测试获取活跃会话列表"""
        mock_sessions = [
            {
                "session_id": self.test_session_id,
                "topic": self.test_topic,
                "status": "active",
                "start_time": datetime.now().isoformat(),
                "active_agents": ["technical_expert"],
                "message_count": 5
            }
        ]
        
        with patch.object(forum_service, 'get_active_sessions', return_value=mock_sessions):
            response = self.client.get("/api/forum/sessions")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["sessions"]) == 1
            assert data["count"] == 1
            assert data["sessions"][0]["session_id"] == self.test_session_id
    
    def test_get_forum_statistics(self):
        """测试获取Forum统计信息"""
        mock_stats = {
            "total_sessions": 5,
            "active_sessions": 3,
            "total_messages": 150,
            "total_interventions": 25,
            "average_consensus": 0.72
        }
        
        with patch.object(forum_service, 'get_session_statistics', return_value=mock_stats):
            response = self.client.get("/api/forum/statistics")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_sessions"] == 5
            assert data["active_sessions"] == 3
            assert data["average_consensus"] == 0.72
    
    def test_delete_session_success(self):
        """测试删除会话成功"""
        mock_result = {
            "session_id": self.test_session_id,
            "topic": self.test_topic,
            "duration": 300.0,
            "total_messages": 15,
            "user_interventions": 3,
            "final_consensus": {"consensus_level": 0.8}
        }
        
        with patch.object(forum_service, 'end_session', new_callable=AsyncMock) as mock_end:
            mock_end.return_value = mock_result
            
            response = self.client.delete(f"/api/forum/session/{self.test_session_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "deleted"
            assert data["session_id"] == self.test_session_id
    
    def test_delete_session_not_found(self):
        """测试删除不存在的会话"""
        with patch.object(forum_service, 'end_session', new_callable=AsyncMock) as mock_end:
            mock_end.return_value = None
            
            response = self.client.delete("/api/forum/session/nonexistent_session")
            
            assert response.status_code == 404
            assert "Session not found" in response.json()["detail"]
    
    def test_forum_health_check(self):
        """测试Forum健康检查"""
        mock_sessions = [
            {
                "session_id": self.test_session_id,
                "topic": self.test_topic,
                "status": "active",
                "start_time": datetime.now().isoformat(),
                "active_agents": ["technical_expert"],
                "message_count": 5
            }
        ]
        
        mock_stats = {
            "total_sessions": 1,
            "active_sessions": 1,
            "total_messages": 5,
            "total_interventions": 0,
            "average_consensus": 0.75
        }
        
        with patch.object(forum_service, 'get_active_sessions', return_value=mock_sessions), \
             patch.object(forum_service, 'get_session_statistics', return_value=mock_stats):
            
            response = self.client.get("/api/forum/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "forum"
            assert data["active_sessions"] == 1
    
    def test_forum_health_check_unhealthy(self):
        """测试Forum健康检查异常"""
        with patch.object(forum_service, 'get_active_sessions', side_effect=Exception("Service error")):
            response = self.client.get("/api/forum/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["service"] == "forum"
            assert "Service error" in data["error"]
    
    def test_get_session_messages(self):
        """测试获取会话消息历史"""
        mock_context = {
            "session_id": self.test_session_id,
            "topic": self.test_topic,
            "status": "active",
            "consensus_level": 0.75,
            "active_agents": ["technical_expert"],
            "key_arguments": [],
            "message_count": 10,
            "user_intervention_count": 2,
            "start_time": datetime.now().isoformat(),
            "duration": 300.0
        }
        
        with patch.object(forum_service, 'get_session_context', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_context
            
            response = self.client.get(f"/api/forum/session/{self.test_session_id}/messages")
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == self.test_session_id
            assert data["message_count"] == 10
            assert data["messages"] == []
    
    def test_optimize_user_input_success(self):
        """测试优化用户输入成功"""
        mock_context = {
            "session_id": self.test_session_id,
            "topic": self.test_topic,
            "status": "active",
            "consensus_level": 0.75,
            "active_agents": ["technical_expert"],
            "key_arguments": [],
            "message_count": 10,
            "user_intervention_count": 2,
            "start_time": datetime.now().isoformat(),
            "duration": 300.0
        }
        
        with patch.object(forum_service, 'get_session_context', new_callable=AsyncMock) as mock_get, \
             patch.object(forum_service.user_intervention_manager, 'optimize_input', new_callable=AsyncMock) as mock_optimize:
            
            mock_get.return_value = mock_context
            mock_optimize.return_value = "优化后的用户输入"
            
            request_data = {
                "input": "原始用户输入",
                "intent": "comment"
            }
            
            response = self.client.post(f"/api/forum/session/{self.test_session_id}/optimize", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["original_input"] == "原始用户输入"
            assert data["optimized_input"] == "优化后的用户输入"
            assert data["intent"] == "comment"
    
    def test_optimize_user_input_missing_input(self):
        """测试优化用户输入缺少输入"""
        request_data = {
            "intent": "comment"
        }
        
        response = self.client.post(f"/api/forum/session/{self.test_session_id}/optimize", json=request_data)
        
        assert response.status_code == 400
        assert "Input is required" in response.json()["detail"]
    
    def test_optimize_user_input_session_not_found(self):
        """测试优化不存在的会话用户输入"""
        with patch.object(forum_service, 'get_session_context', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            
            request_data = {
                "input": "测试输入",
                "intent": "comment"
            }
            
            response = self.client.post(f"/api/forum/session/nonexistent_session/optimize", json=request_data)
            
            assert response.status_code == 404
            assert "Session not found" in response.json()["detail"]


# 集成测试类
class TestForumAPIIntegration:
    """Forum API集成测试"""
    
    def setup_method(self):
        """设置集成测试环境"""
        self.client = TestClient(app)
    
    def test_forum_endpoints_available(self):
        """测试Forum API端点可用性"""
        # 测试健康检查
        response = self.client.get("/api/forum/health")
        assert response.status_code == 200
        
        # 测试统计信息
        response = self.client.get("/api/forum/statistics")
        assert response.status_code == 200
        
        # 测试会话列表
        response = self.client.get("/api/forum/sessions")
        assert response.status_code == 200
    
    def test_create_and_retrieve_session(self):
        """测试创建和检索会话的完整流程"""
        # 这个测试需要实际的Forum服务支持
        # 在实际环境中运行时可能需要mock部分服务
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])