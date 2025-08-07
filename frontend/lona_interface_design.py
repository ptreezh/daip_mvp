#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personal Intelligence Hub - Lona Web界面设计文档

基于DDD架构设计的双入口统一界面框架
支持Secretariat和Forum两种用户交互模式

设计目标：
1. 统一的双入口界面架构
2. 实时通信的WebSocket集成
3. 响应式设计和现代化UI
4. 模块化组件系统
5. 透明度监控和用户干预功能
"""

from lona import LonaApp, View
from lona.html import HTML, Div, H1, H2, Head, Title, Link, Button, P, Span
from lona.html import TextInput, Select, Option, Form, Label, Ul, Li, Nav, Section
from lona.html import Article, Aside, Header, Footer, Main, Table, Tr, Td, Th, Thead, Tbody
from lona.html import Img, I, Strong, Em, Br, Hr, Blockquote, Pre, Code
from lona.html.widget import Widget
from typing import Dict, List, Optional, Any, Callable
import asyncio
import logging
import uuid
from datetime import datetime
from enum import Enum

# 配置日志
logger = logging.getLogger(__name__)

# ============================================================================
# 1. 界面架构设计
# ============================================================================

class EntranceType(Enum):
    """入口类型枚举"""
    SECRETARIAT = "secretariat"
    FORUM = "forum"

class UIState(Enum):
    """界面状态枚举"""
    IDLE = "idle"
    PROCESSING = "processing"
    THINKING = "thinking"
    DEBATING = "debating"
    CONSENSUS = "consensus"

class ComponentRegistry:
    """组件注册表"""
    
    def __init__(self):
        self.components: Dict[str, type] = {}
        self.instances: Dict[str, Widget] = {}
    
    def register(self, name: str, component_class: type):
        """注册组件类"""
        self.components[name] = component_class
        logger.info(f"注册组件: {name}")
    
    def create_instance(self, name: str, *args, **kwargs) -> Widget:
        """创建组件实例"""
        if name not in self.components:
            raise ValueError(f"未找到组件: {name}")
        
        instance = self.components[name](*args, **kwargs)
        self.instances[name] = instance
        return instance
    
    def get_instance(self, name: str) -> Optional[Widget]:
        """获取组件实例"""
        return self.instances.get(name)

# 全局组件注册表
component_registry = ComponentRegistry()

# ============================================================================
# 2. 核心组件设计
# ============================================================================

class BaseWidget(Widget):
    """基础组件类"""
    
    def __init__(self, component_id: Optional[str] = None):
        super().__init__()
        self.component_id = component_id or f"comp_{uuid.uuid4().hex[:8]}"
        self.state = UIState.IDLE
        self.callbacks: Dict[str, List[Callable]] = {}
        
        # 基础样式类
        self.base_classes = ["base-widget"]
        
    def add_callback(self, event_name: str, callback: Callable):
        """添加事件回调"""
        if event_name not in self.callbacks:
            self.callbacks[event_name] = []
        self.callbacks[event_name].append(callback)
    
    async def trigger_callback(self, event_name: str, *args, **kwargs):
        """触发事件回调"""
        if event_name in self.callbacks:
            for callback in self.callbacks[event_name]:
                try:
                    await callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"回调执行失败 {event_name}: {e}")
    
    def set_state(self, new_state: UIState):
        """设置组件状态"""
        self.state = new_state
        self.trigger_callback("state_changed", new_state)
    
    def get_classes(self) -> List[str]:
        """获取CSS类名"""
        return self.base_classes + [f"state-{self.state.value}"]

class EntranceSelector(BaseWidget):
    """统一入口选择器组件"""
    
    def __init__(self):
        super().__init__("entrance_selector")
        self.selected_entrance = None
        self.user_preferences = {}
        
        # 注册组件
        component_registry.register("entrance_selector", EntranceSelector)
    
    def handle_entrance_selection(self, entrance_type: EntranceType):
        """处理入口选择"""
        self.selected_entrance = entrance_type
        self.set_state(UIState.PROCESSING)
        
        # 触发选择事件
        asyncio.create_task(self.trigger_callback("entrance_selected", entrance_type))
    
    def render(self) -> HTML:
        """渲染入口选择器"""
        return Div(
            Div(
                H1("🎭 Personal Intelligence Hub", _class="main-title"),
                P("基于制度原语的集体智慧涌现平台", _class="subtitle"),
                
                # 入口选择卡片
                Div(
                    # Secretariat入口
                    Div(
                        Div(
                            H2("📋 Secretariat", _class="entrance-title"),
                            P("智能任务处理入口", _class="entrance-subtitle"),
                            
                            Ul(
                                Li("✓ 提交任务并获得专业分析"),
                                Li("✓ 自动化多角色协作"),
                                Li("✓ 透明化处理过程"),
                                Li("✓ 高质量结果输出"),
                                _class="features-list"
                            ),
                            
                            Button(
                                "进入 Secretariat",
                                _class="btn btn-primary entrance-btn",
                                handle_click=lambda e: self.handle_entrance_selection(EntranceType.SECRETARIAT)
                            ),
                            
                            _class="entrance-card secretariat-card"
                        ),
                        _class="entrance-container"
                    ),
                    
                    # Forum入口
                    Div(
                        Div(
                            H2("💬 Forum", _class="entrance-title"),
                            P("实时协作讨论入口", _class="entrance-subtitle"),
                            
                            Ul(
                                Li("✓ 多角色实时对话"),
                                Li("✓ 动态共识计算"),
                                Li("✓ 用户直接参与"),
                                Li("✓ 灵活交互模式"),
                                _class="features-list"
                            ),
                            
                            Button(
                                "进入 Forum",
                                _class="btn btn-secondary entrance-btn",
                                handle_click=lambda e: self.handle_entrance_selection(EntranceType.FORUM)
                            ),
                            
                            _class="entrance-card forum-card"
                        ),
                        _class="entrance-container"
                    ),
                    
                    _class="entrances-grid"
                ),
                
                # 用户配置表单
                Div(
                    H2("用户配置", _class="config-title"),
                    Form(
                        Div(
                            Label("用户名:", _for="username", _class="form-label"),
                            TextInput(
                                id="username",
                                placeholder="请输入您的用户名",
                                _class="form-input"
                            ),
                            _class="form-group"
                        ),
                        
                        Div(
                            Label("主题偏好:", _for="theme", _class="form-label"),
                            Select(
                                Option("浅色主题", value="light"),
                                Option("深色主题", value="dark"),
                                Option("自动", value="auto"),
                                id="theme",
                                _class="form-select"
                            ),
                            _class="form-group"
                        ),
                        
                        Div(
                            Label("默认入口:", _for="default_entrance", _class="form-label"),
                            Select(
                                Option("记住我的选择", value="remember"),
                                Option("总是显示选择", value="always_show"),
                                id="default_entrance",
                                _class="form-select"
                            ),
                            _class="form-group"
                        ),
                        
                        _class="config-form"
                    ),
                    
                    _class="user-config"
                ),
                
                _class="entrance-selector-container"
            )
        )

class SecretariatChatInterface(BaseWidget):
    """Secretariat模式聊天界面"""
    
    def __init__(self, session_id: str):
        super().__init__("secretariat_chat")
        self.session_id = session_id
        self.messages = []
        self.current_task = None
        self.task_history = []
        
        # 注册组件
        component_registry.register("secretariat_chat", SecretariatChatInterface)
    
    async def send_message(self, content: str):
        """发送消息"""
        self.set_state(UIState.PROCESSING)
        
        # 添加用户消息
        user_message = {
            "id": f"msg_{uuid.uuid4().hex[:8]}",
            "sender": "user",
            "content": content,
            "timestamp": datetime.now(),
            "type": "text"
        }
        self.messages.append(user_message)
        
        # 模拟处理中
        processing_message = {
            "id": f"msg_{uuid.uuid4().hex[:8]}",
            "sender": "system",
            "content": "🤔 正在分析您的请求...",
            "timestamp": datetime.now(),
            "type": "system"
        }
        self.messages.append(processing_message)
        
        # 触发消息发送事件
        await self.trigger_callback("message_sent", user_message)
        
        # 模拟异步处理
        await asyncio.sleep(1)
        
        # 移除处理中消息
        self.messages = [msg for msg in self.messages if msg["id"] != processing_message["id"]]
        
        # 添加系统回复
        response_message = {
            "id": f"msg_{uuid.uuid4().hex[:8]}",
            "sender": "assistant",
            "content": f"已收到您的任务：'{content}'。正在为您组织专家团队进行分析...",
            "timestamp": datetime.now(),
            "type": "text"
        }
        self.messages.append(response_message)
        
        self.set_state(UIState.IDLE)
        await self.trigger_callback("message_received", response_message)
    
    def render_message(self, message: Dict[str, Any]) -> HTML:
        """渲染单条消息"""
        message_classes = ["message"]
        
        if message["sender"] == "user":
            message_classes.append("user-message")
        elif message["sender"] == "assistant":
            message_classes.append("assistant-message")
        elif message["sender"] == "system":
            message_classes.append("system-message")
        
        return Div(
            Div(
                Strong(f"{message['sender']}: ", _class="message-sender"),
                Span(message["content"], _class="message-content"),
                Span(
                    message["timestamp"].strftime("%H:%M:%S"),
                    _class="message-timestamp"
                ),
                _class="message-body"
            ),
            _class=" ".join(message_classes)
        )
    
    def render(self) -> HTML:
        """渲染Secretariat聊天界面"""
        return Div(
            # 聊天头部
            Header(
                H2("📋 Secretariat - 智能任务处理", _class="chat-header"),
                P(f"会话ID: {self.session_id}", _class="session-info"),
                
                # 快捷操作按钮
                Div(
                    Button(
                        "📊 查看任务状态",
                        _class="btn btn-sm btn-outline",
                        handle_click=lambda e: self.trigger_callback("show_task_status")
                    ),
                    Button(
                        "📚 知识库",
                        _class="btn btn-sm btn-outline",
                        handle_click=lambda e: self.trigger_callback("show_knowledge_base")
                    ),
                    Button(
                        "⚙️ 设置",
                        _class="btn btn-sm btn-outline",
                        handle_click=lambda e: self.trigger_callback("show_settings")
                    ),
                    _class="quick-actions"
                ),
                
                _class="chat-header-container"
            ),
            
            # 消息历史区域
            Main(
                *[self.render_message(msg) for msg in self.messages],
                _class="message-history",
                id="secretariat-message-history"
            ),
            
            # 输入区域
            Footer(
                Div(
                    TextInput(
                        id="secretariat-message-input",
                        placeholder="请输入您的任务或问题...",
                        _class="message-input"
                    ),
                    Button(
                        "发送",
                        _class="btn btn-primary send-button",
                        handle_click=lambda e: asyncio.create_task(
                            self.send_message(
                                e.request.html.get_element_by_id("secretariat-message-input").value
                            )
                        )
                    ),
                    _class="input-container"
                ),
                
                # 工具栏
                Div(
                    Button("📎", _class="btn-icon", title="附件"),
                    Button("🎯", _class="btn-icon", title="快速任务"),
                    Button("📝", _class="btn-icon", title="模板"),
                    Button("🔍", _class="btn-icon", title="搜索"),
                    _class="toolbar"
                ),
                
                _class="chat-footer"
            ),
            
            _class="secretariat-chat-interface"
        )

class ForumChatInterface(BaseWidget):
    """Forum模式聊天界面 - 多智能体辩论"""
    
    def __init__(self, session_id: str):
        super().__init__("forum_chat")
        self.session_id = session_id
        self.messages = []
        self.active_agents = []
        self.debate_topic = ""
        self.consensus_score = 0.0
        self.debate_state = "idle"  # idle, active, paused, consensus
        
        # 注册组件
        component_registry.register("forum_chat", ForumChatInterface)
    
    async def start_debate(self, topic: str, participants: List[str]):
        """开始辩论"""
        self.debate_topic = topic
        self.active_agents = participants
        self.debate_state = "active"
        self.set_state(UIState.DEBATING)
        
        # 添加辩论开始消息
        start_message = {
            "id": f"msg_{uuid.uuid4().hex[:8]}",
            "sender": "system",
            "content": f"🎬 辩论开始！\\n主题: {topic}\\n参与者: {', '.join(participants)}",
            "timestamp": datetime.now(),
            "type": "debate_start"
        }
        self.messages.append(start_message)
        
        # 触发辩论开始事件
        await self.trigger_callback("debate_started", {
            "topic": topic,
            "participants": participants
        })
        
        # 模拟代理发言
        await self._simulate_agent_speeches()
    
    async def _simulate_agent_speeches(self):
        """模拟代理发言"""
        for i, agent in enumerate(self.active_agents):
            await asyncio.sleep(2)  # 模拟思考时间
            
            agent_message = {
                "id": f"msg_{uuid.uuid4().hex[:8]}",
                "sender": agent,
                "content": f"作为{agent}，我认为{self.debate_topic}这个问题需要从多个角度来考虑...",
                "timestamp": datetime.now(),
                "type": "agent_speech",
                "agent_id": f"agent_{i}"
            }
            self.messages.append(agent_message)
            
            await self.trigger_callback("agent_spoke", agent_message)
        
        # 辩论结束，开始共识计算
        await self._calculate_consensus()
    
    async def _calculate_consensus(self):
        """计算共识"""
        self.debate_state = "consensus"
        self.set_state(UIState.CONSENSUS)
        
        consensus_message = {
            "id": f"msg_{uuid.uuid4().hex[:8]}",
            "sender": "system",
            "content": "🎯 正在计算共识...",
            "timestamp": datetime.now(),
            "type": "consensus_calculating"
        }
        self.messages.append(consensus_message)
        
        await asyncio.sleep(2)
        
        # 模拟共识结果
        self.consensus_score = 0.75
        consensus_result = {
            "id": f"msg_{uuid.uuid4().hex[:8]}",
            "sender": "system",
            "content": f"🎉 共识计算完成！\\n共识度: {self.consensus_score:.2f}\\n\\n主要结论：\\n1. 多数专家认为需要综合考虑\\n2. 建议进一步深入研究\\n3. 可以形成初步的行动方案",
            "timestamp": datetime.now(),
            "type": "consensus_result",
            "score": self.consensus_score
        }
        self.messages.append(consensus_result)
        
        self.debate_state = "idle"
        self.set_state(UIState.IDLE)
        
        await self.trigger_callback("consensus_reached", consensus_result)
    
    def render_agent_status(self, agent: str) -> HTML:
        """渲染代理状态"""
        status_classes = ["agent-status"]
        if self.debate_state == "active":
            status_classes.append("active")
        
        return Div(
            Span(agent, _class="agent-name"),
            Span(
                "●" if self.debate_state == "active" else "○",
                _class="agent-indicator"
            ),
            _class=" ".join(status_classes)
        )
    
    def render_consensus_meter(self) -> HTML:
        """渲染共识度指示器"""
        return Div(
            Div(
                Span("共识度", _class="meter-label"),
                Span(f"{self.consensus_score:.2f}", _class="meter-value"),
                _class="meter-header"
            ),
            Div(
                Div(
                    _class="meter-fill",
                    style=f"width: {self.consensus_score * 100}%"
                ),
                _class="meter-bar"
            ),
            _class="consensus-meter"
        )
    
    def render(self) -> HTML:
        """渲染Forum聊天界面"""
        return Div(
            # 辩论控制面板
            Header(
                H2("💬 Forum - 多智能体辩论", _class="forum-header"),
                P(f"会话ID: {self.session_id}", _class="session-info"),
                
                # 辩论设置
                Div(
                    Div(
                        Label("辩论主题:", _for="debate-topic"),
                        TextInput(
                            id="debate-topic",
                            placeholder="输入辩论主题...",
                            value=self.debate_topic,
                            _class="form-input"
                        ),
                        _class="form-group"
                    ),
                    
                    Div(
                        Label("参与者:", _for="participants"),
                        Select(
                            *[Option(agent, value=agent) for agent in self.active_agents],
                            id="participants",
                            multiple=True,
                            _class="form-select"
                        ),
                        _class="form-group"
                    ),
                    
                    Button(
                        "🎬 开始辩论",
                        _class="btn btn-primary",
                        disabled=self.debate_state != "idle",
                        handle_click=lambda e: asyncio.create_task(
                            self.start_debate(
                                e.request.html.get_element_by_id("debate-topic").value,
                                [self.active_agents[0], self.active_agents[1]]  # 简化示例
                            )
                        )
                    ),
                    
                    _class="debate-controls"
                ),
                
                _class="forum-header-container"
            ),
            
            # 主要内容区域
            Div(
                # 左侧：消息区域
                Main(
                    *[self.render_message(msg) for msg in self.messages],
                    _class="forum-message-history",
                    id="forum-message-history"
                ),
                
                # 右侧：状态面板
                Aside(
                    # 活跃代理
                    Div(
                        H3("活跃代理", _class="panel-title"),
                        *[self.render_agent_status(agent) for agent in self.active_agents],
                        _class="active-agents-panel"
                    ),
                    
                    # 共识度
                    Div(
                        H3("共识状态", _class="panel-title"),
                        self.render_consensus_meter(),
                        _class="consensus-panel"
                    ),
                    
                    # 辩论统计
                    Div(
                        H3("辩论统计", _class="panel-title"),
                        Div(
                            P(f"总消息数: {len(self.messages)}"),
                            P(f"代理发言: {len([m for m in self.messages if m['type'] == 'agent_speech'])}"),
                            P(f"辩论时长: 5分钟"),
                            _class="debate-stats"
                        ),
                        _class="stats-panel"
                    ),
                    
                    _class="forum-sidebar"
                ),
                
                _class="forum-content"
            ),
            
            # 输入区域
            Footer(
                Div(
                    TextInput(
                        id="forum-message-input",
                        placeholder="参与辩论...",
                        _class="message-input",
                        disabled=self.debate_state != "active"
                    ),
                    Button(
                        "发言",
                        _class="btn btn-primary send-button",
                        disabled=self.debate_state != "active"
                    ),
                    _class="input-container"
                ),
                
                # 快捷操作
                Div(
                    Button("⏸️", _class="btn-icon", title="暂停", disabled=self.debate_state != "active"),
                    Button("🎯", _class="btn-icon", title="立即共识"),
                    Button("📊", _class="btn-icon", title="统计"),
                    Button("🔧", _class="btn-icon", title="设置"),
                    _class="forum-toolbar"
                ),
                
                _class="forum-footer"
            ),
            
            _class="forum-chat-interface"
        )

class StatusMonitor(BaseWidget):
    """统一状态监控组件"""
    
    def __init__(self):
        super().__init__("status_monitor")
        self.system_status = {
            "connected": True,
            "active_sessions": 1,
            "llm_calls": 0,
            "token_usage": 0,
            "memory_usage": "45MB",
            "uptime": "2h 15m"
        }
        
        # 注册组件
        component_registry.register("status_monitor", StatusMonitor)
    
    def update_status(self, new_status: Dict[str, Any]):
        """更新状态"""
        self.system_status.update(new_status)
        # Lona会自动重新渲染
    
    def render_status_card(self, title: str, value: str, icon: str) -> HTML:
        """渲染状态卡片"""
        return Div(
            Div(I(icon, _class="status-icon"), _class="status-icon-container"),
            Div(
                Div(title, _class="status-label"),
                Div(value, _class="status-value"),
                _class="status-text"
            ),
            _class="status-card"
        )
    
    def render(self) -> HTML:
        """渲染状态监控面板"""
        return Div(
            H3("🔍 系统状态监控", _class="monitor-header"),
            
            # 状态卡片网格
            Div(
                self.render_status_card("连接状态", "✅ 已连接", "🔌"),
                self.render_status_card("活跃会话", str(self.system_status["active_sessions"]), "👥"),
                self.render_status_card("LLM调用", str(self.system_status["llm_calls"]), "🤖"),
                self.render_status_card("Token使用", str(self.system_status["token_usage"]), "💰"),
                self.render_status_card("内存使用", self.system_status["memory_usage"], "💾"),
                self.render_status_card("运行时间", self.system_status["uptime"], "⏱️"),
                _class="status-grid"
            ),
            
            # 实时活动日志
            Div(
                H4("实时活动", _class="activity-header"),
                Div(
                    Div(
                        Span("10:30:25", _class="activity-time"),
                        Span("新用户连接", _class="activity-desc"),
                        _class="activity-item"
                    ),
                    Div(
                        Span("10:30:15", _class="activity-time"),
                        Span("LLM调用完成", _class="activity-desc"),
                        _class="activity-item"
                    ),
                    Div(
                        Span("10:30:05", _class="activity-time"),
                        Span("任务开始执行", _class="activity-desc"),
                        _class="activity-item"
                    ),
                    _class="activity-log"
                ),
                _class="activity-panel"
            ),
            
            _class="status-monitor"
        )

# ============================================================================
# 3. 主界面控制器
# ============================================================================

class DualEntranceController(BaseWidget):
    """双入口统一控制器"""
    
    def __init__(self):
        super().__init__("main_controller")
        self.current_entrance = None
        self.session_id = f"session_{uuid.uuid4().hex[:8]}"
        self.user_preferences = {}
        
        # 初始化子组件
        self.entrance_selector = EntranceSelector()
        self.secretariat_chat = SecretariatChatInterface(self.session_id)
        self.forum_chat = ForumChatInterface(self.session_id)
        self.status_monitor = StatusMonitor()
        
        # 设置事件回调
        self._setup_event_handlers()
        
        # 注册组件
        component_registry.register("main_controller", DualEntranceController)
    
    def _setup_event_handlers(self):
        """设置事件处理器"""
        # 入口选择事件
        self.entrance_selector.add_callback("entrance_selected", self._on_entrance_selected)
        
        # 聊天界面事件
        self.secretariat_chat.add_callback("message_sent", self._on_secretariat_message)
        self.forum_chat.add_callback("debate_started", self._on_debate_started)
    
    async def _on_entrance_selected(self, entrance_type: EntranceType):
        """处理入口选择"""
        self.current_entrance = entrance_type
        logger.info(f"用户选择了入口: {entrance_type.value}")
        
        # 更新状态
        await self.trigger_callback("entrance_changed", entrance_type)
    
    async def _on_secretariat_message(self, message: Dict[str, Any]):
        """处理Secretariat消息"""
        logger.info(f"Secretariat消息: {message['content']}")
        
        # 更新状态监控
        current_calls = self.status_monitor.system_status.get("llm_calls", 0)
        self.status_monitor.update_status({
            "llm_calls": current_calls + 1,
            "token_usage": self.status_monitor.system_status.get("token_usage", 0) + 150
        })
    
    async def _on_debate_started(self, debate_info: Dict[str, Any]):
        """处理辩论开始"""
        logger.info(f"辩论开始: {debate_info['topic']}")
        
        # 更新状态监控
        self.status_monitor.update_status({
            "active_sessions": self.status_monitor.system_status.get("active_sessions", 0) + 1
        })
    
    def render(self) -> HTML:
        """渲染主界面"""
        if self.current_entrance is None:
            # 显示入口选择界面
            return self.entrance_selector.render()
        
        elif self.current_entrance == EntranceType.SECRETARIAT:
            # 显示Secretariat界面
            return Div(
                # 顶部导航
                Header(
                    Nav(
                        Div(
                            H1("🎭 Personal Intelligence Hub", _class="nav-logo"),
                            _class="nav-brand"
                        ),
                        Div(
                            Button(
                                "🏠 首页",
                                _class="btn btn-sm",
                                handle_click=lambda e: setattr(self, 'current_entrance', None)
                            ),
                            Button(
                                "📋 Secretariat",
                                _class="btn btn-sm btn-primary"
                            ),
                            Button(
                                "💬 Forum",
                                _class="btn btn-sm",
                                handle_click=lambda e: setattr(self, 'current_entrance', EntranceType.FORUM)
                            ),
                            _class="nav-menu"
                        ),
                        _class="nav-container"
                    ),
                    _class="main-header"
                ),
                
                # 主要内容区域
                Div(
                    # 左侧：聊天界面
                    Main(
                        self.secretariat_chat.render(),
                        _class="main-content"
                    ),
                    
                    # 右侧：状态监控
                    Aside(
                        self.status_monitor.render(),
                        _class="sidebar"
                    ),
                    
                    _class="content-layout"
                ),
                
                _class="secretariat-layout"
            )
        
        elif self.current_entrance == EntranceType.FORUM:
            # 显示Forum界面
            return Div(
                # 顶部导航
                Header(
                    Nav(
                        Div(
                            H1("🎭 Personal Intelligence Hub", _class="nav-logo"),
                            _class="nav-brand"
                        ),
                        Div(
                            Button(
                                "🏠 首页",
                                _class="btn btn-sm",
                                handle_click=lambda e: setattr(self, 'current_entrance', None)
                            ),
                            Button(
                                "📋 Secretariat",
                                _class="btn btn-sm",
                                handle_click=lambda e: setattr(self, 'current_entrance', EntranceType.SECRETARIAT)
                            ),
                            Button(
                                "💬 Forum",
                                _class="btn btn-sm btn-primary"
                            ),
                            _class="nav-menu"
                        ),
                        _class="nav-container"
                    ),
                    _class="main-header"
                ),
                
                # 主要内容区域
                Div(
                    # 左侧：聊天界面
                    Main(
                        self.forum_chat.render(),
                        _class="main-content"
                    ),
                    
                    # 右侧：状态监控
                    Aside(
                        self.status_monitor.render(),
                        _class="sidebar"
                    ),
                    
                    _class="content-layout"
                ),
                
                _class="forum-layout"
            )

# ============================================================================
# 4. Lona应用主视图
# ============================================================================

class MainView(View):
    """Lona应用主视图"""
    
    def handle_request(self, request):
        """处理HTTP请求"""
        # 创建主控制器
        controller = DualEntranceController()
        
        return HTML(
            Head(
                Title("Personal Intelligence Hub - 双入口系统"),
                Link(
                    rel="stylesheet",
                    href="/static/css/main.css"
                ),
                Link(
                    rel="stylesheet",
                    href="/static/css/components.css"
                ),
                Link(
                    rel="stylesheet",
                    href="/static/css/dual_entrance.css"
                ),
                # 添加响应式meta标签
                Meta(
                    name="viewport",
                    content="width=device-width, initial-scale=1.0"
                ),
                # 添加图标
                Link(
                    rel="icon",
                    href="/static/favicon.ico",
                    type="image/x-icon"
                )
            ),
            
            Body(
                controller.render(),
                _class="main-body"
            )
        )

# ============================================================================
# 5. Lona应用实例
# ============================================================================

def create_lona_app() -> LonaApp:
    """创建Lona应用实例"""
    app = LonaApp(__file__)
    
    # 设置路由
    app.route('/', MainView)
    app.route('/secretariat', MainView)
    app.route('/forum', MainView)
    
    # 设置静态文件目录
    app.static_files.add('/static/', 'frontend/static/')
    
    # 设置应用配置
    app.settings.MAX_WORKERS = 4
    app.settings.SHUTDOWN_TIMEOUT = 10
    
    return app

# ============================================================================
# 6. 启动函数
# ============================================================================

async def startup_tasks():
    """启动时执行的异步任务"""
    logger.info("🚀 启动 Personal Intelligence Hub 双入口系统...")
    logger.info("📍 系统架构: 基于DDD的Lona Web界面")
    logger.info("🔌 WebSocket实时通信: 已启用")
    logger.info("🎭 双入口模式: Secretariat + Forum")
    
    # 初始化WebSocket连接
    # websocket_manager = component_registry.get_instance("websocket_manager")
    # if websocket_manager:
    #     await websocket_manager.connect()
    
    logger.info("✅ 系统启动完成")

def main():
    """主函数"""
    # 创建Lona应用
    app = create_lona_app()
    
    # 启动异步任务
    asyncio.create_task(startup_tasks())
    
    # 运行应用
    app.run(
        host='localhost',
        port=8080,
        debug=True,
        shutdown_timeout=10
    )

if __name__ == '__main__':
    main()