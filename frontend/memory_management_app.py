#!/usr/bin/env python3
"""智能记忆管理应用

基于MemAgent的记忆管理界面，提供完整的记忆管理功能
"""

import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from frontend.components.memory_panel import MemoryPanel
from lona import App
from lona.html import H1, H2, HTML, Button, Div, P
from lona.view import TemplateView
from frontend.services.memory_service import MemoryService

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Lona应用
app = App(__name__)


class MemoryManagementView(TemplateView):
    """记忆管理主视图"""
    
    def __init__(self, request):
        super().__init__(request)
        self.memory_service = MemoryService()
        self.memory_panel = None
        
    async def handle_request(self, request):
        """处理请求"""
        try:
            # 初始化服务
            await self.memory_service.initialize()
            
            # 创建记忆面板
            self.memory_panel = MemoryPanel(self.memory_service)
            
            # 创建主界面
            return self.create_main_interface()
            
        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return self.create_error_interface(str(e))
    
    def create_main_interface(self) -> HTML:
        """创建主界面"""
        return HTML(
            Div(
                # 页面标题
                Div(
                    H1("🧠 DAIP-LIVE 智能记忆管理系统", style="text-align: center; margin-bottom: 10px;"),
                    P("基于MemAgent的智能记忆管理，支持多对话记忆、强化学习选择和记忆共享", 
                      style="text-align: center; color: #6c757d; margin-bottom: 30px;"),
                    style="margin-bottom: 40px;"
                ),
                
                # 功能导航
                Div(
                    Button("记忆管理", _class="nav-btn active", onclick=self.show_memory_panel),
                    Button("记忆分析", _class="nav-btn", onclick=self.show_analysis_panel),
                    Button("协作共享", _class="nav-btn", onclick=self.show_sharing_panel),
                    Button("系统设置", _class="nav-btn", onclick=self.show_settings_panel),
                    style="display: flex; justify-content: center; gap: 15px; margin-bottom: 30px;"
                ),
                
                # 主内容区域
                Div(
                    self.memory_panel.render() if self.memory_panel else Div(),
                    _id="main-content",
                    style="max-width: 1200px; margin: 0 auto; padding: 0 20px;"
                ),
                
                # 页脚
                Div(
                    P("DAIP-LIVE 真实演示系统 - 智能记忆管理模块", 
                      style="text-align: center; color: #6c757d; font-size: 0.9rem;"),
                    style="margin-top: 50px; padding: 20px; border-top: 1px solid #e9ecef;"
                ),
                
                style="min-height: 100vh; background: #f8f9fa;"
            )
        )
    
    def create_error_interface(self, error_message: str) -> HTML:
        """创建错误界面"""
        return HTML(
            Div(
                Div(
                    H1("❌ 系统错误", style="color: #dc3545; text-align: center;"),
                    P(f"初始化记忆管理系统时发生错误: {error_message}", 
                      style="text-align: center; color: #6c757d;"),
                    Button(
                        "重新加载",
                        _class="btn btn-primary",
                        onclick=lambda e: self.request.redirect('/'),
                        style="display: block; margin: 20px auto;"
                    ),
                    style="max-width: 600px; margin: 100px auto; padding: 40px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);"
                ),
                style="min-height: 100vh; background: #f8f9fa; display: flex; align-items: center;"
            )
        )
    
    async def show_memory_panel(self, event):
        """显示记忆管理面板"""
        # 更新导航状态
        self.update_nav_state("记忆管理")
        
        # 显示记忆面板
        if self.memory_panel:
            await self.memory_panel.refresh()
    
    async def show_analysis_panel(self, event):
        """显示记忆分析面板"""
        self.update_nav_state("记忆分析")
        
        # 创建分析面板
        analysis_content = self.create_analysis_panel()
        self.update_main_content(analysis_content)
    
    async def show_sharing_panel(self, event):
        """显示协作共享面板"""
        self.update_nav_state("协作共享")
        
        # 创建共享面板
        sharing_content = self.create_sharing_panel()
        self.update_main_content(sharing_content)
    
    async def show_settings_panel(self, event):
        """显示系统设置面板"""
        self.update_nav_state("系统设置")
        
        # 创建设置面板
        settings_content = self.create_settings_panel()
        self.update_main_content(settings_content)
    
    def update_nav_state(self, active_nav: str):
        """更新导航状态"""
        # 这里需要JavaScript支持来更新导航按钮状态
        pass
    
    def update_main_content(self, content: HTML):
        """更新主内容区域"""
        # 这里需要JavaScript支持来动态更新内容
        pass
    
    def create_analysis_panel(self) -> HTML:
        """创建记忆分析面板"""
        return Div(
            H2("📊 记忆分析", style="margin-bottom: 20px;"),
            
            # 统计卡片
            Div(
                Div(
                    H3("记忆总数", style="margin-bottom: 10px;"),
                    P("156", style="font-size: 2rem; font-weight: bold; color: #007bff; margin: 0;"),
                    P("个记忆单元", style="color: #6c757d; margin: 0;"),
                    style="text-align: center; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                ),
                Div(
                    H3("平均重要性", style="margin-bottom: 10px;"),
                    P("0.73", style="font-size: 2rem; font-weight: bold; color: #28a745; margin: 0;"),
                    P("重要性评分", style="color: #6c757d; margin: 0;"),
                    style="text-align: center; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                ),
                Div(
                    H3("活跃记忆", style="margin-bottom: 10px;"),
                    P("42", style="font-size: 2rem; font-weight: bold; color: #ffc107; margin: 0;"),
                    P("高频访问", style="color: #6c757d; margin: 0;"),
                    style="text-align: center; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                ),
                style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px;"
            ),
            
            # 记忆类型分布
            Div(
                H3("记忆类型分布", style="margin-bottom: 15px;"),
                Div(
                    Div("📅 情节记忆: 45%", style="margin-bottom: 10px;"),
                    Div("📚 语义记忆: 30%", style="margin-bottom: 10px;"),
                    Div("⚙️ 程序记忆: 20%", style="margin-bottom: 10px;"),
                    Div("🧠 元认知记忆: 5%", style="margin-bottom: 10px;"),
                ),
                style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
            )
        )
    
    def create_sharing_panel(self) -> HTML:
        """创建协作共享面板"""
        return Div(
            H2("🤝 协作共享", style="margin-bottom: 20px;"),
            
            # 共享操作区域
            Div(
                H3("记忆共享", style="margin-bottom: 15px;"),
                Div(
                    Div(
                        P("源用户:", style="font-weight: 500; margin-bottom: 5px;"),
                        Button("选择用户", _class="btn btn-outline-primary", style="width: 100%;"),
                        style="margin-bottom: 15px;"
                    ),
                    Div(
                        P("目标用户:", style="font-weight: 500; margin-bottom: 5px;"),
                        Button("选择用户", _class="btn btn-outline-primary", style="width: 100%;"),
                        style="margin-bottom: 15px;"
                    ),
                    Div(
                        P("选择记忆:", style="font-weight: 500; margin-bottom: 5px;"),
                        Button("选择记忆", _class="btn btn-outline-success", style="width: 100%;"),
                        style="margin-bottom: 20px;"
                    ),
                    Button("执行共享", _class="btn btn-success", style="width: 100%;"),
                    style="max-width: 300px;"
                ),
                style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px;"
            ),
            
            # 共享历史
            Div(
                H3("共享历史", style="margin-bottom: 15px;"),
                Div(
                    P("暂无共享记录", style="text-align: center; color: #6c757d; padding: 40px;")
                ),
                style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
            )
        )
    
    def create_settings_panel(self) -> HTML:
        """创建系统设置面板"""
        return Div(
            H2("⚙️ 系统设置", style="margin-bottom: 20px;"),
            
            # MemAgent设置
            Div(
                H3("MemAgent 配置", style="margin-bottom: 15px;"),
                Div(
                    Div(
                        P("强化学习:", style="font-weight: 500; margin-bottom: 5px;"),
                        Button("已启用", _class="btn btn-success btn-sm"),
                        style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;"
                    ),
                    Div(
                        P("记忆整合:", style="font-weight: 500; margin-bottom: 5px;"),
                        Button("自动", _class="btn btn-info btn-sm"),
                        style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;"
                    ),
                    Div(
                        P("向量搜索:", style="font-weight: 500; margin-bottom: 5px;"),
                        Button("已启用", _class="btn btn-success btn-sm"),
                        style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;"
                    ),
                ),
                style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;"
            ),
            
            # 系统信息
            Div(
                H3("系统信息", style="margin-bottom: 15px;"),
                Div(
                    P("版本: DAIP-LIVE v1.0", style="margin-bottom: 8px;"),
                    P("MemAgent: 基于ByteDance/Tsinghua论文实现", style="margin-bottom: 8px;"),
                    P("存储后端: Enhanced SSKG Manager", style="margin-bottom: 8px;"),
                    P("最后更新: 2025-01-27", style="margin-bottom: 0;"),
                ),
                style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
            )
        )


# 路由配置
@app.route('/')
async def memory_management_route(request):
    """记忆管理主路由"""
    view = MemoryManagementView(request)
    return await view.handle_request(request)


if __name__ == '__main__':
    print("🚀 启动智能记忆管理系统...")
    print("📍 访问地址: http://localhost:8080")
    app.run(host='127.0.0.1', port=8080, debug=True)