#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务面板组件 - 简化版本

显示和管理任务状态，支持任务分解和跟踪
"""

from lona.html.widget import Widget
from lona.html import HTML, Div, H3, P, Span, Select, Option
from datetime import datetime


class TaskPanel(Widget):
    """任务面板组件"""
    
    def __init__(self, task_service):
        super().__init__()
        
        self.task_service = task_service
        
        # 模拟任务数据
        self.tasks = [
            {
                "id": "1",
                "title": "分析AI威胁论",
                "status": "in_progress",
                "assigned_agent": "Dr. 理性分析师",
                "progress": 65,
                "subtasks": [
                    {"title": "收集相关资料", "status": "completed"},
                    {"title": "多角度分析", "status": "in_progress"},
                    {"title": "形成结论", "status": "not_started"}
                ]
            },
            {
                "id": "2", 
                "title": "生成共识报告",
                "status": "not_started",
                "assigned_agent": "创意直觉师",
                "progress": 0,
                "subtasks": []
            }
        ]
    
    async def handle_realtime_update(self, data):
        """处理实时任务更新（WebSocket回调）"""
        try:
            update_type = data.get("type")
            task_data = data.get("task")
            
            if update_type == "task_created" and task_data:
                # 添加新任务
                self.tasks.append(task_data)
            
            elif update_type == "task_updated" and task_data:
                # 更新现有任务
                task_id = task_data.get("id")
                for i, task in enumerate(self.tasks):
                    if task["id"] == task_id:
                        self.tasks[i].update(task_data)
                        break
            
            elif update_type == "status_changed":
                # 更新任务状态
                task_id = data.get("task_id")
                new_status = data.get("status")
                for task in self.tasks:
                    if task["id"] == task_id:
                        task["status"] = new_status
                        # 根据状态更新进度
                        if new_status == "completed":
                            task["progress"] = 100
                        elif new_status == "in_progress" and task["progress"] == 0:
                            task["progress"] = 10
                        break
            
            # 刷新组件显示
            await self.refresh()
            
        except Exception as e:
            print(f"处理任务更新失败: {e}")
    
    def get_status_color(self, status):
        """获取状态对应的颜色"""
        colors = {
            "not_started": "secondary",
            "in_progress": "warning", 
            "completed": "success",
            "blocked": "danger"
        }
        return colors.get(status, "secondary")
    
    def get_status_text(self, status):
        """获取状态对应的中文文本"""
        texts = {
            "not_started": "未开始",
            "in_progress": "进行中",
            "completed": "已完成", 
            "blocked": "阻塞"
        }
        return texts.get(status, status)
    
    def render(self) -> HTML:
        return Div(
            H3("📋 任务管理", _class="panel-title"),
            
            # 任务列表
            Div(
                *[
                    Div(
                        # 任务头部
                        Div(
                            Div(
                                P(task["title"], style="font-weight: 600; margin: 0; color: #2c3e50;"),
                                P(f"负责人: {task['assigned_agent']}", style="font-size: 0.85rem; color: #6c757d; margin: 3px 0 0 0;"),
                                style="flex: 1;"
                            ),
                            Span(
                                self.get_status_text(task["status"]),
                                _class=f"badge badge-{self.get_status_color(task['status'])}",
                                style="align-self: flex-start;"
                            ),
                            style="display: flex; align-items: flex-start; gap: 10px; margin-bottom: 10px;"
                        ),
                        
                        # 进度条
                        Div(
                            Div(
                                style=f"width: {task['progress']}%; height: 100%; background: #2ecc71; border-radius: 4px; transition: width 0.3s;"
                            ),
                            style="width: 100%; height: 8px; background: #e9ecef; border-radius: 4px; margin-bottom: 10px;"
                        ),
                        
                        # 子任务（如果有）
                        Div(
                            *[
                                Div(
                                    Span("• ", style="color: #6c757d;"),
                                    Span(subtask["title"], style="font-size: 0.85rem;"),
                                    Span(
                                        self.get_status_text(subtask["status"]),
                                        _class=f"badge badge-{self.get_status_color(subtask['status'])}",
                                        style="margin-left: 8px; font-size: 0.7rem;"
                                    ),
                                    style="margin-bottom: 4px;"
                                )
                                for subtask in task["subtasks"]
                            ],
                            style="padding-left: 10px; border-left: 2px solid #e9ecef;" if task["subtasks"] else "display: none;"
                        ),
                        
                        style="border: 1px solid #e9ecef; border-left: 4px solid #f39c12; border-radius: 6px; padding: 12px; margin-bottom: 12px; background: white;"
                    )
                    for task in self.tasks
                ],
                style="max-height: 400px; overflow-y: auto;"
            ),
            
            # 任务统计
            Div(
                P("任务统计", style="font-weight: 600; color: white; margin: 0;"),
                P(f"总计: {len(self.tasks)} | 进行中: 1 | 已完成: 0", style="color: white; margin: 5px 0 0 0; font-size: 0.9rem;"),
                style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); padding: 12px; border-radius: 6px; margin-top: 10px;"
            ),
            
            _class="task-panel"
        )
