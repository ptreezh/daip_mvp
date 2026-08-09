"""
Search Engine for Wiki Knowledge Base

Handles semantic search, text search, and hybrid search capabilities.
"""

import logging
import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional

from .document import Document
from .vector_store import SearchResult, VectorStore

logger = logging.getLogger(__name__)


class SearchEngine:
    """Advanced search engine for knowledge base"""

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_model: Optional[str] = None,
        enable_text_search: bool = True,
        enable_semantic_search: bool = True,
    ):
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.enable_text_search = enable_text_search
        self.enable_semantic_search = enable_semantic_search
        self.search_history: list[dict[str, Any]] = []
        self.max_history = 1000
        logger.info("Initialized search engine")

    def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[dict[str, Any]] = None,
        include_chunks: bool = False,
        threshold: float = 0.0,
    ) -> list[SearchResult]:
        """Perform semantic search on query"""
        if not self.enable_semantic_search:
            return []

        try:
            # Generate query embedding
            query_vector = self._generate_embedding(query)
            if not query_vector:
                logger.error("Failed to generate query embedding")
                return []

            # Perform vector search
            results = self.vector_store.search(
                query_vector=query_vector,
                top_k=top_k * 2,  # Get more results for filtering
                threshold=threshold,
                include_chunks=include_chunks,
            )

            # Apply filters
            if filters:
                results = self._apply_filters(results, filters)

            # Record search
            self._record_search(query, len(results), filters)

            return results[:top_k]

        except Exception as e:
            logger.error(f"Error during semantic search: {e}")
            return []

    def semantic_search(
        self,
        query_vector: list[float],
        top_k: int = 10,
        filters: Optional[dict[str, Any]] = None,
        include_chunks: bool = False,
        threshold: float = 0.0,
    ) -> list[SearchResult]:
        """Perform semantic search with pre-generated vector"""
        if not self.enable_semantic_search:
            return []

        try:
            results = self.vector_store.search(
                query_vector=query_vector,
                top_k=top_k * 2,
                threshold=threshold,
                include_chunks=include_chunks,
            )

            # Apply filters
            if filters:
                results = self._apply_filters(results, filters)

            # Record search
            self._record_search("vector_query", len(results), filters)

            return results[:top_k]

        except Exception as e:
            logger.error(f"Error during semantic search: {e}")
            return []

    def text_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[dict[str, Any]] = None,
        case_sensitive: bool = False,
        whole_word: bool = False,
    ) -> list[SearchResult]:
        """Perform text-based search"""
        if not self.enable_text_search:
            return []

        try:
            # Get all documents
            all_documents = self.vector_store.get_all_documents()

            # Apply initial filters
            if filters:
                all_documents = self._filter_documents(all_documents, filters)

            # Search for matches
            results = []
            query_pattern = self._build_search_pattern(
                query, case_sensitive, whole_word
            )

            for document in all_documents:
                score = self._calculate_text_score(document, query_pattern, query)
                if score > 0:
                    result = SearchResult(document=document, score=score)
                    results.append(result)

            # Sort by score and return top results
            results.sort(key=lambda x: x.score, reverse=True)

            # Record search
            self._record_search(query, len(results), filters, search_type="text")

            return results[:top_k]

        except Exception as e:
            logger.error(f"Error during text search: {e}")
            return []

    def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[dict[str, Any]] = None,
        text_weight: float = 0.5,
        semantic_weight: float = 0.5,
        include_chunks: bool = False,
    ) -> list[SearchResult]:
        """Perform hybrid search combining text and semantic search"""
        if not (self.enable_text_search and self.enable_semantic_search):
            # Fallback to available search method
            if self.enable_semantic_search:
                return self.search(query, top_k, filters, include_chunks)
            elif self.enable_text_search:
                return self.text_search(query, top_k, filters)
            else:
                return []

        try:
            # Perform both searches
            text_results = self.text_search(query, top_k * 2, filters)
            semantic_results = self.search(query, top_k * 2, filters, include_chunks)

            # Combine results
            combined_results = self._combine_search_results(
                text_results, semantic_results, text_weight, semantic_weight
            )

            # Sort by combined score
            combined_results.sort(key=lambda x: x.score, reverse=True)

            # Record search
            self._record_search(
                query, len(combined_results), filters, search_type="hybrid"
            )

            return combined_results[:top_k]

        except Exception as e:
            logger.error(f"Error during hybrid search: {e}")
            return []

    def get_suggestions(
        self,
        partial_query: str,
        max_suggestions: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[str]:
        """Get search suggestions based on partial query"""
        try:
            # Get all documents
            all_documents = self.vector_store.get_all_documents()

            # Apply filters
            if filters:
                all_documents = self._filter_documents(all_documents, filters)

            # Extract keywords and phrases from documents
            suggestions = set()

            for document in all_documents:
                # Add words from title
                title_words = self._extract_words(document.title)
                suggestions.update(title_words)

                # Add words from content (limited)
                content_preview = document.get_content_preview(500)
                content_words = self._extract_words(content_preview)
                suggestions.update(content_words)

                # Add tags
                suggestions.update(document.tags)

                # Add metadata keywords
                for key, value in document.metadata.items():
                    if isinstance(value, str):
                        suggestions.update(self._extract_words(value))

            # Filter suggestions based on partial query
            partial_query_lower = partial_query.lower()
            filtered_suggestions = [
                suggestion
                for suggestion in suggestions
                if partial_query_lower in suggestion.lower()
            ]

            # Sort by relevance (exact matches first, then alphabetical)
            filtered_suggestions.sort(
                key=lambda x: (
                    0 if x.lower() == partial_query_lower else 1,
                    0 if x.lower().startswith(partial_query_lower) else 1,
                    x.lower(),
                )
            )

            return filtered_suggestions[:max_suggestions]

        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []

    def search_by_category(
        self, category: str, top_k: int = 10, query: Optional[str] = None
    ) -> list[SearchResult]:
        """Search within a specific category"""
        filters = {"category": category}

        if query:
            return self.search(query, top_k, filters)
        else:
            # Return all documents in category
            all_documents = self.vector_store.get_all_documents()
            category_docs = self._filter_documents(all_documents, filters)

            results = [
                SearchResult(document=doc, score=1.0) for doc in category_docs[:top_k]
            ]

            return results

    def get_similar_documents(
        self, document_id: str, top_k: int = 5, include_chunks: bool = False
    ) -> list[SearchResult]:
        """Find documents similar to a given document"""
        try:
            document = self.vector_store.get_document(document_id)
            if not document or not document.embedding:
                logger.warning(f"Document {document_id} not found or has no embedding")
                return []

            # Use document embedding as query
            return self.semantic_search(
                query_vector=document.embedding,
                top_k=top_k,
                include_chunks=include_chunks,
            )

        except Exception as e:
            logger.error(f"Error finding similar documents: {e}")
            return []

    def _generate_embedding(self, text: str) -> Optional[list[float]]:
        """Generate embedding for text"""
        try:
            # This would use an actual embedding model in production
            # For now, use the same mock embedding as DocumentIngestor
            import hashlib

            text_hash = hashlib.md5(text.encode()).hexdigest()
            embedding = []

            for i in range(0, min(len(text_hash), 128), 2):
                hex_pair = text_hash[i : i + 2]
                val = int(hex_pair, 16) / 255.0
                for _ in range(6):
                    embedding.append(val)

            embedding = embedding[:768]
            if len(embedding) < 768:
                embedding.extend([0.0] * (768 - len(embedding)))

            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def _apply_filters(
        self, results: list[SearchResult], filters: dict[str, Any]
    ) -> list[SearchResult]:
        """Apply filters to search results"""
        filtered_results = []

        for result in results:
            document = result.document
            if self._document_matches_filters(document, filters):
                filtered_results.append(result)

        return filtered_results

    def _filter_documents(
        self, documents: list[Document], filters: dict[str, Any]
    ) -> list[Document]:
        """Filter documents based on criteria"""
        return [
            doc for doc in documents if self._document_matches_filters(doc, filters)
        ]

    def _document_matches_filters(
        self, document: Document, filters: dict[str, Any]
    ) -> bool:
        """Check if document matches filters"""
        for key, value in filters.items():
            if key == "document_type":
                if document.document_type != value:
                    return False
            elif key == "author":
                if document.author != value:
                    return False
            elif key == "tags":
                if not any(tag in document.tags for tag in value):
                    return False
            elif key == "category":
                if document.metadata.get("category") != value:
                    return False
            elif key in document.metadata:
                if document.metadata[key] != value:
                    return False
            else:
                # Unknown filter key, skip
                continue

        return True

    def _build_search_pattern(
        self, query: str, case_sensitive: bool, whole_word: bool
    ) -> re.Pattern:
        """Build regex pattern for text search"""
        # Escape special regex characters in query
        escaped_query = re.escape(query)

        if whole_word:
            pattern = r"\b" + escaped_query + r"\b"
        else:
            pattern = escaped_query

        flags = 0 if case_sensitive else re.IGNORECASE
        return re.compile(pattern, flags)

    def _calculate_text_score(
        self, document: Document, pattern: re.Pattern, original_query: str
    ) -> float:
        """Calculate text search score"""
        score = 0.0

        # Title matches (higher weight)
        title_matches = len(pattern.findall(document.title))
        score += title_matches * 10.0

        # Content matches
        content_matches = len(pattern.findall(document.content))
        score += content_matches * 1.0

        # Tag matches
        tag_matches = sum(1 for tag in document.tags if pattern.search(tag))
        score += tag_matches * 5.0

        # Exact phrase bonus
        if original_query.lower() == document.title.lower():
            score += 20.0

        # Normalize score
        max_possible_score = 50.0  # Arbitrary max for normalization
        return min(score / max_possible_score, 1.0)

    def _combine_search_results(
        self,
        text_results: list[SearchResult],
        semantic_results: list[SearchResult],
        text_weight: float,
        semantic_weight: float,
    ) -> list[SearchResult]:
        """Combine text and semantic search results"""
        combined_scores = defaultdict(float)
        combined_results = {}

        # Add text results
        for result in text_results:
            doc_id = result.document.id
            combined_scores[doc_id] += result.score * text_weight
            combined_results[doc_id] = result

        # Add semantic results
        for result in semantic_results:
            doc_id = result.document.id
            combined_scores[doc_id] += result.score * semantic_weight
            combined_results[doc_id] = result

        # Create combined results
        final_results = []
        for doc_id, combined_score in combined_scores.items():
            result = combined_results[doc_id]
            result.score = combined_score  # Update with combined score
            final_results.append(result)

        return final_results

    def _extract_words(self, text: str) -> list[str]:
        """Extract meaningful words from text"""
        # Remove special characters and split into words
        words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9]*\b", text.lower())

        # Filter out very short words and common stop words
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
        }

        meaningful_words = [
            word for word in words if len(word) >= 3 and word not in stop_words
        ]

        return meaningful_words

    def _record_search(
        self,
        query: str,
        result_count: int,
        filters: Optional[dict[str, Any]],
        search_type: str = "semantic",
    ) -> None:
        """Record search query for analytics"""
        search_record = {
            "query": query,
            "result_count": result_count,
            "filters": filters or {},
            "search_type": search_type,
            "timestamp": datetime.now().isoformat(),
        }

        self.search_history.append(search_record)

        # Limit history size
        if len(self.search_history) > self.max_history:
            self.search_history = self.search_history[-self.max_history :]

    def get_search_analytics(self) -> dict[str, Any]:
        """Get search analytics"""
        if not self.search_history:
            return {"total_searches": 0}

        total_searches = len(self.search_history)
        search_types = defaultdict(int)
        avg_results = 0

        for record in self.search_history:
            search_types[record["search_type"]] += 1
            avg_results += record["result_count"]

        avg_results /= total_searches

        return {
            "total_searches": total_searches,
            "search_types": dict(search_types),
            "average_results": avg_results,
            "most_recent_search": self.search_history[-1]
            if self.search_history
            else None,
        }

    def clear_search_history(self) -> None:
        """Clear search history"""
        self.search_history.clear()
        logger.info("Cleared search history")
