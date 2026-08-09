"""
论文搜索下载连续流程实现
文件: advanced_paper_search_download_engine.py
实现从关键词搜索到论文下载的完整连续流程
"""

import asyncio
import re
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
    keywords: Optional[list[str]] = None


class AdvancedPaperSearchDownloadSystem:
    """
    高级论文搜索下载系统
    实现从关键词扩展到搜索再到下载的连续流程
    """

    def __init__(self, model_provider=None):
        self.model_provider = model_provider
        self.downloaded_papers = []
        self.search_history = []

    async def expand_search_keywords_with_llm(self, original_query: str) -> list[str]:
        """
        使用大模型扩展搜索关键词
        基于原始查询产生相关关键词集合
        """
        prompt = f"""请将以下学术查询扩展为相关关键词集合：

原始查询: "{original_query}"

请提供相关的搜索关键词，包括:
1. 原始查询的同义表达
2. 相关的学术领域关键词
3. 相关的技术或方法词汇
4. 相关的应用场景词汇
5. 相关的研究方向词汇

返回格式: 每行一个关键词

示例输入: "机器学习"
示例输出:
- 机器学习
- machine learning
- 深度学习
- deep learning
- 监督学习
- unsupervised learning
- 神经网络
- neural networks"""

        try:
            if self.model_provider:
                response = await self.model_provider.generate(prompt)
                content = response if isinstance(response, str) else str(response)
            else:
                # 模拟大模型响应用于测试
                content = f"""{original_query}
{original_query.replace("学习", "训练")}
{original_query.replace("学习", "算法")}
{original_query.replace("机", "人工").replace("器", "智")}
相关_{original_query}
{original_query}_综述
{original_query}_应用
{original_query}_技术"""

            # 从响应中提取关键词列表
            keywords = []
            lines = content.split("\\n")
            for line in lines:
                # 提取关键词（移除前缀如"- "或"1. "）
                clean_line = re.sub(r"^[\d\-\*\s\.]+\s*", "", line.strip())
                if clean_line and len(clean_line) > 1 and clean_line not in keywords:
                    keywords.append(clean_line)

            # 确保原始查询词也在列表中
            if original_query not in keywords:
                keywords.insert(0, original_query)

            return keywords[:10]  # 限制为最多10个关键词

        except Exception:
            # 备选方案：简单的关键词扩展
            return [original_query]

    async def search_papers_multiple_sources(
        self, keywords: list[str], max_results: int = 5
    ) -> list[PaperInfo]:
        """
        在多个源上搜索论文
        """
        all_papers = []

        # 简化模拟多个源的搜索
        for keyword in keywords[:3]:  # 只搜索前3个关键词，避免搜索太多
            # 模拟arXiv搜索
            try:
                # 在真实实现中这里是调用arXiv API
                papers = await self._simulate_arxiv_search(keyword, max_results)
                all_papers.extend(papers)
            except Exception:
                pass

        return all_papers

    async def _simulate_arxiv_search(
        self, query: str, max_results: int = 5
    ) -> list[PaperInfo]:
        """模拟arXiv搜索 - 在真实实现中会被真正的API调用替代"""
        import random

        # 生成模拟搜索结果
        mock_papers = []
        for i in range(min(max_results, 3)):  # 最多模拟3篇论文
            paper = PaperInfo(
                paper_id=f"{random.randint(1000, 9999)}.{random.randint(1000, 9999)}",
                title=f"{query}的相关研究 - 论文{i + 1}",
                authors=[
                    f"Author_{random.choice(['A', 'B', 'C'])}",
                    f"Author_{random.choice(['D', 'E', 'F'])}",
                ],
                abstract=f"这篇论文探讨了{query}的多个方面，包括技术细节、应用案例和未来发展方向。研究显示{query}在现代技术发展中具有重要作用。",
                url=f"https://arxiv.org/abs/{random.randint(1000, 9999)}.{random.randint(1000, 9999)}",  # noqa: E501
                source="arxiv",
                published_date=f"{random.randint(2020, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",  # noqa: E501
                keywords=[query, f"related_to_{query}".replace(" ", "_")],
            )
            mock_papers.append(paper)

        return mock_papers

    async def select_papers_for_download(
        self, search_results: list[PaperInfo]
    ) -> list[PaperInfo]:
        """
        选择要下载的论文
        基于相关性排序和用户选择
        """
        if not search_results:
            return []

        # 按相关性排序（这里简化为按标题包含关键词的程度）
        def calculate_relevance(paper: PaperInfo, query: str):
            title_lower = paper.title.lower()
            query_lower = query.lower()
            # 简单计算标题中包含查询词的匹配度
            matches = sum(1 for word in query_lower.split() if word in title_lower)
            return matches

        # 这里需要从搜索历史中获取原始查询
        if self.search_history:
            original_query = self.search_history[-1]["query"]
            search_results.sort(
                key=lambda p: calculate_relevance(p, original_query), reverse=True
            )

        # 返回排名靠前的论文
        selected = search_results[: min(3, len(search_results))]  # 选择前3篇

        return selected

    async def download_selected_papers(
        self, papers: list[PaperInfo]
    ) -> list[dict[str, Any]]:
        """
        下载选中的论文
        """
        download_results = []

        for i, paper in enumerate(papers):
            try:
                # 模拟论文下载过程
                download_result = await self._simulate_paper_download(paper)

                download_results.append(
                    {
                        "success": True,
                        "paper_id": paper.paper_id,
                        "title": paper.title,
                        "download_path": download_result.get("path"),
                        "download_time": download_result.get("time", 0.5),
                        "size_mb": download_result.get("size", 1.5),
                    }
                )

            except Exception as e:
                download_results.append(
                    {
                        "success": False,
                        "paper_id": paper.paper_id,
                        "title": paper.title,
                        "error": str(e),
                        "download_path": None,
                    }
                )

        return download_results

    async def _simulate_paper_download(self, paper: PaperInfo) -> dict[str, Any]:
        """模拟论文下载 - 在真实实现中会被真正的下载逻辑替代"""
        import random

        # 模拟下载延迟
        await asyncio.sleep(0.2)  # 模拟网络延迟

        # 返回模拟下载结果
        return {
            "path": f"./papers/{paper.paper_id.replace('.', '_')}.pdf",
            "time": round(random.uniform(0.5, 2.0), 2),  # 下载耗时
            "size": round(random.uniform(1.0, 5.0), 1),  # 文件大小MB
        }

    async def search_and_download_pipeline(self, query: str) -> dict[str, Any]:
        """
        完整的搜索-下载流水线
        从关键词扩展到最终下载的完整连续流程
        """

        start_time = datetime.now()

        # 步骤1: 扩展关键词
        expanded_keywords = await self.expand_search_keywords_with_llm(query)

        # 步骤2: 多源搜索
        search_results = await self.search_papers_multiple_sources(
            expanded_keywords, max_results=5
        )

        # 记录搜索历史
        search_record = {
            "query": query,
            "expanded_keywords": expanded_keywords,
            "results_count": len(search_results),
            "timestamp": datetime.now(),
            "papers": [p.__dict__ for p in search_results],
        }
        self.search_history.append(search_record)

        # 步骤3: 选择论文
        selected_papers = await self.select_papers_for_download(search_results)

        # 步骤4: 执行下载
        download_results = await self.download_selected_papers(selected_papers)

        # 统计成功和失败数量
        success_count = len([r for r in download_results if r["success"]])
        total_count = len(download_results)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 生成结果
        result = {
            "original_query": query,
            "expanded_keywords": expanded_keywords,
            "search_results_count": len(search_results),
            "selected_for_download": len(selected_papers),
            "download_attempts": total_count,
            "download_successes": success_count,
            "download_failures": total_count - success_count,
            "download_results": download_results,
            "search_duration": duration,
            "completed_at": end_time.isoformat(),
            "all_search_results": [p.__dict__ for p in search_results],
        }

        return result


async def integrate_with_intent_recognizer(
    recognizer, paper_system=None, model_provider=None
):
    """
    将论文搜索下载系统集成到意图识别器
    """
    if not paper_system:
        paper_system = AdvancedPaperSearchDownloadSystem(model_provider=model_provider)

    # 将系统附加到意图识别器
    recognizer.advanced_paper_system = paper_system

    return paper_system


if __name__ == "__main__":
    pass
