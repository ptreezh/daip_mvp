#!/usr/bin/env python3
"""
DAIP-LIVE 规范化文档质量评估器
提供系统性的文档质量分析和评分功能
"""

import re
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class DocumentType(Enum):
    """文档类型枚举"""
    STRATEGIC = "strategic"      # 战略级文档
    ARCHITECTURAL = "architectural"  # 架构级文档
    COMPONENT = "component"      # 组件级文档
    FEATURE = "feature"          # 功能级文档
    INTEGRATION = "integration"  # 集成级文档
    PROCESS = "process"          # 流程级文档


class QualityLevel(Enum):
    """质量等级枚举"""
    EXCELLENT = "excellent"      # 优秀 (90-100)
    GOOD = "good"               # 良好 (80-89)
    AVERAGE = "average"         # 一般 (70-79)
    POOR = "poor"               # 较差 (60-69)
    CRITICAL = "critical"       # 严重问题 (0-59)


@dataclass
class QualityDimension:
    """质量维度数据结构"""
    name: str
    weight: float
    score: float
    max_score: float
    issues: List[str]
    suggestions: List[str]


@dataclass
class DocumentMetadata:
    """文档元数据"""
    file_path: str
    file_name: str
    file_size: int
    creation_date: Optional[datetime]
    modification_date: Optional[datetime]
    document_hash: str
    encoding: str


@dataclass
class QualityAssessmentResult:
    """质量评估结果"""
    document_metadata: DocumentMetadata
    document_type: DocumentType
    overall_score: float
    quality_level: QualityLevel
    dimensions: Dict[str, QualityDimension]
    critical_issues: List[str]
    improvement_suggestions: List[str]
    assessment_date: datetime
    version_info: Dict[str, Any]


