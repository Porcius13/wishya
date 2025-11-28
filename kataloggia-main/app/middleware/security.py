"""
Security Middleware
CSRF protection, input validation, etc.
"""
from functools import wraps
from flask import request, jsonify
import re
from urllib.parse import urlparse

# Try to import Flask-WTF
try:
    from flask_wtf.csrf import CSRFProtect, generate_csrf
    CSRF_AVAILABLE = True
except ImportError:
    CSRF_AVAILABLE = False
    print("[INFO] Flask-WTF yüklü değil, CSRF protection devre dışı")

class SecurityMiddleware:
    """Security middleware utilities"""
    
    @staticmethod
    def validate_url(url):
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def sanitize_input(text, max_length=1000):
        """Sanitize user input"""
        if not text:
            return ""
        
        # Remove dangerous characters
        text = text.strip()
        text = text[:max_length]
        
        # Remove script tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        return text
    
    @staticmethod
    def validate_product_data(data):
        """Validate product data"""
        errors = []
        
        if 'name' not in data or not data['name']:
            errors.append('Ürün adı gerekli')
        elif len(data['name']) > 500:
            errors.append('Ürün adı çok uzun (max 500 karakter)')
        
        if 'price' not in data or not data['price']:
            errors.append('Fiyat gerekli')
        
        if 'url' not in data or not data['url']:
            errors.append('URL gerekli')
        elif not SecurityMiddleware.validate_url(data['url']):
            errors.append('Geçersiz URL formatı')
        
        if 'brand' not in data or not data['brand']:
            errors.append('Marka gerekli')
        
        return errors

def require_csrf(f):
    """CSRF protection decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if CSRF_AVAILABLE and request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # CSRF token validation would go here
            # For now, just pass through
            pass
        return f(*args, **kwargs)
    return decorated_function

def validate_json(schema=None):
    """JSON validation decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Content-Type must be application/json'
                }), 400
            
            data = request.get_json()
            
            if schema:
                # Schema validation would go here
                # For now, just pass through
                pass
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

