import logging
import re
from pathlib import Path
from typing import Optional

from src.kernel.vector_store import VectorStore

# Define a path for the Wiki data files
WIKI_DIR = Path("data/wiki")

# Module-level cache for the VectorStore instance to avoid re-initialization
_vector_store_instance: Optional[VectorStore] = None


def _get_vector_store() -> VectorStore:
    """Initializes and returns a shared VectorStore instance."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance


def _sanitize_filename(title: str) -> str:
    """Converts a wiki entry title into a safe, valid filename.
    Example: "What is AI?" -> "what_is_ai.md"
    """
    # Step 1: Strip leading/trailing whitespace and convert to lowercase.
    s = title.strip().lower()
    # Step 2: Replace any character that is not a letter, number, or underscore with a space.
    s = re.sub(r"[^a-z0-9_]+", " ", s)
    # Step 3: Replace one or more whitespace characters with a single underscore.
    s = re.sub(r"\s+", "_", s)
    # Step 4: Remove leading/trailing underscores that might have been created.
    s = s.strip("_")
    # Ensure it's not empty and add the .md extension
    return f"{s or 'untitled'}.md"


def write_wiki_entry(title: str, content: str) -> str:
    """Creates or overwrites an entry in the Wiki/Memory Bank.

    Args:
        title: The title of the knowledge entry.
        content: The content of the knowledge entry.

    Returns:
        A confirmation message.

    """
    try:
        WIKI_DIR.mkdir(exist_ok=True)
        file_path = WIKI_DIR / _sanitize_filename(title)
        file_path.write_text(content, encoding="utf-8")

        # Also add/update the entry in the vector store for semantic search
        vector_store = _get_vector_store()
        vector_store.add_entry(
            doc_id=file_path.name, content=content, metadata={"title": title}
        )
        logging.info(f"Wrote to wiki entry: '{title}'")
        return f"Successfully saved the wiki entry titled '{title}'."
    except Exception as e:
        logging.exception(f"Failed to write wiki entry '{title}'")
        return f"An error occurred while saving the wiki entry: {e}"


def read_wiki_entry(title: str) -> str:
    """Reads an entry from the Wiki/Memory Bank.

    Args:
        title: The title of the knowledge entry to read.

    Returns:
        The content of the entry or an error message.

    """
    try:
        file_path = WIKI_DIR / _sanitize_filename(title)
        if not file_path.is_file():
            return f"Error: Wiki entry with title '{title}' not found."
        return file_path.read_text(encoding="utf-8")
    except Exception as e:
        logging.exception(f"Failed to read wiki entry '{title}'")
        return f"An error occurred while reading the wiki entry: {e}"


def list_wiki_entries() -> str:
    """Lists all available entries in the Wiki/Memory Bank.

    Returns:
        A formatted string of all entry titles.

    """
    if not WIKI_DIR.is_dir():
        return "The Wiki is empty. No entries found."

    entries = [p.stem.replace("_", " ") for p in WIKI_DIR.glob("*.md")]
    if not entries:
        return "The Wiki is empty. No entries found."

    return "Available Wiki entries:\n- " + "\n- ".join(sorted(entries))


def search_wiki(query: str) -> str:
    """Performs a semantic search across all entries in the Wiki/Memory Bank.

    Args:
        query: The natural language query or concept to search for.

    Returns:
        A formatted string of the most relevant entries found.

    """
    try:
        vector_store = _get_vector_store()
        results = vector_store.search(query, n_results=3)

        if not results or not results.get("documents"):
            return f"No relevant wiki entries found for the query: '{query}'"

        output_parts = [f"Found {len(results['documents'][0])} relevant results for '{query}':\n"]
        for i, doc in enumerate(results["documents"][0]):
            title = results["metadatas"][0][i].get("title", "Unknown Title")
            # Provide a snippet of the content
            snippet = (doc[:200] + "...") if len(doc) > 200 else doc
            output_parts.append(f"Result {i+1}:")
            output_parts.append(f"  Title: {title}")
            output_parts.append(f"  Content Snippet: {snippet}\n")

        return "\n".join(output_parts)
    except Exception as e:
        logging.exception(f"An error occurred during wiki search for query: {query}")
        return f"An error occurred during the search: {e}"
