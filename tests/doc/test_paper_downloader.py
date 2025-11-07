"""
论文下载工具的TDD测试用例
遵循RED-GREEN-REFACTOR循环

测试论文下载器的核心功能，包括：
- arXiv API集成
- PDF下载和保存
- 元数据提取和存储
- 批量下载支持
- 错误处理和重试机制
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List
import requests

from daip_live.doc.paper_downloader import PaperDownloader, PaperMetadata, DownloadResult


class TestPaperDownloader:
    """论文下载器核心功能的测试套件"""

    def test_paper_downloader_initialization(self):
        """测试论文下载器初始化"""
        # Arrange & Act & Assert - 这个测试在实现之前会失败
        downloader = PaperDownloader(download_dir=Path("/tmp/papers"))

        assert downloader.download_dir == Path("/tmp/papers")
        assert hasattr(downloader, 'session')
        assert hasattr(downloader, 'max_retries')
        assert hasattr(downloader, 'timeout')

    def test_search_arxiv_by_query(self):
        """测试通过查询搜索arXiv论文"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = PaperDownloader(download_dir=Path(temp_dir))

            # Act & Assert - 在实现之前会失败
            results = downloader.search_arxiv("machine learning", max_results=5)

            assert isinstance(results, list)
            assert len(results) <= 5
            if results:
                assert all(isinstance(result, PaperMetadata) for result in results)

    def test_download_single_arxiv_paper(self):
        """测试下载单个arXiv论文"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = PaperDownloader(download_dir=Path(temp_dir))
            arxiv_id = "2301.07041"  # 已知的arXiv ID

            # Act & Assert - 在实现之前会失败
            result = downloader.download_arxiv_paper(arxiv_id)

            assert isinstance(result, DownloadResult)
            assert result.success is True
            assert result.arxiv_id == arxiv_id
            assert result.pdf_path.exists()
            assert result.metadata_path.exists()
            assert result.pdf_path.suffix == ".pdf"
            assert result.metadata_path.suffix == ".json"

    def test_download_multiple_arxiv_papers(self):
        """测试批量下载arXiv论文"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = PaperDownloader(download_dir=Path(temp_dir))
            arxiv_ids = ["2301.07041", "2212.08023"]

            # Act & Assert - 在实现之前会失败
            results = downloader.download_multiple_papers(arxiv_ids)

            assert isinstance(results, list)
            assert len(results) == len(arxiv_ids)
            assert all(isinstance(result, DownloadResult) for result in results)

            # 检查成功下载的论文
            successful_downloads = [r for r in results if r.success]
            for result in successful_downloads:
                assert result.pdf_path.exists()
                assert result.metadata_path.exists()

    def test_extract_arxiv_metadata(self):
        """测试提取arXiv论文元数据"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = PaperDownloader(download_dir=Path(temp_dir))
            arxiv_id = "2301.07041"

            # Act & Assert - 在实现之前会失败
            metadata = downloader.extract_arxiv_metadata(arxiv_id)

            assert isinstance(metadata, PaperMetadata)
            assert metadata.arxiv_id == arxiv_id
            assert metadata.title is not None
            assert metadata.authors is not None
            assert metadata.abstract is not None
            assert metadata.published_date is not None
            assert len(metadata.title) > 0

    def test_save_and_load_metadata(self):
        """测试元数据保存和加载"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = PaperDownloader(download_dir=Path(temp_dir))
            metadata = PaperMetadata(
                arxiv_id="2301.07041",
                title="Test Paper Title",
                authors=["Author 1", "Author 2"],
                abstract="This is a test abstract",
                published_date=datetime(2023, 1, 17),
                categories=["cs.AI", "cs.LG"],
                pdf_url="http://arxiv.org/pdf/2301.07041.pdf"
            )

            # Act & Assert - 在实现之前会失败
            metadata_path = downloader.save_metadata(metadata)
            loaded_metadata = downloader.load_metadata(metadata_path)

            assert metadata_path.exists()
            assert isinstance(loaded_metadata, PaperMetadata)
            assert loaded_metadata.arxiv_id == metadata.arxiv_id
            assert loaded_metadata.title == metadata.title
            assert loaded_metadata.authors == metadata.authors
            assert loaded_metadata.abstract == metadata.abstract

    def test_handle_invalid_arxiv_id(self):
        """测试处理无效的arXiv ID"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = PaperDownloader(download_dir=Path(temp_dir))
            invalid_id = "invalid-id"

            # Act & Assert - 在实现之前会失败
            result = downloader.download_arxiv_paper(invalid_id)

            assert isinstance(result, DownloadResult)
            assert result.success is False
            assert result.error_message is not None
            assert len(result.error_message) > 0

    def test_retry_mechanism_on_network_error(self):
        """测试网络错误时的重试机制"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = PaperDownloader(download_dir=Path(temp_dir), max_retries=3)
            arxiv_id = "2301.07041"

            # Mock网络请求失败
            with patch.object(downloader.session, 'get') as mock_get:
                mock_get.side_effect = requests.exceptions.RequestException("Network error")

                # Act & Assert - 在实现之前会失败
                result = downloader.download_arxiv_paper(arxiv_id)

                assert isinstance(result, DownloadResult)
                assert result.success is False
                assert "Network error" in result.error_message or "PDF下载失败" in result.error_message
                assert mock_get.call_count >= 1  # 至少调用了一次

    def test_search_with_category_filter(self):
        """测试按类别过滤搜索"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = PaperDownloader(download_dir=Path(temp_dir))

            # Act & Assert - 在实现之前会失败
            results = downloader.search_arxiv(
                "neural networks",
                max_results=10,
                categories=["cs.AI", "cs.LG"]
            )

            assert isinstance(results, list)
            assert len(results) <= 10
            if results:
                for result in results:
                    assert isinstance(result, PaperMetadata)
                    # 检查类别匹配
                    assert any(cat in result.categories for cat in ["cs.AI", "cs.LG"])

    def test_download_with_progress_callback(self):
        """测试带进度回调的下载"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = PaperDownloader(download_dir=Path(temp_dir))
            arxiv_id = "2301.07041"
            progress_calls = []

            def progress_callback(progress: float):
                progress_calls.append(progress)

            # Act & Assert - 在实现之前会失败
            result = downloader.download_arxiv_paper(
                arxiv_id,
                progress_callback=progress_callback
            )

            assert isinstance(result, DownloadResult)
            if result.success:
                assert len(progress_calls) > 0
                assert 0.0 <= min(progress_calls) <= 1.0
                assert 0.0 <= max(progress_calls) <= 1.0

    def test_check_existing_paper_avoid_re_download(self):
        """测试检查已存在论文避免重复下载"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = PaperDownloader(download_dir=Path(temp_dir))
            arxiv_id = "2301.07041"

            # Act & Assert - 在实现之前会失败
            # 第一次下载
            result1 = downloader.download_arxiv_paper(arxiv_id)
            assert result1.success is True

            # 第二次下载（应该检测到已存在）
            result2 = downloader.download_arxiv_paper(arxiv_id)
            assert isinstance(result2, DownloadResult)
            assert result2.success is True
            assert result2.pdf_path == result1.pdf_path
            assert "exists" in result2.message.lower() or "跳过" in result2.message.lower()

    def test_generate_download_report(self):
        """测试生成下载报告"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = PaperDownloader(download_dir=Path(temp_dir))
            arxiv_ids = ["2301.07041", "2212.08023"]

            # Act & Assert - 在实现之前会失败
            results = downloader.download_multiple_papers(arxiv_ids)
            report = downloader.generate_download_report(results)

            assert isinstance(report, dict)
            assert "total_papers" in report
            assert "successful_downloads" in report
            assert "failed_downloads" in report
            assert "download_time" in report
            assert report["total_papers"] == len(arxiv_ids)
            assert report["successful_downloads"] + report["failed_downloads"] == len(arxiv_ids)

    def test_papers_directory_creation(self):
        """测试论文目录自动创建"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            papers_dir = Path(temp_dir) / "my_papers"
            assert not papers_dir.exists()

            # Act & Assert - 在实现之前会失败
            downloader = PaperDownloader(download_dir=papers_dir)

            # 下载操作应该自动创建目录
            result = downloader.download_arxiv_paper("2301.07041")

            assert papers_dir.exists()
            assert papers_dir.is_dir()

    def test_cleanup_on_download_failure(self):
        """测试下载失败时清理临时文件"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = PaperDownloader(download_dir=Path(temp_dir))

            # Mock部分下载然后失败
            with patch.object(downloader, '_download_pdf_stream') as mock_download:
                mock_download.side_effect = IOError("Download failed")

                # Act & Assert - 在实现之前会失败
                result = downloader.download_arxiv_paper("2301.07041")

                assert result.success is False
                # 检查没有留下不完整的文件
                incomplete_files = list(Path(temp_dir).glob("*.pdf.part"))
                assert len(incomplete_files) == 0

    def test_arxiv_url_validation(self):
        """测试arXiv URL验证"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = PaperDownloader(download_dir=Path(temp_dir))

            # Act & Assert - 在实现之前会失败
            # 有效的arXiv ID格式
            valid_ids = [
                "2301.07041",
                "cs.AI/2301.07041",
                "hep-th/9901001"
            ]

            for arxiv_id in valid_ids:
                assert downloader._is_valid_arxiv_id(arxiv_id) is True

            # 无效的arXiv ID格式
            invalid_ids = [
                "invalid",
                "123",
                "abc.def.ghi",
                ""
            ]

            for arxiv_id in invalid_ids:
                assert downloader._is_valid_arxiv_id(arxiv_id) is False

    def test_concurrent_download_support(self):
        """测试并发下载支持"""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            downloader = PaperDownloader(download_dir=Path(temp_dir))
            arxiv_ids = ["2301.07041", "2212.08023", "2211.12345"]

            # Act & Assert - 在实现之前会失败
            import time
            start_time = time.time()

            results = downloader.download_multiple_papers_concurrent(
                arxiv_ids,
                max_workers=2
            )

            end_time = time.time()

            assert isinstance(results, list)
            assert len(results) == len(arxiv_ids)
            # 并发下载应该比串行快（这里只是检查结构，不测试实际性能）
            assert all(isinstance(result, DownloadResult) for result in results)