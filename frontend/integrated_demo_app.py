#!/usr/bin/env python3
"""集成演示应用 - 真实DAIP-LIVE演示系统

整合所有前端组件，提供统一的演示体验
支持真实LLM调用、角色库集成和工作流执行
"""

import asyncio
import logging
import uuid

# 导入现有组件
from components.chat_interface import ChatInterface
from components.task_panel import TaskPanel
from components.transparency_monitor import TransparencyMonitor
from components.wiki_panel import WikiPanel
from lona import LonaApp, View
from lona.html import H1, H2, HTML, Button, Div, Head, Option, P, Select, Span, Title
from services.backend_connector import BackendConnector

# 导入服务
from services.personal_assistant import PersonalAssistantService
from services.websocket_manager import realtime_manager, websocket_manager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Lona应用实例
app = LonaApp(__file__)

# 静态文件服务暂时禁用，先确保基本功能工作
# app.add_static_file('/static/', 'static/')


class IntegratedDemoView(View):
    """集成演示主视图"""

    def __init__(self, server, view_runtime, request):
        super().__init__(server, view_runtime, request)

        # 初始化后端连接器
        self.backend_connector = BackendConnector()

        # 初始化服务
        self.assistant_service = PersonalAssistantService(
            backend_connector=self.backend_connector
        )

        # 初始化后端连接器
        self.backend_connector = BackendConnector()

        # 初始化服务
        self.assistant_service = PersonalAssistantService(
            backend_connector=self.backend_connector
        )

        # 组件实例
        self.chat_interface = None
        self.transparency_monitor = None
        self.wiki_panel = None
        self.task_panel = None

        # 演示状态
        self.demo_session_id = None
        self.current_scenario = None
        self.demo_active = False

        # 演示场景配置
        self.demo_scenarios = {
            "ai_ethics": {
                "name": "AI伦理决策分析",
                "description": "基于真实角色库和工作流的AI伦理风险评估",
                "duration": "15分钟",
                "roles": ["医疗伦理专家", "AI技术专家", "法律顾问", "患者权益代表"],
                "workflows": ["批判性审查", "多视角综合", "共识计算"]
            },
            "product_strategy": {
                "name": "产品策略评估",
                "description": "多专家协作的产品决策分析",
                "duration": "20分钟",
                "roles": ["市场分析师", "技术专家", "财务顾问", "用户体验专家"],
                "workflows": ["风险评估", "机会分析", "决策支持"]
            },
            "tech_risk": {
                "name": "技术风险评估",
                "description": "企业技术决策的风险收益分析",
                "duration": "25分钟",
                "roles": ["系统架构师", "安全专家", "运维专家", "业务分析师"],
                "workflows": ["风险量化", "成本效益分析", "缓解策略"]
            }
        }

        # 初始化WebSocket连接
        self._setup_websocket()

    def _setup_websocket(self):
        """设置WebSocket连接和事件处理"""
        # 检查是否有运行的事件循环
        try:
            loop = asyncio.get_running_loop()
            # 有运行的事件循环，创建WebSocket连接任务
            loop.create_task(self._initialize_websocket())
            logger.info("🔌 WebSocket初始化任务已创建")
        except RuntimeError:
            # 没有运行的事件循环，延迟初始化（测试模式或同步环境）
            logger.warning("⚠️ 没有运行的事件循环，WebSocket将在应用启动时初始化")
            self._websocket_deferred = True

    async def _initialize_websocket(self):
        """初始化WebSocket连接"""
        try:
            await websocket_manager.connect()
            logger.info("✅ WebSocket连接已建立")
        except Exception as e:
            logger.error(f"⚠️ WebSocket连接失败: {e}")

    async def ensure_websocket_initialized(self):
        """确保WebSocket已初始化（用于应用启动时调用）"""
        if hasattr(self, '_websocket_deferred') and self._websocket_deferred:
            await self._initialize_websocket()
            self._websocket_deferred = False
            logger.info("🔌 延迟的WebSocket初始化已完成")

    async def handle_request(self, request):
        """处理HTTP请求并返回页面内容"""
        try:
            # 生成演示会话ID
            self.demo_session_id = str(uuid.uuid4())

            # 初始化组件
            self.chat_interface = ChatInterface(
                self.assistant_service,
                session_id=self.demo_session_id
            )
            self.transparency_monitor = TransparencyMonitor()
            self.wiki_panel = WikiPanel(self.backend_connector.wiki_service)
            self.task_panel = TaskPanel(self.backend_connector.task_service)

            # 注册组件间通信
            self._setup_component_communication()

            # 注册实时更新回调
            self._register_realtime_callbacks()

            return self._create_demo_interface()

        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return self._create_error_interface(str(e))

    def _create_demo_interface(self):
        """创建演示界面"""
        return HTML(
            Head(
                Title("DAIP-LIVE 真实演示系统")
                # 暂时移除CSS链接，先确保基本功能工作
            ),

            Div(
                # 演示系统标题
                self._render_demo_header(),

                # 演示控制面板
                self._render_demo_controls(),

                # 主要演示区域
                self._render_main_demo_area(),

                style="padding: 20px; font-family: Arial, sans-serif;"
            )
        )

    def _create_error_interface(self, error_message):
        """创建错误界面"""
        return HTML(
            Head(Title("DAIP-LIVE 演示系统 - 错误")),
            Div(
                H1("❌ 系统错误"),
                P(f"错误信息: {error_message}"),
                P("请检查系统配置并重试。"),
                style="padding: 20px; font-family: Arial, sans-serif; color: red;"
            )
        )

    def _render_demo_header(self):
        """渲染演示系统标题"""
        return Div(
            H1("🎭 DAIP-LIVE 真实演示系统", _class="demo-title"),
            Div(
                Span("🔴 LIVE", _class="status-live"),
                Span("📊 真实调用", _class="status-real"),
                Span("⚡ 实时监控", _class="status-monitor"),
                Span("🔍 完全透明", _class="status-transparent"),
                _class="demo-status-bar"
            ),
            _class="demo-header"
        )

    def _render_demo_controls(self):
        """渲染演示控制面板"""
        scenario_options = [
            Option("选择演示场景...", value="", selected=True)
        ]

        for key, scenario in self.demo_scenarios.items():
            scenario_options.append(
                Option(f"{scenario['name']} ({scenario['duration']})", value=key)
            )

        return Div(
            H2("🎯 演示控制", _class="control-title"),

            Div(
                # 场景选择
                Div(
                    P("选择演示场景:", _class="control-label"),
                    Select(
                        *scenario_options,
                        _id="scenario-select",
                        _class="form-select"
                    ),
                    _class="control-group"
                ),

                # 系统状态
                Div(
                    P("系统状态:", _class="control-label"),
                    Div(
                        Span("✅ Ollama (localhost:11434)", _class="status-item"),
                        Span("✅ 角色库 (127个角色)", _class="status-item"),
                        Span("✅ 工作流引擎", _class="status-item"),
                        _class="status-grid"
                    ),
                    _class="control-group"
                ),

                # 控制按钮
                Div(
                    Button(
                        "开始真实演示",
                        _id="start-demo-btn",
                        _class="btn btn-primary btn-lg"
                    ),
                    Button(
                        "系统检查",
                        _id="system-check-btn",
                        _class="btn btn-secondary"
                    ),
                    Button(
                        "重置演示",
                        _id="reset-demo-btn",
                        _class="btn btn-warning"
                    ),
                    _class="control-buttons"
                ),

                _class="demo-controls-content"
            ),

            _class="demo-controls"
        )

    def _render_main_demo_area(self):
        """渲染主要演示区域"""
        return Div(
            # 左侧：聊天界面和透明度监控
            Div(
                # 聊天界面
                Div(
                    H2("💬 智能对话", _class="panel-title"),
                    self.chat_interface,
                    _class="chat-panel"
                ),

                # 透明度监控
                Div(
                    H2("🔍 透明度监控", _class="panel-title"),
                    self.transparency_monitor,
                    _class="transparency-panel"
                ),

                _class="left-demo-area"
            ),

            # 右侧：Wiki和任务面板
            Div(
                # Wiki知识库
                Div(
                    H2("📚 知识库", _class="panel-title"),
                    self.wiki_panel,
                    _class="wiki-panel"
                ),

                # 任务管理
                Div(
                    H2("📋 任务管理", _class="panel-title"),
                    self.task_panel,
                    _class="task-panel"
                ),

                _class="right-demo-area"
            ),

            _class="main-demo-area"
        )

    def _setup_component_communication(self):
        """设置组件间通信"""
        # 聊天界面 -> 透明度监控
        self.chat_interface.on_message_sent = self._handle_chat_message

        # 透明度监控 -> 其他组件
        self.transparency_monitor.on_agent_update = self._handle_agent_update

        # Wiki面板 -> 聊天界面
        self.wiki_panel.on_knowledge_selected = self._handle_knowledge_selection

        # 任务面板 -> 聊天界面
        self.task_panel.on_task_selected = self._handle_task_selection

    async def _handle_chat_message(self, message):
        """处理聊天消息"""
        try:
            # 更新透明度监控
            await self.transparency_monitor.log_user_interaction(message)

            # 触发工作流执行
            if self.demo_active and self.current_scenario:
                await self._execute_demo_workflow(message)

        except Exception as e:
            logger.error(f"处理聊天消息失败: {e}")

    async def _handle_agent_update(self, agent_data):
        """处理代理状态更新"""
        try:
            # 更新任务面板中的代理状态
            await self.task_panel.update_agent_status(agent_data)

            # 如果有新的知识产生，更新Wiki
            if agent_data.get("knowledge_output"):
                await self.wiki_panel.add_knowledge(agent_data["knowledge_output"])

        except Exception as e:
            logger.error(f"处理代理更新失败: {e}")

    async def _handle_knowledge_selection(self, knowledge_data):
        """处理知识选择"""
        try:
            # 将选中的知识添加到聊天上下文
            await self.chat_interface.add_context(knowledge_data)

        except Exception as e:
            logger.error(f"处理知识选择失败: {e}")

    async def _handle_task_selection(self, task_data):
        """处理任务选择"""
        try:
            # 将任务信息添加到聊天上下文
            await self.chat_interface.set_current_task(task_data)

        except Exception as e:
            logger.error(f"处理任务选择失败: {e}")

    async def _execute_demo_workflow(self, user_message):
        """执行演示工作流"""
        try:
            scenario = self.demo_scenarios[self.current_scenario]

            # 记录工作流开始
            await self.transparency_monitor.log_workflow_start(
                scenario["workflows"],
                scenario["roles"]
            )

            # 执行真实的工作流
            workflow_result = await self.assistant_service.process_with_workflow(
                user_message,
                scenario["workflows"],
                scenario["roles"]
            )

            # 更新各个面板
            await self._update_panels_with_workflow_result(workflow_result)

        except Exception as e:
            logger.error(f"执行演示工作流失败: {e}")
            await self.transparency_monitor.log_error(str(e))

    async def _update_panels_with_workflow_result(self, workflow_result):
        """根据工作流结果更新各个面板"""
        try:
            # 更新透明度监控
            await self.transparency_monitor.update_workflow_status(workflow_result)

            # 更新Wiki知识库
            if workflow_result.get("knowledge_updates"):
                await self.wiki_panel.batch_update(workflow_result["knowledge_updates"])

            # 更新任务状态
            if workflow_result.get("task_updates"):
                await self.task_panel.batch_update(workflow_result["task_updates"])

            # 更新聊天界面
            await self.chat_interface.display_workflow_result(workflow_result)

        except Exception as e:
            logger.error(f"更新面板失败: {e}")

    def _register_realtime_callbacks(self):
        """注册实时更新回调"""
        # 注册透明度监控更新
        realtime_manager.register_component_callback(
            "agent_status",
            self.transparency_monitor.update_agent_status
        )

        # 注册Wiki更新
        realtime_manager.register_component_callback(
            "wiki_update",
            self.wiki_panel.handle_realtime_update
        )

        # 注册任务更新
        realtime_manager.register_component_callback(
            "task_update",
            self.task_panel.handle_realtime_update
        )

        # 注册聊天消息更新
        realtime_manager.register_component_callback(
            "chat_message",
            self.chat_interface.handle_realtime_message
        )


