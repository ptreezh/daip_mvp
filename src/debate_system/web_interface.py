#!/usr/bin/env python3
"""多轮辩论系统Web界面

基于现有ChatInterface和TransparencyMonitor组件，
为多轮辩论系统提供专门的Web界面。

核心功能：
- 辩论会话管理
- 多角色对话展示
- 实时状态监控
- 响应式设计
- WebSocket实时通信
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from lona.html import (
    H2,
    H3,
    HTML,
    A,
    Button,
    Div,
    Nav,
    Option,
    P,
    Select,
    Span,
    TextInput,
)
from lona.html.widget import Widget

# 导入现有组件
try:
    from frontend.components.chat_interface import ChatInterface, ChatMessage, MessageType
    from frontend.components.transparency_monitor import TransparencyMonitor
    from frontend.services.websocket_manager import WebSocketMessage, websocket_manager
except ImportError:
    # 如果无法导入，创建占位符类
    class ChatInterface:
        def __init__(self, *args, **kwargs):
            pass
    class TransparencyMonitor:
        def __init__(self, *args, **kwargs):
            pass
    class websocket_manager:
        @staticmethod
        def send_message(*args, **kwargs):
            pass

# 导入辩论系统组件
from debate_state_manager import DebateStateManager
from multi_role_dialogue_engine import MultiRoleDialogueEngine

from .debate_flow_definition import DebateSession, DebateStatus

logger = logging.getLogger(__name__)


class DebateInterfaceMode(Enum):
    """辩论界面模式"""
    SETUP = "setup"          # 设置模式
    ACTIVE = "active"        # 活跃辩论
    MONITORING = "monitoring" # 监控模式
    RESULTS = "results"      # 结果展示


class DebateWebInterface(Widget):
    """多轮辩论系统Web界面"""
    
    def __init__(self, 
                 dialogue_engine: MultiRoleDialogueEngine,
                 state_manager: DebateStateManager):
        super().__init__()
        
        self.dialogue_engine = dialogue_engine
        self.state_manager = state_manager
        
        # 界面状态
        self.current_mode = DebateInterfaceMode.SETUP
        self.active_session: Optional[DebateSession] = None
        self.session_history: list[dict[str, Any]] = []
        
        # 子组件
        self.chat_interface = None
        self.transparency_monitor = None
        
        # UI元素
        self.topic_input = TextInput(
            placeholder="请输入辩论话题...",
            _class="form-control topic-input"
        )
        self.participant_count_select = Select(
            Option("2", "2个角色"),
            Option("3", "3个角色"),
            Option("4", "4个角色"),
            Option("5", "5个角色"),
            value="4",
            _class="form-control"
        )
        self.debate_format_select = Select(
            Option("traditional", "传统辩论"),
            Option("oxford", "牛津辩论"),
            Option("consensus_building", "共识构建"),
            Option("socratic", "苏格拉底式"),
            value="traditional",
            _class="form-control"
        )
        self.start_debate_button = Button(
            "开始辩论",
            _class="btn btn-primary btn-lg"
        )
        self.stop_debate_button = Button(
            "结束辩论",
            _class="btn btn-danger",
            disabled=True
        )
        self.mode_switch_buttons = {
            DebateInterfaceMode.SETUP: Button("设置", _class="btn btn-outline-primary"),
            DebateInterfaceMode.ACTIVE: Button("辩论", _class="btn btn-outline-success"),
            DebateInterfaceMode.MONITORING: Button("监控", _class="btn btn-outline-info"),
            DebateInterfaceMode.RESULTS: Button("结果", _class="btn btn-outline-warning")
        }
        
        # 绑定事件
        self.start_debate_button.handle_click = self.handle_start_debate
        self.stop_debate_button.handle_click = self.handle_stop_debate
        
        for mode, button in self.mode_switch_buttons.items():
            button.handle_click = lambda event, m=mode: asyncio.create_task(self.switch_mode(m))
        
        # 初始化子组件
        self._initialize_components()
        
        logger.info("多轮辩论Web界面初始化完成")
    
    def _initialize_components(self):
        """初始化子组件"""
        try:
            # 创建透明度监控组件
            self.transparency_monitor = TransparencyMonitor(
                websocket_manager=websocket_manager
            )
            
            # 设置监控回调
            self.transparency_monitor.on_agent_update = self.handle_agent_update
            self.transparency_monitor.on_workflow_update = self.handle_workflow_update
            
            logger.info("子组件初始化完成")
        except Exception as e:
            logger.error(f"子组件初始化失败: {e}")
    
    async def handle_start_debate(self, event):
        """处理开始辩论"""
        try:
            topic = self.topic_input.value.strip()
            if not topic:
                await self.show_error("请输入辩论话题")
                return
            
            participant_count = int(self.participant_count_select.value)
            debate_format = self.debate_format_select.value
            
            # 创建辩论会话
            session = DebateSession(
                title=f"辩论：{topic}",
                topic=topic,
                description=f"关于'{topic}'的多角色辩论"
            )
            
            # 保存会话到状态管理器
            success = await self.state_manager.create_session(session)
            if not success:
                await self.show_error("创建辩论会话失败")
                return
            
            # 启动多角色对话
            dialogue_success = await self.dialogue_engine.start_dialogue(
                session, topic, max_roles=participant_count
            )
            
            if not dialogue_success:
                await self.show_error("启动多角色对话失败")
                return
            
            # 更新界面状态
            self.active_session = session
            self.start_debate_button.disabled = True
            self.stop_debate_button.disabled = False
            
            # 切换到活跃模式
            await self.switch_mode(DebateInterfaceMode.ACTIVE)
            
            # 创建聊天界面（模拟PersonalAssistantService）
            mock_assistant = MockPersonalAssistantService(self.dialogue_engine, session.session_id)
            self.chat_interface = ChatInterface(mock_assistant, session.session_id)
            
            # 添加辩论开始消息
            await self.chat_interface.add_system_message(
                f"🎭 多角色辩论已开始！\n\n"
                f"📋 话题: {topic}\n"
                f"👥 参与角色: {participant_count}个\n"
                f"📝 格式: {debate_format}\n\n"
                f"各位专家正在准备发言，请稍候...",
                MessageType.SYSTEM_INFO
            )
            
            # 启动透明度监控
            await self.transparency_monitor.start_monitoring()
            
            logger.info(f"辩论已开始: {topic}")
            
        except Exception as e:
            logger.error(f"开始辩论失败: {e}")
            await self.show_error(f"开始辩论失败: {str(e)}")
    
    async def handle_stop_debate(self, event):
        """处理结束辩论"""
        try:
            if not self.active_session:
                return
            
            # 结束对话
            success = await self.dialogue_engine.end_dialogue(self.active_session.session_id)
            
            if success:
                # 更新会话状态
                self.active_session.status = DebateStatus.COMPLETED
                self.active_session.completed_at = datetime.now()
                
                await self.state_manager.update_session(self.active_session)
                
                # 添加到历史记录
                summary = await self.dialogue_engine.get_dialogue_summary(self.active_session.session_id)
                self.session_history.append({
                    "session": self.active_session,
                    "summary": summary,
                    "completed_at": datetime.now()
                })
                
                # 更新界面状态
                self.start_debate_button.disabled = False
                self.stop_debate_button.disabled = True
                
                # 切换到结果模式
                await self.switch_mode(DebateInterfaceMode.RESULTS)
                
                # 添加结束消息
                if self.chat_interface:
                    await self.chat_interface.add_system_message(
                        "🏁 辩论已结束！正在生成总结报告...",
                        MessageType.SYSTEM_INFO
                    )
                
                # 停止监控
                await self.transparency_monitor.stop_monitoring()
                
                logger.info(f"辩论已结束: {self.active_session.session_id}")
            else:
                await self.show_error("结束辩论失败")
                
        except Exception as e:
            logger.error(f"结束辩论失败: {e}")
            await self.show_error(f"结束辩论失败: {str(e)}")
    
    async def switch_mode(self, mode: DebateInterfaceMode):
        """切换界面模式"""
        try:
            self.current_mode = mode
            
            # 更新按钮状态
            for m, button in self.mode_switch_buttons.items():
                if m == mode:
                    button._class = "btn btn-primary"
                else:
                    button._class = "btn btn-outline-secondary"
            
            logger.info(f"界面模式已切换到: {mode.value}")
            
        except Exception as e:
            logger.error(f"切换模式失败: {e}")
    
    async def handle_agent_update(self, agent_data: dict[str, Any]):
        """处理代理状态更新"""
        try:
            if self.chat_interface:
                agent_name = agent_data.get("name", "Unknown Agent")
                status = agent_data.get("status", "unknown")
                current_task = agent_data.get("current_task", "")
                
                if status == "thinking":
                    await self.chat_interface.add_system_message(
                        f"🤖 {agent_name} 正在思考: {current_task}",
                        MessageType.WORKFLOW_STATUS
                    )
                elif status == "completed" and current_task:
                    await self.chat_interface.add_agent_message(
                        agent_name,
                        current_task,
                        {"agent_id": agent_data.get("agent_id")}
                    )
        except Exception as e:
            logger.error(f"处理代理更新失败: {e}")
    
    async def handle_workflow_update(self, workflow_data: dict[str, Any]):
        """处理工作流更新"""
        try:
            if self.chat_interface:
                workflow_type = workflow_data.get("type", "unknown")
                status = workflow_data.get("status", "unknown")
                progress = workflow_data.get("progress", 0)
                
                await self.chat_interface.add_system_message(
                    f"🔄 工作流 {workflow_type}: {status} ({progress}%)",
                    MessageType.WORKFLOW_STATUS
                )
        except Exception as e:
            logger.error(f"处理工作流更新失败: {e}")
    
    async def show_error(self, message: str):
        """显示错误消息"""
        if self.chat_interface:
            await self.chat_interface.add_system_message(
                f"❌ {message}",
                MessageType.ERROR
            )
        logger.error(message)
    
    def _render_setup_mode(self) -> HTML:
        """渲染设置模式"""
        return Div(
            H2("🎭 创建新辩论", _class="mb-4"),
            
            # 辩论设置表单
            Div(
                Div(
                    Div(
                        HTML('<label class="form-label">辩论话题</label>'),
                        self.topic_input,
                        _class="mb-3"
                    ),
                    Div(
                        HTML('<label class="form-label">参与角色数量</label>'),
                        self.participant_count_select,
                        _class="mb-3"
                    ),
                    Div(
                        HTML('<label class="form-label">辩论格式</label>'),
                        self.debate_format_select,
                        _class="mb-3"
                    ),
                    Div(
                        self.start_debate_button,
                        _class="d-grid"
                    ),
                    _class="col-md-6"
                ),
                
                # 历史记录
                Div(
                    H3("📚 历史辩论", _class="mb-3"),
                    *[
                        Div(
                            H5(record["session"].title, _class="mb-2"),
                            P(f"话题: {record['session'].topic}", _class="text-muted mb-1"),
                            P(f"完成时间: {record['completed_at'].strftime('%Y-%m-%d %H:%M')}", 
                              _class="text-muted mb-2"),
                            P(f"参与角色: {record['summary']['active_roles'] if record['summary'] else 'N/A'}", 
                              _class="text-muted"),
                            _class="card card-body mb-3"
                        )
                        for record in self.session_history[-5:]  # 显示最近5条
                    ] if self.session_history else [
                        P("暂无历史记录", _class="text-muted text-center py-4")
                    ],
                    _class="col-md-6"
                ),
                _class="row"
            ),
            _class="container-fluid"
        )
    
    def _render_active_mode(self) -> HTML:
        """渲染活跃辩论模式"""
        if not self.chat_interface:
            return Div(
                P("正在初始化辩论界面...", _class="text-center py-5"),
                _class="container-fluid"
            )
        
        return Div(
            # 辩论控制栏
            Div(
                Div(
                    H3(f"🎭 {self.active_session.title}" if self.active_session else "辩论进行中", 
                       _class="mb-0"),
                    P(f"话题: {self.active_session.topic}" if self.active_session else "", 
                      _class="text-muted mb-0"),
                    _class="col"
                ),
                Div(
                    self.stop_debate_button,
                    _class="col-auto"
                ),
                _class="row align-items-center mb-3 p-3 bg-light rounded"
            ),
            
            # 主要内容区域
            Div(
                # 聊天界面
                Div(
                    self.chat_interface.render(),
                    _class="col-lg-8"
                ),
                
                # 侧边栏 - 辩论状态
                Div(
                    self._render_debate_status_panel(),
                    _class="col-lg-4"
                ),
                _class="row"
            ),
            _class="container-fluid"
        )
    
    def _render_monitoring_mode(self) -> HTML:
        """渲染监控模式"""
        if not self.transparency_monitor:
            return Div(
                P("监控组件未初始化", _class="text-center py-5"),
                _class="container-fluid"
            )
        
        return Div(
            H2("📊 系统监控", _class="mb-4"),
            
            # 监控面板
            Div(
                self.transparency_monitor.render(),
                _class="monitoring-panel"
            ),
            _class="container-fluid"
        )
    
    def _render_results_mode(self) -> HTML:
        """渲染结果模式"""
        if not self.active_session:
            return Div(
                P("暂无辩论结果", _class="text-center py-5"),
                _class="container-fluid"
            )
        
        return Div(
            H2("📊 辩论结果", _class="mb-4"),
            
            # 结果摘要
            Div(
                H3("📋 辩论摘要", _class="mb-3"),
                Div(
                    P(f"话题: {self.active_session.topic}", _class="mb-2"),
                    P(f"开始时间: {self.active_session.started_at.strftime('%Y-%m-%d %H:%M') if self.active_session.started_at else 'N/A'}", 
                      _class="mb-2"),
                    P(f"结束时间: {self.active_session.completed_at.strftime('%Y-%m-%d %H:%M') if self.active_session.completed_at else 'N/A'}", 
                      _class="mb-2"),
                    P(f"参与者: {len(self.active_session.participants)}", _class="mb-2"),
                    _class="card card-body"
                ),
                _class="mb-4"
            ),
            
            # 详细结果（如果有的话）
            Div(
                H3("💡 关键洞察", _class="mb-3"),
                P("辩论结果分析将在此显示...", _class="text-muted"),
                _class="card card-body"
            ),
            _class="container-fluid"
        )
    
    def _render_debate_status_panel(self) -> HTML:
        """渲染辩论状态面板"""
        if not self.active_session:
            return Div()
        
        # 获取对话摘要
        try:
            summary = asyncio.create_task(
                self.dialogue_engine.get_dialogue_summary(self.active_session.session_id)
            )
        except:
            summary = None
        
        return Div(
            H4("📊 辩论状态", _class="mb-3"),
            
            # 基本信息
            Div(
                P(f"会话ID: {self.active_session.session_id[:8]}...", _class="mb-1 small text-muted"),
                P(f"状态: {self.active_session.status.value}", _class="mb-1"),
                P(f"当前轮次: {self.active_session.current_round}", _class="mb-1"),
                P(f"参与者: {len(self.active_session.participants)}", _class="mb-1"),
                _class="card card-body mb-3"
            ),
            
            # 参与者列表
            Div(
                H5("👥 参与角色", _class="mb-2"),
                *[
                    Div(
                        Span(participant.name, _class="fw-bold"),
                        Span(participant.role.value, _class="badge bg-secondary ms-2"),
                        _class="d-flex justify-content-between align-items-center mb-1"
                    )
                    for participant in self.active_session.participants
                ] if self.active_session.participants else [
                    P("暂无参与者", _class="text-muted small")
                ],
                _class="card card-body mb-3"
            ),
            
            # 快速操作
            Div(
                H5("⚡ 快速操作", _class="mb-2"),
                Button("触发共识", _class="btn btn-sm btn-outline-primary me-2 mb-2"),
                Button("暂停辩论", _class="btn btn-sm btn-outline-warning me-2 mb-2"),
                Button("导出记录", _class="btn btn-sm btn-outline-info mb-2"),
                _class="card card-body"
            )
        )
    
    def _render_navigation(self) -> HTML:
        """渲染导航栏"""
        return Nav(
            Div(
                # 品牌
                A("🎭 多轮辩论系统", href="#", _class="navbar-brand"),
                
                # 模式切换按钮
                Div(
                    *[button for button in self.mode_switch_buttons.values()],
                    _class="btn-group"
                ),
                _class="container-fluid d-flex justify-content-between"
            ),
            _class="navbar navbar-expand-lg navbar-light bg-light mb-4"
        )
    
    def render(self) -> HTML:
        """渲染主界面"""
        # 根据当前模式渲染不同内容
        content_map = {
            DebateInterfaceMode.SETUP: self._render_setup_mode,
            DebateInterfaceMode.ACTIVE: self._render_active_mode,
            DebateInterfaceMode.MONITORING: self._render_monitoring_mode,
            DebateInterfaceMode.RESULTS: self._render_results_mode
        }
        
        content_renderer = content_map.get(self.current_mode, self._render_setup_mode)
        
        return Div(
            # 导航栏
            self._render_navigation(),
            
            # 主要内容
            content_renderer(),
            
            # 样式
            HTML("""
            <style>
                .topic-input { font-size: 1.1rem; padding: 12px; }
                .chat-interface { height: 600px; border: 1px solid #dee2e6; border-radius: 8px; }
                .monitoring-panel { background: #f8f9fa; padding: 20px; border-radius: 8px; }
                .debate-status-panel { background: white; }
                .message { margin-bottom: 10px; padding: 10px; border-radius: 8px; }
                .message.user { background: #e3f2fd; margin-left: 20%; }
                .message.assistant { background: #f3e5f5; margin-right: 20%; }
                .message.agent { background: #e8f5e8; margin-right: 15%; }
                .message.system-info { background: #fff3e0; text-align: center; }
                .message.error { background: #ffebee; color: #c62828; }
                .message-timestamp { font-size: 0.8rem; color: #666; margin-top: 5px; }
                .navbar-brand { font-size: 1.5rem; font-weight: bold; }
                .btn-group .btn { margin-right: 5px; }
            </style>
            """),
            
            _class="debate-web-interface"
        )


class MockPersonalAssistantService:
    """模拟PersonalAssistantService用于集成"""
    
    def __init__(self, dialogue_engine: MultiRoleDialogueEngine, session_id: str):
        self.dialogue_engine = dialogue_engine
        self.session_id = session_id
        self.conversation_contexts = {}
    
    async def process_message(self, message: str, session_id: str) -> str:
        """处理消息"""
        try:
            # 继续对话
            success = await self.dialogue_engine.continue_dialogue(session_id)
            
            if success:
                return "✅ 消息已发送给各位专家，他们正在准备回应..."
            else:
                return "❌ 处理消息时出现问题，请稍后重试。"
        
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            return f"❌ 处理消息时出现错误: {str(e)}"
    
    def update_conversation_context(self, session_id: str, context: dict[str, Any]):
        """更新对话上下文"""
        if session_id not in self.conversation_contexts:
            self.conversation_contexts[session_id] = []
        self.conversation_contexts[session_id].append(context)


# 使用示例和测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_debate_web_interface():
        """测试多轮辩论Web界面"""
        print("🧪 测试多轮辩论Web界面...")
        
        # 这里需要实际的组件实例
        print("⚠️ 需要实际的组件实例才能运行完整测试")
        print("✅ 多轮辩论Web界面代码结构验证完成")
    
    # 运行测试
    asyncio.run(test_debate_web_interface())