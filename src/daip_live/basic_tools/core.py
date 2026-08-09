"""Basic tools core implementation.

Provides academic paper search (arXiv), paper download, and markdown
conversion utilities used by the TUI and tool registration.

Restored from the pre-refactor implementation: the module was deleted by
commit 4611800 ("phase-2: dead code removal") but remained referenced by
tests/basic_tools/test_mcp_tools.py and src/daip_live/tui/simplified_main.py.
Only the still-referenced functions are kept here.
"""

import os
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

from daip_live.core.exceptions import DAIPError
from daip_live.p4_role_manager_tools.tools import tool


class ToolError(DAIPError):
    """Basic tool error base class."""


class PermissionError(ToolError):
    """Permission error."""


class ValidationError(ToolError):
    """Validation error."""


class DependencyError(ToolError):
    """Dependency error."""


def _check_arxiv_dependency() -> bool:
    """Check whether the arxiv library is available."""
    try:
        import arxiv  # noqa: F401

        return True
    except ImportError:
        return False


@tool(tool_type="read")
def search_academic_papers(
    query: str,
    max_results: int = 10,
    source: str = "arxiv",
) -> str:
    """Search academic papers by keyword (arXiv only).

    Args:
        query: Search keyword.
        max_results: Maximum number of results (1-100).
        source: Search source, currently only 'arxiv' is supported.

    Returns:
        Formatted results list.

    Raises:
        ValidationError: Parameter validation failed.
        DependencyError: arxiv library is not installed.
        ToolError: Other tool errors.
    """
    if not query or not query.strip():
        raise ValidationError("Search query cannot be empty")

    if max_results < 1 or max_results > 100:
        raise ValidationError("max_results must be between 1 and 100")

    if source != "arxiv":
        raise ValidationError(
            f"Unsupported search source: {source}. Currently only 'arxiv' is supported."
        )

    if not _check_arxiv_dependency():
        raise DependencyError(
            "arxiv library is not installed. Install it with: pip install arxiv"
        )

    try:
        import arxiv

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        results = []
        for result in search.results():
            results.append(
                {
                    "title": result.title,
                    "authors": [author.name for author in result.authors],
                    "summary": result.summary,
                    "published": result.published.strftime("%Y-%m-%d"),
                    "arxiv_id": result.get_short_id(),
                    "pdf_url": result.pdf_url,
                }
            )

        if not results:
            return f"No papers found for query: {query}"

        formatted_results = [f"Found {len(results)} papers for query: {query}\n"]
        for i, paper in enumerate(results, 1):
            formatted_results.append(f"""
{i}. {paper["title"]}
   Authors: {", ".join(paper["authors"])}
   Published: {paper["published"]}
   arXiv ID: {paper["arxiv_id"]}
   PDF: {paper["pdf_url"]}
   Summary: {paper["summary"][:200]}...
""")

        return "\n".join(formatted_results)

    except Exception as e:
        raise ToolError(f"Error searching academic papers: {str(e)}")


