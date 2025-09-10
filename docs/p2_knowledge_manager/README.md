---
id: P2
title: Knowledge Management Service
status: Finalized
architecture_drivers: [SOLID, KISS, YAGNI, KDD]
---

# P2: Knowledge Management Service

## 1. Overview

This work package (`P2`) is responsible for the "Retrieval" part of the Retrieval-Augmented Generation (RAG) pipeline. Its **sole responsibility** is to process local documents, build an embedded vector index, and provide a simple API for semantic search. Any functionality beyond this (e.g., managing consensus results) is explicitly out of scope for this package.

## 2. `KnowledgeManager` API Specification

The public API is the `KnowledgeManager` class, which implements the `IKnowledgeManager` interface from `P0`. The API is asynchronous to prevent blocking the main application thread during I/O-heavy operations.

```python
# Models are imported from P0
from P0_Core_Interfaces_Types import SearchResultChunk
from P1_Services_DataPersistence import DatabaseManager
from P3_Services_ModelProvider import IModelProvider

class KnowledgeManager(IKnowledgeManager):
    def __init__(self, db_manager: DatabaseManager, model_provider: IModelProvider, config: Dict):
        """Initializes the knowledge manager with dependencies and configuration."""
        pass

    async def sync_knowledge_base(self) -> Dict[str, int]:
        """Scans the knowledge directory, processes changes, and updates the index.

        Returns:
            A dictionary summarizing the sync results, e.g.,
            {'added': 5, 'updated': 2, 'removed': 1, 'unchanged': 100}
        """
        pass

    async def search(self, query_text: str, top_k: int = 5) -> List[SearchResultChunk]:
        """Searches the index and returns the most relevant document chunks."""
        pass
```

## 3. Core Workflow: `sync_knowledge_base`

This is the heart of the package. The process is as follows:

1.  **Scan Files**: Recursively scan the user-defined `knowledge/` directory.
2.  **Detect Changes**: For each file, compare its current hash against the hash stored in the `knowledge_sources` table (via `P1.DatabaseManager`).
3.  **Process Deltas**:
    -   **New/Modified Files**: Use the `unstructured` library to parse the file content. Split the content into chunks. Call `P3.IModelProvider.embed()` for each chunk. `Upsert` the new vectors into the FAISS index.
    -   **Deleted Files**: Remove the corresponding vectors from the FAISS index and delete the metadata record from the database.

## 4. Implementation Policies & Requirements

-   **Vector Store**: The implementation **must** use **`faiss-cpu`** as the vector store. The FAISS index file must be saved to and loaded from a designated `data/vector_store` directory.
-   **Document Parsing**: The implementation **must** use the **`unstructured`** library to handle parsing of different file formats (`.md`, `.txt`, `.pdf`, etc.). This provides robust, out-of-the-box support.
-   **Concurrency Control**: The `sync_knowledge_base` method **must** be atomic. It must acquire a file-based lock (e.g., using the `fasteners` library) upon entry and release it upon exit. This prevents race conditions from multiple sync processes corrupting the index.
-   **Configuration**: Key parameters such as `chunk_size`, `chunk_overlap`, and the `embedding_model_name` **must** be loaded from a central configuration object passed during initialization.
-   **Asynchronous Execution**: I/O-bound (file reading) and CPU-bound (chunking, FAISS operations) tasks within the `async` methods should be run in a separate thread using `asyncio.to_thread` to avoid blocking the event loop.

## 5. Test Plan Summary

-   **TDD Approach**: All methods must be developed via TDD.
-   **Dependency Mocking**: All external dependencies (`P1.DatabaseManager`, `P3.IModelProvider`) **must** be mocked during testing.
-   **File System**: All tests involving file operations **must** use a temporary directory fixture (e.g., `pytest.tmp_path`).
-   **Key Test Cases**:
    -   Verify the sync logic for new, modified, deleted, and unchanged files.
    -   Verify that the `search` method returns correctly structured `SearchResultChunk` objects.
    -   Verify that attempting to run two `sync_knowledge_base` operations concurrently results in the second one being blocked or raising an exception, due to the file lock.
-   **Acceptance**: Test coverage >= 90%; passes `ruff` and `mypy --strict`.

## 6. Implementation Status

-   **`KnowledgeManager` Class**: The class structure is defined, and the constructor is implemented. It is integrated into the `cli.py` for application startup.
-   **`sync_knowledge_base` Method**: The core logic for scanning, detecting changes, and processing new/modified/deleted files is implemented. It uses `IKnowledgeManager` and `IModelProvider`.
-   **`search` Method**: Currently a placeholder. The actual implementation for vector search and retrieval is pending.
-   **Dependencies**: Integration with `faiss-cpu` and `unstructured` is pending full implementation of the `search` method and robust file processing.
