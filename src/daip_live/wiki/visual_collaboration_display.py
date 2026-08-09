"""
可视化协作显示组件
提供实时协作过程的可视化展示
"""

import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class VisualEvent:
    """可视化事件"""

    timestamp: datetime
    event_type: str  # 'role_contribution', 'content_merge', 'analysis', 'progress'
    role_name: Optional[str]
    section: Optional[str]
    content: str
    metadata: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "role_name": self.role_name,
            "section": self.section,
            "content": self.content,
            "metadata": self.metadata or {},
        }


class VisualCollaborationDisplay:
    """可视化协作显示器"""

    def __init__(self, enable_logging: bool = True, log_path: Optional[Path] = None):
        self.events: list[VisualEvent] = []
        self.enable_logging = enable_logging
        self.log_path = log_path or Path("./wiki_collaboration_log.json")
        self.start_time = time.time()
        self.role_colors = {
            "Researcher_Agent": "cyan",
            "Writer_Agent": "green",
            "Fact_Checker_Agent": "red",
            "Editor_Agent": "blue",
            "domain_expert": "yellow",
            "researcher": "magenta",
            "editor": "blue",
            "critic": "red",
        }

    def log_event(
        self,
        event_type: str,
        role_name: Optional[str],
        section: Optional[str],
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """记录可视化事件"""
        event = VisualEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            role_name=role_name,
            section=section,
            content=content,
            metadata=metadata or {},
        )
        self.events.append(event)

        # 实时显示
        self._display_event(event)

        # 保存日志
        if self.enable_logging:
            self._save_log()

    def _display_event(self, event: VisualEvent):
        """显示事件到输出区"""
        time.time() - self.start_time

        if event.event_type == "role_contribution":
            self.role_colors.get(event.role_name, "white")
        elif event.event_type == "content_merge":
            pass
        elif event.event_type == "analysis":
            pass
        elif event.event_type == "progress":
            pass
        else:
            pass

    def _save_log(self):
        """保存日志到文件"""
        log_data = {
            "session_start": self.start_time,
            "events": [event.to_dict() for event in self.events],
        }

        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2, default=str)

    async def display_real_time_collaboration(
        self, collaborator, title: str, participants: list[str], total_rounds: int = 1
    ):
        """显示实时协作过程"""
        self.log_event("progress", None, "system", f"开始协作创建维基词条: {title}")

        # 启动协作会话
        await collaborator.start_collaboration(title, participants)

        for round_num in range(1, total_rounds + 1):
            self.log_event("progress", None, "system", f"开始第 {round_num} 轮协作编辑")

            # 运行一轮协作编辑
            contributions = await collaborator.run_collaborative_editing_round()

            for contribution in contributions:
                self.log_event(
                    "role_contribution",
                    contribution.contributor,
                    contribution.section,
                    contribution.content[:200] + "..."
                    if len(contribution.content) > 200
                    else contribution.content,
                    {
                        "contribution_type": contribution.contribution_type,
                        "timestamp": contribution.timestamp.isoformat(),
                    },
                )

            self.log_event("progress", None, "system", f"第 {round_num} 轮协作编辑完成")

        # 获取最终内容
        final_content = await collaborator.get_current_content()
        content_summary = f"共包含 {len(final_content)} 个部分"

        self.log_event("progress", None, "system", f"协作完成! {content_summary}")

        return final_content

    def get_detailed_log(self) -> str:
        """获取详细的协作日志"""
        log_lines = [f"协作会话日志 (共 {len(self.events)} 个事件)", "=" * 50]

        for event in self.events:
            log_lines.append(
                f"[{event.timestamp.strftime('%H:%M:%S')}] {event.event_type.upper()}"
            )
            if event.role_name:
                log_lines[-1] += f" - {event.role_name}"
            if event.section:
                log_lines[-1] += f" (部分: {event.section})"
            log_lines.append(
                f"  内容: {event.content[:100]}{'...' if len(event.content) > 100 else ''}"  # noqa: E501
            )
            log_lines.append("")

        return "\n".join(log_lines)

    def get_collaboration_summary(self) -> dict[str, Any]:
        """获取协作摘要"""
        if not self.events:
            return {"message": "暂无协作事件"}

        total_time = time.time() - self.start_time
        roles_involved = {event.role_name for event in self.events if event.role_name}
        sections_edited = {event.section for event in self.events if event.section}
        contribution_events = [
            e for e in self.events if e.event_type == "role_contribution"
        ]

        return {
            "total_time_seconds": total_time,
            "roles_involved": list(roles_involved),
            "sections_edited": list(sections_edited),
            "total_contributions": len(contribution_events),
            "total_events": len(self.events),
            "first_event_time": self.events[0].timestamp.isoformat(),
            "last_event_time": self.events[-1].timestamp.isoformat(),
        }