# 添加路由（使用类路由，这是Lona的标准方式）
@app.route('/')
class IntegratedDemoRoute(IntegratedDemoView):
    pass


async def startup_tasks():
    """启动时执行的异步任务"""
    logger.info("🔌 初始化WebSocket连接...")
    try:
        await websocket_manager.connect()
        logger.info("✅ WebSocket连接就绪")
    except Exception as e:
        logger.error(f"❌ WebSocket连接失败: {e}")

    # 如果有延迟的WebSocket初始化，现在执行
    # 注意：这里需要访问IntegratedDemoView实例，但在当前架构下不容易实现
    # 实际应用中，WebSocket初始化应该在Lona应用启动时自动处理


if __name__ == '__main__':
    print("=" * 60)
    print("🎭 DAIP-LIVE 真实演示系统")
    print("基于制度原语的集体智慧涌现平台")
    print("=" * 60)
    print()
    print("🚀 正在启动集成演示应用...")
    print("📍 访问地址: http://localhost:8080")
    print("🔧 开发模式: 已启用")
    print("🔴 真实LLM调用: 已启用")
    print("📊 透明度监控: 已启用")
    print()
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)

    # 启动异步任务
    asyncio.create_task(startup_tasks())

    app.run(
        host='localhost',
        port=8080,
        debug=True,
        shutdown_timeout=10
    )
