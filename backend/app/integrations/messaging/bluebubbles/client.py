"""
BlueBubbles API client
"""
import logging
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.integrations.messaging.base_messaging import Message

logger = logging.getLogger(__name__)


class BlueBubblesClient:
    """Client for BlueBubbles REST API"""
    
    def __init__(self):
        self.base_url = settings.BLUEBUBBLES_SERVER_URL.rstrip('/')
        self.password = settings.BLUEBUBBLES_SERVER_PASSWORD
        self.timeout = 30.0
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Content-Type": "application/json",
        }
    
    def _get_params(self) -> Dict[str, str]:
        """Get query parameters with authentication"""
        return {
            "password": self.password,
        }
    
    async def send_message(
        self,
        chat_guid: str = None,
        message: str = None,
        address: str = None,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send a message via BlueBubbles API
        
        Uses the correct format per BlueBubbles documentation:
        - If chat_guid is provided: {"chatGuid": "...", "text": "...", "method": "private-api"}
        - Falls back to other formats only if needed
        
        Args:
            chat_guid: The chat GUID (preferred - use this when available)
            message: The message text
            address: The recipient address/phone number (fallback if no chat_guid)
            attachments: Optional attachments
        """
        url = f"{self.base_url}/api/v1/message/text"
        
        # Build payloads in order of preference (correct format first)
        payloads_to_try = []
        
        # PREFERRED: Use chatGuid with "text" field (correct format per BlueBubbles docs)
        if chat_guid:
            payload = {
                "chatGuid": chat_guid,
                "text": message,
                "method": "private-api",
            }
            if attachments:
                payload["attachments"] = attachments
            payloads_to_try.append(payload)
            
            # Fallback: Try "message" field instead of "text" (some API versions)
            payload_alt = {
                "chatGuid": chat_guid,
                "message": message,
                "method": "private-api",
            }
            if attachments:
                payload_alt["attachments"] = attachments
            payloads_to_try.append(payload_alt)
        
        # FALLBACK: If no chat_guid, try with address (less reliable)
        if address and not chat_guid:
            payloads_to_try.append({
                "address": address,
                "text": message,
                "method": "private-api",
            })
            payloads_to_try.append({
                "address": address,
                "message": message,
                "method": "private-api",
            })
        
        if not payloads_to_try:
            raise ValueError("Either chat_guid or address must be provided")
        
        logger.debug(f"Sending message to BlueBubbles: {url} with chat_guid={chat_guid}")
        
        last_error = None
        for i, payload in enumerate(payloads_to_try):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        url,
                        json=payload,
                        headers=self._get_headers(),
                        params=self._get_params()
                    )
                    
                    if response.status_code == 200:
                        logger.debug(f"Successfully sent message using format {i+1}/{len(payloads_to_try)}")
                        return response.json()
                    elif response.status_code == 400:
                        # Bad request - try next format (but log at debug level to reduce noise)
                        last_error = f"400 Bad Request: {response.text[:200]}"
                        logger.debug(f"Format {i+1} failed (400), trying next format...")
                        continue
                    else:
                        response.raise_for_status()
            except httpx.HTTPStatusError as e:
                if e.response.status_code in (400, 404):
                    last_error = f"{e.response.status_code}: {e.response.text[:200]}"
                    logger.debug(f"Format {i+1} failed ({e.response.status_code}), trying next...")
                    continue
                else:
                    logger.error(f"BlueBubbles HTTP error: {e.response.status_code} - {e.response.text}")
                    raise
            except httpx.RequestError as e:
                logger.error(f"BlueBubbles request error: {e}")
                raise
        
        # If all payload formats failed
        raise ValueError(f"Could not send message - all payload formats failed. Last error: {last_error}")
    
    async def send_message_direct(
        self,
        recipient: str,
        message: str,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send a message directly to a phone number (without chat GUID)"""
        # Try constructing chat GUID from phone number (iMessage format)
        # Common patterns: "iMessage;+;<phone>", "SMS;+;<phone>", etc.
        phone_clean = recipient.replace("+", "").replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        
        chat_guid_patterns = [
            f"iMessage;+;chat{phone_clean}",  # Group chat pattern
            f"iMessage;+;+{phone_clean}",  # Direct message pattern
            f"SMS;+;+{phone_clean}",  # SMS pattern
            f"iMessage;-;+{phone_clean}",  # Alternative pattern
        ]
        
        # Try each constructed chat GUID
        for chat_guid in chat_guid_patterns:
            try:
                result = await self.send_message(
                    chat_guid=chat_guid,
                    message=message,
                    attachments=attachments
                )
                logger.info(f"Successfully sent message using constructed chat GUID: {chat_guid}")
                return result
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    # Chat doesn't exist with this GUID, try next pattern
                    continue
                else:
                    # Other error, log and continue
                    logger.warning(f"Error with chat GUID {chat_guid}: {e.response.status_code}")
                    continue
            except Exception as e:
                logger.warning(f"Exception with chat GUID {chat_guid}: {e}")
                continue
        
        # If all constructed GUIDs failed, try alternative endpoints to find/create chat
        # Try GET /api/v1/chat with query parameters (use proper URL encoding)
        import urllib.parse
        password_encoded = urllib.parse.quote(self.password, safe='')
        recipient_encoded = urllib.parse.quote(recipient, safe='')
        
        alternative_endpoints = [
            f"{self.base_url}/api/v1/chat?password={password_encoded}&address={recipient_encoded}",
            f"{self.base_url}/api/v1/chat?password={password_encoded}&phoneNumber={recipient_encoded}",
            f"{self.base_url}/api/v1/chat?password={password_encoded}&recipient={recipient_encoded}",
        ]
        
        for url in alternative_endpoints:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, headers=self._get_headers())
                    if response.status_code == 200:
                        chat_data = response.json()
                        # Extract chat GUID from response
                        if isinstance(chat_data, dict):
                            chat_guid = chat_data.get("data", {}).get("guid") or chat_data.get("guid")
                            if chat_guid:
                                logger.info(f"Found chat GUID via alternative endpoint: {chat_guid}")
                                return await self.send_message(
                                    chat_guid=chat_guid,
                                    message=message,
                                    attachments=attachments
                                )
            except Exception as e:
                logger.debug(f"Alternative endpoint failed: {e}")
                continue
        
        # If all methods failed, raise error
        raise ValueError(f"Could not find or create chat for {recipient}. BlueBubbles requires a chatGuid to send messages. The chat must already exist in iMessage.")
    
    async def get_chats(self) -> List[Dict[str, Any]]:
        """Get list of chats using the proper BlueBubbles API endpoint"""
        # Use POST /api/v1/chat/query as documented in BlueBubbles API
        url = f"{self.base_url}/api/v1/chat/query"
        
        payload = {
            "limit": 1000,
            "offset": 0,
            "with": ["participants", "lastMessage"],
            "sort": "lastmessage"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    params=self._get_params()  # Password as query parameter
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Handle response format: {"status": 200, "message": "Success", "data": [...]}
                    if isinstance(result, dict) and "data" in result:
                        chats = result["data"]
                    elif isinstance(result, list):
                        chats = result
                    else:
                        chats = result
                    
                    return chats if isinstance(chats, list) else [chats]
                else:
                    response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"BlueBubbles get_chats HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"BlueBubbles get_chats request error: {e}")
            raise
    
    async def create_chat(self, recipient: str, message: str = None) -> Dict[str, Any]:
        """Create a new chat using the proper BlueBubbles API endpoint
        
        Args:
            recipient: The recipient address (phone number or email)
            message: Optional message to send when creating the chat
        """
        # Use POST /api/v1/chat/new as documented in BlueBubbles API
        # This requires Private API and can optionally send a message
        url = f"{self.base_url}/api/v1/chat/new"
        
        payload = {
            "addresses": [recipient],  # Array of participant addresses
        }
        
        if message:
            payload["message"] = message  # Optional message to send
        
        logger.debug(f"Creating new chat via BlueBubbles API: {url}")
        logger.debug(f"Recipient: {recipient}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    params=self._get_params()  # Password as query parameter
                )
                
                logger.debug(f"BlueBubbles create_chat response status: {response.status_code}")
                logger.debug(f"BlueBubbles create_chat response: {response.text[:200]}")
                
                if response.status_code == 200:
                    # The endpoint returns no body, but the chat is created
                    # We need to query for it to get the chat GUID
                    return {"success": True, "recipient": recipient}
                else:
                    response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"BlueBubbles create_chat HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"BlueBubbles create_chat request error: {e}")
            raise

