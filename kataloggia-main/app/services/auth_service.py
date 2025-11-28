"""
Auth Service
Authentication business logic
"""
from app.models.user import User

class AuthService:
    """Authentication business logic"""
    
    def authenticate(self, username, password):
        """Kullanıcı doğrula"""
        print(f"[AUTH DEBUG] Authenticating user: {username}")
        user = User.get_by_username(username)
        print(f"[AUTH DEBUG] User found: {user is not None}")
        
        if user:
            print(f"[AUTH DEBUG] Checking password...")
            password_valid = user.check_password(password)
            print(f"[AUTH DEBUG] Password valid: {password_valid}")
            if password_valid:
                return user
            else:
                print(f"[AUTH DEBUG] Password check failed for user: {username}")
        else:
            print(f"[AUTH DEBUG] User not found: {username}")
        
        return None
    
    def register(self, username, email, password):
        """Yeni kullanıcı kaydet"""
        try:
            user = User.create(username, email, password)
            return user
        except Exception as e:
            print(f"Registration error: {e}")
            return None

