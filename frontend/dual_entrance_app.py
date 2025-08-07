#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双入口系统启动器

集成所有组件并提供统一的启动接口
支持Secretariat和Forum两种入口模式
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from lona import LonaApp, View
from lona.html import HTML, Div, H1, Head, Title, Link, Button, P, Span
from lona.html import TextInput, Select, Option, Form

# 导入服务和组件
from services.dual_entrance_websocket_manager import dual_entrance_websocket_manager, EntranceType
from services.entrance_manager import entrance_manager
from services.personal_assistant import PersonalAssistantService
from services.backend_connector import BackendConnector

from components.chat_interface import ChatInterface
from components.transparency_monitor import TransparencyMonitor
from components.wiki_panel import WikiPanel
from components.task_panel import TaskPanel

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DualEntranceApp:
    """双入口应用主类"""
    
    def __init__(self):
        self.app = LonaApp(__file__)
        self.backend_connector = BackendConnector()
        self.assistant_service = PersonalAssistantService(
            intent_analysis_service=self.backend_connector.intent_analysis_service,
            role_manager=self.backend_connector.role_manager,
            workflow_integrator=self.backend_connector.workflow_integrator,
            consensus_selector=self.backend_connector.consensus_selector
        )
        
        # 设置路由
        self._setup_routes()
        
        logger.info("双入口应用初始化完成")
    
    def _setup_routes(self):
        """设置路由"""
        self.app.route('/', EntranceChoiceView)
        self.app.route('/secretariat', SecretariatView)
        self.app.route('/forum', ForumView)
        self.app.route('/switch', EntranceSwitchView)
    
    async def startup(self):
        """启动应用"""
        logger.info("启动双入口应用...")
        
        # 初始化WebSocket连接
        await dual_entrance_websocket_manager.connect()
        
        # 启动后台任务
        asyncio.create_task(self._background_tasks())
        
        logger.info("双入口应用启动完成")
    
    async def _background_tasks(self):
        """后台任务"""
        while True:
            try:
                # 清理不活跃的会话
                entrance_manager.cleanup_inactive_sessions()
                
                # 等待5分钟
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"后台任务执行失败: {e}")
                await asyncio.sleep(60)
    
    def run(self, host='localhost', port=8080, debug=True):
        """运行应用"""
        print("🚀 启动 Personal Intelligence Hub 双入口系统...")
        print("📍 访问地址: http://localhost:8080")
        print("🎭 基于制度原语的集体智慧涌现平台")
        print("🔌 WebSocket实时通信: 已启用")
        print("📋 Secretariat入口: http://localhost:8080/secretariat")
        print("💬 Forum入口: http://localhost:8080/forum")
        
        # 启动异步任务
        asyncio.create_task(self.startup())
        
        self.app.run(
            host=host,
            port=port,
            debug=debug,
            shutdown_timeout=10
        )


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
        
        # 生成用户ID
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        
        # 创建用户上下文
        user_preferences = {
            "username": username or "匿名用户",
            "preferred_entrance": preferred_entrance,
            "theme": theme
        }
        
        # 异步创建用户上下文
        asyncio.create_task(
            entrance_manager.create_user_context(user_id, user_preferences)
        )
        
        # 重定向到相应的入口界面
        if entrance_type == "secretariat":
            return self._redirect_to_secretariat(user_id)
        else:
            return self._redirect_to_forum(user_id)
    
    def _redirect_to_secretariat(self, user_id):
        """重定向到Secretariat入口"""
        return HTML(
            Head(
                Title("Personal Intelligence Hub - Secretariat"),
                Link(rel="stylesheet", href="/static/css/main.css")
            ),
            Div(
                H1("📋 Secretariat 入口"),
                P(f"欢迎, 用户 {user_id}!"),
                P("正在加载Secretariat界面..."),
                P("如果页面没有自动跳转，请点击下面的链接："),
                Button(
                    "进入 Secretariat",
                    _class="btn btn-primary",
                    handle_click=lambda event: self._load_secretariat_view(user_id)
                ),
                _class="container"
            )
        )
    
    def _redirect_to_forum(self, user_id):
        """重定向到Forum入口"""
        return HTML(
            Head(
                Title("Personal Intelligence Hub - Forum"),
                Link(rel="stylesheet", href="/static/css/main.css")
            ),
            Div(
                H1("💬 Forum 入口"),
                P(f"欢迎, 用户 {user_id}!"),
                P("正在加载Forum界面..."),
                P("如果页面没有自动跳转，请点击下面的链接："),
                Button(
                    "进入 Forum",
                    _class="btn btn-secondary",
                    handle_click=lambda event: self._load_forum_view(user_id)
                ),
                _class="container"
            )
        )
    
    def _load_secretariat_view(self, user_id):
        """加载Secretariat视图"""
        # 这里可以实现实际的视图加载逻辑
        pass
    
    def _load_forum_view(self, user_id):
        """加载Forum视图"""
        # 这里可以实现实际的视图加载逻辑
        pass


