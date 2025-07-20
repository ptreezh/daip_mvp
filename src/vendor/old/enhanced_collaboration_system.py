"""增强型虚拟团队协作系统
集成文档自动生成、归档、溯源功能
严格遵循全局规则和规范
"""

import json
import logging
import shutil
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from src.adapter import dict_to_deliverable
from src.collaboration_document_generator import CollaborationDocumentGenerator
from src.memory_bank_manager import MemoryBankManager

logger = logging.getLogger(__name__)


@dataclass
class WorkflowMetadata:
    """工作流元数据"""

    workflow_id: str
    name: str
    description: str
    version: str
    created_at: str
    updated_at: str
    status: str
    stages: list[str]
    roles: list[str]
    deliverables_count: int
    archive_path: str


@dataclass
class DocumentTrace:
    """文档溯源信息"""

    document_id: str
    filename: str
    workflow_id: str
    stage: str
    role: str
    created_at: str
    updated_at: str
    parent_documents: list[str]
    child_documents: list[str]
    metadata: dict[str, Any]
    archive_path: str


class EnhancedCollaborationSystem:
    """增强型虚拟团队协作系统"""

    def __init__(self, base_path: str = "memory_bank"):
        self.base_path = Path(base_path)
        self.workflows_path = self.base_path / "workflows"
        self.archive_path = self.base_path / "archive"
        self.traces_path = self.base_path / "traces"

        # 初始化子系统
        self.document_generator = CollaborationDocumentGenerator(str(self.base_path))
        self.memory_manager = MemoryBankManager(str(self.base_path))

        # 确保目录结构
        self._ensure_directories()

        logger.info(f"增强型协作系统初始化完成: {self.base_path}")

    def _ensure_directories(self):
        """确保必要的目录结构存在"""
        directories = [
            self.workflows_path,
            self.archive_path,
            self.traces_path,
            self.archive_path / "workflows",
            self.archive_path / "deliverables",
            self.archive_path / "reports",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def create_workflow(
        self,
        workflow_id: str,
        workflow_config: dict[str, Any],
    ) -> dict[str, Any]:
        """创建工作流

        Args:
        ----
            workflow_id: 工作流ID
            workflow_config: 工作流配置

        Returns:
        -------
            创建结果

        """
        try:
            workflow_path = self.workflows_path / workflow_id
            workflow_path.mkdir(parents=True, exist_ok=True)

            # 创建工作流元数据
            metadata = WorkflowMetadata(
                workflow_id=workflow_id,
                name=workflow_config.get("name", ""),
                description=workflow_config.get("description", ""),
                version=workflow_config.get("version", "1.0.0"),
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                status="active",
                stages=workflow_config.get("stages", []),
                roles=workflow_config.get("roles", []),
                deliverables_count=0,
                archive_path=str(self.archive_path / "workflows" / workflow_id),
            )

            # 保存工作流配置
            config_path = workflow_path / "workflow_config.json"
            config_path.write_text(
                json.dumps(workflow_config, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            # 保存元数据
            metadata_path = workflow_path / "metadata.json"
            metadata_path.write_text(
                json.dumps(asdict(metadata), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            # 创建工作流目录结构
            for stage in workflow_config.get("stages", []):
                stage_path = workflow_path / stage
                stage_path.mkdir(exist_ok=True)

            return {
                "status": "success",
                "message": f"工作流 {workflow_id} 创建成功",
                "workflow_id": workflow_id,
                "metadata": asdict(metadata),
            }

        except Exception as e:
            logger.error(f"创建工作流失败: {e}")
            return {
                "status": "error",
                "message": f"创建工作流失败: {e!s}",
                "workflow_id": workflow_id,
            }

    def create_deliverable(
        self,
        workflow_id: str,
        deliverable_data: dict[str, Any],
        content: str,
    ) -> dict[str, Any]:
        """创建产出物文档

        Args:
        ----
            workflow_id: 工作流ID
            deliverable_data: 产出物数据
            content: 文档内容

        Returns:
        -------
            创建结果

        """
        try:
            # 通过适配器将dict转换为Deliverable实例
            deliverable = dict_to_deliverable(deliverable_data)
            result = self.document_generator.create_deliverable(
                project_id=workflow_id,
                deliverable=deliverable,
                content=content,
            )

            if result["status"] == "success":
                # 创建文档溯源记录
                document_id = str(uuid.uuid4())
                trace = DocumentTrace(
                    document_id=document_id,
                    filename=result.get("filename", ""),
                    workflow_id=workflow_id,
                    stage=deliverable_data.get("stage", ""),
                    role=deliverable_data.get("role", ""),
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat(),
                    parent_documents=deliverable_data.get("parent_documents", []),
                    child_documents=[],
                    metadata=deliverable_data.get("output_metadata", {}),
                    archive_path=str(self.archive_path / "deliverables" / workflow_id),
                )

                # 保存溯源信息
                trace_path = self.traces_path / f"{document_id}.json"
                trace_path.write_text(
                    json.dumps(asdict(trace), indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )

                # 更新工作流元数据
                self._update_workflow_metadata(workflow_id, "deliverables_count", 1)

                result["document_id"] = document_id
                result["trace"] = asdict(trace)

            return result

        except Exception as e:
            logger.error(f"创建产出物失败: {e}")
            return {"status": "error", "message": f"创建产出物失败: {e!s}"}

    async def generate_final_report(
        self,
        workflow_id: str,
        model: str = "gpt-4-32k",
    ) -> dict[str, Any]:
        """生成最终综合报告

        Args:
        ----
            workflow_id: 工作流ID
            model: 使用的模型

        Returns:
        -------
            生成结果

        """
        try:
            # 使用文档生成器生成最终报告
            result = await self.document_generator.generate_final_report(
                workflow_id,
                model,
            )

            if result["status"] == "success":
                # 归档最终报告
                report_filename = result.get("filename", "")
                if report_filename:
                    source_path = (
                        self.document_generator.projects_path
                        / workflow_id
                        / "final"
                        / report_filename
                    )
                    archive_path = (
                        self.archive_path / "reports" / workflow_id / report_filename
                    )
                    archive_path.parent.mkdir(parents=True, exist_ok=True)

                    if source_path.exists():
                        shutil.copy2(source_path, archive_path)

                        # 创建报告溯源记录
                        report_id = str(uuid.uuid4())
                        trace = DocumentTrace(
                            document_id=report_id,
                            filename=report_filename,
                            workflow_id=workflow_id,
                            stage="final",
                            role="system_synthesis_master_001",
                            created_at=datetime.now().isoformat(),
                            updated_at=datetime.now().isoformat(),
                            parent_documents=[],
                            child_documents=[],
                            metadata={
                                "type": "final_report",
                                "model": model,
                                "generated_at": datetime.now().isoformat(),
                            },
                            archive_path=str(archive_path.parent),
                        )

                        # 保存溯源信息
                        trace_path = self.traces_path / f"{report_id}.json"
                        trace_path.write_text(
                            json.dumps(asdict(trace), indent=2, ensure_ascii=False),
                            encoding="utf-8",
                        )

                        result["report_id"] = report_id
                        result["archive_path"] = str(archive_path)

            return result

        except Exception as e:
            logger.error(f"生成最终报告失败: {e}")
            return {"status": "error", "message": f"生成最终报告失败: {e!s}"}

    def search_documents(
        self,
        workflow_id: str,
        query: str = "",
        filters: dict[str, Any] = {},
    ) -> dict[str, Any]:
        """搜索文档

        Args:
        ----
            workflow_id: 工作流ID
            query: 搜索查询
            filters: 过滤条件

        Returns:
        -------
            搜索结果

        """
        try:
            # 使用文档生成器搜索产出物
            result = self.document_generator.search_deliverables(
                project_id=workflow_id,
                query=query,
                stage=filters.get("stage", "") if filters else "",
                role=filters.get("role", "") if filters else "",
                output_type=filters.get("output_type", "") if filters else "",
            )
            # 兼容results/deliverables字段
            deliverables = result.get("deliverables")
            if deliverables is None:
                deliverables = result.get("results", [])
                result["deliverables"] = deliverables
            # 添加溯源信息
            if result["status"] == "success" and deliverables:
                for deliverable in deliverables:
                    filename = deliverable.get("filename", "")
                    if filename:
                        # 查找对应的溯源记录
                        trace_info = self._find_document_trace(workflow_id, filename)
                        if trace_info:
                            deliverable["trace"] = trace_info
            return result

        except Exception as e:
            logger.error(f"搜索文档失败: {e}")
            return {"status": "error", "message": f"搜索文档失败: {e!s}"}

    def trace_document(self, document_id: str) -> dict[str, Any]:
        """追踪文档

        Args:
        ----
            document_id: 文档ID

        Returns:
        -------
            追踪结果

        """
        try:
            trace_path = self.traces_path / f"{document_id}.json"
            if not trace_path.exists():
                return {"status": "error", "message": f"文档溯源记录不存在: {document_id}"}

            trace_data = json.loads(trace_path.read_text(encoding="utf-8"))

            # 获取文档内容
            content_result = self.document_generator.get_deliverable_content(
                project_id=trace_data["workflow_id"],
                filename=trace_data["filename"],
            )

            if content_result["status"] == "success":
                trace_data["content"] = content_result.get("content", "")

            return {"status": "success", "trace": trace_data}

        except Exception as e:
            logger.error(f"追踪文档失败: {e}")
            return {"status": "error", "message": f"追踪文档失败: {e!s}"}

    def archive_workflow(
        self,
        workflow_id: str,
        archive_reason: str = "",
    ) -> dict[str, Any]:
        """归档工作流

        Args:
        ----
            workflow_id: 工作流ID
            archive_reason: 归档原因

        Returns:
        -------
            归档结果

        """
        try:
            workflow_path = self.workflows_path / workflow_id
            if not workflow_path.exists():
                return {"status": "error", "message": f"工作流不存在: {workflow_id}"}

            # 创建归档目录
            archive_workflow_path = self.archive_path / "workflows" / workflow_id
            archive_workflow_path.mkdir(parents=True, exist_ok=True)

            # 复制工作流文件到归档目录
            shutil.copytree(workflow_path, archive_workflow_path, dirs_exist_ok=True)

            # 更新工作流状态
            metadata_path = workflow_path / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                metadata["status"] = "archived"
                metadata["archived_at"] = datetime.now().isoformat()
                metadata["archive_reason"] = archive_reason
                metadata["archive_path"] = str(archive_workflow_path)

                metadata_path.write_text(
                    json.dumps(metadata, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )

            return {
                "status": "success",
                "message": f"工作流 {workflow_id} 归档成功",
                "archive_path": str(archive_workflow_path),
            }

        except Exception as e:
            logger.error(f"归档工作流失败: {e}")
            return {"status": "error", "message": f"归档工作流失败: {e!s}"}

    def validate_workflow(self, workflow_id: str) -> dict[str, Any]:
        """验证工作流

        Args:
        ----
            workflow_id: 工作流ID

        Returns:
        -------
            验证结果

        """
        try:
            workflow_path = self.workflows_path / workflow_id
            if not workflow_path.exists():
                return {"status": "error", "message": f"工作流不存在: {workflow_id}"}

            validation_result = {
                "workflow_id": workflow_id,
                "status": "valid",
                "issues": [],
                "warnings": [],
                "metadata": {},
                "deliverables": [],
                "traces": [],
            }

            # 验证工作流配置
            config_path = workflow_path / "workflow_config.json"
            if config_path.exists():
                config = json.loads(config_path.read_text(encoding="utf-8"))
                validation_result["metadata"]["config"] = config

                # 检查必需字段
                required_fields = ["name", "description", "stages", "roles"]
                for field in required_fields:
                    if field not in config:
                        validation_result["issues"].append(f"缺少必需字段: {field}")
                        validation_result["status"] = "invalid"
            else:
                validation_result["issues"].append("工作流配置文件不存在")
                validation_result["status"] = "invalid"

            # 验证产出物
            deliverables = self.document_generator.search_deliverables(workflow_id)
            if deliverables["status"] == "success":
                validation_result["deliverables"] = deliverables.get("deliverables", [])

            # 验证溯源记录
            traces = self._get_workflow_traces(workflow_id)
            validation_result["traces"] = traces

            return validation_result

        except Exception as e:
            logger.error(f"验证工作流失败: {e}")
            return {"status": "error", "message": f"验证工作流失败: {e!s}"}

    def get_workflow_summary(self, workflow_id: str) -> dict[str, Any]:
        """获取工作流摘要

        Args:
        ----
            workflow_id: 工作流ID

        Returns:
        -------
            工作流摘要

        """
        try:
            workflow_path = self.workflows_path / workflow_id
            if not workflow_path.exists():
                return {"status": "error", "message": f"工作流不存在: {workflow_id}"}

            # 获取工作流元数据
            metadata_path = workflow_path / "metadata.json"
            metadata = {}
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

            # 获取产出物统计
            deliverables = self.document_generator.search_deliverables(workflow_id)
            deliverables_count = (
                len(deliverables.get("deliverables", []))
                if deliverables["status"] == "success"
                else 0
            )

            # 获取溯源记录统计
            traces = self._get_workflow_traces(workflow_id)
            traces_count = len(traces)

            summary = {
                "workflow_id": workflow_id,
                "name": metadata.get("name", ""),
                "description": metadata.get("description", ""),
                "status": metadata.get("status", "unknown"),
                "created_at": metadata.get("created_at", ""),
                "updated_at": metadata.get("updated_at", ""),
                "stages": metadata.get("stages", []),
                "roles": metadata.get("roles", []),
                "deliverables_count": deliverables_count,
                "traces_count": traces_count,
                "archive_path": metadata.get("archive_path", ""),
            }

            return {"status": "success", "summary": summary}

        except Exception as e:
            logger.error(f"获取工作流摘要失败: {e}")
            return {"status": "error", "message": f"获取工作流摘要失败: {e!s}"}

    def _update_workflow_metadata(self, workflow_id: str, field: str, value: Any):
        """更新工作流元数据"""
        try:
            metadata_path = self.workflows_path / workflow_id / "metadata.json"
            if metadata_path.exists():
                metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                metadata[field] = value
                metadata["updated_at"] = datetime.now().isoformat()
                metadata_path.write_text(
                    json.dumps(metadata, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
        except Exception as e:
            logger.error(f"更新工作流元数据失败: {e}")

    def _find_document_trace(
        self,
        workflow_id: str,
        filename: str,
    ) -> Optional[dict[str, Any]]:
        """查找文档溯源记录"""
        try:
            for trace_file in self.traces_path.glob("*.json"):
                trace_data = json.loads(trace_file.read_text(encoding="utf-8"))
                if (
                    trace_data.get("workflow_id") == workflow_id
                    and trace_data.get("filename") == filename
                ):
                    return trace_data
            return None
        except Exception as e:
            logger.error(f"查找文档溯源记录失败: {e}")
            return None

    def _get_workflow_traces(self, workflow_id: str) -> list[dict[str, Any]]:
        """获取工作流的所有溯源记录"""
        traces = []
        try:
            for trace_file in self.traces_path.glob("*.json"):
                trace_data = json.loads(trace_file.read_text(encoding="utf-8"))
                if trace_data.get("workflow_id") == workflow_id:
                    traces.append(trace_data)
        except Exception as e:
            logger.error(f"获取工作流溯源记录失败: {e}")
        return traces


# 全局增强型协作系统实例
enhanced_collaboration_system = EnhancedCollaborationSystem()
