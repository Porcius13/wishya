# Render Üzerinde Görsel Çekme Sorunları Çözümü

## Sorun
Render üzerinde hiçbir linkten görsel çekilemiyor. Bu genellikle şu sebeplerden kaynaklanır:

1. **Headless environment**: Render'da browser tam olarak yüklenmemiş
2. **Görsel yükleme zamanlaması**: Görseller henüz yüklenmeden çekilmeye çalışılıyor
3. **Selector uyumsuzluğu**: Site yapısı değişmiş olabilir
4. **Network sorunları**: Render'da network bağlantısı sorunları

## Yapılan İyileştirmeler

### 1. Görsel Çekme Fonksiyonu Optimizasyonu
- Daha uzun bekleme süreleri (3-5 saniye)
- Daha fazla selector eklendi
- Detaylı debug logları
- Alternatif görsel çekme yöntemi

### 2. Sayfa Yükleme İyileştirmeleri
- Network idle durumu bekleme
- Scroll işlemleri eklendi
- Mouse hareketleri eklendi
- Site-specific navigation

### 3. Browser Ayarları
- Render için optimize edilmiş browser argümanları
- Gelişmiş stealth script
- Mobile user agent kullanımı

### 4. Debug Araçları
- `render_debug.py` script'i eklendi
- Debug endpoint'i eklendi (`/api/debug/scrape`)
- Detaylı log sistemi

## Test Etme

### 1. Debug Script Kullanımı
```bash
python render_debug.py "https://example.com/product-url"
```

Bu script:
- Sayfadaki tüm görselleri analiz eder
- HTML içeriğini kaydeder
- Screenshot alır
- JSON raporu oluşturur

### 2. Debug Endpoint Kullanımı
```bash
curl -X POST https://your-app.onrender.com/api/debug/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/product-url"}'
```

### 3. Log Kontrolü
Render dashboard'unda logları kontrol edin:
- `[DEBUG]` mesajlarını arayın
- Görsel çekme sürecini takip edin
- Hata mesajlarını inceleyin

## Sorun Giderme

### Görsel Bulunamıyorsa:
1. **Debug script çalıştırın**: `python render_debug.py <URL>`
2. **HTML içeriğini kontrol edin**: `debug_page.html` dosyasını inceleyin
3. **Screenshot'ı kontrol edin**: `debug_screenshot.png` dosyasını inceleyin
4. **JSON raporunu inceleyin**: `debug_result.json` dosyasını kontrol edin

### Yaygın Sorunlar:

#### 1. "Hiç img elementi bulunamadı"
- Sayfa JavaScript ile yükleniyor olabilir
- Bot koruması aktif olabilir
- Network bağlantısı sorunu olabilir

**Çözüm:**
- Daha uzun bekleme süreleri ekleyin
- JavaScript'in yüklenmesini bekleyin
- User agent'ı değiştirin

#### 2. "Görseller çok küçük"
- Logo/icon görselleri çekiliyor olabilir
- Boyut filtreleme çok katı olabilir

**Çözüm:**
- Boyut eşiğini düşürün (100x100 yerine 50x50)
- Daha fazla selector ekleyin

#### 3. "Network timeout"
- Render'da network yavaş olabilir
- Site yavaş yükleniyor olabilir

**Çözüm:**
- Timeout sürelerini artırın
- Retry mekanizması ekleyin

## Önerilen Test URL'leri

Farklı siteleri test edin:
- H&M: `https://www2.hm.com/tr_tr/productpage.1234567890.html`
- Zara: `https://www.zara.com/tr/tr/product/1234567890.html`
- Mango: `https://shop.mango.com/tr/kadin/elbiseler/1234567890.html`

## Monitoring

### Başarı Oranını İzleyin:
```bash
curl https://your-app.onrender.com/api/scraping/stats
```

### Son Hataları Kontrol Edin:
```bash
curl https://your-app.onrender.com/api/scraping/errors
```

## Ek Optimizasyonlar

### 1. Cache Sistemi
- Başarılı scraping sonuçlarını cache'leyin
- Aynı URL'yi tekrar çekmeyin

### 2. Rate Limiting
- Site bazında rate limiting uygulayın
- Çok sık istek göndermeyin

### 3. Fallback Yöntemler
- Birincil yöntem başarısız olursa alternatif yöntemler deneyin
- Farklı selector'lar kullanın

## Sonuç

Bu iyileştirmelerle Render üzerinde görsel çekme sorunları büyük ölçüde çözülmüş olmalı. Eğer hala sorun yaşıyorsanız:

1. Debug script'i çalıştırın
2. Logları detaylı inceleyin
3. Farklı siteleri test edin
4. Gerekirse daha fazla optimizasyon yapın
