#!/usr/bin/env python3
"""
DAIP-LIVE 批量质量评估器
使用精炼的文档列表进行质量评估
"""

import json
import os
from pathlib import Path
from document_quality_assessor import DocumentQualityAssessor


def main():
    """主函数 - 批量评估精炼的文档"""
    project_root = "."
    base_dir = Path(project_root)
    filtered_docs_file = base_dir / "tutor/document_quality_assessment/filtered_documents_sorted_by_date.json"
    output_dir = base_dir / "tutor/document_quality_assessment/automated_analysis"

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 读取精炼的文档列表
    if not filtered_docs_file.exists():
        print(f"找不到精炼文档列表: {filtered_docs_file}")
        print("请先运行 filtered_document_discoverer.py")
        return

    with open(filtered_docs_file, 'r', encoding='utf-8') as f:
        filtered_docs = json.load(f)

    print(f"开始评估 {len(filtered_docs)} 份精炼规范文档...")

    assessor = DocumentQualityAssessor()
    results = []

    for i, doc_info in enumerate(filtered_docs, 1):
        file_path = doc_info["file_path"]
        relative_path = doc_info["relative_path"]
        file_name = doc_info["file_name"]

        print(f"[{i}/{len(filtered_docs)}] 评估: {relative_path}")

        try:
            # 检查文件是否存在
            if not Path(file_path).exists():
                print(f"文件不存在，跳过: {relative_path}")
                continue

            result = assessor.assess_document(file_path)
            results.append(result)

            # 导出单个结果
            safe_name = file_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_')
            output_file = output_dir / f"{safe_name}_quality_assessment.json"
            assessor.export_result_to_json(result, str(output_file))

        except Exception as e:
            print(f"评估失败 {relative_path}: {e}")
            continue

    # 生成汇总报告
    if results:
        summary_report = assessor.generate_summary_report(results)

        # 保存汇总报告
        summary_file = output_dir / "quality_assessment_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_report)

        # 生成质量排名
        results_by_quality = sorted(results, key=lambda r: r.overall_score, reverse=True)
        quality_ranking_file = output_dir / "quality_ranking.json"

        ranking_data = {
            "total_documents": len(results),
            "assessment_date": results[0].assessment_date.isoformat() if results else None,
            "average_score": sum(r.overall_score for r in results) / len(results) if results else 0,
            "rankings": []
        }

        for rank, result in enumerate(results_by_quality, 1):
            ranking_entry = {
                "rank": rank,
                "file_name": result.document_metadata.file_name,
                "file_path": result.document_metadata.file_path,
                "overall_score": result.overall_score,
                "quality_level": result.quality_level.value,
                "document_type": result.document_type.value
            }
            ranking_data["rankings"].append(ranking_entry)

        with open(quality_ranking_file, 'w', encoding='utf-8') as f:
            json.dump(ranking_data, f, ensure_ascii=False, indent=2)

        # 生成问题汇总
        all_issues = []
        quality_level_counts = {"excellent": 0, "good": 0, "average": 0, "poor": 0, "critical": 0}

        for result in results:
            all_issues.extend(result.critical_issues)
            quality_level_counts[result.quality_level.value] += 1

        # 统计最常见的问题
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:20]

        issues_summary = {
            "total_issues": len(all_issues),
            "unique_issues": len(issue_counts),
            "quality_distribution": quality_level_counts,
            "top_issues": [{"issue": issue, "count": count} for issue, count in top_issues]
        }

        issues_summary_file = output_dir / "issues_summary.json"
        with open(issues_summary_file, 'w', encoding='utf-8') as f:
            json.dump(issues_summary, f, ensure_ascii=False, indent=2)

        print(f"\n质量评估完成！")
        print(f"- 成功评估 {len(results)} 份文档")
        print(f"- 汇总报告: {summary_file}")
        print(f"- 质量排名: {quality_ranking_file}")
        print(f"- 问题汇总: {issues_summary_file}")
        print(f"- 详细结果: {output_dir}")

        # 显示统计信息
        avg_score = sum(r.overall_score for r in results) / len(results)
        print(f"\n质量统计:")
        print(f"  平均得分: {avg_score:.2f}/100")
        print(f"  优秀文档: {quality_level_counts['excellent']} 份")
        print(f"  良好文档: {quality_level_counts['good']} 份")
        print(f"  一般文档: {quality_level_counts['average']} 份")
        print(f"  较差文档: {quality_level_counts['poor']} 份")
        print(f"  严重问题: {quality_level_counts['critical']} 份")

        # 显示最佳和最差文档
        if results_by_quality:
            best_doc = results_by_quality[0]
            worst_doc = results_by_quality[-1]
            print(f"\n最佳文档:")
            print(f"  {best_doc.document_metadata.file_name} ({best_doc.overall_score:.2f}分)")
            print(f"\n最需要改进的文档:")
            print(f"  {worst_doc.document_metadata.file_name} ({worst_doc.overall_score:.2f}分)")

        # 显示最常见的问题
        print(f"\n最常见的问题 (Top 5):")
        for i, (issue, count) in enumerate(top_issues[:5], 1):
            print(f"  {i}. {issue} (出现{count}次)")

    else:
        print("没有成功评估任何文档")


if __name__ == "__main__":
    main()