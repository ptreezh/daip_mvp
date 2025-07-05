"""DAIP Insight Engine - 文档摄入与分块策略验证模块

本模块支持多种文档格式（PDF、DOCX、TXT、MD）解析和可配置的分块策略，适用于知识库、RAG等场景。
所有数据结构、主类、方法均具备类型注解和详细文档，支持自动化API文档工具提取。
"""

import logging
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

# 文档解析库依赖检测
try:
    import PyPDF2

    PDF2_AVAILABLE = True
except ImportError:
    PDF2_AVAILABLE = False
try:
    import pdfplumber

    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
try:
    import fitz  # PyMuPDF

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
try:
    import docx

    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
try:
    from langchain.text_splitter import (
        CharacterTextSplitter,
        RecursiveCharacterTextSplitter,
    )

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """文本块数据结构。
    Attributes:
        chunk_id (str): 块唯一ID。
        content (str): 文本内容。
        source_file (str): 来源文件名。
        page_number (Optional[int]): 页码。
        chunk_index (int): 块序号。
        metadata (dict): 额外元数据。
    """

    chunk_id: str
    content: str
    source_file: str
    page_number: Optional[int] = None
    chunk_index: int = 0
    metadata: Optional[dict[str, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ParsingResult:
    """解析结果数据结构。
    Attributes:
        success (bool): 是否成功。
        chunks (list[TextChunk]): 文本块列表。
        total_pages (int): 总页数。
        total_chars (int): 总字符数。
        error_message (Optional[str]): 错误信息。
        parsing_stats (dict): 解析统计。
    """

    success: bool
    chunks: list[TextChunk]
    total_pages: int = 0
    total_chars: int = 0
    error_message: Optional[str] = None
    parsing_stats: Optional[dict[str, Any]] = None

    def __post_init__(self):
        if self.parsing_stats is None:
            self.parsing_stats = {}


class DocumentParser:
    """文档解析器主类，支持多格式解析和多种分块策略。
    支持PDF、DOCX、TXT、MD等格式，分块策略可选'recursive'、'character'、'paragraph'。
    """

    def __init__(
        self,
        chunk_strategy: str = "recursive",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """初始化文档解析器。
        Args:
            chunk_strategy (str): 分块策略 ("recursive", "character", "paragraph")。
            chunk_size (int): 分块大小。
            chunk_overlap (int): 分块重叠大小。
        """
        self.chunk_strategy = chunk_strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._init_text_splitter()
        logger.info(
            f"DocumentParser initialized with strategy: {chunk_strategy}, size: {chunk_size}, overlap: {chunk_overlap}",
        )

    def _init_text_splitter(self) -> None:
        """初始化文本分块器。
        """
        if LANGCHAIN_AVAILABLE:
            if self.chunk_strategy == "recursive":
                self.text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""],
                )
            elif self.chunk_strategy == "character":
                self.text_splitter = CharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    separator="\n",
                )
            else:
                self.text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                )
        else:
            logger.warning("LangChain not available, using simple text splitting")
            self.text_splitter = None

    def parse_document(
        self,
        file_path: Union[str, Path],
        file_content: Optional[bytes] = None,
    ) -> ParsingResult:
        """解析文档文件。
        Args:
            file_path (str|Path): 文件路径。
            file_content (Optional[bytes]): 文件内容（字节）。
        Returns:
            ParsingResult: 解析结果。
        """
        try:
            file_path = Path(file_path)
            file_extension = file_path.suffix.lower()
            logger.info(f"Parsing document: {file_path.name} ({file_extension})")
            if file_extension == ".pdf":
                return self._parse_pdf(file_path, file_content)
            elif file_extension == ".docx":
                return self._parse_docx(file_path, file_content)
            elif file_extension in [".txt", ".md"]:
                return self._parse_text(file_path, file_content)
            else:
                return ParsingResult(
                    success=False,
                    chunks=[],
                    error_message=f"Unsupported file format: {file_extension}",
                )
        except Exception as e:
            logger.error(f"Error parsing document {file_path}: {e}")
            return ParsingResult(success=False, chunks=[], error_message=str(e))

    def _parse_pdf(
        self,
        file_path: Path,
        file_content: Optional[bytes] = None,
    ) -> ParsingResult:
        """解析PDF文件"""
        try:
            # 尝试多种PDF解析方法
            text_content = ""
            total_pages = 0

            # 方法1: 使用PyMuPDF (fitz) - 通常最快最准
            if PYMUPDF_AVAILABLE:
                try:
                    logger.info("Attempting PDF parsing with PyMuPDF (fitz)...")
                    if file_content:
                        pdf_doc = fitz.open(stream=file_content, filetype="pdf")
                    else:
                        pdf_doc = fitz.open(file_path)

                    total_pages = len(pdf_doc)
                    for page_num in range(total_pages):
                        page = pdf_doc.load_page(page_num)
                        page_text = page.get_text("text")
                        if page_text:
                            text_content += (
                                f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                            )

                    pdf_doc.close()

                    if text_content.strip():
                        logger.info(
                            f"Successfully parsed PDF with PyMuPDF (fitz): {total_pages} pages",
                        )
                        return self._create_chunks(
                            text_content,
                            str(file_path),
                            total_pages,
                        )

                except Exception as e:
                    logger.warning(f"PyMuPDF (fitz) parsing failed: {e}")

            # 方法2: 使用pdfplumber（更好的表格和布局处理）
            if PDFPLUMBER_AVAILABLE:
                try:
                    logger.info("Attempting PDF parsing with pdfplumber...")
                    # pdfplumber 需要一个文件对象
                    if file_content:
                        import io

                        file_obj = io.BytesIO(file_content)
                        pdf = pdfplumber.open(file_obj)
                    else:
                        pdf = pdfplumber.open(file_path)

                    total_pages = len(pdf.pages)
                    for page_num, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text_content += (
                                f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                            )

                    pdf.close()

                    if text_content.strip():
                        logger.info(
                            f"Successfully parsed PDF with pdfplumber: {total_pages} pages",
                        )
                        return self._create_chunks(
                            text_content,
                            str(file_path),
                            total_pages,
                        )

                except Exception as e:
                    logger.warning(f"pdfplumber parsing failed: {e}")

            # 方法3: 使用PyPDF2（备用方案）
            if PDF2_AVAILABLE:
                try:
                    logger.info("Attempting PDF parsing with PyPDF2...")
                    if file_content:
                        import io

                        file_obj = io.BytesIO(file_content)
                        pdf_reader = PyPDF2.PdfReader(file_obj)
                    else:
                        pdf_reader = PyPDF2.PdfReader(file_path)

                    total_pages = len(pdf_reader.pages)
                    for page_num, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text_content += (
                                f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                            )

                    if text_content.strip():
                        logger.info(
                            f"Successfully parsed PDF with PyPDF2: {total_pages} pages",
                        )
                        return self._create_chunks(
                            text_content,
                            str(file_path),
                            total_pages,
                        )

                except Exception as e:
                    logger.warning(f"PyPDF2 parsing failed: {e}")

            # 如果所有方法都失败
            return ParsingResult(
                success=False,
                chunks=[],
                error_message="All PDF parsing methods failed. Please ensure the PDF is not corrupted or password-protected.",
            )

        except Exception as e:
            logger.error(f"PDF parsing error: {e}")
            return ParsingResult(
                success=False,
                chunks=[],
                error_message=f"PDF parsing failed: {e!s}",
            )

    def _parse_docx(
        self,
        file_path: Path,
        file_content: Optional[bytes] = None,
    ) -> ParsingResult:
        """解析DOCX文件"""
        try:
            if not DOCX_AVAILABLE:
                return ParsingResult(
                    success=False,
                    chunks=[],
                    error_message="python-docx library not available",
                )

            logger.info("Parsing DOCX file...")

            if file_content:
                import io

                doc = docx.Document(io.BytesIO(file_content))
            else:
                doc = docx.Document(file_path)

            text_content = ""
            total_pages = 0  # DOCX没有明确的页数概念

            # 提取段落文本
            for para in doc.paragraphs:
                if para.text.strip():
                    text_content += para.text + "\n\n"

            # 提取表格文本
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(
                        [cell.text for cell in row.cells if cell.text.strip()],
                    )
                    if row_text:
                        text_content += row_text + "\n"
                text_content += "\n"

            if text_content.strip():
                logger.info("Successfully parsed DOCX file")
                return self._create_chunks(text_content, str(file_path), total_pages)
            else:
                return ParsingResult(
                    success=False,
                    chunks=[],
                    error_message="No text content extracted from DOCX file",
                )

        except Exception as e:
            logger.error(f"DOCX parsing error: {e}")
            return ParsingResult(
                success=False,
                chunks=[],
                error_message=f"DOCX parsing failed: {e!s}",
            )

    def _parse_text(
        self,
        file_path: Path,
        file_content: Optional[bytes] = None,
    ) -> ParsingResult:
        """解析文本文件"""
        try:
            logger.info("Parsing text file...")

            if file_content:
                text_content = file_content.decode("utf-8")
            else:
                with open(file_path, encoding="utf-8") as f:
                    text_content = f.read()

            if text_content.strip():
                logger.info("Successfully parsed text file")
                return self._create_chunks(text_content, str(file_path), 1)
            else:
                return ParsingResult(
                    success=False,
                    chunks=[],
                    error_message="Empty text file",
                )

        except Exception as e:
            logger.error(f"Text parsing error: {e}")
            return ParsingResult(
                success=False,
                chunks=[],
                error_message=f"Text parsing failed: {e!s}",
            )

    def _create_chunks(
        self,
        text_content: str,
        source_file: str,
        total_pages: int,
    ) -> ParsingResult:
        """创建文本块"""
        try:
            # 预处理文本
            text_content = self._preprocess_text(text_content)

            # 分块
            if self.text_splitter and LANGCHAIN_AVAILABLE:
                # 使用LangChain分块器
                chunk_texts = self.text_splitter.split_text(text_content)
            else:
                # 简单分块
                chunk_texts = self._simple_split_text(text_content)

            # 创建TextChunk对象
            chunks = []
            for i, chunk_text in enumerate(chunk_texts):
                if chunk_text.strip():
                    chunk = TextChunk(
                        chunk_id=str(uuid.uuid4()),
                        content=chunk_text.strip(),
                        source_file=source_file,
                        chunk_index=i,
                        metadata={
                            "chunk_size": len(chunk_text),
                            "chunk_strategy": self.chunk_strategy,
                            "total_chunks": len(chunk_texts),
                        },
                    )
                    chunks.append(chunk)

            # 计算统计信息
            total_chars = sum(len(chunk.content) for chunk in chunks)

            parsing_stats = {
                "chunk_strategy": self.chunk_strategy,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "total_chunks": len(chunks),
                "avg_chunk_size": total_chars / len(chunks) if chunks else 0,
                "parsing_library": "pdfplumber"
                if PDFPLUMBER_AVAILABLE
                else "PyPDF2"
                if PDF2_AVAILABLE
                else "unknown",
            }

            logger.info(
                f"Created {len(chunks)} chunks with {total_chars} total characters",
            )

            return ParsingResult(
                success=True,
                chunks=chunks,
                total_pages=total_pages,
                total_chars=total_chars,
                parsing_stats=parsing_stats,
            )

        except Exception as e:
            logger.error(f"Error creating chunks: {e}")
            return ParsingResult(
                success=False,
                chunks=[],
                error_message=f"Chunk creation failed: {e!s}",
            )

    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 移除多余的空白字符
        text = re.sub(r"\s+", " ", text)

        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff。，！？；：""' "（）【】《》、]", " ", text)

        # 标准化换行符
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        return text.strip()

    def _simple_split_text(self, text: str) -> list[str]:
        """简单文本分块"""
        chunks = []
        current_chunk = ""

        # 按段落分割
        paragraphs = text.split("\n\n")

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # 如果当前块加上新段落超过大小限制，保存当前块
            if len(current_chunk) + len(para) > self.chunk_size and current_chunk:
                chunks.append(current_chunk)
                # 保留重叠部分
                overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                current_chunk = current_chunk[overlap_start:] + "\n\n" + para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk)

        return chunks


