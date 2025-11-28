"""
Database path utility
Veritabanı yolunu tutarlı şekilde belirlemek için yardımcı fonksiyon
"""
import os

def get_db_path():
    """Veritabanı dosya yolunu döndür"""
    # run.py dosyasının bulunduğu dizini bul
    # run.py -> kataloggia-main/kataloggia-main/run.py
    # favit.db -> kataloggia-main/kataloggia-main/favit.db
    
    # Önce çalışma dizininde kontrol et
    current_dir = os.getcwd()
    db_path = os.path.join(current_dir, 'favit.db')
    
    # Eğer çalışma dizininde yoksa, run.py'nin olduğu dizinde ara
    if not os.path.exists(db_path):
        # run.py genellikle kataloggia-main/kataloggia-main/ dizininde
        # app/utils/db_path.py -> app/utils -> app -> kataloggia-main/kataloggia-main
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        # app/utils -> app -> kataloggia-main/kataloggia-main
        base_dir = os.path.dirname(os.path.dirname(current_file_dir))
        db_path = os.path.join(base_dir, 'favit.db')
        
        # Eğer hala yoksa, bir üst dizinde ara
        if not os.path.exists(db_path):
            parent_dir = os.path.dirname(base_dir)
            db_path = os.path.join(parent_dir, 'favit.db')
    
    return db_path

def get_db_connection():
    """Veritabanı bağlantısı oluştur"""
    import sqlite3
    db_path = get_db_path()
    return sqlite3.connect(db_path)

