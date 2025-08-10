import sqlite3

def check_database():
    try:
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        
        # Tabloları kontrol et
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("📋 Veritabanı Tabloları:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Kullanıcı sayısını kontrol et
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"\n👥 Toplam Kullanıcı: {user_count}")
        
        # Kullanıcıları listele
        if user_count > 0:
            cursor.execute("SELECT username, email FROM users")
            users = cursor.fetchall()
            print("\n📝 Kullanıcı Listesi:")
            for user in users:
                print(f"  - {user[0]} ({user[1]})")
        
        conn.close()
        print("\n✅ Veritabanı kontrolü tamamlandı!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    check_database() 