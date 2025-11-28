import sqlite3
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

def init_db():
    """Veritabanını başlat"""
    conn = sqlite3.connect('favit.db')
    cursor = conn.cursor()
    
    # Kullanıcılar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            profile_url TEXT UNIQUE
        )
    ''')
    
    # Ürünler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            price TEXT NOT NULL,
            image TEXT,
            brand TEXT NOT NULL,
            url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            old_price TEXT,
            current_price TEXT,
            discount_percentage TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Eksik kolonları ekle (eğer yoksa)
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN old_price TEXT')
    except:
        pass  # Kolon zaten varsa hata vermez
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN current_price TEXT')
    except:
        pass  # Kolon zaten varsa hata vermez
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN discount_percentage TEXT')
    except:
        pass  # Kolon zaten varsa hata vermez
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN images TEXT')
    except:
        pass  # Kolon zaten varsa hata vermez
    
    try:
        cursor.execute('ALTER TABLE products ADD COLUMN discount_info TEXT')
    except:
        pass  # Kolon zaten varsa hata vermez
    
    # Koleksiyonlar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collections (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            is_public BOOLEAN DEFAULT 1,
            share_url TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Koleksiyon ürünleri tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection_products (
            id TEXT PRIMARY KEY,
            collection_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (collection_id) REFERENCES collections (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Fiyat takip tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_tracking (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            current_price TEXT NOT NULL,
            original_price TEXT NOT NULL,
            price_change TEXT DEFAULT '0',
            is_active BOOLEAN DEFAULT 1,
            alert_price TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Fiyat geçmişi tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            price TEXT NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Beğeni ve yorum tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS likes (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            collection_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (collection_id) REFERENCES collections (id)
        )
    ''')
    
    # Takip tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS follows (
            id TEXT PRIMARY KEY,
            follower_id TEXT NOT NULL,
            following_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (follower_id) REFERENCES users (id),
            FOREIGN KEY (following_id) REFERENCES users (id)
        )
    ''')
    

    
    conn.commit()
    conn.close()

class User(UserMixin):
    def __init__(self, id, username, email, password_hash, created_at, profile_url):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at
        self.profile_url = profile_url
    
    @staticmethod
    def get_by_id(user_id):
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return User(*user_data)
        return None
    
    @staticmethod
    def get_by_username(username):
        """Kullanıcı adına göre kullanıcı getir"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return User(*user_data)
        return None
    
    @staticmethod
    def get_by_email(email):
        """Email'e göre kullanıcı getir"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return User(*user_data)
        return None
    
    @staticmethod
    def get_by_profile_url(profile_url):
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE profile_url = ?', (profile_url,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return User(*user_data)
        return None
    
    @staticmethod
    def create(username, email, password):
        """Yeni kullanıcı oluştur"""
        try:
            user_id = str(uuid.uuid4())
            profile_url = f"user_{user_id[:8]}"
            password_hash = generate_password_hash(password)
            
            conn = sqlite3.connect('favit.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (id, username, email, password_hash, profile_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, email, password_hash, profile_url))
            
            conn.commit()
            conn.close()
            
            return User(user_id, username, email, password_hash, datetime.now(), profile_url)
        except sqlite3.IntegrityError as e:
            print(f"[HATA] Veritabanı bütünlük hatası: {e}")
            raise Exception("Bu kullanıcı adı veya email zaten kullanılıyor")
        except Exception as e:
            print(f"[HATA] Kullanıcı oluşturma hatası: {e}")
            raise Exception(f"Kullanıcı oluşturulamadı: {str(e)}")
    
    def check_password(self, password):
        """Şifre kontrolü"""
        return check_password_hash(self.password_hash, password)
    
    def get_products(self):
        """Kullanıcının ürünlerini getir"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE user_id = ? ORDER BY created_at DESC', (self.id,))
        products = cursor.fetchall()
        conn.close()
        
        return [Product(*product) for product in products]
    
    def get_collections(self):
        """Kullanıcının koleksiyonlarını getir"""
        return Collection.get_user_collections(self.id)

class Product:
    def __init__(self, id, user_id, name, price, image, brand, url, created_at, old_price=None, current_price=None, discount_percentage=None, images=None, discount_info=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.price = price
        self.image = image
        self.brand = brand
        self.url = url
        self.created_at = created_at
        self.old_price = old_price
        self.current_price = current_price
        self.discount_percentage = discount_percentage
        self.discount_info = discount_info
        # images JSON array olarak saklanır, parse et
        if images:
            try:
                import json
                self.images = json.loads(images) if isinstance(images, str) else images
            except:
                self.images = [image] if image else []
        else:
            # Eğer images yoksa, mevcut image'i kullan (backward compatibility)
            self.images = [image] if image else []
    
    @staticmethod
    def create(user_id, name, price, image, brand, url, old_price=None, current_price=None, discount_percentage=None, images=None, discount_info=None):
        """Yeni ürün oluştur"""
        product_id = str(uuid.uuid4())
        
        # images'i JSON string'e çevir
        import json
        if images:
            images_json = json.dumps(images) if isinstance(images, list) else images
        else:
            # Eğer images verilmemişse, image'i kullan
            images_json = json.dumps([image]) if image else None
        
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO products (id, user_id, name, price, image, brand, url, old_price, current_price, discount_percentage, images, discount_info, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product_id, user_id, name, price, image, brand, url, old_price, current_price, discount_percentage, images_json, discount_info, datetime.now()))
        
        conn.commit()
        conn.close()
        
        return Product(product_id, user_id, name, price, image, brand, url, datetime.now(), old_price, current_price, discount_percentage, images_json, discount_info)
    
    @staticmethod
    def get_by_id(product_id):
        """ID ile ürün getir"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product_data = cursor.fetchone()
        conn.close()
        
        if product_data:
            return Product(*product_data)
        return None
    
    @staticmethod
    def update(product_id, user_id, **kwargs):
        """Ürün güncelle"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        
        # Güncellenecek alanları hazırla
        updates = []
        values = []
        
        allowed_fields = ['name', 'price', 'image', 'brand', 'url', 'old_price', 'current_price', 'discount_percentage', 'images', 'discount_info']
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                # images field'ı için JSON string'e çevir
                if field == 'images' and isinstance(value, list):
                    import json
                    value = json.dumps(value)
                updates.append(f"{field} = ?")
                values.append(value)
        
        if not updates:
            conn.close()
            return None
        
        values.append(product_id)
        values.append(user_id)
        
        query = f"UPDATE products SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        
        return Product.get_by_id(product_id)
    
    @staticmethod
    def delete(product_id, user_id):
        """Ürün sil - Transaction safe"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        try:
            # Önce ürünün kullanıcıya ait olduğunu kontrol et
            cursor.execute('SELECT id FROM products WHERE id = ? AND user_id = ?', (product_id, user_id))
            if not cursor.fetchone():
                return False  # Ürün bulunamadı veya kullanıcıya ait değil
            
            # Koleksiyonlardan da çıkar
            cursor.execute('DELETE FROM collection_products WHERE product_id = ?', (product_id,))
            
            # Fiyat takibini sil
            cursor.execute('DELETE FROM price_tracking WHERE product_id = ?', (product_id,))
            
            # Fiyat geçmişini sil
            cursor.execute('DELETE FROM price_history WHERE product_id = ?', (product_id,))
            
            # Ürünü sil
            cursor.execute('DELETE FROM products WHERE id = ? AND user_id = ?', (product_id, user_id))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[HATA] Ürün silme hatası: {e}")
            return False
        finally:
            conn.close()

class Collection:
    def __init__(self, id, user_id, name, description, type, is_public, share_url, created_at):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.type = type
        self.is_public = is_public
        self.share_url = share_url
        self.created_at = created_at
    
    @staticmethod
    def create(user_id, name, description, type, is_public=True):
        """Yeni koleksiyon oluştur"""
        collection_id = str(uuid.uuid4())
        share_url = f"collection_{collection_id[:8]}"
        
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO collections (id, user_id, name, description, type, is_public, share_url, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (collection_id, user_id, name, description, type, is_public, share_url, datetime.now()))
        
        conn.commit()
        conn.close()
        
        return Collection(collection_id, user_id, name, description, type, is_public, share_url, datetime.now())
    
    @staticmethod
    def get_by_id(collection_id):
        """ID ile koleksiyon getir"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM collections WHERE id = ?', (collection_id,))
        collection_data = cursor.fetchone()
        conn.close()
        
        if collection_data:
            return Collection(*collection_data)
        return None
    
    @staticmethod
    def get_by_share_url(share_url):
        """Share URL ile koleksiyon getir"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM collections WHERE share_url = ?', (share_url,))
        collection_data = cursor.fetchone()
        conn.close()
        
        if collection_data:
            return Collection(*collection_data)
        return None
    
    @staticmethod
    def get_user_collections(user_id):
        """Kullanıcının koleksiyonlarını getir"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM collections WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        collections = cursor.fetchall()
        conn.close()
        
        return [Collection(*collection) for collection in collections]
    

    
    def get_products(self):
        """Koleksiyondaki ürünleri getir"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.* FROM products p
            JOIN collection_products cp ON p.id = cp.product_id
            WHERE cp.collection_id = ?
            ORDER BY cp.added_at DESC
        ''', (self.id,))
        products = cursor.fetchall()
        conn.close()
        
        return [Product(*product) for product in products]
    
    def add_product(self, product_id):
        """Koleksiyona ürün ekle - Race condition safe"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        
        try:
            # Ürünün zaten koleksiyonda olup olmadığını kontrol et
            cursor.execute('SELECT id FROM collection_products WHERE collection_id = ? AND product_id = ?', (self.id, product_id))
            if cursor.fetchone():
                return False
            
            # Ürünün kullanıcıya ait olduğunu kontrol et (güvenlik)
            cursor.execute('SELECT id FROM products WHERE id = ? AND user_id = ?', (product_id, self.user_id))
            if not cursor.fetchone():
                return False  # Ürün kullanıcıya ait değil
            
            cp_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO collection_products (id, collection_id, product_id)
                VALUES (?, ?, ?)
            ''', (cp_id, self.id, product_id))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Duplicate entry (race condition durumunda)
            conn.rollback()
            return False
        except Exception as e:
            conn.rollback()
            print(f"[HATA] Koleksiyona ürün ekleme hatası: {e}")
            return False
        finally:
            conn.close()
    
    def remove_product(self, product_id):
        """Koleksiyondan ürün çıkar"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM collection_products WHERE collection_id = ? AND product_id = ?', (self.id, product_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"[HATA] Koleksiyondan ürün çıkarma hatası: {e}")
            raise
        finally:
            conn.close()
    
    def delete(self):
        """Koleksiyonu sil - Transaction safe"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        try:
            # Önce koleksiyon ürünlerini sil
            cursor.execute('DELETE FROM collection_products WHERE collection_id = ?', (self.id,))
            # Sonra koleksiyonu sil
            cursor.execute('DELETE FROM collections WHERE id = ?', (self.id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"[HATA] Koleksiyon silme hatası: {e}")
            raise
        finally:
            conn.close()
    


class PriceTracking:
    def __init__(self, id, product_id, user_id, current_price, original_price, price_change, is_active, alert_price, created_at, last_checked):
        self.id = id
        self.product_id = product_id
        self.user_id = user_id
        self.current_price = current_price
        self.original_price = original_price
        self.price_change = price_change
        self.is_active = is_active
        self.alert_price = alert_price
        self.created_at = created_at
        self.last_checked = last_checked
    
    @staticmethod
    def create(user_id, product_id, current_price, original_price=None, alert_price=None):
        """Fiyat takibi oluştur"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        
        tracking_id = str(uuid.uuid4())
        original_price = original_price or current_price
        
        cursor.execute('''
            INSERT INTO price_tracking (id, user_id, product_id, current_price, original_price, alert_price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (tracking_id, user_id, product_id, current_price, original_price, alert_price))
        
        # Fiyat geçmişine ekle
        history_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO price_history (id, product_id, price)
            VALUES (?, ?, ?)
        ''', (history_id, product_id, current_price))
        
        conn.commit()
        conn.close()
        
        return tracking_id
    
    @staticmethod
    def get_by_product_and_user(product_id, user_id):
        """Belirli bir ürün için kullanıcının takip kaydını getir"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, product_id, user_id, current_price, price_change, 
                   original_price, is_active, alert_price, created_at, last_checked
            FROM price_tracking 
            WHERE product_id = ? AND user_id = ? AND is_active = 1
        ''', (product_id, user_id))
        tracking_data = cursor.fetchone()
        conn.close()
        
        return tracking_data
    
    @staticmethod
    def remove_tracking(tracking_id):
        """Fiyat takibini kaldır (pasif hale getir)"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE price_tracking 
            SET is_active = 0 
            WHERE id = ?
        ''', (tracking_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    @staticmethod
    def get_user_tracking(user_id):
        """Kullanıcının fiyat takiplerini getir"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT pt.id, pt.product_id, pt.user_id, pt.current_price, pt.price_change, 
                   pt.original_price, pt.is_active, pt.alert_price, pt.created_at, pt.last_checked,
                   p.name, p.brand, p.image 
            FROM price_tracking pt
            JOIN products p ON pt.product_id = p.id
            WHERE pt.user_id = ? AND pt.is_active = 1
            ORDER BY pt.created_at DESC
        ''', (user_id,))
        tracking_data = cursor.fetchall()
        conn.close()
        
        return tracking_data
    
    @staticmethod
    def update_price(tracking_id, new_price):
        """Fiyat güncelle"""
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        
        # Mevcut fiyatı al
        cursor.execute('SELECT current_price, original_price FROM price_tracking WHERE id = ?', (tracking_id,))
        current_data = cursor.fetchone()
        
        if current_data:
            current_price = current_data[0]
            original_price = current_data[1]
            
            # Fiyat değişimini hesapla
            try:
                current_num = float(str(current_price).replace('₺', '').replace('TL', '').replace(',', '').strip())
                new_num = float(str(new_price).replace('₺', '').replace('TL', '').replace(',', '').strip())
                price_change = new_num - current_num
            except:
                price_change = 0
            
            # Fiyat takibini güncelle
            cursor.execute('''
                UPDATE price_tracking 
                SET current_price = ?, price_change = ?, last_checked = ?
                WHERE id = ?
            ''', (new_price, str(price_change), datetime.now(), tracking_id))
            
            # Fiyat geçmişine ekle
            history_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO price_history (id, product_id, price)
                VALUES (?, ?, ?)
            ''', (history_id, tracking_id, new_price))
            
            conn.commit()
            conn.close()
            return True
        
        conn.close()
        return False
    


 