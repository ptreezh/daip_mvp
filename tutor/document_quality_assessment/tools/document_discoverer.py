#!/usr/bin/env python3
"""
DAIP-LIVE 规范化文档发现器
用于发现、分类和按时间排序所有规范化文档
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict


@dataclass
class DocumentInfo:
    """文档信息数据结构"""
    file_path: str
    file_name: str
    relative_path: str
    file_size: int
    creation_date: datetime
    modification_date: datetime
    file_hash: str
    document_type: str
    priority_level: str
    version_info: Dict[str, str]
    content_preview: str


class DocumentDiscoverer:
    """文档发现器"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.spec_file_patterns = [
            "*spec*.md",
            "*SPEC*.md",
            "*requirement*.md",
            "*REQUIREMENT*.md",
            "*architecture*.md",
            "*ARCHITECTURE*.md",
            "*design*.md",
            "*DESIGN*.md",
            "*plan*.md",
            "*PLAN*.md",
            "*manual*.md",
            "*MANUAL*.md",
            "*guide*.md",
            "*GUIDE*.md",
            "*process*.md",
            "*PROCESS*.md",
            "PROJECT_SPEC.md",
            "MAIN_CONTROL_DOCUMENT.md",
            "SYSTEM_ARCHITECTURE.md",
            "DETAILED_SYSTEM_ARCHITECTURE.md"
        ]

        self.document_type_patterns = {
            "strategic": [
                "project_spec", "main_control", "overall", "战略", "总体规划", "PROJECT_SPEC",
                "MAIN_CONTROL", "总体架构", "整体设计"
            ],
            "architectural": [
                "architecture", "arch", "架构", "system_design", "系统设计", "SYSTEM_ARCHITECTURE",
                "DETAILED_SYSTEM_ARCHITECTURE", "架构设计", "系统架构"
            ],
            "component": [
                "component", "module", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8",
                "组件", "模块", "persistence", "wiki", "model_provider", "agent_engine"
            ],
            "feature": [
                "feature", "functional", "功能", "features", "debate", "permission", "intent",
                "scaffold", "collaboration", "cli", "tui", "gui"
            ],
            "integration": [
                "integration", "interface", "api", "集成", "接口", "API", "INTERFACE",
                "permission_integration", "user_response", "tui_interface"
            ],
            "process": [
                "process", "workflow", "tdd", "methodology", "流程", "方法", "TDD",
                "TESTING_STRATEGY", "testing", "test", "implementation_spec"
            ]
        }

        self.priority_keywords = {
            "critical": [
                "核心", "关键", "重要", "主要", "core", "critical", "key", "important",
                "main", "primary", "essential"
            ],
            "high": [
                "高", "优先", "必须", "要求", "high", "priority", "must", "requirement",
                "mandatory", "necessary"
            ],
            "medium": [
                "中", "应该", "建议", "medium", "should", "recommended", "suggested"
            ],
            "low": [
                "低", "可选", "参考", "low", "optional", "reference", "nice_to_have"
            ]
        }

    def calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        import hashlib

        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception:
            return ""

    def extract_version_info(self, file_path: str, content: str) -> Dict[str, str]:
        """提取版本信息"""
        version_info = {}

        # 版本号匹配
        version_patterns = [
            r'v?(\d+\.\d+(?:\.\d+)?)',
            r'版本[：:]\s*(\d+\.\d+(?:\.\d+)?)',
            r'version[：:]\s*(\d+\.\d+(?:\.\d+)?)',
            r'Version[：:]\s*(\d+\.\d+(?:\.\d+)?)'
        ]

        for pattern in version_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                version_info["version"] = match.group(1)
                break

        # 日期匹配
        date_patterns = [
            r'(20\d{2}[/-]\d{1,2}[/-]\d{1,2})',
            r'(20\d{2}年\d{1,2}月\d{1,2}日)',
            r'日期[：:]\s*(20\d{2}[/-]\d{1,2}[/-]\d{1,2})',
            r'Date[：:]\s*(20\d{2}[/-]\d{1,2}[/-]\d{1,2})',
            r'更新时间[：:]\s*(20\d{2}[/-]\d{1,2}[/-]\d{1,2})'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                version_info["date"] = match.group(1)
                break

        # 作者信息
        author_patterns = [
            r'作者[：:]\s*([^\n\r]+)',
            r'Author[：:]\s*([^\n\r]+)',
            r'创建者[：:]\s*([^\n\r]+)'
        ]

        for pattern in author_patterns:
            match = re.search(pattern, content)
            if match:
                version_info["author"] = match.group(1).strip()
                break

        # 状态信息
        status_patterns = [
            r'状态[：:]\s*([^\n\r]+)',
            r'Status[：:]\s*([^\n\r]+)',
            r'(草稿|draft|评审|review|批准|approved|实施|implemented)'
        ]

        for pattern in status_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                version_info["status"] = match.group(1).strip()
                break

        return version_info

    def classify_document_type(self, file_path: str, content: str) -> str:
        """分类文档类型"""
        file_name = Path(file_path).name.lower()
        file_path_lower = file_path.lower()
        content_lower = content.lower()

        # 计算每种类型的匹配分数
        type_scores = {doc_type: 0 for doc_type in self.document_type_patterns}

        for doc_type, keywords in self.document_type_patterns.items():
            for keyword in keywords:
                # 文件名匹配（权重最高）
                if keyword.lower() in file_name:
                    type_scores[doc_type] += 10

                # 路径匹配（权重中等）
                if keyword.lower() in file_path_lower:
                    type_scores[doc_type] += 5

                # 内容匹配（权重较低）
                if keyword.lower() in content_lower:
                    type_scores[doc_type] += 1

        # 返回得分最高的类型
        best_type = max(type_scores, key=type_scores.get)
        return best_type if type_scores[best_type] > 0 else "feature"

    def determine_priority_level(self, file_path: str, content: str) -> str:
        """确定优先级"""
        file_name = Path(file_path).name.lower()
        content_lower = content.lower()

        # 计算优先级分数
        priority_scores = {priority: 0 for priority in self.priority_keywords}

        for priority, keywords in self.priority_keywords.items():
            for keyword in keywords:
                # 文件名匹配
                if keyword.lower() in file_name:
                    priority_scores[priority] += 3

                # 内容匹配
                if keyword.lower() in content_lower:
                    priority_scores[priority] += 1

        # 特殊规则：特定文件名的高优先级
        high_priority_files = [
            "project_spec", "main_control", "system_architecture", "requirements_specification"
        ]

        for high_file in high_priority_files:
            if high_file.lower() in file_name:
                priority_scores["critical"] += 20
                break

        # 返回得分最高的优先级
        best_priority = max(priority_scores, key=priority_scores.get)
        return best_priority if priority_scores[best_priority] > 0 else "medium"

    def get_content_preview(self, file_path: str, max_length: int = 200) -> str:
        """获取内容预览"""
        try:
            # 尝试不同编码
            encodings = ['utf-8', 'gbk', 'utf-8-sig']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                        # 移除markdown格式标记
                        content = re.sub(r'[#*`\[\]()_-]', ' ', content)
                        # 移除多余空格
                        content = re.sub(r'\s+', ' ', content).strip()
                        return content[:max_length] + "..." if len(content) > max_length else content
                except UnicodeDecodeError:
                    continue

            return "无法读取文件内容"
        except Exception:
            return "读取文件失败"

    def discover_documents(self, search_paths: List[str] = None) -> List[DocumentInfo]:
        """发现所有规范化文档"""
        if search_paths is None:
            search_paths = [
                "docs",
                "docs/specs",
                "docs/architecture",
                "docs/specifications",
                "specs",
                "."
            ]

        documents = []
        total_files = 0

        for search_path in search_paths:
            full_path = self.base_path / search_path
            if not full_path.exists():
                continue

            print(f"搜索路径: {full_path}")

            # 递归搜索所有markdown文件
            for file_path in full_path.rglob("*.md"):
                total_files += 1

                # 检查是否匹配规范文档模式
                file_name = file_path.name
                is_spec_doc = False

                for pattern in self.spec_file_patterns:
                    if file_path.match(pattern):
                        is_spec_doc = True
                        break

                # 也在特定目录中查找
                spec_dirs = ["specs", "specifications", "architecture", "docs"]
                if any(spec_dir in str(file_path).lower() for spec_dir in spec_dirs):
                    is_spec_doc = True

                if not is_spec_doc:
                    continue

                try:
                    # 获取文件信息
                    stat = file_path.stat()
                    relative_path = str(file_path.relative_to(self.base_path))

                    # 读取文件内容
                    content = ""
                    encodings = ['utf-8', 'gbk', 'utf-8-sig']
                    for encoding in encodings:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                content = f.read()
                                break
                        except UnicodeDecodeError:
                            continue

                    if not content:
                        continue

                    # 创建文档信息
                    doc_info = DocumentInfo(
                        file_path=str(file_path.absolute()),
                        file_name=file_name,
                        relative_path=relative_path,
                        file_size=stat.st_size,
                        creation_date=datetime.fromtimestamp(stat.st_ctime),
                        modification_date=datetime.fromtimestamp(stat.st_mtime),
                        file_hash=self.calculate_file_hash(str(file_path)),
                        document_type=self.classify_document_type(str(file_path), content),
                        priority_level=self.determine_priority_level(str(file_path), content),
                        version_info=self.extract_version_info(str(file_path), content),
                        content_preview=self.get_content_preview(str(file_path))
                    )

                    documents.append(doc_info)

                except Exception as e:
                    print(f"处理文件失败 {file_path}: {e}")
                    continue

        print(f"总共检查了 {total_files} 个文件，找到 {len(documents)} 份规范文档")
        return documents

    def sort_documents_by_date(self, documents: List[DocumentInfo], sort_by: str = "modification") -> List[DocumentInfo]:
        """按日期排序文档"""
        if sort_by == "creation":
            return sorted(documents, key=lambda d: d.creation_date, reverse=True)
        elif sort_by == "modification":
            return sorted(documents, key=lambda d: d.modification_date, reverse=True)
        elif sort_by == "version_date":
            # 按版本信息中的日期排序
            def get_version_date(doc):
                if doc.version_info.get("date"):
                    try:
                        # 尝试解析不同格式的日期
                        date_str = doc.version_info["date"]
                        if "/" in date_str:
                            return datetime.strptime(date_str, "%Y/%m/%d")
                        elif "-" in date_str:
                            return datetime.strptime(date_str, "%Y-%m-%d")
                        elif "年" in date_str:
                            return datetime.strptime(date_str, "%Y年%m月%d日")
                    except:
                        pass
                return doc.modification_date

            return sorted(documents, key=get_version_date, reverse=True)
        else:
            return documents

    def group_documents_by_type(self, documents: List[DocumentInfo]) -> Dict[str, List[DocumentInfo]]:
        """按类型分组文档"""
        groups = {doc_type: [] for doc_type in self.document_type_patterns}
        groups["other"] = []

        for doc in documents:
            if doc.document_type in groups:
                groups[doc.document_type].append(doc)
            else:
                groups["other"].append(doc)

        return groups

    def group_documents_by_priority(self, documents: List[DocumentInfo]) -> Dict[str, List[DocumentInfo]]:
        """按优先级分组文档"""
        groups = {priority: [] for priority in self.priority_keywords}
        groups["unknown"] = []

        for doc in documents:
            if doc.priority_level in groups:
                groups[doc.priority_level].append(doc)
            else:
                groups["unknown"].append(doc)

        return groups

    def export_documents_to_json(self, documents: List[DocumentInfo], output_path: str):
        """导出文档信息到JSON文件"""
        # 转换为可序列化的格式
        serializable_docs = []
        for doc in documents:
            serializable_doc = asdict(doc)
            # 转换日期为字符串
            serializable_doc["creation_date"] = doc.creation_date.isoformat()
            serializable_doc["modification_date"] = doc.modification_date.isoformat()
            serializable_docs.append(serializable_doc)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_docs, f, ensure_ascii=False, indent=2)

    def generate_discovery_report(self, documents: List[DocumentInfo]) -> str:
        """生成文档发现报告"""
        total_docs = len(documents)

        if total_docs == 0:
            return "# 文档发现报告\n\n没有找到任何规范文档。"

        # 按类型统计
        type_groups = self.group_documents_by_type(documents)
        type_stats = {doc_type: len(docs) for doc_type, docs in type_groups.items() if docs}

        # 按优先级统计
        priority_groups = self.group_documents_by_priority(documents)
        priority_stats = {priority: len(docs) for priority, docs in priority_groups.items() if docs}

        # 按日期排序
        docs_by_modification = self.sort_documents_by_date(documents, "modification")
        docs_by_creation = self.sort_documents_by_date(documents, "creation")

        # 最新和最旧的文档
        newest_doc = docs_by_modification[0] if docs_by_modification else None
        oldest_doc = docs_by_modification[-1] if docs_by_modification else None

        # 计算总文件大小
        total_size = sum(doc.file_size for doc in documents)
        avg_size = total_size / total_docs if total_docs > 0 else 0

        report = f"""# DAIP-LIVE 规范化文档发现报告

## 总体概况
- **文档总数**: {total_docs} 份
- **总文件大小**: {total_size:,} 字节 ({total_size/1024/1024:.2f} MB)
- **平均文件大小**: {avg_size:.0f} 字节
- **发现时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 文档类型分布
"""
        for doc_type, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = count / total_docs * 100
            report += f"- **{doc_type}**: {count} 份 ({percentage:.1f}%)\n"

        report += "\n## 优先级分布\n"
        for priority, count in sorted(priority_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = count / total_docs * 100
            report += f"- **{priority}**: {count} 份 ({percentage:.1f}%)\n"

        if newest_doc and oldest_doc:
            report += f"""
## 时间跨度
- **最新文档**: {newest_doc.file_name} ({newest_doc.modification_date.strftime('%Y-%m-%d %H:%M:%S')})
- **最旧文档**: {oldest_doc.file_name} ({oldest_doc.modification_date.strftime('%Y-%m-%d %H:%M:%S')})
- **时间跨度**: {(newest_doc.modification_date - oldest_doc.modification_date).days} 天
"""

        report += "\n## 最新更新的10份文档\n"
        for i, doc in enumerate(docs_by_modification[:10], 1):
            report += f"{i}. **{doc.file_name}** ({doc.modification_date.strftime('%Y-%m-%d %H:%M')}) - {doc.document_type} - {doc.priority_level}\n"

        report += "\n## 关键文档（高优先级）\n"
        high_priority_docs = [doc for doc in documents if doc.priority_level in ["critical", "high"]]
        high_priority_docs.sort(key=lambda d: d.modification_date, reverse=True)

        for i, doc in enumerate(high_priority_docs[:15], 1):
            version_str = f" v{doc.version_info.get('version', '')}" if doc.version_info.get('version') else ""
            report += f"{i}. **{doc.file_name}**{version_str} - {doc.document_type}\n"

        report += "\n## 文档版本信息统计\n"
        docs_with_version = [doc for doc in documents if doc.version_info.get("version")]
        docs_with_date = [doc for doc in documents if doc.version_info.get("date")]
        docs_with_author = [doc for doc in documents if doc.version_info.get("author")]

        report += f"- **有版本信息**: {len(docs_with_version)} 份 ({len(docs_with_version)/total_docs*100:.1f}%)\n"
        report += f"- **有日期信息**: {len(docs_with_date)} 份 ({len(docs_with_date)/total_docs*100:.1f}%)\n"
        report += f"- **有作者信息**: {len(docs_with_author)} 份 ({len(docs_with_author)/total_docs*100:.1f}%)\n"

        # 版本分布
        if docs_with_version:
            version_counts = {}
            for doc in docs_with_version:
                version = doc.version_info["version"]
                major_version = version.split('.')[0]
                version_counts[major_version] = version_counts.get(major_version, 0) + 1

            report += "\n### 主版本分布\n"
            for version, count in sorted(version_counts.items(), key=lambda x: x[1], reverse=True):
                report += f"- **v{version}**: {count} 份\n"

        return report


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 3:
        print("用法: python document_discoverer.py <项目根目录> <输出目录>")
        return

    project_root = sys.argv[1]
    output_dir = sys.argv[2]

    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 创建文档发现器
    discoverer = DocumentDiscoverer(project_root)

    # 发现文档
    documents = discoverer.discover_documents()

    if documents:
        # 导出原始数据
        json_file = Path(output_dir) / "discovered_documents.json"
        discoverer.export_documents_to_json(documents, str(json_file))

        # 生成报告
        report = discoverer.generate_discovery_report(documents)
        report_file = Path(output_dir) / "document_discovery_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        # 按日期排序的文档列表
        docs_by_date = discoverer.sort_documents_by_date(documents, "modification")
        sorted_json_file = Path(output_dir) / "documents_sorted_by_date.json"
        discoverer.export_documents_to_json(docs_by_date, str(sorted_json_file))

        print(f"文档发现完成！")
        print(f"- 找到 {len(documents)} 份规范文档")
        print(f"- 发现报告: {report_file}")
        print(f"- 完整数据: {json_file}")
        print(f"- 按日期排序: {sorted_json_file}")

        # 显示统计信息
        type_groups = discoverer.group_documents_by_type(documents)
        priority_groups = discoverer.group_documents_by_priority(documents)

        print(f"\n文档类型分布:")
        for doc_type, docs in type_groups.items():
            if docs:
                print(f"  {doc_type}: {len(docs)} 份")

        print(f"\n优先级分布:")
        for priority, docs in priority_groups.items():
            if docs:
                print(f"  {priority}: {len(docs)} 份")

    else:
        print("没有找到任何规范文档。")


if __name__ == "__main__":
    main()