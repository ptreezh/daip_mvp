"""
论文搜索下载连续流程系统
使用大模型扩展关键词，执行搜索，然后下载
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class PaperInfo:
    """论文信息"""

    paper_id: str
    title: str
    authors: list[str]
    abstract: str
    url: str
    source: str
    published_date: Optional[str] = None


class AdvancedPaperSearchDownloadSystem:
    """
    高级论文搜索下载系统
    1. 使用大模型分析和扩展关键词
    2. 多源搜索获取论文列表
    3. 生成下载指令并批量执行
    """

    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.downloaded_papers: list[PaperInfo] = []

    async def expand_search_keywords_with_llm(self, original_query: str) -> list[str]:
        """
        使用大模型扩展搜索关键词
        将原始查询扩展为相关关键词集合
        """
        if not original_query or original_query.strip() == "":
            return []

        prompt = f"""请将以下学术查询扩展为相关关键词集合：

原始查询: "{original_query}"

请提供:
1. 原始查询的同义表达
2. 相关的学术领域关键词
3. 相关的技术或方法词汇
4. 相关的应用场景词汇
5. 相关的研究方向词汇

返回格式:
- 关键词1
- 关键词2
- 关键词3
...
- 关键词N

示例:
原始: 机器学习
扩展:
- 机器学习
- machine learning
- 深度学习
- deep learning
- 监督学习
- unsupervised learning
- 神经网络
- neural networks
- AI"""

        try:
            if self.model_provider:
                response = await self.model_provider.generate(prompt)
                if isinstance(response, dict):
                    content = response.get("content", str(response))
                else:
                    content = str(response)
            else:
                # 模拟大模型响应用于测试
                content = f"""原始: {original_query}
