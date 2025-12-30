# Security Review - Pre-Push Checklist

## Issues Found

### 🔴 CRITICAL ISSUES

1. **Bare Except Clauses (Code Quality & Error Handling)**
   - **Location**: `backend/app/integrations/calendar/google_calendar/service.py` lines 229, 241
   - **Issue**: Bare `except:` clauses can hide critical errors and make debugging difficult
   - **Risk**: Medium - Could hide security-relevant errors
   - **Fix**: Use specific exception types (`except ValueError:`, `except Exception as e:`)

2. **Direct Access to Private Attribute**
   - **Location**: `backend/app/services/agent/handlers/scheduling_handler.py` line 379
   - **Issue**: Accessing `calendar_service._credentials` directly (private attribute)
   - **Risk**: Low-Medium - Breaks encapsulation, could break if implementation changes
   - **Fix**: Add a public method `get_credentials()` or pass credentials as parameter

### ⚠️ MEDIUM PRIORITY ISSUES

3. **Webhook Authentication Missing**
   - **Location**: `backend/app/api/v1/webhooks/bluebubbles.py`
   - **Issue**: No authentication/authorization on webhook endpoint - anyone can POST to it
   - **Risk**: Medium-High - Could allow unauthorized message injection
   - **Fix**: Add API key authentication, IP whitelist, or signature verification

4. **Event ID Validation**
   - **Location**: `backend/app/integrations/calendar/google_calendar/service.py` - `update_event`, `get_event_meet_link`
   - **Issue**: Event IDs are used directly without validating they belong to the user
   - **Risk**: Low (mitigated by using user's own credentials) - Google API should enforce this, but worth noting
   - **Status**: Acceptable - Google Calendar API enforces user isolation via credentials

5. **Input Validation on Search Title**
   - **Location**: `backend/app/integrations/calendar/google_calendar/service.py` - `get_events` line 196
   - **Issue**: `search_title` passed directly to Google API query parameter
   - **Risk**: Low - Google API should sanitize, but input validation is good practice
   - **Status**: Acceptable - Google Calendar API handles query sanitization

### ✅ GOOD SECURITY PRACTICES FOUND

1. **SQL Injection Protection**: ✅ Using SQLAlchemy ORM with parameterized queries
2. **User Isolation**: ✅ All queries filter by `user_id` to ensure data isolation
3. **Authentication**: ✅ JWT token validation via `get_current_user_id` dependency
4. **Password Hashing**: ✅ Using bcrypt with SHA-256 preprocessing
5. **UUID Usage**: ✅ Using UUIDs for IDs prevents enumeration attacks
6. **Error Handling**: ✅ Most exceptions are caught and logged appropriately
7. **Credential Storage**: ✅ Credentials stored in database (should be encrypted at rest in production)

## Recommended Fixes

### Fix 1: Replace Bare Except Clauses

```python
# backend/app/integrations/calendar/google_calendar/service.py

# Line 229 - Change from:
except:
    continue

# To:
except (ValueError, TypeError) as e:
    logger.warning(f"Error parsing start_time: {e}")
    continue

# Line 241 - Change from:
except:
    end_time = start_time

# To:
except (ValueError, TypeError) as e:
    logger.warning(f"Error parsing end_time: {e}")
    end_time = start_time
```

### Fix 2: Add Public Method for Credentials

```python
# backend/app/integrations/calendar/google_calendar/service.py

class GoogleCalendarService(BaseCalendarIntegration):
    # ... existing code ...
    
    def get_credentials(self) -> Optional[Dict]:
        """Get credentials (for internal use by handlers)"""
        return self._credentials

# Then in scheduling_handler.py line 379, change:
creds = GoogleOAuth.get_credentials_from_dict(calendar_service._credentials)

# To:
creds = GoogleOAuth.get_credentials_from_dict(calendar_service.get_credentials())
```

### Fix 3: Add Webhook Authentication (RECOMMENDED)

```python
# backend/app/api/v1/webhooks/bluebubbles.py

from app.core.config import settings
from fastapi import HTTPException, Header

@router.post("")
async def bluebubbles_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_webhook_secret: Optional[str] = Header(None)  # Add webhook secret header
):
    """Handle incoming BlueBubbles webhook"""
    # Verify webhook secret if configured
    if settings.WEBHOOK_SECRET:
        if x_webhook_secret != settings.WEBHOOK_SECRET:
            logger.warning(f"Unauthorized webhook attempt from {request.client.host}")
            raise HTTPException(status_code=401, detail="Unauthorized")
    
    # ... rest of the code
```

Add to `backend/app/core/config.py`:
```python
WEBHOOK_SECRET: Optional[str] = None  # Set in environment variables
```

## Notes

- The code uses proper authentication for API endpoints via JWT tokens
- User data is properly isolated by user_id in all queries
- Google Calendar API enforces user isolation via OAuth credentials
- Database connections use SSL (configured in database.py)
- Consider adding rate limiting for webhook endpoints
- Consider adding request logging for security auditing
- Ensure credentials are encrypted at rest in production (check database encryption settings)

## Pre-Push Checklist

- [ ] Fix bare except clauses
- [ ] Add public method for credentials access (or refactor to avoid direct access)
- [ ] Consider adding webhook authentication (if BlueBubbles supports it)
- [ ] Review error messages to ensure no sensitive data leakage
- [ ] Ensure all environment variables are documented and not hardcoded
- [ ] Verify database encryption at rest is enabled in production
- [ ] Test that users cannot access other users' data
- [ ] Review logging to ensure no sensitive credentials are logged

