# 🚀 Deployment Rehberi - GitHub ve Vercel

Bu rehber, Wishya uygulamasını GitHub'a yükleyip Vercel üzerinden deploy etmeniz için hazırlanmıştır.

## ✅ Yapılan Değişiklikler

1. **localStorage Desteği**: Tüm kullanıcı verileri artık tarayıcıda localStorage'da saklanıyor
2. **Vercel Uyumluluğu**: `app.py` dosyası Vercel için hazırlandı
3. **Client-Side Auth**: Kimlik doğrulama artık frontend'de localStorage ile yapılıyor
4. **GitHub Hazırlığı**: `.gitignore` ve `README.md` dosyaları eklendi

## 📋 Adım Adım Deployment

### 1. GitHub'a Yükleme

```bash
# Proje dizinine gidin
cd kataloggia-main/kataloggia-main

# Git repository başlatın
git init

# Tüm dosyaları ekleyin
git add .

# İlk commit
git commit -m "Initial commit - localStorage based Wishya app"

# GitHub'da yeni repository oluşturun, sonra:
git remote add origin https://github.com/KULLANICIADI/REPO-ADI.git
git branch -M main
git push -u origin main
```

### 2. Vercel'e Deploy Etme

1. **Vercel Hesabı Oluşturun**
   - [vercel.com](https://vercel.com) adresine gidin
   - GitHub hesabınızla giriş yapın

2. **Yeni Proje Oluşturun**
   - Dashboard'da "New Project" butonuna tıklayın
   - GitHub repository'nizi seçin
   - "Import" butonuna tıklayın

3. **Ayarları Yapılandırın**
   - **Framework Preset**: Other
   - **Root Directory**: `kataloggia-main/kataloggia-main` (eğer repo root'ta değilse)
   - **Build Command**: (boş bırakın)
   - **Output Directory**: (boş bırakın)
   - **Install Command**: `pip install -r requirements.txt`

4. **Environment Variables (Opsiyonel)**
   - `SECRET_KEY`: Flask için secret key (rastgele bir string)
   - Örnek: `python -c "import secrets; print(secrets.token_hex(32))"`

5. **Deploy**
   - "Deploy" butonuna tıklayın
   - Deployment tamamlandıktan sonra URL'nizi alacaksınız

## 🔧 Önemli Notlar

### localStorage Kullanımı

- **Tüm veriler tarayıcıda saklanır**: Ürünler, koleksiyonlar, kullanıcı bilgileri
- **Her kullanıcının verileri kendi tarayıcısında**: Farklı cihazlarda farklı veriler
- **Tarayıcı verilerini temizlerseniz veriler silinir**: Dikkatli olun!

### Veritabanı Yok

- Backend'de veritabanı kullanılmıyor
- Tüm işlemler frontend'de localStorage ile yapılıyor
- Scraping işlemleri için backend API kullanılıyor (sadece scraping için)

### Kullanıcı Kayıtları

- Kullanıcılar `wishya_users` key'i altında localStorage'da saklanıyor
- Şifreler **şifrelenmemiş** olarak saklanıyor (güvenlik için production'da hash'lenmeli)
- Her kullanıcının verileri kendi tarayıcısında

## 🐛 Sorun Giderme

### Import Hatası

Eğer Vercel'de import hatası alırsanız:
1. `app.py` dosyasının doğru dizinde olduğundan emin olun
2. `vercel.json` dosyasının doğru yapılandırıldığından emin olun
3. Vercel logs'ları kontrol edin

### Static Dosyalar Yüklenmiyor

`vercel.json` dosyasında static dosyalar için route tanımlı:
```json
{
  "src": "/static/(.*)",
  "dest": "/static/$1"
}
```

### localStorage Çalışmıyor

- Tarayıcı console'unda hata var mı kontrol edin
- `localStorage.js` ve `auth.js` dosyalarının yüklendiğinden emin olun
- HTTPS kullanıyorsanız localStorage çalışmalı

## 📝 Dosya Yapısı

```
kataloggia-main/kataloggia-main/
├── app.py                 # Vercel entry point
├── vercel.json           # Vercel konfigürasyonu
├── .gitignore            # Git ignore dosyası
├── README.md             # Proje dokümantasyonu
├── static/
│   └── js/
│       ├── localStorage.js  # localStorage yönetimi
│       └── auth.js          # Client-side auth
└── templates/
    ├── login.html        # localStorage ile login
    └── register.html     # localStorage ile register
```

## 🎉 Başarılı Deployment Sonrası

1. Uygulamanız canlı olacak
2. Arkadaşlarınız URL'yi kullanarak erişebilir
3. Her kullanıcı kendi tarayıcısında verilerini saklayacak
4. Veritabanı gerektirmez, tamamen ücretsiz!

## 📞 Destek

Sorun yaşarsanız:
1. Vercel logs'larını kontrol edin
2. Browser console'da hataları kontrol edin
3. GitHub Issues'da sorun açın

---

**Not**: Bu uygulama tamamen client-side çalışır. Backend sadece scraping için kullanılır. Tüm kullanıcı verileri localStorage'da saklanır.

