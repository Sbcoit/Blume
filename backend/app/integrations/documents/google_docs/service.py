"""
Google Docs integration service
"""
from typing import List, Dict
from app.integrations.documents.base_documents import BaseDocumentsIntegration, Document
from app.integrations.base import IntegrationStatus
from app.integrations.google.oauth import GoogleOAuth
from googleapiclient.discovery import build
import json


class GoogleDocsService(BaseDocumentsIntegration):
    """Google Docs integration service"""
    
    def __init__(self):
        self._connected = False
        self._credentials = None
    
    @property
    def name(self) -> str:
        return "Google Docs"
    
    @property
    def provider(self) -> str:
        return "google_docs"
    
    async def connect(self, credentials: dict) -> bool:
        """Connect to Google Docs using shared Google OAuth credentials"""
        try:
            # Refresh credentials if needed
            credentials = GoogleOAuth.refresh_credentials_if_needed(credentials)
            self._credentials = credentials
            self._connected = True
            return True
        except Exception as e:
            print(f"Error connecting to Google Docs: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Google Docs"""
        self._connected = False
        self._credentials = None
        return True
    
    async def get_status(self) -> IntegrationStatus:
        """Get connection status"""
        if self._connected:
            return IntegrationStatus.CONNECTED
        return IntegrationStatus.DISCONNECTED
    
    async def refresh_credentials(self) -> bool:
        """Refresh OAuth credentials"""
        if not self._credentials:
            return False
        try:
            from app.integrations.google.oauth import GoogleOAuth
            self._credentials = GoogleOAuth.refresh_credentials_if_needed(self._credentials)
            return True
        except Exception as e:
            print(f"Error refreshing credentials: {e}")
            return False
    
    async def create_document(self, document: Document) -> str:
        """Create a document"""
        if not self._connected or not self._credentials:
            raise ValueError("Not connected to Google Docs")
        
        creds = GoogleOAuth.get_credentials_from_dict(self._credentials)
        docs_service = build('docs', 'v1', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Create a new Google Doc
        doc = docs_service.documents().create(body={'title': document.title}).execute()
        document_id = doc.get('documentId')
        
        # If content is provided, insert it
        if document.content:
            requests = [{
                'insertText': {
                    'location': {'index': 1},
                    'text': document.content
                }
            }]
            docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
        
        return document_id
    
    async def get_document(self, document_id: str) -> Document:
        """Get a document"""
        if not self._connected or not self._credentials:
            raise ValueError("Not connected to Google Docs")
        
        creds = GoogleOAuth.get_credentials_from_dict(self._credentials)
        docs_service = build('docs', 'v1', credentials=creds)
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Get document metadata
        doc = docs_service.documents().get(documentId=document_id).execute()
        title = doc.get('title', '')
        
        # Extract text content
        content = doc.get('body', {}).get('content', [])
        text_content = self._extract_text_from_content(content)
        
        return Document(title=title, content=text_content, document_id=document_id)
    
    def _extract_text_from_content(self, content: List[Dict]) -> str:
        """Extract text from Google Docs content structure"""
        text_parts = []
        for element in content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for text_elem in paragraph.get('elements', []):
                    if 'textRun' in text_elem:
                        text_parts.append(text_elem['textRun'].get('content', ''))
        return ''.join(text_parts)
    
    async def update_document(self, document_id: str, document: Document) -> bool:
        """Update a document"""
        if not self._connected or not self._credentials:
            raise ValueError("Not connected to Google Docs")
        
        creds = GoogleOAuth.get_credentials_from_dict(self._credentials)
        docs_service = build('docs', 'v1', credentials=creds)
        
        requests = []
        
        # Update title if provided
        if document.title:
            # Get current document to find title element
            doc = docs_service.documents().get(documentId=document_id).execute()
            # Note: Title update requires Drive API, but we'll update content here
            pass  # Title updates are complex, skip for now
        
        # Replace all content if provided
        if document.content:
            # First, get document to find end index
            doc = docs_service.documents().get(documentId=document_id).execute()
            end_index = doc.get('body', {}).get('content', [{}])[-1].get('endIndex', 1)
            
            # Delete existing content (except first character which is required)
            if end_index > 1:
                requests.append({
                    'deleteContentRange': {
                        'range': {
                            'startIndex': 1,
                            'endIndex': end_index - 1
                        }
                    }
                })
            
            # Insert new content
            requests.append({
                'insertText': {
                    'location': {'index': 1},
                    'text': document.content
                }
            })
        
        if requests:
            docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
        
        return True
    
    async def list_documents(self) -> List[dict]:
        """List all documents"""
        if not self._connected or not self._credentials:
            raise ValueError("Not connected to Google Docs")
        
        creds = GoogleOAuth.get_credentials_from_dict(self._credentials)
        drive_service = build('drive', 'v3', credentials=creds)
        
        # Search for Google Docs files
        results = drive_service.files().list(
            q="mimeType='application/vnd.google-apps.document'",
            pageSize=100,
            fields="files(id, name, modifiedTime, createdTime)"
        ).execute()
        
        documents = []
        for file in results.get('files', []):
            documents.append({
                'id': file.get('id'),
                'title': file.get('name'),
                'modified_time': file.get('modifiedTime'),
                'created_time': file.get('createdTime')
            })
        
        return documents

