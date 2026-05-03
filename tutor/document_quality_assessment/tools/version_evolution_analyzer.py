#!/usr/bin/env python3
"""
DAIP-LIVE 文档版本演化分析器
分析文档的版本历史、演化趋势和质量变化
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from document_discoverer import DocumentInfo
from document_quality_assessor import DocumentQualityAssessor, QualityAssessmentResult


class VersionEvolutionAnalyzer:
    """版本演化分析器"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.version_patterns = [
            r'v?(\d+\.\d+(?:\.\d+)?)',
            r'版本[：:]\s*(\d+\.\d+(?:\.\d+)?)',
            r'version[：:]\s*(\d+\.\d+(?:\.\d+)?)',
            r'Version[：:]\s*(\d+\.\d+(?:\.\d+)?)'
        ]

    def extract_version_from_content(self, content: str) -> Optional[str]:
        """从内容中提取版本信息"""
        for pattern in self.version_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def extract_version_from_filename(self, filename: str) -> Optional[str]:
        """从文件名中提取版本信息"""
        version_match = re.search(r'v?(\d+\.\d+(?:\.\d+)?)', filename)
        return version_match.group(1) if version_match else None

    def group_documents_by_base_name(self, documents: List[DocumentInfo]) -> Dict[str, List[DocumentInfo]]:
        """根据基础名称分组文档（识别同一文档的不同版本）"""
        groups = defaultdict(list)

        for doc in documents:
            # 移除版本号和日期后缀，提取基础名称
            base_name = doc.file_name

            # 移除常见的版本模式
            base_name = re.sub(r'_v\d+(\.\d+)*', '', base_name)
            base_name = re.sub(r'_version\d+(\.\d+)*', '', base_name, re.IGNORECASE)
            base_name = re.sub(r'_\d{8}', '', base_name)  # 移除日期后缀
            base_name = re.sub(r'_\d{4}-\d{2}-\d{2}', '', base_name)

            # 移除常见的后缀
            base_name = re.sub(r'_(final|latest|current|old|backup|draft)$', '', base_name, re.IGNORECASE)

            groups[base_name].append(doc)

        return dict(groups)

    def analyze_version_evolution(self, documents: List[DocumentInfo]) -> Dict:
        """分析版本演化"""
        evolution_data = {
            "document_families": {},
            "version_statistics": {},
            "quality_evolution": {},
            "timeline_analysis": {}
        }

        # 按基础名称分组
        doc_groups = self.group_documents_by_base_name(documents)

        for base_name, doc_versions in doc_groups.items():
            if len(doc_versions) <= 1:
                continue  # 跳过单版本文档

            family_data = {
                "base_name": base_name,
                "versions": [],
                "version_count": len(doc_versions),
                "time_span_days": 0,
                "evolution_pattern": "unknown"
            }

            # 处理每个版本
            version_info_list = []
            for doc in doc_versions:
                # 从内容和文件名提取版本信息
                content_version = None
                try:
                    with open(doc.file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        content_version = self.extract_version_from_content(content)
                except:
                    pass

                filename_version = self.extract_version_from_filename(doc.file_name)
                version = content_version or filename_version or "unknown"

                version_info = {
                    "version": version,
                    "file_name": doc.file_name,
                    "file_path": doc.file_path,
                    "modification_date": doc.modification_date.isoformat(),
                    "file_size": doc.file_size,
                    "version_source": "content" if content_version else "filename" if filename_version else "unknown"
                }

                version_info_list.append(version_info)

            # 按日期排序版本
            version_info_list.sort(key=lambda x: x["modification_date"])

            family_data["versions"] = version_info_list

            # 计算时间跨度
            if len(version_info_list) >= 2:
                first_date = datetime.fromisoformat(version_info_list[0]["modification_date"])
                last_date = datetime.fromisoformat(version_info_list[-1]["modification_date"])
                family_data["time_span_days"] = (last_date - first_date).days

                # 分析演化模式
                family_data["evolution_pattern"] = self._analyze_evolution_pattern(version_info_list)

            evolution_data["document_families"][base_name] = family_data

        # 统计版本信息
        evolution_data["version_statistics"] = self._calculate_version_statistics(evolution_data["document_families"])

        return evolution_data

    def _analyze_evolution_pattern(self, version_info_list: List[Dict]) -> str:
        """分析版本演化模式"""
        if len(version_info_list) < 2:
            return "single_version"

        versions = [v["version"] for v in version_info_list if v["version"] != "unknown"]

        if not versions:
            return "unversioned"

        # 检查版本号规律
        try:
            # 提取主版本号
            major_versions = []
            for version in versions:
                if '.' in version:
                    major_versions.append(int(version.split('.')[0]))

            if len(set(major_versions)) == 1:
                return "minor_updates"  # 只有次版本号变化
            elif len(set(major_versions)) > 1:
                return "major_updates"  # 有主版本号变化
            else:
                return "incremental"  # 增量更新
        except:
            return "irregular"

    def _calculate_version_statistics(self, document_families: Dict) -> Dict:
        """计算版本统计信息"""
        stats = {
            "total_families": len(document_families),
            "total_versions": sum(family["version_count"] for family in document_families.values()),
            "average_versions_per_family": 0,
            "evolution_patterns": {},
            "time_span_distribution": {
                "short_term": 0,    # < 7 days
                "medium_term": 0,   # 7-30 days
                "long_term": 0      # > 30 days
            }
        }

        if stats["total_families"] > 0:
            stats["average_versions_per_family"] = stats["total_versions"] / stats["total_families"]

        # 统计演化模式
        for family in document_families.values():
            pattern = family["evolution_pattern"]
            stats["evolution_patterns"][pattern] = stats["evolution_patterns"].get(pattern, 0) + 1

            # 统计时间跨度
            time_span = family["time_span_days"]
            if time_span < 7:
                stats["time_span_distribution"]["short_term"] += 1
            elif time_span <= 30:
                stats["time_span_distribution"]["medium_term"] += 1
            else:
                stats["time_span_distribution"]["long_term"] += 1

        return stats

    def analyze_quality_evolution(self, documents: List[DocumentInfo], quality_results: List[QualityAssessmentResult]) -> Dict:
        """分析质量演化趋势"""
        quality_evolution = {
            "quality_trends": {},
            "improvement_patterns": {},
            "quality_metrics": {}
        }

        # 创建文件路径到质量结果的映射
        quality_map = {result.document_metadata.file_path: result for result in quality_results}

        # 按基础名称分组并分析质量趋势
        doc_groups = self.group_documents_by_base_name(documents)

        for base_name, doc_versions in doc_groups.items():
            if len(doc_versions) <= 1:
                continue

            # 获取质量结果
            version_qualities = []
            for doc in doc_versions:
                quality_result = quality_map.get(doc.file_path)
                if quality_result:
                    version_qualities.append({
                        "version": self.extract_version_from_filename(doc.file_name) or "unknown",
                        "date": doc.modification_date,
                        "score": quality_result.overall_score,
                        "quality_level": quality_result.quality_level.value,
                        "file_name": doc.file_name
                    })

            if len(version_qualities) <= 1:
                continue

            # 按日期排序
            version_qualities.sort(key=lambda x: x["date"])

            # 分析质量趋势
            trend_data = {
                "base_name": base_name,
                "versions": version_qualities,
                "trend": "stable",
                "improvement_rate": 0,
                "score_change": 0
            }

            if len(version_qualities) >= 2:
                first_score = version_qualities[0]["score"]
                last_score = version_qualities[-1]["score"]
                trend_data["score_change"] = last_score - first_score
                trend_data["improvement_rate"] = ((last_score - first_score) / first_score * 100) if first_score > 0 else 0

                if trend_data["score_change"] > 5:
                    trend_data["trend"] = "improving"
                elif trend_data["score_change"] < -5:
                    trend_data["trend"] = "declining"
                else:
                    trend_data["trend"] = "stable"

            quality_evolution["quality_trends"][base_name] = trend_data

        # 计算整体质量指标
        all_trends = quality_evolution["quality_trends"]
        if all_trends:
            improving_count = sum(1 for t in all_trends.values() if t["trend"] == "improving")
            declining_count = sum(1 for t in all_trends.values() if t["trend"] == "declining")
            stable_count = sum(1 for t in all_trends.values() if t["trend"] == "stable")

            quality_evolution["quality_metrics"] = {
                "total_analyzed_families": len(all_trends),
                "improving_families": improving_count,
                "declining_families": declining_count,
                "stable_families": stable_count,
                "average_improvement_rate": sum(t["improvement_rate"] for t in all_trends.values()) / len(all_trends)
            }

        return quality_evolution

    def analyze_timeline_evolution(self, documents: List[DocumentInfo]) -> Dict:
        """分析时间线演化"""
        timeline_data = {
            "monthly_activity": {},
            "peak_periods": [],
            "development_phases": {},
            "document_creation_trends": {}
        }

        # 按月统计文档创建活动
        monthly_counts = defaultdict(int)
        monthly_sizes = defaultdict(int)

        for doc in documents:
            date = doc.modification_date
            month_key = date.strftime("%Y-%m")
            monthly_counts[month_key] += 1
            monthly_sizes[month_key] += doc.file_size

        # 计算平均值
        for month in monthly_counts:
            timeline_data["monthly_activity"][month] = {
                "document_count": monthly_counts[month],
                "total_size": monthly_sizes[month],
                "average_size": monthly_sizes[month] / monthly_counts[month]
            }

        # 识别高峰期
        sorted_months = sorted(monthly_counts.items(), key=lambda x: x[1], reverse=True)
        if sorted_months:
            avg_count = sum(monthly_counts.values()) / len(monthly_counts)
            timeline_data["peak_periods"] = [
                {"month": month, "count": count, "is_peak": count > avg_count * 1.5}
                for month, count in sorted_months[:10]
            ]

        return timeline_data

    def generate_evolution_report(self, documents: List[DocumentInfo], quality_results: List[QualityAssessmentResult] = None) -> str:
        """生成版本演化报告"""
        # 分析版本演化
        version_evolution = self.analyze_version_evolution(documents)

        # 分析质量演化
        quality_evolution = {}
        if quality_results:
            quality_evolution = self.analyze_quality_evolution(documents, quality_results)

        # 分析时间线演化
        timeline_evolution = self.analyze_timeline_evolution(documents)

        # 生成报告
        report = f"""# DAIP-LIVE 文档版本演化分析报告

## 分析概述

- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **文档总数**: {len(documents)}
- **多版本文档族**: {version_evolution['version_statistics']['total_families']}
- **总版本数**: {version_evolution['version_statistics']['total_versions']}

## 版本演化统计

### 基本统计
- **平均每文档族版本数**: {version_evolution['version_statistics']['average_versions_per_family']:.2f}
- **演化模式分布**:
"""

        # 添加演化模式统计
        for pattern, count in version_evolution['version_statistics']['evolution_patterns'].items():
            percentage = count / version_evolution['version_statistics']['total_families'] * 100 if version_evolution['version_statistics']['total_families'] > 0 else 0
            report += f"  - **{pattern}**: {count} 个文档族 ({percentage:.1f}%)\n"

        # 添加时间跨度分布
        report += f"\n### 时间跨度分布\n"
        time_dist = version_evolution['version_statistics']['time_span_distribution']
        total_families = version_evolution['version_statistics']['total_families']
        report += f"- **短期演化** (<7天): {time_dist['short_term']} 个文档族 ({time_dist['short_term']/total_families*100:.1f}%)\n"
        report += f"- **中期演化** (7-30天): {time_dist['medium_term']} 个文档族 ({time_dist['medium_term']/total_families*100:.1f}%)\n"
        report += f"- **长期演化** (>30天): {time_dist['long_term']} 个文档族 ({time_dist['long_term']/total_families*100:.1f}%)\n"

        # 添加重要文档族分析
        report += f"\n## 重要文档族分析\n\n"
        significant_families = sorted(
            version_evolution['document_families'].items(),
            key=lambda x: x[1]['version_count'],
            reverse=True
        )[:10]

        for base_name, family_data in significant_families:
            report += f"### {base_name}\n"
            report += f"- **版本数**: {family_data['version_count']}\n"
            report += f"- **时间跨度**: {family_data['time_span_days']} 天\n"
            report += f"- **演化模式**: {family_data['evolution_pattern']}\n"

            # 添加版本列表
            if len(family_data['versions']) <= 5:
                report += "- **版本历史**:\n"
                for version in family_data['versions']:
                    date_str = datetime.fromisoformat(version['modification_date']).strftime('%Y-%m-%d')
                    report += f"  - v{version['version']} ({date_str}) - {version['file_name']}\n"

            report += "\n"

        # 添加质量演化分析
        if quality_evolution and quality_evolution.get('quality_metrics'):
            metrics = quality_evolution['quality_metrics']
            report += f"## 质量演化分析\n\n"
            report += f"### 质量趋势概览\n"
            report += f"- **分析的文档族**: {metrics['total_analyzed_families']}\n"
            report += f"- **质量提升**: {metrics['improving_families']} 个\n"
            report += f"- **质量下降**: {metrics['declining_families']} 个\n"
            report += f"- **质量稳定**: {metrics['stable_families']} 个\n"
            report += f"- **平均改进率**: {metrics['average_improvement_rate']:.2f}%\n\n"

            # 添加显著质量变化案例
            improving_cases = sorted(
                [t for t in quality_evolution['quality_trends'].values() if t['trend'] == 'improving'],
                key=lambda x: x['improvement_rate'],
                reverse=True
            )[:5]

            if improving_cases:
                report += "### 显著质量提升案例\n"
                for case in improving_cases:
                    report += f"- **{case['base_name']}**: 提升 {case['improvement_rate']:.1f}% "
                    report += f"({case['versions'][0]['score']:.1f} → {case['versions'][-1]['score']:.1f}分)\n"

        # 添加时间线分析
        if timeline_evolution.get('monthly_activity'):
            report += f"\n## 时间线演化分析\n\n"
            report += "### 月度活动统计\n"

            # 按时间排序的月度数据
            sorted_months = sorted(timeline_evolution['monthly_activity'].items())

            for month, data in sorted_months[-12:]:  # 最近12个月
                report += f"- **{month}**: {data['document_count']} 个文档, "
                report += f"平均大小 {data['average_size']:.0f} 字节\n"

            # 添加高峰期分析
            if timeline_evolution.get('peak_periods'):
                report += f"\n### 开发高峰期\n"
                peak_periods = [p for p in timeline_evolution['peak_periods'] if p['is_peak']]
                if peak_periods:
                    report += "识别到的高峰开发期:\n"
                    for period in peak_periods[:5]:
                        report += f"- **{period['month']}**: {period['count']} 个文档\n"

        # 添加建议和结论
        report += f"\n## 总结与建议\n\n"

        report += "### 主要发现\n"
        report += f"1. **版本管理成熟度**: {version_evolution['version_statistics']['total_families']} 个文档族中，"
        report += f"平均每个有 {version_evolution['version_statistics']['average_versions_per_family']:.1f} 个版本\n"

        if quality_evolution.get('quality_metrics'):
            total_analyzed = quality_evolution['quality_metrics']['total_analyzed_families']
            if total_analyzed > 0:
                improving_pct = quality_evolution['quality_metrics']['improving_families'] / total_analyzed * 100
                report += f"2. **质量改进趋势**: {improving_pct:.1f}% 的文档族显示质量提升\n"

        report += "\n### 改进建议\n"
        report += "1. **版本标准化**: 建立统一的版本命名规范，提高版本识别准确性\n"
        report += "2. **变更跟踪**: 完善版本变更记录，便于理解演化过程\n"
        report += "3. **质量监控**: 建立文档质量监控机制，确保版本迭代不降低质量\n"
        report += "4. **演化模式优化**: 分析成功的演化模式，指导后续文档维护策略\n"

        return report


def main():
    """主函数"""
    import sys

    if len(sys.argv) < 3:
        print("用法: python version_evolution_analyzer.py <项目根目录> <输出目录>")
        return

    project_root = sys.argv[1]
    output_dir = sys.argv[2]

    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 读取精炼的文档列表
    filtered_docs_file = Path(project_root) / "tutor/document_quality_assessment/filtered_documents_sorted_by_date.json"

    if not filtered_docs_file.exists():
        print(f"找不到精炼文档列表: {filtered_docs_file}")
        return

    with open(filtered_docs_file, 'r', encoding='utf-8') as f:
        filtered_docs = json.load(f)

    # 转换为DocumentInfo对象
    documents = []
    for doc_data in filtered_docs:
        # 确保所有必需字段存在
        file_hash = doc_data.get("document_hash", "")
        version_info = doc_data.get("version_info", {})
        content_preview = doc_data.get("content_preview", "")

        doc_info = DocumentInfo(
            file_path=doc_data["file_path"],
            file_name=doc_data["file_name"],
            relative_path=doc_data["relative_path"],
            file_size=doc_data["file_size"],
            creation_date=datetime.fromisoformat(doc_data["creation_date"]),
            modification_date=datetime.fromisoformat(doc_data["modification_date"]),
            file_hash=file_hash,
            document_type=doc_data["document_type"],
            priority_level=doc_data["priority_level"],
            version_info=version_info,
            content_preview=content_preview
        )
        documents.append(doc_info)

    # 创建分析器
    analyzer = VersionEvolutionAnalyzer(project_root)

    print("开始版本演化分析...")

    # 生成演化报告
    evolution_report = analyzer.generate_evolution_report(documents)

    # 保存报告
    report_file = Path(output_dir) / "version_evolution_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(evolution_report)

    # 执行详细分析
    version_evolution = analyzer.analyze_version_evolution(documents)
    evolution_data_file = Path(output_dir) / "version_evolution_data.json"
    with open(evolution_data_file, 'w', encoding='utf-8') as f:
        json.dump(version_evolution, f, ensure_ascii=False, indent=2, default=str)

    print(f"版本演化分析完成！")
    print(f"- 演化报告: {report_file}")
    print(f"- 详细数据: {evolution_data_file}")


if __name__ == "__main__":
    main()