"""Defines the core interface contracts (Abstract Base Classes) for services."""

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any, Dict, List


class IModelProvider(ABC):
    """Interface for a service that provides LLM generation and embeddings."""

    @abstractmethod
    async def generate(self, prompt: str, params: Dict) -> AsyncGenerator[str, None]:
        """Generates a response from a language model."""
        # This is an async generator, so it must be implemented with `async def`
        # and use `yield` to stream tokens.
        yield ""
        # The yield is necessary to make this an async generator function.
        # The actual implementation will not have it.

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Creates an embedding vector for a given text asynchronously."""
        pass


class IKnowledgeManager(ABC):
    """Interface for a service that manages the knowledge base."""

    @abstractmethod
    def search(self, query_text: str, top_k: int) -> List[Dict]:
        """Searches the knowledge base for relevant documents."""
        pass

    @abstractmethod
    def sync_knowledge_base(self) -> Dict:
        """Synchronizes the knowledge base with the source documents."""
        pass


class ITool(ABC):
    """Interface for a tool that can be executed by the agent."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The unique name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A description of what the tool does."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Executes the tool with the given arguments."""
        pass
