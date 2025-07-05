"""虚拟团队项目协作引擎
基于记忆银行的AI角色协作系统
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from src.constants import (
    EXECUTION_STATUS_COMPLETED,
    TASK_STATUS_PENDING,
)
from src.expert_library import ExpertLibrary
from src.memory_bank_tools import MemoryBankTools

logger = logging.getLogger(__name__)


class ProjectStatus(Enum):
    """项目状态枚举"""

    CREATED = "created"
    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    """任务状态枚举"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_REVIEW = "waiting_review"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


@dataclass
class VirtualProject:
    """虚拟项目数据结构"""

    project_id: str
    name: str
    description: str
    status: ProjectStatus
    created_at: str
    updated_at: str
    creator: str
    assigned_roles: list[str]
    memory_bank_path: str
    config: dict[str, Any]


@dataclass
class VirtualTask:
    """虚拟任务数据结构"""

    task_id: str
    project_id: str
    title: str
    description: str
    assigned_role: str
    status: TaskStatus
    priority: int
    created_at: str
    updated_at: str
    due_date: Optional[str]
    dependencies: list[str]
    progress: int = 0


@dataclass
class RoleContext:
    """角色上下文数据结构"""

    role_id: str
    role_name: str
    role_data: dict[str, Any]
    current_task: Optional[str]
    memory_context: dict[str, Any]
    last_activity: str


class VirtualTeamProjectEngine:
    """虚拟团队项目协作引擎"""

    def __init__(self, memory_tools: MemoryBankTools, expert_library: ExpertLibrary):
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

        logger.info("虚拟团队项目引擎初始化完成")

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

            logger.info(f"创建虚拟团队项目: {project_id} - {name}")
            return project_id

        except Exception as e:
            logger.error(f"创建项目失败: {e}")
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
{chr(10).join([f"- {role_id}" for role_id in project.assigned_roles])}

## 项目配置
```json
{json.dumps(project.config, indent=2, ensure_ascii=False)}
```

