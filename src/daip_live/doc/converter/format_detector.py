"""
Format detection for document conversion tools.
"""

import mimetypes
from pathlib import Path
from typing import Optional


class FormatDetector:
    """Utility class to detect document formats."""

    def __init__(self):
        self._format_map: dict[str, str] = {
            ".md": "markdown",
            ".txt": "text",
            ".pdf": "pdf",
            ".doc": "word",
            ".docx": "word",
            ".ppt": "powerpoint",
            ".pptx": "powerpoint",
            ".xls": "excel",
            ".xlsx": "excel",
            ".html": "html",
            ".htm": "html",
            ".json": "json",
            ".xml": "xml",
            ".csv": "csv",
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".rb": "ruby",
            ".go": "go",
            ".rs": "rust",
            ".yaml": "yaml",
            ".yml": "yaml",
        }

    def detect_format(self, file_path: Path) -> tuple[str, str]:
        """Detect format and MIME type for a file."""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type is None:
            mime_type = "application/octet-stream"

        # Get format from extension
        ext = file_path.suffix.lower()
        format_type = self._format_map.get(ext, "unknown")

        return format_type, mime_type

    def is_supported_format(self, file_path: Path) -> bool:
        """Check if the file format is supported."""
        ext = file_path.suffix.lower()
        return ext in self._format_map

    def get_supported_extensions(self) -> list:
        """Get all supported file extensions."""
        return list(self._format_map.keys())

    def get_format_from_content(
        self, content: str, max_bytes: int = 1024
    ) -> Optional[str]:
        """Detect format from file content."""
        content_sample = content[:max_bytes].lower()

        # Simple heuristics for content-based detection
        if content_sample.startswith("<"):
            if any(
                tag in content_sample
                for tag in ["<html>", "<head>", "<body>", "<!doctype", "<!DOCTYPE"]
            ):
                return "html"
            elif "<?xml" in content_sample or any(
                "<" + tag in content_sample for tag in ["xml", "document", "note"]
            ):
                return "xml"
        elif content_sample.startswith(("{", "[")):
            return "json"
        elif any(
            marker in content_sample
            for marker in ["# ", "## ", "### ", "- ", "* ", "> "]
        ):
            return "markdown"
        elif any(marker in content_sample for marker in ["[", "]"]) and any(
            "title:" in content_sample or "author:" in content_sample
        ):
            # Could be ini, toml, or similar config file with title/author metadata
            return "yaml"
        elif any(
            marker in content_sample
            for marker in ["import ", "def ", "class ", "from ", "async def"]
        ):
            return "python"
        else:
            return "text"  # Default fallback
