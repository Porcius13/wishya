# 🚀 Gelişmiş Scraper Kullanım Kılavuzu

## 📋 İçindekiler
1. [Yeni Özellikler](#yeni-özellikler)
2. [Kurulum](#kurulum)
3. [Kullanım](#kullanım)
4. [Hata Yönetimi](#hata-yönetimi)
5. [İzleme ve Raporlama](#izleme-ve-raporlama)
6. [Sorun Giderme](#sorun-giderme)
7. [En İyi Uygulamalar](#en-iyi-uygulamalar)

## ✨ Yeni Özellikler

### 🔄 Retry Mekanizması
- **Otomatik Yeniden Deneme**: Başarısız scraping işlemleri otomatik olarak 3 kez denenir
- **Exponential Backoff**: Her denemede bekleme süresi katlanarak artar
- **Akıllı Başarı Kontrolü**: Sadece gerçekten başarılı sonuçlar kabul edilir

### ⏱️ Rate Limiting
- **Domain Bazlı Sınırlama**: Her domain için saniyede maksimum 2 istek
- **Otomatik Bekleme**: Rate limit aşıldığında otomatik bekleme
- **Akıllı Zamanlama**: 60 saniyelik pencere içinde istekleri yönetir

### 🛡️ Gelişmiş Bot Koruması Aşma
- **Stealth Scripts**: Gelişmiş bot tespiti engelleme
- **Mobil User-Agent**: iPhone Safari simülasyonu
- **Fingerprinting Engelleme**: Canvas, WebGL, Audio fingerprinting koruması
- **Site-Specific Yaklaşımlar**: Her site için özel stratejiler

### 📊 İzleme ve Raporlama
- **Gerçek Zamanlı İstatistikler**: Başarı oranları, hata analizi
- **Domain Bazlı Analiz**: Hangi sitelerde sorun yaşandığını tespit
- **Hata Kategorileri**: Timeout, bot detection, selector not found vb.
- **Otomatik Öneriler**: Hata türüne göre düzeltme önerileri

### 🔧 Gelişmiş Hata Yakalama
- **Detaylı Loglama**: Tüm hatalar timestamp ile kaydedilir
- **Hata Kategorileri**: Hatalar türlerine göre sınıflandırılır
- **Otomatik Analiz**: Hata paternleri otomatik tespit edilir

## 🛠️ Kurulum

### Gereksinimler
```bash
pip install playwright flask flask-login
playwright install chromium
```

### Konfigürasyon
```python
# app.py içinde otomatik olarak yapılandırılır
# Ek konfigürasyon gerekmez
```

## 📖 Kullanım

### Temel Kullanım
```python
import asyncio
from app import scrape_product

# Async scraping
async def main():
    url = "https://www.hepsiburada.com/product/123"
    result = await scrape_product(url)
    print(result)

# Çalıştır
asyncio.run(main())
```

### Flask Route ile Kullanım
```python
@app.route("/add_product", methods=["POST"])
@login_required
def add_product():
    url = request.form.get('url')
    result = asyncio.run(scrape_product(url))
    # Sonucu işle...
```

## 🔍 Hata Yönetimi

### Hata Türleri ve Çözümler

#### 1. Timeout Hataları
**Belirtiler:**
- Sayfa yüklenme süresi aşımı
- Network bağlantı sorunları

**Çözümler:**
```python
# Timeout süresini artır
await page.goto(url, timeout=60000)  # 60 saniye
await page.wait_for_timeout(5000)    # 5 saniye ek bekleme
```

#### 2. Bot Detection Hataları
**Belirtiler:**
- "Access Denied" mesajları
- CAPTCHA sayfaları
- "BIR DAKIKA" uyarıları

**Çözümler:**
```python
# Stealth script'leri güncelle
await page.add_init_script(get_advanced_stealth_script())

# User-Agent değiştir
context = await browser.new_context(
    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
)
```

#### 3. Selector Not Found Hataları
**Belirtiler:**
- CSS selector'lar bulunamıyor
- Sayfa yapısı değişmiş

**Çözümler:**
```python
# Gelişmiş selector'ları kullan
enhanced_selectors = get_enhanced_selectors()
selectors = enhanced_selectors.get(domain, default_selectors)
```

### Hata İzleme
```python
from app import get_scraping_stats, analyze_and_suggest_fixes

# İstatistikleri al
stats = get_scraping_stats()
print(f"Başarı oranı: {stats['success_rate']:.1f}%")

# Hata analizi
analysis = analyze_and_suggest_fixes()
print(f"Öneriler: {analysis['suggestions']}")
```

## 📊 İzleme ve Raporlama

### API Endpoint'leri

#### 1. Scraping İstatistikleri
```bash
GET /api/scraping/stats
```
**Yanıt:**
```json
{
  "total_requests": 100,
  "successful_requests": 85,
  "failed_requests": 15,
  "success_rate": 85.0,
  "domain_stats": {
    "hepsiburada.com": {"success": 20, "failed": 2},
    "mango.com": {"success": 15, "failed": 8}
  }
}
```

#### 2. Sağlık Durumu
```bash
GET /api/scraping/health
```
**Yanıt:**
```json
{
  "status": "healthy",
  "success_rate": 85.0,
  "total_requests": 100,
  "recent_errors_count": 3
}
```

#### 3. Son Hatalar
```bash
GET /api/scraping/errors
```
**Yanıt:**
```json
{
  "errors": [
    {
      "timestamp": "2024-01-15T10:30:00",
      "url": "https://example.com",
      "domain": "example.com",
      "error": "Timeout error",
      "attempt": 2
    }
  ],
  "total_errors": 15
}
```

#### 4. İyileştirme Önerileri
```bash
GET /api/scraping/suggestions
```
**Yanıt:**
```json
{
  "error_analysis": {
    "timeout": 5,
    "bot_detection": 3
  },
  "suggestions": [
    "Sayfa yükleme süresini artırın",
    "Daha uzun bekleme süreleri ekleyin"
  ]
}
```

### Test Raporları
```bash
python test_improved_scraper.py
```

**Oluşturulan Dosyalar:**
- `test_report.json`: Detaylı test raporu
- `scraping.log`: Scraping logları

## 🔧 Sorun Giderme

### Yaygın Sorunlar ve Çözümleri

#### 1. Düşük Başarı Oranı
**Belirtiler:** %60'ın altında başarı oranı

**Çözümler:**
```python
# Rate limiting ayarlarını güncelle
RATE_LIMIT_PER_DOMAIN = 1  # Daha az istek
RATE_LIMIT_WINDOW = 120    # Daha uzun pencere

# Retry sayısını artır
result = await retry_scraping(url, max_retries=5, base_delay=3)
```

#### 2. Belirli Site'lerde Sorun
**Belirtiler:** Belirli domain'lerde sürekli hata

**Çözümler:**
```python
# Site-specific konfigürasyon ekle
SITE_CONFIGS["problematic-site.com"] = {
    "wait_time": 10000,  # 10 saniye bekle
    "timeout": 90000,    # 90 saniye timeout
    "retry_count": 5     # 5 kez dene
}
```

#### 3. Memory Sorunları
**Belirtiler:** Yüksek memory kullanımı

**Çözümler:**
```python
# Browser'ı düzenli olarak kapat
await browser.close()

# Cache'i temizle
scraping_cache.clear()
```

### Debug Modu
```python
# Debug loglarını aktifleştir
logging.basicConfig(level=logging.DEBUG)

# Detaylı hata bilgisi
try:
    result = await scrape_product(url)
except Exception as e:
    print(f"Detaylı hata: {e}")
    import traceback
    traceback.print_exc()
```

## 🎯 En İyi Uygulamalar

### 1. Rate Limiting
```python
# Her domain için uygun rate limit ayarla
RATE_LIMIT_PER_DOMAIN = {
    "hepsiburada.com": 2,
    "mango.com": 1,      # Bot koruması yüksek
    "sahibinden.com": 1  # Bot koruması yüksek
}
```

### 2. Error Handling
```python
# Hataları yakala ve logla
try:
    result = await scrape_product(url)
    if not result or result.get('name') == "İsim bulunamadı":
        # Alternatif yöntem dene
        result = await alternative_scraping_method(url)
except Exception as e:
    log_scraping_error(url, e)
    # Fallback sonuç döndür
    return get_fallback_result(url)
```

### 3. Monitoring
```python
# Düzenli sağlık kontrolü
def monitor_scraping_health():
    stats = get_scraping_stats()
    if stats['success_rate'] < 70:
        # Uyarı gönder
        send_alert(f"Düşük başarı oranı: {stats['success_rate']}%")
    
    # Problemli domain'leri raporla
    problematic_domains = get_problematic_domains(stats)
    if problematic_domains:
        send_report(problematic_domains)
```

### 4. Cache Yönetimi
```python
# Cache süresini ayarla
CACHE_DURATION = 3600  # 1 saat

# Cache'i düzenli temizle
def cleanup_cache():
    current_time = time.time()
    expired_keys = [
        key for key, (data, timestamp) in scraping_cache.items()
        if current_time - timestamp > CACHE_DURATION
    ]
    for key in expired_keys:
        del scraping_cache[key]
```

### 5. Site-Specific Optimizasyonlar
```python
# Her site için özel ayarlar
SITE_SPECIFIC_SETTINGS = {
    "mango.com": {
        "pre_navigation": True,  # Ana sayfaya önce git
        "cookie_handling": True, # Cookie banner'ı kabul et
        "human_behavior": True,  # İnsan benzeri davranış
        "wait_time": 5000        # 5 saniye bekle
    },
    "sahibinden.com": {
        "bot_protection_check": True,  # Bot koruması kontrolü
        "reload_on_error": True,       # Hata durumunda yeniden yükle
        "wait_time": 3000              # 3 saniye bekle
    }
}
```

## 📈 Performans İyileştirme

### 1. Parallel Processing
```python
# Birden fazla URL'yi paralel işle
async def scrape_multiple_urls(urls):
    tasks = [scrape_product(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### 2. Connection Pooling
```python
# Browser context'lerini yeniden kullan
browser_contexts = {}

async def get_or_create_context(domain):
    if domain not in browser_contexts:
        browser_contexts[domain] = await browser.new_context()
    return browser_contexts[domain]
```

### 3. Smart Caching
```python
# Akıllı cache stratejisi
def should_cache_result(result):
    return (
        result and 
        result.get('name') and 
        result.get('price') and
        result.get('name') != "İsim bulunamadı"
    )
```

## 🚨 Acil Durumlar

### 1. Tüm Scraping Başarısız
```python
# Emergency mode
EMERGENCY_MODE = True

if EMERGENCY_MODE:
    # Daha uzun bekleme süreleri
    RATE_LIMIT_PER_DOMAIN = 1
    RATE_LIMIT_WINDOW = 300  # 5 dakika
    
    # Daha fazla retry
    MAX_RETRIES = 5
    BASE_DELAY = 5
```

### 2. Belirli Site Tamamen Çalışmıyor
```python
# Site'yi geçici olarak devre dışı bırak
DISABLED_SITES = ["problematic-site.com"]

def is_site_disabled(url):
    domain = extract_domain_from_url(url)
    return domain in DISABLED_SITES
```

### 3. Memory Overflow
```python
# Memory temizleme
import gc

def emergency_cleanup():
    # Cache'i temizle
    scraping_cache.clear()
    
    # Browser'ları kapat
    for context in browser_contexts.values():
        await context.close()
    browser_contexts.clear()
    
    # Garbage collection
    gc.collect()
```

## 📞 Destek

### Log Dosyaları
- `scraping.log`: Ana scraping logları
- `test_report.json`: Test sonuçları
- `error_log.json`: Hata detayları

### Debug Komutları
```bash
# Test çalıştır
python test_improved_scraper.py

# Logları kontrol et
tail -f scraping.log

# İstatistikleri görüntüle
curl http://localhost:5000/api/scraping/stats
```

### İletişim
Sorun yaşadığınızda şu bilgileri paylaşın:
1. Hata mesajı
2. URL
3. Scraping logları
4. Test raporu
5. Sistem bilgileri

---

**Not:** Bu kılavuz sürekli güncellenmektedir. Yeni özellikler ve iyileştirmeler için düzenli olarak kontrol edin.
