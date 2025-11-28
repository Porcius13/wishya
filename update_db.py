#!/usr/bin/env python3

import sqlite3
from models import init_db

def update_database():
    """Veritabanını güncelle ve eksik kolonları ekle"""
    
    print("Veritabanı güncelleniyor...")
    
    # Veritabanını başlat (yeni şema ile)
    init_db()
    
    # Eksik kolonları manuel olarak ekle
    conn = sqlite3.connect('favit.db')
    cursor = conn.cursor()
    
    # Mevcut kolonları kontrol et
    cursor.execute("PRAGMA table_info(products)")
    columns = [column[1] for column in cursor.fetchall()]
    
    print(f"Mevcut kolonlar: {columns}")
    
    # Eksik kolonları ekle
    missing_columns = []
    
    if 'old_price' not in columns:
        missing_columns.append('old_price')
        cursor.execute('ALTER TABLE products ADD COLUMN old_price TEXT')
        print("✓ old_price kolonu eklendi")
    
    if 'current_price' not in columns:
        missing_columns.append('current_price')
        cursor.execute('ALTER TABLE products ADD COLUMN current_price TEXT')
        print("✓ current_price kolonu eklendi")
    
    if 'discount_percentage' not in columns:
        missing_columns.append('discount_percentage')
        cursor.execute('ALTER TABLE products ADD COLUMN discount_percentage TEXT')
        print("✓ discount_percentage kolonu eklendi")
    
    if not missing_columns:
        print("✓ Tüm kolonlar zaten mevcut")
    
    conn.commit()
    conn.close()
    
    print("Veritabanı güncelleme tamamlandı!")

if __name__ == "__main__":
    update_database()
