# Wishya - Render Deployment Guide

Bu dosya, Wishya projesini Render üzerinde deploy etmek için gerekli adımları açıklar.

## 🚀 Render'da Deploy Etme Adımları

### 1. Render Hesabı Oluşturma
- [Render.com](https://render.com) adresine gidin
- GitHub hesabınızla giriş yapın
- Yeni bir hesap oluşturun

### 2. Projeyi Render'a Bağlama
1. Render Dashboard'da "New +" butonuna tıklayın
2. "Blueprint" seçeneğini seçin
3. GitHub repository'nizi bağlayın
4. `render.yaml` dosyası otomatik olarak algılanacak

### 3. Environment Variables
Render otomatik olarak şu environment variables'ları ayarlayacak:
- `DATABASE_URL`: PostgreSQL veritabanı bağlantısı
- `SECRET_KEY`: Güvenli secret key
- `FLASK_ENV`: production
- `RENDER`: true

### 4. Veritabanı
- PostgreSQL veritabanı otomatik olarak oluşturulacak
- Tablolar uygulama ilk çalıştığında otomatik oluşturulacak

### 5. Build ve Deploy
- Render otomatik olarak Docker image'ını build edecek
- Playwright browser'ları yüklenecek
- Gunicorn ile production server başlatılacak

## 📁 Dosya Yapısı

```
wishya/
├── app.py                 # Ana Flask uygulaması
├── models.py             # Veritabanı modelleri (PostgreSQL desteği)
├── requirements.txt      # Python bağımlılıkları
├── Dockerfile           # Docker konfigürasyonu
├── render.yaml          # Render deployment konfigürasyonu
├── templates/           # HTML template'leri
└── README_RENDER.md     # Bu dosya
```

## 🔧 Teknik Detaylar

### Veritabanı Değişiklikleri
- SQLite yerine PostgreSQL kullanılıyor
- `models.py` dosyasında otomatik veritabanı algılama
- Render'da `DATABASE_URL` environment variable'ı kullanılıyor

### Production Server
- Gunicorn kullanılıyor (Flask development server yerine)
- 2 worker process
- 120 saniye timeout
- Port 8080'de çalışıyor

### Browser Automation
- Playwright Chromium browser kullanılıyor
- Docker container'da headless modda çalışıyor
- Chrome dependencies yüklü

## 🐛 Sorun Giderme

### Build Hatası
- Logları kontrol edin
- Requirements.txt'deki versiyonları kontrol edin
- Docker build cache'ini temizleyin

### Veritabanı Bağlantı Hatası
- `DATABASE_URL` environment variable'ını kontrol edin
- PostgreSQL servisinin çalıştığından emin olun
- Firewall ayarlarını kontrol edin

### Scraping Hatası
- Playwright browser'larının yüklendiğinden emin olun
- Chrome dependencies'in yüklü olduğunu kontrol edin
- Memory limit'leri kontrol edin

## 📊 Monitoring

Render Dashboard'da şunları takip edebilirsiniz:
- Application logs
- Database logs
- Resource usage (CPU, Memory)
- Response times
- Error rates

## 🔄 Otomatik Deploy

- GitHub'a push yaptığınızda otomatik deploy
- `render.yaml` dosyasında `autoDeploy: true` ayarı
- Health check endpoint: `/`

## 💰 Maliyet

- Starter plan: $7/ay (web service)
- Starter plan: $7/ay (PostgreSQL database)
- Toplam: ~$14/ay

## 📞 Destek

Sorun yaşarsanız:
1. Render Dashboard loglarını kontrol edin
2. GitHub Issues'da sorun açın
3. Render Support'a başvurun

---

**Not:** Bu deployment guide sürekli güncellenmektedir. En güncel bilgiler için GitHub repository'yi kontrol edin.
