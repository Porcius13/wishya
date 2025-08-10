# Evrensel Scraper Kullanım Kılavuzu

## 🚀 Genel Bakış

`UniversalScraper` sınıfı, farklı e-ticaret sitelerinden ürün verilerini otomatik olarak çekmek için tasarlanmış güçlü bir araçtır. Mevcut başarılı scraping deneyimlerini analiz ederek oluşturulmuştur.

## ✨ Özellikler

- **Akıllı Site Tespiti**: URL'den otomatik site tespiti
- **Fallback Mekanizmaları**: Birden fazla selector deneme
- **Hata Toleransı**: Başarısız denemelerde alternatif yöntemler
- **Genişletilebilir Yapı**: Yeni siteler kolayca eklenebilir
- **Performans Optimizasyonu**: Gereksiz bekleme süreleri minimize edilmiş
- **Marka Tespiti**: Otomatik marka tespiti (teknoloji, araba, moda)
- **Görsel Kalitesi**: Otomatik görsel kalitesi artırma

## 📦 Kurulum

```bash
pip install playwright
playwright install chromium
```

## 🔧 Temel Kullanım

### Basit Kullanım

```python
from universal_scraper import UniversalScraper

# Scraper oluştur
scraper = UniversalScraper()

# Tek ürün çek
url = "https://www.hepsiburada.com/product-url"
result = scraper.scrape_product_sync(url)

if result:
    print(f"Başlık: {result['title']}")
    print(f"Fiyat: {result['price']}")
    print(f"Marka: {result['brand']}")
    print(f"Görsel: {result['image']}")
    print(f"Site: {result['site']}")
```

### Asenkron Kullanım

```python
import asyncio
from universal_scraper import UniversalScraper

async def main():
    scraper = UniversalScraper()
    
    # Tek ürün
    result = await scraper.scrape_product(url)
    
    # Birden fazla ürün
    urls = ["url1", "url2", "url3"]
    results = await scraper.scrape_multiple_products(urls)

asyncio.run(main())
```

## 🛠️ Gelişmiş Kullanım

### Yeni Site Konfigürasyonu Ekleme

```python
scraper = UniversalScraper()

# Yeni site konfigürasyonu
new_config = {
    "name": "Yeni Site",
    "selectors": {
        "title": ["h1", ".product-title", "[data-testid='title']"],
        "price": [".price", "span[class*='price']", "[data-testid='price']"],
        "image": ["img[class*='product']", "img[src*='product']", "img"]
    },
    "price_cleaner": scraper._clean_general_price,
    "image_enhancer": scraper._enhance_general_image,
    "brand_detector": scraper._detect_general_brands,
    "wait_time": 3000,
    "timeout": 45000
}

# Konfigürasyonu ekle
scraper.add_site_config("yeni-site.com", new_config)
```

### Konfigürasyon Kaydetme ve Yükleme

```python
# Konfigürasyonları kaydet
scraper.save_configs("my_configs.json")

# Yeni scraper oluştur ve konfigürasyonları yükle
new_scraper = UniversalScraper()
new_scraper.load_configs("my_configs.json")
```

### Özel Fiyat Temizleme Fonksiyonu

```python
def custom_price_cleaner(price_text):
    """Özel fiyat temizleme fonksiyonu"""
    if not price_text:
        return ""
    
    # Özel temizleme mantığı
    price_clean = re.sub(r'[^\d.,]', '', price_text)
    price_clean = price_clean.replace(',', '.')
    
    return price_clean

# Konfigürasyona ekle
config["price_cleaner"] = custom_price_cleaner
```

## 📊 Desteklenen Siteler

### Mevcut Konfigürasyonlar

1. **Hepsiburada** (`hepsiburada.com`)
   - Teknoloji ürünleri
   - İndirimli/indirimsiz fiyat desteği
   - Görsel kalitesi optimizasyonu

