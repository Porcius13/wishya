import os
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from typing import Any, Optional

# Database configuration for Render
# Lightweight wrappers to normalize parameter style between SQLite ('?') and psycopg2 ('%s')
class PostgresCursorWrapper:
    def __init__(self, inner_cursor):
        self._cursor = inner_cursor

    def execute(self, sql: str, params: Optional[tuple] = None):
        # Convert sqlite style placeholders to psycopg2 style
        sql_converted = sql.replace('?', '%s')
        if params is None:
            return self._cursor.execute(sql_converted)
        return self._cursor.execute(sql_converted, params)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    # Expose attributes that might be used implicitly
    def __getattr__(self, name: str) -> Any:
        return getattr(self._cursor, name)


class PostgresConnectionWrapper:
    def __init__(self, inner_connection):
        self._conn = inner_connection

    def cursor(self):
        return PostgresCursorWrapper(self._conn.cursor())

    def commit(self):
        return self._conn.commit()

    def close(self):
        return self._conn.close()

    # Expose attributes if needed
    def __getattr__(self, name: str) -> Any:
        return getattr(self._conn, name)

def get_db_url():
    """Get database URL from environment variables"""
    if os.environ.get('DATABASE_URL'):
        # Render provides DATABASE_URL, but SQLAlchemy expects postgresql://
        url = os.environ.get('DATABASE_URL')
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        return url
    else:
        # Fallback to SQLite for local development
        return 'sqlite:///favit.db'

def get_db_connection():
    """Get database connection based on environment"""
    if os.environ.get('DATABASE_URL'):
        # Use PostgreSQL for production
        import psycopg2
        from urllib.parse import urlparse
        
        url = urlparse(os.environ.get('DATABASE_URL'))
        conn = psycopg2.connect(
            host=url.hostname,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            port=url.port or 5432
        )
        # Return wrapper to normalize paramstyle
        return PostgresConnectionWrapper(conn)
    else:
        # Use SQLite for local development
        import sqlite3
        return sqlite3.connect('favit.db')

def init_db():
    """Veritabanını başlat"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if we're using PostgreSQL
    is_postgres = os.environ.get('DATABASE_URL') is not None
    
    if is_postgres:
        # PostgreSQL syntax
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                price TEXT NOT NULL,
                image TEXT,
                brand TEXT NOT NULL,
                url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Ensure old_price column exists for compatibility with inserts
        cursor.execute('''
            ALTER TABLE products ADD COLUMN IF NOT EXISTS old_price TEXT
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collections (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL,
                is_public BOOLEAN DEFAULT TRUE,
                share_url TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_products (
                id TEXT PRIMARY KEY,
                collection_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_tracking (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                current_price TEXT NOT NULL,
                original_price TEXT NOT NULL,
                price_change TEXT DEFAULT '0',
                is_active BOOLEAN DEFAULT TRUE,
                alert_price TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                price TEXT NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                collection_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                collection_id TEXT NOT NULL,
                comment TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_logs (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                domain TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                response_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limits (
                id TEXT PRIMARY KEY,
                domain TEXT NOT NULL,
                request_count INTEGER DEFAULT 0,
                last_request TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS follows (
                id TEXT PRIMARY KEY,
                follower_id TEXT NOT NULL,
                following_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
    else:
        # SQLite syntax (existing code)
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
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Ensure old_price column exists on SQLite as well
        try:
            cursor.execute('PRAGMA table_info(products)')
            cols = [row[1] for row in cursor.fetchall()]
            if 'old_price' not in cols:
                cursor.execute('ALTER TABLE products ADD COLUMN old_price TEXT')
        except Exception:
            pass
        
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                price TEXT NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                collection_id TEXT NOT NULL,
                comment TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (collection_id) REFERENCES collections (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_logs (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                domain TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                response_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rate_limits (
                id TEXT PRIMARY KEY,
                domain TEXT NOT NULL,
                request_count INTEGER DEFAULT 0,
                last_request TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
        conn = get_db_connection()
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
        conn = get_db_connection()
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            return User(*user_data)
        return None
    
    @staticmethod
    def get_by_profile_url(profile_url):
        conn = get_db_connection()
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
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (id, username, email, password_hash, profile_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, email, password_hash, profile_url))
            
            conn.commit()
            conn.close()
            
            return User(user_id, username, email, password_hash, datetime.now(), profile_url)
        except Exception as e:
            print(f"[HATA] Kullanıcı oluşturma hatası: {e}")
            if "UNIQUE constraint failed" in str(e) or "duplicate key value" in str(e):
                raise Exception("Bu kullanıcı adı veya email zaten kullanılıyor")
            raise Exception("Kullanıcı oluşturulamadı")
    
    def check_password(self, password):
        """Şifre kontrolü"""
        return check_password_hash(self.password_hash, password)
    
    def get_products(self):
        """Kullanıcının ürünlerini getir"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE user_id = ? ORDER BY created_at DESC', (self.id,))
        products = cursor.fetchall()
        conn.close()
        
        return [Product(*product) for product in products]
    
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
    def create(user_id, name, price, image, brand, url):
        """Yeni ürün oluştur"""
        product_id = str(uuid.uuid4())
        created_at = datetime.now()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO products (id, user_id, name, price, image, brand, url, created_at, old_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product_id, user_id, name, price, image, brand, url, created_at, None))
        
        conn.commit()
        conn.close()
        
        return Product(product_id, user_id, name, price, image, brand, url, created_at, None)
    
    @staticmethod
    def get_by_id(product_id):
        """ID ile ürün getir"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product_data = cursor.fetchone()
        conn.close()
        
        if product_data:
            return Product(*product_data)
        return None
    
    @staticmethod
    def delete(product_id, user_id):
        """Ürün sil"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM products WHERE id = ? AND user_id = ?', (product_id, user_id))
        conn.commit()
        conn.close()

    @staticmethod
    def get_user_products(user_id):
        """Kullanıcının ürünlerini getir"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        products = cursor.fetchall()
        conn.close()
        
        return [Product(*product) for product in products]

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
        
        conn = get_db_connection()
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
        conn = get_db_connection()
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
        conn = get_db_connection()
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM collections WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        collections = cursor.fetchall()
        conn.close()
        
        return [Collection(*collection) for collection in collections]
    

    
    def get_products(self):
        """Koleksiyondaki ürünleri getir"""
        conn = get_db_connection()
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
        """Koleksiyona ürün ekle"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ürünün zaten koleksiyonda olup olmadığını kontrol et
        cursor.execute('SELECT id FROM collection_products WHERE collection_id = ? AND product_id = ?', (self.id, product_id))
        if cursor.fetchone():
            conn.close()
            return False
        
        cp_id = str(uuid.uuid4())
        cursor.execute('''
            INSERT INTO collection_products (id, collection_id, product_id)
            VALUES (?, ?, ?)
        ''', (cp_id, self.id, product_id))
        
        conn.commit()
        conn.close()
        return True
    
    def remove_product(self, product_id):
        """Koleksiyondan ürün çıkar"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM collection_products WHERE collection_id = ? AND product_id = ?', (self.id, product_id))
        conn.commit()
        conn.close()
    
    def delete(self):
        """Koleksiyonu sil"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM collection_products WHERE collection_id = ?', (self.id,))
        cursor.execute('DELETE FROM collections WHERE id = ?', (self.id,))
        conn.commit()
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
        conn = get_db_connection()
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
        conn = get_db_connection()
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
        conn = get_db_connection()
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
        conn = get_db_connection()
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
        conn = get_db_connection()
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
    


 