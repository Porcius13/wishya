"""
Product Service
Business logic for products with caching
"""
from app.models.product import Product
from app.services.cache_service import cache_service

class ProductService:
    """Product business logic with caching"""
    
    def _get_cache_key(self, user_id, product_id=None):
        """Cache key oluştur"""
        if product_id:
            return f"product:{product_id}:{user_id}"
        return f"products:user:{user_id}"
    
    def get_user_products(self, user_id, use_cache=True):
        """Kullanıcının ürünlerini getir (cached)"""
        cache_key = self._get_cache_key(user_id)
        
        if use_cache:
            cached_products = cache_service.get(cache_key)
            if cached_products is not None:
                return cached_products
        
        products = Product.get_by_user_id(user_id)
        
        # Cache products
        if use_cache:
            cache_service.set(cache_key, products, expiration=300)  # 5 minutes
        
        return products
    
    def get_product(self, product_id, user_id, use_cache=True):
        """Tek bir ürünü getir (cached)"""
        cache_key = self._get_cache_key(user_id, product_id)
        
        if use_cache:
            cached_product = cache_service.get(cache_key)
            if cached_product is not None:
                return cached_product
        
        product = Product.get_by_id(product_id)
        if product and product.user_id == user_id:
            # Cache product
            if use_cache:
                cache_service.set(cache_key, product, expiration=600)  # 10 minutes
            return product
        return None
    
    def create_product(self, user_id, name, price, url, brand, image=None, 
                      old_price=None, current_price=None, discount_percentage=None, images=None):
        """Yeni ürün oluştur"""
        product = Product.create(
            user_id=user_id,
            name=name,
            price=price,
            image=image,
            brand=brand,
            url=url,
            old_price=old_price,
            current_price=current_price,
            discount_percentage=discount_percentage,
            images=images
        )
        
        # Invalidate cache
        cache_key = self._get_cache_key(user_id)
        cache_service.delete(cache_key)
        
        return product
    
    def update_product(self, product_id, user_id, **kwargs):
        """Ürün güncelle"""
        product = self.get_product(product_id, user_id, use_cache=False)
        if not product:
            return None
        
        # Update logic (mevcut model yapısına göre)
        # Şimdilik basit bir implementasyon
        
        # Invalidate cache
        cache_key = self._get_cache_key(user_id, product_id)
        cache_service.delete(cache_key)
        cache_service.delete(self._get_cache_key(user_id))
        
        return product
    
    def delete_product(self, product_id, user_id):
        """Ürün sil"""
        product = self.get_product(product_id, user_id, use_cache=False)
        if not product:
            return False
        
        Product.delete(product_id, user_id)
        
        # Invalidate cache
        cache_key = self._get_cache_key(user_id, product_id)
        cache_service.delete(cache_key)
        cache_service.delete(self._get_cache_key(user_id))
        
        return True
