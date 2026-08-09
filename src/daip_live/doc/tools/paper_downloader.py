"""
Enhanced paper download and management tools.
Supports arXiv, PubMed, and web-based paper retrieval with metadata extraction.
"""

import asyncio
import re
from pathlib import Path

# Import the arxiv library if available
try:
    import arxiv

    ARXIV_AVAILABLE = True
except ImportError:
    ARXIV_AVAILABLE = False
    arxiv = None

from daip_live.doc.models.document_models import (
    PaperDownloadResult,
    PaperMetadata,
    PaperSource,
)


class PaperDownloader:
    """Download academic papers from various sources."""

    def __init__(self, download_dir: str = "./papers"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)

    async def download_paper_by_topic(
        self, topic: str, source: PaperSource = PaperSource.ARXIV
    ) -> PaperDownloadResult:
        """Download paper by topic from specified source."""
        start_time = asyncio.get_event_loop().time()

        try:
            if source == PaperSource.ARXIV:
                return await self._download_from_arxiv(topic, start_time)
            elif source == PaperSource.PUBMED:
                return await self._download_from_pubmed(topic, start_time)
            elif source == PaperSource.WEB:
                return await self._download_from_web(topic, start_time)
            else:
                # Try to guess appropriate source based on topic
                return await self._smart_download(topic, start_time)

        except Exception as e:
            return PaperDownloadResult(
                paper_id=f"failed_{topic.replace(' ', '_')}",
                title=topic,
                source=source,
                success=False,
                file_path="",
                download_time=asyncio.get_event_loop().time() - start_time,
                error_message=str(e),
            )

    async def _smart_download(
        self, topic: str, start_time: float
    ) -> PaperDownloadResult:
        """Smart download that decides best source based on topic."""
        # Check if topic looks like an arXiv ID
        if self._is_arxiv_id(topic):
            result = await self._download_from_arxiv_by_id(topic, start_time)
            if result.success:
                return result

        # Otherwise search arXiv
        result = await self._download_from_arxiv(topic, start_time)
        if result.success:
            return result

        # If arXiv fails, try PubMed or web
        return await self._download_from_web(topic, start_time)

    def _is_arxiv_id(self, topic: str) -> bool:
        """Check if the topic is an arXiv ID."""
        # Common arXiv ID patterns: [1207.1234], 1207.1234, arXiv:1207.1234
        arxiv_pattern = (
            r"(?:arxiv:)?(?:[a-z-]+/\d{4}\.\d{4,5}(v\d+)?)|(?:\d{4}\.\d{4,5}(v\d+)?)"
        )
        return bool(re.match(arxiv_pattern, topic.strip(), re.IGNORECASE))

    async def _download_from_arxiv(
        self, query: str, start_time: float
    ) -> PaperDownloadResult:
        """Download paper from arXiv by search query."""
        if not ARXIV_AVAILABLE:
            return PaperDownloadResult(
                paper_id=f"arxiv_failed_{query.replace(' ', '_')}",
                title=query,
                source=PaperSource.ARXIV,
                success=False,
                file_path="",
                download_time=asyncio.get_event_loop().time() - start_time,
                error_message="arXiv library not available",
            )

        try:
            # Search for papers using arXiv API with Client (recommended approach)
            search = arxiv.Search(
                query=query,
                max_results=1,
                sort_by=arxiv.SortCriterion.Relevance,
                sort_order=arxiv.SortOrder.Descending,
            )

            # Use Client.results() method as recommended
            client = arxiv.Client()
            results = list(client.results(search))

            if not results:
                return PaperDownloadResult(
                    paper_id=f"arxiv_no_results_{query.replace(' ', '_')}",
                    title=query,
                    source=PaperSource.ARXIV,
                    success=False,
                    file_path="",
                    download_time=asyncio.get_event_loop().time() - start_time,
                    error_message="No papers found matching query",
                )

            paper = results[0]  # Get the first result

            # Create download directory for this paper
            paper_dir = self.download_dir / "arxiv"
            paper_dir.mkdir(exist_ok=True)

            # Clean title for filename
            clean_title = "".join(
                c for c in paper.title if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            clean_title = clean_title[:100]  # Limit filename length

            # Download the PDF
            filename = f"{clean_title}.pdf"
            file_path = paper_dir / filename
            paper.download_pdf(dirpath=str(paper_dir), filename=filename)

            # Create metadata
            metadata = PaperMetadata(
                title=paper.title,
                authors=[author.name for author in paper.authors],
                abstract=paper.summary,
                publication_date=paper.published,
                doi=paper.doi,
                arxiv_id=paper.entry_id.split("/")[-1]
                if paper.entry_id
                else paper.get_short_id(),
                url=paper.entry_id,
                categories=paper.categories,  # Use categories attribute instead of tags
                source=PaperSource.ARXIV,
                file_path=str(file_path),
            )

            return PaperDownloadResult(
                paper_id=metadata.arxiv_id or f"arxiv_{query.replace(' ', '_')}",
                title=metadata.title,
                source=PaperSource.ARXIV,
                success=True,
                file_path=str(file_path),
                metadata=metadata,
                download_time=asyncio.get_event_loop().time() - start_time,
            )

        except Exception as e:
            return PaperDownloadResult(
                paper_id=f"arxiv_error_{query.replace(' ', '_')}",
                title=query,
                source=PaperSource.ARXIV,
                success=False,
                file_path="",
                download_time=asyncio.get_event_loop().time() - start_time,
                error_message=str(e),
            )

    async def _download_from_arxiv_by_id(
        self, arxiv_id: str, start_time: float
    ) -> PaperDownloadResult:
        """Download paper from arXiv by ID."""
        if not ARXIV_AVAILABLE:
            return PaperDownloadResult(
                paper_id=arxiv_id,
                title=f"Paper {arxiv_id}",
                source=PaperSource.ARXIV,
                success=False,
                file_path="",
                download_time=asyncio.get_event_loop().time() - start_time,
                error_message="arXiv library not available",
            )

        try:
            # Clean the arXiv ID
            clean_arxiv_id = (
                arxiv_id.replace("arxiv:", "").replace("arXiv:", "").strip()
            )

            # Search for the specific paper
            search = arxiv.Search(id_list=[clean_arxiv_id])

            # Use Client.results() method as recommended
            client = arxiv.Client()
            results = list(client.results(search))

            if not results:
                return PaperDownloadResult(
                    paper_id=arxiv_id,
                    title=f"Paper {arxiv_id}",
                    source=PaperSource.ARXIV,
                    success=False,
                    file_path="",
                    download_time=asyncio.get_event_loop().time() - start_time,
                    error_message="Paper not found with provided ID",
                )

            paper = results[0]  # Get the first result

            # Create download directory for this paper
            paper_dir = self.download_dir / "arxiv"
            paper_dir.mkdir(exist_ok=True)

            # Clean title for filename
            clean_title = "".join(
                c for c in paper.title if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            clean_title = clean_title[:100]  # Limit filename length

            # Download the PDF
            filename = f"{clean_title}.pdf"
            file_path = paper_dir / filename
            paper.download_pdf(dirpath=str(paper_dir), filename=filename)

            # Create metadata
            metadata = PaperMetadata(
                title=paper.title,
                authors=[author.name for author in paper.authors],
                abstract=paper.summary,
                publication_date=paper.published,
                doi=paper.doi,
                arxiv_id=paper.entry_id.split("/")[-1] if paper.entry_id else arxiv_id,
                url=paper.entry_id,
                categories=paper.categories,  # Use categories attribute instead of tags
                source=PaperSource.ARXIV,
                file_path=str(file_path),
            )

            return PaperDownloadResult(
                paper_id=metadata.arxiv_id or arxiv_id,
                title=metadata.title,
                source=PaperSource.ARXIV,
                success=True,
                file_path=str(file_path),
                metadata=metadata,
                download_time=asyncio.get_event_loop().time() - start_time,
            )

        except Exception as e:
            return PaperDownloadResult(
                paper_id=arxiv_id,
                title=f"Paper {arxiv_id}",
                source=PaperSource.ARXIV,
                success=False,
                file_path="",
                download_time=asyncio.get_event_loop().time() - start_time,
                error_message=str(e),
            )

    async def _download_from_pubmed(
        self, query: str, start_time: float
    ) -> PaperDownloadResult:
        """Download paper from PubMed."""
        # This would require pubmed-api or similar - stubbing for now
        return PaperDownloadResult(
            paper_id=f"pubmed_stub_{query.replace(' ', '_')}",
            title=query,
            source=PaperSource.PUBMED,
            success=False,
            file_path="",
            download_time=asyncio.get_event_loop().time() - start_time,
            error_message="PubMed download not implemented yet",
            warnings=[
                "PubMed download functionality is planned but not yet implemented"
            ],
        )

    async def _download_from_web(
        self, query: str, start_time: float
    ) -> PaperDownloadResult:
        """Download paper from web sources."""
        # For now, this is a stub - would implement more sophisticated web scraping
        return PaperDownloadResult(
            paper_id=f"web_stub_{query.replace(' ', '_')}",
            title=query,
            source=PaperSource.WEB,
            success=False,
            file_path="",
            download_time=asyncio.get_event_loop().time() - start_time,
            error_message="Web download not implemented yet",
            warnings=["Web download functionality is planned but not yet implemented"],
        )

    async def search_papers(
        self, query: str, source: PaperSource = PaperSource.ARXIV, max_results: int = 5
    ) -> list[PaperMetadata]:
        """Search for papers without downloading them."""
        if not ARXIV_AVAILABLE:
            return []

        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance,
                sort_order=arxiv.SortOrder.Descending,
            )

            # Use Client.results() method as recommended
            client = arxiv.Client()

            results = []
            for paper in client.results(search):
                metadata = PaperMetadata(
                    title=paper.title,
                    authors=[author.name for author in paper.authors],
                    abstract=paper.summary,
                    publication_date=paper.published,
                    doi=paper.doi,
                    arxiv_id=paper.entry_id.split("/")[-1]
                    if paper.entry_id
                    else paper.get_short_id(),
                    url=paper.entry_id,
                    categories=paper.categories,  # Use categories attribute instead of tags  # noqa: E501
                    source=PaperSource.ARXIV,
                )
                results.append(metadata)

            return results

        except Exception:
            return []


class EnhancedDebatePaperManager:
    """Enhanced paper manager with debate-specific features."""

    def __init__(self, download_dir: str = "./papers"):
        self.downloader = PaperDownloader(download_dir=download_dir)
        self._downloaded_papers: dict[str, PaperMetadata] = {}
        self._search_cache: dict[str, list[PaperMetadata]] = {}

    async def download_paper_for_debate(
        self, topic: str, roles: list[str]
    ) -> PaperDownloadResult:
        """Download paper for debate preparation."""
        # This is for internal tracking, not for direct event emission
        # In this tool, we just return appropriate results

        # Search for papers related to the topic
        results = await self.downloader.search_papers(topic, max_results=3)

        if not results:
            return PaperDownloadResult(
                paper_id=f"none_found_{topic.replace(' ', '_')}",
                title=topic,
                source=PaperSource.LOCAL,
                success=False,
                file_path="",
                download_time=0.0,
                error_message="No papers found for debate topic",
            )

        # Select the most relevant paper
        selected_paper = results[0]

        # For now, return the first result as if it was downloaded
        return PaperDownloadResult(
            paper_id=selected_paper.arxiv_id or f"selected_{topic.replace(' ', '_')}",
            title=selected_paper.title,
            source=selected_paper.source,
            success=True,
            file_path=selected_paper.file_path if selected_paper.file_path else "",
            metadata=selected_paper,
            download_time=0.0,
        )

    def get_available_sources(self) -> list[PaperSource]:
        """Get list of available paper sources."""
        sources = [PaperSource.LOCAL]

        if ARXIV_AVAILABLE:
            sources.append(PaperSource.ARXIV)

        sources.extend([PaperSource.PUBMED, PaperSource.WEB])
        return sources