---
*最后更新: {datetime.now().isoformat()}*
"""

            # 写入核心文件
            await self._write_shared_memory(
                project_id,
                "project_brief.md",
                project_brief,
            )
            await self._write_shared_memory(
                project_id,
                "task_assignments.md",
                "# 任务分配\n\n## 待分配任务\n\n## 进行中任务\n\n## 已完成任务\n",
            )
            await self._write_shared_memory(
                project_id,
                "collaboration_log.md",
                "# 协作日志\n\n## 项目启动\n\n项目已创建并初始化记忆银行。\n",
            )

            logger.info(f"项目 {project_id} 记忆银行初始化完成")

        except Exception as e:
            logger.error(f"初始化项目记忆银行失败: {e}")
            raise

    async def assign_role(self, project_id: str, role_id: str) -> bool:
        """为项目分配AI角色"""
        try:
            if project_id not in self.projects:
                raise ValueError(f"项目不存在: {project_id}")

            # 检查角色是否存在
            expert = self.expert_library.get_expert_by_id(role_id)
            if not expert:
                raise ValueError(f"角色不存在: {role_id}")

            project = self.projects[project_id]

            # 添加角色到项目
            if role_id not in project.assigned_roles:
                project.assigned_roles.append(role_id)
                project.updated_at = datetime.now().isoformat()

            # 创建角色上下文
            role_context = RoleContext(
                role_id=role_id,
                role_name=expert.get("name", role_id),
                role_data=expert,
                current_task=None,
                memory_context={},
                last_activity=datetime.now().isoformat(),
            )

            self.role_contexts[f"{project_id}_{role_id}"] = role_context

            # 更新协作日志
            await self._update_collaboration_log(
                project_id,
                f"角色 {expert.get('name', role_id)} 已分配到项目",
            )

            logger.info(f"角色 {role_id} 已分配到项目 {project_id}")
            return True

        except Exception as e:
            logger.error(f"分配角色失败: {e}")
            return False

    async def create_task(
        self,
        project_id: str,
        title: str,
        description: str,
        assigned_role: str,
        priority: int = 5,
        dependencies: Optional[list[str]] = None,
    ) -> str:
        """创建项目任务"""
        try:
            if project_id not in self.projects:
                raise ValueError(f"项目不存在: {project_id}")

            task_id = f"task_{uuid.uuid4().hex[:8]}"
            timestamp = datetime.now().isoformat()

            task = VirtualTask(
                task_id=task_id,
                project_id=project_id,
                title=title,
                description=description,
                assigned_role=assigned_role,
                status=TaskStatus.PENDING,
                priority=priority,
                created_at=timestamp,
                updated_at=timestamp,
                due_date=None,
                dependencies=dependencies or [],
            )

            self.tasks[task_id] = task

            # 更新任务分配文档
            await self._update_task_assignments(project_id)

            # 更新协作日志
            await self._update_collaboration_log(
                project_id,
                f"创建任务: {title} (分配给 {assigned_role})",
            )

            logger.info(f"创建任务: {task_id} - {title}")
            return task_id

        except Exception as e:
            logger.error(f"创建任务失败: {e}")
            raise

    async def execute_task(self, task_id: str) -> dict[str, Any]:
        """执行任务"""
        try:
            if task_id not in self.tasks:
                raise ValueError(f"任务不存在: {task_id}")

            task = self.tasks[task_id]
            project_id = task.project_id

            # 检查任务状态
            if task.status.value != TASK_STATUS_PENDING:
                raise ValueError(f"任务状态不允许执行: {task.status}")

            # 更新任务状态
            task.status = TaskStatus.IN_PROGRESS
            task.updated_at = datetime.now().isoformat()

            # 获取角色上下文
            role_context_key = f"{project_id}_{task.assigned_role}"
            if role_context_key not in self.role_contexts:
                raise ValueError(f"角色上下文不存在: {task.assigned_role}")

            role_context = self.role_contexts[role_context_key]
            role_context.current_task = task_id
            role_context.last_activity = datetime.now().isoformat()

            # 加载记忆银行上下文
            await self._load_role_memory_context(project_id, task.assigned_role)

            # 生成任务执行提示
            prompt = await self._generate_task_execution_prompt(task, role_context)

            # 模拟LLM响应（实际应调用llm.py）
            response = f"任务执行完成: {task.title}\n\n基于角色 {role_context.role_name} 的专业知识，已完成任务分析和执行。\n\n{prompt[:200]}..."

            # 更新记忆银行
            await self._update_role_memory(
                project_id,
                task.assigned_role,
                task_id,
                response,
            )

            # 更新任务进度
            task.progress = 100
            task.status = TaskStatus.COMPLETED
            task.updated_at = datetime.now().isoformat()

            # 更新任务分配文档
            await self._update_task_assignments(project_id)

            # 更新协作日志
            await self._update_collaboration_log(project_id, f"任务完成: {task.title}")

            logger.info(f"任务执行完成: {task_id}")

            return {
                "task_id": task_id,
                "status": EXECUTION_STATUS_COMPLETED,
                "response": response,
                "role": task.assigned_role,
                "completion_time": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"执行任务失败: {e}")
            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.BLOCKED
            raise

    async def _generate_task_execution_prompt(
        self,
        task: VirtualTask,
        role_context: RoleContext,
    ) -> str:
        """生成任务执行提示"""
        # 获取项目上下文
        project = self.projects[task.project_id]

        # 获取相关记忆银行内容
        project_brief = await self._read_shared_memory(
            task.project_id,
            "project_brief.md",
        )
        collaboration_log = await self._read_shared_memory(
            task.project_id,
            "collaboration_log.md",
        )

        prompt = f"""# 任务执行指令

## 角色信息
- **角色名称**: {role_context.role_name}
- **角色描述**: {role_context.role_data.get('description', '')}
- **专业领域**: {', '.join(role_context.role_data.get('specialties', []))}

## 项目上下文
- **项目名称**: {project.name}
- **项目描述**: {project.description}

## 当前任务
- **任务标题**: {task.title}
- **任务描述**: {task.description}
- **优先级**: {task.priority}
- **依赖任务**: {', '.join(task.dependencies) if task.dependencies else '无'}

## 项目背景
{project_brief.get('content', '')}

## 协作历史
{collaboration_log.get('content', '')}

