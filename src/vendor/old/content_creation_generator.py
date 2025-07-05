"""内容创作协议生成器
专门用于论文撰写、教材编辑等主动内容创作任务
"""

from typing import Any


class ContentCreationGenerator:
    """内容创作协议生成器

    专门处理论文撰写、教材编辑、报告编写等主动创作任务
    采用"任务驱动、分工协作、专家共创"的流程设计
    """

    def __init__(self):
        """初始化内容创作协议生成器"""
        self.creation_templates = self._load_creation_templates()
        self.expert_pools = self._load_expert_pools()

    def _load_creation_templates(self) -> dict[str, dict[str, Any]]:
        """加载内容创作模板"""
        return {
            "paper_writing": {
                "name": "论文撰写",
                "description": "从研究设想到完整论文的协作撰写流程",
                "stages": [
                    {
                        "stage_name": "RESEARCH_PLANNING",
                        "role": "研究规划专家团队",
                        "description": "研究方向确定与计划制定",
                        "experts": ["领域专家", "方法论专家", "文献调研专家"],
                        "output_schema": "src.schemas.creation.ResearchPlan",
                    },
                    {
                        "stage_name": "LITERATURE_SYNTHESIS",
                        "role": "文献综述专家团队",
                        "description": "相关文献收集、分析与综述",
                        "experts": ["文献检索专家", "学术写作专家", "批判性思维专家"],
                        "output_schema": "src.schemas.creation.LiteratureReview",
                    },
                    {
                        "stage_name": "METHODOLOGY_DESIGN",
                        "role": "研究方法设计团队",
                        "description": "研究方法设计与实验方案制定",
                        "experts": ["统计学专家", "实验设计专家", "数据分析专家"],
                        "output_schema": "src.schemas.creation.MethodologyDesign",
                    },
                    {
                        "stage_name": "CONTENT_DRAFTING",
                        "role": "论文撰写团队",
                        "description": "论文各部分协作撰写",
                        "experts": ["学术写作专家", "领域专家", "语言润色专家"],
                        "output_schema": "src.schemas.creation.PaperDraft",
                    },
                    {
                        "stage_name": "PEER_REVIEW_OPTIMIZATION",
                        "role": "同行评议团队",
                        "description": "内部评议与优化改进",
                        "experts": ["同行评议专家", "质量控制专家", "学术标准审查员"],
                        "output_schema": "src.schemas.creation.FinalPaper",
                    },
                ],
            },
            "textbook_editing": {
                "name": "教材编辑",
                "description": "从教学大纲到完整教材的协作编辑流程",
                "stages": [
                    {
                        "stage_name": "CURRICULUM_ANALYSIS",
                        "role": "教学设计专家团队",
                        "description": "教学大纲分析与知识体系构建",
                        "experts": ["教学设计专家", "课程规划专家", "学习目标分析师"],
                        "output_schema": "src.schemas.creation.CurriculumStructure",
                    },
                    {
                        "stage_name": "CONTENT_PLANNING",
                        "role": "内容规划团队",
                        "description": "章节规划与内容框架设计",
                        "experts": ["内容架构师", "知识图谱专家", "教学逻辑专家"],
                        "output_schema": "src.schemas.creation.ContentPlan",
                    },
                    {
                        "stage_name": "COLLABORATIVE_WRITING",
                        "role": "协作编写团队",
                        "description": "多专家协作编写教材内容",
                        "experts": ["学科专家", "教学专家", "案例设计专家", "思政融入专家"],
                        "output_schema": "src.schemas.creation.TextbookContent",
                    },
                    {
                        "stage_name": "QUALITY_REVIEW",
                        "role": "质量审查团队",
                        "description": "教材质量审查与标准化",
                        "experts": ["教材审查专家", "语言文字专家", "教学适用性评估师"],
                        "output_schema": "src.schemas.creation.QualityReport",
                    },
                    {
                        "stage_name": "FINAL_INTEGRATION",
                        "role": "整合定稿团队",
                        "description": "最终整合与版本定稿",
                        "experts": ["总编辑", "版式设计专家", "出版标准专家"],
                        "output_schema": "src.schemas.creation.FinalTextbook",
                    },
                ],
            },
            "report_writing": {
                "name": "报告编写",
                "description": "从需求分析到完整报告的协作编写流程",
                "stages": [
                    {
                        "stage_name": "REQUIREMENT_ANALYSIS",
                        "role": "需求分析团队",
                        "description": "报告需求分析与目标确定",
                        "experts": ["需求分析师", "业务专家", "目标设定专家"],
                        "output_schema": "src.schemas.creation.ReportRequirements",
                    },
                    {
                        "stage_name": "RESEARCH_EXECUTION",
                        "role": "调研执行团队",
                        "description": "数据收集与调研执行",
                        "experts": ["调研专家", "数据收集专家", "访谈专家"],
                        "output_schema": "src.schemas.creation.ResearchData",
                    },
                    {
                        "stage_name": "ANALYSIS_SYNTHESIS",
                        "role": "分析综合团队",
                        "description": "数据分析与结论综合",
                        "experts": ["数据分析师", "统计专家", "洞察提炼专家"],
                        "output_schema": "src.schemas.creation.AnalysisResults",
                    },
                    {
                        "stage_name": "REPORT_COMPOSITION",
                        "role": "报告撰写团队",
                        "description": "报告结构设计与内容撰写",
                        "experts": ["报告写作专家", "可视化专家", "商务沟通专家"],
                        "output_schema": "src.schemas.creation.ReportDraft",
                    },
                    {
                        "stage_name": "STAKEHOLDER_REVIEW",
                        "role": "利益相关方评审团队",
                        "description": "利益相关方评审与优化",
                        "experts": ["业务评审专家", "技术评审专家", "决策支持专家"],
                        "output_schema": "src.schemas.creation.FinalReport",
                    },
                ],
            },
        }

    def _load_expert_pools(self) -> dict[str, list[str]]:
        """加载专家库"""
        return {
            "academic": [
                "领域专家",
                "方法论专家",
                "文献调研专家",
                "学术写作专家",
                "统计学专家",
                "实验设计专家",
                "同行评议专家",
                "质量控制专家",
            ],
            "education": [
                "教学设计专家",
                "课程规划专家",
                "内容架构师",
                "学科专家",
                "教学专家",
                "案例设计专家",
                "思政融入专家",
                "教材审查专家",
            ],
            "business": [
                "需求分析师",
                "业务专家",
                "调研专家",
                "数据分析师",
                "报告写作专家",
                "商务沟通专家",
                "决策支持专家",
            ],
            "technical": ["技术专家", "系统架构师", "数据工程师", "算法专家", "产品经理", "用户体验专家", "质量保证专家"],
        }

    def generate_creation_protocol(
        self,
        user_request: str,
        creation_type: str = "auto",
    ) -> dict[str, Any]:
        """生成内容创作协议

        Args:
        ----
            user_request: 用户需求描述
            creation_type: 创作类型 (paper_writing, textbook_editing, report_writing, auto)

        Returns:
        -------
            生成的协议字典

        """
        # 自动识别创作类型
        if creation_type == "auto":
            creation_type = self._identify_creation_type(user_request)

        # 获取对应模板
        template = self.creation_templates.get(creation_type)
        if not template:
            # 使用通用创作模板
            template = self._generate_generic_creation_template(user_request)

        # 生成协议
        protocol = self._build_protocol_from_template(template, user_request)

        return protocol

    def _identify_creation_type(self, user_request: str) -> str:
        """识别创作类型"""
        request_lower = user_request.lower()

        if any(keyword in request_lower for keyword in ["论文", "paper", "研究", "study"]):
            return "paper_writing"
        elif any(
            keyword in request_lower for keyword in ["教材", "教程", "textbook", "课程"]
        ):
            return "textbook_editing"
        elif any(keyword in request_lower for keyword in ["报告", "report", "调研", "分析"]):
            return "report_writing"
        else:
            return "report_writing"  # 默认为报告编写

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
        workflow_id += "_" + datetime.now().strftime("%Y%m%d")

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
                "prompt_template": self._generate_creation_prompt(
                    stage_template,
                    user_request,
                ),
                "output_schema": stage_template["output_schema"],
            }
            protocol["stages"].append(stage)

        protocol["stages"] = self.auto_complete_stage_fields(protocol["stages"])

        return protocol

    def _generate_creation_prompt(
        self,
        stage_template: dict[str, Any],
        user_request: str,
    ) -> str:
        """生成创作阶段的提示词"""
        experts = "、".join(stage_template["experts"])

        prompt = f"""
## 阶段任务: {stage_template['description']}
## 参与专家: {experts}
## 用户需求: {user_request}

### 协作流程:
1. **专家独立思考**: 每位专家基于自身专业背景，独立分析任务需求
2. **观点交流**: 各专家分享观点，讨论不同视角和方法
3. **协作创作**: 团队协作完成本阶段的创作任务
4. **质量把控**: 对创作内容进行质量检查和优化
5. **成果输出**: 形成结构化的阶段成果

### 输出要求:
- 内容完整、逻辑清晰
- 符合专业标准和规范
- 为下一阶段提供有效输入
- 包含必要的元数据和溯源信息

请严格按照协作流程执行，确保输出质量。
"""
        return prompt.strip()

    def _generate_generic_creation_template(self, user_request: str) -> dict[str, Any]:
        """生成通用创作模板"""
        return {
            "name": "通用内容创作",
            "description": "通用的内容创作协作流程",
            "stages": [
                {
                    "stage_name": "PLANNING_AND_DESIGN",
                    "role": "规划设计团队",
                    "description": "内容规划与结构设计",
                    "experts": ["内容策划专家", "结构设计师", "目标分析师"],
                    "output_schema": "src.schemas.creation.ContentPlan",
                },
                {
                    "stage_name": "COLLABORATIVE_CREATION",
                    "role": "协作创作团队",
                    "description": "多专家协作创作内容",
                    "experts": ["内容创作专家", "领域专家", "质量控制专家"],
                    "output_schema": "src.schemas.creation.CreatedContent",
                },
                {
                    "stage_name": "REVIEW_AND_OPTIMIZATION",
                    "role": "评审优化团队",
                    "description": "内容评审与优化改进",
                    "experts": ["评审专家", "优化专家", "标准化专家"],
                    "output_schema": "src.schemas.creation.OptimizedContent",
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
content_creation_generator = ContentCreationGenerator()
