"""Schema智能推荐系统
基于现有schema库和LLM推理的输出schema自动推荐功能
"""

import json
from pathlib import Path
from typing import Any, Optional


class SchemaRecommender:
    """Schema智能推荐系统

    基于任务类型、阶段目标和现有schema库，智能推荐最合适的输出schema
    """

    def __init__(self):
        """初始化Schema推荐系统"""
        self.schema_library = self._load_schema_library()
        self.schema_patterns = self._build_schema_patterns()

    def _load_schema_library(self) -> dict[str, dict[str, Any]]:
        """加载现有schema库"""
        schema_library = {}

        # 扫描schemas目录
        schemas_dir = Path("daip-insight-engine/schemas")
        if schemas_dir.exists():
            for domain_dir in schemas_dir.iterdir():
                if domain_dir.is_dir():
                    domain_name = domain_dir.name
                    schema_library[domain_name] = {}

                    for schema_file in domain_dir.glob("*.json"):
                        schema_name = schema_file.stem
                        try:
                            with open(schema_file, encoding="utf-8") as f:
                                schema_content = json.load(f)
                                schema_library[domain_name][schema_name] = {
                                    "path": f"src.schemas.{domain_name}.{schema_name}",
                                    "content": schema_content,
                                    "file_path": str(schema_file),
                                }
                        except Exception as e:
                            print(f"加载schema文件失败 {schema_file}: {e}")

        # 添加预定义的schema库
        predefined_schemas = {
            "financial": {
                "FinancialMetrics": {
                    "path": "src.schemas.financial.FinancialMetrics",
                    "description": "财务指标数据结构",
                    "fields": [
                        "revenue",
                        "profit",
                        "cash_flow",
                        "assets",
                        "liabilities",
                    ],
                },
                "FinancialSummary": {
                    "path": "src.schemas.financial.FinancialSummary",
                    "description": "财务分析摘要",
                    "fields": ["summary", "key_metrics", "trends", "recommendations"],
                },
                "BalanceSheet": {
                    "path": "src.schemas.financial.BalanceSheet",
                    "description": "资产负债表",
                    "fields": ["assets", "liabilities", "equity", "date"],
                },
            },
            "academic": {
                "PaperContent": {
                    "path": "src.schemas.academic.PaperContent",
                    "description": "论文内容结构",
                    "fields": [
                        "title",
                        "abstract",
                        "methodology",
                        "results",
                        "conclusions",
                    ],
                },
                "PaperSummary": {
                    "path": "src.schemas.academic.PaperSummary",
                    "description": "论文摘要",
                    "fields": [
                        "summary",
                        "key_contributions",
                        "methodology",
                        "limitations",
                    ],
                },
                "KeyPoints": {
                    "path": "src.schemas.academic.KeyPoints",
                    "description": "关键点提取",
                    "fields": [
                        "main_points",
                        "innovations",
                        "contributions",
                        "implications",
                    ],
                },
            },
            "market": {
                "MarketData": {
                    "path": "src.schemas.market.MarketData",
                    "description": "市场数据",
                    "fields": ["market_size", "growth_rate", "segments", "competitors"],
                },
                "TrendAnalysis": {
                    "path": "src.schemas.market.TrendAnalysis",
                    "description": "趋势分析",
                    "fields": ["trends", "drivers", "challenges", "opportunities"],
                },
                "CompetitiveAnalysis": {
                    "path": "src.schemas.market.CompetitiveAnalysis",
                    "description": "竞争分析",
                    "fields": [
                        "competitors",
                        "strengths",
                        "weaknesses",
                        "market_position",
                    ],
                },
            },
            "general": {
                "KeyInformation": {
                    "path": "src.schemas.general.KeyInformation",
                    "description": "关键信息提取",
                    "fields": ["key_points", "entities", "relationships", "metadata"],
                },
                "AnalysisReport": {
                    "path": "src.schemas.general.AnalysisReport",
                    "description": "分析报告",
                    "fields": ["summary", "findings", "recommendations", "appendix"],
                },
                "EntityCount": {
                    "path": "src.schemas.general.EntityCount",
                    "description": "实体计数",
                    "fields": ["entity_type", "count", "details"],
                },
            },
        }

        # 合并预定义schema
        for domain, schemas in predefined_schemas.items():
            if domain not in schema_library:
                schema_library[domain] = {}
            schema_library[domain].update(schemas)

        return schema_library

    def _build_schema_patterns(self) -> dict[str, list[str]]:
        """构建schema模式匹配规则"""
        patterns = {
            # 财务相关关键词
            "financial": [
                "财务",
                "财报",
                "financial",
                "revenue",
                "profit",
                "cash",
                "balance",
                "income",
                "statement",
                "资产",
                "负债",
                "利润",
                "收入",
                "现金流",
            ],
            # 学术相关关键词
            "academic": [
                "论文",
                "paper",
                "research",
                "study",
                "academic",
                "scholar",
                "publication",
                "研究",
                "学术",
                "文献",
                "期刊",
                "会议",
                "citation",
                "abstract",
            ],
            # 市场相关关键词
            "market": [
                "市场",
                "market",
                "competition",
                "competitor",
                "trend",
                "analysis",
                "竞争",
                "趋势",
                "调研",
                "survey",
                "customer",
                "segment",
                "strategy",
            ],
            # 通用关键词
            "general": [
                "分析",
                "analysis",
                "report",
                "summary",
                "information",
                "data",
                "extract",
                "count",
                "classify",
                "summarize",
                "key",
                "important",
            ],
        }
        return patterns

    def recommend_schema(
        self,
        stage_name: str,
        role: str,
        prompt_template: str,
        task_context: str = "",
    ) -> tuple[str, float]:
        """推荐最合适的schema

        Args:
        ----
            stage_name: 阶段名称
            role: 角色描述
            prompt_template: 提示模板
            task_context: 任务上下文

        Returns:
        -------
            推荐的schema路径和置信度分数

        """
        # 合并所有文本用于分析
        combined_text = f"{stage_name} {role} {prompt_template} {task_context}".lower()

        # 计算每个领域的匹配分数
        domain_scores = {}
        for domain, keywords in self.schema_patterns.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                domain_scores[domain] = score / len(keywords)  # 归一化分数

        if not domain_scores:
            # 如果没有匹配，返回通用schema
            return "src.schemas.general.AnalysisReport", 0.5

        # 找到最高分的领域
        best_domain = max(domain_scores.keys(), key=lambda x: domain_scores[x])
        best_score = domain_scores[best_domain]

        # 在最佳领域中选择最合适的schema
        if best_domain in self.schema_library:
            schema_scores = {}
            for schema_name, schema_info in self.schema_library[best_domain].items():
                # 基于阶段名称和角色匹配schema
                schema_score = self._calculate_schema_score(
                    stage_name,
                    role,
                    prompt_template,
                    schema_name,
                    schema_info,
                )
                schema_scores[schema_name] = schema_score

            if schema_scores:
                best_schema = max(schema_scores.keys(), key=lambda x: schema_scores[x])
                schema_path = self.schema_library[best_domain][best_schema]["path"]
                return schema_path, min(best_score + schema_scores[best_schema], 1.0)

        # 回退到领域默认schema
        default_schemas = {
            "financial": "src.schemas.financial.FinancialMetrics",
            "academic": "src.schemas.academic.PaperContent",
            "market": "src.schemas.market.MarketData",
            "general": "src.schemas.general.KeyInformation",
        }

        return (
            default_schemas.get(best_domain, "src.schemas.general.AnalysisReport"),
            best_score,
        )

    def _calculate_schema_score(
        self,
        stage_name: str,
        role: str,
        prompt_template: str,
        schema_name: str,
        schema_info: dict[str, Any],
    ) -> float:
        """计算schema匹配分数"""
        score = 0.0

        # 基于schema名称匹配
        if any(word in stage_name.lower() for word in schema_name.lower().split()):
            score += 0.3

        # 基于角色匹配
        if "description" in schema_info:
            if any(
                word in role.lower()
                for word in schema_info["description"].lower().split()
            ):
                score += 0.2

        # 基于字段匹配
        if "fields" in schema_info:
            prompt_lower = prompt_template.lower()
            field_matches = sum(
                1 for field in schema_info["fields"] if field in prompt_lower
            )
            score += (field_matches / len(schema_info["fields"])) * 0.3

        # 基于特定模式匹配
        pattern_matches = {
            "extract": ["Content", "Data", "Information", "Metrics"],
            "analyze": ["Analysis", "Report", "Summary"],
            "generate": ["Summary", "Report", "Recommendations"],
            "count": ["Count", "Statistics", "Metrics"],
        }

        stage_lower = stage_name.lower()
        for pattern, preferred_schemas in pattern_matches.items():
            if pattern in stage_lower:
                if any(preferred in schema_name for preferred in preferred_schemas):
                    score += 0.2
                break

        return score

    def get_available_schemas(
        self,
        domain: Optional[str] = None,
    ) -> dict[str, list[str]]:
        """获取可用的schema列表"""
        if domain:
            return {domain: list(self.schema_library.get(domain, {}).keys())}
        else:
            return {
                domain: list(schemas.keys())
                for domain, schemas in self.schema_library.items()
            }

    def create_custom_schema_suggestion(
        self,
        stage_name: str,
        role: str,
        prompt_template: str,
    ) -> dict[str, Any]:
        """为新的需求创建自定义schema建议"""
        # 分析需求，生成schema建议
        stage_lower = stage_name.lower()

        # 确定schema类型
        if "extract" in stage_lower:
            schema_type = "extraction"
            suggested_fields = ["extracted_data", "entities", "metadata"]
        elif "analyze" in stage_lower:
            schema_type = "analysis"
            suggested_fields = ["analysis_results", "insights", "recommendations"]
        elif "generate" in stage_lower or "create" in stage_lower:
            schema_type = "generation"
            suggested_fields = ["generated_content", "summary", "key_points"]
        elif "count" in stage_lower or "statistics" in stage_lower:
            schema_type = "statistics"
            suggested_fields = ["counts", "statistics", "breakdown"]
        else:
            schema_type = "general"
            suggested_fields = ["results", "data", "metadata"]

        # 生成schema名称
        stage_words = [
            word.capitalize() for word in stage_name.split("_") if word.upper() != word
        ]
        schema_name = "".join(stage_words) + "Result"

        # 确定领域
        domain = "custom"
        for domain_name, keywords in self.schema_patterns.items():
            if any(keyword in prompt_template.lower() for keyword in keywords):
                domain = domain_name
                break

        schema_path = f"src.schemas.{domain}.{schema_name}"

        return {
            "schema_path": schema_path,
            "schema_name": schema_name,
            "domain": domain,
            "type": schema_type,
            "suggested_fields": suggested_fields,
            "description": f"Schema for {stage_name} stage results",
        }


# 创建全局实例
schema_recommender = SchemaRecommender()
