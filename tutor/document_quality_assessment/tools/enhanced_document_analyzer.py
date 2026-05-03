#!/usr/bin/env python3
"""
增强版文档分析器
汇聚并分析项目中的所有规范文档，包括：
- docs/ 目录下的所有文档
- docs/specs/ 目录下的规格文档
- specs/ 目录下的功能规格文档
- 其他相关文档
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from datetime import datetime
import yaml

@dataclass
class DocumentInfo:
    """文档信息"""
    path: str
    relative_path: str
    file_name: str
    file_size: int
    modified_time: str
    document_type: str  # 'spec', 'architecture', 'process', 'compliance', 'other'
    module_id: Optional[str]
    title: Optional[str]
    content_preview: str
    word_count: int
    line_count: int
    tags: List[str]
    quality_score: float

@dataclass
class DocumentRelationship:
    """文档关系"""
    source_doc: str
    target_doc: str
    relationship_type: str  # 'depends_on', 'references', 'implements', 'extends'
    confidence: float
    evidence: List[str]

class EnhancedDocumentAnalyzer:
    """增强版文档分析器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)

        # 定义要搜索的文档目录
        self.document_directories = [
            "docs",
            "docs/specs",
            "docs/architecture",
            "docs/process",
            "docs/compliance",
            "docs/newP5",
            "docs/newP6",
            "docs/newP7",
            "specs",
            "tutor/document_quality_assessment",
            "tutor/platform_architecture.md"
        ]

        # 文档类型识别模式
        self.type_patterns = {
            'spec': [
                r'spec.*\.md$',
                r'.*spec.*\.md$',
                r'requirement.*\.md$',
                r'.*requirement.*\.md$'
            ],
            'architecture': [
                r'architecture.*\.md$',
                r'.*architecture.*\.md$',
                r'design.*\.md$',
                r'.*design.*\.md$'
            ],
            'process': [
                r'process.*\.md$',
                r'.*process.*\.md$',
                r'procedure.*\.md$',
                r'.*procedure.*\.md$',
                r'workflow.*\.md$'
            ],
            'compliance': [
                r'compliance.*\.md$',
                r'.*compliance.*\.md$',
                r'checklist.*\.md$',
                r'.*checklist.*\.md$'
            ],
            'testing': [
                r'test.*\.md$',
                r'.*test.*\.md$',
                r'validation.*\.md$'
            ]
        }

        # 模块识别模式
        self.module_patterns = {
            'p0': [r'p0', r'core.*interface', r'interface'],
            'p1': [r'p1', r'data.*persistence', r'database', r'persistence'],
            'p2': [r'p2', r'knowledge.*manager', r'wiki', r'knowledge'],
            'p3': [r'p3', r'model.*provider', r'llm', r'provider'],
            'p4': [r'p4', r'role.*manager', r'tool'],
            'p5': [r'p5', r'agent.*engine', r'agent'],
            'p6': [r'p6', r'cli.*tui', r'tui', r'cli'],
            'p7': [r'p7', r'gui', r'interface'],
            'p8': [r'p8', r'debate.*system', r'debate'],
            'newp5': [r'newp5', r'new.*p5'],
            'newp6': [r'newp6', r'new.*p6'],
            'newp7': [r'newp7', r'new.*p7']
        }

    def analyze_all_documents(self) -> Dict[str, DocumentInfo]:
        """分析所有文档"""
        print("🔍 开始分析项目文档...")

        all_documents = {}

        # 搜索所有文档目录
        for directory in self.document_directories:
            doc_path = self.project_root / directory
            if doc_path.exists():
                print(f"   分析目录: {directory}")
                documents = self._analyze_directory(doc_path, directory)
                all_documents.update(documents)
            else:
                print(f"   目录不存在: {directory}")

        print(f"📊 总共发现 {len(all_documents)} 个文档")
        return all_documents

    def _analyze_directory(self, directory: Path, relative_to: str) -> Dict[str, DocumentInfo]:
        """分析单个目录"""
        documents = {}

        # 查找所有Markdown文件
        for file_path in directory.rglob("*.md"):
            if file_path.is_file():
                try:
                    doc_info = self._analyze_document(file_path, relative_to)
                    if doc_info:
                        documents[str(file_path.relative_to(self.project_root))] = doc_info
                except Exception as e:
                    print(f"      ⚠️  分析文档失败 {file_path}: {e}")

        return documents

    def _analyze_document(self, file_path: Path, relative_to: str) -> Optional[DocumentInfo]:
        """分析单个文档"""
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 获取文件信息
            stat = file_path.stat()
            relative_path = str(file_path.relative_to(self.project_root))

            # 提取文档信息
            title = self._extract_title(content)
            document_type = self._identify_document_type(file_path.name, content)
            module_id = self._identify_module(file_path.name, content)
            tags = self._extract_tags(content)

            # 计算质量评分
            quality_score = self._calculate_quality_score(content, file_path.name)

            return DocumentInfo(
                path=str(file_path),
                relative_path=relative_path,
                file_name=file_path.name,
                file_size=stat.st_size,
                modified_time=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                document_type=document_type,
                module_id=module_id,
                title=title,
                content_preview=content[:200] + "..." if len(content) > 200 else content,
                word_count=len(content.split()),
                line_count=len(content.splitlines()),
                tags=tags,
                quality_score=quality_score
            )

        except Exception as e:
            print(f"      ❌ 读取文档失败 {file_path}: {e}")
            return None

    def _extract_title(self, content: str) -> Optional[str]:
        """提取文档标题"""
        lines = content.splitlines()
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        return None

    def _identify_document_type(self, filename: str, content: str) -> str:
        """识别文档类型"""
        filename_lower = filename.lower()
        content_lower = content.lower()

        # 根据文件名和内容识别类型
        for doc_type, patterns in self.type_patterns.items():
            for pattern in patterns:
                if (re.search(pattern, filename_lower, re.IGNORECASE) or
                    re.search(pattern, content_lower, re.IGNORECASE)):
                    return doc_type

        return 'other'

    def _identify_module(self, filename: str, content: str) -> Optional[str]:
        """识别文档所属模块"""
        filename_lower = filename.lower()
        content_lower = content.lower()

        for module_id, patterns in self.module_patterns.items():
            for pattern in patterns:
                if (re.search(pattern, filename_lower, re.IGNORECASE) or
                    re.search(pattern, content_lower, re.IGNORECASE)):
                    return module_id

        return None

    def _extract_tags(self, content: str) -> List[str]:
        """提取文档标签"""
        tags = []

        # 查找常见的标签模式
        tag_patterns = [
            r'#(\w+)',  # #标签
            r'tag:\s*(\w+)',  # tag: 标签
            r'category:\s*(\w+)',  # category: 分类
        ]

        for pattern in tag_patterns:
            matches = re.findall(pattern, content.lower())
            tags.extend(matches)

        # 去重并限制数量
        return list(set(tags))[:10]

    def _calculate_quality_score(self, content: str, filename: str) -> float:
        """计算文档质量评分 (0-100)"""
        score = 0.0

        # 基础分数 (有内容)
        if content.strip():
            score += 20

        # 标题存在
        if re.search(r'^# ', content, re.MULTILINE):
            score += 10

        # 结构化程度
        if re.search(r'^#+ ', content, re.MULTILINE):
            headings = len(re.findall(r'^#+ ', content, re.MULTILINE))
            score += min(headings * 2, 15)

        # 列表存在
        if re.search(r'^[-*+] ', content, re.MULTILINE):
            score += 10

        # 代码块存在
        if re.search(r'```', content):
            score += 10

        # 表格存在
        if re.search(r'\|.*\|', content):
            score += 5

        # 链接存在
        if re.search(r'\[.*\]\(.*\)', content):
            score += 5

        # 长度适中 (不能太短也不能太长)
        word_count = len(content.split())
        if 100 <= word_count <= 2000:
            score += 15
        elif 50 <= word_count < 100 or 2000 < word_count <= 5000:
            score += 10
        elif word_count > 50:
            score += 5

        # 文件名规范
        if re.match(r'^[a-zA-Z0-9_-]+\.md$', filename):
            score += 5

        # 没有明显的格式错误
        errors = 0
        if 'TODO' in content or 'FIXME' in content:
            errors -= 5
        if content.count('```') % 2 != 0:
            errors -= 5

        score += max(errors, -15)

        return min(max(score, 0), 100)

    def find_document_relationships(self, documents: Dict[str, DocumentInfo]) -> List[DocumentRelationship]:
        """分析文档间关系"""
        relationships = []
        doc_list = list(documents.values())

        print("🔗 分析文档关系...")

        for i, doc1 in enumerate(doc_list):
            for j, doc2 in enumerate(doc_list):
                if i >= j:  # 避免重复和自引用
                    continue

                relationship = self._analyze_relationship(doc1, doc2)
                if relationship:
                    relationships.append(relationship)

        print(f"📊 发现 {len(relationships)} 个文档关系")
        return relationships

    def _analyze_relationship(self, doc1: DocumentInfo, doc2: DocumentInfo) -> Optional[DocumentRelationship]:
        """分析两个文档之间的关系"""
        # 读取文档内容进行详细分析
        try:
            with open(self.project_root / doc1.path, 'r', encoding='utf-8') as f:
                content1 = f.read()
            with open(self.project_root / doc2.path, 'r', encoding='utf-8') as f:
                content2 = f.read()
        except:
            return None

        evidence = []
        relationship_type = None
        confidence = 0.0

        # 检查引用关系
        if doc2.file_name in content1:
            evidence.append(f"文档1直接引用了文档2的文件名")
            relationship_type = 'references'
            confidence += 30

        if doc2.title and doc2.title in content1:
            evidence.append(f"文档1引用了文档2的标题")
            relationship_type = 'references'
            confidence += 40

        # 检查模块关系
        if doc1.module_id and doc2.module_id:
            if doc1.module_id == doc2.module_id:
                evidence.append(f"两个文档属于同一模块 {doc1.module_id}")
                confidence += 20

        # 检查类型关系
        if doc1.document_type == 'spec' and doc2.document_type == 'architecture':
            evidence.append("规格文档引用架构文档")
            relationship_type = 'implements'
            confidence += 25
        elif doc1.document_type == 'architecture' and doc2.document_type == 'spec':
            evidence.append("架构文档被规格文档实现")
            relationship_type = 'implements'
            confidence += 25

        # 检查标签相似性
        common_tags = set(doc1.tags) & set(doc2.tags)
        if common_tags:
            evidence.append(f"共同标签: {', '.join(common_tags)}")
            confidence += len(common_tags) * 5

        # 如果有足够的证据，返回关系
        if confidence > 20 and evidence:
            return DocumentRelationship(
                source_doc=doc1.relative_path,
                target_doc=doc2.relative_path,
                relationship_type=relationship_type or 'related',
                confidence=min(confidence, 100),
                evidence=evidence
            )

        return None

    def generate_analysis_report(self, documents: Dict[str, DocumentInfo],
                               relationships: List[DocumentRelationship]) -> Dict:
        """生成分析报告"""
        # 统计信息
        total_docs = len(documents)
        docs_by_type = Counter(doc.document_type for doc in documents.values())
        docs_by_module = Counter(doc.module_id for doc in documents.values() if doc.module_id)

        avg_quality = sum(doc.quality_score for doc in documents.values()) / total_docs if total_docs > 0 else 0

        high_quality_docs = [doc for doc in documents.values() if doc.quality_score >= 80]
        low_quality_docs = [doc for doc in documents.values() if doc.quality_score < 50]

        return {
            'summary': {
                'total_documents': total_docs,
                'documents_by_type': dict(docs_by_type),
                'documents_by_module': dict(docs_by_module),
                'average_quality_score': round(avg_quality, 2),
                'high_quality_documents': len(high_quality_docs),
                'low_quality_documents': len(low_quality_docs),
                'total_relationships': len(relationships)
            },
            'documents': {path: asdict(doc) for path, doc in documents.items()},
            'relationships': [asdict(rel) for rel in relationships],
            'quality_distribution': {
                'excellent': len([d for d in documents.values() if d.quality_score >= 90]),
                'good': len([d for d in documents.values() if 70 <= d.quality_score < 90]),
                'fair': len([d for d in documents.values() if 50 <= d.quality_score < 70]),
                'poor': len([d for d in documents.values() if d.quality_score < 50])
            }
        }

def main():
    """主函数"""
    import sys
    project_root = len(sys.argv) > 1 and sys.argv[1] or "."

    print("📚 DAIP-LIVE 增强版文档分析器")
    print("=" * 50)
    print(f"项目根目录: {project_root}")

    # 创建分析器
    analyzer = EnhancedDocumentAnalyzer(project_root)

    # 分析所有文档
    documents = analyzer.analyze_all_documents()

    # 分析文档关系
    relationships = analyzer.find_document_relationships(documents)

    # 生成报告
    report = analyzer.generate_analysis_report(documents, relationships)

    # 保存报告
    output_file = Path(project_root) / "tutor" / "enhanced_document_analysis_report.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 分析报告已保存到: {output_file}")

    # 打印摘要
    summary = report['summary']
    print(f"\n📊 分析摘要:")
    print(f"   总文档数: {summary['total_documents']}")
    print(f"   平均质量分: {summary['average_quality_score']}")
    print(f"   高质量文档: {summary['high_quality_documents']}")
    print(f"   文档关系数: {summary['total_relationships']}")

    print(f"\n📋 文档类型分布:")
    for doc_type, count in summary['documents_by_type'].items():
        print(f"   {doc_type}: {count}")

if __name__ == "__main__":
    main()