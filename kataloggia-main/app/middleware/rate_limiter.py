"""
Rate Limiting Middleware
API rate limiting with Flask-Limiter
"""
from functools import wraps
from flask import request, jsonify
import time
from collections import defaultdict

# Try to import Flask-Limiter
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    LIMITER_AVAILABLE = True
except ImportError:
    LIMITER_AVAILABLE = False
    print("[INFO] Flask-Limiter yüklü değil, basit rate limiting kullanılacak")

class SimpleRateLimiter:
    """Simple in-memory rate limiter (fallback)"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.default_limit = 100  # requests per hour
        self.default_window = 3600  # 1 hour in seconds
    
    def is_allowed(self, key, limit=None, window=None):
        """Check if request is allowed"""
        limit = limit or self.default_limit
        window = window or self.default_window
        
        now = time.time()
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window
        ]
        
        # Check limit
        if len(self.requests[key]) >= limit:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True
    
    def get_remaining(self, key, limit=None, window=None):
        """Get remaining requests"""
        limit = limit or self.default_limit
        window = window or self.default_window
        
        now = time.time()
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window
        ]
        
        return max(0, limit - len(self.requests[key]))

# Global rate limiter instance
simple_limiter = SimpleRateLimiter()

def rate_limit(limit="100 per hour", key_func=None):
    """Rate limit decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if LIMITER_AVAILABLE:
                # Use Flask-Limiter if available
                return f(*args, **kwargs)
            else:
                # Use simple rate limiter
                if key_func:
                    key = key_func()
                else:
                    key = get_remote_address()
                
                # Parse limit (e.g., "100 per hour")
                parts = limit.split()
                limit_num = int(parts[0])
                window_map = {
                    'second': 1,
                    'minute': 60,
                    'hour': 3600,
                    'day': 86400
                }
                window = window_map.get(parts[-1], 3600)
                
                if not simple_limiter.is_allowed(key, limit_num, window):
                    remaining = simple_limiter.get_remaining(key, limit_num, window)
                    return jsonify({
                        'success': False,
                        'error': 'Rate limit exceeded',
                        'limit': limit_num,
                        'window': window,
                        'remaining': remaining
                    }), 429
                
                return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_remote_address():
    """Get client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr or 'unknown'

