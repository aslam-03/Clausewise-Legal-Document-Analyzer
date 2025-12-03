from pathlib import Path
from docx import Document
import fitz  # PyMuPDF
import re

class TextExtractor:
    @staticmethod
    def extract_text(file_path: str | Path) -> str:
        """Handle both string and Path objects"""
        file_path = Path(file_path) if isinstance(file_path, str) else file_path
        
        # Convert path to string for extension check
        file_str = str(file_path).lower()
        
        if file_str.endswith('.pdf'):
            return TextExtractor._extract_from_pdf(file_path)
        elif file_str.endswith('.docx'):
            return TextExtractor._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

    @staticmethod
    def _extract_from_pdf(file_path: Path) -> str:
        """Extract text from PDF using PyMuPDF"""
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return TextExtractor._clean_text(text)

    @staticmethod
    def _extract_from_docx(file_path: Path) -> str:
        """Extract text from DOCX using python-docx"""
        doc = Document(file_path)
        return TextExtractor._clean_text("\n".join([para.text for para in doc.paragraphs]))

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean extracted text"""
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'Page \d+ of \d+', '', text)
        return text