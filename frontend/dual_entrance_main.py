#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personal Intelligence Hub - 双入口主界面

基于Lona Web框架的统一入口界面
支持Secretariat和Forum两种用户交互模式
"""

from lona import LonaApp, View
from lona.html import HTML, Div, H1, H2, Head, Title, Link, Button, P, Span
from lona.html import TextInput, Select, Option, Form
import asyncio
import logging
import uuid

# 配置日志
logger = logging.getLogger(__name__)

# 导入现有组件
from components.chat_interface import ChatInterface
from components.transparency_monitor import TransparencyMonitor
from components.wiki_panel import WikiPanel
from components.task_panel import TaskPanel

# 导入服务
from services.personal_assistant import PersonalAssistantService
from services.backend_connector import BackendConnector
from services.websocket_manager import websocket_manager, realtime_manager

# 创建Lona应用实例
app = LonaApp(__file__)


class EntranceChoiceView(View):
    """入口选择界面"""
    
    def handle_request(self, request):
        return HTML(
            Head(
                Title("Personal Intelligence Hub - 选择入口"),
                Link(
                    rel="stylesheet",
                    href="/static/css/main.css"
                ),
                Link(
                    rel="stylesheet",
                    href="/static/css/entrance.css"
                )
            ),
            Div(
                # 页面标题
                H1(
                    "🎭 Personal Intelligence Hub",
                    _class="page-title"
                ),
                
                P(
                    "基于制度原语的集体智慧涌现平台",
                    _class="page-subtitle"
                ),
                
                # 入口选择卡片
                Div(
                    # Secretariat入口
                    Div(
                        Div(
                            H2("📋 Secretariat", _class="entrance-title"),
                            P("智能任务处理入口", _class="entrance-subtitle"),
                            
                            Div(
                                "• 提交任务并获得专业分析",
                                _class="feature-item"
                            ),
                            Div(
                                "• 自动化多角色协作",
                                _class="feature-item"
                            ),
                            Div(
                                "• 透明化处理过程",
                                _class="feature-item"
                            ),
                            Div(
                                "• 高质量结果输出",
                                _class="feature-item"
                            ),
                            
                            Button(
                                "进入 Secretariat",
                                _class="btn btn-primary entrance-btn",
                                handle_click=lambda event: self._choose_entrance(event, "secretariat")
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
                            
                            Div(
                                "• 多角色实时对话",
                                _class="feature-item"
                            ),
                            Div(
                                "• 动态共识计算",
                                _class="feature-item"
                            ),
                            Div(
                                "• 用户直接参与",
                                _class="feature-item"
                            ),
                            Div(
                                "• 灵活交互模式",
                                _class="feature-item"
                            ),
                            
                            Button(
                                "进入 Forum",
                                _class="btn btn-secondary entrance-btn",
                                handle_click=lambda event: self._choose_entrance(event, "forum")
                            ),
                            
                            _class="entrance-card forum-card"
                        ),
                        _class="entrance-container"
                    ),
                    
                    _class="entrances-grid"
                ),
                
                # 用户信息表单
                Div(
                    H2("用户信息", _class="section-title"),
                    
                    Form(
                        Div(
                            Label("用户名:", _for="username"),
                            TextInput(
                                id="username",
                                placeholder="请输入您的用户名",
                                _class="form-input"
                            ),
                            _class="form-group"
                        ),
                        
                        Div(
                            Label("首选入口:", _for="preferred_entrance"),
                            Select(
                                Option("Secretariat", value="secretariat"),
                                Option("Forum", value="forum"),
                                id="preferred_entrance",
                                _class="form-select"
                            ),
                            _class="form-group"
                        ),
                        
                        Div(
                            Label("主题:", _for="theme"),
                            Select(
                                Option("浅色", value="light"),
                                Option("深色", value="dark"),
                                id="theme",
                                _class="form-select"
                            ),
                            _class="form-group"
                        ),
                        
                        _class="user-form"
                    ),
                    
                    _class="user-info-section"
                ),
                
                _class="container entrance-page"
            )
        )
    
    def _choose_entrance(self, event, entrance_type):
        """选择入口类型"""
        # 获取用户信息
        username = event.request.html.get_element_by_id("username").value
        preferred_entrance = event.request.html.get_element_by_id("preferred_entrance").value
        theme = event.request.html.get_element_by_id("theme").value
        
        # 保存用户偏好
        user_preferences = {
            "username": username or "匿名用户",
            "preferred_entrance": preferred_entrance,
            "theme": theme,
            "current_entrance": entrance_type
        }
        
        # 重定向到相应的入口界面
        if entrance_type == "secretariat":
            return self._redirect_to_secretariat(user_preferences)
        else:
            return self._redirect_to_forum(user_preferences)
    
    def _redirect_to_secretariat(self, user_preferences):
        """重定向到Secretariat入口"""
        # 这里可以创建SecretariatView并传递用户偏好
        return HTML(
            Head(
                Title("Personal Intelligence Hub - Secretariat"),
                Link(rel="stylesheet", href="/static/css/main.css")
            ),
            Div(
                H1("📋 Secretariat 入口"),
                P(f"欢迎, {user_preferences['username']}!"),
                P("正在加载Secretariat界面..."),
                _class="container"
            )
        )
    
    def _redirect_to_forum(self, user_preferences):
        """重定向到Forum入口"""
        # 这里可以创建ForumView并传递用户偏好
        return HTML(
            Head(
                Title("Personal Intelligence Hub - Forum"),
                Link(rel="stylesheet", href="/static/css/main.css")
            ),
            Div(
                H1("💬 Forum 入口"),
                P(f"欢迎, {user_preferences['username']}!"),
                P("正在加载Forum界面..."),
                _class="container"
            )
        )


class SecretariatView(View):
    """Secretariat入口界面"""
    
    def handle_request(self, request):
        # 生成会话ID
        session_id = f"secretariat_{uuid.uuid4().hex[:8]}"
        
        # 初始化后端连接器
        backend_connector = BackendConnector()
        
        # 初始化服务
        assistant_service = PersonalAssistantService(
            intent_analysis_service=backend_connector.intent_analysis_service,
            role_manager=backend_connector.role_manager,
            workflow_integrator=backend_connector.workflow_integrator,
            consensus_selector=backend_connector.consensus_selector
        )
        
        # 初始化组件
        chat_interface = ChatInterface(assistant_service, session_id)
        transparency_monitor = TransparencyMonitor()
        wiki_panel = WikiPanel(backend_connector.wiki_service)
        task_panel = TaskPanel(backend_connector.task_service)
        
        return HTML(
            Head(
                Title("Personal Intelligence Hub - Secretariat"),
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
                    href="/static/css/secretariat.css"
                )
            ),
            
            Div(
                # 页面标题
                H1(
                    "📋 Personal Intelligence Hub - Secretariat",
                    _class="page-title"
                ),
                
                # 主要布局容器
                Div(
                    # 左侧主要聊天区域
                    Div(
                        chat_interface,
                        _class="main-chat-area secretariat-chat"
                    ),
                    
                    # 右侧面板区域
                    Div(
                        # 透明度监控面板
                        Div(
                            transparency_monitor,
                            _class="panel transparency-panel"
                        ),
                        
                        # Wiki知识库面板
                        Div(
                            wiki_panel,
                            _class="panel wiki-panel"
                        ),
                        
                        # 任务管理面板
                        Div(
                            task_panel,
                            _class="panel task-panel"
                        ),
                        
                        _class="side-panels"
                    ),
                    
                    _class="hub-layout"
                ),
                
                _class="container secretariat-container"
            )
        )


class ForumView(View):
    """Forum入口界面"""
    
    def handle_request(self, request):
        # 生成会话ID
        session_id = f"forum_{uuid.uuid4().hex[:8]}"
        
        # 初始化后端连接器
        backend_connector = BackendConnector()
        
        # 初始化服务
        assistant_service = PersonalAssistantService(
            intent_analysis_service=backend_connector.intent_analysis_service,
            role_manager=backend_connector.role_manager,
            workflow_integrator=backend_connector.workflow_integrator,
            consensus_selector=backend_connector.consensus_selector
        )
        
        # 初始化组件
        chat_interface = ChatInterface(assistant_service, session_id)
        transparency_monitor = TransparencyMonitor()
        wiki_panel = WikiPanel(backend_connector.wiki_service)
        
        return HTML(
            Head(
                Title("Personal Intelligence Hub - Forum"),
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
                    href="/static/css/forum.css"
                )
            ),
            
            Div(
                # 页面标题
                H1(
                    "💬 Personal Intelligence Hub - Forum",
                    _class="page-title"
                ),
                
                # Forum特有控件
                Div(
                    # 讨论主题设置
                    Div(
                        H2("讨论主题", _class="section-title"),
                        TextInput(
                            placeholder="输入讨论主题...",
                            _class="topic-input"
                        ),
                        Button(
                            "开始讨论",
                            _class="btn btn-primary",
                            handle_click=self._start_discussion
                        ),
                        _class="topic-setup"
                    ),
                    
                    # 参与者选择
                    Div(
                        H2("参与者", _class="section-title"),
                        Div(
                            # 这里可以添加参与者选择逻辑
                            _class="participants-list"
                        ),
                        _class="participants-section"
                    ),
                    
                    # 共识监控
                    Div(
                        H2("共识状态", _class="section-title"),
                        Div(
                            # 这里可以添加共识状态显示
                            _class="consensus-monitor"
                        ),
                        _class="consensus-section"
                    ),
                    
                    _class="forum-controls"
                ),
                
                # 主要布局容器
                Div(
                    # 左侧主要聊天区域
                    Div(
                        chat_interface,
                        _class="main-chat-area forum-chat"
                    ),
                    
                    # 右侧面板区域
                    Div(
                        # 透明度监控面板
                        Div(
                            transparency_monitor,
                            _class="panel transparency-panel"
                        ),
                        
                        # Wiki知识库面板
                        Div(
                            wiki_panel,
                            _class="panel wiki-panel"
                        ),
                        
                        _class="side-panels"
                    ),
                    
                    _class="hub-layout"
                ),
                
                _class="container forum-container"
            )
        )
    
    def _start_discussion(self, event):
        """开始讨论"""
        # 这里可以实现开始讨论的逻辑
        pass


# 添加路由
app.route('/', EntranceChoiceView)
app.route('/secretariat', SecretariatView)
app.route('/forum', ForumView)


async def startup_tasks():
    """启动时执行的异步任务"""
    print("🔌 初始化WebSocket连接...")
    await websocket_manager.connect()
    print("✅ WebSocket连接就绪")


if __name__ == '__main__':
    print("🚀 启动 Personal Intelligence Hub 双入口系统...")
    print("📍 访问地址: http://localhost:8080")
    print("🎭 基于制度原语的集体智慧涌现平台")
    print("🔌 WebSocket实时通信: 已启用")
    
    # 启动异步任务
    asyncio.create_task(startup_tasks())
    
    app.run(
        host='localhost',
        port=8080,
        debug=True,
        shutdown_timeout=10
    )