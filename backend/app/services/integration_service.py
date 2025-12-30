"""
Integration service for checking integration status
"""
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.integration import Integration


class IntegrationService:
    """Service for checking integration connection status"""
    
    @staticmethod
    def is_integration_connected(db: Session, user_id: UUID, provider: str) -> bool:
        """Check if user has a specific integration connected
        
        Args:
            db: Database session
            user_id: User UUID
            provider: Integration provider name (e.g., "google", "notion")
            
        Returns:
            True if integration is connected, False otherwise
        """
        try:
            # Handle Google Account (checks google_calendar, google_docs, and google_gmail)
            if provider == "google":
                result = db.query(Integration).filter(
                    Integration.user_id == user_id,
                    Integration.provider.in_(["google_calendar", "google_docs", "google_gmail"]),
                    Integration.status == "connected"
                ).first()
                return result is not None
            
            # For other providers, check directly
            result = db.query(Integration).filter(
                Integration.user_id == user_id,
                Integration.provider == provider,
                Integration.status == "connected"
            ).first()
            return result is not None
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error checking integration status for {provider}: {e}", exc_info=True)
            return False
    
    @staticmethod
    def get_integration_name(provider: str) -> str:
        """Get user-friendly name for integration
        
        Args:
            provider: Integration provider name
            
        Returns:
            User-friendly integration name
        """
        names = {
            "google": "Google Account",
            "google_calendar": "Google Calendar",
            "google_docs": "Google Docs",
            "google_gmail": "Gmail",
            "notion": "Notion"
        }
        return names.get(provider, provider)

