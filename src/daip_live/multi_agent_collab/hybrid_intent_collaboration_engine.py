"""
增强意图识别器 - 集成规则匹配和大模型分析
将传统的规则匹配与大模型意图分析相结合
"""

import sys

sys.path.insert(0, "./src")


from daip_live.agent_engine.enhanced_intent_recognizer import EnhancedIntentRecognizer
from daip_live.multi_agent_collab.paper_search_download_system import (
    AdvancedPaperSearchDownloadSystem,
)
from daip_live.multi_agent_collab.real_collaboration_engine import (
    LLMBasedIntentAnalyzer,
)


class HybridIntentRecognizer(EnhancedIntentRecognizer):
    """
    混合意图识别器
    结合传统规则匹配和大模型分析，提高准确性
    """

    def __init__(self, llm_model_provider=None):
        super().__init__()

        # 创建大模型意图分析器
        self.llm_analyzer = LLMBasedIntentAnalyzer(model_provider=llm_model_provider)

        # 信任分数配置
        self.rule_based_confidence_weight = 0.7
        self.llm_based_confidence_weight = 0.3

    def recognize_intent(self, text: str, session_id: str = "default"):
        """
        混合意图识别方法
        1. 首先尝试规则匹配（高置信度）
        2. 如规则未匹配，则使用大模型进行分析
        3. 融合结果返回最可信的意图
        """
        # 首先尝试规则匹配
        rule_intent = super().recognize_intent(text, session_id)

        # 如果规则匹配成功且置信度足够高，直接返回
        if rule_intent and getattr(rule_intent, "confidence", 0.0) >= 0.8:
            return rule_intent

        # 如果规则匹配失败或置信度不够，使用真实的大模型分析
        try:
            import asyncio

            # 在异步环境中运行LLM分析
            try:
                loop = asyncio.get_running_loop()
                if loop and self.llm_analyzer:
                    # 使用真实的LLM分析器
                    llm_result_task = asyncio.create_task(
                        self.llm_analyzer.analyze_intent_with_llm(text)
                    )
                    # 等待任务完成
                    llm_result = llm_result_task
                else:
                    # 如果没有LLM分析器或不在事件循环中，跳过LLM分析
                    llm_result = None
            except RuntimeError:
                # 如果不在事件循环中，跳过LLM分析
                llm_result = None

            # 根据大模型分析结果创建意图对象
            if isinstance(llm_result, dict) and "intent_name" in llm_result:
                from daip_live.agent_engine.enhanced_intent_recognizer import (
                    Intent,
                    IntentType,
                )

                llm_intent = Intent(
                    name=llm_result["intent_name"],
                    confidence=llm_result.get("confidence", 0.7),
                    description=llm_result.get("explanation", "通过大模型分析识别"),
                    parameters=llm_result.get("parameters", {}),
                    intent_type=IntentType.WORKFLOW
                    if "work" in llm_result.get("intent_name", "").lower()
                    else IntentType.QUESTION,
                    requires_clarification=llm_result.get(
                        "requires_clarification", False
                    ),
                )

                # 如果规则匹配没有结果，返回LLM结果
                if not rule_intent:
                    return llm_intent

                # 如果都有结果，选择置信度更高的
                rule_confidence = getattr(rule_intent, "confidence", 0.0)
                if rule_confidence > llm_intent.confidence:
                    return rule_intent
                else:
                    return llm_intent

        except Exception:
            import traceback

            traceback.print_exc()
            # 如果LLM分析失败，返回规则匹配结果（如果有的话）
            pass

        # 如果都失败，返回规则匹配结果
        return rule_intent


# 为集成论文搜索下载功能而创建的增强版本
class EnhancedWikiCollaborationEngine:
    """
    增强版维基协作引擎
    包括大模型协作和论文搜索下载的连续流程
    """

    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.hybrid_recognizer = HybridIntentRecognizer(
            llm_model_provider=model_provider
        )
        self.paper_system = AdvancedPaperSearchDownloadSystem(
            model_provider=model_provider
        )

    async def process_collaborative_wiki_request(self, user_input: str):
        """
        处理协作维基请求
        根据用户输入启动协作会话
        """
        from daip_live.multi_agent_collab.real_collaboration_engine import (
            MultiRoleWikiCollaborator,
        )

        # 使用混合意图识别器识别意图
        intent = self.hybrid_recognizer.recognize_intent(user_input)

        if intent and "wiki" in intent.name.lower():
            # 创建多角色协作编辑器
            collaborator = MultiRoleWikiCollaborator(model_provider=self.model_provider)

            # 提取标题参数
            title = intent.parameters.get("title", intent.parameters.get("query", ""))
            if not title:
                # 如果没有明确标题，尝试从用户输入中提取
                title = (
                    user_input.replace("创建维基", "")
                    .replace("写个维基", "")
                    .replace("新建维基", "")
                    .strip()
                )

            # 定义参与协作的角色
            roles = [
                "Researcher_Agent",  # 研究专家
                "Writer_Agent",  # 写作专家
                "Fact_Checker_Agent",  # 事实核查员
                "Editor_Agent",  # 编辑专家
            ]

            # 启动协作会话
            await collaborator.start_collaboration(
                title=title or "未命名维基",
                participants=roles,
                initial_content=f"关于 '{title}' 的协作维基内容",
            )

            # 运行一轮协作编辑
            contributions = await collaborator.execute_collaborative_round(["overview"])

            # 保存内容
            save_path = await collaborator.save_wiki_content()

            return {
                "success": True,
                "session_id": collaborator.session_id,
                "title": collaborator.title,
                "contributions_count": len(contributions),
                "roles_involved": roles,
                "save_path": save_path,
                "content_preview": collaborator.content.get("overview", "")[:200]
                + "...",
            }

        return {"success": False, "message": "不是维基协作请求"}

    async def process_paper_search_download_request(self, user_input: str):
        """
        处理论文搜索下载请求
        执行从关键词扩展到搜索再到下载的连续流程
        """
        intent = self.hybrid_recognizer.recognize_intent(user_input)

        if intent and (
            "download" in intent.name.lower()
            or "search" in intent.name.lower()
            or "paper" in intent.name.lower()
        ):
            # 获取查询参数
            search_query = intent.parameters.get(
                "search_query", intent.parameters.get("query", "")
            )
            if not search_query:
                # 尝试从用户输入中提取
                search_query = (
                    user_input.replace("下载论文", "")
                    .replace("搜索论文", "")
                    .replace("查找论文", "")
                    .strip()
                )

            if not search_query:
                return {
                    "success": False,
                    "requires_clarification": True,
                    "message": "请提供论文搜索关键词或arXiv ID",
                }

            # 执行搜索-下载流水线
            pipeline_result = await self.paper_system.search_and_download_pipeline(
                search_query
            )

            return pipeline_result

        return {"success": False, "message": "不是论文处理请求"}


if __name__ == "__main__":
    pass
