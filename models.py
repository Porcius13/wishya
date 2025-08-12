import sqlite3
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import os

# PostgreSQL için opsiyonel import
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("[UYARI] psycopg2 modülü bulunamadı, PostgreSQL desteği devre dışı")

def get_db_connection():
    """Database bağlantısı - Render PostgreSQL veya local SQLite"""
    # Check if we're in Render environment and have DATABASE_URL
    if os.environ.get('RENDER') and PSYCOPG2_AVAILABLE and os.environ.get('DATABASE_URL'):
        # Render PostgreSQL
        print(f"[DEBUG] Render ortamında PostgreSQL kullanılıyor")
        database_url = os.environ.get('DATABASE_URL')
        print(f"[DEBUG] DATABASE_URL: {database_url[:20]}..." if database_url else "[DEBUG] DATABASE_URL yok")
        
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
            print(f"[DEBUG] URL güncellendi: {database_url[:20]}...")
        
        try:
            print(f"[DEBUG] PostgreSQL bağlantısı kuruluyor...")
            conn = psycopg2.connect(database_url)
            print(f"[DEBUG] PostgreSQL bağlantısı başarılı")
            return conn
        except Exception as e:
            print(f"[HATA] PostgreSQL bağlantı hatası: {e}")
            print(f"[HATA] SQLite fallback kullanılıyor")
            # Fallback to SQLite
            return sqlite3.connect('wishya.db')
    else:
        # Local SQLite veya PostgreSQL mevcut değilse
        print(f"[DEBUG] Local ortamda SQLite kullanılıyor")
        return sqlite3.connect('wishya.db')

