"""
Validators for Activity Tracker Calendar
Provides validation functions for user inputs
"""

import re
from datetime import datetime

def validate_date_format(date_str):
    """Validate date string format (YYYY-MM-DD)"""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_duration(duration):
    """Validate activity duration (minutes)"""
    try:
        duration = int(duration)
        return duration > 0
    except (ValueError, TypeError):
        return False

def validate_color_hex(color):
    """Validate hex color code"""
    pattern = r'^#(?:[0-9a-fA-F]{3}){1,2}$'
    return bool(re.match(pattern, color))

def sanitize_input(text):
    """Sanitize user input text"""
    if not text:
        return ""
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>]', '', text)
    return text.strip()