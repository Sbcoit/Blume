"""
Google OAuth implementation for unified Google account connection
Provides access to both Google Calendar and Google Docs through a single OAuth flow
"""
from typing import Optional, Dict
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from app.core.config import settings
import json
import os


class GoogleOAuth:
    """Google OAuth handler for unified Google account connection"""
    
    # Scopes for Google Account integration (Calendar, Docs, Drive, etc.)
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',  # Google Calendar
        'https://www.googleapis.com/auth/documents',  # Google Docs
        'https://www.googleapis.com/auth/drive.readonly',  # Google Drive (read-only for accessing files)
    ]
    
    REDIRECT_URI = "http://localhost:8000/api/v1/integrations/google/callback"
    
    @staticmethod
    def get_authorization_url(state: str) -> str:
        """Generate Google OAuth authorization URL"""
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise ValueError("Google OAuth credentials not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in environment variables.")
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GoogleOAuth.REDIRECT_URI]
                }
            },
            scopes=GoogleOAuth.SCOPES,
            redirect_uri=GoogleOAuth.REDIRECT_URI
        )
        
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'
        )
        
        return authorization_url
    
    @staticmethod
    def exchange_code_for_credentials(code: str) -> Dict:
        """Exchange authorization code for credentials"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GoogleOAuth.REDIRECT_URI]
                }
            },
            scopes=GoogleOAuth.SCOPES,
            redirect_uri=GoogleOAuth.REDIRECT_URI
        )
        
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Return credentials as dictionary for storage
        return {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
        }
    
    @staticmethod
    def get_credentials_from_dict(cred_dict: Dict) -> Credentials:
        """Create Credentials object from dictionary"""
        return Credentials(
            token=cred_dict.get("token"),
            refresh_token=cred_dict.get("refresh_token"),
            token_uri=cred_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=cred_dict.get("client_id"),
            client_secret=cred_dict.get("client_secret"),
            scopes=cred_dict.get("scopes", GoogleOAuth.SCOPES),
        )
    
    @staticmethod
    def refresh_credentials_if_needed(cred_dict: Dict) -> Dict:
        """Refresh credentials if expired"""
        credentials = GoogleOAuth.get_credentials_from_dict(cred_dict)
        
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            
            # Update dictionary with new token
            cred_dict["token"] = credentials.token
            if credentials.refresh_token:
                cred_dict["refresh_token"] = credentials.refresh_token
        
        return cred_dict

