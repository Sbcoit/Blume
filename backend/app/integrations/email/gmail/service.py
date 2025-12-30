"""
Gmail integration service
"""
from typing import List, Dict, Optional, Any
from base64 import urlsafe_b64encode
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.integrations.email.base_email import BaseEmailIntegration, Email
from app.integrations.base import IntegrationStatus
from app.integrations.google.oauth import GoogleOAuth
from googleapiclient.discovery import build
import json
import logging

logger = logging.getLogger(__name__)


class GmailService(BaseEmailIntegration):
    """Gmail integration service"""
    
    def __init__(self):
        self._connected = False
        self._credentials = None
    
    @property
    def name(self) -> str:
        return "Gmail"
    
    @property
    def provider(self) -> str:
        return "google_gmail"
    
    async def connect(self, credentials: dict) -> bool:
        """Connect to Gmail using shared Google OAuth credentials"""
        try:
            # Refresh credentials if needed
            credentials = GoogleOAuth.refresh_credentials_if_needed(credentials)
            self._credentials = credentials
            self._connected = True
            return True
        except Exception as e:
            logger.error(f"Error connecting to Gmail: {e}", exc_info=True)
            self._connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Gmail"""
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
            self._credentials = GoogleOAuth.refresh_credentials_if_needed(self._credentials)
            return True
        except Exception as e:
            logger.error(f"Error refreshing credentials: {e}", exc_info=True)
            return False
    
    def _create_message(self, email: Email) -> Dict[str, str]:
        """Create a message object for Gmail API"""
        message = MIMEMultipart('alternative')
        message['to'] = email.to
        message['subject'] = email.subject
        
        if email.cc:
            message['cc'] = ', '.join(email.cc)
        if email.bcc:
            message['bcc'] = ', '.join(email.bcc)
        
        # Add body
        text_part = MIMEText(email.body, 'plain')
        message.attach(text_part)
        
        # Encode message
        raw_message = urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}
    
    async def send_email(self, email: Email) -> bool:
        """Send an email"""
        if not self._connected or not self._credentials:
            raise ValueError("Not connected to Gmail")
        
        try:
            creds = GoogleOAuth.get_credentials_from_dict(self._credentials)
            service = build('gmail', 'v1', credentials=creds)
            
            message = self._create_message(email)
            sent_message = service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            logger.info(f"Email sent successfully. Message ID: {sent_message.get('id')}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            raise
    
    async def draft_email(self, email: Email) -> str:
        """Create a draft email"""
        if not self._connected or not self._credentials:
            raise ValueError("Not connected to Gmail")
        
        try:
            creds = GoogleOAuth.get_credentials_from_dict(self._credentials)
            service = build('gmail', 'v1', credentials=creds)
            
            message = self._create_message(email)
            draft = service.users().drafts().create(
                userId='me',
                body={'message': message}
            ).execute()
            
            draft_id = draft.get('id')
            logger.info(f"Draft created successfully. Draft ID: {draft_id}")
            return draft_id
        except Exception as e:
            logger.error(f"Error creating draft: {e}", exc_info=True)
            raise
    
    async def list_emails(self, query: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
        """List emails"""
        if not self._connected or not self._credentials:
            raise ValueError("Not connected to Gmail")
        
        try:
            creds = GoogleOAuth.get_credentials_from_dict(self._credentials)
            service = build('gmail', 'v1', credentials=creds)
            
            # List messages
            results = service.users().messages().list(
                userId='me',
                q=query or '',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            email_list = []
            
            for msg in messages:
                # Get message details
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
                
                email_list.append({
                    'id': message['id'],
                    'from': headers.get('From', ''),
                    'subject': headers.get('Subject', ''),
                    'date': headers.get('Date', ''),
                    'snippet': message.get('snippet', '')
                })
            
            return email_list
        except Exception as e:
            logger.error(f"Error listing emails: {e}", exc_info=True)
            raise
    
    async def get_email(self, email_id: str) -> Email:
        """Get an email by ID"""
        if not self._connected or not self._credentials:
            raise ValueError("Not connected to Gmail")
        
        try:
            creds = GoogleOAuth.get_credentials_from_dict(self._credentials)
            service = build('gmail', 'v1', credentials=creds)
            
            message = service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
            
            # Extract body
            body = ''
            payload = message.get('payload', {})
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            from base64 import urlsafe_b64decode
                            body = urlsafe_b64decode(data).decode('utf-8')
                            break
            
            # If no body found in parts, try direct body
            if not body and 'body' in payload:
                data = payload['body'].get('data', '')
                if data:
                    from base64 import urlsafe_b64decode
                    body = urlsafe_b64decode(data).decode('utf-8')
            
            # Extract recipients
            to = headers.get('To', '')
            cc = headers.get('Cc', '')
            
            email = Email(
                to=to,
                subject=headers.get('Subject', ''),
                body=body,
                cc=[cc] if cc else [],
                email_id=email_id
            )
            
            return email
        except Exception as e:
            logger.error(f"Error getting email: {e}", exc_info=True)
            raise

