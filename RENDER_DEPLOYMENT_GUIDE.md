# Render Deployment Rehberi - Ücretsiz Plan

Bu rehber, Wishya projenizi Render'ın ücretsiz planında deploy etmek için hazırlanmıştır.

## 🚀 Render Ücretsiz Plan Özellikleri

- **750 saat/ay** (yaklaşık 31 gün)
- **512 MB RAM**
- **0.1 CPU**
- **15 dakika inaktiflik** sonrası uyku modu
- **Otomatik uyandırma** (ilk istek geldiğinde)

## 📋 Ön Gereksinimler

1. **Render Hesabı**: [render.com](https://render.com) adresinden ücretsiz hesap oluşturun
2. **GitHub Repository**: Projenizi GitHub'a yükleyin
3. **PostgreSQL Database**: Render'da ücretsiz PostgreSQL veritabanı oluşturun

## 🔧 Deployment Adımları

### 1. Render Dashboard'a Giriş

1. [Render Dashboard](https://dashboard.render.com) adresine gidin
2. GitHub hesabınızla giriş yapın

### 2. PostgreSQL Database Oluşturma

1. **New** > **PostgreSQL** seçin
2. **Name**: `wishya-db`
3. **Database**: `wishya`
4. **User**: `wishya_user`
5. **Region**: `Oregon` (en hızlı)
6. **Plan**: `Free`
7. **Create Database** butonuna tıklayın

### 3. Web Service Oluşturma

1. **New** > **Web Service** seçin
2. **Connect Repository**: GitHub repository'nizi seçin
3. **Name**: `wishya-app`
4. **Region**: `Oregon`
5. **Branch**: `main` (veya `master`)
6. **Root Directory**: Boş bırakın
7. **Runtime**: `Docker`
8. **Build Command**: `docker build -t wishya-app .`
9. **Start Command**: `docker run -p $PORT:8080 wishya-app`

### 4. Environment Variables

Aşağıdaki environment variable'ları ekleyin:

```
PYTHON_VERSION=3.11.0
FLASK_ENV=production
FLASK_DEBUG=false
RENDER=true
SECRET_KEY=<otomatik oluşturulacak>
DATABASE_URL=<PostgreSQL connection string>
PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=false
PYTHONUNBUFFERED=1
```

### 5. Database URL Bağlantısı

1. PostgreSQL service'inize gidin
2. **Connections** sekmesine tıklayın
3. **External Database URL**'yi kopyalayın
4. Web service'inizde `DATABASE_URL` environment variable'ına yapıştırın

## ⚡ Optimizasyonlar

### Memory Management
- Cache süresi 30 dakikaya düşürüldü
- Maksimum cache boyutu 50 entry ile sınırlandırıldı
- Otomatik memory cleanup eklendi

### Performance
- Tek worker kullanımı (512MB RAM için)
- Gunicorn timeout 120 saniye
- Keep-alive bağlantıları optimize edildi

### Health Check
- `/health` endpoint'i eklendi
- Database bağlantı kontrolü
- Memory usage monitoring

## 🔍 Monitoring

### Health Check Endpoint
```
https://your-app-name.onrender.com/health
```

Response:
```json
{
  "status": "healthy",
  "memory_usage": "45%",
  "cache_size": 12,
  "timestamp": 1705123456.789
}
```

### Logs
Render Dashboard'da **Logs** sekmesinden canlı logları takip edebilirsiniz.

## 🚨 Önemli Notlar

### Uyku Modu
- 15 dakika inaktiflik sonrası uygulama uyku moduna geçer
- İlk istek geldiğinde otomatik olarak uyanır (30-60 saniye)
- Bu normal bir durumdur ve ücretsiz planın özelliğidir

### Memory Limitleri
- 512MB RAM sınırı vardır
- Büyük scraping işlemleri memory'yi doldurabilir
- Otomatik cleanup mekanizması eklendi

### Rate Limiting
- Render'da rate limiting vardır
- Çok fazla istek gönderirseniz geçici olarak engellenebilirsiniz

## 🛠️ Sorun Giderme

### Build Hatası
```bash
# Local test
docker build -t wishya-app .
docker run -p 8080:8080 wishya-app
```

### Database Bağlantı Hatası
1. `DATABASE_URL` environment variable'ını kontrol edin
2. PostgreSQL service'inin aktif olduğundan emin olun
3. Database credentials'larını doğrulayın

### Memory Hatası
1. `/health` endpoint'ini kontrol edin
2. Cache boyutunu azaltın
3. Scraping işlemlerini optimize edin

## 📊 Performance Monitoring

### Memory Usage
- `/health` endpoint'inden memory kullanımını takip edin
- %80 üzerinde ise otomatik cleanup çalışır

### Response Times
- İlk istek: 30-60 saniye (uyku modundan uyanma)
- Normal istekler: 1-5 saniye
- Scraping işlemleri: 10-30 saniye

## 🔄 Güncelleme

Kod değişikliklerinizi GitHub'a push ettiğinizde Render otomatik olarak yeni deployment başlatacaktır.

## 💰 Maliyet

Render ücretsiz planı tamamen ücretsizdir:
- 750 saat/ay web service
- 1GB PostgreSQL database
- Otomatik SSL sertifikası
- Global CDN

## 📞 Destek

Sorun yaşarsanız:
1. Render Dashboard'daki logları kontrol edin
2. `/health` endpoint'ini test edin
3. GitHub Issues'da sorun bildirin

---

**Not**: Bu rehber Render'ın ücretsiz planı için optimize edilmiştir. Daha yüksek performans için ücretli planlara geçiş yapabilirsiniz.
