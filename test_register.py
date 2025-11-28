from models import User, init_db

def test_registration():
    print("🧪 Kayıt Sistemi Testi Başlıyor...")
    
    # Veritabanını başlat
    init_db()
    
    # Test kullanıcısı oluştur
    try:
        user = User.create("testuser", "test@example.com", "password123")
        print(f"✅ Kullanıcı oluşturuldu: {user.username}")
        
        # Kullanıcıyı kontrol et
        found_user = User.get_by_username("testuser")
        if found_user:
            print(f"✅ Kullanıcı bulundu: {found_user.username}")
        else:
            print("❌ Kullanıcı bulunamadı!")
        
        # Email kontrolü
        email_user = User.get_by_email("test@example.com")
        if email_user:
            print(f"✅ Email ile kullanıcı bulundu: {email_user.email}")
        else:
            print("❌ Email ile kullanıcı bulunamadı!")
        
        # Şifre kontrolü
        if found_user and found_user.check_password("password123"):
            print("✅ Şifre kontrolü başarılı!")
        else:
            print("❌ Şifre kontrolü başarısız!")
            
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    test_registration() 