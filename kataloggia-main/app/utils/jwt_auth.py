"""
JWT Authentication Utilities
JWT token generation and validation
"""
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app

# Try to import PyJWT
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("[INFO] PyJWT yüklü değil, JWT authentication devre dışı")

class JWTAuth:
    """JWT authentication utilities"""
    
    @staticmethod
    def generate_token(user_id, username, email, expiration_hours=24):
        """Generate JWT token"""
        if not JWT_AVAILABLE:
            return None
        
        secret_key = os.environ.get('JWT_SECRET_KEY', os.environ.get('SECRET_KEY', 'jwt-secret-key'))
        
        payload = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=expiration_hours),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token"""
        if not JWT_AVAILABLE:
            return None
        
        try:
            secret_key = os.environ.get('JWT_SECRET_KEY', os.environ.get('SECRET_KEY', 'jwt-secret-key'))
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def get_token_from_request():
        """Get JWT token from request"""
        # Check Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                return parts[1]
        
        # Check token in query string
        return request.args.get('token')

def jwt_required(f):
    """JWT authentication decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not JWT_AVAILABLE:
            # Fallback to Flask-Login
            from flask_login import login_required
            return login_required(f)(*args, **kwargs)
        
        token = JWTAuth.get_token_from_request()
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token gerekli'
            }), 401
        
        payload = JWTAuth.verify_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Geçersiz veya süresi dolmuş token'
            }), 401
        
        # Store user info in request context
        request.current_user_id = payload['user_id']
        request.current_username = payload['username']
        request.current_email = payload['email']
        
        return f(*args, **kwargs)
    return decorated_function

