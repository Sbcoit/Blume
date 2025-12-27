"""
Base processor interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseProcessor(ABC):
    """Base class for all processors"""
    
    @abstractmethod
    async def process(self, data: bytes, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process the input data"""
        pass
    
    @abstractmethod
    async def extract_text(self, data: bytes) -> str:
        """Extract text from the input data"""
        pass
    
    @abstractmethod
    async def analyze(self, data: bytes) -> Dict[str, Any]:
        """Analyze the input data"""
        pass

