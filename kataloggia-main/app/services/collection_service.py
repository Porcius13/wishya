"""
Collection Service
Collection business logic
"""
from app.models.collection import Collection

class CollectionService:
    """Collection business logic"""
    
    def get_user_collections(self, user_id):
        """Kullanıcının koleksiyonlarını getir"""
        return Collection.get_user_collections(user_id)
    
    def get_collection(self, collection_id, user_id):
        """Tek bir koleksiyonu getir"""
        collection = Collection.get_by_id(collection_id)
        if collection and collection.user_id == user_id:
            return collection
        return None
    
    def create_collection(self, user_id, name, description=None, type='custom', is_public=True):
        """Yeni koleksiyon oluştur"""
        return Collection.create(
            user_id=user_id,
            name=name,
            description=description,
            type=type,
            is_public=is_public
        )
    
    def add_product(self, collection_id, product_id, user_id):
        """Koleksiyona ürün ekle"""
        collection = self.get_collection(collection_id, user_id)
        if not collection:
            return False
        
        return collection.add_product(product_id)

