"""
Cache Service
Redis cache implementation with fallback to in-memory cache
"""
import json
import hashlib
import os
from functools import wraps

# Try to import Redis, fallback to simple cache
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("[INFO] Redis yüklü değil, in-memory cache kullanılacak")

class CacheService:
    """Cache service with Redis support"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        
        if REDIS_AVAILABLE:
            try:
                redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                print("[INFO] Redis bağlantısı başarılı")
            except Exception as e:
                print(f"[WARNING] Redis bağlantısı başarısız: {e}")
                print("[INFO] In-memory cache kullanılacak")
                self.redis_client = None
    
    def _get_key(self, prefix, *args, **kwargs):
        """Cache key oluştur"""
        key_data = f"{prefix}:{args}:{kwargs}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key):
        """Cache'den değer al"""
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                print(f"[ERROR] Redis get error: {e}")
        
        # Fallback to memory cache
        return self.memory_cache.get(key)
    
    def set(self, key, value, expiration=3600):
        """Cache'e değer kaydet"""
        try:
            serialized = json.dumps(value)
            
            if self.redis_client:
                try:
                    self.redis_client.setex(key, expiration, serialized)
                    return True
                except Exception as e:
                    print(f"[ERROR] Redis set error: {e}")
            
            # Fallback to memory cache
            self.memory_cache[key] = value
            return True
        except Exception as e:
            print(f"[ERROR] Cache set error: {e}")
            return False
    
    def delete(self, key):
        """Cache'den değer sil"""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                print(f"[ERROR] Redis delete error: {e}")
        
        # Fallback to memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
    
    def clear(self, pattern=None):
        """Cache'i temizle"""
        if self.redis_client and pattern:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                print(f"[ERROR] Redis clear error: {e}")
        
        # Clear memory cache
        if pattern:
            # Simple pattern matching for memory cache
            keys_to_delete = [k for k in self.memory_cache.keys() if pattern.replace('*', '') in k]
            for key in keys_to_delete:
                del self.memory_cache[key]
        else:
            self.memory_cache.clear()
    
    def exists(self, key):
        """Key var mı kontrol et"""
        if self.redis_client:
            try:
                return self.redis_client.exists(key) > 0
            except Exception as e:
                print(f"[ERROR] Redis exists error: {e}")
        
        return key in self.memory_cache

# Global cache instance
cache_service = CacheService()

def cached(expiration=3600, key_prefix='cache'):
    """Cache decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_service._get_key(
                f"{key_prefix}:{func.__name__}",
                *args,
                **kwargs
            )
            
            # Try to get from cache
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_service.set(cache_key, result, expiration)
            
            return result
        return wrapper
    return decorator

