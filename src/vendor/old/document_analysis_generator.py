"""文档分析协议生成器
专门用于财务分析、合同审查等被动文档处理任务
"""

from typing import Any


class DocumentAnalysisGenerator:
    """文档分析协议生成器

    专门处理财务分析、合同审查、文献综述等被动分析任务
    采用"信息提取、结构化分析、报告生成"的流程设计
    """

    def __init__(self):
        """初始化文档分析协议生成器"""
        self.analysis_templates = self._load_analysis_templates()
        self.analysis_experts = self._load_analysis_experts()

    def _load_analysis_templates(self) -> dict[str, dict[str, Any]]:
        """加载文档分析模板"""
        return {
            "financial_analysis": {
                "name": "财务分析",
                "description": "财务报告的结构化分析与风险评估",
                "stages": [
                    {
                        "stage_name": "DOCUMENT_PREPROCESSING",
                        "role": "文档预处理专家",
                        "description": "财务文档预处理与格式标准化",
                        "experts": ["文档解析专家", "数据清洗专家"],
                        "output_schema": "src.schemas.analysis.ProcessedDocument",
                    },
                    {
                        "stage_name": "FINANCIAL_DATA_EXTRACTION",
                        "role": "财务数据提取专家",
                        "description": "关键财务指标提取与验证",
                        "experts": ["财务分析师", "会计专家", "数据验证专家"],
                        "output_schema": "src.schemas.analysis.FinancialMetrics",
                    },
                    {
                        "stage_name": "RATIO_ANALYSIS",
                        "role": "财务比率分析专家",
                        "description": "财务比率计算与趋势分析",
                        "experts": ["比率分析专家", "趋势分析师", "基准对比专家"],
                        "output_schema": "src.schemas.analysis.RatioAnalysis",
                    },
                    {
                        "stage_name": "RISK_ASSESSMENT",
                        "role": "风险评估专家",
                        "description": "财务风险识别与评估",
                        "experts": ["风险分析师", "信用评估专家", "合规检查专家"],
                        "output_schema": "src.schemas.analysis.RiskAssessment",
                    },
                    {
                        "stage_name": "REPORT_GENERATION",
                        "role": "财务报告生成专家",
                        "description": "综合财务分析报告生成",
                        "experts": ["报告撰写专家", "可视化专家", "决策建议专家"],
                        "output_schema": "src.schemas.analysis.FinancialReport",
                    },
                ],
            },
            "contract_review": {
                "name": "合同审查",
                "description": "合同条款分析与风险识别",
                "stages": [
                    {
                        "stage_name": "CONTRACT_PARSING",
                        "role": "合同解析专家",
                        "description": "合同文本解析与结构化",
                        "experts": ["法律文档专家", "合同解析专家"],
                        "output_schema": "src.schemas.analysis.ParsedContract",
                    },
                    {
                        "stage_name": "CLAUSE_EXTRACTION",
                        "role": "条款提取专家",
                        "description": "关键条款识别与提取",
                        "experts": ["法律条款专家", "合同要素分析师"],
                        "output_schema": "src.schemas.analysis.ContractClauses",
                    },
                    {
                        "stage_name": "LEGAL_RISK_ANALYSIS",
                        "role": "法律风险分析专家",
                        "description": "法律风险点识别与评估",
                        "experts": ["法律风险专家", "合规审查专家", "争议预防专家"],
                        "output_schema": "src.schemas.analysis.LegalRisks",
                    },
                    {
                        "stage_name": "COMPLIANCE_CHECK",
                        "role": "合规检查专家",
                        "description": "法规合规性检查",
                        "experts": ["合规专家", "法规解读专家", "标准对照专家"],
                        "output_schema": "src.schemas.analysis.ComplianceReport",
                    },
                    {
                        "stage_name": "REVIEW_SUMMARY",
                        "role": "审查总结专家",
                        "description": "合同审查结果汇总",
                        "experts": ["法律顾问", "风险总结专家", "建议制定专家"],
                        "output_schema": "src.schemas.analysis.ContractReview",
                    },
                ],
            },
            "literature_review": {
                "name": "文献综述",
                "description": "学术文献的系统性分析与综述",
                "stages": [
                    {
                        "stage_name": "LITERATURE_CLASSIFICATION",
                        "role": "文献分类专家",
                        "description": "文献分类与主题识别",
                        "experts": ["文献分类专家", "主题建模专家"],
                        "output_schema": "src.schemas.analysis.ClassifiedLiterature",
                    },
                    {
                        "stage_name": "CONTENT_EXTRACTION",
                        "role": "内容提取专家",
                        "description": "关键内容与观点提取",
                        "experts": ["学术内容分析师", "观点提取专家", "方法论分析师"],
                        "output_schema": "src.schemas.analysis.ExtractedContent",
                    },
                    {
                        "stage_name": "COMPARATIVE_ANALYSIS",
                        "role": "比较分析专家",
                        "description": "文献间比较分析",
                        "experts": ["比较研究专家", "差异分析师", "共识识别专家"],
                        "output_schema": "src.schemas.analysis.ComparativeAnalysis",
                    },
                    {
                        "stage_name": "TREND_IDENTIFICATION",
                        "role": "趋势识别专家",
                        "description": "研究趋势与发展方向识别",
                        "experts": ["趋势分析师", "发展预测专家", "研究前沿专家"],
                        "output_schema": "src.schemas.analysis.ResearchTrends",
                    },
                    {
                        "stage_name": "SYNTHESIS_REPORT",
                        "role": "综述报告专家",
                        "description": "文献综述报告生成",
                        "experts": ["学术写作专家", "综述专家", "知识图谱专家"],
                        "output_schema": "src.schemas.analysis.LiteratureReview",
                    },
                ],
            },
            "data_analysis": {
                "name": "数据分析",
                "description": "结构化数据的深度分析与洞察",
                "stages": [
                    {
                        "stage_name": "DATA_PROFILING",
                        "role": "数据画像专家",
                        "description": "数据质量评估与特征分析",
                        "experts": ["数据质量专家", "统计分析师"],
                        "output_schema": "src.schemas.analysis.DataProfile",
                    },
                    {
                        "stage_name": "EXPLORATORY_ANALYSIS",
                        "role": "探索性分析专家",
                        "description": "数据探索与模式发现",
                        "experts": ["数据科学家", "模式识别专家", "可视化专家"],
                        "output_schema": "src.schemas.analysis.ExploratoryResults",
                    },
                    {
                        "stage_name": "STATISTICAL_MODELING",
                        "role": "统计建模专家",
                        "description": "统计模型构建与验证",
                        "experts": ["统计学家", "机器学习专家", "模型验证专家"],
                        "output_schema": "src.schemas.analysis.StatisticalModel",
                    },
                    {
                        "stage_name": "INSIGHT_EXTRACTION",
                        "role": "洞察提取专家",
                        "description": "业务洞察提取与解释",
                        "experts": ["业务分析师", "洞察专家", "决策支持专家"],
                        "output_schema": "src.schemas.analysis.BusinessInsights",
                    },
                    {
                        "stage_name": "ANALYTICAL_REPORT",
                        "role": "分析报告专家",
                        "description": "数据分析报告生成",
                        "experts": ["数据报告专家", "可视化设计师", "沟通专家"],
                        "output_schema": "src.schemas.analysis.AnalyticalReport",
                    },
                ],
            },
        }

    def _load_analysis_experts(self) -> dict[str, list[str]]:
        """加载分析专家库"""
        return {
            "financial": [
                "财务分析师",
                "会计专家",
                "风险分析师",
                "投资分析师",
                "审计专家",
                "税务专家",
                "合规专家",
                "信用评估专家",
            ],
            "legal": ["法律专家", "合同专家", "合规专家", "风险评估师", "法规解读专家", "争议解决专家", "知识产权专家"],
            "academic": [
                "学术研究专家",
                "文献分析师",
                "方法论专家",
                "统计专家",
                "同行评议专家",
                "学科专家",
                "研究趋势专家",
            ],
            "data": ["数据科学家", "统计学家", "机器学习专家", "数据工程师", "业务分析师", "可视化专家", "数据质量专家"],
        }

    def generate_analysis_protocol(
        self,
        user_request: str,
        analysis_type: str = "auto",
    ) -> dict[str, Any]:
        """生成文档分析协议

        Args:
        ----
            user_request: 用户需求描述
            analysis_type: 分析类型 (financial_analysis, contract_review, literature_review, data_analysis, auto)

        Returns:
        -------
            生成的协议字典

        """
        # 自动识别分析类型
        if analysis_type == "auto":
            analysis_type = self._identify_analysis_type(user_request)

        # 获取对应模板
        template = self.analysis_templates.get(analysis_type)
        if not template:
            # 使用通用分析模板
            template = self._generate_generic_analysis_template(user_request)

        # 生成协议
        protocol = self._build_protocol_from_template(template, user_request)

        return protocol

    def _identify_analysis_type(self, user_request: str) -> str:
        """识别分析类型"""
        request_lower = user_request.lower()

        if any(keyword in request_lower for keyword in ["财务", "财报", "financial", "会计"]):
            return "financial_analysis"
        elif any(
            keyword in request_lower for keyword in ["合同", "contract", "协议", "法律"]
        ):
            return "contract_review"
        elif any(
            keyword in request_lower for keyword in ["文献", "literature", "论文", "研究"]
        ):
            return "literature_review"
        elif any(keyword in request_lower for keyword in ["数据", "data", "统计", "分析"]):
            return "data_analysis"
        else:
            return "data_analysis"  # 默认为数据分析

    def _build_protocol_from_template(
        self,
        template: dict[str, Any],
        user_request: str,
    ) -> dict[str, Any]:
        """从模板构建协议"""
        import re
        from datetime import datetime

        # 生成workflow_id
        workflow_id = re.sub(r"[^a-zA-Z0-9]+", "_", template["name"]).lower()
        workflow_id += "_analysis_" + datetime.now().strftime("%Y%m%d")

        # 构建协议
        protocol = {
            "workflow_id": workflow_id,
            "description": f"{template['description']} - {user_request[:50]}",
            "stages": [],
        }

        # 构建阶段
        for stage_template in template["stages"]:
            stage = {
                "stage_name": stage_template["stage_name"],
                "role": stage_template["role"],
                "prompt_template": self._generate_analysis_prompt(
                    stage_template,
                    user_request,
                ),
                "output_schema": stage_template["output_schema"],
            }
            protocol["stages"].append(stage)

        protocol["stages"] = self.auto_complete_stage_fields(protocol["stages"])

        return protocol

    def _generate_analysis_prompt(
        self,
        stage_template: dict[str, Any],
        user_request: str,
    ) -> str:
        """生成分析阶段的提示词"""
        experts = "、".join(stage_template["experts"])

        prompt = f"""
## 分析任务: {stage_template['description']}
## 分析专家: {experts}
## 用户需求: {user_request}

### 分析流程:
1. **文档理解**: 深入理解待分析文档的结构和内容
2. **专业分析**: 运用专业知识进行深度分析
3. **信息提取**: 提取关键信息和数据点
4. **结构化整理**: 将分析结果结构化组织
5. **质量验证**: 验证分析结果的准确性和完整性

### 输出要求:
- 分析结果准确、客观
- 信息提取完整、有序
- 结构化输出便于后续处理
- 包含溯源信息和置信度
- 符合专业标准和规范

### 注意事项:
- 保持分析的客观性和中立性
- 确保信息提取的准确性
- 标注不确定或需要进一步验证的内容
- 提供清晰的分析逻辑和依据

请严格按照分析流程执行，确保输出质量。
"""
        return prompt.strip()

    def _generate_generic_analysis_template(self, user_request: str) -> dict[str, Any]:
        """生成通用分析模板"""
        return {
            "name": "通用文档分析",
            "description": "通用的文档分析处理流程",
            "stages": [
                {
                    "stage_name": "DOCUMENT_PREPROCESSING",
                    "role": "文档预处理专家",
                    "description": "文档预处理与格式标准化",
                    "experts": ["文档解析专家", "数据清洗专家"],
                    "output_schema": "src.schemas.analysis.ProcessedDocument",
                },
                {
                    "stage_name": "INFORMATION_EXTRACTION",
                    "role": "信息提取专家",
                    "description": "关键信息提取与结构化",
                    "experts": ["信息提取专家", "结构化专家", "数据验证专家"],
                    "output_schema": "src.schemas.analysis.ExtractedInformation",
                },
                {
                    "stage_name": "ANALYTICAL_PROCESSING",
                    "role": "分析处理专家",
                    "description": "深度分析与洞察发现",
                    "experts": ["分析专家", "洞察专家", "模式识别专家"],
                    "output_schema": "src.schemas.analysis.AnalysisResults",
                },
                {
                    "stage_name": "REPORT_GENERATION",
                    "role": "报告生成专家",
                    "description": "分析报告生成与总结",
                    "experts": ["报告专家", "总结专家", "可视化专家"],
                    "output_schema": "src.schemas.analysis.AnalysisReport",
                },
            ],
        }

    def auto_complete_stage_fields(self, stages):
        import re

        def schema_to_output_key(schema_path):
            class_name = schema_path.split(".")[-1]
            s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", class_name)
            return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

        n = len(stages)
        for i, stage in enumerate(stages):
            output_key = schema_to_output_key(stage["output_schema"])
            stage["outputs"] = [output_key]
            if i == 0:
                stage["depends_on"] = []
                stage["inputs"] = [{"type": "external", "key": "document_text"}]
            else:
                stage["depends_on"] = [stages[i - 1]["stage_name"]]
                prev_output_key = schema_to_output_key(stages[i - 1]["output_schema"])
                stage["inputs"] = [
                    {
                        "type": "stage",
                        "from_stage": stages[i - 1]["stage_name"],
                        "key": prev_output_key,
                    },
                ]
            stage["acceptance_required"] = i == n - 1
        return stages


# 创建全局实例
document_analysis_generator = DocumentAnalysisGenerator()
