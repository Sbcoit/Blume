"""
Integration registry system
"""
from typing import Dict, List, Type, Optional
from app.integrations.base import BaseIntegration, IntegrationStatus


class IntegrationRegistry:
    """Registry for managing integrations"""
    
    def __init__(self):
        self._integrations: Dict[str, Type[BaseIntegration]] = {}
        self._instances: Dict[str, BaseIntegration] = {}
    
    def register(self, integration_class: Type[BaseIntegration]):
        """Register an integration class"""
        provider = integration_class().provider
        self._integrations[provider] = integration_class
        return integration_class
    
    def get_integration_class(self, provider: str) -> Optional[Type[BaseIntegration]]:
        """Get integration class by provider"""
        return self._integrations.get(provider)
    
    def create_instance(
        self,
        provider: str,
        instance_id: Optional[str] = None
    ) -> Optional[BaseIntegration]:
        """Create an integration instance"""
        integration_class = self.get_integration_class(provider)
        if not integration_class:
            return None
        
        # Use instance_id for caching if provided
        key = f"{provider}:{instance_id}" if instance_id else provider
        
        if key not in self._instances:
            self._instances[key] = integration_class()
        
        return self._instances[key]
    
    def list_providers(self) -> List[str]:
        """List all registered integration providers"""
        return list(self._integrations.keys())
    
    def get_integration_info(self, provider: str) -> Optional[Dict]:
        """Get integration metadata"""
        integration_class = self.get_integration_class(provider)
        if not integration_class:
            return None
        
        instance = integration_class()
        return {
            "provider": instance.provider,
            "name": instance.name,
        }


# Global registry instance
integration_registry = IntegrationRegistry()

