"""
Integration endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_database
from app.api.v1.auth import get_current_user_id
from app.integrations.registry import integration_registry
from pydantic import BaseModel

router = APIRouter(prefix="/integrations", tags=["integrations"])


class IntegrationInfo(BaseModel):
    provider: str
    name: str


@router.get("", response_model=List[IntegrationInfo])
async def list_integrations():
    """List available integrations"""
    # For now, return hardcoded list
    # In production, this would come from the registry
    return [
        IntegrationInfo(provider="google", name="Google Account"),  # Unified Google Account
        IntegrationInfo(provider="notion", name="Notion"),
    ]


@router.get("/connected")
async def list_connected_integrations(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_database)
):
    """List user's connected integrations"""
    from app.models.integration import Integration
    from uuid import UUID
    
    user_integrations = db.query(Integration).filter(
        Integration.user_id == UUID(user_id)
    ).all()
    
    # Consolidate Google Calendar and Google Docs into single "google" provider
    connected_providers = set()
    for integration in user_integrations:
        if integration.provider in ["google_calendar", "google_docs"]:
            # If either Google Calendar or Docs is connected, mark "google" as connected
            connected_providers.add("google")
        else:
            connected_providers.add(integration.provider)
    
    return [
        {
            "id": provider,  # Use provider as ID for frontend
            "provider": provider,
        }
        for provider in connected_providers
    ]


@router.post("/{provider}/authorize")
async def authorize_integration(
    provider: str,
    user_id: str = Depends(get_current_user_id)
):
    """Initiate OAuth flow for integration"""
    if provider == "google":
        # Use unified Google OAuth for Calendar, Docs, Drive, etc.
        from app.integrations.google.oauth import GoogleOAuth
        import secrets
        import base64
        import json
        
        # Encode user_id in state for callback verification
        state_data = {
            "user_id": user_id,
            "nonce": secrets.token_urlsafe(16)
        }
        state = base64.urlsafe_b64encode(json.dumps(state_data).encode()).decode()
        
        auth_url = GoogleOAuth.get_authorization_url(state)
        return {
            "auth_url": auth_url,
            "provider": "google",  # Unified Google Account connection
        }
    
    # For other providers (Notion, etc.)
    return {
        "auth_url": f"/oauth/{provider}/authorize?user_id={user_id}",
        "provider": provider,
    }


@router.get("/google/callback")
async def google_oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_database)
):
    """Handle Google OAuth callback - connects both Calendar and Docs"""
    from app.integrations.google.oauth import GoogleOAuth
    from app.models.integration import Integration, IntegrationProvider
    from uuid import UUID, uuid4
    import base64
    import json
    
    # Extract user_id from state
    try:
        state_data = json.loads(base64.urlsafe_b64decode(state.encode()).decode())
        user_id = state_data.get("user_id")
        if not user_id:
            return {"error": "Invalid state token"}
    except Exception as e:
        return {"error": f"Invalid state token: {str(e)}"}
    
    # Exchange code for credentials
    credentials = GoogleOAuth.exchange_code_for_credentials(code)
    
    # Store credentials for both Google Calendar and Google Docs
    # They share the same credentials since it's one Google account
    
    # Create/update Google Calendar integration
    calendar_integration = db.query(Integration).filter(
        Integration.user_id == UUID(user_id),
        Integration.provider == IntegrationProvider.GOOGLE_CALENDAR.value
    ).first()
    
    if not calendar_integration:
        calendar_integration = Integration(
            id=uuid4(),
            user_id=UUID(user_id),
            provider=IntegrationProvider.GOOGLE_CALENDAR.value,
            credentials=credentials,
            status="connected"
        )
        db.add(calendar_integration)
    else:
        calendar_integration.credentials = credentials
        calendar_integration.status = "connected"
    
    # Create/update Google Docs integration
    docs_integration = db.query(Integration).filter(
        Integration.user_id == UUID(user_id),
        Integration.provider == IntegrationProvider.GOOGLE_DOCS.value
    ).first()
    
    if not docs_integration:
        docs_integration = Integration(
            id=uuid4(),
            user_id=UUID(user_id),
            provider=IntegrationProvider.GOOGLE_DOCS.value,
            credentials=credentials,  # Same credentials
            status="connected"
        )
        db.add(docs_integration)
    else:
        docs_integration.credentials = credentials
        docs_integration.status = "connected"
    
    db.commit()
    
    return {
        "status": "connected",
        "providers": ["google_calendar", "google_docs"]
    }


@router.delete("/{integration_id}")
async def disconnect_integration(
    integration_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_database)
):
    """Disconnect an integration"""
    from app.models.integration import Integration, IntegrationProvider
    from app.core.exceptions import NotFoundError
    from uuid import UUID
    
    # Handle Google account disconnection (disconnect both Calendar and Docs)
    if integration_id == "google":
        # Delete both Google Calendar and Google Docs integrations
        google_integrations = db.query(Integration).filter(
            Integration.user_id == UUID(user_id),
            Integration.provider.in_([IntegrationProvider.GOOGLE_CALENDAR.value, IntegrationProvider.GOOGLE_DOCS.value])
        ).all()
        
        if not google_integrations:
            raise NotFoundError("Google Account integration not found")
        
        for integration in google_integrations:
            db.delete(integration)
        db.commit()
        
        return {"status": "disconnected", "provider": "google"}
    
    # For other integrations, use integration_id as UUID
    integration = db.query(Integration).filter(
        Integration.id == UUID(integration_id),
        Integration.user_id == UUID(user_id)
    ).first()
    
    if not integration:
        raise NotFoundError("Integration not found")
    
    db.delete(integration)
    db.commit()
    
    return {"status": "disconnected"}
