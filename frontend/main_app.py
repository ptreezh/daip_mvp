#!/usr/bin/env python3
"""Personal Intelligence Hub - Lona Web应用入口点

基于Lona Web框架的统一Python前后端解决方案
为DAIP-LIVE项目提供直观的用户交互界面
"""

import asyncio
import logging

from lona import LonaApp, View
from lona.html import H1, HTML, Div, Head, Link, Title

logger = logging.getLogger(__name__)

# 导入组件
from components.chat_interface import ChatInterface
from components.task_panel import TaskPanel
from components.transparency_monitor import TransparencyMonitor
from components.wiki_panel import WikiPanel
from services.backend_connector import BackendConnector

# 导入服务
from services.personal_assistant import PersonalAssistantService
from services.websocket_manager import realtime_manager, websocket_manager

# 创建Lona应用实例
app = LonaApp(__file__)

# 配置静态文件服务
# app.add_static_file_view(
#     '/static/',
#     StaticFilesView('static/')
# )


class PersonalIntelligenceHubView(View):
    """Personal Intelligence Hub主视图"""

    def __init__(self):
        super().__init__()

        # 初始化后端连接器
        self.backend_connector = BackendConnector()

        # 初始化服务
        self.assistant_service = PersonalAssistantService(intent_analysis_service=self.backend_connector.intent_analysis_service, role_manager=self.backend_connector.role_manager, workflow_integrator=self.backend_connector.workflow_integrator, consensus_selector=self.backend_connector.consensus_selector)

        # 初始化组件
        self.chat_interface = None
        self.transparency_monitor = None
        self.wiki_panel = None
        self.task_panel = None

        # 初始化WebSocket连接
        self._setup_websocket()

    def _setup_websocket(self):
        """设置WebSocket连接和事件处理"""
        # 启动WebSocket连接任务
        asyncio.create_task(self._initialize_websocket())

    async def _initialize_websocket(self):
        """初始化WebSocket连接"""
        try:
            await websocket_manager.connect()
            print("✅ WebSocket连接已建立")
        except Exception as e:
            print(f"⚠️ WebSocket连接失败: {e}")

    def handle_request(self, request):
        """处理HTTP请求并返回页面内容"""
        # 初始化组件（在请求时初始化以确保正确的上下文）
        # Obtain session_id from request, or generate one if not available
        # Assuming request.session.sid is available in Lona's request object
        session_id = getattr(request.session, 'sid', None)
        if not session_id:
            # Fallback if session ID is not directly available
            import uuid
            session_id = str(uuid.uuid4())
            logger.warning(f"Session ID not found in request, generated a new one: {session_id}")

        self.chat_interface = ChatInterface(self.assistant_service, session_id=session_id)
        self.transparency_monitor = TransparencyMonitor()
        self.wiki_panel = WikiPanel(self.backend_connector.wiki_service)
        self.task_panel = TaskPanel(self.backend_connector.task_service)

        # 注册实时更新回调
        self._register_realtime_callbacks()

        return HTML(
            Head(
                Title("Personal Intelligence Hub - DAIP-LIVE"),
                Link(
                    rel="stylesheet",
                    href="/static/css/main.css"
                ),
                Link(
                    rel="stylesheet",
                    href="/static/css/components.css"
                )
            ),

            Div(
                # 页面标题
                H1(
                    "🎭 Personal Intelligence Hub",
                    _class="page-title"
                ),

                # 主要布局容器
                Div(
                    # 左侧主要聊天区域
                    Div(
                        self.chat_interface,
                        _class="main-chat-area"
                    ),

                    # 右侧面板区域
                    Div(
                        # 透明度监控面板
                        Div(
                            self.transparency_monitor,
                            _class="panel transparency-panel"
                        ),

                        # Wiki知识库面板
                        Div(
                            self.wiki_panel,
                            _class="panel wiki-panel"
                        ),

                        # 任务管理面板
                        Div(
                            self.task_panel,
                            _class="panel task-panel"
                        ),

                        _class="side-panels"
                    ),

                    _class="hub-layout"
                ),

                _class="container"
            )
        )

    def _register_realtime_callbacks(self):
        """注册实时更新回调"""
        # 注册透明度监控更新
        realtime_manager.register_component_callback(
            "agent_status",
            self.transparency_monitor.update_agent_status
        )

        # 注册Wiki更新
        realtime_manager.register_component_callback(
            "wiki",
            self.wiki_panel.handle_realtime_update
        )

        # 注册任务更新
        realtime_manager.register_component_callback(
            "task",
            self.task_panel.handle_realtime_update
        )


# 添加路由
app.route('/', PersonalIntelligenceHubView)


async def startup_tasks():
    """启动时执行的异步任务"""
    print("🔌 初始化WebSocket连接...")
    await websocket_manager.connect()
    print("✅ WebSocket连接就绪")


if __name__ == '__main__':
    print("🚀 启动 Personal Intelligence Hub...")
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
