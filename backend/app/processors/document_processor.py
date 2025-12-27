"""
Document processor orchestrator
"""
from typing import Dict, Any, Optional, List
from app.processors.base import BaseProcessor
from app.processors.pdf_processor import PDFProcessor
from app.processors.image_processor import ImageProcessor


class DocumentProcessor:
    """Orchestrator for document processing"""
    
    def __init__(self):
        self.processors: Dict[str, BaseProcessor] = {
            "pdf": PDFProcessor(),
            "image": ImageProcessor(),
        }
    
    def register_processor(self, file_type: str, processor: BaseProcessor):
        """Register a processor for a file type"""
        self.processors[file_type] = processor
    
    def _detect_file_type(self, filename: str, data: bytes) -> str:
        """Detect file type from filename or content"""
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf'):
            return "pdf"
        elif filename_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            return "image"
        else:
            return "unknown"
    
    async def process(
        self,
        data: bytes,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process a document"""
        file_type = self._detect_file_type(filename, data)
        
        if file_type not in self.processors:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        processor = self.processors[file_type]
        result = await processor.process(data, metadata)
        result["filename"] = filename
        result["file_type"] = file_type
        
        return result
    
    async def extract_text(
        self,
        data: bytes,
        filename: str
    ) -> str:
        """Extract text from document"""
        file_type = self._detect_file_type(filename, data)
        
        if file_type not in self.processors:
            return ""
        
        processor = self.processors[file_type]
        return await processor.extract_text(data)

