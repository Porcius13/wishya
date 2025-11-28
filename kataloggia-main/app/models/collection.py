"""
Collection Model
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
from models import Collection as BaseCollection

# Mevcut Collection modelini kullan
Collection = BaseCollection

# to_dict method ekle
def to_dict(self):
    """Collection'ı dictionary'ye çevir"""
    return {
        'id': self.id,
        'user_id': self.user_id,
        'name': self.name,
        'description': self.description,
        'type': self.type,
        'is_public': self.is_public,
        'share_url': self.share_url,
        'created_at': str(self.created_at)
    }

BaseCollection.to_dict = to_dict
Collection = BaseCollection

