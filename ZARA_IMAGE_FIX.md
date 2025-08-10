# Zara Görsel Çekme Sorunu Çözümü

## 🎯 Problem
Zara ürünlerinden görsel çekme işlemi başarısız oluyordu. Ana sorunlar:
- Bot koruması (Access Denied hatası)
- Eksik site-specific konfigürasyonlar
- Yetersiz görsel selector'ları
- Zara CDN görsellerine erişim sorunu

## ✅ Çözüm

### 1. Zara Site Konfigürasyonu Eklendi
`app.py` dosyasındaki `SITE_CONFIGS` bölümüne Zara için özel konfigürasyon eklendi:

```python
"zara.com": {
    "image_selectors": [
        "img[data-qa-action='product-image']",
        "img[data-testid='product-detail-image']",
        "img[data-testid='product-image']",
        "img.product-image",
        "img[class*='product'][class*='image']",
        "img[class*='main'][class*='image']",
        "img[class*='detail'][class*='image']",
        "img[loading='lazy']",
        "img[src*='static.zara.net']",
        "img[src*='zara.net']",
        "img[src*='zara.com']",
        "img[alt*='product']",
        "img[alt*='ürün']",
        "img[alt*='Zara']",
        "img[title*='product']",
        "img[title*='ürün']",
        "img[title*='Zara']",
        "img[srcset*='zara']",
        "img[srcset*='static.zara.net']",
        "img[decoding='async']",
        "img[data-nimg='1']",
        "img[style*='color:transparent']",
        "img[fetchpriority='high']",
        "img[loading='eager']"
    ],
    "price_selectors": [
        "span[data-qa-action='price-current']",
        "span[data-testid='price']",
        "span[data-testid='current-price']",
        "span.price-current",
        "span.current-price",
        # ... daha fazla selector
    ],
    "title_selectors": [
        "h1[data-qa-action='product-name']",
        "h1[data-testid='product-name']",
        "h1[data-testid='product-title']",
        "h1.product-name",
        "h1.product-title",
        # ... daha fazla selector
    ]
}
```

### 2. Gelişmiş Bot Koruması Aşma
Zara için özel navigation ve bot koruması aşma yöntemleri eklendi:

```python
elif "zara.com" in url:
    print(f"[DEBUG] Zara için gelişmiş bot koruması aşma başlıyor")
    
    # Zara ana sayfasına git ve cookie'leri kabul et
    await page.goto("https://www.zara.com/tr/", wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(5000)
    
    # Cookie banner'ını kabul et (varsa)
    try:
        cookie_button = await page.query_selector('button[data-testid="cookie-banner-accept"], button:has-text("Kabul"), button:has-text("Accept"), button:has-text("OK"), button:has-text("Aceptar"), button:has-text("Aceitar")')
        if cookie_button:
            await cookie_button.click()
            print(f"[DEBUG] Zara cookie banner kabul edildi")
            await page.wait_for_timeout(3000)
    except:
        pass
    
    # Sayfada biraz gezin
    await page.mouse.move(100, 100)
    await page.wait_for_timeout(1000)
    await page.mouse.move(200, 200)
    await page.wait_for_timeout(1000)
    
    # Scroll yap
    await page.evaluate("window.scrollTo(0, 500)")
    await page.wait_for_timeout(2000)
    await page.evaluate("window.scrollTo(0, 0)")
    await page.wait_for_timeout(1000)
    
    # Ek insan benzeri davranışlar
    await page.mouse.move(300, 300)
    await page.wait_for_timeout(500)
    await page.mouse.move(400, 400)
    await page.wait_for_timeout(500)
```

### 3. Zara Ürün Sayfası Navigasyonu
Ürün sayfasına gitme işlemi için özel konfigürasyon:

```python
elif "zara.com" in url:
    print(f"[DEBUG] Zara ürün sayfasına gidiliyor...")
    
    # Zara ürün sayfasına git
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_timeout(8000)  # Daha uzun bekleme
    
    # Sayfanın tam yüklenmesini bekle
    try:
        await page.wait_for_load_state("networkidle", timeout=30000)
    except:
        pass
    
    # Zara için ek insan benzeri davranışlar
    await page.mouse.move(300, 300)
    await page.wait_for_timeout(1000)
    
    # Sayfayı scroll et
    await page.evaluate("window.scrollTo(0, 300)")
    await page.wait_for_timeout(2000)
    await page.evaluate("window.scrollTo(0, 600)")
    await page.wait_for_timeout(2000)
    await page.evaluate("window.scrollTo(0, 0)")
    await page.wait_for_timeout(1000)
    
    # Bot koruması kontrolü
    try:
        page_title = await page.title()
        if "Access Denied" in page_title or "403" in page_title or "Forbidden" in page_title:
            print(f"[DEBUG] Zara bot koruması tespit edildi, daha uzun bekleniyor...")
            await page.wait_for_timeout(15000)  # 15 saniye daha bekle
            await page.reload()
            await page.wait_for_timeout(8000)
    except:
        pass
```

### 4. Zara Görsel Kalitesi Optimizasyonu
Zara CDN görsellerinin kalitesini artırmak için özel işlemler:

