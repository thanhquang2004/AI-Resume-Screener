"""
PDF Parser - Extract text from PDF files.
"""
from typing import Optional
from pathlib import Path
import io
import re


class PDFParser:
    """Parse PDF files and extract text content."""
    
    def __init__(self):
        """Initialize PDF parser."""
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if required libraries are installed."""
        try:
            from pdfminer.high_level import extract_text
            self.extract_text = extract_text
        except ImportError:
            raise ImportError("pdfminer.six is required. Install with: pip install pdfminer.six")
    
    def parse(self, file_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if path.suffix.lower() != '.pdf':
            raise ValueError(f"Not a PDF file: {file_path}")
        
        try:
            text = self.extract_text(str(path))
            return self._clean_text(text)
        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF: {e}")
    
    def parse_bytes(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF bytes.
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Extracted text content
        """
        try:
            text = self.extract_text(io.BytesIO(pdf_bytes))
            return self._clean_text(text)
        except Exception as e:
            raise RuntimeError(f"Failed to parse PDF bytes: {e}")
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep essential punctuation
        text = re.sub(r'[^\w\s\.\,\-\(\)\@\+\#\/]', ' ', text)
        
        # Clean up spaces
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