## 执行要求
1. 基于你的专业知识和角色定位，分析并执行上述任务
2. 考虑项目的整体目标和约束条件
3. 提供详细的分析、建议或解决方案
4. 更新相关的记忆银行文件
5. 记录重要的决策和进展

请开始执行任务...
"""
        return prompt

    async def _load_role_memory_context(self, project_id: str, role_id: str):
        """加载角色记忆上下文"""
        try:
            role_context_key = f"{project_id}_{role_id}"
            if role_context_key not in self.role_contexts:
                return

            role_context = self.role_contexts[role_context_key]

            # 加载共享记忆
            shared_memories = {}
            for filename in self.core_files:
                memory = await self._read_shared_memory(project_id, filename)
                if memory.get("status") == "success":
                    shared_memories[filename] = memory.get("content", "")

            # 加载私有记忆
            private_memories = {}
            private_files = await self._list_private_memory_files(project_id, role_id)
            if private_files.get("status") == "success":
                for filename in private_files.get("files", []):
                    memory = await self._read_private_memory(
                        project_id,
                        role_id,
                        filename,
                    )
                    if memory.get("status") == "success":
                        private_memories[filename] = memory.get("content", "")

            role_context.memory_context = {
                "shared": shared_memories,
                "private": private_memories,
            }

        except Exception as e:
            logger.error(f"加载角色记忆上下文失败: {e}")

    async def _update_role_memory(
        self,
        project_id: str,
        role_id: str,
        task_id: str,
        response: str,
    ):
        """更新角色记忆"""
        try:
            task = self.tasks[task_id]

            # 更新协作日志
            log_entry = f"""
## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 任务执行结果

**任务**: {task.title}
**执行角色**: {role_id}
**状态**: 已完成

### 执行结果
{response}

---
"""
            await self._append_to_shared_memory(
                project_id,
                "collaboration_log.md",
                log_entry,
            )

            # 更新角色私有记忆
            private_content = f"""# 任务执行记录

## 任务信息
- **任务ID**: {task_id}
- **任务标题**: {task.title}
- **执行时间**: {datetime.now().isoformat()}

## 执行结果
{response}

## 关键决策
- 基于任务要求进行了分析和执行
- 更新了项目协作日志
- 记录了执行过程和结果

