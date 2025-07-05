"""智能DAIP协议生成器
使用大模型进行自然语言理解，自动推理出合适的workflow_id、stages、角色、分工、输出schema等
支持few-shot示例提升输出质量和多样性
"""

from typing import Any, Optional

import yaml

from src.content_creation_generator import ContentCreationGenerator
from src.document_analysis_generator import DocumentAnalysisGenerator
from src.lim import LLMInteractionModule
from src.protocol_validator import validate_protocol
from src.schema_recommender import SchemaRecommender
from src.sskg import SSKG
from src.task_classifier import TaskClassifier, TaskType


class IntelligentProtocolGenerator:
    """智能DAIP协议生成器

    使用大模型进行自然语言理解，自动推理出合适的workflow_id、stages、角色、分工、输出schema等。
    支持few-shot示例提升输出质量和多样性。
    """

    def __init__(self, llm_module: Optional[LLMInteractionModule] = None):
        """初始化智能协议生成器"""
        if llm_module is None:
            # 创建一个临时的SSKG实例用于LLM交互
            from src.config import CHROMA_PATH, DATABASE_PATH

            sskg = SSKG(DATABASE_PATH, CHROMA_PATH)
            sskg.init_db()  # 初始化数据库
            self.llm_module = LLMInteractionModule(sskg)
        else:
            self.llm_module = llm_module

        # 初始化组件
        self.schema_recommender = SchemaRecommender()
        self.task_classifier = TaskClassifier()
        self.content_creation_generator = ContentCreationGenerator()
        self.document_analysis_generator = DocumentAnalysisGenerator()

        # 加载few-shot示例
        self.few_shot_examples = self._load_few_shot_examples()

        # 加载现有schema库
        self.schema_library = self._load_schema_library()

        self.system_prompt = self._build_system_prompt()

    def _load_few_shot_examples(self) -> list[dict[str, Any]]:
        """加载few-shot示例"""
        examples = [
            {
                "user_input": "帮我创建一个分析财报的流程，先提取关键财务指标，然后生成摘要",
                "output": """workflow_id: financial_analysis_v1
description: 分析财务报告并提取关键指标
stages:
  - stage_name: EXTRACT_FINANCIAL_METRICS
    role: "首席金融分析师"
    prompt_template: "请分析以下财务报告，提取关键财务指标包括收入、利润、现金流等。\\n\\n报告内容:\\n{document_text}"
    output_schema: "src.schemas.financial.FinancialMetrics"
  - stage_name: GENERATE_FINANCIAL_SUMMARY
    role: "财务报告专家"
    prompt_template: "基于提取的财务指标，生成一份简洁的财务分析摘要。\\n\\n财务指标:\\n{financial_metrics_json}"
    output_schema: "src.schemas.financial.FinancialSummary"
""",
            },
            {
                "user_input": "我需要一个论文分析的协议，包括内容提取、关键点识别、摘要生成",
                "output": """workflow_id: paper_analysis_v1
description: 分析学术论文并生成结构化摘要
stages:
  - stage_name: EXTRACT_PAPER_CONTENT
    role: "学术论文分析专家"
    prompt_template: "请分析以下学术论文，提取主要观点、方法和结论。\\n\\n论文内容:\\n{document_text}"
    output_schema: "src.schemas.academic.PaperContent"
  - stage_name: IDENTIFY_KEY_POINTS
    role: "研究方法专家"
    prompt_template: "基于提取的论文内容，识别关键研究点、创新点和贡献。\\n\\n论文内容:\\n{paper_content_json}"
    output_schema: "src.schemas.academic.KeyPoints"
  - stage_name: GENERATE_PAPER_SUMMARY
    role: "学术写作专家"
    prompt_template: "基于识别的关键点，生成一份结构化的论文摘要。\\n\\n关键点:\\n{key_points_json}"
    output_schema: "src.schemas.academic.PaperSummary"
""",
            },
            {
                "user_input": "创建一个市场调研报告分析流程，需要数据提取、趋势分析、竞争分析、建议生成",
                "output": """workflow_id: market_research_analysis_v1
description: 分析市场调研报告并生成战略建议
stages:
  - stage_name: EXTRACT_MARKET_DATA
    role: "市场数据分析师"
    prompt_template: "请从市场调研报告中提取关键数据，包括市场规模、增长率、用户画像等。\\n\\n报告内容:\\n{document_text}"
    output_schema: "src.schemas.market.MarketData"
  - stage_name: ANALYZE_TRENDS
    role: "趋势分析专家"
    prompt_template: "基于提取的市场数据，分析行业趋势和发展方向。\\n\\n市场数据:\\n{market_data_json}"
    output_schema: "src.schemas.market.TrendAnalysis"
  - stage_name: COMPETITIVE_ANALYSIS
    role: "竞争策略分析师"
    prompt_template: "结合市场数据和趋势分析，进行竞争对手分析。\\n\\n市场数据:\\n{market_data_json}\\n\\n趋势分析:\\n{trend_analysis_json}"
    output_schema: "src.schemas.market.CompetitiveAnalysis"
  - stage_name: GENERATE_RECOMMENDATIONS
    role: "战略咨询专家"
    prompt_template: "基于全面的市场分析，生成具体的战略建议和行动计划。\\n\\n竞争分析:\\n{competitive_analysis_json}"
    output_schema: "src.schemas.market.StrategicRecommendations"
""",
            },
        ]
        return examples

    def _load_schema_library(self) -> dict[str, list[str]]:
        """加载现有schema库"""
        schema_library = {
            "financial": [
                "src.schemas.financial.FinancialMetrics",
                "src.schemas.financial.FinancialSummary",
                "src.schemas.financial.BalanceSheet",
                "src.schemas.financial.IncomeStatement",
                "src.schemas.financial.CashFlow",
            ],
            "academic": [
                "src.schemas.academic.PaperContent",
                "src.schemas.academic.PaperSummary",
                "src.schemas.academic.KeyPoints",
                "src.schemas.academic.ResearchMethod",
                "src.schemas.academic.Citation",
            ],
            "market": [
                "src.schemas.market.MarketData",
                "src.schemas.market.TrendAnalysis",
                "src.schemas.market.CompetitiveAnalysis",
                "src.schemas.market.StrategicRecommendations",
                "src.schemas.market.CustomerSegment",
            ],
            "general": [
                "src.schemas.general.KeyInformation",
                "src.schemas.general.AnalysisReport",
                "src.schemas.general.EntityCount",
                "src.schemas.general.Summary",
                "src.schemas.general.Classification",
            ],
        }
        return schema_library

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        few_shot_text = "\n\n".join(
            [
                f"**示例 {i+1}:**\n用户输入: {ex['user_input']}\n输出:\n```yaml\n{ex['output']}\n```"
                for i, ex in enumerate(self.few_shot_examples)
            ],
        )

        schema_text = "\n".join(
            [
                f"**{domain}领域:** {', '.join(schemas)}"
                for domain, schemas in self.schema_library.items()
            ],
        )

        return f"""# 智能DAIP协议生成专家

你是一个专业的DAIP协议生成专家，能够根据用户的自然语言需求，智能生成结构化的YAML协议文件。

## 核心能力

1. **自然语言理解**: 深度理解用户需求，识别关键业务逻辑
2. **智能多阶段分解**: 自动将复杂任务分解为合理的处理阶段
3. **专家角色分配**: 为每个阶段分配最合适的AI专家角色
4. **Schema智能推荐**: 基于任务类型推荐合适的输出schema

## 协议结构要求

每个协议必须包含：
- **workflow_id**: 工作流唯一标识符（snake_case格式）
- **description**: 协议用途的人类可读描述
- **stages**: 阶段列表，每个阶段包含：
  - **stage_name**: 阶段名称（UPPER_SNAKE_CASE格式）
  - **role**: 执行该阶段的AI专家角色描述
  - **prompt_template**: 详细的AI指令模板，可包含占位符
  - **output_schema**: 输出数据的Pydantic模型导入路径

## 可用Schema库

{schema_text}

## Few-shot示例

{few_shot_text}

## 生成原则

1. **智能分解**: 根据任务复杂度自动确定合适的阶段数量（2-6个阶段）
2. **角色专业化**: 每个阶段分配具有相关专业背景的AI角色
3. **数据流设计**: 确保阶段间的数据传递逻辑清晰
4. **Schema匹配**: 优先使用现有schema，必要时创建新的schema路径
5. **Prompt优化**: 生成清晰、具体、可执行的指令模板

## 输出要求

直接输出完整的YAML协议，不需要额外解释。确保：
- workflow_id使用snake_case格式
- stage_name使用UPPER_SNAKE_CASE格式
- 所有字段完整且格式正确
- prompt_template中的换行符使用\\n转义
"""

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

    async def generate_protocol_smart(
        self,
        user_request: str,
        validate: bool = True,
    ) -> dict[str, Any]:
        """智能协议生成 - 根据任务类型自动选择生成器

        Args:
        ----
            user_request: 用户的自然语言需求
            validate: 是否验证生成的协议

        Returns:
        -------
            包含生成结果的字典

        """
        try:
            (
                task_type,
                confidence,
                classification_info,
            ) = self.task_classifier.classify_task(user_request)
            print(f"任务分类: {task_type.value}, 置信度: {confidence:.2f}")
            print(f"分类信息: {classification_info}")
            if task_type == TaskType.CONTENT_CREATION:
                protocol_dict = (
                    self.content_creation_generator.generate_creation_protocol(
                        user_request,
                    )
                )
            else:
                protocol_dict = (
                    self.document_analysis_generator.generate_analysis_protocol(
                        user_request,
                    )
                )
            protocol_dict["stages"] = self.auto_complete_stage_fields(
                protocol_dict["stages"],
            )
            yaml_content = yaml.dump(
                protocol_dict,
                allow_unicode=True,
                default_flow_style=False,
            )
            optimized_yaml = self._optimize_schemas(yaml_content, user_request)
            if validate:
                validation_result = validate_protocol(optimized_yaml)
                if validation_result["success"]:
                    return {
                        "success": True,
                        "yaml_content": optimized_yaml,
                        "validation_result": validation_result,
                        "task_classification": {
                            "task_type": task_type.value,
                            "confidence": confidence,
                            "classification_info": classification_info,
                        },
                        "generation_method": "内容创作生成器"
                        if task_type == TaskType.CONTENT_CREATION
                        else "文档分析生成器",
                        "message": f"智能协议生成成功 (使用{'内容创作生成器' if task_type == TaskType.CONTENT_CREATION else '文档分析生成器'})",
                    }
                else:
                    return {
                        "success": False,
                        "yaml_content": optimized_yaml,
                        "validation_result": validation_result,
                        "task_classification": {
                            "task_type": task_type.value,
                            "confidence": confidence,
                            "classification_info": classification_info,
                        },
                        "generation_method": "内容创作生成器"
                        if task_type == TaskType.CONTENT_CREATION
                        else "文档分析生成器",
                        "message": f"协议生成但验证失败 (使用{'内容创作生成器' if task_type == TaskType.CONTENT_CREATION else '文档分析生成器'})",
                        "error": validation_result.get("error", "未知验证错误"),
                    }
            else:
                return {
                    "success": True,
                    "yaml_content": optimized_yaml,
                    "task_classification": {
                        "task_type": task_type.value,
                        "confidence": confidence,
                        "classification_info": classification_info,
                    },
                    "generation_method": "内容创作生成器"
                    if task_type == TaskType.CONTENT_CREATION
                    else "文档分析生成器",
                    "message": f"智能协议生成成功 (使用{'内容创作生成器' if task_type == TaskType.CONTENT_CREATION else '文档分析生成器'}, 未验证)",
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"智能协议生成过程中发生错误: {e!s}",
                "error": str(e),
            }

    async def generate_protocol(
        self,
        user_request: str,
        validate: bool = True,
    ) -> dict[str, Any]:
        """根据用户请求智能生成DAIP协议

        Args:
        ----
            user_request: 用户的自然语言需求
            validate: 是否验证生成的协议

        Returns:
        -------
            包含生成结果的字典

        """
        try:
            # 使用LLM生成协议
            llm_response = await self.llm_module.get_llm_response(
                f"请根据以下用户需求生成DAIP协议:\n\n{user_request}",
                [],  # 不需要工具定义
            )

            if llm_response["type"] != "text":
                return {
                    "success": False,
                    "message": f"LLM响应错误: {llm_response.get('content', '未知错误')}",
                    "error": llm_response.get("content", "未知错误"),
                }

            generated_yaml = llm_response["content"]

            # 提取YAML内容（如果包含在代码块中）
            if "```yaml" in generated_yaml:
                yaml_start = generated_yaml.find("```yaml") + 7
                yaml_end = generated_yaml.find("```", yaml_start)
                if yaml_end != -1:
                    generated_yaml = generated_yaml[yaml_start:yaml_end].strip()
            elif "```" in generated_yaml:
                yaml_start = generated_yaml.find("```") + 3
                yaml_end = generated_yaml.find("```", yaml_start)
                if yaml_end != -1:
                    generated_yaml = generated_yaml[yaml_start:yaml_end].strip()

            if validate:
                # 验证生成的协议
                validation_result = validate_protocol(generated_yaml)

                if validation_result["success"]:
                    return {
                        "success": True,
                        "yaml_content": generated_yaml,
                        "validation_result": validation_result,
                        "message": "智能协议生成成功并通过验证",
                    }
                else:
                    return {
                        "success": False,
                        "yaml_content": generated_yaml,
                        "validation_result": validation_result,
                        "message": "协议生成但验证失败",
                        "error": validation_result.get("error", "未知验证错误"),
                    }
            else:
                return {
                    "success": True,
                    "yaml_content": generated_yaml,
                    "message": "智能协议生成成功（未验证）",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"智能协议生成过程中发生错误: {e!s}",
                "error": str(e),
            }

    async def analyze_and_decompose_task(self, user_request: str) -> dict[str, Any]:
        """智能分析和分解用户任务

        Args:
        ----
            user_request: 用户的自然语言需求

        Returns:
        -------
            包含任务分解结果的字典

        """
        analysis_prompt = f"""
请分析以下用户需求，并将其分解为合理的处理阶段：

用户需求: {user_request}

请按以下格式输出分析结果：

任务类型: [数据分析/文档处理/报告生成/其他]
复杂度: [简单/中等/复杂]
建议阶段数: [2-6个]
主要领域: [financial/academic/market/general/其他]

阶段分解:
1. 阶段名称: [UPPER_SNAKE_CASE格式]
   目标: [该阶段的具体目标]
   输入: [需要的输入数据]
   输出: [预期的输出结果]
   专家角色: [最适合的专家角色]

2. [继续其他阶段...]

请确保阶段间的逻辑关系清晰，数据流合理。
"""

        try:
            llm_response = await self.llm_module.get_llm_response(analysis_prompt, [])

            if llm_response["type"] == "text":
                return {
                    "success": True,
                    "analysis": llm_response["content"],
                    "message": "任务分析完成",
                }
            else:
                return {
                    "success": False,
                    "message": f"任务分析失败: {llm_response.get('content', '未知错误')}",
                    "error": llm_response.get("content", "未知错误"),
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"任务分析过程中发生错误: {e!s}",
                "error": str(e),
            }

    async def generate_protocol_with_analysis(
        self,
        user_request: str,
        validate: bool = True,
    ) -> dict[str, Any]:
        """基于任务分析生成智能协议

        Args:
        ----
            user_request: 用户的自然语言需求
            validate: 是否验证生成的协议

        Returns:
        -------
            包含生成结果的字典

        """
        try:
            # 首先分析任务
            analysis_result = await self.analyze_and_decompose_task(user_request)

            if not analysis_result["success"]:
                return analysis_result

            # 基于分析结果生成协议
            enhanced_prompt = f"""
基于以下任务分析，生成完整的DAIP协议：

原始需求: {user_request}

任务分析:
{analysis_result["analysis"]}

请生成完整的YAML协议，确保：
1. 使用分析中建议的阶段结构
2. 为每个阶段选择最合适的专家角色
3. 设计清晰的prompt模板
4. 推荐合适的output_schema

直接输出YAML格式的协议，不需要额外解释。
"""

            llm_response = await self.llm_module.get_llm_response(enhanced_prompt, [])

            if llm_response["type"] != "text":
                return {
                    "success": False,
                    "message": f"协议生成失败: {llm_response.get('content', '未知错误')}",
                    "error": llm_response.get("content", "未知错误"),
                }

            generated_yaml = llm_response["content"]

            # 提取YAML内容
            if "```yaml" in generated_yaml:
                yaml_start = generated_yaml.find("```yaml") + 7
                yaml_end = generated_yaml.find("```", yaml_start)
                if yaml_end != -1:
                    generated_yaml = generated_yaml[yaml_start:yaml_end].strip()
            elif "```" in generated_yaml:
                yaml_start = generated_yaml.find("```") + 3
                yaml_end = generated_yaml.find("```", yaml_start)
                if yaml_end != -1:
                    generated_yaml = generated_yaml[yaml_start:yaml_end].strip()

            # 使用Schema推荐器优化schema选择
            optimized_yaml = self._optimize_schemas(generated_yaml, user_request)

            if validate:
                validation_result = validate_protocol(optimized_yaml)

                if validation_result["success"]:
                    return {
                        "success": True,
                        "yaml_content": optimized_yaml,
                        "validation_result": validation_result,
                        "task_analysis": analysis_result["analysis"],
                        "message": "智能协议生成成功并通过验证",
                    }
                else:
                    return {
                        "success": False,
                        "yaml_content": optimized_yaml,
                        "validation_result": validation_result,
                        "task_analysis": analysis_result["analysis"],
                        "message": "协议生成但验证失败",
                        "error": validation_result.get("error", "未知验证错误"),
                    }
            else:
                return {
                    "success": True,
                    "yaml_content": optimized_yaml,
                    "task_analysis": analysis_result["analysis"],
                    "message": "智能协议生成成功（未验证）",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"智能协议生成过程中发生错误: {e!s}",
                "error": str(e),
            }

    def _optimize_schemas(self, yaml_content: str, user_request: str) -> str:
        """使用Schema推荐器优化schema选择"""
        try:
            # 解析YAML
            protocol_data = yaml.safe_load(yaml_content)

            if "stages" in protocol_data:
                for stage in protocol_data["stages"]:
                    # 为每个阶段推荐更合适的schema
                    (
                        recommended_schema,
                        confidence,
                    ) = self.schema_recommender.recommend_schema(
                        stage.get("stage_name", ""),
                        stage.get("role", ""),
                        stage.get("prompt_template", ""),
                        user_request,
                    )

                    # 如果推荐的schema置信度较高，则使用推荐的schema
                    if confidence > 0.6:
                        stage["output_schema"] = recommended_schema

            # 重新序列化为YAML
            return yaml.dump(
                protocol_data,
                allow_unicode=True,
                default_flow_style=False,
            )

        except Exception as e:
            print(f"Schema优化失败: {e}")
            return yaml_content

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return self.system_prompt


# 创建全局实例
intelligent_protocol_generator = IntelligentProtocolGenerator()
