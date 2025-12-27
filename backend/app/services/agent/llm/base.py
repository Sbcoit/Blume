"""
Base LLM interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMMessage:
    """LLM message structure"""
    def __init__(self, role: str, content: str):
        self.role = role  # 'system', 'user', 'assistant'
        self.content = content


class BaseLLM(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def chat(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Send a chat completion request"""
        pass
    
    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Model name being used"""
        pass

