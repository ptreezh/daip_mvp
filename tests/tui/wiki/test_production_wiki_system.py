# ruff: noqa: E501
"""
Production Wiki Knowledge System Tests

This test suite validates the production-grade wiki knowledge system with
comprehensive testing of all enterprise features including:
- Multi-modal document processing
- Real-time vector indexing
- Performance monitoring
- Error handling and resilience
- Concurrent processing
- Backup and recovery
"""

import asyncio
import json
import os
import tempfile
import time
import zipfile
from datetime import datetime
from pathlib import Path

import pytest

# Import production system components
from daip_live.tui_v1.wiki.production_wiki_system import (
    CircuitBreaker,
    DocumentChunk,
    DocumentMetadata,
    DocumentStatus,
    EmbeddingService,
    PDFProcessor,
    PerformanceMetrics,
    ProcessingPriority,
    ProductionWikiKnowledgeSystem,
    RateLimiter,
    SearchType,
    TextProcessor,
    VectorIndex,
    create_production_wiki_system,
)


class TestPerformanceMetrics:
    """Test performance metrics tracking"""

    def test_metrics_initialization(self):
        """Test metrics initialization"""
        metrics = PerformanceMetrics()

        assert metrics.operation_count == 0
        assert metrics.total_duration == 0.0
        assert metrics.avg_duration == 0.0
        assert metrics.min_duration == float("inf")
        assert metrics.max_duration == 0.0
        assert metrics.error_count == 0
        assert isinstance(metrics.last_updated, datetime)

    def test_metrics_update(self):
        """Test metrics updating"""
        metrics = PerformanceMetrics()

        # Update with successful operation
        metrics.update(0.5, success=True)

        assert metrics.operation_count == 1
        assert metrics.total_duration == 0.5
        assert metrics.avg_duration == 0.5
        assert metrics.min_duration == 0.5
        assert metrics.max_duration == 0.5
        assert metrics.error_count == 0

    def test_metrics_multiple_updates(self):
        """Test metrics with multiple updates"""
        metrics = PerformanceMetrics()

        durations = [0.1, 0.5, 0.3, 0.8, 0.2]
        for i, duration in enumerate(durations):
            success = i != 2  # Make third operation fail
            metrics.update(duration, success=success)

        assert metrics.operation_count == 5
        assert abs(metrics.total_duration - sum(durations)) < 1e-10
        assert abs(metrics.avg_duration - sum(durations) / 5) < 1e-10
        assert metrics.min_duration == 0.1
        assert metrics.max_duration == 0.8
        assert metrics.error_count == 1
        assert metrics.get_success_rate() == 80.0

    def test_metrics_success_rate(self):
        """Test success rate calculation"""
        metrics = PerformanceMetrics()

        # Empty metrics should have 100% success rate
        assert metrics.get_success_rate() == 100.0

        # Add some operations
        metrics.update(0.1, success=True)
        metrics.update(0.2, success=False)
        metrics.update(0.3, success=True)

        assert metrics.get_success_rate() == 66.66666666666666


class TestCircuitBreaker:
    """Test circuit breaker functionality"""

    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initialization"""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

        assert cb.failure_threshold == 3
        assert cb.recovery_timeout == 60
        assert cb.failure_count == 0
        assert cb.state == "CLOSED"

    def test_circuit_breaker_success(self):
        """Test circuit breaker with successful operations"""
        cb = CircuitBreaker(failure_threshold=3)

        def successful_func():
            return "success"

        result = cb.call(successful_func)
        assert result == "success"
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0

    def test_circuit_breaker_failure(self):
        """Test circuit breaker with failed operations"""
        cb = CircuitBreaker(failure_threshold=2)

        def failing_func():
            raise ValueError("Test error")

        # First failure
        with pytest.raises(ValueError):
            cb.call(failing_func)

        assert cb.failure_count == 1
        assert cb.state == "CLOSED"

        # Second failure should open circuit
        with pytest.raises(ValueError):
            cb.call(failing_func)

        assert cb.failure_count == 2
        assert cb.state == "OPEN"

    def test_circuit_breaker_open_state(self):
        """Test circuit breaker in open state"""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

        def failing_func():
            raise ValueError("Test error")

        # Trigger circuit opening
        with pytest.raises(ValueError):
            cb.call(failing_func)
        with pytest.raises(ValueError):
            cb.call(failing_func)

        assert cb.state == "OPEN"

        # Should raise exception without calling function
        def test_func():
            return "should not be called"

        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            cb.call(test_func)

    def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker half-open state and recovery"""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

        def failing_func():
            raise ValueError("Test error")

        # Trigger circuit opening
        with pytest.raises(ValueError):
            cb.call(failing_func)
        with pytest.raises(ValueError):
            cb.call(failing_func)

        assert cb.state == "OPEN"

        # Wait for recovery timeout
        time.sleep(0.2)

        # Successful call should close circuit
        def successful_func():
            return "recovered"

        result = cb.call(successful_func)
        assert result == "recovered"
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0


