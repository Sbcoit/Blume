"""
Base LLM interface
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union


class LLMMessage:
    """LLM message structure"""
    def __init__(self, role: str, content: str, function_call: Optional[Dict[str, Any]] = None):
        self.role = role  # 'system', 'user', 'assistant', 'function'
        self.content = content
        self.function_call = function_call  # For function calling support


class FunctionDefinition:
    """Function definition for LLM function calling"""
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any]
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for API"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


class BaseLLM(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def chat(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        functions: Optional[List[FunctionDefinition]] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Send a chat completion request
        
        Returns:
            str: If no function call is made
            Dict[str, Any]: If function call is made, contains 'function_name' and 'arguments'
        """
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

