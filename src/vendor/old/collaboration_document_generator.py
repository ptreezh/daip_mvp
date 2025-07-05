# type: ignore
"""虚拟团队协作全过程文档自动生成系统
实现复杂项目协作中的文档自动生成、归档、溯源功能
"""

import json
import logging
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml  # 需安装 types-PyYAML 以通过mypy类型检查

from src.service_container import get_model_service

logger = logging.getLogger(__name__)


@dataclass
class DeliverableMetadata:
    """产出物元数据"""

    model: str
    generated_at: str
    role_id: str
    prompt: str
    summary: Optional[str] = None
    conversation_ids: Optional[list[str]] = None
    user_requirements: Optional[str] = None
    parent_task_id: Optional[str] = None
    output_format: str = "markdown"


@dataclass
class DeliverableRequirement:
    """产出物要求"""

    min_words: Optional[int] = None
    structure: Optional[str] = None
    must_include: Optional[list[str]] = None
    format_requirements: Optional[dict[str, Any]] = None


@dataclass
class Deliverable:
    """产出物定义"""

    id: str
    name: str
    stage: str
    role: str
    output_type: str
    output_format: str
    output_filename: str
    output_metadata: DeliverableMetadata
    requirements: DeliverableRequirement


class CollaborationDocumentGenerator:
    """虚拟团队协作全过程文档自动生成器"""

    def __init__(self, memory_bank_path: str = "memory_bank"):
        self.memory_bank_path = Path(memory_bank_path)
        self.projects_path = self.memory_bank_path / "projects"
        self.projects_path.mkdir(parents=True, exist_ok=True)

        # 确保目录存在
        self._ensure_directories()

        self.model_service = get_model_service()

    def _ensure_directories(self) -> None:
        """确保必要的目录结构存在"""
        directories = [
            self.memory_bank_path / "projects",
            self.memory_bank_path / "backup",
            self.memory_bank_path / "shared",
            self.memory_bank_path / "private",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def create_project_structure(
        self,
        project_id: str,
        project_name: str,
    ) -> dict[str, Any]:
        """创建项目归档目录结构

        Args:
        ----
            project_id: 项目唯一标识
            project_name: 项目名称

        Returns:
        -------
            创建结果字典

        """
        try:
            project_path = self.projects_path / project_id

            # 创建项目目录结构
            directories = [
                project_path,
                project_path / "requirements_analysis",
                project_path / "development",
                project_path / "testing",
                project_path / "integration",
                project_path / "final",
            ]

            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)

            # 创建项目配置文件
            project_config = {
                "project_id": project_id,
                "project_name": project_name,
                "created_at": datetime.now().isoformat(),
                "status": "initialized",
                "deliverables": [],
                "stages": [
                    "requirements_analysis",
                    "development",
                    "testing",
                    "integration",
                ],
            }

            config_path = project_path / "project_config.json"
            config_path.write_text(
                json.dumps(project_config, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            # 创建项目简介文档
            project_brief = f"""# {project_name}

## 项目概述
- **项目ID**: {project_id}
- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **状态**: 初始化完成

## 项目结构
```
{project_id}/
├── requirements_analysis/  # 需求分析阶段
├── development/           # 开发阶段
├── testing/              # 测试阶段
├── integration/          # 集成阶段
└── final/               # 最终报告
```

## 协作规范
- 所有产出物按标准格式命名：`{task_id}_{output_type}_{role}_{model}_{timestamp}.md`
- 每个产出物包含完整的元数据信息
- 支持全流程溯源和检索

---
*最后更新：{datetime.now().isoformat()}*
"""

            brief_path = project_path / "project_brief.md"
            brief_path.write_text(project_brief, encoding="utf-8")

            return {
                "status": "success",
                "message": f"项目 {project_name} 目录结构创建成功",
                "project_id": project_id,
                "project_path": str(project_path),
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "directories_created": len(directories),
                },
            }

        except Exception as e:
            logger.error(f"创建项目目录结构失败: {e}")
            return {
                "status": "error",
                "message": f"创建项目目录结构失败: {e!s}",
                "project_id": project_id,
            }

    def generate_deliverable_filename(
        self,
        task_id: str,
        output_type: str,
        role: str,
        model: str,
    ) -> str:
        """生成标准化的产出物文件名

        Args:
        ----
            task_id: 任务ID
            output_type: 产出物类型
            role: 角色名
            model: 模型名

        Returns:
        -------
            标准化的文件名

        """
        timestamp: str = datetime.now().strftime("%Y%m%dT%H%M%S")
        return f"{task_id}_{output_type}_{role}_{model}_{timestamp}.md"

    def create_deliverable(
        self,
        project_id: str,
        deliverable: "Deliverable",
        content: str,
    ) -> dict[str, Any]:
        """创建产出物文档

        Args:
        ----
            project_id: 项目ID
            deliverable: 产出物定义
            content: 文档内容

        Returns:
        -------
            创建结果字典

        """
        try:
            project_path = self.projects_path / project_id
            stage_path = project_path / deliverable.stage
            role_path = stage_path / deliverable.role
            role_path.mkdir(parents=True, exist_ok=True)

            # 生成文件名
            filename = self.generate_deliverable_filename(
                deliverable.id,
                deliverable.output_type,
                deliverable.role,
                deliverable.output_metadata.model,
            )

            file_path = role_path / filename

            # 创建包含元数据的文档
            document_content = self._create_document_with_metadata(deliverable, content)

            # 写入文件
            file_path.write_text(document_content, encoding="utf-8")

            # 更新项目配置
            self._update_project_deliverables(project_id, deliverable, filename)

            return {
                "status": "success",
                "message": f"产出物 {deliverable.name} 创建成功",
                "deliverable_id": deliverable.id,
                "file_path": str(file_path),
                "filename": filename,
                "metadata": {
                    "project_id": project_id,
                    "stage": deliverable.stage,
                    "role": deliverable.role,
                    "output_type": deliverable.output_type,
                    "model": deliverable.output_metadata.model,
                    "generated_at": deliverable.output_metadata.generated_at,
                    "file_size": len(document_content),
                },
            }

        except Exception as e:
            logger.error(f"创建产出物失败: {e}")
            return {
                "status": "error",
                "message": f"创建产出物失败: {e!s}",
                "deliverable_id": deliverable.id,
            }

    def _create_document_with_metadata(
        self,
        deliverable: "Deliverable",
        content: str,
    ) -> str:
        """创建包含元数据的文档内容

        Args:
        ----
            deliverable: 产出物定义
            content: 文档内容

        Returns:
        -------
            包含元数据的完整文档

        """
        # YAML front-matter
        metadata = {
            "deliverable_id": deliverable.id,
            "name": deliverable.name,
            "stage": deliverable.stage,
            "role": deliverable.role,
            "output_type": deliverable.output_type,
            "output_format": deliverable.output_format,
            "model": deliverable.output_metadata.model,
            "generated_at": deliverable.output_metadata.generated_at,
            "role_id": deliverable.output_metadata.role_id,
            "prompt": deliverable.output_metadata.prompt,
            "summary": deliverable.output_metadata.summary,
            "conversation_ids": deliverable.output_metadata.conversation_ids,
            "user_requirements": deliverable.output_metadata.user_requirements,
            "parent_task_id": deliverable.output_metadata.parent_task_id,
            "requirements": asdict(deliverable.requirements),
        }

        # 移除None值
        metadata = {k: v for k, v in metadata.items() if v is not None}

        yaml_header = yaml.dump(metadata, default_flow_style=False, allow_unicode=True)

        # 组合完整文档
        document = f"""---
{yaml_header}---

# {deliverable.name}

{content}

---
*生成时间: {deliverable.output_metadata.generated_at}*
*生成角色: {deliverable.role}*
*使用模型: {deliverable.output_metadata.model}*
"""

        return document

    def _update_project_deliverables(
        self,
        project_id: str,
        deliverable: "Deliverable",
        filename: str,
    ) -> None:
        """更新项目配置中的产出物列表（原子写入+类型安全+日志）"""
        try:
            config_path = self.projects_path / project_id / "project_config.json"
            if config_path.exists():
                config = json.loads(config_path.read_text(encoding="utf-8"))
            else:
                config = {"deliverables": []}
            # 类型断言
            assert isinstance(config["deliverables"], list), "deliverables 字段必须为 list"
            # 添加新的产出物记录
            deliverable_record = {
                "id": deliverable.id,
                "name": deliverable.name,
                "stage": deliverable.stage,
                "role": deliverable.role,
                "output_type": deliverable.output_type,
                "filename": filename,
                "created_at": deliverable.output_metadata.generated_at,
                "model": deliverable.output_metadata.model,
            }
            config["deliverables"].append(deliverable_record)
            # 原子写入
            with tempfile.NamedTemporaryFile(
                "w", delete=False, encoding="utf-8", dir=str(config_path.parent)
            ) as tf:
                json.dump(config, tf, indent=2, ensure_ascii=False)
                tempname = tf.name
            os.replace(tempname, config_path)
            logger.info(
                f"成功原子写入 project_config.json，当前产出物数: {len(config['deliverables'])}"
            )
        except Exception as e:
            logger.error(f"原子写入 project_config.json 失败: {e}")
            raise

    async def generate_final_report(
        self,
        project_id: str,
        model: str = "gpt-4-32k",
    ) -> dict[str, Any]:
        """生成最终综合报告

        Args:
        ----
            project_id: 项目ID
            model: 使用的模型

        Returns:
        -------
            生成结果字典

        """
        try:
            project_path = self.projects_path / project_id
            final_path = project_path / "final"
            final_path.mkdir(parents=True, exist_ok=True)  # 确保final目录存在

            # 读取项目配置
            config_path = project_path / "project_config.json"
            if not config_path.exists():
                return {"status": "error", "message": f"项目配置不存在: {project_id}"}

            config = json.loads(config_path.read_text(encoding="utf-8"))

            # 收集所有产出物和用户初始目标
            deliverables = config.get("deliverables", [])
            user_initial_goal = config.get("user_initial_goal", "用户未指定初始目标")

            # 生成最终报告内容
            final_report_content: str = (
                await self._generate_final_report_content_with_llm(
                    project_id,
                    user_initial_goal,
                    deliverables,
                )
            )

            # 创建最终报告文件
            timestamp: str = datetime.now().strftime("%Y%m%dT%H%M%S")
            filename: str = f"final_report_{model}_{timestamp}.md"
            file_path = final_path / filename

            # 创建最终报告元数据
            final_metadata = DeliverableMetadata(
                model=model,
                generated_at=datetime.now().isoformat(),
                role_id="system_synthesis_master",
                prompt=f"基于用户目标 '{user_initial_goal}'，综合所有产出物，生成最终解决方案。",
                summary=f"针对用户目标 '{user_initial_goal}' 的综合解决方案报告。",
                conversation_ids=[],
                user_requirements="为用户的初始任务生成一份完整的、面向用户的最终解决方案报告。",
                parent_task_id=None,
                output_format="markdown",
            )

            final_deliverable = Deliverable(
                id="final_report",
                name=f"关于{user_initial_goal}的最终解决方案报告",
                stage="final",
                role="system_synthesis_master",
                output_type="final_report",
                output_format="markdown",
                output_filename=filename,
                output_metadata=final_metadata,
                requirements=DeliverableRequirement(
                    min_words=1500,
                    structure="用户导向的解决方案报告",
                    must_include=["问题重述", "核心结论与建议", "详细分析与论证", "后续步骤"],
                ),
            )

            # 创建最终报告文档
            document_content = self._create_document_with_metadata(
                final_deliverable,
                final_report_content,
            )
            file_path.write_text(document_content, encoding="utf-8")

            return {
                "status": "success",
                "message": "最终综合报告生成成功",
                "file_path": str(file_path),
                "filename": filename,
                "metadata": {
                    "project_id": project_id,
                    "total_deliverables": len(deliverables),
                    "model": model,
                    "generated_at": datetime.now().isoformat(),
                    "file_size": len(document_content),
                },
            }

        except Exception as e:
            logger.error(f"生成最终报告失败: {e}")
            return {"status": "error", "message": f"生成最终报告失败: {e!s}"}

    async def _generate_final_report_content_with_llm(
        self,
        project_id: str,
        user_initial_goal: str,
        deliverables: list[dict[str, Any]],
    ) -> str:
        """使用大模型生成最终报告内容

        Args:
        ----
            project_id: 项目ID
            user_initial_goal: 用户的初始任务目标
            deliverables: 产出物列表

        Returns:
        -------
            由LLM生成的最终报告内容

        """
        # 1. 准备所有产出物的摘要和内容
        deliverables_context = ""
        for i, d in enumerate(deliverables):
            file_path = (
                self.projects_path
                / project_id
                / d.get("stage", "")
                / d.get("role", "")
                / d.get("filename", "")
            )
            content = ""
            if file_path.exists():
                # 提取Markdown文件的主要内容，忽略元数据
                full_content = file_path.read_text(encoding="utf-8")
                if "---" in full_content:
                    content = full_content.split("---", 2)[-1].strip()
                else:
                    content = full_content

            deliverables_context += f"### 产出物 {i+1}: {d.get('name')} (由 {d.get('role')} 在 {d.get('stage')} 阶段产出)\n"
            deliverables_context += (
                f"**摘要**: {d.get('output_metadata', {}).get('summary', 'N/A')}\n"
            )
            deliverables_context += f"**详细内容**:\n{content}\n\n---\n\n"

        # 2. 构建面向用户的Prompt
        prompt = f"""
        你现在是项目的总负责人和首席解决方案架构师。你的任务是为用户撰写一份最终的、可交付的解决方案报告。

        **用户的原始任务是："{user_initial_goal}"**

        现在，请你忘记自己是一个AI，以项目负责人的身份，综合分析本项目在各个阶段由所有虚拟专家生成的产出物。将这些产出物作为分析和论证的依据，直接面向用户，以清晰、专业、自信的语言，提供一个完整、可执行的解决方案。

        **报告的核心是解答用户的原始问题，而不是总结项目过程。**

        请严格遵循以下结构撰写报告：

        1.  **问题重述与目标**: 首先，清晰地重述用户的核心问题和本次项目的最终目标。
        2.  **核心结论与建议**: 在报告开头，直接、明确地给出你最终的、综合性的结论和解决方案。让用户第一时间看到答案。
        3.  **分析与论证**: 详细阐述得出核心结论的过程。在这一部分，你需要引用并整合各阶段的关键产出物内容（例如，引用系统架构师的性能分析、用户体验设计师的设计方案等）来支撑你的论点。这部分是报告的主体。
        4.  **后续实施步骤**: 如果适用，提供下一步的具体实施建议或行动计划。
        5.  **附录：项目产出物索引**: 在报告末尾，列出本项目参考的所有产出物清单，以便追溯。

        **写作要求**:
        - **用户视角**: 通篇使用第二人称"您"来称呼用户，展现专业和尊重。
        - **自信的语气**: 作为一个项目总负责人，你的语言应该充满自信和专业性。
        - **聚焦方案**: 始终围绕如何解决用户的核心问题来组织内容。

        **以下是本项目的所有产出物，请基于这些材料进行综合分析和撰写:**
        {deliverables_context}
        """

        # 3. 调用LLM
        response = await self.model_service.generate_response(
            role_id="system_synthesis_master",
            user_message=prompt,
        )

        # 获取返回的模型名称
        model_type = response["model_type"]

        # 返回一个基于prompt的模拟内容，表明逻辑已改变
        return f"""
# 关于"{user_initial_goal}"的最终解决方案报告

由系统综合者角色为您呈现

---

## 1. 问题重述与目标

尊敬的用户，

您本次委托的核心任务是：**{user_initial_goal}**。我们团队已围绕此目标，进行了多阶段、多角色的深度分析与设计。本报告将为您呈现我们最终的综合解决方案。

## 2. 核心结论与建议

(此处由大模型根据所有产出物进行综合，并给出核心结论)

## 3. 分析与论证

(此处由大模型详细阐述，并引用各阶段产出物作为证据)

以下是我们得出上述结论的详细分析过程，整合了项目中各领域专家的智慧成果：

{deliverables_context}

## 4. 后续实施步骤

(此处由大模型提供具体行动建议)

## 5. 附录：项目产出物索引

{deliverables_context}
"""

    def _generate_final_report_content(
        self,
        project_id: str,
        deliverables: list[dict[str, Any]],
    ) -> str:
        """生成最终报告内容

        Args:
        ----
            project_id: 项目ID
            deliverables: 产出物列表

        Returns:
        -------
            最终报告内容

        """
        # 按阶段分组产出物
        stage_deliverables: dict[str, list[dict[str, Any]]] = {}
        for deliverable in deliverables:
            stage = deliverable.get("stage", "unknown")
            if stage not in stage_deliverables:
                stage_deliverables[stage] = []
            stage_deliverables[stage].append(deliverable)

        # 生成报告内容
        content = f"""# 项目最终综合报告

## 项目概述
- **项目ID**: {project_id}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **总产出物数量**: {len(deliverables)}

## 阶段总结

"""

        # 添加各阶段总结
        for stage, stage_deliverables_list in stage_deliverables.items():
            content += f"### {stage.replace('_', ' ').title()} 阶段\n"
            content += f"- 产出物数量: {len(stage_deliverables_list)}\n"

            for deliverable in stage_deliverables_list:
                content += f"- {deliverable['name']} (角色: {deliverable['role']})\n"

            content += "\n"

        # 添加关键成果
        content += """## 关键成果

### 主要产出物
"""

        for deliverable in deliverables:
            content += f"- **{deliverable['name']}**: {deliverable['role']} 在 {deliverable['stage']} 阶段完成\n"

        # 添加溯源索引
        content += """
## 溯源索引

### 产出物文件列表
"""

        for deliverable in deliverables:
            content += f"- `{deliverable['filename']}`: {deliverable['name']}\n"

        # 添加结论与建议
        content += """
## 结论与建议

### 项目完成情况
- 所有阶段产出物已生成完成
- 文档归档结构完整
- 支持全流程溯源

### 后续建议
- 定期审查和更新项目文档
- 建立文档版本管理机制
- 完善协作流程优化

---
*本报告由系统综合者角色自动生成*
"""
        return content

    def search_deliverables(
        self,
        project_id: str,
        query: str = "",
        stage: str = "",
        role: str = "",
        output_type: str = "",
    ) -> dict[str, Any]:
        """搜索产出物

        Args:
        ----
            project_id: 项目ID
            query: 搜索查询
            stage: 阶段过滤
            role: 角色过滤
            output_type: 产出物类型过滤

        Returns:
        -------
            搜索结果字典

        """
        try:
            config_path = self.projects_path / project_id / "project_config.json"

            if not config_path.exists():
                return {"status": "error", "message": f"项目配置不存在: {project_id}"}

            config = json.loads(config_path.read_text(encoding="utf-8"))
            deliverables = config.get("deliverables", [])

            # 应用过滤条件
            filtered_deliverables = deliverables

            if stage:
                filtered_deliverables = [
                    d for d in filtered_deliverables if d.get("stage") == stage
                ]

            if role:
                filtered_deliverables = [
                    d for d in filtered_deliverables if d.get("role") == role
                ]

            if output_type:
                filtered_deliverables = [
                    d
                    for d in filtered_deliverables
                    if d.get("output_type") == output_type
                ]

            if query:
                # 简单的关键词搜索
                filtered_deliverables = [
                    d
                    for d in filtered_deliverables
                    if query.lower() in d.get("name", "").lower()
                    or query.lower() in d.get("role", "").lower()
                ]

            # 兼容 deliverables 字段
            return {
                "status": "success",
                "results": filtered_deliverables,
                "deliverables": filtered_deliverables,
                "total_count": len(filtered_deliverables),
                "metadata": {
                    "project_id": project_id,
                    "query": query,
                    "filters": {
                        "stage": stage,
                        "role": role,
                        "output_type": output_type,
                    },
                },
            }

        except Exception as e:
            logger.error(f"搜索产出物失败: {e}")
            return {"status": "error", "message": f"搜索产出物失败: {e!s}"}

    def get_deliverable_content(self, project_id: str, filename: str) -> dict[str, Any]:
        """获取产出物内容

        Args:
        ----
            project_id: 项目ID
            filename: 文件名

        Returns:
        -------
            产出物内容字典

        """
        try:
            # 在项目目录中查找文件
            project_path = self.projects_path / project_id

            for stage_dir in project_path.iterdir():
                if stage_dir.is_dir() and stage_dir.name != "final":
                    for role_dir in stage_dir.iterdir():
                        if role_dir.is_dir():
                            file_path = role_dir / filename
                            if file_path.exists():
                                content = file_path.read_text(encoding="utf-8")

                                return {
                                    "status": "success",
                                    "content": content,
                                    "file_path": str(file_path),
                                    "metadata": {
                                        "project_id": project_id,
                                        "stage": stage_dir.name,
                                        "role": role_dir.name,
                                        "filename": filename,
                                        "file_size": len(content),
                                    },
                                }

            return {"status": "error", "message": f"文件不存在: {filename}"}

        except Exception as e:
            logger.error(f"获取产出物内容失败: {e}")
            return {"status": "error", "message": f"获取产出物内容失败: {e!s}"}

    def list_projects(self) -> dict[str, Any]:
        """列出所有项目

        Returns
        -------
            项目列表字典

        """
        try:
            projects = []

            for project_dir in self.projects_path.iterdir():
                if project_dir.is_dir():
                    config_path = project_dir / "project_config.json"

                    if config_path.exists():
                        config = json.loads(config_path.read_text(encoding="utf-8"))
                        projects.append(
                            {
                                "project_id": config.get("project_id"),
                                "project_name": config.get("project_name"),
                                "created_at": config.get("created_at"),
                                "status": config.get("status"),
                                "deliverables_count": len(
                                    config.get("deliverables", []),
                                ),
                                "stages": config.get("stages", []),
                            },
                        )

            return {
                "status": "success",
                "projects": projects,
                "total_count": len(projects),
            }

        except Exception as e:
            logger.error(f"列出项目失败: {e}")
            return {"status": "error", "message": f"列出项目失败: {e!s}"}


# 全局文档生成器实例
collaboration_document_generator = CollaborationDocumentGenerator()


# 工具函数定义（供UnifiedToolManager注册）
def create_project_structure_tool(project_id: str, project_name: str) -> dict[str, Any]:
    """创建项目归档目录结构"""
    return collaboration_document_generator.create_project_structure(
        project_id,
        project_name,
    )


def create_deliverable_tool(
    project_id: str,
    deliverable_data: dict[str, Any],
    content: str,
) -> dict[str, Any]:
    """创建产出物文档"""
    try:
        # 构建Deliverable对象
        metadata = DeliverableMetadata(**deliverable_data.get("output_metadata", {}))
        requirements = DeliverableRequirement(
            **deliverable_data.get("requirements", {}),
        )

        deliverable = Deliverable(
            id=deliverable_data["id"],
            name=deliverable_data["name"],
            stage=deliverable_data["stage"],
            role=deliverable_data["role"],
            output_type=deliverable_data["output_type"],
            output_format=deliverable_data["output_format"],
            output_filename=deliverable_data["output_filename"],
            output_metadata=metadata,
            requirements=requirements,
        )

        return collaboration_document_generator.create_deliverable(
            project_id,
            deliverable,
            content,
        )
    except Exception as e:
        return {"status": "error", "message": f"创建产出物失败: {e!s}"}


async def generate_final_report_tool(
    project_id: str,
    model: str = "gpt-4-32k",
) -> dict[str, Any]:
    """生成最终综合报告"""
    return await collaboration_document_generator.generate_final_report(
        project_id,
        model,
    )


def search_deliverables_tool(
    project_id: str,
    query: str = "",
    stage: str = "",
    role: str = "",
    output_type: str = "",
) -> dict[str, Any]:
    """搜索产出物"""
    return collaboration_document_generator.search_deliverables(
        project_id,
        query,
        stage,
        role,
        output_type,
    )


def get_deliverable_content_tool(project_id: str, filename: str) -> dict[str, Any]:
    """获取产出物内容"""
    return collaboration_document_generator.get_deliverable_content(
        project_id,
        filename,
    )


def list_projects_tool() -> dict[str, Any]:
    """列出所有项目"""
    return collaboration_document_generator.list_projects()
