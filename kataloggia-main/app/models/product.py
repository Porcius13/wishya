"""
Product Model
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
from models import Product as BaseProduct

# Mevcut Product modelini kullan
Product = BaseProduct

# to_dict method ekle
def to_dict(self):
    """Product'ı dictionary'ye çevir"""
    return {
        'id': self.id,
        'user_id': self.user_id,
        'name': self.name,
        'price': self.price,
        'image': self.image,
        'brand': self.brand,
        'url': self.url,
        'created_at': str(self.created_at),
        'old_price': self.old_price,
        'current_price': self.current_price,
        'discount_percentage': self.discount_percentage
    }

# Method'u ekle
BaseProduct.to_dict = to_dict

# get_by_user_id method ekle
@classmethod
def get_by_user_id(cls, user_id):
    """Kullanıcı ID'sine göre ürünleri getir"""
    import sqlite3
    from app.utils.db_path import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    products = cursor.fetchall()
    conn.close()
    
    return [cls(*product) for product in products]

BaseProduct.get_by_user_id = get_by_user_id

Product = BaseProduct