---
*最后更新: {datetime.now().isoformat()}*
"""
            await self._write_private_memory(
                project_id,
                role_id,
                f"task_{task_id}_result.md",
                private_content,
            )

        except Exception as e:
            logger.error(f"更新角色记忆失败: {e}")

    async def get_project_status(self, project_id: str) -> dict[str, Any]:
        """获取项目状态"""
        try:
            if project_id not in self.projects:
                raise ValueError(f"项目不存在: {project_id}")

            project = self.projects[project_id]

            # 获取项目任务
            project_tasks = [
                task for task in self.tasks.values() if task.project_id == project_id
            ]

            # 统计任务状态
            task_stats = {
                "total": len(project_tasks),
                "pending": len(
                    [t for t in project_tasks if t.status == TaskStatus.PENDING],
                ),
                "in_progress": len(
                    [t for t in project_tasks if t.status == TaskStatus.IN_PROGRESS],
                ),
                "completed": len(
                    [t for t in project_tasks if t.status == TaskStatus.COMPLETED],
                ),
                "blocked": len(
                    [t for t in project_tasks if t.status == TaskStatus.BLOCKED],
                ),
            }

            # 计算总体进度
            total_progress = 0
            if project_tasks:
                total_progress = sum(task.progress for task in project_tasks) / len(
                    project_tasks,
                )

            return {
                "project": asdict(project),
                "task_statistics": task_stats,
                "overall_progress": round(total_progress, 2),
                "active_roles": len(project.assigned_roles),
                "last_activity": project.updated_at,
            }

        except Exception as e:
            logger.error(f"获取项目状态失败: {e}")
            raise

    async def get_memory_bank_content(
        self,
        project_id: str,
        filename: Optional[str] = None,
    ) -> dict[str, Any]:
        """获取记忆银行内容"""
        try:
            if project_id not in self.projects:
                raise ValueError(f"项目不存在: {project_id}")

            if filename:
                # 获取特定文件
                return await self._read_shared_memory(project_id, filename)
            else:
                # 获取所有核心文件
                memory_content = {}
                for core_file in self.core_files:
                    memory = await self._read_shared_memory(project_id, core_file)
                    if memory.get("status") == "success":
                        memory_content[core_file] = memory.get("content", "")

                return {
                    "status": "success",
                    "content": memory_content,
                    "files": list(memory_content.keys()),
                }

        except Exception as e:
            logger.error(f"获取记忆银行内容失败: {e}")
            raise

    # 记忆银行操作辅助方法
    async def _read_shared_memory(
        self,
        project_id: str,
        filename: str,
    ) -> dict[str, Any]:
        """读取共享记忆"""
        return self.memory_tools.get_shared_memory(filename)

    async def _write_shared_memory(
        self,
        project_id: str,
        filename: str,
        content: str,
    ) -> dict[str, Any]:
        """写入共享记忆"""
        return self.memory_tools.set_shared_memory(filename, content)

    async def _append_to_shared_memory(
        self,
        project_id: str,
        filename: str,
        content: str,
    ) -> dict[str, Any]:
        """追加到共享记忆"""
        current = await self._read_shared_memory(project_id, filename)
        if current.get("status") == "success":
            new_content = current.get("content", "") + content
            return await self._write_shared_memory(project_id, filename, new_content)
        else:
            return await self._write_shared_memory(project_id, filename, content)

    async def _read_private_memory(
        self,
        project_id: str,
        role_id: str,
        filename: str,
    ) -> dict[str, Any]:
        """读取私有记忆"""
        return self.memory_tools.get_private_memory(role_id, filename)

    async def _write_private_memory(
        self,
        project_id: str,
        role_id: str,
        filename: str,
        content: str,
    ) -> dict[str, Any]:
        """写入私有记忆"""
        return self.memory_tools.set_private_memory(role_id, filename, content)

    async def _list_private_memory_files(
        self,
        project_id: str,
        role_id: str,
    ) -> dict[str, Any]:
        """列出私有记忆文件"""
        result = self.memory_tools.list_memory_files(role_id)
        return result

    async def _update_task_assignments(self, project_id: str):
        """更新任务分配文档"""
        try:
            project_tasks = [
                task for task in self.tasks.values() if task.project_id == project_id
            ]

            content = "# 任务分配\n\n"

            # 按状态分组
            status_groups = {
                TaskStatus.PENDING: "待分配任务",
                TaskStatus.IN_PROGRESS: "进行中任务",
                TaskStatus.WAITING_REVIEW: "等待审核任务",
                TaskStatus.COMPLETED: "已完成任务",
                TaskStatus.BLOCKED: "阻塞任务",
            }

            for status, title in status_groups.items():
                tasks_in_status = [t for t in project_tasks if t.status == status]
                if tasks_in_status:
                    content += f"## {title}\n\n"
                    for task in tasks_in_status:
                        content += f"### {task.title}\n"
                        content += f"- **任务ID**: {task.task_id}\n"
                        content += f"- **描述**: {task.description}\n"
                        content += f"- **分配角色**: {task.assigned_role}\n"
                        content += f"- **优先级**: {task.priority}\n"
                        content += f"- **进度**: {task.progress}%\n"
                        content += f"- **创建时间**: {task.created_at}\n"
                        if task.dependencies:
                            content += f"- **依赖**: {', '.join(task.dependencies)}\n"
                        content += "\n"

            await self._write_shared_memory(project_id, "task_assignments.md", content)

        except Exception as e:
            logger.error(f"更新任务分配文档失败: {e}")

    async def _update_collaboration_log(self, project_id: str, message: str):
        """更新协作日志"""
        try:
            log_entry = (
                f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{message}\n"
            )
            await self._append_to_shared_memory(
                project_id,
                "collaboration_log.md",
                log_entry,
            )
        except Exception as e:
            logger.error(f"更新协作日志失败: {e}")

    async def _assign_role_to_project(self, project_id: str, role_id: str):
        """内部方法：分配角色到项目"""
        return await self.assign_role(project_id, role_id)
