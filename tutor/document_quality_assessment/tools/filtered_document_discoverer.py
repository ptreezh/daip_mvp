#!/usr/bin/env python3
"""
DAIP-LIVE 规范化文档发现器（精炼版）
用于发现真正的规范化文档，过滤临时文件和重复内容
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from document_discoverer import DocumentDiscoverer, DocumentInfo


class FilteredDocumentDiscoverer(DocumentDiscoverer):
    """精炼的文档发现器，专注于真正的规范化文档"""

    def __init__(self, base_path: str):
        super().__init__(base_path)

        # 精确的规范文档模式
        self.exact_spec_patterns = [
            # 核心规范文档
            r"PROJECT_SPEC\.md$",
            r"MAIN_CONTROL_DOCUMENT\.md$",
            r"SYSTEM_ARCHITECTURE\.md$",
            r"DETAILED_SYSTEM_ARCHITECTURE\.md$",
            r"REQUIREMENTS_SPECIFICATION\.md$",

            # 组件规范
            r".*_REQUIREMENTS\.md$",
            r".*_SPECIFICATION\.md$",
            r".*_DESIGN_SPEC\.md$",
            r".*_IMPLEMENTATION_SPEC\.md$",

            # 架构和设计文档
            r".*_ARCHITECTURE\.md$",
            r".*_DESIGN\.md$",
            r"DATABASE_DESIGN_SPECIFICATION\.md$",
            r"TUI_.*_SPEC\.md$",

            # 流程规范
            r"TDD_.*_SPEC\.md$",
            r"TESTING_.*\.md$",
            r"SPEC_.*_DEVELOPMENT\.md$",

            # 集成规范
            r".*_INTEGRATION_.*\.md$",
            r".*_INTERFACE_.*\.md$",
            r"permission_.*_spec\.md$",

            # feature specs
            r"specs/[^/]+/spec\.md$",
            r"specs/[^/]+/plan\.md$",
        ]

        # 排除模式
        self.exclude_patterns = [
            # 测试文件
            r"^test_.*\.md$",
            r".*_test\.md$",
            r".*_TEST\.md$",
            r"^tests?/.*",

            # 临时和报告文件
            r".*_REPORT\.md$",
            r".*_FIX_.*\.md$",
            r".*_SUMMARY\.md$",
            r".*_STATUS\.md$",
            r".*_LOG\.md$",
            r"debug_.*\.md$",
            r"temp_.*\.md$",
            r".*_TEMP\.md$",

            # 备份和版本文件
            r".*\.backup\.md$",
            r".*\.bak\.md$",
            r".*_v\d+\.md$",

            # 例子和演示文件
            r".*_example\.md$",
            r".*_demo\.md$",
            r".*_sample\.md$",

            # 文档工具文件
            r"README\.md$",
            r"CHANGELOG\.md$",
            r"HISTORY\.md$",

            # 用户文档
            r".*_GUIDE\.md$",
            r".*_MANUAL\.md$",
            r".*_TUTORIAL\.md$",
            r"how_to_.*\.md$",

            # 个人笔记和草稿
            r"工作日志.*\.md$",
            r".*草稿\.md$",
            r".*NOTE\.md$",

            # 构建和配置文件
            r".*config\.md$",
            r".*setup\.md$",
            r".*install\.md$",
        ]

        # 重点关注的目录
        self.priority_directories = [
            "docs/specs",
            "docs/specifications",
            "docs/architecture",
            "specs",
            ".spec-kit",
        ]

        # 必须包含的关键词（用于验证文档质量）
        self.required_content_indicators = [
            "需求", "要求", "功能", "设计", "架构", "实现", "接口", "组件",
            "requirement", "specification", "design", "architecture",
            "implementation", "interface", "component", "module"
        ]

    def should_exclude_file(self, file_path: Path, relative_path: str) -> bool:
        """判断是否应该排除文件"""
        file_name = file_path.name
        relative_lower = relative_path.lower()

        # 检查排除模式
        for pattern in self.exclude_patterns:
            if re.match(pattern, file_name) or re.search(pattern, relative_lower):
                return True

        # 排除深层目录中的文件（可能是临时文件）
        if relative_lower.count('/') >= 4:
            return True

        # 排除在典型非规范目录中的文件
        non_spec_dirs = [
            "test", "tests", "example", "examples", "demo", "temp", "backup",
            "archive", "node_modules", ".git", "__pycache__", "build", "dist"
        ]

        for non_spec_dir in non_spec_dirs:
            if f"/{non_spec_dir}/" in relative_lower or relative_lower.startswith(f"{non_spec_dir}/"):
                return True

        return False

    def is_valid_spec_document(self, file_path: Path, relative_path: str, content: str) -> bool:
        """验证是否为有效的规范文档"""
        # 检查是否匹配精确模式
        is_exact_match = False
        for pattern in self.exact_spec_patterns:
            if re.search(pattern, relative_path) or re.search(pattern, file_path.name):
                is_exact_match = True
                break

        # 如果在优先目录中，降低匹配要求
        in_priority_dir = any(
            priority_dir in relative_path
            for priority_dir in self.priority_directories
        )

        # 检查内容质量指标
        content_indicators = 0
        content_lower = content.lower()

        for indicator in self.required_content_indicators:
            if indicator in content_lower:
                content_indicators += 1

        # 验证文档长度和结构
        min_lines = 20 if in_priority_dir else 30
        has_headers = len(re.findall(r'^#+\s+', content, re.MULTILINE)) >= 3
        has_proper_structure = (
            '##' in content or  # 有二级标题
            '###' in content or  # 有三级标题
            any(keyword in content.lower() for keyword in ['概述', 'overview', 'introduction'])
        )

        # 决策逻辑
        if is_exact_match:
            return True

        if in_priority_dir and content_indicators >= 2 and len(content.split('\n')) >= min_lines:
            return True

        if not in_priority_dir and content_indicators >= 3 and has_headers and has_proper_structure:
            return True

        return False

    def discover_documents(self, search_paths: List[str] = None) -> List[DocumentInfo]:
        """发现真正的规范化文档"""
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
        excluded_files = 0
        invalid_content_files = 0

        for search_path in search_paths:
            full_path = self.base_path / search_path
            if not full_path.exists():
                continue

            print(f"搜索路径: {full_path}")

            # 递归搜索所有markdown文件
            for file_path in full_path.rglob("*.md"):
                total_files += 1
                relative_path = str(file_path.relative_to(self.base_path))

                # 排除检查
                if self.should_exclude_file(file_path, relative_path):
                    excluded_files += 1
                    continue

                try:
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

                    if not content or len(content.strip()) < 100:
                        continue

                    # 验证是否为有效规范文档
                    if not self.is_valid_spec_document(file_path, relative_path, content):
                        invalid_content_files += 1
                        continue

                    # 获取文件信息
                    stat = file_path.stat()

                    # 创建文档信息
                    doc_info = DocumentInfo(
                        file_path=str(file_path.absolute()),
                        file_name=file_path.name,
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

        print(f"文档发现统计:")
        print(f"  总文件数: {total_files}")
        print(f"  排除文件: {excluded_files}")
        print(f"  内容无效: {invalid_content_files}")
        print(f"  最终文档: {len(documents)}")

        return documents

    def remove_duplicates(self, documents: List[DocumentInfo]) -> List[DocumentInfo]:
        """移除重复的文档"""
        seen_hashes = set()
        seen_names = set()
        unique_docs = []

        for doc in documents:
            # 基于文件哈希去重
            if doc.file_hash and doc.file_hash in seen_hashes:
                continue

            # 基于文件名去重（在相同目录下）
            name_key = f"{doc.relative_path.rsplit('/', 1)[0]}/{doc.file_name}"
            if name_key in seen_names:
                continue

            seen_hashes.add(doc.file_hash)
            seen_names.add(name_key)
            unique_docs.append(doc)

        print(f"去重前: {len(documents)} 份文档")
        print(f"去重后: {len(unique_docs)} 份文档")

        return unique_docs


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 3:
        print("用法: python filtered_document_discoverer.py <项目根目录> <输出目录>")
        return

    project_root = sys.argv[1]
    output_dir = sys.argv[2]

    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 创建精炼文档发现器
    discoverer = FilteredDocumentDiscoverer(project_root)

    # 发现文档
    documents = discoverer.discover_documents()

    if documents:
        # 去重
        unique_documents = discoverer.remove_duplicates(documents)

        # 导出原始数据
        json_file = Path(output_dir) / "filtered_documents.json"
        discoverer.export_documents_to_json(unique_documents, str(json_file))

        # 生成报告
        report = discoverer.generate_discovery_report(unique_documents)
        report_file = Path(output_dir) / "filtered_document_discovery_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        # 按日期排序的文档列表
        docs_by_date = discoverer.sort_documents_by_date(unique_documents, "modification")
        sorted_json_file = Path(output_dir) / "filtered_documents_sorted_by_date.json"
        discoverer.export_documents_to_json(docs_by_date, str(sorted_json_file))

        print(f"\n精炼文档发现完成！")
        print(f"- 找到 {len(unique_documents)} 份高质量规范文档")
        print(f"- 发现报告: {report_file}")
        print(f"- 完整数据: {json_file}")
        print(f"- 按日期排序: {sorted_json_file}")

        # 显示统计信息
        type_groups = discoverer.group_documents_by_type(unique_documents)
        priority_groups = discoverer.group_documents_by_priority(unique_documents)

        print(f"\n文档类型分布:")
        for doc_type, docs in type_groups.items():
            if docs:
                print(f"  {doc_type}: {len(docs)} 份")

        print(f"\n优先级分布:")
        for priority, docs in priority_groups.items():
            if docs:
                print(f"  {priority}: {len(docs)} 份")

    else:
        print("没有找到任何符合条件的规范文档。")


if __name__ == "__main__":
    main()