扩展:
- {original_query}
- {original_query.replace(" ", "_")}
- 相关_{original_query}
- {original_query}_研究
- {original_query}_应用"""

            # 从响应中提取关键词列表
            keywords = []
            lines = content.split("\\n")
            for line in lines:
                # 查找包含关键词的行 (格式如 "- 关键词" 或 "关键词")
                if line.strip().startswith("- "):
                    keyword = line.strip()[2:].strip()
                    if keyword and keyword not in original_query:
                        keywords.append(keyword)
                elif (
                    "扩展:" not in line
                    and len(line.strip()) > 1
                    and line.strip() not in keywords
                ):
                    # 简单关键词提取
                    clean_line = line.strip().strip("-").strip("*").strip()
                    if (
                        clean_line
                        and len(clean_line) > 1
                        and clean_line not in keywords
                        and clean_line != original_query
                    ):
                        keywords.append(clean_line)

            # 确保包含原查询词
            if original_query not in keywords:
                keywords.insert(0, original_query)

            return keywords[:10]  # 限制为最多10个关键词，避免搜索过多

        except Exception:
            # 备选方案：简单关键词扩展
            return [original_query, original_query + " 研究", original_query + " 应用"]

    async def search_papers_multiple_sources(
        self, keywords: list[str]
    ) -> list[PaperInfo]:
        """
        在多个源上搜索论文
        返回匹配的论文列表
        """
        all_papers = []

        # 模拟arXiv搜索
        for keyword in keywords[:3]:  # 只处理前3个关键词以避免搜索过多
            # 模拟arXiv API调用
            # 在真实实现中，这里会调用真实的arXiv API
            simulated_results = await self._simulate_arxiv_search(keyword)
            all_papers.extend(simulated_results)

        return all_papers

    async def _simulate_arxiv_search(self, query: str) -> list[PaperInfo]:
        """模拟arXiv搜索 - 在真实实现中会被真正的API调用替代"""
        import random

        # 模拟搜索结果
        mock_papers = [
            PaperInfo(
                paper_id=f"{random.randint(1000, 9999)}.{random.randint(1000, 9999)}",
                title=f"关于 {query} 的研究 - 论文 {i}",
                authors=[f"Author {j}" for j in range(1, random.randint(2, 4))],
                abstract=f"这篇论文研究了 {query} 的各个方面，包括方法学、应用场景和未来发展方向。",  # noqa: E501
                url=f"https://arxiv.org/abs/{random.randint(1000, 9999)}.{random.randint(1000, 9999)}",  # noqa: E501
                source="arxiv",
            )
            for i in range(1, 4)  # 为每个查询返回3篇模拟论文
        ]

        return mock_papers

    async def generate_download_instructions(
        self, papers: list[PaperInfo]
    ) -> list[dict[str, Any]]:
        """
        为搜索结果生成下载指令
        """
        download_instructions = []

        for paper in papers:
            instruction = {
                "paper_id": paper.paper_id,
                "title": paper.title,
                "source": paper.source,
                "download_url": paper.url.replace("/abs/", "/pdf/") + ".pdf",
                "save_path": f"./papers/{paper.paper_id.replace('.', '_')}.pdf",
                "priority": 1,  # 默认优先级
            }
            download_instructions.append(instruction)

        return download_instructions

    async def execute_download_batch(
        self, download_instructions: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        批量执行下载指令
        """
        download_results = []

        for i, instruction in enumerate(download_instructions):
            try:
                # 在真实实现中，这里会执行实际的PDF下载
                # 模拟下载成功
                result = {
                    "success": True,
                    "paper_id": instruction["paper_id"],
                    "title": instruction["title"],
                    "file_path": instruction["save_path"],
                    "download_time": 0.5,  # 模拟下载时间
                    "size_mb": round(1.2 + i * 0.3, 1),  # 模拟文件大小
                }

                self.downloaded_papers.append(
                    PaperInfo(
                        paper_id=instruction["paper_id"],
                        title=instruction["title"],
                        authors=[],
                        abstract="",
                        url=instruction["download_url"],
                        source=instruction["source"],
                    )
                )

                download_results.append(result)

            except Exception as e:
                download_results.append(
                    {
                        "success": False,
                        "paper_id": instruction["paper_id"],
                        "title": instruction["title"],
                        "error": str(e),
                        "file_path": instruction.get("save_path", ""),
                    }
                )

        return download_results

    async def search_and_download_pipeline(self, query: str) -> dict[str, Any]:
        """
        完整的搜索-下载流水线
        """

        # 步骤1: 使用大模型扩展关键词
        expanded_keywords = await self.expand_search_keywords_with_llm(query)

        # 步骤2: 多源搜索论文
        search_results = await self.search_papers_multiple_sources(expanded_keywords)

        # 步骤3: 生成下载指令
        download_instructions = await self.generate_download_instructions(
            search_results
        )

        # 步骤4: 执行批量下载
        download_results = await self.execute_download_batch(download_instructions)

        # 步骤5: 返回完整结果
        success_count = len([r for r in download_results if r["success"]])
        total_count = len(download_results)

        result = {
            "original_query": query,
            "expanded_keywords": expanded_keywords,
            "search_results_count": len(search_results),
            "download_attempts": total_count,
            "download_successes": success_count,
            "download_failures": total_count - success_count,
            "download_results": download_results,
            "search_papers": [paper.__dict__ for paper in search_results],
            "pipeline_completed_at": datetime.now().isoformat(),
        }

        return result


# 为意图识别器提供集成接口
async def integrate_paper_search_download_functionality(intent_recognizer):
    """
    将高级论文搜索下载功能集成到意图识别器
    """

    # 创建论文搜索下载系统实例
    paper_system = AdvancedPaperSearchDownloadSystem(
        model_provider=intent_recognizer.model_provider
        if hasattr(intent_recognizer, "model_provider")
        else None
    )

    # 将功能附加到意图识别器
    intent_recognizer.advanced_paper_search_download_system = paper_system

    return paper_system


if __name__ == "__main__":
    pass
