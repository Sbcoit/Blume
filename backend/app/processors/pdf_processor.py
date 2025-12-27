"""
PDF processor implementation
"""
from typing import Dict, Any, Optional
import PyPDF2
from io import BytesIO
from app.processors.base import BaseProcessor


class PDFProcessor(BaseProcessor):
    """PDF document processor"""
    
    async def process(self, data: bytes, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process PDF file"""
        text = await self.extract_text(data)
        
        return {
            "type": "pdf",
            "text": text,
            "pages": len(PyPDF2.PdfReader(BytesIO(data)).pages),
            "metadata": metadata or {}
        }
    
    async def extract_text(self, data: bytes) -> str:
        """Extract text from PDF"""
        pdf_reader = PyPDF2.PdfReader(BytesIO(data))
        text = ""
        
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    
    async def analyze(self, data: bytes) -> Dict[str, Any]:
        """Analyze PDF structure"""
        pdf_reader = PyPDF2.PdfReader(BytesIO(data))
        
        return {
            "pages": len(pdf_reader.pages),
            "encrypted": pdf_reader.is_encrypted,
            "metadata": pdf_reader.metadata or {}
        }

