"""
Timezone Utility Functions
Handles conversion between UTC and Indian Standard Time (IST)
"""

from datetime import datetime, timedelta, timezone

# Indian Standard Time is UTC+5:30
IST_OFFSET = timedelta(hours=5, minutes=30)
IST = timezone(IST_OFFSET)


def utc_to_ist(utc_dt):
    """
    Convert a UTC datetime to IST
    
    Args:
        utc_dt: datetime object (naive or aware)
        
    Returns:
        datetime object in IST
    """
    if utc_dt is None:
        return None
    
    # If datetime is naive, assume it's UTC
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    
    # Convert to IST
    ist_dt = utc_dt.astimezone(IST)
    return ist_dt


def ist_now():
    """
    Get current time in IST
    
    Returns:
        datetime object in IST
    """
    return datetime.now(IST)


def format_ist_time(utc_dt, format_str='%I:%M %p'):
    """
    Convert UTC datetime to IST and format it
    
    Args:
        utc_dt: datetime object in UTC
        format_str: strftime format string (default: '12:30 PM')
        
    Returns:
        Formatted time string in IST
    """
    if utc_dt is None:
        return None
    
    ist_dt = utc_to_ist(utc_dt)
    return ist_dt.strftime(format_str)


def format_ist_datetime(utc_dt, format_str='%d %b %Y %I:%M %p'):
    """
    Convert UTC datetime to IST and format it with date
    
    Args:
        utc_dt: datetime object in UTC
        format_str: strftime format string (default: '14 Jan 2026 12:30 PM')
        
    Returns:
        Formatted datetime string in IST
    """
    if utc_dt is None:
        return None
    
    ist_dt = utc_to_ist(utc_dt)
    return ist_dt.strftime(format_str)