2. **Sahibinden** (`sahibinden.com`)
   - Araç ilanları
   - Detaylı ürün bilgileri
   - Çoklu görsel desteği

3. **Zara** (`zara.com`)
   - Moda ürünleri
   - Uluslararası fiyat desteği

4. **Mango** (`mango.com`)
   - Moda ürünleri
   - Çoklu dil desteği

5. **H&M** (`hm.com`)
   - Moda ürünleri
   - Global site desteği

### Bilinmeyen Siteler

Bilinmeyen siteler için otomatik genel selector'lar kullanılır:
- Akıllı başlık arama
- Para birimi bazlı fiyat arama
- Ürün görseli tespiti

## 🎯 Marka Tespiti

### Desteklenen Marka Kategorileri

1. **Teknoloji Markaları**
   - Apple, Samsung, Xiaomi, Huawei, vb.
   - Bilgisayar parçaları (Intel, AMD, NVIDIA, vb.)
   - Aksesuarlar (Logitech, Razer, vb.)

2. **Araba Markaları**
   - Lada, BMW, Mercedes, Audi, vb.
   - Türk ve uluslararası markalar

3. **Moda Markaları**
   - Zara, Mango, H&M, vb.
   - Lüks markalar (Gucci, Prada, vb.)

## ⚙️ Konfigürasyon Parametreleri

### Site Konfigürasyonu Yapısı

```python
{
    "name": "Site Adı",
    "selectors": {
        "title": ["selector1", "selector2", "selector3"],
        "price": ["price_selector1", "price_selector2"],
        "image": ["image_selector1", "image_selector2"],
        "original_price": ["original_price_selector"],  # Opsiyonel
        "description": ["description_selector"]  # Opsiyonel
    },
    "price_cleaner": function,  # Fiyat temizleme fonksiyonu
    "image_enhancer": function,  # Görsel kalitesi artırma fonksiyonu
    "brand_detector": function,  # Marka tespit fonksiyonu
    "wait_time": 3000,  # Sayfa yükleme bekleme süresi (ms)
    "timeout": 45000    # Maksimum timeout süresi (ms)
}
```

### Selector Stratejileri

1. **Spesifik Selector'lar**: Site özel selector'lar
2. **Genel Selector'lar**: Bilinmeyen siteler için
3. **Akıllı Arama**: Otomatik element tespiti

## 🔍 Hata Yönetimi

### Retry Mekanizması

```python
# Varsayılan: 3 deneme
result = scraper.scrape_product_sync(url, max_retries=3)

# Özel deneme sayısı
result = scraper.scrape_product_sync(url, max_retries=5)
```

### Hata Türleri

1. **Network Hatası**: Bağlantı sorunları
2. **Selector Hatası**: Element bulunamadı
3. **Timeout Hatası**: Sayfa yükleme zaman aşımı
4. **Rate Limiting**: Çok fazla istek

## 📈 Performans Optimizasyonu

### Tarayıcı Optimizasyonları

- Görsel ve CSS dosyaları engellenir
- GPU hızlandırma devre dışı
- Sandbox güvenlik ayarları
- Bellek kullanımı optimize edilmiş

### Rate Limiting

```python
# Otomatik rate limiting
results = await scraper.scrape_multiple_products(urls)

# Manuel bekleme
import time
for url in urls:
    result = scraper.scrape_product_sync(url)
    time.sleep(2)  # 2 saniye bekle
```

## 🧪 Test Etme

### Test Dosyası Çalıştırma

```bash
python test_universal_scraper.py
```

### Özel Test

```python
from universal_scraper import UniversalScraper

scraper = UniversalScraper()

# Test URL'leri
test_urls = [
    "https://www.hepsiburada.com/product1",
    "https://www.sahibinden.com/ilan1",
    "https://www.zara.com/product1"
]

# Test et
for url in test_urls:
    result = scraper.scrape_product_sync(url)
    print(f"URL: {url}")
    print(f"Başarılı: {result is not None}")
    if result:
        print(f"Site: {result['site']}")
        print(f"Başlık: {result['title'][:50]}...")
```

