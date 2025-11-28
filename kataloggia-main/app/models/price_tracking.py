"""
Price Tracking Model
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
from models import PriceTracking as BasePriceTracking

# Mevcut PriceTracking modelini kullan
PriceTracking = BasePriceTracking

# get_all_active method ekle
@classmethod
def get_all_active(cls):
    """Tüm aktif fiyat takiplerini getir"""
    import sqlite3
    from app.utils.db_path import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, product_id, user_id, current_price, price_change, 
               original_price, is_active, alert_price, created_at, last_checked
        FROM price_tracking 
        WHERE is_active = 1
    ''')
    trackings = cursor.fetchall()
    conn.close()
    
    return [cls(*tracking) for tracking in trackings]

BasePriceTracking.get_all_active = get_all_active
PriceTracking = BasePriceTracking

