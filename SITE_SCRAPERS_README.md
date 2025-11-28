# Site Spesifik Scraper'lar

Bu proje, verdiğiniz linkler için özel olarak tasarlanmış site spesifik web scraping sistemidir. Her site için özel selector'lar ve temizleme fonksiyonları içerir.

## 📋 Desteklenen Siteler

| Site | Domain | Durum |
|------|--------|-------|
| Beymen | beymen.com | ✅ |
| Ellesse | ellesse.com.tr | ✅ |
| Beyyoglu | beyyoglu.com | ✅ |
| Nine West | ninewest.com.tr | ✅ |
| Levi's | levis.com.tr | ✅ |
| Dockers | dockers.com.tr | ✅ |
| Sarar | sarar.com | ✅ |
| Salomon | salomon.com.tr | ✅ |
| Abercrombie | abercrombie.com | ✅ |
| Loft | loft.com.tr | ✅ |
| UCLA | ucla.com.tr | ✅ |
| Yargıcı | yargici.com | ✅ |

## 🚀 Kurulum

### Gereksinimler

```bash
pip install playwright
playwright install chromium
```

### Dosyalar

- `site_specific_scrapers.py` - Temel site spesifik scraper'lar
- `advanced_site_scrapers.py` - Gelişmiş scraper'lar (özel işleyiciler ile)
- `test_site_scrapers.py` - Test aracı

## 📖 Kullanım

### Temel Kullanım

```python
from site_specific_scrapers import SiteSpecificScrapers

async def main():
    scraper = SiteSpecificScrapers()
    
    url = "https://www.beymen.com/tr/p_polo-ralph-lauren-beyaz-oxford-gomlek_1646218"
    result = await scraper.scrape_product(url)
    
    print(f"Site: {result['site']}")
    print(f"Başlık: {result['title']}")
    print(f"Güncel Fiyat: {result['current_price']}")
    print(f"Eski Fiyat: {result['original_price']}")
    print(f"Resim: {result['image_url']}")

# Çalıştır
import asyncio
asyncio.run(main())
```

### Gelişmiş Kullanım

```python
from advanced_site_scrapers import AdvancedSiteScrapers

async def main():
    scraper = AdvancedSiteScrapers()
    
    url = "https://www.ellesse.com.tr/products/ellesse-erkek-polo-yaka-tisort-em460-bk"
    result = await scraper.scrape_product(url)
    
    if "error" not in result:
        print(f"✅ Başarılı: {result}")
    else:
        print(f"❌ Hata: {result['error']}")

# Çalıştır
import asyncio
asyncio.run(main())
```

## 🧪 Test Etme

### Tüm Siteleri Test Et

```bash
python test_site_scrapers.py
```

### Tek URL Test Et

```bash
python test_site_scrapers.py "https://www.beymen.com/tr/p_polo-ralph-lauren-beyaz-oxford-gomlek_1646218"
```

### Yardım

```bash
python test_site_scrapers.py --help
```

## 📊 Test Sonuçları

Test sonuçları JSON dosyalarına kaydedilir:

- `basic_scraping_results.json` - Temel scraper sonuçları
- `advanced_scraping_results.json` - Gelişmiş scraper sonuçları

## 🔧 Site Konfigürasyonları

Her site için özel konfigürasyon:

### Beymen
```python
"beymen.com": {
    "name": "Beymen",
    "selectors": {
        "title": ["span.o-productDetail__description"],
        "current_price": ["ins#priceNew.m-price__new"],
        "original_price": ["del#priceOld.m-price__old"],
        "image": ["img.m-productDetailImage__item"]
    },
    "price_cleaner": self._clean_beymen_price,
    "wait_time": 2000,
    "timeout": 30000
}
```

### Ellesse
```python
"ellesse.com.tr": {
    "name": "Ellesse",
    "selectors": {
        "title": ["h1.product__title.h4"],
        "current_price": ["span.price-item.price-item--sale.price-item--last"],
        "original_price": ["s.price-item.price-item--regular"],
        "image": ["img[src*='cdn.shop/files']"]
    },
    "price_cleaner": self._clean_ellesse_price,
    "wait_time": 2000,
    "timeout": 30000
}
```

## 🛠️ Özellikler

### Temel Scraper
- ✅ Site spesifik selector'lar
- ✅ Fiyat temizleme fonksiyonları
- ✅ Hata yönetimi
- ✅ Rate limiting

### Gelişmiş Scraper
- ✅ Tüm temel özellikler
- ✅ Özel işleyiciler (cookie banner kapatma, sayfa bekleme)
- ✅ User agent ayarları
- ✅ Gelişmiş hata yönetimi
- ✅ Fallback mekanizmaları

## 📝 Örnek Çıktı

```json
{
  "url": "https://www.beymen.com/tr/p_polo-ralph-lauren-beyaz-oxford-gomlek_1646218",
  "site": "Beymen",
  "title": "Beyaz Oxford Gömlek",
  "current_price": "6.095",
  "original_price": "7.750",
  "image_url": "https://cdn.beymen.com/mnresize/596/830/productimages/rmz5juiz.wrw_IMG_01_2110099651101.jpg"
}
```

## 🔍 Hata Yönetimi

Scraper'lar şu durumları yönetir:

- ✅ Site bulunamadı
- ✅ Selector bulunamadı
- ✅ Sayfa yüklenme hatası
- ✅ Timeout hataları
- ✅ Network hataları

## 🚨 Önemli Notlar

1. **Rate Limiting**: Siteler arasında 1-2 saniye bekleme süresi
2. **User Agent**: Gerçekçi browser user agent kullanılır
3. **Timeout**: Her site için 30 saniye timeout
4. **Headless Mode**: Tarayıcı headless modda çalışır

## 🔧 Özelleştirme

### Yeni Site Ekleme

```python
"yeni-site.com": {
    "name": "Yeni Site",
    "selectors": {
        "title": ["h1.product-title"],
        "current_price": ["span.current-price"],
        "original_price": ["span.original-price"],
        "image": ["img.product-image"]
    },
    "price_cleaner": self._clean_yeni_site_price,
    "special_handlers": [self._handle_yeni_site_special],
    "wait_time": 2000,
    "timeout": 30000
}
```

### Özel İşleyici Ekleme

```python
async def _handle_yeni_site_special(self, page):
    """Yeni site için özel işlemler"""
    try:
        # Cookie banner'ı kapat
        await page.click("button[class*='cookie']", timeout=5000)
    except:
        pass
```

## 📞 Destek

Herhangi bir sorun yaşarsanız:

1. Test dosyasını çalıştırın
2. Hata mesajlarını kontrol edin
3. Site selector'larını güncelleyin
4. Gerekirse yeni özel işleyici ekleyin

## 📄 Lisans

Bu proje eğitim amaçlı oluşturulmuştur. Ticari kullanım için gerekli izinleri almayı unutmayın.
