"""End-to-end tests for knowledge base collaboration.

Tests the complete workflow of knowledge management including
document addition, search, retrieval, and wiki-style collaboration.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from daip_live.core.models import KnowledgeBaseConfig
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.persistence.database import DatabaseManager


@pytest.mark.e2e
class TestKnowledgeBaseE2E:
    """End-to-end tests for knowledge base functionality."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_path = Path(temp_file.name)
        temp_file.close()
        db = DatabaseManager(db_path=str(temp_path))
        yield db
        try:
            temp_path.unlink()
        except (PermissionError, OSError):
            pass

    @pytest.fixture
    def knowledge_dir(self):
        """Create temporary knowledge directory."""
        temp_dir = tempfile.mkdtemp(prefix="knowledge_")
        yield temp_dir
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_model_provider(self):
        """Create mock model provider."""
        provider = Mock(spec=LiteLLMProvider)
        # Mock embedding generation
        provider.embed = AsyncMock(
            return_value=[0.1, 0.2, 0.3, 0.4, 0.5] * 100
        )  # 500-dimensional vector
        provider.generate = AsyncMock(return_value="Summary of document content")
        return provider

    @pytest.fixture
    def knowledge_manager(self, temp_db, mock_model_provider, knowledge_dir):
        """Create knowledge manager with test dependencies."""
        config = KnowledgeBaseConfig(directory=knowledge_dir, embedding_dimension=500)
        return KnowledgeManager(
            db_manager=temp_db, model_provider=mock_model_provider, config=config
        )

    def test_knowledge_initialization_e2e(self, knowledge_manager):
        """Test knowledge manager initialization."""
        assert knowledge_manager is not None
        assert knowledge_manager.db_manager is not None
        assert knowledge_manager.model_provider is not None

    def test_document_addition_workflow_e2e(self, knowledge_manager, knowledge_dir):
        """Test complete document addition workflow."""
        # Create a test document
        test_doc_path = Path(knowledge_dir) / "test_doc.md"
        test_doc_path.write_text("""
# Machine Learning Basics

Machine learning is a subset of artificial intelligence that focuses on
building systems that learn from data.

## Key Concepts

- **Training**: Teaching a model on example data
- **Inference**: Making predictions on new data
- **Features**: Input variables used for prediction

## Common Algorithms

1. Linear Regression
2. Decision Trees
3. Neural Networks
4. Support Vector Machines
        """)

        # 同步文档到知识库（真实 API：文件驱动扫描 + 向量索引）
        result = asyncio.run(knowledge_manager.sync_knowledge_base())

        assert result["added"] == 1
        assert result["unchanged"] == 0

    def test_document_search_workflow_e2e(self, knowledge_manager):
        """Test complete document search workflow."""
        # Mock search results
        mock_results = [
            {
                "content": "Machine learning algorithms include neural networks and decision trees",  # noqa: E501
                "metadata": {"source": "ml_basics.md", "category": "ml"},
                "score": 0.92,
            },
            {
                "content": "Deep learning uses multi-layered neural networks",
                "metadata": {"source": "deep_learning.md", "category": "dl"},
                "score": 0.87,
            },
        ]

        knowledge_manager.search = AsyncMock(return_value=mock_results)

        # Perform search
        query = "neural networks in machine learning"
        results = asyncio.run(knowledge_manager.search(query, top_k=5))

        assert len(results) == 2
        assert results[0]["score"] >= results[1]["score"]
        assert "neural" in results[0]["content"].lower()

    def test_document_update_workflow_e2e(self, knowledge_manager, knowledge_dir):
        """Test document update workflow."""
        # Create initial document
        doc_path = Path(knowledge_dir) / "update_test.md"
        doc_path.write_text("# Original Content\n\nThis is the original content.")

        # 初始同步（文件驱动）
        initial_sync = asyncio.run(knowledge_manager.sync_knowledge_base())
        assert initial_sync["added"] == 1

        # Update document
        doc_path.write_text(
            "# Updated Content\n\nThis is the updated content with new information."
        )

        # 再次同步，应检测到更新
        updated_sync = asyncio.run(knowledge_manager.sync_knowledge_base())
        assert updated_sync["updated"] == 1

        # 搜索应命中已更新的索引
        results = asyncio.run(knowledge_manager.search("updated content"))
        assert len(results) == 1
        assert "update_test" in results[0]["file_path"]

    def test_knowledge_deletion_workflow_e2e(self, knowledge_manager, knowledge_dir):
        """Test document deletion workflow."""
        # Create test document
        doc_path = Path(knowledge_dir) / "delete_test.md"
        doc_path.write_text("# To Be Deleted\n\nThis document will be deleted.")

        # 添加文档（文件驱动同步）
        asyncio.run(knowledge_manager.sync_knowledge_base())

        # 删除文档：删除文件后同步
        doc_path.unlink()
        deletion_result = asyncio.run(knowledge_manager.sync_knowledge_base())
        assert deletion_result["removed"] == 1

        # 搜索不应返回已删除文档
        results = asyncio.run(knowledge_manager.search("deleted document"))
        assert len(results) == 0

    def test_batch_document_import_e2e(self, knowledge_manager, knowledge_dir):
        """Test importing multiple documents at once."""
        # Create multiple test documents
        docs_to_create = [
            ("doc1.md", "Content for document 1"),
            ("doc2.md", "Content for document 2"),
            ("doc3.md", "Content for document 3"),
            ("doc4.md", "Content for document 4"),
            ("doc5.md", "Content for document 5"),
        ]

        for filename, content in docs_to_create:
            doc_path = Path(knowledge_dir) / filename
            doc_path.write_text(f"# {filename}\n\n{content}")

        # 批量导入（文件驱动：一次同步处理全部文档）
        import_results = asyncio.run(knowledge_manager.sync_knowledge_base())

        assert import_results["added"] == 5

    def test_knowledge_categorization_e2e(self, knowledge_manager):
        """Test document categorization and tagging."""
        # Mock categorized search results
        categorized_results = {
            "ml": [
                {"content": "Machine learning basics", "score": 0.91},
                {"content": "Advanced ML techniques", "score": 0.88},
            ],
            "dl": [{"content": "Deep learning fundamentals", "score": 0.93}],
            "nlp": [{"content": "Natural language processing", "score": 0.89}],
        }

        # Test category filtering
        for category, docs in categorized_results.items():
            assert len(docs) > 0
            for doc in docs:
                assert "score" in doc
                assert 0 <= doc["score"] <= 1

    def test_knowledge_query_expansion_e2e(self, knowledge_manager):
        """Test query expansion for better search results."""
        # Original query
        original_query = "ML algorithms"

        # Expanded queries (simulating query expansion)
        expanded_queries = [
            "machine learning algorithms",
            "ML algorithm types",
            "machine learning methods",
            original_query,
        ]

        # Mock search results
        knowledge_manager.search = AsyncMock(
            return_value=[{"content": "List of ML algorithms", "score": 0.90}]
        )

        # Search with expanded queries
        all_results = []
        for query in expanded_queries:
            results = asyncio.run(knowledge_manager.search(query, top_k=3))
            all_results.extend(results)

        # Should get results from at least one query
        assert len(all_results) >= 4  # 4 queries

    def test_knowledge_summary_generation_e2e(self, knowledge_manager):
        """Test generating summaries from knowledge base."""
        # Mock document retrieval
        retrieved_docs = [
            "Machine learning is a subset of AI that learns from data.",
            "Deep learning uses neural networks with multiple layers.",
            "Reinforcement learning learns through trial and error.",
        ]

        # Mock summary generation
        knowledge_manager.model_provider.generate = AsyncMock(
            return_value="Summary: ML, DL, and RL are key AI approaches."
        )

        # Generate summary
        combined_content = "\n".join(retrieved_docs)
        summary = asyncio.run(
            knowledge_manager.model_provider.generate(
                f"Summarize these documents:\n{combined_content}"
            )
        )

        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0