def init_db():
    """Database tablolarını oluştur"""
    try:
        print(f"[DEBUG] init_db başladı, RENDER: {os.environ.get('RENDER')}")
        conn = get_db_connection()
        cursor = conn.cursor()
        print(f"[DEBUG] Database bağlantısı başarılı")
    except Exception as e:
        print(f"[HATA] Database bağlantı hatası: {e}")
        raise
    
    if os.environ.get('RENDER') and PSYCOPG2_AVAILABLE and os.environ.get('DATABASE_URL'):
        # PostgreSQL için tablo oluşturma
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(255) PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                profile_url VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                name TEXT NOT NULL,
                price VARCHAR(255) NOT NULL,
                image TEXT,
                brand VARCHAR(255),
                url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                old_price VARCHAR(255),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collections (
                id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                type VARCHAR(255) NOT NULL,
                is_public BOOLEAN DEFAULT TRUE,
                share_url VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_products (
                collection_id VARCHAR(255) NOT NULL,
                product_id VARCHAR(255) NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (collection_id, product_id),
                FOREIGN KEY (collection_id) REFERENCES collections (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_tracking (
                id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                product_id VARCHAR(255) NOT NULL,
                current_price DECIMAL(10,2) NOT NULL,
                original_price DECIMAL(10,2),
                alert_price DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id VARCHAR(255) PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                type VARCHAR(50) DEFAULT 'info',
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
    else:
        # SQLite için tablo oluşturma
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                profile_url TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                price TEXT NOT NULL,
                image TEXT,
                brand TEXT,
                url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                old_price TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collections (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL,
                is_public BOOLEAN DEFAULT 1,
                share_url TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_products (
                collection_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (collection_id, product_id),
                FOREIGN KEY (collection_id) REFERENCES collections (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_tracking (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                current_price REAL NOT NULL,
                original_price REAL,
                alert_price REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT DEFAULT 'info',
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
    
    conn.commit()
    conn.close()
    print(f"[DEBUG] Database tabloları başarıyla oluşturuldu")

def get_placeholder():
    """Database placeholder'ını döndür (PostgreSQL: %s, SQLite: ?)"""
    # Check if we're actually using PostgreSQL
    if os.environ.get('RENDER') and PSYCOPG2_AVAILABLE and os.environ.get('DATABASE_URL'):
        return '%s'  # PostgreSQL
    else:
        return '?'   # SQLite

def execute_query(cursor, query, params=None):
    """Database query'sini çalıştır"""
    if params is None:
        params = ()
    
    try:
        # Check if we're actually using PostgreSQL
        if os.environ.get('RENDER') and PSYCOPG2_AVAILABLE and os.environ.get('DATABASE_URL'):
            # PostgreSQL için parametreleri tuple'a çevir
            if isinstance(params, list):
                params = tuple(params)
            print(f"[DEBUG] PostgreSQL query: {query[:100]}...")
            print(f"[DEBUG] PostgreSQL params: {params}")
            cursor.execute(query, params)
        else:
            # SQLite için parametreleri olduğu gibi kullan
            print(f"[DEBUG] SQLite query: {query[:100]}...")
            print(f"[DEBUG] SQLite params: {params}")
            cursor.execute(query, params)
        print(f"[DEBUG] Query başarıyla çalıştırıldı")
    except Exception as e:
        print(f"[HATA] Query çalıştırma hatası: {e}")
        print(f"[HATA] Query: {query}")
        print(f"[HATA] Params: {params}")
        raise

def get_boolean_value(value):
    """Database için boolean değerini döndür"""
    if os.environ.get('RENDER') and PSYCOPG2_AVAILABLE and os.environ.get('DATABASE_URL'):
        # PostgreSQL için True/False
        return True if value else False
    else:
        # SQLite için 1/0
        return 1 if value else 0

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
        """ID ile kullanıcı getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'SELECT * FROM users WHERE id = {placeholder}', (user_id,))
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                return User(*user_data)
            return None
        except Exception as e:
            print(f"[HATA] Kullanıcı getirme hatası: {e}")
            return None
    
    @staticmethod
    def get_by_username(username):
        """Kullanıcı adı ile kullanıcı getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'SELECT * FROM users WHERE username = {placeholder}', (username,))
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                return User(*user_data)
            return None
        except Exception as e:
            print(f"[HATA] Kullanıcı adı ile getirme hatası: {e}")
            return None
    
    @staticmethod
    def get_by_email(email):
        """Email ile kullanıcı getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'SELECT * FROM users WHERE email = {placeholder}', (email,))
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                return User(*user_data)
            return None
        except Exception as e:
            print(f"[HATA] Email ile getirme hatası: {e}")
            return None
    
    @staticmethod
    def get_by_profile_url(profile_url):
        """Profile URL ile kullanıcı getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'SELECT * FROM users WHERE profile_url = {placeholder}', (profile_url,))
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                return User(*user_data)
            return None
        except Exception as e:
            print(f"[HATA] Profile URL ile getirme hatası: {e}")
            return None
    
    @staticmethod
    def create(username, email, password):
        """Yeni kullanıcı oluştur"""
        try:
            print(f"[DEBUG] Kullanıcı oluşturma başladı: {username}, {email}")
            user_id = str(uuid.uuid4())
            profile_url = f"user_{user_id[:8]}"
            password_hash = generate_password_hash(password)
            
            print(f"[DEBUG] Database bağlantısı kuruluyor...")
            conn = get_db_connection()
            cursor = conn.cursor()
            
            print(f"[DEBUG] Placeholder: {get_placeholder()}")
            placeholder = get_placeholder()
            
            # Önce tabloyu kontrol et
            try:
                execute_query(cursor, "SELECT COUNT(*) FROM users")
                print(f"[DEBUG] Users tablosu mevcut")
            except Exception as table_error:
                print(f"[HATA] Users tablosu bulunamadı: {table_error}")
                # Tabloyu oluştur
                init_db()
                conn = get_db_connection()
                cursor = conn.cursor()
            
            query = f'''
                INSERT INTO users (id, username, email, password_hash, profile_url)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            '''
            print(f"[DEBUG] Query: {query}")
            print(f"[DEBUG] Params: {user_id}, {username}, {email}, {password_hash}, {profile_url}")
            
            execute_query(cursor, query, (user_id, username, email, password_hash, profile_url))
            
            print(f"[DEBUG] Commit yapılıyor...")
            conn.commit()
            conn.close()
            
            print(f"[DEBUG] Kullanıcı başarıyla oluşturuldu")
            return User(user_id, username, email, password_hash, datetime.now(), profile_url)
        except Exception as e:
            print(f"[HATA] Kullanıcı oluşturma hatası: {e}")
            print(f"[HATA] Hata türü: {type(e)}")
            if "UNIQUE constraint failed" in str(e) or "duplicate key value" in str(e):
                raise Exception("Bu kullanıcı adı veya email zaten kullanılıyor")
            raise Exception(f"Kullanıcı oluşturulamadı: {str(e)}")
    
    def check_password(self, password):
        """Şifre kontrolü"""
        return check_password_hash(self.password_hash, password)
    
    def save(self):
        """Kullanıcı bilgilerini güncelle"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'''
                UPDATE users 
                SET username = {placeholder}, email = {placeholder}, password_hash = {placeholder}
                WHERE id = {placeholder}
            ''', (self.username, self.email, self.password_hash, self.id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[HATA] Kullanıcı güncelleme hatası: {e}")
            return False
    
    def set_password(self, password):
        """Şifre güncelle"""
        self.password_hash = generate_password_hash(password)
        return self.save()
    
    def get_products(self):
        """Kullanıcının ürünlerini getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'SELECT * FROM products WHERE user_id = {placeholder} ORDER BY created_at DESC', (self.id,))
            products = cursor.fetchall()
            conn.close()
            
            return [Product(*product) for product in products]
        except Exception as e:
            print(f"[HATA] Kullanıcı ürünleri getirme hatası: {e}")
            return []
    
    def get_collections(self):
        """Kullanıcının koleksiyonlarını getir"""
        return Collection.get_user_collections(self.id)

class Product:
    def __init__(self, id, user_id, name, price, image, brand, url, created_at, old_price=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.price = price
        self.image = image
        self.brand = brand
        self.url = url
        self.created_at = created_at
        self.old_price = old_price
    
    @staticmethod
    def create(user_id, name, price, image, brand, url, old_price=None):
        """Yeni ürün oluştur"""
        try:
            product_id = str(uuid.uuid4())
            created_at = datetime.now()
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            placeholder = get_placeholder()
            execute_query(cursor, f'''
                INSERT INTO products (id, user_id, name, price, image, brand, url, created_at, old_price)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', (product_id, user_id, name, price, image, brand, url, created_at, old_price))
            
            conn.commit()
            conn.close()
            
            return Product(product_id, user_id, name, price, image, brand, url, created_at, old_price)
        except Exception as e:
            print(f"[HATA] Ürün oluşturma hatası: {e}")
            return None
    
    @staticmethod
    def get_by_id(product_id):
        """ID ile ürün getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'SELECT * FROM products WHERE id = {placeholder}', (product_id,))
            product_data = cursor.fetchone()
            conn.close()
            
            if product_data:
                return Product(*product_data)
            return None
        except Exception as e:
            print(f"[HATA] Ürün getirme hatası: {e}")
            return None
    
    @staticmethod
    def delete(product_id, user_id):
        """Ürün sil"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'DELETE FROM products WHERE id = {placeholder} AND user_id = {placeholder}', (product_id, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[HATA] Ürün silme hatası: {e}")
            return False

    @staticmethod
    def get_user_products(user_id):
        """Kullanıcının ürünlerini getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'SELECT * FROM products WHERE user_id = {placeholder} ORDER BY created_at DESC', (user_id,))
            products = cursor.fetchall()
            conn.close()
            
            return [Product(*product) for product in products]
        except Exception as e:
            print(f"[HATA] Kullanıcı ürünleri getirme hatası: {e}")
            return []

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
        try:
            collection_id = str(uuid.uuid4())
            share_url = f"collection_{collection_id[:8]}"
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            placeholder = get_placeholder()
            execute_query(cursor, f'''
                INSERT INTO collections (id, user_id, name, description, type, is_public, share_url)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', (collection_id, user_id, name, description, type, get_boolean_value(is_public), share_url))
            
            conn.commit()
            conn.close()
            
            return Collection(collection_id, user_id, name, description, type, is_public, share_url, datetime.now())
        except Exception as e:
            print(f"[HATA] Koleksiyon oluşturma hatası: {e}")
            return None
    
    @staticmethod
    def get_by_id(collection_id):
        """ID ile koleksiyon getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'SELECT * FROM collections WHERE id = {placeholder}', (collection_id,))
            collection_data = cursor.fetchone()
            conn.close()
            
            if collection_data:
                return Collection(*collection_data)
            return None
        except Exception as e:
            print(f"[HATA] Koleksiyon getirme hatası: {e}")
            return None
    
    @staticmethod
    def get_user_collections(user_id):
        """Kullanıcının koleksiyonlarını getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            placeholder = get_placeholder()
            execute_query(cursor, f'SELECT * FROM collections WHERE user_id = {placeholder} ORDER BY created_at DESC', (user_id,))
            collections = cursor.fetchall()
            conn.close()
            
            return [Collection(*collection) for collection in collections]
        except Exception as e:
            print(f"[HATA] Kullanıcı koleksiyonları getirme hatası: {e}")
            return []
    
    @staticmethod
    def get_by_share_url(share_url):
        """Share URL ile koleksiyon getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'SELECT * FROM collections WHERE share_url = {placeholder}', (share_url,))
            collection_data = cursor.fetchone()
            conn.close()
            
            if collection_data:
                return Collection(*collection_data)
            return None
        except Exception as e:
            print(f"[HATA] Share URL ile koleksiyon getirme hatası: {e}")
            return None
    
    def get_products(self):
        """Koleksiyondaki ürünleri getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'''
                SELECT p.* FROM products p
                JOIN collection_products cp ON p.id = cp.product_id
                WHERE cp.collection_id = {placeholder}
                ORDER BY cp.added_at DESC
            ''', (self.id,))
            products = cursor.fetchall()
            conn.close()
            
            return [Product(*product) for product in products]
        except Exception as e:
            print(f"[HATA] Koleksiyon ürünleri getirme hatası: {e}")
            return []
    
    def add_product(self, product_id):
        """Koleksiyona ürün ekle"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Ürünün zaten koleksiyonda olup olmadığını kontrol et
            placeholder = get_placeholder()
            execute_query(cursor, f'SELECT id FROM collection_products WHERE collection_id = {placeholder} AND product_id = {placeholder}', (self.id, product_id))
            if cursor.fetchone():
                conn.close()
                return False
            
            execute_query(cursor, f'''
                INSERT INTO collection_products (collection_id, product_id)
                VALUES ({placeholder}, {placeholder})
            ''', (self.id, product_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[HATA] Koleksiyona ürün ekleme hatası: {e}")
            return False
    
    def remove_product(self, product_id):
        """Koleksiyondan ürün çıkar"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'DELETE FROM collection_products WHERE collection_id = {placeholder} AND product_id = {placeholder}', (self.id, product_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[HATA] Koleksiyondan ürün çıkarma hatası: {e}")
            return False
    
    def delete(self):
        """Koleksiyonu sil"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'DELETE FROM collection_products WHERE collection_id = {placeholder}', (self.id,))
            execute_query(cursor, f'DELETE FROM collections WHERE id = {placeholder}', (self.id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[HATA] Koleksiyon silme hatası: {e}")
            return False
    


class PriceTracking:
    def __init__(self, id, user_id, product_id, current_price, original_price, alert_price, created_at, last_checked):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.current_price = current_price
        self.original_price = original_price
        self.alert_price = alert_price
        self.created_at = created_at
        self.last_checked = last_checked
    
    @staticmethod
    def create(user_id, product_id, current_price, original_price=None, alert_price=None):
        """Fiyat takibi oluştur"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            tracking_id = str(uuid.uuid4())
            original_price = original_price or current_price
            
            placeholder = get_placeholder()
            execute_query(cursor, f'''
                INSERT INTO price_tracking (id, user_id, product_id, current_price, original_price, alert_price)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', (tracking_id, user_id, product_id, current_price, original_price, alert_price))
            
            conn.commit()
            conn.close()
            
            return tracking_id
        except Exception as e:
            print(f"[HATA] Fiyat takibi oluşturma hatası: {e}")
            return None
    
    @staticmethod
    def get_by_product_and_user(product_id, user_id):
        """Ürün ve kullanıcı için fiyat takibi getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'SELECT * FROM price_tracking WHERE product_id = {placeholder} AND user_id = {placeholder}', (product_id, user_id))
            tracking_data = cursor.fetchone()
            conn.close()
            
            if tracking_data:
                return PriceTracking(*tracking_data)
            return None
        except Exception as e:
            print(f"[HATA] Fiyat takibi getirme hatası: {e}")
            return None
    
    @staticmethod
    def get_user_trackings(user_id):
        """Kullanıcının fiyat takiplerini getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'SELECT * FROM price_tracking WHERE user_id = {placeholder} ORDER BY created_at DESC', (user_id,))
            trackings = cursor.fetchall()
            conn.close()
            
            return [PriceTracking(*tracking) for tracking in trackings]
        except Exception as e:
            print(f"[HATA] Kullanıcı fiyat takipleri getirme hatası: {e}")
            return []
    
    @staticmethod
    def get_user_trackings_with_products(user_id):
        """Kullanıcının fiyat takiplerini ürün bilgileriyle birlikte getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'''
                SELECT pt.*, p.name, p.brand, p.image, p.old_price
                FROM price_tracking pt
                JOIN products p ON pt.product_id = p.id
                WHERE pt.user_id = {placeholder}
                ORDER BY pt.created_at DESC
            ''', (user_id,))
            trackings = cursor.fetchall()
            conn.close()
            
            return trackings
        except Exception as e:
            print(f"[HATA] Kullanıcı fiyat takipleri (ürünlerle) getirme hatası: {e}")
            return []
    
    @staticmethod
    def get_by_id(tracking_id):
        """ID ile fiyat takibi getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'SELECT * FROM price_tracking WHERE id = {placeholder}', (tracking_id,))
            tracking_data = cursor.fetchone()
            conn.close()
            
            if tracking_data:
                return PriceTracking(*tracking_data)
            return None
        except Exception as e:
            print(f"[HATA] Fiyat takibi getirme hatası: {e}")
            return None
    
    def delete(self):
        """Fiyat takibini sil"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'DELETE FROM price_tracking WHERE id = {placeholder}', (self.id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[HATA] Fiyat takibi silme hatası: {e}")
            return False
    
    @staticmethod
    def remove_tracking(tracking_id):
        """Fiyat takibini kaldır"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'DELETE FROM price_tracking WHERE id = {placeholder}', (tracking_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[HATA] Fiyat takibi kaldırma hatası: {e}")
            return False


class Notification:
    def __init__(self, id, user_id, title, message, type, is_read, created_at):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.message = message
        self.type = type
        self.is_read = is_read
        self.created_at = created_at
    
    @staticmethod
    def create(user_id, title, message, type="info"):
        """Yeni bildirim oluştur"""
        try:
            notification_id = str(uuid.uuid4())
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            placeholder = get_placeholder()
            execute_query(cursor, f'''
                INSERT INTO notifications (id, user_id, title, message, type)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', (notification_id, user_id, title, message, type))
            
            conn.commit()
            conn.close()
            
            return notification_id
        except Exception as e:
            print(f"[HATA] Bildirim oluşturma hatası: {e}")
            return None
    
    @staticmethod
    def get_user_notifications(user_id, limit=50):
        """Kullanıcının bildirimlerini getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            
            if os.environ.get('RENDER') and PSYCOPG2_AVAILABLE and os.environ.get('DATABASE_URL'):
                # PostgreSQL için LIMIT syntax
                execute_query(cursor, f'''
                    SELECT * FROM notifications 
                    WHERE user_id = {placeholder} 
                    ORDER BY created_at DESC 
                    LIMIT {limit}
                ''', (user_id,))
            else:
                # SQLite için LIMIT syntax
                execute_query(cursor, f'''
                    SELECT * FROM notifications 
                    WHERE user_id = {placeholder} 
                    ORDER BY created_at DESC 
                    LIMIT {placeholder}
                ''', (user_id, limit))
                
            notifications = cursor.fetchall()
            conn.close()
            
            return [Notification(*notification) for notification in notifications]
        except Exception as e:
            print(f"[HATA] Bildirimler getirme hatası: {e}")
            return []
    
    @staticmethod
    def mark_as_read(notification_id):
        """Bildirimi okundu olarak işaretle"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'UPDATE notifications SET is_read = {get_boolean_value(True)} WHERE id = {placeholder}', (notification_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[HATA] Bildirim okundu işaretleme hatası: {e}")
            return False
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Kullanıcının tüm bildirimlerini okundu olarak işaretle"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'UPDATE notifications SET is_read = {get_boolean_value(True)} WHERE user_id = {placeholder}', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[HATA] Tüm bildirimleri okundu işaretleme hatası: {e}")
            return False
    
    @staticmethod
    def get_unread_count(user_id):
        """Kullanıcının okunmamış bildirim sayısını getir"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            placeholder = get_placeholder()
            execute_query(cursor, f'SELECT COUNT(*) FROM notifications WHERE user_id = {placeholder} AND is_read = {get_boolean_value(False)}', (user_id,))
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
        except Exception as e:
            print(f"[HATA] Okunmamış bildirim sayısı getirme hatası: {e}")
            return 0 