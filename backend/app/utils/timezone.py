"""
Timezone detection utilities
"""
import logging
import phonenumbers
from phonenumbers import timezone as phonenumbers_timezone
from phonenumbers import NumberParseException

logger = logging.getLogger(__name__)


def detect_timezone_from_phone(phone_number: str) -> str:
    """Detect timezone from phone number using phonenumbers library
    
    Returns IANA timezone string (e.g., 'America/Los_Angeles')
    Raises exception if unable to detect timezone
    """
    if not phone_number:
        raise ValueError("Phone number is required for timezone detection")
    
    # Parse the phone number (try without region first, then with 'US' as fallback)
    parsed_number = None
    try:
        parsed_number = phonenumbers.parse(phone_number, None)
    except NumberParseException:
        # If parsing fails, try with 'US' as default region
        try:
            parsed_number = phonenumbers.parse(phone_number, 'US')
        except NumberParseException as e:
            raise ValueError(f"Could not parse phone number: {phone_number}") from e
    
    # Get timezones for this number
    timezones = phonenumbers_timezone.time_zones_for_number(parsed_number)
    
    if not timezones:
        raise ValueError(f"No timezone found for phone number: {phone_number}")
    
    # Return the first timezone (most common case)
    tz = timezones[0]
    # Map common timezone names to IANA format
    tz_mapping = {
        'US/Pacific': 'America/Los_Angeles',
        'US/Mountain': 'America/Denver',
        'US/Central': 'America/Chicago',
        'US/Eastern': 'America/New_York',
        'America/Phoenix': 'America/Phoenix',  # Already correct
    }
    result = tz_mapping.get(tz, tz)
    logger.debug(f"Detected timezone {result} for phone number {phone_number}")
    return result

