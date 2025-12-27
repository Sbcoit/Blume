"""
Base handler interface for agent task handlers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseHandler(ABC):
    """Base class for all agent task handlers"""
    
    @property
    @abstractmethod
    def task_type(self) -> str:
        """Task type this handler processes"""
        pass
    
    @abstractmethod
    async def handle(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a task
        
        Args:
            task_data: Task input data
            
        Returns:
            Task output/result
        """
        pass
    
    @abstractmethod
    def can_handle(self, task_data: Dict[str, Any]) -> bool:
        """Check if this handler can handle the given task"""
        pass

