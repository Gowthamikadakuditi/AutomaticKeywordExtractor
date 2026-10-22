"""
Document Reader Utility.

Safely extracts textual content from uploaded PDF, DOCX, and TXT files.
Handles encoding varieties, validates file size and formats,
detects scanned/empty documents, and ensures safe in-memory or temporary handling.
"""

import io
import os
from typing import Tuple
from werkzeug.utils import secure_filename
import docx
import pymupdf  # PyMuPDF

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

class DocumentReaderError(Exception):
    """Custom exception for user-friendly document reading errors."""
    pass

def validate_file_metadata(filename: str, file_size: int) -> str:
    """
    Validates file extension and file size.
    Returns the lowercased extension.
    """
    if not filename:
        raise DocumentReaderError("No file was provided.")

    clean_name = secure_filename(filename)
    _, ext = os.path.splitext(clean_name)
    ext = ext.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise DocumentReaderError(
            f"Unsupported file format '{ext}'. Allowed formats are: .pdf, .docx, and .txt"
        )

    if file_size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        raise DocumentReaderError(
            f"File exceeds maximum allowed size ({max_mb} MB). Please upload a smaller document."
        )

    return ext

def extract_text_from_txt(file_bytes: bytes) -> str:
    """
    Decodes plain text with UTF-8, UTF-16, or Latin-1 fallback.
    """
    for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise DocumentReaderError("Unable to decode the TXT file. Please verify its character encoding.")

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text page-by-page from PDF using PyMuPDF.
    Detects scanned or image-only documents.
    """
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise DocumentReaderError(f"Corrupted or invalid PDF file: {str(e)}")

    extracted_pages = []
    try:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            if text and text.strip():
                extracted_pages.append(text.strip())
    finally:
        doc.close()

    full_text = "\n\n".join(extracted_pages).strip()
    if not full_text:
        raise DocumentReaderError(
            "The uploaded PDF contains no extractable digital text. "
            "It may be a scanned image or protected document requiring Optical Character Recognition (OCR)."
        )

    return full_text

def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extracts text paragraphs and table cells from a Microsoft Word .docx file.
    """
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
    except Exception as e:
        raise DocumentReaderError(f"Unable to read DOCX document: {str(e)}")

    paragraphs = []
    # Read body paragraphs
    for p in doc.paragraphs:
        t = p.text.strip()
        if t:
            paragraphs.append(t)

    # Also read table cells if present
    for table in doc.tables:
        for row in table.rows:
            row_texts = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_texts:
                paragraphs.append(" | ".join(row_texts))

    full_text = "\n\n".join(paragraphs).strip()
    if not full_text:
        raise DocumentReaderError("The uploaded DOCX document contains no text.")

    return full_text

def extract_text_from_stream(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """
    Main dispatch function to validate and extract text from supported file types.
    
    Returns:
        Tuple of (clean_text, clean_filename)
    """
    ext = validate_file_metadata(filename, len(file_bytes))
    clean_name = secure_filename(filename)

    if ext == ".txt":
        text = extract_text_from_txt(file_bytes)
    elif ext == ".pdf":
        text = extract_text_from_pdf(file_bytes)
    elif ext == ".docx":
        text = extract_text_from_docx(file_bytes)
    else:
        raise DocumentReaderError(f"Unsupported file format: {ext}")

    return text.strip(), clean_name