class SecretariatView(View):
    """Secretariat入口界面"""
    
    async def handle_request(self, request):
        # 获取用户ID（这里简化处理，实际应该从会话中获取）
        user_id = request.GET.get('user_id', f"user_{uuid.uuid4().hex[:8]}")
        
        # 创建用户上下文
        user_context = await entrance_manager.create_user_context(user_id)
        
        # 创建会话上下文
        session_id = await entrance_manager.create_session_context(
            user_id, EntranceType.SECRETARIAT
        )
        
        # 初始化组件
        chat_interface = ChatInterface(self.assistant_service, session_id)
        transparency_monitor = TransparencyMonitor()
        wiki_panel = WikiPanel(self.backend_connector.wiki_service)
        task_panel = TaskPanel(self.backend_connector.task_service)
        
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
                
                # 用户信息显示
                Div(
                    P(f"用户: {user_context.user_id}"),
                    P(f"会话: {session_id}"),
                    Button(
                        "切换到Forum",
                        _class="btn btn-secondary",
                        handle_click=lambda event: self._switch_to_forum(user_id, session_id)
                    ),
                    _class="user-info"
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
    
    def _switch_to_forum(self, user_id, current_session_id):
        """切换到Forum入口"""
        # 这里可以实现入口切换逻辑
        pass


class ForumView(View):
    """Forum入口界面"""
    
    async def handle_request(self, request):
        # 获取用户ID
        user_id = request.GET.get('user_id', f"user_{uuid.uuid4().hex[:8]}")
        
        # 创建用户上下文
        user_context = await entrance_manager.create_user_context(user_id)
        
        # 创建会话上下文
        session_id = await entrance_manager.create_session_context(
            user_id, EntranceType.FORUM
        )
        
        # 初始化组件
        chat_interface = ChatInterface(self.assistant_service, session_id)
        transparency_monitor = TransparencyMonitor()
        wiki_panel = WikiPanel(self.backend_connector.wiki_service)
        
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
                
                # 用户信息显示
                Div(
                    P(f"用户: {user_context.user_id}"),
                    P(f"会话: {session_id}"),
                    Button(
                        "切换到Secretariat",
                        _class="btn btn-primary",
                        handle_click=lambda event: self._switch_to_secretariat(user_id, session_id)
                    ),
                    _class="user-info"
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
                            _class="participants-list"
                        ),
                        _class="participants-section"
                    ),
                    
                    # 共识监控
                    Div(
                        H2("共识状态", _class="section-title"),
                        Div(
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
    
    def _switch_to_secretariat(self, user_id, current_session_id):
        """切换到Secretariat入口"""
        # 这里可以实现入口切换逻辑
        pass


class EntranceSwitchView(View):
    """入口切换界面"""
    
    def handle_request(self, request):
        current_session = request.GET.get('session_id')
        target_entrance = request.GET.get('target_entrance')
        
        return HTML(
            Head(
                Title("Personal Intelligence Hub - 切换入口"),
                Link(rel="stylesheet", href="/static/css/main.css")
            ),
            Div(
                H1("🔄 切换入口"),
                P(f"当前会话: {current_session}"),
                P(f"目标入口: {target_entrance}"),
                P("正在切换入口..."),
                _class="container"
            )
        )


# 全局应用实例
dual_entrance_app = DualEntranceApp()

if __name__ == '__main__':
    dual_entrance_app.run()