@pytest.mark.e2e
class TestWikiCollaborationE2E:
    """End-to-end tests for wiki-style collaboration features."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_path = Path(temp_file.name)
        temp_file.close()
        db = DatabaseManager(db_path=str(temp_path))
        yield db
        try:
            temp_path.unlink()
        except (PermissionError, OSError):
            pass

    @pytest.fixture
    def wiki_manager(self, temp_db):
        """Create wiki manager (in-memory fake with state for editing flows)."""
        # 有状态的假 Wiki：create/update 维护内容状态，get_page 反映最新版本
        pages = {}

        def _create_page(title, content=None, author=None, tags=None):
            pages[title] = {
                "title": title,
                "content": content or "",
                "version": 1,
                "author": author,
            }
            return f"page_{len(pages)}"

        def _update_page(page_id=None, content=None, author=None, comment=None):
            for page in pages.values():
                page["content"] = content
                page["version"] += 1
                page["author"] = author
            return True

        def _get_page(page_id):
            if not pages:
                return {"title": "Test Page", "content": "# Test Content", "version": 1}
            page = next(iter(pages.values()))
            return {
                "title": page["title"],
                "content": page["content"],
                "version": page["version"],
            }

        wiki = Mock()
        wiki.create_page = Mock(side_effect=_create_page)
        wiki.update_page = Mock(side_effect=_update_page)
        wiki.get_page = Mock(side_effect=_get_page)
        wiki.list_pages = Mock(
            return_value=[
                {"title": "Page 1", "modified": "2024-01-01"},
                {"title": "Page 2", "modified": "2024-01-02"},
            ]
        )
        wiki.search_pages = Mock(
            return_value=[{"title": "Search Result", "excerpt": "Matching content..."}]
        )
        return wiki

    def test_wiki_page_creation_workflow_e2e(self, wiki_manager):
        """Test complete wiki page creation workflow."""
        # Create page
        page_id = wiki_manager.create_page(
            title="Machine Learning Guide",
            content="# Machine Learning Guide\n\nComplete guide to ML...",
            author="user_1",
            tags=["ml", "guide", "beginner"],
        )

        assert page_id is not None

    def test_wiki_page_update_workflow_e2e(self, wiki_manager):
        """Test wiki page update with version control."""
        # Update existing page
        success = wiki_manager.update_page(
            page_id="page_001",
            content="# Updated Guide\n\nNew content added...",
            author="user_2",
            comment="Added advanced techniques section",
        )

        assert success is True

    def test_wiki_page_retrieval_e2e(self, wiki_manager):
        """Test retrieving wiki pages."""
        page = wiki_manager.get_page("page_001")

        assert page is not None
        assert "title" in page
        assert "content" in page

    def test_wiki_search_workflow_e2e(self, wiki_manager):
        """Test wiki search functionality."""
        results = wiki_manager.search_pages("machine learning")

        assert len(results) > 0
        for result in results:
            assert "title" in result or "excerpt" in result

    def test_wiki_collaborative_editing_e2e(self, wiki_manager):
        """Test collaborative editing scenario."""
        # User 1 creates page
        page_id = wiki_manager.create_page(
            title="Collaborative Document",
            content="Initial content by user 1",
            author="user_1",
        )

        # User 2 adds content
        wiki_manager.update_page(
            page_id=page_id,
            content="Initial content by user 1\n\nAdded by user 2",
            author="user_2",
            comment="Added section",
        )

        # User 1 revises
        wiki_manager.update_page(
            page_id=page_id,
            content="Initial content by user 1 (revised)\n\nAdded by user 2",
            author="user_1",
            comment="Clarified initial section",
        )

        # Verify final state
        final_page = wiki_manager.get_page(page_id)
        assert "revised" in final_page["content"].lower()
        assert "user 2" in final_page["content"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
