"""
Security utilities and rate limiting
"""

import asyncio
from functools import wraps
from datetime import datetime, timedelta
from typing import Dict, Set
from aiogram.types import Message, CallbackQuery

from utils.database import check_rate_limit
from config import ADMIN_USER, RATE_LIMIT_SECONDS, EMOJIS

# In-memory rate limiting for quick checks
_rate_limit_cache: Dict[int, datetime] = {}
_blocked_users: Set[int] = set()

def rate_limit(func):
    """Rate limiting decorator"""
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract user_id from different event types
        user_id = None
        
        for arg in args:
            if isinstance(arg, (Message, CallbackQuery)):
                user_id = arg.from_user.id
                break
        
        if user_id is None:
            # If we can't determine user_id, allow the request
            return await func(*args, **kwargs)
        
        # Check if user is blocked
        if user_id in _blocked_users:
            return
        
        # Quick in-memory check
        now = datetime.now()
        if user_id in _rate_limit_cache:
            time_diff = (now - _rate_limit_cache[user_id]).total_seconds()
            if time_diff < RATE_LIMIT_SECONDS:
                # Rate limited - send warning
                if isinstance(args[0], Message):
                    await args[0].answer(
                        f"{EMOJIS['warning']} Please wait {RATE_LIMIT_SECONDS - int(time_diff)} seconds before next action."
                    )
                elif isinstance(args[0], CallbackQuery):
                    await args[0].answer(
                        f"{EMOJIS['warning']} Rate limited! Please wait.",
                        show_alert=True
                    )
                return
        
        # Update rate limit cache
        _rate_limit_cache[user_id] = now
        
        # Database check for persistent rate limiting
        if not await check_rate_limit(user_id, RATE_LIMIT_SECONDS):
            return
        
        # Execute the original function
        return await func(*args, **kwargs)
    
    return wrapper

async def is_admin(user_id: int, username: str = None) -> bool:
    """Check if user is admin"""
    
    # Check by username
    if username and f"@{username}" == ADMIN_USER:
        return True
    
    # You can add user_id based admin check here
    # For now, we rely on username
    return False

def block_user(user_id: int):
    """Block a user from using the bot"""
    _blocked_users.add(user_id)

def unblock_user(user_id: int):
    """Unblock a user"""
    _blocked_users.discard(user_id)

def is_blocked(user_id: int) -> bool:
    """Check if user is blocked"""
    return user_id in _blocked_users

async def log_security_event(event_type: str, user_id: int, details: str = ""):
    """Log security events"""
    
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] SECURITY: {event_type} - User: {user_id} - {details}"
    
    # Write to security log file
    try:
        with open("security.log", "a") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"Error writing security log: {e}")

def validate_amount(amount_str: str) -> tuple[bool, float]:
    """Validate and parse amount string"""
    
    try:
        # Remove common formatting
        cleaned = amount_str.replace(',', '').replace('₹', '').strip()
        amount = float(cleaned)
        
        # Basic validation
        if amount <= 0:
            return False, 0
        
        if amount > 10000000:  # 1 crore limit
            return False, 0
        
        return True, amount
        
    except (ValueError, TypeError):
        return False, 0

def sanitize_text(text: str, max_length: int = 1000) -> str:
    """Sanitize user input text"""
    
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = text.strip()
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # Basic HTML escape for safety
    sanitized = sanitized.replace('<', '&lt;').replace('>', '&gt;')
    
    return sanitized

def generate_secure_id(length: int = 8) -> str:
    """Generate a secure random ID"""
    
    import secrets
    import string
    
    # Use uppercase letters and numbers
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

async def verify_deal_access(deal_id: str, user_id: int) -> bool:
    """Verify if user has access to a deal"""
    
    from utils.database import get_deal
    
    deal = await get_deal(deal_id)
    if not deal:
        return False
    
    # Creator always has access
    if deal['creator_id'] == user_id:
        return True
    
    # Add additional access logic here (e.g., participants, admin)
    return False

class SecurityMonitor:
    """Security monitoring class"""
    
    def __init__(self):
        self.suspicious_activity: Dict[int, int] = {}
        self.failed_attempts: Dict[int, int] = {}
    
    async def log_failed_attempt(self, user_id: int, attempt_type: str):
        """Log failed attempt"""
        
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = 0
        
        self.failed_attempts[user_id] += 1
        
        await log_security_event(
            "FAILED_ATTEMPT", 
            user_id, 
            f"Type: {attempt_type}, Count: {self.failed_attempts[user_id]}"
        )
        
        # Auto-block after too many failures
        if self.failed_attempts[user_id] >= 5:
            block_user(user_id)
            await log_security_event("AUTO_BLOCK", user_id, "Too many failed attempts")
    
    async def log_suspicious_activity(self, user_id: int, activity: str):
        """Log suspicious activity"""
        
        await log_security_event("SUSPICIOUS", user_id, activity)
        
        if user_id not in self.suspicious_activity:
            self.suspicious_activity[user_id] = 0
        
        self.suspicious_activity[user_id] += 1

# Global security monitor instance
security_monitor = SecurityMonitor()