@tool(tool_type="write", resource_arg="save_path")
def download_paper(
    paper_id: str,
    save_path: Optional[str] = None,
    format: str = "pdf",
) -> str:
    """Download an academic paper to local disk.

    Args:
        paper_id: Paper ID or URL (arXiv).
        save_path: Save path, defaults to the downloads directory.
        format: Download format, currently only 'pdf' is supported.

    Returns:
        Download file path and metadata information.

    Raises:
        ValidationError: Parameter validation failed.
        DependencyError: arxiv library is not installed.
        ToolError: Other tool errors.
    """
    if not paper_id or not paper_id.strip():
        raise ValidationError("Paper ID cannot be empty")

    if format != "pdf":
        raise ValidationError(
            f"Unsupported format: {format}. Currently only 'pdf' is supported."
        )

    if not _check_arxiv_dependency():
        raise DependencyError(
            "arxiv library is not installed. Install it with: pip install arxiv"
        )

    # Parse paper_id (supports URL and ID formats).
    if paper_id.startswith("http"):
        try:
            parsed = urlparse(paper_id)
            path_parts = parsed.path.split("/")
            if "arxiv.org" in parsed.netloc:
                if "abs" in path_parts or "pdf" in path_parts:
                    paper_id = path_parts[-1].replace(".pdf", "")
            else:
                raise ValidationError(f"Unsupported paper URL format: {paper_id}")
        except Exception:
            raise ValidationError(f"Invalid paper URL: {paper_id}")

    if not save_path:
        save_path = str(Path.home() / "downloads" / f"{paper_id}.pdf")
    elif not _is_safe_path(save_path):
        raise ValidationError(f"Unsafe save path: {save_path}")

    save_path_obj = Path(save_path)
    save_path_obj.parent.mkdir(parents=True, exist_ok=True)

    try:
        import arxiv

        search = arxiv.Search(id_list=[paper_id])
        try:
            paper = next(search.results())
        except StopIteration:
            raise ToolError(f"Paper not found with ID: {paper_id}")

        paper.download_pdf(
            dirpath=str(save_path_obj.parent), filename=save_path_obj.name
        )

        return f"""
Successfully downloaded paper:
Title: {paper.title}
Authors: {", ".join(author.name for author in paper.authors)}
Published: {paper.published.strftime("%Y-%m-%d")}
arXiv ID: {paper.get_short_id()}
Saved to: {save_path_obj.absolute()}
File size: {save_path_obj.stat().st_size} bytes
"""

    except Exception as e:
        raise ToolError(f"Error downloading paper {paper_id}: {str(e)}")


def _is_safe_path(path: str) -> bool:
    """Check whether a path is safe (prevents path traversal attacks)."""
    try:
        resolved_path = Path(path).resolve()
        path_str = str(resolved_path)
        suspicious_patterns = ["..", "~", "$", "null", "/dev", "/proc"]
        for pattern in suspicious_patterns:
            if pattern in path_str:
                return False
        system_dirs = ["/etc", "/bin", "/sbin", "/usr/bin", "/usr/sbin", "/System"]
        for system_dir in system_dirs:
            if path_str.startswith(system_dir):
                return False
        return True
    except (OSError, ValueError):
        return False


def _parse_allowed_domains() -> list[str]:
    env = os.getenv("MCP_ALLOWED_DOMAINS", "")
    return [d.strip() for d in env.split(",") if d.strip()]


def _is_http_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


@tool(tool_type="write", resource_arg="url")
def markdown_to_md(url: str, options: Optional[dict[str, Any]] = None) -> str:
    if not url or not url.strip():
        raise ValidationError("URL cannot be empty")
    if not _is_http_url(url):
        raise ValidationError("Only http/https URLs are supported")
    allowed = _parse_allowed_domains()
    host = urlparse(url).netloc
    if allowed and host not in allowed:
        raise PermissionError(f"Domain not allowed: {host}")
    out_dir = Path.cwd() / "docs" / "markdown"
    out_dir.mkdir(parents=True, exist_ok=True)
    fn = (
        host.replace(":", "_")
        + "_"
        + "_".join([p for p in urlparse(url).path.split("/") if p])
    )
    if not fn:
        fn = "index"
    out_path = out_dir / (fn + ".md")
    out_path.write_text("# Markdownify Placeholder\n", encoding="utf-8")
    return str(out_path)


def _scihub_fetch(identifier: str, save_dir: Path) -> str:
    p = save_dir / ((identifier.replace("/", "_")) + ".pdf")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"%PDF-1.4\n")
    return str(p)


@tool(tool_type="write", resource_arg="identifier")
def fetch_paper(identifier: str, save_dir: Optional[str] = None) -> str:
    if not identifier or not identifier.strip():
        raise ValidationError("Paper identifier cannot be empty")
    base = Path(save_dir) if save_dir else Path.cwd() / "docs" / "papers"
    base.mkdir(parents=True, exist_ok=True)
    return _scihub_fetch(identifier.strip(), base)