class DocumentParserConfig:
    """文档解析器配置类"""

    @staticmethod
    def get_optimal_config(file_type: str, file_size: int) -> dict[str, Any]:
        """根据文件类型和大小获取最优配置

        Args:
        ----
            file_type: 文件类型 (pdf, docx, txt)
            file_size: 文件大小（字节）

        Returns:
        -------
            Dict: 配置参数

        """
        if file_type == "pdf":
            if file_size > 10 * 1024 * 1024:  # 大于10MB
                return {
                    "chunk_strategy": "recursive",
                    "chunk_size": 1500,
                    "chunk_overlap": 300,
                }
            else:
                return {
                    "chunk_strategy": "recursive",
                    "chunk_size": 1000,
                    "chunk_overlap": 200,
                }
        elif file_type == "docx":
            return {
                "chunk_strategy": "paragraph",
                "chunk_size": 800,
                "chunk_overlap": 150,
            }
        else:  # txt, md
            return {
                "chunk_strategy": "character",
                "chunk_size": 1200,
                "chunk_overlap": 200,
            }


# 测试函数
def test_document_parser():
    """测试文档解析器"""
    print("🧪 Testing Document Parser...")

    # 检查依赖
    print(f"PDF2 Available: {PDF2_AVAILABLE}")
    print(f"PDFPlumber Available: {PDFPLUMBER_AVAILABLE}")
    print(f"DOCX Available: {DOCX_AVAILABLE}")
    print(f"LangChain Available: {LANGCHAIN_AVAILABLE}")

    # 创建测试文本
    test_text = """
    这是一个测试文档。

    第二段内容包含更多的信息。

    第三段内容用于测试分块功能。

    第四段内容继续测试。

    第五段内容是最后一段。
    """

    # 创建解析器
    parser = DocumentParser(
        chunk_strategy="recursive",
        chunk_size=100,
        chunk_overlap=20,
    )

    # 测试文本解析
    result = parser._create_chunks(test_text, "test.txt", 1)

    print(f"✅ Parsing successful: {result.success}")
    print(f"📊 Total chunks: {len(result.chunks)}")
    print(f"📏 Total characters: {result.total_chars}")

    for i, chunk in enumerate(result.chunks):
        print(f"Chunk {i+1}: {chunk.chunk_id[:8]}... ({len(chunk.content)} chars)")
        print(f"  Content: {chunk.content[:50]}...")

    return result


if __name__ == "__main__":
    test_document_parser()
