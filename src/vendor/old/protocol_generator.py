"""DAIP协议生成器智能体
负责将自然语言需求转换为符合格式的YAML协议
"""

from typing import Any

from src.protocol_validator import validate_protocol


class ProtocolGeneratorAgent:
    """DAIP协议生成器智能体
    将用户的自然语言需求转换为符合DAIP规范的YAML协议
    """

    def __init__(self):
        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        """获取协议生成器的系统提示"""
        return """# ROLE: DAIP Protocol Architect

## MISSION
Your sole mission is to translate a user's natural language request into a perfectly structured and valid DAIP Insight Engine YAML protocol. You must adhere strictly to the defined schema and best practices.

## CORE PROTOCOL SCHEMA
A valid protocol MUST contain the following root keys:
- `workflow_id`: A unique, snake_case identifier (e.g., `financial_report_analyzer_v1`).
- `description`: A human-readable sentence explaining the protocol's purpose.
- `stages`: A list of one or more stage objects.

Each `stage` object in the `stages` list MUST contain:
- `stage_name`: A unique, UPPER_SNAKE_CASE identifier for the stage (e.g., `EXTRACT_KEY_METRICS`).
- `role`: A descriptive title for the expert AI performing this stage (e.g., "首席金融分析师").
- `prompt_template`: The detailed instructions for the AI. It can use placeholders like `{document_text}` or variables from previous stages like `{key_metrics_json}`.
- `output_schema`: The Python import path to the Pydantic model that defines the expected structured output (e.g., `src.schemas.financial.KeyMetrics`).

## CRITICAL INSTRUCTIONS & SELF-CORRECTION
1. **Deconstruct Request:** First, break down the user's request into logical steps. Each step becomes a `stage`.
2. **Schema Proposal:** For the `output_schema`, you must propose a plausible Python Pydantic model path (e.g., `src.schemas.custom.NewModel`). Clearly state in your response that a developer needs to create this file if it doesn't exist.
3. **Draft YAML:** Generate the complete YAML content based on the deconstructed steps.
4. **VALIDATE YOURSELF:** Before providing the final answer, YOU MUST use the `validate_protocol` tool to check your own generated YAML for both syntax and structural validity.
5. **Final Output:**
   - If `validate_protocol` returns success, present the final, validated YAML to the user inside a ```yaml code block.
   - If `validate_protocol` returns an error, ANALYZE the error message, CORRECT your YAML, and re-validate. Repeat until the validation succeeds. Do not show the user the invalid attempts, only the final, correct result.

## EXAMPLE
**User Request:** "I need a simple protocol to first pull out all names and email addresses from a document, and then count them."

**Your Thought Process (internal monologue):**
1. *Deconstruct:* Two steps. Step 1: Extraction. Step 2: Counting.
2. *Stage 1 (Extraction):* `stage_name`: `EXTRACT_ENTITIES`, `role`: "数据提取专家", `output_schema`: `src.schemas.general.ExtractedEntities`. I'll need to imagine this schema has a list of names and emails.
3. *Stage 2 (Counting):* `stage_name`: `COUNT_ENTITIES`, `role`: "统计员", `prompt_template`: "Based on the following JSON: {extracted_entities_json}, count the number of names and emails.", `output_schema`: `src.schemas.general.EntityCount`.
4. *Draft YAML:* I will now write the full YAML.
5. *Validate:* I will call `validate_protocol` with my draft.
6. *Finalize:* The tool confirms it's valid. I will now present the final YAML.

**Your Final Output (after successful validation):**
```yaml
workflow_id: contact_extraction_and_count_v1
description: Extracts names and emails from a document and then counts them.
stages:
  - stage_name: EXTRACT_ENTITIES
    role: "数据提取专家"
    prompt_template: "Please analyze the following document and extract all personal names and email addresses you can find. Structure the output precisely as requested.\\n\\nDocument:\\n{document_text}"
    output_schema: "src.schemas.general.ExtractedEntities"
  - stage_name: COUNT_ENTITIES
    role: "统计员"
    prompt_template: "Based on the extracted entities JSON below, please provide a count of the total number of names and the total number of emails.\\n\\nExtracted Entities JSON:\\n{extracted_entities_json}"
    output_schema: "src.schemas.general.EntityCount"
```

## IMPORTANT NOTES
- Always use the `validate_protocol` tool to verify your generated YAML
- If validation fails, analyze the error and fix the issues before presenting the final result
- Be creative but realistic with schema paths - they should follow Python import conventions
- Ensure all stage names are unique and in UPPER_SNAKE_CASE format
- Make sure workflow_id is in snake_case format
- Provide clear, actionable prompt templates that guide the AI effectively"""

    def generate_protocol(
        self,
        user_request: str,
        validate: bool = True,
    ) -> dict[str, Any]:
        """根据用户请求生成DAIP协议

        Args:
        ----
            user_request: 用户的自然语言需求
            validate: 是否验证生成的协议

        Returns:
        -------
            包含生成结果的字典

        """
        try:
            # 这里应该调用LLM来生成协议
            # 由于这是一个示例实现，我们返回一个模板
            generated_yaml = self._generate_template_protocol(user_request)

            if validate:
                # 验证生成的协议
                validation_result = validate_protocol(generated_yaml)

                if validation_result["success"]:
                    return {
                        "success": True,
                        "yaml_content": generated_yaml,
                        "validation_result": validation_result,
                        "message": "协议生成成功并通过验证",
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
                    "message": "协议生成成功（未验证）",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"协议生成过程中发生错误: {e!s}",
                "error": str(e),
            }

    def _generate_template_protocol(self, user_request: str) -> str:
        """生成模板协议（示例实现）
        在实际使用中，这里应该调用LLM来生成协议
        """
        # 这是一个简化的模板生成器
        # 实际实现应该使用LLM来解析用户请求并生成相应的协议

        # 基于用户请求的关键词生成不同的模板
        request_lower = user_request.lower()

        if (
            "财务" in request_lower
            or "财报" in request_lower
            or "financial" in request_lower
        ):
            return """workflow_id: financial_analysis_v1
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
"""
        elif "论文" in request_lower or "paper" in request_lower or "研究" in request_lower:
            return """workflow_id: paper_analysis_v1
description: 分析学术论文并生成摘要
stages:
  - stage_name: EXTRACT_PAPER_CONTENT
    role: "学术论文分析专家"
    prompt_template: "请分析以下学术论文，提取主要观点、方法和结论。\\n\\n论文内容:\\n{document_text}"
    output_schema: "src.schemas.academic.PaperContent"
  - stage_name: GENERATE_PAPER_SUMMARY
    role: "学术写作专家"
    prompt_template: "基于提取的论文内容，生成一份结构化的论文摘要。\\n\\n论文内容:\\n{paper_content_json}"
    output_schema: "src.schemas.academic.PaperSummary"
"""
        else:
            # 通用模板
            return """workflow_id: document_analysis_v1
description: 分析文档内容并提取关键信息
stages:
  - stage_name: EXTRACT_KEY_INFORMATION
    role: "文档分析专家"
    prompt_template: "请分析以下文档，提取关键信息和重要观点。\\n\\n文档内容:\\n{document_text}"
    output_schema: "src.schemas.general.KeyInformation"
  - stage_name: GENERATE_ANALYSIS_REPORT
    role: "报告生成专家"
    prompt_template: "基于提取的关键信息，生成一份分析报告。\\n\\n关键信息:\\n{key_information_json}"
    output_schema: "src.schemas.general.AnalysisReport"
"""

    def get_system_prompt(self) -> str:
        """获取系统提示"""
        return self.system_prompt


# 创建全局实例
protocol_generator = ProtocolGeneratorAgent()