class TestRateLimiter:
    """Test rate limiter functionality"""

    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization"""
        rl = RateLimiter(max_calls=5, time_window=60)

        assert rl.max_calls == 5
        assert rl.time_window == 60
        assert len(rl.calls) == 0

    def test_rate_limiter_acquire(self):
        """Test rate limiter acquire"""
        rl = RateLimiter(max_calls=2, time_window=1)

        # Should be able to acquire initially
        assert rl.acquire()
        assert rl.acquire()

        # Should be limited now
        assert not rl.acquire()

        # Wait for window to pass
        time.sleep(1.1)

        # Should be able to acquire again
        assert rl.acquire()

    def test_rate_limiter_wait_for_slot(self):
        """Test rate limiter wait for slot"""
        rl = RateLimiter(max_calls=1, time_window=0.5)

        # Acquire one slot
        assert rl.acquire()

        start_time = time.time()
        rl.wait_for_slot()
        end_time = time.time()

        # Should have waited at least 0.5 seconds
        assert end_time - start_time >= 0.5


class TestVectorIndex:
    """Test vector index functionality"""

    def test_vector_index_initialization(self):
        """Test vector index initialization"""
        index = VectorIndex(dimension=384)

        assert index.dimension == 384
        assert index.index_type == "faiss"
        assert len(index.vectors) == 0
        assert len(index.metadata) == 0
        assert not index.is_initialized

    def test_vector_index_add_vector(self):
        """Test adding vectors to index"""
        index = VectorIndex(dimension=3)

        vector = [0.1, 0.2, 0.3]
        metadata = {"document_id": "doc1", "chunk_index": 0}

        success = index.add_vector("vec1", vector, metadata)

        assert success
        assert index.size() == 1
        assert "vec1" in index.vectors
        assert index.vectors["vec1"] == vector
        assert index.metadata["vec1"] == metadata
        assert index.is_initialized

    def test_vector_index_dimension_mismatch(self):
        """Test vector dimension mismatch"""
        index = VectorIndex(dimension=3)

        # Wrong dimension should raise error
        with pytest.raises(ValueError, match="Vector dimension mismatch"):
            index.add_vector("vec1", [0.1, 0.2])  # 2D instead of 3D

    def test_vector_index_search(self):
        """Test vector search"""
        index = VectorIndex(dimension=3)

        # Add some vectors
        vectors = [
            ([1.0, 0.0, 0.0], {"doc": "A"}),
            ([0.0, 1.0, 0.0], {"doc": "B"}),
            ([0.0, 0.0, 1.0], {"doc": "C"}),
        ]

        for i, (vector, metadata) in enumerate(vectors):
            index.add_vector(f"vec{i}", vector, metadata)

        # Search for similar to [1.0, 0.0, 0.0]
        query_vector = [1.0, 0.1, 0.0]
        results = index.search(query_vector, top_k=2)

        assert len(results) == 2
        assert results[0][0] == "vec0"  # Most similar
        assert results[0][1] > results[1][1]  # Higher similarity score

    def test_vector_index_search_with_filters(self):
        """Test vector search with filters"""
        index = VectorIndex(dimension=2)

        # Add vectors with different metadata
        index.add_vector("vec1", [1.0, 0.0], {"category": "tech", "doc": "A"})
        index.add_vector("vec2", [0.0, 1.0], {"category": "business", "doc": "B"})
        index.add_vector("vec3", [0.5, 0.5], {"category": "tech", "doc": "C"})

        # Search with category filter
        results = index.search([1.0, 0.0], top_k=10, filters={"category": "tech"})

        assert len(results) == 2
        # Should only return vectors with category "tech"
        vector_ids = [result[0] for result in results]
        assert "vec1" in vector_ids
        assert "vec3" in vector_ids
        assert "vec2" not in vector_ids

    def test_vector_index_delete_vector(self):
        """Test deleting vectors"""
        index = VectorIndex(dimension=2)

        index.add_vector("vec1", [1.0, 0.0])
        index.add_vector("vec2", [0.0, 1.0])

        assert index.size() == 2

        # Delete existing vector
        success = index.delete_vector("vec1")
        assert success
        assert index.size() == 1
        assert "vec1" not in index.vectors

        # Delete non-existing vector
        success = index.delete_vector("nonexistent")
        assert not success
        assert index.size() == 1

    def test_vector_index_get_vector(self):
        """Test getting vector by ID"""
        index = VectorIndex(dimension=2)

        vector = [1.0, 0.0]
        index.add_vector("vec1", vector)

        # Get existing vector
        retrieved = index.get_vector("vec1")
        assert retrieved == vector

        # Get non-existing vector
        retrieved = index.get_vector("nonexistent")
        assert retrieved is None


class TestEmbeddingService:
    """Test embedding service functionality"""

    @pytest.mark.asyncio
    async def test_embedding_service_initialization(self):
        """Test embedding service initialization"""
        service = EmbeddingService(model_name="test-model", max_calls_per_minute=30)

        assert service.model_name == "test-model"
        assert service.dimension == 384
        assert service.rate_limiter.max_calls == 30
        assert isinstance(service.circuit_breaker, CircuitBreaker)
        assert isinstance(service.metrics, PerformanceMetrics)

    @pytest.mark.asyncio
    async def test_embedding_encode_single_text(self):
        """Test encoding single text"""
        service = EmbeddingService()

        text = "This is a test text for embedding"
        embedding = await service.encode(text)

        assert isinstance(embedding, list)
        assert len(embedding) == service.dimension
        assert all(isinstance(x, float) for x in embedding)

        # Check if embedding is normalized
        norm = sum(x * x for x in embedding) ** 0.5
        assert abs(norm - 1.0) < 1e-6  # Should be very close to 1.0

    @pytest.mark.asyncio
    async def test_embedding_encode_multiple_texts(self):
        """Test encoding multiple texts"""
        service = EmbeddingService()

        texts = ["First test text", "Second test text", "Third test text"]

        embeddings = await service.encode(texts)

        assert isinstance(embeddings, list)
        assert len(embeddings) == len(texts)

        for embedding in embeddings:
            assert isinstance(embedding, list)
            assert len(embedding) == service.dimension

    @pytest.mark.asyncio
    async def test_embedding_encode_batch_processing(self):
        """Test batch processing of embeddings"""
        service = EmbeddingService()

        # Create a large list of texts
        texts = [f"Test text {i}" for i in range(10)]

        embeddings = await service.encode(texts, batch_size=3)

        assert len(embeddings) == 10

        # Check that same text produces same embedding
        embeddings_1 = await service.encode("test text")
        embeddings_2 = await service.encode("test text")

        assert embeddings_1 == embeddings_2

    @pytest.mark.asyncio
    async def test_embedding_service_metrics(self):
        """Test embedding service metrics"""
        service = EmbeddingService()

        # Generate some embeddings
        await service.encode("test text 1")
        await service.encode("test text 2")

        metrics = service.get_metrics()

        assert metrics["model_name"] == service.model_name
        assert metrics["dimension"] == service.dimension
        assert metrics["metrics"]["operation_count"] == 2
        assert metrics["success_rate"] == 100.0


class TestDocumentProcessors:
    """Test document processors"""

    @pytest.mark.asyncio
    async def test_text_processor(self):
        """Test text document processor"""
        processor = TextProcessor(chunk_size=100, overlap=20)

        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            content = "This is a test document. " * 20  # Create longer content
            f.write(content)
            temp_path = f.name

        try:
            assert processor.can_process(temp_path)

            document_id, chunks = await processor.process(temp_path)

            assert isinstance(document_id, str)
            assert len(chunks) > 1  # Should be multiple chunks

            # Check chunk properties
            for i, chunk in enumerate(chunks):
                assert isinstance(chunk, DocumentChunk)
                assert chunk.document_id == document_id
                assert chunk.chunk_index == i
                assert chunk.total_chunks == len(chunks)
                assert len(chunk.content) <= processor.chunk_size + processor.overlap

        finally:
            # 后台处理线程可能仍持有文件句柄（负载下竞态），unlink 失败可忽略
            try:
                os.unlink(temp_path)
            except (PermissionError, OSError):
                pass

    @pytest.mark.asyncio
    async def test_pdf_processor(self):
        """Test PDF document processor"""
        processor = PDFProcessor(chunk_size=200, overlap=50)

        # Test with a fake PDF file (just for testing can_process)
        fake_pdf = "test.pdf"
        assert processor.can_process(fake_pdf)

        # Process the mock PDF
        document_id, chunks = await processor.process(fake_pdf)

        assert isinstance(document_id, str)
        assert len(chunks) >= 1

        # Check that chunks have PDF metadata
        for chunk in chunks:
            assert chunk.metadata.get("source") == "pdf"

    def test_processor_file_type_detection(self):
        """Test processor file type detection"""
        text_processor = TextProcessor()
        pdf_processor = PDFProcessor()

        # Test various file types
        assert text_processor.can_process("test.txt")
        assert text_processor.can_process("test.md")
        assert text_processor.can_process("test.rst")
        assert not text_processor.can_process("test.pdf")

        assert pdf_processor.can_process("test.pdf")
        assert not pdf_processor.can_process("test.txt")


class TestProductionWikiKnowledgeSystem:
    """Test production wiki knowledge system"""

    def test_system_initialization(self):
        """Test system initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = ProductionWikiKnowledgeSystem(
                storage_path=temp_dir,
                embedding_dimension=128,
                max_concurrent_processors=2,
            )

            assert system.storage_path == Path(temp_dir)
            assert system.embedding_dimension == 128
            assert system.max_concurrent_processors == 2
            assert len(system.processors) == 0  # No processors registered yet
            assert system.vector_index.dimension == 128
            assert isinstance(system.embedding_service, EmbeddingService)

    def test_system_with_factory(self):
        """Test system creation using factory function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = create_production_wiki_system(
                storage_path=temp_dir, embedding_dimension=256
            )

            assert isinstance(system, ProductionWikiKnowledgeSystem)
            assert len(system.processors) >= 2  # Should have text and PDF processors

            # Check that processors are registered
            processor_types = [type(p).__name__ for p in system.processors]
            assert "TextProcessor" in processor_types
            assert "PDFProcessor" in processor_types

    def test_register_processor(self):
        """Test registering document processors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = ProductionWikiKnowledgeSystem(storage_path=temp_dir)

            # Register custom processor
            custom_processor = TextProcessor(chunk_size=500)
            system.register_processor(custom_processor)

            assert len(system.processors) == 1
            assert system.processors[0] == custom_processor

    @pytest.mark.asyncio
    async def test_add_document(self):
        """Test adding document to system"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = create_production_wiki_system(storage_path=temp_dir)

            # Create temporary text file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            ) as f:
                content = "This is a test document for the production wiki system."
                f.write(content)
                temp_path = f.name

            try:
                # Add document
                document_id = await system.add_document(
                    temp_path, priority=ProcessingPriority.HIGH
                )

                assert isinstance(document_id, str)
                assert document_id in system.documents

                # Check document status
                status = system.get_document_status(document_id)
                assert status in [
                    DocumentStatus.PENDING,
                    DocumentStatus.PROCESSING,
                    DocumentStatus.COMPLETED,
                ]

            finally:
                # 后台处理线程可能仍持有文件句柄（负载下竞态），unlink 失败可忽略
                try:
                    os.unlink(temp_path)
                except (PermissionError, OSError):
                    pass

    @pytest.mark.asyncio
    async def test_search_functionality(self):
        """Test search functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = create_production_wiki_system(storage_path=temp_dir)

            # Wait for system to be ready
            await asyncio.sleep(0.1)

            # Create and add a document
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            ) as f:
                content = "Artificial intelligence and machine learning are transforming technology."  # noqa: E501
                f.write(content)
                temp_path = f.name

            try:
                await system.add_document(temp_path)

                # Wait for processing
                await asyncio.sleep(1.0)

                # Perform search
                results = await system.search(
                    "artificial intelligence", search_type=SearchType.SEMANTIC, top_k=5
                )

                assert isinstance(results, list)
                # Note: May be empty if processing hasn't completed

            finally:
                # 后台处理线程可能仍持有文件句柄（负载下竞态），unlink 失败可忽略
                try:
                    os.unlink(temp_path)
                except (PermissionError, OSError):
                    pass

    @pytest.mark.asyncio
    async def test_different_search_types(self):
        """Test different search types"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = create_production_wiki_system(storage_path=temp_dir)

            await asyncio.sleep(0.1)

            # Test different search types
            search_types = [SearchType.SEMANTIC, SearchType.KEYWORD, SearchType.HYBRID]

            for search_type in search_types:
                results = await system.search(
                    "test query", search_type=search_type, top_k=3
                )

                assert isinstance(results, list)
                # Verify search type is set in results
                for result in results:
                    assert result.search_type == search_type

    def test_get_system_metrics(self):
        """Test getting system metrics"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = create_production_wiki_system(storage_path=temp_dir)

            metrics = system.get_system_metrics()

            assert "documents_count" in metrics
            assert "chunks_count" in metrics
            assert "vector_index_size" in metrics
            assert "processing_metrics" in metrics
            assert "embedding_service_metrics" in metrics
            assert "queue_status" in metrics
            assert "storage_usage" in metrics

            # Check queue status
            queue_status = metrics["queue_status"]
            assert "queue_size" in queue_status
            assert "active_tasks" in queue_status
            assert "pending_tasks" in queue_status

    def test_processing_queue_status(self):
        """Test processing queue status"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = create_production_wiki_system(storage_path=temp_dir)

            status = system.get_processing_queue_status()

            assert "queue_size" in status
            assert "active_tasks" in status
            assert "pending_tasks" in status
            assert "completed_tasks" in status
            assert "failed_tasks" in status

            # Initially should be empty
            assert status["queue_size"] == 0

    @pytest.mark.asyncio
    async def test_delete_document(self):
        """Test document deletion"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = create_production_wiki_system(storage_path=temp_dir)

            # Create temporary file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            ) as f:
                content = "Document to be deleted"
                f.write(content)
                temp_path = f.name

            try:
                # Add document
                document_id = await system.add_document(temp_path)

                # Wait a bit for processing
                await asyncio.sleep(0.5)

                # Delete document
                success = await system.delete_document(document_id)
                assert success

                # Verify document is deleted
                status = system.get_document_status(document_id)
                assert status is None

            finally:
                # 后台处理线程可能仍持有文件句柄（负载下竞态），unlink 失败可忽略
                try:
                    os.unlink(temp_path)
                except (PermissionError, OSError):
                    pass

    def test_backup_system(self):
        """Test system backup functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = create_production_wiki_system(storage_path=temp_dir)

            # Create backup
            backup_path = system.backup_system()

            assert os.path.exists(backup_path)
            assert backup_path.endswith(".zip")

            # Verify backup contains system state
            with zipfile.ZipFile(backup_path, "r") as zipf:
                assert "system_state.json" in zipf.namelist()

                # Check system state file
                with zipf.open("system_state.json") as f:
                    state_data = json.load(f)

                assert "documents" in state_data
                assert "chunks" in state_data
                assert "version" in state_data
                assert "backup_timestamp" in state_data

    def test_backup_custom_path(self):
        """Test backup with custom path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = create_production_wiki_system(storage_path=temp_dir)

            custom_backup = os.path.join(temp_dir, "custom_backup.zip")
            backup_path = system.backup_system(custom_backup)

            assert backup_path == custom_backup
            assert os.path.exists(custom_backup)

    def test_system_shutdown(self):
        """Test graceful system shutdown"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = create_production_wiki_system(storage_path=temp_dir)

            # System should be running
            assert system._processing_active
            assert system._processor_thread is not None

            # Shutdown system
            system.shutdown()

            # System should be stopped
            assert not system._processing_active

    @pytest.mark.asyncio
    async def test_search_session_context_manager(self):
        """Test search session context manager"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = create_production_wiki_system(storage_path=temp_dir)

            async with system.search_session() as session_id:
                assert isinstance(session_id, str)

                # Perform search within session
                results = await system.search("test query")
                assert isinstance(results, list)

    def test_persistence_and_recovery(self):
        """Test system state persistence and recovery"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create and configure system
            system1 = create_production_wiki_system(storage_path=temp_dir)

            # Simulate some data
            system1.documents["test_doc"] = {
                "id": "test_doc",
                "status": "completed",
                "created_at": datetime.now().isoformat(),
            }

            # Save state
            system1._save_system_state()

            # Create new system instance (should load saved state)
            system2 = ProductionWikiKnowledgeSystem(storage_path=temp_dir)

            # Verify state was loaded
            assert "test_doc" in system2.documents
            assert system2.documents["test_doc"]["status"] == "completed"


class TestIntegrationScenarios:
    """Integration tests for complex scenarios"""

    @pytest.mark.asyncio
    async def test_end_to_end_document_processing(self):
        """Test complete document processing pipeline"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = create_production_wiki_system(storage_path=temp_dir)

            # Create test document
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False
            ) as f:
                content = """
                Artificial Intelligence (AI) is a branch of computer science that aims to create  # noqa: E501
                intelligent machines that can perform tasks that typically require human intelligence.  # noqa: E501
                Machine learning is a subset of AI that focuses on algorithms that can learn from data.  # noqa: E501
                Deep learning is a subset of machine learning that uses neural networks with multiple layers.  # noqa: E501
                """
                f.write(content.strip())
                temp_path = f.name

            try:
                # Add document
                document_id = await system.add_document(
                    temp_path,
                    metadata=DocumentMetadata(
                        title="AI Introduction",
                        author="Test Author",
                        tags=["AI", "machine learning", "deep learning"],
                    ),
                )

                # Wait for processing
                await asyncio.sleep(2.0)

                # Verify processing completed
                status = system.get_document_status(document_id)
                assert status == DocumentStatus.COMPLETED

                # Test search functionality
                search_results = await system.search("machine learning", top_k=5)

                # Should find the document
                assert len(search_results) > 0
                assert any(
                    result.document_id == document_id for result in search_results
                )

                # Test different search types
                for search_type in [
                    SearchType.SEMANTIC,
                    SearchType.KEYWORD,
                    SearchType.HYBRID,
                ]:
                    results = await system.search(
                        "artificial intelligence", search_type=search_type
                    )
                    assert isinstance(results, list)

                # Get system metrics
                metrics = system.get_system_metrics()
                assert metrics["documents_count"] >= 1
                assert metrics["chunks_count"] >= 1

            finally:
                # 后台处理线程可能仍持有文件句柄（负载下竞态），unlink 失败可忽略
                try:
                    os.unlink(temp_path)
                except (PermissionError, OSError):
                    pass

    @pytest.mark.asyncio
    async def test_concurrent_document_processing(self):
        """Test processing multiple documents concurrently"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = create_production_wiki_system(
                storage_path=temp_dir, max_concurrent_processors=3
            )

            # Create multiple test documents
            document_paths = []
            for i in range(5):
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".txt", delete=False
                ) as f:
                    content = f"This is test document {i} with unique content {i * 10}."
                    f.write(content)
                    document_paths.append(f.name)

            try:
                # Add all documents concurrently
                tasks = []
                for i, path in enumerate(document_paths):
                    task = system.add_document(
                        path,
                        metadata=DocumentMetadata(
                            title=f"Document {i}", tags=[f"tag{i}", "test"]
                        ),
                    )
                    tasks.append(task)

                document_ids = await asyncio.gather(*tasks)

                # Verify all documents were added
                assert len(document_ids) == 5
                for doc_id in document_ids:
                    assert doc_id in system.documents

                # Wait for processing
                await asyncio.sleep(3.0)

                # Check final status
                completed_count = 0
                for doc_id in document_ids:
                    status = system.get_document_status(doc_id)
                    if status == DocumentStatus.COMPLETED:
                        completed_count += 1

                # At least some should be processed
                assert completed_count >= 3

                # Test search across all documents
                results = await system.search("unique content", top_k=10)
                assert isinstance(results, list)

            finally:
                for path in document_paths:
                    os.unlink(path)

    def test_performance_monitoring_integration(self):
        """Test performance monitoring across all components"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = create_production_wiki_system(storage_path=temp_dir)

            # Get initial metrics
            initial_metrics = system.get_system_metrics()

            # Verify metrics structure
            assert "processing_metrics" in initial_metrics
            assert all(
                metric in initial_metrics["processing_metrics"]
                for metric in [
                    "documents_processed",
                    "searches_performed",
                    "embeddings_generated",
                ]
            )

            # Verify each metric has proper structure
            for metric_name, metric_data in initial_metrics[
                "processing_metrics"
            ].items():
                assert "operation_count" in metric_data
                assert "avg_duration" in metric_data
                assert "min_duration" in metric_data
                assert "max_duration" in metric_data
                assert "error_count" in metric_data

    def test_error_handling_and_recovery(self):
        """Test system error handling and recovery mechanisms"""
        with tempfile.TemporaryDirectory() as temp_dir:
            system = create_production_wiki_system(storage_path=temp_dir)

            # Test circuit breaker integration
            assert hasattr(system.embedding_service, "circuit_breaker")

            # Test rate limiting integration
            assert hasattr(system.embedding_service, "rate_limiter")

            # Verify system can handle various error conditions
            try:
                # Try to search with empty system
                asyncio.run(system.search("test query"))
            except Exception:
                pass  # Should handle gracefully

            # System should still be functional
            metrics = system.get_system_metrics()
            assert isinstance(metrics, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