class EnhancedMultiRoleWikiCollaborator:
    """增强版多角色Wiki协作器，集成可视化显示"""

    def __init__(
        self,
        model_provider=None,
        visual_display: Optional[VisualCollaborationDisplay] = None,
    ):
        from .real_collaboration_engine import MultiRoleWikiCollaborator

        self.base_collaborator = MultiRoleWikiCollaborator(
            model_provider=model_provider
        )
        self.visual_display = visual_display or VisualCollaborationDisplay()
        self.content_history = []

    async def start_collaboration(
        self, title: str, participants: list[str], initial_content: str = ""
    ):
        """开始协作会话"""
        self.visual_display.log_event(
            "progress",
            None,
            "system",
            f"启动协作会话: '{title}'",
            {"participants": participants},
        )

        # 记录初始状态
        self.content_history.append(
            {
                "round": 0,
                "timestamp": datetime.now(),
                "content": {**self.base_collaborator.content},
            }
        )

        return await self.base_collaborator.start_collaboration(
            title, participants, initial_content
        )

    async def generate_content_with_role(
        self, role_name: str, section: str, current_content: str = ""
    ):
        """使用指定角色生成内容"""
        self.visual_display.log_event(
            "progress",
            role_name,
            section,
            f"角色 {role_name} 开始为 '{section}' 生成内容",
        )

        result = await self.base_collaborator.generate_content_with_role(
            role_name, section, current_content
        )

        self.visual_display.log_event(
            "role_contribution",
            role_name,
            section,
            f"角色 {role_name} 完成对 '{section}' 的贡献",
            {"content_length": len(result)},
        )

        return result

    async def run_collaborative_editing_round(self, sections_to_edit: list[str] = None):
        """运行一轮协作编辑"""
        self.visual_display.log_event(
            "progress",
            None,
            "system",
            "开始协作编辑轮次",
            {
                "sections": sections_to_edit
                or list(self.base_collaborator.content.keys())
            },
        )

        contributions = await self.base_collaborator.run_collaborative_editing_round(
            sections_to_edit
        )

        # 记录内容历史
        self.content_history.append(
            {
                "round": len(self.content_history),
                "timestamp": datetime.now(),
                "content": {**self.base_collaborator.content},
            }
        )

        self.visual_display.log_event(
            "progress",
            None,
            "system",
            f"协作编辑轮次完成，产生 {len(contributions)} 个贡献",
        )

        return contributions

    async def get_current_content(self):
        """获取当前内容"""
        content = await self.base_collaborator.get_current_content()
        return content

    async def save_wiki_content(self, save_path: str = None):
        """保存维基内容"""
        self.visual_display.log_event("progress", None, "system", "开始保存维基内容")

        result = await self.base_collaborator.save_wiki_content(save_path)

        self.visual_display.log_event(
            "progress", None, "system", f"维基内容已保存到: {result}"
        )

        return result

    async def end_collaboration(self):
        """结束协作"""
        result = await self.base_collaborator.end_collaboration()

        self.visual_display.log_event(
            "progress",
            None,
            "system",
            f"协作会话结束，总计 {result['total_contributions']} 个贡献",
        )

        return result

    def get_detailed_log(self) -> str:
        """获取详细日志"""
        return self.visual_display.get_detailed_log()

    def get_collaboration_summary(self) -> dict[str, Any]:
        """获取协作摘要"""
        return self.visual_display.get_collaboration_summary()

    def get_content_history(self) -> list[dict[str, Any]]:
        """获取内容变更历史"""
        return self.content_history


def create_visual_collaboration_system(model_provider=None):
    """创建可视化协作系统"""
    visual_display = VisualCollaborationDisplay()
    collaborator = EnhancedMultiRoleWikiCollaborator(
        model_provider=model_provider, visual_display=visual_display
    )
    return collaborator, visual_display