```python
# Zara için görsel kalitesini artır
if "zara.net" in src or "zara.com" in src:
    # Zara görselleri için kalite optimizasyonu
    if "static.zara.net" in src:
        # Mevcut parametreleri kontrol et ve yüksek kalite için güncelle
        if "w=" in src:
            # Genişliği artır
            src = re.sub(r'w=\d+', 'w=2000', src)
            print(f"[DEBUG] Zara görsel genişliği artırıldı: {src}")
        elif "h=" in src:
            # Yüksekliği artır
            src = re.sub(r'h=\d+', 'h=2000', src)
            print(f"[DEBUG] Zara görsel yüksekliği artırıldı: {src}")
        else:
            # Parametre yoksa ekle
            if "?" in src:
                src += "&w=2000&h=2000"
            else:
                src += "?w=2000&h=2000"
            print(f"[DEBUG] Zara görsel parametreleri eklendi: {src}")
    else:
        print(f"[DEBUG] Zara görsel mevcut kalite: {src}")
```

### 5. Enhanced Selectors Eklendi
`get_enhanced_selectors()` fonksiyonuna Zara için özel selector'lar eklendi:

```python
"zara.com": {
    "title_selectors": [
        'h1[data-qa-action="product-name"]',
        'h1[data-testid="product-name"]',
        'h1[data-testid="product-title"]',
        'h1.product-name',
        'h1.product-title',
        # ... daha fazla selector
    ],
    "price_selectors": [
        'span[data-qa-action="price-current"]',
        'span[data-testid="price"]',
        'span[data-testid="current-price"]',
        'span.price-current',
        'span.current-price',
        # ... daha fazla selector
    ],
    "image_selectors": [
        'img[data-qa-action="product-image"]',
        'img[data-testid="product-detail-image"]',
        'img[data-testid="product-image"]',
        'img.product-image',
        'img[class*="product"][class*="image"]',
        # ... daha fazla selector
    ]
}
```

## 🧪 Test

### Test Scripti
`test_zara_images.py` dosyası oluşturuldu:

```bash
python test_zara_images.py
```

Bu script:
- Zara konfigürasyonunu test eder
- 4 farklı Zara ürün URL'sini test eder
- Görsel çekme başarısını kontrol eder
- Görsel kalitesini doğrular

### Test URL'leri
```python
test_urls = [
    "https://www.zara.com/tr/tr/oversize-blazer-p04234543.html",
    "https://www.zara.com/tr/tr/kaykay-ayakkabisi-p12212520.html",
    "https://www.zara.com/tr/tr/bol-kesim-isci-tipi-jean-p01538478.html",
    "https://www.zara.com/tr/tr/rolyef-nakisli-gomlek-p02878304.html"
]
```

## 📊 Beklenen Sonuçlar

### ✅ Başarılı Durum
- Zara ürünlerinden görsel çekme başarılı
- Yüksek kaliteli görseller (2000x2000)
- Bot koruması aşıldı
- Cookie banner'ları otomatik kabul edildi

### ⚠️ Dikkat Edilecekler
- Zara'nın bot koruması sürekli güncelleniyor
- Bazen "Access Denied" hatası alınabilir
- Bu durumda daha uzun bekleme süreleri gerekebilir
- Proxy kullanımı gerekebilir

## 🔧 Ek İyileştirmeler

### 1. Proxy Desteği
Gelecekte proxy desteği eklenebilir:

```python
# Proxy konfigürasyonu
proxy_config = {
    "server": "proxy.example.com:8080",
    "username": "user",
    "password": "pass"
}

context = await browser.new_context(
    proxy=proxy_config,
    user_agent="...",
    # ... diğer ayarlar
)
```

### 2. Rotating User Agents
Farklı user agent'lar arasında geçiş:

```python
user_agents = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
]
```

### 3. Rate Limiting
Zara için özel rate limiting:

```python
# Zara için daha yavaş istekler
if "zara.com" in url:
    await asyncio.sleep(random.uniform(3, 7))  # 3-7 saniye arası rastgele bekleme
```

## 📝 Kullanım

### Manuel Test
```python
from app import scrape_product
import asyncio

async def test_zara():
    url = "https://www.zara.com/tr/tr/oversize-blazer-p04234543.html"
    result = await scrape_product(url)
    print(f"Başlık: {result.get('name')}")
    print(f"Fiyat: {result.get('price')}")
    print(f"Görsel: {result.get('image')}")

asyncio.run(test_zara())
```

### Web Arayüzü
Web arayüzünden Zara URL'si ekleyerek test edebilirsiniz.

## 🎯 Sonuç

Bu iyileştirmelerle Zara ürünlerinden görsel çekme işlemi büyük ölçüde iyileştirildi:

- ✅ Bot koruması aşma yöntemleri eklendi
- ✅ Zara-specific selector'lar eklendi
- ✅ Görsel kalitesi optimizasyonu yapıldı
- ✅ Test scripti oluşturuldu
- ✅ Kapsamlı dokümantasyon hazırlandı

Artık Zara ürünlerinden yüksek kaliteli görseller çekilebilir.
