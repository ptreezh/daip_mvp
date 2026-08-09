"""
论文下载工具

遵循TDD RED-GREEN-REFACTOR循环开发
"""

import hashlib
import json
import logging
import re
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

import requests


@dataclass
class PaperMetadata:
    """论文元数据"""

    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    published_date: datetime
    categories: list[str]
    pdf_url: str
    doi: Optional[str] = None
    comments: Optional[str] = None
    journal_ref: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        data["published_date"] = self.published_date.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PaperMetadata":
        """从字典创建"""
        data["published_date"] = datetime.fromisoformat(data["published_date"])
        return cls(**data)


@dataclass
class DownloadResult:
    """下载结果"""

    arxiv_id: str
    success: bool
    pdf_path: Path
    metadata_path: Path
    message: str = ""
    error_message: Optional[str] = None
    download_time: Optional[float] = None


class PaperDownloader:
    """论文下载器"""

    def __init__(
        self,
        download_dir: Path,
        max_retries: int = 3,
        timeout: int = 30,
        enable_cache: bool = True,
        cache_ttl: int = 3600,
    ):
        """初始化论文下载器"""
        self.download_dir = Path(download_dir)
        self.max_retries = max_retries
        self.timeout = timeout
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl  # 缓存生存时间（秒）

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"  # noqa: E501
            }
        )
        self.arxiv_api_base = "http://export.arxiv.org/api/query"
        self.arxiv_pdf_base = "http://arxiv.org/pdf/"

        # 设置日志
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # 缓存设置
        self.cache_dir = self.download_dir / ".cache"
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.warning(f"创建缓存目录失败: {str(e)}")
            self.enable_cache = False

    def search_arxiv(
        self, query: str, max_results: int = 10, categories: Optional[list[str]] = None
    ) -> list[PaperMetadata]:
        """智能搜索arXiv论文 - 支持关键词扩展和渐进式搜索"""
        try:
            # 第一步：尝试原始查询
            original_results = self._search_with_query(query, max_results, categories)
            if original_results:
                self.logger.info(f"原始查询找到 {len(original_results)} 个结果")
                return original_results[:max_results]

            # 第二步：关键词扩展搜索
            expanded_queries = self._expand_search_query(query)
            self.logger.info(f"扩展查询关键词: {expanded_queries}")

            all_results = []
            for expanded_query in expanded_queries:
                expanded_results = self._search_with_query(
                    expanded_query, max_results, categories
                )
                if expanded_results:
                    self.logger.info(
                        f"扩展查询 '{expanded_query}' 找到 {len(expanded_results)} 个结果"  # noqa: E501
                    )
                    all_results.extend(expanded_results)
                    if len(all_results) >= max_results:
                        break

            if all_results:
                # 去重和排序
                unique_results = self._deduplicate_and_rank(all_results, query)
                self.logger.info(f"扩展搜索总共找到 {len(unique_results)} 个唯一结果")
                return unique_results[:max_results]

            # 第三步：宽泛搜索（如果前面都失败）
            broad_results = self._broad_search(query, max_results)
            if broad_results:
                self.logger.info(f"宽泛搜索找到 {len(broad_results)} 个结果")
                return broad_results[:max_results]

            self.logger.warning(f"所有搜索策略都未找到匹配的论文，查询: {query}")
            return []

        except Exception as e:
            self.logger.error(f"搜索失败: {str(e)}")
            return []

    def _search_with_query(
        self, query: str, max_results: int, categories: Optional[list[str]] = None
    ) -> list[PaperMetadata]:
        """使用指定查询进行搜索"""
        try:
            search_query = query
            if categories:
                category_filter = " OR ".join([f"cat:{cat}" for cat in categories])
                search_query = f"({query}) AND ({category_filter})"

            params = {
                "search_query": f"all:{search_query}",  # 修复：添加all:前缀
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
                "sortOrder": "descending",
            }

            self.logger.debug(f"执行搜索查询: {search_query}")
            response = self._make_request_with_retry(self.arxiv_api_base, params=params)
            results = self._parse_arxiv_response(response.text)
            self.logger.debug(f"查询 '{search_query}' 返回 {len(results)} 个结果")
            return results
        except Exception as e:
            self.logger.error(f"查询 '{query}' 搜索失败: {str(e)}")
            return []

    def _expand_search_query(self, original_query: str) -> list[str]:
        """扩展搜索查询关键词"""
        expansions = []

        # 英文关键词扩展映射
        keyword_expansions = {
            "机器学习": ["machine learning", "ML", "artificial intelligence", "AI"],
            "深度学习": [
                "deep learning",
                "neural network",
                "deep neural network",
                "DNN",
            ],
            "人工智能": ["artificial intelligence", "AI", "machine intelligence"],
            "神经网络": ["neural network", "neural networks", "NN", "connectionist"],
            "自然语言处理": [
                "natural language processing",
                "NLP",
                "computational linguistics",
            ],
            "计算机视觉": [
                "computer vision",
                "CV",
                "image recognition",
                "visual recognition",
            ],
            "强化学习": ["reinforcement learning", "RL", "reward learning"],
            "数据挖掘": ["data mining", "knowledge discovery", "KDD"],
            "大数据": ["big data", "large scale data", "massive data"],
            "算法": ["algorithm", "algorithms", "computational method"],
            "模型": ["model", "modeling", "framework"],
            "优化": ["optimization", "optimal", "optimize"],
            "分类": ["classification", "categorization", "classifying"],
            "回归": ["regression", "prediction", "predictive modeling"],
            "聚类": ["clustering", "cluster analysis", "unsupervised learning"],
            "生成": ["generation", "generative", "synthesis"],
            "检测": ["detection", "detecting", "recognition"],
            "分割": ["segmentation", "segmenting", "partitioning"],
            "推荐": ["recommendation", "recommender", "collaborative filtering"],
            "搜索": ["search", "retrieval", "information retrieval"],
            "图": ["graph", "network", "graphical"],
            "树": ["tree", "hierarchical", "tree structure"],
            "序列": ["sequence", "sequential", "temporal"],
            "时间": ["time", "temporal", "time series"],
            "空间": ["spatial", "space", "geometric"],
            "概率": ["probability", "probabilistic", "stochastic"],
            "统计": ["statistics", "statistical", "analysis"],
            "分布式": ["distributed", "parallel", "decentralized"],
            "云计算": ["cloud computing", "cloud", "distributed computing"],
            "安全": ["security", "secure", "cryptography"],
            "隐私": ["privacy", "private", "confidential"],
        }

        # 生成扩展查询
        for chinese, english_list in keyword_expansions.items():
            if chinese in original_query:
                for english in english_list:
                    # 替换中文关键词为英文
                    expanded_query = original_query.replace(chinese, english)
                    if expanded_query not in expansions:
                        expansions.append(expanded_query)

                    # 添加英文关键词作为补充
                    combined_query = f"{original_query} {english}"
                    if combined_query not in expansions:
                        expansions.append(combined_query)

        # 如果没有找到中文关键词，尝试英文同义词扩展
        if not expansions:
            # 常见学术词汇的同义词
            synonyms = {
                "machine": ["computational", "automated", "algorithmic"],
                "learning": ["training", "adaptation", "optimization"],
                "network": ["neural", "connectionist", "graph"],
                "analysis": ["analytics", "examination", "study"],
                "method": ["approach", "technique", "algorithm"],
                "system": ["framework", "architecture", "platform"],
                "data": ["information", "dataset", "knowledge"],
                "model": ["framework", "approach", "methodology"],
            }

            for word, synonym_list in synonyms.items():
                if word in original_query.lower():
                    for synonym in synonym_list:
                        expanded_query = original_query.lower().replace(word, synonym)
                        if expanded_query not in expansions:
                            expansions.append(expanded_query)

        return expansions[:5]  # 限制扩展查询数量

    def _broad_search(
        self, original_query: str, max_results: int
    ) -> list[PaperMetadata]:
        """宽泛搜索 - 提取核心关键词"""
        # 提取查询中的核心词汇
        words = re.findall(r"\b\w+\b", original_query.lower())

        # 过滤掉常见停用词
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "what",
            "which",
            "who",
            "when",
            "where",
            "why",
            "how",
            "all",
            "each",
            "every",
            "both",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "just",
        }

        core_words = [
            word for word in words if word not in stop_words and len(word) > 2
        ]

        if not core_words:
            return []

        # 尝试单个核心词汇搜索
        for word in core_words[:3]:  # 只尝试前3个核心词
            results = self._search_with_query(word, max_results, None)
            if results:
                self.logger.info(f"宽泛搜索 '{word}' 找到 {len(results)} 个结果")
                return results

        return []

    def _deduplicate_and_rank(
        self, results: list[PaperMetadata], original_query: str
    ) -> list[PaperMetadata]:
        """去重并按相关性排序结果"""
        # 按arXiv ID去重
        seen_ids = set()
        unique_results = []

        for result in results:
            if result.arxiv_id not in seen_ids:
                seen_ids.add(result.arxiv_id)
                unique_results.append(result)

        # 计算相关性分数并排序
        def relevance_score(paper: PaperMetadata) -> float:
            score = 0.0
            query_words = set(re.findall(r"\b\w+\b", original_query.lower()))

            # 标题匹配权重最高
            title_words = set(re.findall(r"\b\w+\b", paper.title.lower()))
            title_match = len(query_words & title_words)
            score += title_match * 3.0

            # 摘要匹配
            abstract_words = set(re.findall(r"\b\w+\b", paper.abstract.lower()))
            abstract_match = len(query_words & abstract_words)
            score += abstract_match * 1.0

            # 类别匹配
            if paper.categories:
                category_words = {cat.lower() for cat in paper.categories}
                category_match = len(query_words & category_words)
                score += category_match * 2.0

            return score

        # 按相关性分数排序
        unique_results.sort(key=relevance_score, reverse=True)
        return unique_results

    def download_arxiv_paper(
        self, arxiv_id: str, progress_callback: Optional[Callable[[float], None]] = None
    ) -> DownloadResult:
        """下载单个arXiv论文"""
        start_time = time.time()

        try:
            if not self._is_valid_arxiv_id(arxiv_id):
                return DownloadResult(
                    arxiv_id=arxiv_id,
                    success=False,
                    pdf_path=Path(""),
                    metadata_path=Path(""),
                    error_message=f"无效的arXiv ID: {arxiv_id}",
                )

            # 创建下载目录
            self.download_dir.mkdir(parents=True, exist_ok=True)

            # 提取元数据
            metadata = self.extract_arxiv_metadata(arxiv_id)

            # 生成文件路径
            pdf_filename = f"{metadata.title.replace('/', '_').replace(':', '_')}.pdf"
            pdf_path = self.download_dir / pdf_filename
            metadata_filename = (
                f"{metadata.title.replace('/', '_').replace(':', '_')}.json"
            )
            metadata_path = self.download_dir / metadata_filename

            # 检查文件是否已存在
            if pdf_path.exists() and metadata_path.exists():
                return DownloadResult(
                    arxiv_id=arxiv_id,
                    success=True,
                    pdf_path=pdf_path,
                    metadata_path=metadata_path,
                    message="论文已存在，跳过下载",
                    download_time=time.time() - start_time,
                )

            # 下载PDF
            if self._download_pdf_stream(metadata.pdf_url, pdf_path, progress_callback):
                # 保存元数据
                self.save_metadata(metadata, metadata_path)

                return DownloadResult(
                    arxiv_id=arxiv_id,
                    success=True,
                    pdf_path=pdf_path,
                    metadata_path=metadata_path,
                    message="下载成功",
                    download_time=time.time() - start_time,
                )
            else:
                return DownloadResult(
                    arxiv_id=arxiv_id,
                    success=False,
                    pdf_path=Path(""),
                    metadata_path=Path(""),
                    error_message="PDF下载失败",
                )

        except Exception as e:
            return DownloadResult(
                arxiv_id=arxiv_id,
                success=False,
                pdf_path=Path(""),
                metadata_path=Path(""),
                error_message=str(e),
                download_time=time.time() - start_time,
            )

    def download_multiple_papers(self, arxiv_ids: list[str]) -> list[DownloadResult]:
        """批量下载论文"""
        results = []
        for arxiv_id in arxiv_ids:
            result = self.download_arxiv_paper(arxiv_id)
            results.append(result)
        return results

    def download_multiple_papers_concurrent(
        self, arxiv_ids: list[str], max_workers: int = 4
    ) -> list[DownloadResult]:
        """并发下载论文"""
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_id = {
                executor.submit(self.download_arxiv_paper, arxiv_id): arxiv_id
                for arxiv_id in arxiv_ids
            }

            for future in as_completed(future_to_id):
                result = future.result()
                results.append(result)

        # 按原始顺序排列
        results_dict = {result.arxiv_id: result for result in results}
        return [results_dict[arxiv_id] for arxiv_id in arxiv_ids]

    def extract_arxiv_metadata(self, arxiv_id: str) -> PaperMetadata:
        """提取arXiv论文元数据"""
        # 首先尝试从缓存获取
        cached_metadata = self._get_cached_metadata(arxiv_id)
        if cached_metadata:
            return cached_metadata

        try:
            # 清理arXiv ID
            clean_id = arxiv_id.replace("abs/", "").replace("pdf/", "")

            params = {"search_query": f"id:{clean_id}", "start": 0, "max_results": 1}

            response = self._make_request_with_retry(self.arxiv_api_base, params=params)
            entries = self._parse_arxiv_response(response.text)

            if entries:
                metadata = entries[0]
                # 缓存元数据
                self._cache_metadata(arxiv_id, metadata)
                return metadata
            else:
                raise ValueError(f"未找到arXiv论文: {arxiv_id}")

        except Exception as e:
            self.logger.warning(f"提取元数据失败: {str(e)}")
            # 返回默认元数据
            default_metadata = PaperMetadata(
                arxiv_id=arxiv_id,
                title=f"Unknown Paper {arxiv_id}",
                authors=["Unknown"],
                abstract="Abstract not available",
                published_date=datetime.now(),
                categories=["unknown"],
                pdf_url=f"{self.arxiv_pdf_base}{arxiv_id}.pdf",
            )
            return default_metadata

    def save_metadata(
        self, metadata: PaperMetadata, metadata_path: Optional[Path] = None
    ) -> Path:
        """保存元数据"""
        if metadata_path is None:
            metadata_filename = (
                f"{metadata.title.replace('/', '_').replace(':', '_')}.json"
            )
            metadata_path = self.download_dir / metadata_filename

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata.to_dict(), f, ensure_ascii=False, indent=2)

        return metadata_path

    def load_metadata(self, metadata_path: Path) -> PaperMetadata:
        """加载元数据"""
        with open(metadata_path, encoding="utf-8") as f:
            data = json.load(f)
        return PaperMetadata.from_dict(data)

    def generate_download_report(self, results: list[DownloadResult]) -> dict[str, Any]:
        """生成下载报告"""
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        total_time = sum(r.download_time or 0 for r in results)

        return {
            "total_papers": len(results),
            "successful_downloads": len(successful),
            "failed_downloads": len(failed),
            "download_time": total_time,
            "success_rate": len(successful) / len(results) if results else 0,
            "failed_ids": [r.arxiv_id for r in failed],
            "successful_ids": [r.arxiv_id for r in successful],
        }

    def _is_valid_arxiv_id(self, arxiv_id: str) -> bool:
        """验证arXiv ID格式"""
        # 简化的arXiv ID验证
        patterns = [
            r"^\d{4}\.\d{4,5}$",  # 新格式: 2301.07041
            r"^[a-z\.\-]+/\d{4}\.\d{4,5}$",  # 旧格式: cs.AI/2301.07041
            r"^[a-z\.\-]+/\d{7}$",  # 最旧格式: hep-th/9901001
        ]

        for pattern in patterns:
            if re.match(pattern, arxiv_id, re.IGNORECASE):
                return True
        return False

    def _download_pdf_stream(
        self,
        url: str,
        local_path: Path,
        progress_callback: Optional[Callable[[float], None]] = None,
    ) -> bool:
        """下载PDF流"""
        try:
            response = self._make_request_with_retry(url, stream=True)

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if progress_callback and total_size > 0:
                            progress = downloaded / total_size
                            progress_callback(min(progress, 1.0))

            return True

        except Exception as e:
            # 清理不完整的文件
            if local_path.exists():
                local_path.unlink()
            self.logger.error(f"下载失败: {str(e)}")
            return False

    def _make_request_with_retry(
        self,
        url: str,
        method: str = "GET",
        params: Optional[dict] = None,
        stream: bool = False,
    ) -> requests.Response:
        """带重试机制的HTTP请求"""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                if stream:
                    response = self.session.get(
                        url, params=params, stream=True, timeout=self.timeout
                    )
                else:
                    response = self.session.get(
                        url, params=params, timeout=self.timeout
                    )

                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait_time = 2**attempt  # 指数退避
                    self.logger.warning(
                        f"请求失败，{wait_time}秒后重试 (尝试 {attempt + 1}/{self.max_retries + 1}): {str(e)}"  # noqa: E501
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"请求最终失败: {str(e)}")

        raise last_exception

    def _parse_arxiv_response(self, xml_content: str) -> list[PaperMetadata]:
        """解析arXiv API响应"""
        try:
            root = ET.fromstring(xml_content)
            entries = []

            # 定义命名空间
            namespaces = {
                "atom": "http://www.w3.org/2005/Atom",
                "arxiv": "http://arxiv.org/schemas/atom",
            }

            for entry in root.findall("atom:entry", namespaces):
                # 提取基本信息
                arxiv_id = entry.find("arxiv:id", namespaces)
                if arxiv_id is None:
                    continue

                id_text = arxiv_id.text
                # 提取arXiv ID，格式可能是 http://arxiv.org/abs/2301.00001
                if "arxiv.org/abs/" in id_text:
                    arxiv_id = id_text.split("arxiv.org/abs/")[-1]
                else:
                    arxiv_id = id_text.split("/")[-1]  # 获取ID部分

                title = entry.find("atom:title", namespaces)
                title = title.text.strip() if title is not None else "Unknown Title"

                abstract = entry.find("atom:summary", namespaces)
                abstract = (
                    abstract.text.strip()
                    if abstract is not None
                    else "Abstract not available"
                )

                # 提取作者
                authors = []
                for author in entry.findall("atom:author", namespaces):
                    name = author.find("atom:name", namespaces)
                    if name is not None:
                        authors.append(name.text)

                # 提取发布日期
                published = entry.find("atom:published", namespaces)
                if published is not None:
                    published_date = datetime.fromisoformat(
                        published.text.replace("Z", "+00:00")
                    )
                else:
                    published_date = datetime.now()

                # 提取分类
                categories = []
                for category in entry.findall("atom:category", namespaces):
                    if category.get("term"):
                        categories.append(category.get("term"))

                # 构建PDF URL
                pdf_url = f"{self.arxiv_pdf_base}{arxiv_id}.pdf"

                # 提取其他信息
                doi = None
                for link in entry.findall("atom:link", namespaces):
                    if link.get("title") == "doi":
                        doi = link.get("href")
                        break

                metadata = PaperMetadata(
                    arxiv_id=arxiv_id,
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    published_date=published_date,
                    categories=categories,
                    pdf_url=pdf_url,
                    doi=doi,
                )

                entries.append(metadata)

            return entries

        except Exception as e:
            self.logger.error(f"解析arXiv响应失败: {str(e)}")
            return []

    def _get_cache_key(self, data: str) -> str:
        """生成缓存键"""
        return hashlib.md5(data.encode()).hexdigest()

    def _get_cached_metadata(self, arxiv_id: str) -> Optional[PaperMetadata]:
        """获取缓存的元数据"""
        if not self.enable_cache:
            return None

        cache_key = self._get_cache_key(f"arxiv_{arxiv_id}")
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, encoding="utf-8") as f:
                    cache_data = json.load(f)

                # 检查缓存是否过期
                cache_time = datetime.fromisoformat(cache_data["cached_at"])
                if (datetime.now() - cache_time).seconds < self.cache_ttl:
                    self.logger.debug(f"使用缓存元数据: {arxiv_id}")
                    return PaperMetadata.from_dict(cache_data["metadata"])
                else:
                    # 删除过期缓存
                    cache_file.unlink()

            except Exception as e:
                self.logger.warning(f"读取缓存失败: {str(e)}")

        return None

    def _cache_metadata(self, arxiv_id: str, metadata: PaperMetadata) -> None:
        """缓存元数据"""
        if not self.enable_cache:
            return

        cache_key = self._get_cache_key(f"arxiv_{arxiv_id}")
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            cache_data = {
                "cached_at": datetime.now().isoformat(),
                "metadata": metadata.to_dict(),
            }

            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            self.logger.debug(f"缓存元数据: {arxiv_id}")

        except Exception as e:
            self.logger.warning(f"缓存元数据失败: {str(e)}")

    def clear_cache(self) -> int:
        """清理缓存"""
        if not self.enable_cache:
            return 0

        cache_files = list(self.cache_dir.glob("*.json"))
        count = 0

        for cache_file in cache_files:
            try:
                cache_file.unlink()
                count += 1
            except Exception as e:
                self.logger.warning(f"删除缓存文件失败 {cache_file}: {str(e)}")

        self.logger.info(f"清理了 {count} 个缓存文件")
        return count

    def _make_request_with_retry(
        self, url: str, params: Optional[dict] = None
    ) -> requests.Response:
        """带重试机制的HTTP请求"""
        for attempt in range(self.max_retries):
            try:
                self.logger.debug(f"尝试请求 {url} (第 {attempt + 1} 次)")
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"请求失败 (第 {attempt + 1} 次): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2**attempt)  # 指数退避

        raise requests.exceptions.RequestException(
            f"请求失败，已重试 {self.max_retries} 次"
        )

    def _parse_arxiv_response(self, xml_text: str) -> list[PaperMetadata]:
        """解析arXiv API响应"""
        try:
            root = ET.fromstring(xml_text)

            # 注册命名空间
            namespaces = {
                "atom": "http://www.w3.org/2005/Atom",
                "arxiv": "http://arxiv.org/schemas/atom",
                "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
            }

            entries = []
            for entry in root.findall("atom:entry", namespaces):
                # 提取基本信息
                id_elem = entry.find(
                    "atom:id", namespaces
                )  # 修改：使用atom:id而不是arxiv:id
                if id_elem is None:
                    continue

                id_text = id_elem.text
                # 提取arXiv ID，格式可能是 http://arxiv.org/abs/2301.00001
                if "arxiv.org/abs/" in id_text:
                    arxiv_id = id_text.split("arxiv.org/abs/")[-1]
                else:
                    arxiv_id = id_text.split("/")[-1]

                title = entry.find("atom:title", namespaces)
                title = title.text.strip() if title is not None else "Unknown Title"

                abstract = entry.find("atom:summary", namespaces)
                abstract = (
                    abstract.text.strip()
                    if abstract is not None
                    else "Abstract not available"
                )

                # 提取作者
                authors = []
                for author in entry.findall("atom:author", namespaces):
                    name = author.find("atom:name", namespaces)
                    if name is not None:
                        authors.append(name.text)

                # 提取发布日期
                published = entry.find("atom:published", namespaces)
                if published is not None:
                    published_date = datetime.fromisoformat(
                        published.text.replace("Z", "+00:00")
                    )
                else:
                    published_date = datetime.now()

                # 提取分类
                categories = []
                for category in entry.findall("atom:category", namespaces):
                    if category.get("term"):
                        categories.append(category.get("term"))

                # 提取PDF链接
                pdf_url = ""
                for link in entry.findall("atom:link", namespaces):
                    if link.get("title") == "pdf":
                        pdf_url = link.get("href", "")
                        break

                # 提取DOI和其他信息
                doi = None

                # 创建元数据对象
                metadata = PaperMetadata(
                    arxiv_id=arxiv_id,
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    published_date=published_date,
                    categories=categories,
                    pdf_url=pdf_url,
                    doi=doi,
                )

                entries.append(metadata)

            return entries

        except Exception as e:
            self.logger.error(f"解析arXiv响应失败: {str(e)}")
            import traceback

            self.logger.debug(traceback.format_exc())
            return []
