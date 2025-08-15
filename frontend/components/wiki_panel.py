#!/usr/bin/env python3
"""Wiki面板组件 - 简化版本

显示和管理知识库内容，支持实时更新
"""

from datetime import datetime

from lona.html import H3, HTML, Button, Div, P, TextInput
from lona.html.widget import Widget


class WikiPanel(Widget):
    """Wiki面板组件"""
    
    def __init__(self, wiki_service):
        super().__init__()
        
        self.wiki_service = wiki_service
        
        # 模拟数据
        self.current_page = {
            "title": "AI协作原理",
            "content": "多代理协作系统通过制度原语实现集体智慧涌现...",
            "quality_score": 0.85,
            "last_updated": "2024-01-15 14:25"
        }
        
        self.recent_updates = [
            {"title": "共识算法", "type": "新增", "time": "14:30"},
            {"title": "认知多样性", "type": "更新", "time": "14:15"},
        ]
        
        # 创建搜索输入框
        self.search_input = TextInput(
            placeholder="搜索知识库...",
            _class="form-input"
        )
        self.search_button = Button(
            "搜索",
            _class="btn btn-success btn-sm"
        )
    
    async def handle_realtime_update(self, data):
        """处理实时Wiki更新（WebSocket回调）"""
        try:
            update_type = data.get("type")
            page_data = data.get("page")
            
            if update_type == "page_updated" and page_data:
                # 更新当前页面
                if page_data.get("id") == self.current_page.get("id"):
                    self.current_page.update(page_data)
            
            elif update_type == "new_fact":
                # 添加新的更新记录
                current_time = datetime.now().strftime("%H:%M")
                self.recent_updates.insert(0, {
                    "title": data.get("title", "新事实"),
                    "type": "新增",
                    "time": current_time
                })
                
                # 保持更新列表长度
                if len(self.recent_updates) > 10:
                    self.recent_updates = self.recent_updates[:10]
            
            # 刷新组件显示
        except Exception as e:
            print(f"处理Wiki更新失败: {e}")
    
    def render(self) -> HTML:
        return Div(
            H3("📚 知识库", _class="panel-title"),
            
            # 搜索区域
            Div(
                self.search_input,
                self.search_button,
                style="display: flex; gap: 8px; margin-bottom: 15px;"
            ),
            
            # 当前页面
            Div(
                P(f"📄 {self.current_page['title']}", style="font-weight: 600; margin-bottom: 8px;"),
                P(f"质量评分: {self.current_page['quality_score']:.2f}", style="font-size: 0.85rem; color: #28a745; margin-bottom: 5px;"),
                P(self.current_page['content'][:100] + "...", style="font-size: 0.9rem; line-height: 1.4; margin-bottom: 8px;"),
                P(f"更新时间: {self.current_page['last_updated']}", style="font-size: 0.8rem; color: #6c757d;"),
                style="border: 1px solid #e9ecef; border-radius: 6px; padding: 12px; background: #f8f9fa; margin-bottom: 15px;"
            ),
            
            # 最近更新
            Div(
                P("最近更新:", style="font-weight: 600; margin-bottom: 10px;"),
                *[
                    Div(
                        Span(update["title"], style="font-weight: 500;"),
                        Span(
                            update["type"], 
                            _class=f"badge badge-{'success' if update['type'] == '新增' else 'info'}",
                            style="margin-left: 8px;"
                        ),
                        P(f"时间: {update['time']}", style="font-size: 0.8rem; color: #6c757d; margin: 3px 0 0 0;"),
                        style="padding: 8px; border-left: 3px solid #2ecc71; background: #f8f9fa; margin-bottom: 6px;"
                    )
                    for update in self.recent_updates
                ]
            ),
            
            _class="wiki-panel"
        )