## 🔧 Sorun Giderme

### Yaygın Sorunlar

1. **Element Bulunamadı**
   - Selector'ları güncelleyin
   - Sayfa yapısı değişmiş olabilir
   - Akıllı arama kullanın

2. **Yavaş Performans**
   - Timeout değerlerini artırın
   - Rate limiting ekleyin
   - Görsel yüklemeyi devre dışı bırakın

3. **Hatalı Veri**
   - Fiyat temizleme fonksiyonunu kontrol edin
   - Marka tespitini doğrulayın
   - Selector'ları test edin

### Debug Modu

```python
import logging
logging.basicConfig(level=logging.DEBUG)

scraper = UniversalScraper()
result = scraper.scrape_product_sync(url)
```

## 📝 Örnek Kullanım Senaryoları

### Senaryo 1: E-ticaret Fiyat Takibi

```python
scraper = UniversalScraper()

# Ürün listesi
products = [
    "https://www.hepsiburada.com/product1",
    "https://www.sahibinden.com/product2",
    "https://www.zara.com/product3"
]

# Fiyatları kontrol et
for url in products:
    result = scraper.scrape_product_sync(url)
    if result:
        print(f"{result['title']}: {result['price']} TL")
```

### Senaryo 2: Marka Analizi

```python
scraper = UniversalScraper()

# Farklı sitelerden aynı marka ürünleri
brand_urls = [
    "https://site1.com/apple-iphone",
    "https://site2.com/apple-iphone",
    "https://site3.com/apple-iphone"
]

# Marka karşılaştırması
for url in brand_urls:
    result = scraper.scrape_product_sync(url)
    if result and result['brand'] == 'APPLE':
        print(f"{result['site']}: {result['price']}")
```

### Senaryo 3: Yeni Site Entegrasyonu

```python
scraper = UniversalScraper()

# Yeni site için test
test_url = "https://yeni-site.com/product/123"

# Önce genel selector'larla test et
result = scraper.scrape_product_sync(test_url)

if result:
    print("Genel selector'lar çalışıyor!")
    
    # Özel konfigürasyon ekle
    custom_config = {
        "name": "Yeni Site",
        "selectors": {
            "title": ["h1.product-title"],
            "price": [".product-price"],
            "image": ["img.product-image"]
        },
        "price_cleaner": scraper._clean_general_price,
        "image_enhancer": scraper._enhance_general_image,
        "brand_detector": scraper._detect_general_brands,
        "wait_time": 2000,
        "timeout": 30000
    }
    
    scraper.add_site_config("yeni-site.com", custom_config)
    scraper.save_configs()
```

## 📚 API Referansı

### UniversalScraper Sınıfı

#### Metodlar

- `scrape_product(url, max_retries=3)`: Asenkron ürün çekme
- `scrape_product_sync(url, max_retries=3)`: Senkron ürün çekme
- `scrape_multiple_products(urls, max_retries=3)`: Toplu ürün çekme
- `add_site_config(domain, config)`: Yeni site konfigürasyonu ekleme
- `save_configs(filename)`: Konfigürasyonları kaydetme
- `load_configs(filename)`: Konfigürasyonları yükleme

#### Dönen Veri Yapısı

```python
{
    "title": "Ürün Başlığı",
    "price": "123.45",
    "image": "https://example.com/image.jpg",
    "brand": "MARKA_ADI",
    "url": "https://example.com/product",
    "site": "Site Adı",
    "scraped_at": "2024-01-01 12:00:00",
    "original_price": "150.00"  # Opsiyonel (Hepsiburada)
}
```

## 🤝 Katkıda Bulunma

1. Yeni site konfigürasyonları ekleyin
2. Selector'ları güncelleyin
3. Test senaryoları ekleyin
4. Performans iyileştirmeleri yapın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.
