"""
User Model
"""
import sys
import os

# Mevcut models.py'yi import etmek için path ekle
# run.py'den çalıştırıldığında: kataloggia-main/kataloggia-main/models.py
# app/models/user.py -> ../../models.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# app/models -> app -> kataloggia-main/kataloggia-main
project_root = os.path.join(current_dir, '../..')
models_path = os.path.join(project_root, 'models.py')

# Alternatif: kataloggia-main/models.py (bir üst dizin)
alt_project_root = os.path.join(project_root, '..')
alt_models_path = os.path.join(alt_project_root, 'models.py')

if os.path.exists(models_path):
    sys.path.insert(0, project_root)
    from models import User as BaseUser
    User = BaseUser
elif os.path.exists(alt_models_path):
    sys.path.insert(0, alt_project_root)
    from models import User as BaseUser
    User = BaseUser
else:
    # Fallback: Eğer models.py bulunamazsa, basit bir User sınıfı oluştur
    from flask_login import UserMixin
    class User(UserMixin):
        def __init__(self, id, username, email, password_hash=None):
            self.id = id
            self.username = username
            self.email = email
            self.password_hash = password_hash
        
        @staticmethod
        def get_by_id(user_id):
            # Bu fonksiyon models.py'de tanımlı olmalı
            return None

