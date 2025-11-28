# Scraping Modülü Entegrasyon Talimatları

Bu modül (`unified_scraper`), Nike, Bershka ve Decathlon ürünlerini tek bir arayüz üzerinden scrape etmek için tasarlanmıştır.

## Kurulum

1.  `unified_scraper` klasörünü hedef projenizin kök dizinine veya uygun bir alt klasöre (örn: `src/utils/scraper`) kopyalayın.
2.  Terminali açın ve kopyaladığınız `unified_scraper` klasörünün içine gidin:
    ```bash
    cd unified_scraper
    ```
3.  Gerekli bağımlılıkları yükleyin:
    ```bash
    npm install
    ```

## Kullanım

Hedef projenizdeki herhangi bir dosyadan modülü şu şekilde çağırabilirsiniz:

```javascript
const scraper = require('./unified_scraper'); // Klasör yolunuza göre düzenleyin

async function urunBilgisiGetir(url) {
    try {
        console.log(`Scraping başlatılıyor: ${url}`);
        const sonuc = await scraper.scrape(url);
        
        if (sonuc.error) {
            console.error("Hata oluştu:", sonuc.error);
        } else {
            console.log("Başarılı:", sonuc);
            // Burada veritabanına kayıt veya başka işlemler yapabilirsiniz
        }
    } catch (err) {
        console.error("Beklenmeyen hata:", err);
    }
}

// Örnek kullanım
// urunBilgisiGetir('https://www.nike.com/tr/t/ornek-urun-linki');
```

## Desteklenen Siteler

*   **Nike** (Fiyat, İsim, Resim)
*   **Bershka** (Fiyat, İsim, Resim, Açıklama, Stok Kodu)
*   **Decathlon** (Fiyat, İsim, Resim, İndirim Oranı)
*   **Diğerleri** (Genel meta etiketleri üzerinden temel bilgi)

## Notlar

*   Bu modül `puppeteer` ve `puppeteer-extra-plugin-stealth` kullanır. İlk çalıştırmada Chromium tarayıcısını indirebilir.
*   Sunucu ortamında (Ubuntu/Linux) çalıştıracaksanız `puppeteer` için ek sistem kütüphanelerine ihtiyaç duyabilirsiniz.
