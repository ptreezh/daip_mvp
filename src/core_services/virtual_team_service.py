# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-26 11:00:00
@Author  : DAIP-LIVE Team
@File    : virtual_team_service.py
@Description:
    Service for managing virtual team projects, tasks, and collaboration.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Optional

from src.memory_bank_tools import MemoryBankTools
from src.models.virtual_team import (
    ProjectStatus,
    RoleContext,
    TaskStatus,
    VirtualProject,
    VirtualTask,
)
from src.core_services.expert_service import ExpertService

logger = logging.getLogger(__name__)


class VirtualTeamService:
    """虚拟团队项目协作引擎"""

    def __init__(self, expert_library: ExpertService, memory_tools: MemoryBankTools):
        self.memory_tools = memory_tools
        self.expert_library = expert_library

        # 项目存储
        self.projects: dict[str, VirtualProject] = {}
        self.tasks: dict[str, VirtualTask] = {}
        self.role_contexts: dict[str, RoleContext] = {}

        # 核心文件列表
        self.core_files = [
            "project_brief.md",
            "system_architecture.md",
            "development_progress.md",
            "quality_metrics.md",
            "user_experience.md",
            "documentation_status.md",
            "task_assignments.md",
            "collaboration_log.md",
        ]

        logger.info("VirtualTeamService initialized")

    async def create_project(
        self,
        name: str,
        description: str,
        creator: str,
        initial_roles: Optional[list[str]] = None,
        config: Optional[dict[str, Any]] = None,
    ) -> str:
        """创建虚拟团队项目"""
        try:
            project_id = f"proj_{uuid.uuid4().hex[:8]}"
            timestamp = datetime.now().isoformat()

            # 创建项目
            project = VirtualProject(
                project_id=project_id,
                name=name,
                description=description,
                status=ProjectStatus.CREATED,
                created_at=timestamp,
                updated_at=timestamp,
                creator=creator,
                assigned_roles=initial_roles or [],
                memory_bank_path=f"memory_bank/projects/{project_id}",
                config=config or {},
            )

            self.projects[project_id] = project

            # 初始化记忆银行
            await self._initialize_project_memory_bank(project_id)

            # 分配初始角色
            if initial_roles:
                for role_id in initial_roles:
                    await self._assign_role_to_project(project_id, role_id)

            logger.info(f"Created virtual team project: {project_id} - {name}")
            return project_id

        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise

    async def _initialize_project_memory_bank(self, project_id: str):
        """初始化项目记忆银行"""
        try:
            project = self.projects[project_id]

            # 创建项目简介
            project_brief = f"""# 项目简介

## 项目信息
- **项目ID**: {project_id}
- **项目名称**: {project.name}
- **项目描述**: {project.description}
- **创建时间**: {project.created_at}
- **创建者**: {project.creator}
- **状态**: {project.status.value}

## 项目目标
{project.description}

## 团队角色
{chr(