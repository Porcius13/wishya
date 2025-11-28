# Render.com Deployment Rehberi

Bu rehber, site spesifik scraper'ları Render.com'da deploy etmek için hazırlanmıştır.

## 🚀 Hızlı Başlangıç

### 1. Render.com'da Yeni Web Service Oluşturma

1. [Render.com](https://render.com) hesabınıza giriş yapın
2. "New +" butonuna tıklayın
3. "Web Service" seçin
4. GitHub repository'nizi bağlayın

### 2. Build Ayarları

Render.com'da aşağıdaki ayarları kullanın:

**Build Command:**
```bash
pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium && playwright install-deps
```

**Start Command:**
```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --max-requests 1000 --max-requests-jitter 100 --preload
```

### 3. Environment Variables

Aşağıdaki environment variable'ları ekleyin:

| Key | Value | Açıklama |
|-----|-------|----------|
| `PYTHON_VERSION` | `3.11.0` | Python versiyonu |
| `RENDER` | `true` | Render.com ortamı |
| `DISPLAY` | `:99` | Display ayarı |
| `PLAYWRIGHT_BROWSERS_PATH` | `/opt/playwright` | Playwright browser path |
| `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD` | `0` | Browser download'ı etkinleştir |
| `FLASK_ENV` | `production` | Flask production modu |
| `FLASK_DEBUG` | `false` | Debug modu kapalı |
| `SECRET_KEY` | `[generate]` | Güvenli secret key |
| `PYTHONUNBUFFERED` | `1` | Python output buffering kapalı |

## 📁 Dosya Yapısı

```
kataloggia/
├── app.py                          # Ana Flask uygulaması
├── render_scraper.py               # Render.com için optimize edilmiş scraper
├── site_specific_scrapers.py       # Site spesifik scraper'lar
├── advanced_site_scrapers.py       # Gelişmiş scraper'lar
├── requirements.txt                # Python dependencies
├── render.yaml                     # Render.com konfigürasyonu
├── build.sh                        # Build script
└── templates/                      # Flask template'leri
```

## 🔧 Önemli Ayarlar

### 1. Worker Sayısı
Render.com'da `--workers 1` kullanın çünkü:
- Playwright browser instance'ları memory kullanır
- Free tier'da memory sınırlıdır
- Async/await sorunlarını önler

### 2. Timeout Ayarları
- `--timeout 300`: 5 dakika timeout
- Playwright scraping işlemleri uzun sürebilir

### 3. Browser Ayarları
Playwright için özel browser argümanları:
```python
args=[
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    # ... diğer ayarlar
]
```

## 🧪 Test Etme

### 1. Yerel Test
```bash
python render_scraper.py
```

### 2. Render.com Test
Deploy sonrası şu URL'leri test edin:
- `https://your-app.onrender.com/` - Ana sayfa
- `https://your-app.onrender.com/scrape?url=URL` - Scraping test

## 🐛 Sorun Giderme

### 1. Playwright Kurulum Sorunları
```bash
# Build loglarında şu komutları kontrol edin:
playwright install chromium
playwright install-deps chromium
```

### 2. Memory Sorunları
- Worker sayısını 1'e düşürün
- Browser instance'larını düzgün kapatın
- Timeout değerlerini artırın

### 3. Async/Await Sorunları
- `render_scraper.py` kullanın
- Sync wrapper fonksiyonlarını kullanın
- Event loop sorunlarını kontrol edin

## 📊 Performans

### 1. Memory Kullanımı
- Her browser instance ~50-100MB kullanır
- Free tier'da 512MB limit var
- Dikkatli memory yönetimi gerekli

### 2. Response Time
- İlk scraping: 10-30 saniye
- Cache'li scraping: 1-5 saniye
- Timeout: 300 saniye

### 3. Rate Limiting
- Her request arasında 1 saniye bekleme
- Render.com rate limit'lerini aşmayın

## 🔒 Güvenlik

### 1. Environment Variables
- `SECRET_KEY` güvenli olmalı
- Production'da debug kapalı olmalı
- API key'ler environment variable'da saklanmalı

### 2. Input Validation
- URL validation yapın
- XSS koruması ekleyin
- Rate limiting uygulayın

## 📈 Monitoring

### 1. Logs
Render.com dashboard'unda:
- Build logs
- Runtime logs
- Error logs

### 2. Health Check
```yaml
healthCheckPath: /
```

### 3. Metrics
- Response time
- Memory usage
- Error rate

## 🚀 Deployment Checklist

- [ ] `render.yaml` dosyası hazır
- [ ] `requirements.txt` güncel
- [ ] Environment variables ayarlandı
- [ ] Build script test edildi
- [ ] Scraper'lar test edildi
- [ ] Health check çalışıyor
- [ ] Logs kontrol edildi

## 📞 Destek

Sorun yaşarsanız:
1. Render.com build logs'ları kontrol edin
2. Runtime logs'ları inceleyin
3. Yerel test yapın
4. Memory ve timeout ayarlarını kontrol edin

---

**Not:** Bu rehber Render.com free tier için optimize edilmiştir. Pro tier'da daha fazla resource kullanabilirsiniz.
