"""
Base conversion interface for document tools.
"""
from abc import ABC, abstractmethod
from typing import Protocol, Optional
from pathlib import Path

from daip_live.doc.models.document_models import DocumentConversionResult


class ConverterProtocol(Protocol):
    """Protocol for document converters."""
    
    async def convert(self, source_path: Path, target_path: Path) -> DocumentConversionResult:
        """Convert document from source to target format."""
        ...


class BaseConverter(ABC):
    """Abstract base class for document converters."""
    
    def __init__(self):
        self.supported_formats = set()
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def convert(self, source_path: Path, target_path: Path) -> DocumentConversionResult:
        """Convert document from source to target format."""
        pass
    
    def supports_format(self, format_ext: str) -> bool:
        """Check if converter supports the given format."""
        return format_ext.lower() in self.supported_formats
    
    async def validate_input(self, source_path: Path) -> bool:
        """Validate input file before conversion."""
        return source_path.exists() and source_path.is_file()
    
    async def validate_output(self, target_path: Path) -> bool:
        """Validate output file after conversion."""
        return target_path.exists() and target_path.is_file()