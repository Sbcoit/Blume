"""
Groq LLM client implementation
"""
from typing import List, Optional
from groq import Groq
from app.services.agent.llm.base import BaseLLM, LLMMessage
from app.core.config import settings


class GroqClient(BaseLLM):
    """Groq LLM client implementation"""
    
    def __init__(self, model: str = "llama-3.1-70b-versatile"):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self._model = model
    
    @property
    def model_name(self) -> str:
        """Model name being used"""
        return self._model
    
    async def chat(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = 0.7,
        max_tokens: Optional[int] = 2048
    ) -> str:
        """Send a chat completion request"""
        # Convert LLMMessage to Groq format
        groq_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=groq_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return response.choices[0].message.content
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        # Groq doesn't have embedding API, return empty list or use alternative
        # This can be implemented with a separate embedding service if needed
        raise NotImplementedError("Groq does not provide embedding API")

