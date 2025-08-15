#!/usr/bin/env python3
"""Personal Intelligence Hub - Main Application Entry Point

基于Lona Web框架的统一Python前后端应用
提供Personal Intelligence Hub的核心用户体验
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lona import LonaApp, View
from lona.html import H1, HTML, Div, P

# 导入组件和服务
from personal_intelligence_hub.components.chat_interface import ChatInterface
from personal_intelligence_hub.components.task_panel import TaskPanel
from personal_intelligence_hub.components.transparency_monitor import TransparencyMonitor
from personal_intelligence_hub.components.wiki_panel import WikiPanel
from personal_intelligence_hub.services.personal_assistant import PersonalAssistantService

# 创建Lona应用实例
app = LonaApp(__name__)

# 配置静态文件服务
# Lona 1.16版本使用settings配置静态文件
app.settings.STATIC_FILES_SERVE = True
app.settings.STATIC_ROOT = Path(__file__).parent / 'static'
app.settings.STATIC_URL_PREFIX = '/static/'


class PersonalIntelligenceHubView(View):
    """Personal Intelligence Hub主视图"""
    
    def __init__(self, server=None, view_runtime=None, request=None):
        if server and view_runtime and request:
            super().__init__(server, view_runtime, request)
        self.name = "hub"
        
        # 初始化服务
        self.assistant_service = PersonalAssistantService()
        
        # 初始化组件
        self.chat_interface = None
        self.transparency_monitor = None
        self.wiki_panel = None
        self.task_panel = None
    
    def handle_request(self, request):
        """处理HTTP请求并返回HTML响应"""
        # 初始化组件（延迟初始化以避免循环依赖）
        if not self.chat_interface:
            self.chat_interface = ChatInterface(self.assistant_service)
            self.transparency_monitor = TransparencyMonitor()
            self.wiki_panel = WikiPanel()
            self.task_panel = TaskPanel()
        
        return HTML(
            # 页面头部
            H1("Personal Intelligence Hub", _class="hub-title"),
            P("基于制度原语的集体智慧涌现平台", _class="hub-subtitle"),
            
            # 主要布局容器
            Div(
                # 主要聊天区域
                Div(
                    self.chat_interface,
                    _class="main-chat-area"
                ),
                
                # 右侧面板区域
                Div(
                    # 透明度监控面板
                    Div(
                        self.transparency_monitor,
                        _class="transparency-panel"
                    ),
                    
                    # Wiki知识面板
                    Div(
                        self.wiki_panel,
                        _class="wiki-panel"
                    ),
                    
                    # 任务管理面板
                    Div(
                        self.task_panel,
                        _class="task-panel"
                    ),
                    
                    _class="side-panels"
                ),
                
                _class="hub-layout"
            )
        )


class IndexView(View):
    """首页视图，重定向到Personal Intelligence Hub"""
    
    def __init__(self, server=None, view_runtime=None, request=None):
        if server and view_runtime and request:
            super().__init__(server, view_runtime, request)
        self.name = "index"
    
    def handle_request(self, request):
        return HTML(
            H1("欢迎使用 Personal Intelligence Hub"),
            P("正在初始化系统..."),
            Div(
                P("系统将自动跳转到主界面"),
                _class="loading-message"
            )
        )


# 配置路由
@app.route('/')
class IndexView(View):
    """首页视图，重定向到Personal Intelligence Hub"""
    
    def handle_request(self, request):
        return HTML(
            H1("欢迎使用 Personal Intelligence Hub"),
            P("正在初始化系统..."),
            Div(
                P("系统将自动跳转到主界面"),
                _class="loading-message"
            )
        )

@app.route('/hub')
class PersonalIntelligenceHubView(View):
    """Personal Intelligence Hub主视图"""
    
    def __init__(self, server=None, view_runtime=None, request=None):
        if server and view_runtime and request:
            super().__init__(server, view_runtime, request)
    
    def handle_request(self, request):
        """处理HTTP请求并返回HTML响应"""
        # 初始化服务
        self.assistant_service = PersonalAssistantService()
        
        # 初始化组件
        self.chat_interface = ChatInterface(self.assistant_service)
        self.transparency_monitor = TransparencyMonitor()
        self.wiki_panel = WikiPanel()
        self.task_panel = TaskPanel()
        
        return HTML(
            # 页面头部
            H1("Personal Intelligence Hub", _class="hub-title"),
            P("基于制度原语的集体智慧涌现平台", _class="hub-subtitle"),
            
            # 主要布局容器
            Div(
                # 主要聊天区域
                Div(
                    self.chat_interface,
                    _class="main-chat-area"
                ),
                
                # 右侧面板区域
                Div(
                    # 透明度监控面板
                    Div(
                        self.transparency_monitor,
                        _class="transparency-panel"
                    ),
                    
                    # Wiki知识面板
                    Div(
                        self.wiki_panel,
                        _class="wiki-panel"
                    ),
                    
                    # 任务管理面板
                    Div(
                        self.task_panel,
                        _class="task-panel"
                    ),
                    
                    _class="side-panels"
                ),
                
                _class="hub-layout"
            )
        )


def main():
    """主函数 - 启动Lona应用"""
    # 配置应用设置
    app.settings.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    app.settings.HOST = os.getenv('HOST', 'localhost')
    app.settings.PORT = int(os.getenv('PORT', '8086'))
    
    # 启动应用
    print("🎭 Personal Intelligence Hub 正在启动...")
    print(f"📍 访问地址: http://{app.settings.HOST}:{app.settings.PORT}")
    print(f"🚀 主界面: http://{app.settings.HOST}:{app.settings.PORT}/hub")
    
    try:
        app.run(
            host=app.settings.HOST,
            port=app.settings.PORT,
            debug=app.settings.DEBUG
        )
    except KeyboardInterrupt:
        print("\n👋 Personal Intelligence Hub 已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
