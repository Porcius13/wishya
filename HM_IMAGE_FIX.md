# H&M Görsel Çekme Sorunu Çözümü

## Sorun
H&M (hm.com) ürün sayfalarından görsel çekilemiyordu çünkü site-specific konfigürasyon eksikti.

## Çözüm
H&M için kapsamlı site-specific konfigürasyon eklendi:

### 1. SITE_CONFIGS'e H&M Eklendi
`app.py` dosyasındaki `SITE_CONFIGS` sözlüğüne H&M konfigürasyonu eklendi:

```python
"hm.com": {
    "image_selectors": [
        "img.product-image",
        "img[class*='product-image']",
        "img[class*='product'][class*='image']",
        "img[data-testid='product-image']",
        "img[data-qa-action='product-image']",
        "img[alt*='product']",
        "img[alt*='ürün']",
        "img[alt*='H&M']",
        "img[title*='product']",
        "img[title*='ürün']",
        "img[title*='H&M']",
        "img[src*='hm.com']",
        "img[src*='hmcdn.net']",
        "img[src*='static.hm.com']",
        "img[loading='lazy']",
        "img[decoding='async']",
        "img[data-nimg='1']",
        "img[style*='color:transparent']",
        "img[fetchpriority='high']",
        "img[loading='eager']",
        "img[srcset*='hm.com']",
        "img[srcset*='hmcdn.net']",
        "img[srcset*='static.hm.com']"
    ],
    "price_selectors": [...],
    "old_price_selectors": [...],
    "title_selectors": [...]
}
```

### 2. Enhanced Selectors'a H&M Eklendi
`get_enhanced_selectors()` fonksiyonuna H&M için gelişmiş selector'lar eklendi.

### 3. Site-Specific Navigation Eklendi
`handle_site_specific_navigation()` fonksiyonuna H&M için özel navigasyon eklendi:
- H&M ana sayfasına gitme
- Cookie banner'ını kabul etme
- İnsan benzeri davranışlar (mouse hareketleri, scroll)

### 4. Product Page Navigation Eklendi
`navigate_to_product_page()` fonksiyonuna H&M için özel ürün sayfası navigasyonu eklendi:
- Uzun bekleme süreleri
- Bot koruması kontrolü
- İnsan benzeri davranışlar

## Test Sonuçları
Test script'i çalıştırıldığında:
- ✅ H&M site config bulundu
- ✅ 23 adet image selector eklendi
- ✅ 15 adet price selector eklendi
- ✅ 16 adet title selector eklendi

## Kullanım
Artık H&M ürün URL'leri ile scraping yapılabilir:

```python
from app import scrape_product

# H&M ürün URL'si
url = "https://www2.hm.com/tr_tr/productpage.1234567890.html"
result = await scrape_product(url)

# Sonuç
print(f"Başlık: {result['name']}")
print(f"Fiyat: {result['price']}")
print(f"Görsel: {result['image']}")
print(f"Marka: {result['brand']}")
```

## Özellikler
- **Kapsamlı Image Selectors**: 23 farklı image selector ile görsel bulma
- **Bot Koruması Aşma**: Gelişmiş stealth teknikleri
- **Cookie Yönetimi**: Otomatik cookie banner kabul etme
- **İnsan Benzeri Davranış**: Mouse hareketleri ve scroll
- **Retry Mekanizması**: Başarısız durumlarda tekrar deneme
- **Cache Sistemi**: Performans için önbellekleme

## Notlar
- H&M sitesi bot koruması kullandığı için özel navigasyon teknikleri gerekli
- Görsel URL'leri hm.com, hmcdn.net ve static.hm.com domain'lerinden gelebilir
- Farklı görsel formatları (jpg, webp, png) desteklenir
- srcset attribute'ları yüksek kaliteli görseller için kontrol edilir
