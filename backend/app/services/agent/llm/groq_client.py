"""
Groq LLM client implementation
"""
from typing import List, Optional, Union, Dict, Any
from groq import Groq
from app.services.agent.llm.base import BaseLLM, LLMMessage, FunctionDefinition
from app.core.config import settings


class GroqClient(BaseLLM):
    """Groq LLM client implementation"""
    
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
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
        max_tokens: Optional[int] = 2048,
        functions: Optional[List[FunctionDefinition]] = None
    ) -> Union[str, Dict[str, Any]]:
        """Send a chat completion request"""
        import logging
        import asyncio
        logger = logging.getLogger(__name__)
        
        # Convert LLMMessage to Groq format
        groq_messages = []
        for msg in messages:
            message_dict = {"role": msg.role, "content": msg.content}
            if msg.function_call:
                message_dict["function_call"] = msg.function_call
            groq_messages.append(message_dict)
        
        # Prepare function definitions if provided
        tools = None
        if functions:
            tools = [
                {
                    "type": "function",
                    "function": func.to_dict()
                }
                for func in functions
            ]
        
        # Prepare request parameters
        request_params = {
            "model": self.model_name,
            "messages": groq_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # Add tools if provided
        if tools:
            request_params["tools"] = tools
            request_params["tool_choice"] = "auto"
        
        try:
            # Run synchronous Groq API call in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(**request_params)
            )
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Request params (sanitized): model={request_params.get('model')}, messages_count={len(request_params.get('messages', []))}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                logger.error(f"API response: {e.response.text}")
            raise
        
        message = response.choices[0].message
        
        # Check if function call was made
        # Handle both tool_calls (newer format) and function_call (older format)
        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_call = message.tool_calls[0]
            return {
                "function_name": tool_call.function.name,
                "arguments": tool_call.function.arguments,
                "tool_call_id": getattr(tool_call, 'id', None)
            }
        elif hasattr(message, 'function_call') and message.function_call:
            # Older format support
            return {
                "function_name": message.function_call.name,
                "arguments": message.function_call.arguments,
                "tool_call_id": None
            }
        
        return message.content or ""
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        # Groq doesn't have embedding API, return empty list or use alternative
        # This can be implemented with a separate embedding service if needed
        raise NotImplementedError("Groq does not provide embedding API")