class DocumentQualityAssessor:
    """文档质量评估器"""

    def __init__(self):
        self.quality_framework = {
            "清晰度与精确性": {
                "weight": 0.25,
                "criteria": [
                    "需求描述是否明确无歧义",
                    "技术术语是否定义清晰",
                    "是否有具体的量化指标",
                    "语言表达是否简洁准确"
                ]
            },
            "逻辑一致性": {
                "weight": 0.20,
                "criteria": [
                    "文档内部逻辑是否自洽",
                    "是否存在相互矛盾的描述",
                    "章节之间逻辑是否连贯",
                    "需求之间是否存在冲突"
                ]
            },
            "完整性": {
                "weight": 0.20,
                "criteria": [
                    "覆盖范围是否完整",
                    "关键要素是否齐全",
                    "需求可追溯性是否良好",
                    "是否缺失重要信息"
                ]
            },
            "标准化": {
                "weight": 0.15,
                "criteria": [
                    "格式是否符合规范",
                    "术语使用是否一致",
                    "结构是否符合标准",
                    "文档元数据是否完整"
                ]
            },
            "可维护性": {
                "weight": 0.10,
                "criteria": [
                    "版本跟踪是否完善",
                    "变更记录是否清晰",
                    "更新机制是否明确",
                    "维护责任是否明确"
                ]
            },
            "实用性": {
                "weight": 0.10,
                "criteria": [
                    "实施是否具有可行性",
                    "资源需求是否合理",
                    "时间安排是否现实",
                    "技术方案是否可行"
                ]
            }
        }

        self.ambiguity_patterns = [
            r"适当的|合理的|充分的|必要的",  # 模糊限定词
            r"尽可能|尽快|尽可能早",        # 模糊时间描述
            r"高性能|高质量|高效率",        # 模糊质量描述
            r"优化|改进|完善|增强",         # 模糊动作描述
            r"支持|包括|包含等",            # 不完整的列举
        ]

        self.contradiction_patterns = [
            (r"单机|单用户", r"多用户|分布式|并发"),  # 架构矛盾
            (r"本地处理|离线", r"云端处理|在线"),     # 部署矛盾
            (r"简单|轻量级", r"复杂|功能全面"),      # 复杂度矛盾
        ]

    def extract_metadata(self, file_path: str) -> DocumentMetadata:
        """提取文档元数据"""
        path = Path(file_path)
        stat = path.stat()

        # 计算文件哈希
        file_hash = ""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                file_hash = hashlib.md5(content).hexdigest()
        except Exception as e:
            print(f"计算文件哈希失败 {file_path}: {e}")

        # 尝试检测编码
        encoding = "utf-8"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1000)
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    f.read(1000)
                encoding = "gbk"
            except:
                encoding = "unknown"

        return DocumentMetadata(
            file_path=str(path.absolute()),
            file_name=path.name,
            file_size=stat.st_size,
            creation_date=datetime.fromtimestamp(stat.st_ctime),
            modification_date=datetime.fromtimestamp(stat.st_mtime),
            document_hash=file_hash,
            encoding=encoding
        )

    def classify_document_type(self, file_path: str, content: str) -> DocumentType:
        """根据文件路径和内容分类文档类型"""
        file_name = Path(file_path).name.lower()
        file_path_lower = file_path.lower()

        # 战略级文档识别
        if any(keyword in file_name for keyword in [
            "project_spec", "main_control", "overall", "战略", "总体规划"
        ]):
            return DocumentType.STRATEGIC

        # 架构级文档识别
        if any(keyword in file_path_lower or keyword in file_name for keyword in [
            "architecture", "arch", "架构", "system_design", "系统设计"
        ]):
            return DocumentType.ARCHITECTURAL

        # 组件级文档识别
        if any(keyword in file_path_lower for keyword in [
            "component", "module", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"
        ]):
            return DocumentType.COMPONENT

        # 功能级文档识别
        if any(keyword in file_path_lower for keyword in [
            "feature", "functional", "功能", "specs/"
        ]):
            return DocumentType.FEATURE

        # 集成级文档识别
        if any(keyword in file_name for keyword in [
            "integration", "interface", "api", "集成", "接口"
        ]):
            return DocumentType.INTEGRATION

        # 流程级文档识别
        if any(keyword in file_name for keyword in [
            "process", "workflow", "tdd", "methodology", "流程", "方法"
        ]):
            return DocumentType.PROCESS

        # 默认为功能级文档
        return DocumentType.FEATURE

    def assess_clarity_precision(self, content: str) -> QualityDimension:
        """评估清晰度与精确性"""
        issues = []
        suggestions = []
        score = 100.0

        # 检查模糊表达
        ambiguity_matches = 0
        for pattern in self.ambiguity_patterns:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            ambiguity_matches += matches
            if matches > 0:
                issues.append(f"发现 {matches} 处模糊表达: {pattern}")
                score -= min(matches * 3, 20)  # 每个模糊表达扣3分，最多扣20分

        # 检查术语定义
        if len(re.findall(r"[A-Z]{2,}|[A-Z][a-z]+(?:[A-Z][a-z]+)+", content)) > 10:
            technical_terms = len(re.findall(r"[A-Z]{2,}|[A-Z][a-z]+(?:[A-Z][a-z]+)+", content))
            if "术语" not in content and "定义" not in content:
                issues.append(f"发现 {technical_terms} 个技术术语，但缺少术语定义章节")
                score -= 10
                suggestions.append("添加术语定义章节，解释关键概念和缩写")

        # 检查量化指标
        if not re.search(r"\d+%|\d+ms|\d+s|\d+MB|\d+GB|\d+个|\d+次", content):
            issues.append("缺少具体的量化指标和性能要求")
            score -= 15
            suggestions.append("添加具体的性能指标和量化要求")

        # 检查语言简洁性
        sentences = content.split('。')
        long_sentences = sum(1 for s in sentences if len(s.strip()) > 100)
        if long_sentences > len(sentences) * 0.3:
            issues.append(f"发现 {long_sentences} 个长句（超过100字符），影响可读性")
            score -= 10
            suggestions.append("拆分长句，提高文档可读性")

        if ambiguity_matches == 0:
            suggestions.append("语言表达清晰，避免了模糊词汇")

        return QualityDimension(
            name="清晰度与精确性",
            weight=0.25,
            score=max(0, score),
            max_score=100.0,
            issues=issues,
            suggestions=suggestions
        )

    def assess_logical_consistency(self, content: str) -> QualityDimension:
        """评估逻辑一致性"""
        issues = []
        suggestions = []
        score = 100.0

        # 检查矛盾模式
        for neg_pattern, pos_pattern in self.contradiction_patterns:
            neg_matches = len(re.findall(neg_pattern, content, re.IGNORECASE))
            pos_matches = len(re.findall(pos_pattern, content, re.IGNORECASE))

            if neg_matches > 0 and pos_matches > 0:
                issues.append(f"发现潜在矛盾：{neg_pattern} vs {pos_pattern}")
                score -= 25
                suggestions.append(f"澄清和统一对{neg_pattern}和{pos_pattern}的描述")

        # 检查章节逻辑连贯性
        headers = re.findall(r'^#+\s*(.+)$', content, re.MULTILINE)
        if len(headers) < 3:
            issues.append("文档结构过于简单，缺少逻辑层次的章节划分")
            score -= 15
            suggestions.append("增加章节层次，建立清晰的文档结构")

        # 检查需求冲突
        requirement_sections = re.split(r'#+\s*(?:需求|要求|requirements)', content, flags=re.IGNORECASE)
        if len(requirement_sections) > 2:
            # 检查是否有重复或冲突的需求描述
            requirements = []
            for section in requirement_sections[1:]:
                reqs = re.findall(r'[-*]\s*(.+)', section)
                requirements.extend(reqs)

            if len(requirements) > 10:
                # 简单的重复检查
                unique_requirements = set(requirements)
                if len(unique_requirements) < len(requirements) * 0.8:
                    issues.append("发现可能重复的需求描述")
                    score -= 10
                    suggestions.append("合并重复需求，确保需求描述的唯一性")

        # 检查时态一致性
        tenses = {
            "现在时": len(re.findall(r"[是|为|具有|支持|提供]", content)),
            "将来时": len(re.findall(r"[将|会|将要|计划|预期]", content)),
            "过去时": len(re.findall(r"[已|已经|完成|实现|过去]", content))
        }

        if tenses["将来时"] > tenses["现在时"] * 2:
            suggestions.append("注意时态一致性，确保文档描述的准确性")

        if not issues:
            suggestions.append("文档逻辑一致性良好，未发现明显矛盾")

        return QualityDimension(
            name="逻辑一致性",
            weight=0.20,
            score=max(0, score),
            max_score=100.0,
            issues=issues,
            suggestions=suggestions
        )

    def assess_completeness(self, content: str, document_type: DocumentType) -> QualityDimension:
        """评估完整性"""
        issues = []
        suggestions = []
        score = 100.0

        # 基础完整性检查
        if len(content) < 500:
            issues.append("文档内容过短，可能缺少重要信息")
            score -= 30
        elif len(content) < 1500:
            issues.append("文档内容较少，可能需要更多详细信息")
            score -= 15

        # 检查关键章节
        required_sections = {
            DocumentType.STRATEGIC: ["概述", "目标", "范围", "成功标准"],
            DocumentType.ARCHITECTURAL: ["架构", "组件", "接口", "数据流"],
            DocumentType.COMPONENT: ["功能", "接口", "依赖", "实现"],
            DocumentType.FEATURE: ["需求", "设计", "实现", "测试"],
            DocumentType.INTEGRATION: ["接口", "协议", "数据格式", "错误处理"],
            DocumentType.PROCESS: ["流程", "步骤", "角色", "交付物"]
        }

        missing_sections = []
        for section in required_sections.get(document_type, []):
            if section not in content:
                missing_sections.append(section)

        if missing_sections:
            issues.append(f"缺少关键章节：{', '.join(missing_sections)}")
            score -= len(missing_sections) * 8
            suggestions.append(f"补充缺失的章节：{', '.join(missing_sections)}")

        # 检查可追溯性
        if "需求" in content and "测试" not in content and "验证" not in content:
            issues.append("有需求描述但缺少测试和验证策略")
            score -= 12
            suggestions.append("添加测试策略和验证标准")

        # 检查错误处理
        if document_type in [DocumentType.COMPONENT, DocumentType.INTEGRATION, DocumentType.FEATURE]:
            if "错误" not in content and "异常" not in content and "失败" not in content:
                issues.append("缺少错误处理和异常情况的描述")
                score -= 10
                suggestions.append("补充错误处理和异常情况说明")

        # 检查依赖关系
        if "依赖" not in content and "前置条件" not in content and document_type != DocumentType.STRATEGIC:
            suggestions.append("考虑添加依赖关系和前置条件说明")

        if not issues:
            suggestions.append("文档结构完整，覆盖了关键要素")

        return QualityDimension(
            name="完整性",
            weight=0.20,
            score=max(0, score),
            max_score=100.0,
            issues=issues,
            suggestions=suggestions
        )

    def assess_standardization(self, content: str, metadata: DocumentMetadata) -> QualityDimension:
        """评估标准化"""
        issues = []
        suggestions = []
        score = 100.0

        # 检查标题格式一致性
        headers = re.findall(r'^(#{1,6})\s*(.+)$', content, re.MULTILINE)
        header_levels = [len(h[0]) for h in headers]

        if header_levels:
            # 检查标题层次跳跃
            for i in range(1, len(header_levels)):
                if header_levels[i] - header_levels[i-1] > 1:
                    issues.append("发现标题层次跳跃，建议遵循渐进式标题结构")
                    score -= 8
                    break

        # 检查列表格式一致性
        dash_lists = len(re.findall(r'^-\s+', content, re.MULTILINE))
        star_lists = len(re.findall(r'^\*\s+', content, re.MULTILINE))
        number_lists = len(re.findall(r'^\d+\.\s+', content, re.MULTILINE))

        total_lists = dash_lists + star_lists + number_lists
        if total_lists > 0:
            dominant_format = max(dash_lists, star_lists, number_lists)
            if total_lists - dominant_format > 3:
                issues.append("列表格式不一致，建议统一使用同一种列表格式")
                score -= 10
                suggestions.append("统一列表格式，使用一致的符号或编号")

        # 检查术语一致性
        terms = re.findall(r'\b[A-Z]{2,}\b', content)
        term_variations = {}
        for term in terms:
            term_variations[term.lower()] = term_variations.get(term.lower(), 0) + 1

        inconsistent_terms = [term for term, count in term_variations.items() if count > 1]
        if inconsistent_terms:
            issues.append(f"发现术语大小写不一致：{', '.join(inconsistent_terms)}")
            score -= len(inconsistent_terms) * 3
            suggestions.append("统一术语的大小写使用规范")

        # 检查文档元数据
        metadata_indicators = ["版本", "日期", "作者", "状态", "version", "date", "author", "status"]
        missing_metadata = [indicator for indicator in metadata_indicators if indicator not in content[:500]]

        if len(missing_metadata) > 3:
            issues.append(f"文档元数据不完整，缺少：{', '.join(missing_metadata[:3])}等")
            score -= 8
            suggestions.append("完善文档元信息，包括版本、日期、作者、状态等")

        # 检查编码规范
        if metadata.encoding != "utf-8":
            suggestions.append("建议使用UTF-8编码以确保兼容性")

        if not issues:
            suggestions.append("文档格式标准化程度较高")

        return QualityDimension(
            name="标准化",
            weight=0.15,
            score=max(0, score),
            max_score=100.0,
            issues=issues,
            suggestions=suggestions
        )

    def assess_maintainability(self, content: str, metadata: DocumentMetadata) -> QualityDimension:
        """评估可维护性"""
        issues = []
        suggestions = []
        score = 100.0

        # 检查版本信息
        if not re.search(r'版本|version|v\d+\.\d+', content[:200]):
            issues.append("缺少明确的版本信息")
            score -= 15
            suggestions.append("添加文档版本号和版本说明")

        # 检查变更记录
        if "变更记录" not in content and "changelog" not in content and "更新历史" not in content:
            issues.append("缺少变更记录或更新历史")
            score -= 12
            suggestions.append("添加变更记录章节，跟踪文档演化历史")

        # 检查更新日期
        if metadata.modification_date:
            date_in_content = re.search(r'(20\d{2}[/-]\d{1,2}[/-]\d{1,2})', content)
            if not date_in_content:
                suggestions.append("在文档中明确标注最后更新日期")

        # 检查维护责任
        if "负责" not in content and "维护" not in content and "owner" not in content:
            suggestions.append("明确文档维护责任人")

        # 检查文档状态
        status_indicators = ["草稿", " draft", "评审", " review", "批准", " approved", "实施", " implemented"]
        has_status = any(indicator in content.lower() for indicator in status_indicators)
        if not has_status:
            suggestions.append("标注文档当前状态（草稿/评审/批准等）")

        # 检查引用完整性
        references = re.findall(r'\[([^\]]+)\]', content)
        if references and "参考" not in content and "reference" not in content:
            suggestions.append("添加参考文献章节，完善引用管理")

        if not issues:
            suggestions.append("文档可维护性设置良好")

        return QualityDimension(
            name="可维护性",
            weight=0.10,
            score=max(0, score),
            max_score=100.0,
            issues=issues,
            suggestions=suggestions
        )

    def assess_practicality(self, content: str, document_type: DocumentType) -> QualityDimension:
        """评估实用性"""
        issues = []
        suggestions = []
        score = 100.0

        # 检查技术可行性
        technical_terms = re.findall(r'\b[A-Z]{2,}\b', content)
        if len(technical_terms) > 20 and document_type != DocumentType.ARCHITECTURAL:
            suggestions.append("技术术语较多，建议增加技术可行性分析")

        # 检查资源需求
        if "资源" not in content and "resource" not in content and document_type != DocumentType.STRATEGIC:
            suggestions.append("考虑添加资源需求分析（人力、时间、设备等）")

        # 检查时间安排
        if "时间" not in content and "timeline" not in content and "schedule" not in content:
            if document_type in [DocumentType.FEATURE, DocumentType.PROCESS]:
                suggestions.append("建议添加时间安排和里程碑")

        # 检查依赖关系
        if "依赖" not in content and "dependency" not in content and "前提" not in content:
            if document_type != DocumentType.STRATEGIC:
                suggestions.append("分析并说明实施的先决条件和依赖关系")

        # 检查风险评估
        if "风险" not in content and "risk" not in content and "问题" not in content:
            if document_type in [DocumentType.ARCHITECTURAL, DocumentType.FEATURE]:
                suggestions.append("建议添加风险评估和缓解策略")

        # 检查可测试性
        if "测试" not in content and "test" not in content and "验证" not in content:
            if document_type in [DocumentType.FEATURE, DocumentType.COMPONENT]:
                issues.append("缺少测试策略和验证方法")
                score -= 15
                suggestions.append("添加具体的测试方案和验收标准")

        # 检查复杂度评估
        if document_type == DocumentType.FEATURE:
            complexity_indicators = ["复杂", "困难", "挑战", "complex", "difficult", "challenge"]
            has_complexity = any(indicator in content for indicator in complexity_indicators)
            if not has_complexity:
                suggestions.append("评估实施复杂度和难度级别")

        if not issues:
            suggestions.append("文档实用性考虑较为全面")

        return QualityDimension(
            name="实用性",
            weight=0.10,
            score=max(0, score),
            max_score=100.0,
            issues=issues,
            suggestions=suggestions
        )

    def assess_document(self, file_path: str) -> QualityAssessmentResult:
        """对单个文档进行全面质量评估"""
        # 提取元数据
        metadata = self.extract_metadata(file_path)

        # 读取内容
        try:
            with open(file_path, 'r', encoding=metadata.encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

        # 分类文档类型
        document_type = self.classify_document_type(file_path, content)

        # 执行各维度评估
        dimensions = {
            "清晰度与精确性": self.assess_clarity_precision(content),
            "逻辑一致性": self.assess_logical_consistency(content),
            "完整性": self.assess_completeness(content, document_type),
            "标准化": self.assess_standardization(content, metadata),
            "可维护性": self.assess_maintainability(content, metadata),
            "实用性": self.assess_practicality(content, document_type)
        }

        # 计算总分
        overall_score = sum(
            dim.score * dim.weight
            for dim in dimensions.values()
        )

        # 确定质量等级
        if overall_score >= 90:
            quality_level = QualityLevel.EXCELLENT
        elif overall_score >= 80:
            quality_level = QualityLevel.GOOD
        elif overall_score >= 70:
            quality_level = QualityLevel.AVERAGE
        elif overall_score >= 60:
            quality_level = QualityLevel.POOR
        else:
            quality_level = QualityLevel.CRITICAL

        # 收集关键问题和改进建议
        critical_issues = []
        improvement_suggestions = []

        for dim in dimensions.values():
            critical_issues.extend(dim.issues)
            improvement_suggestions.extend(dim.suggestions)

        # 提取版本信息
        version_info = {}
        version_match = re.search(r'v?(\d+\.\d+(?:\.\d+)?)', content)
        if version_match:
            version_info["version"] = version_match.group(1)

        date_match = re.search(r'(20\d{2}[/-]\d{1,2}[/-]\d{1,2})', content)
        if date_match:
            version_info["date"] = date_match.group(1)

        return QualityAssessmentResult(
            document_metadata=metadata,
            document_type=document_type,
            overall_score=round(overall_score, 2),
            quality_level=quality_level,
            dimensions=dimensions,
            critical_issues=critical_issues,
            improvement_suggestions=improvement_suggestions,
            assessment_date=datetime.now(),
            version_info=version_info
        )

    def export_result_to_json(self, result: QualityAssessmentResult, output_path: str):
        """将评估结果导出为JSON文件"""
        # 转换为可序列化的格式
        serializable_result = {
            "document_metadata": {
                "file_path": result.document_metadata.file_path,
                "file_name": result.document_metadata.file_name,
                "file_size": result.document_metadata.file_size,
                "creation_date": result.document_metadata.creation_date.isoformat() if result.document_metadata.creation_date else None,
                "modification_date": result.document_metadata.modification_date.isoformat() if result.document_metadata.modification_date else None,
                "document_hash": result.document_metadata.document_hash,
                "encoding": result.document_metadata.encoding
            },
            "document_type": result.document_type.value,
            "overall_score": result.overall_score,
            "quality_level": result.quality_level.value,
            "dimensions": {
                name: {
                    "name": dim.name,
                    "weight": dim.weight,
                    "score": dim.score,
                    "max_score": dim.max_score,
                    "issues": dim.issues,
                    "suggestions": dim.suggestions
                } for name, dim in result.dimensions.items()
            },
            "critical_issues": result.critical_issues,
            "improvement_suggestions": result.improvement_suggestions,
            "assessment_date": result.assessment_date.isoformat(),
            "version_info": result.version_info
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_result, f, ensure_ascii=False, indent=2)

    def generate_summary_report(self, results: List[QualityAssessmentResult]) -> str:
        """生成汇总报告"""
        total_docs = len(results)
        avg_score = sum(r.overall_score for r in results) / total_docs if total_docs > 0 else 0

        # 按质量等级统计
        quality_counts = {level.value: 0 for level in QualityLevel}
        for result in results:
            quality_counts[result.quality_level.value] += 1

        # 按文档类型统计
        type_counts = {doc_type.value: 0 for doc_type in DocumentType}
        type_scores = {doc_type.value: [] for doc_type in DocumentType}
        for result in results:
            type_counts[result.document_type.value] += 1
            type_scores[result.document_type.value].append(result.overall_score)

        # 计算各类型平均分
        type_avg_scores = {}
        for doc_type, scores in type_scores.items():
            if scores:
                type_avg_scores[doc_type] = sum(scores) / len(scores)
            else:
                type_avg_scores[doc_type] = 0

        report = f"""
# DAIP-LIVE 规范化文档质量评估汇总报告

## 总体概况
- **评估文档总数**: {total_docs}
- **平均质量得分**: {avg_score:.2f}/100
- **评估完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 质量等级分布
- **优秀 (90-100分)**: {quality_counts['excellent']} 份 ({quality_counts['excellent']/total_docs*100:.1f}%)
- **良好 (80-89分)**: {quality_counts['good']} 份 ({quality_counts['good']/total_docs*100:.1f}%)
- **一般 (70-79分)**: {quality_counts['average']} 份 ({quality_counts['average']/total_docs*100:.1f}%)
- **较差 (60-69分)**: {quality_counts['poor']} 份 ({quality_counts['poor']/total_docs*100:.1f}%)
- **严重问题 (0-59分)**: {quality_counts['critical']} 份 ({quality_counts['critical']/total_docs*100:.1f}%)

## 文档类型分布及平均分
"""
        for doc_type in DocumentType:
            count = type_counts[doc_type.value]
            avg_score = type_avg_scores[doc_type.value]
            report += f"- **{doc_type.value}**: {count} 份，平均分 {avg_score:.2f}\n"

        # 找出最佳和最差文档
        if results:
            best_doc = max(results, key=lambda r: r.overall_score)
            worst_doc = min(results, key=lambda r: r.overall_score)

            report += f"""
## 质量 extremes
- **最佳文档**: {best_doc.document_metadata.file_name} ({best_doc.overall_score:.2f}分)
- **最差文档**: {worst_doc.document_metadata.file_name} ({worst_doc.overall_score:.2f}分)

## 主要问题汇总
"""
            # 统计最常见的问题
            all_issues = []
            for result in results:
                all_issues.extend(result.critical_issues)

            issue_counts = {}
            for issue in all_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

            top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            for i, (issue, count) in enumerate(top_issues, 1):
                report += f"{i}. {issue} (出现{count}次)\n"

        return report


def main():
    """主函数 - 批量评估文档"""
    import sys

    if len(sys.argv) < 3:
        print("用法: python document_quality_assessor.py <输入目录> <输出目录>")
        return

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    assessor = DocumentQualityAssessor()

    # 查找所有markdown文档
    doc_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(('.md', '.MD')):
                doc_files.append(os.path.join(root, file))

    print(f"找到 {len(doc_files)} 份文档，开始质量评估...")

    results = []
    for i, file_path in enumerate(doc_files, 1):
        print(f"[{i}/{len(doc_files)}] 评估: {os.path.relpath(file_path, input_dir)}")
        try:
            result = assessor.assess_document(file_path)
            results.append(result)

            # 导出单个结果
            output_file = os.path.join(
                output_dir,
                f"{os.path.splitext(os.path.basename(file_path))[0]}_quality_assessment.json"
            )
            assessor.export_result_to_json(result, output_file)

        except Exception as e:
            print(f"评估失败 {file_path}: {e}")

    # 生成汇总报告
    if results:
        summary_report = assessor.generate_summary_report(results)

        # 保存汇总报告
        summary_file = os.path.join(output_dir, "quality_assessment_summary.md")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_report)

        print(f"\n评估完成！")
        print(f"汇总报告: {summary_file}")
        print(f"详细结果: {output_dir}")
    else:
        print("没有成功评估任何文档")


if __name__ == "__main__":
    main()