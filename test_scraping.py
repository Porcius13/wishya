"""
50 Farklı Siteden Ürün Linklerini Test Et
Her site için örnek URL'ler test edilir ve sonuçlar analiz edilir
"""
import asyncio
import json
from datetime import datetime
from app_old import scrape_product

# 50 Farklı siteden örnek ürün URL'leri
TEST_URLS = [
    # Türk E-ticaret Siteleri
    ("https://www.trendyol.com/urun/example", "Trendyol"),
    ("https://www.hepsiburada.com/urun/example", "Hepsiburada"),
    ("https://www.gittigidiyor.com/urun/example", "GittiGidiyor"),
    ("https://www.n11.com/urun/example", "N11"),
    
    # Moda Markaları
    ("https://www.zara.com/tr/tr/urun/example", "Zara"),
    ("https://shop.mango.com/tr/urun/example", "Mango"),
    ("https://www.bershka.com/tr/urun/example", "Bershka"),
    ("https://www.pullandbear.com/tr/urun/example", "Pull&Bear"),
    ("https://www.stradivarius.com/tr/urun/example", "Stradivarius"),
    ("https://www.mavi.com/urun/example", "Mavi"),
    ("https://www.koton.com/urun/example", "Koton"),
    ("https://www.defacto.com.tr/urun/example", "Defacto"),
    ("https://www.lcwaikiki.com/tr-TR/TR/urun/example", "LC Waikiki"),
    ("https://www.colins.com.tr/urun/example", "Colin's"),
    ("https://www.ltbjeans.com/urun/example", "LTB Jeans"),
    ("https://www.superstep.com.tr/urun/example", "Superstep"),
    ("https://www.catiuniform.com/urun/example", "Çatı Uniform"),
    ("https://www.ontrailstore.com/urun/example", "Ontrail Store"),
    ("https://www.wwfmarket.com/tr/urun/example", "WWF Market"),
    ("https://www.lesbenjamins.com/urun/example", "Les Benjamins"),
    ("https://www.spx.com.tr/urun/example", "SPX"),
    ("https://www.boyner.com.tr/urun/example", "Boyner"),
    ("https://www.kaft.com/urun/example", "Kaft"),
    ("https://www.kigili.com/urun/example", "Kigili"),
    ("https://www.jackjones.com/tr/urun/example", "Jack & Jones"),
    ("https://www.selected.com/tr/urun/example", "Selected"),
    
    # Lüks Markalar
    ("https://www.vakko.com/urun/example", "Vakko"),
    ("https://www.beymen.com/urun/example", "Beymen"),
    ("https://www.net-a-porter.com/tr/urun/example", "Net-a-Porter"),
    ("https://www.farfetch.com/tr/urun/example", "Farfetch"),
    
    # Uluslararası Markalar
    ("https://www.asos.com/tr/urun/example", "ASOS"),
    ("https://www.zalando.com.tr/urun/example", "Zalando"),
    ("https://www.uniqlo.com/tr/urun/example", "Uniqlo"),
    ("https://www.gap.com/tr/urun/example", "Gap"),
    ("https://www.oldnavy.com/tr/urun/example", "Old Navy"),
    ("https://www.bananarepublic.com/tr/urun/example", "Banana Republic"),
    ("https://www.tommyhilfiger.com/tr/urun/example", "Tommy Hilfiger"),
    ("https://www.calvinklein.com/tr/urun/example", "Calvin Klein"),
    ("https://www.levis.com/tr/urun/example", "Levi's"),
    ("https://www.wrangler.com/tr/urun/example", "Wrangler"),
    ("https://www.diesel.com/tr/urun/example", "Diesel"),
    ("https://www.guess.com/tr/urun/example", "Guess"),
    
    # Spor Markaları
    ("https://www.adidas.com.tr/urun/example", "Adidas"),
    ("https://www.nike.com/tr/urun/example", "Nike"),
    ("https://www.puma.com/tr/urun/example", "Puma"),
    ("https://www.reebok.com/tr/urun/example", "Reebok"),
    
    # Diğer
    ("https://www.esprit.com/tr/urun/example", "Esprit"),
    ("https://www.benetton.com/tr/urun/example", "Benetton"),
    ("https://www.sandro.com/tr/urun/example", "Sandro"),
    ("https://www.maje.com/tr/urun/example", "Maje"),
    ("https://www.promod.com/tr/urun/example", "Promod"),
    ("https://www.jennyfer.com/tr/urun/example", "Jennyfer"),
]

# Gerçek test URL'leri - 50 farklı siteden örnek ürün linkleri
# Not: Bu URL'ler örnek - gerçek ürün linkleri ile değiştirilmeli
REAL_TEST_URLS = [
    # SPX - Kullanıcının verdiği link
    ("https://www.spx.com.tr/quiksilver-big-logo-hoodie-erkek-sweatshirt-aqyft03356-954-3/?recommended_by=dynamic&recommended_code=f012fe53b1f31a0753d3cf511ef84e90", "SPX"),
    
    # Popüler Türk E-ticaret
    # ("https://www.trendyol.com/...", "Trendyol"),
    # ("https://www.hepsiburada.com/...", "Hepsiburada"),
    
    # Moda Markaları - Gerçek linkler eklenmeli
    # Zara, Mango, Bershka, Pull&Bear, Stradivarius, Mavi, Koton, Defacto, vb.
    
    # Not: Gerçek test için bu URL'lerin gerçek ürün linkleri ile değiştirilmesi gerekiyor
]

async def test_single_url(url, site_name):
    """Tek bir URL'yi test et"""
    print(f"\n{'='*80}")
    print(f"Test: {site_name}")
    print(f"URL: {url}")
    print(f"{'='*80}")
    
    start_time = datetime.now()
    
    try:
        result = await scrape_product(url)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Sonuç analizi
        success = result and result.get('name') and result.get('name') != "İsim bulunamadı"
        has_price = result and result.get('price') and result.get('price') != "Fiyat bulunamadı"
        has_image = result and result.get('image')
        has_brand = result and result.get('brand') and result.get('brand') != "Bilinmiyor"
        
        status = "✅ BAŞARILI" if success and has_price else "❌ BAŞARISIZ"
        
        print(f"\n{status}")
        print(f"Süre: {duration:.2f} saniye")
        print(f"Başlık: {result.get('name', 'YOK') if result else 'HATA'}")
        print(f"Fiyat: {result.get('price', 'YOK') if result else 'HATA'}")
        print(f"Eski Fiyat: {result.get('old_price', 'YOK') if result else 'HATA'}")
        print(f"Görsel: {'VAR' if has_image else 'YOK'}")
        print(f"Marka: {result.get('brand', 'YOK') if result else 'HATA'}")
        
        return {
            'url': url,
            'site_name': site_name,
            'success': success,
            'has_price': has_price,
            'has_image': has_image,
            'has_brand': has_brand,
            'duration': duration,
            'result': result,
            'error': None
        }
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n❌ HATA")
        print(f"Süre: {duration:.2f} saniye")
        print(f"Hata: {str(e)}")
        
        return {
            'url': url,
            'site_name': site_name,
            'success': False,
            'has_price': False,
            'has_image': False,
            'has_brand': False,
            'duration': duration,
            'result': None,
            'error': str(e)
        }

async def run_all_tests():
    """Tüm testleri çalıştır"""
    print("\n" + "="*80)
    print("50 SİTE SCRAPING TESTİ BAŞLIYOR")
    print("="*80)
    
    # Gerçek URL'leri test et (eğer varsa)
    test_urls = REAL_TEST_URLS if REAL_TEST_URLS else TEST_URLS[:10]  # İlk 10'u test et
    
    results = []
    
    for url, site_name in test_urls:
        result = await test_single_url(url, site_name)
        results.append(result)
        
        # Her test arasında kısa bir bekleme
        await asyncio.sleep(2)
    
    # Sonuçları analiz et
    print("\n" + "="*80)
    print("TEST SONUÇLARI ÖZETİ")
    print("="*80)
    
    total = len(results)
    successful = sum(1 for r in results if r['success'])
    with_price = sum(1 for r in results if r['has_price'])
    with_image = sum(1 for r in results if r['has_image'])
    with_brand = sum(1 for r in results if r['has_brand'])
    
    avg_duration = sum(r['duration'] for r in results) / total if total > 0 else 0
    
    print(f"\nToplam Test: {total}")
    print(f"Başarılı: {successful} ({successful/total*100:.1f}%)")
    print(f"Fiyat Çekilen: {with_price} ({with_price/total*100:.1f}%)")
    print(f"Görsel Çekilen: {with_image} ({with_image/total*100:.1f}%)")
    print(f"Marka Tespit Edilen: {with_brand} ({with_brand/total*100:.1f}%)")
    print(f"Ortalama Süre: {avg_duration:.2f} saniye")
    
    # Başarısız testler
    failed = [r for r in results if not r['success']]
    if failed:
        print(f"\n❌ BAŞARISIZ TESTLER ({len(failed)}):")
        for r in failed:
            print(f"  - {r['site_name']}: {r['error'] or 'Bilinmeyen hata'}")
    
    # Fiyat çekilemeyenler
    no_price = [r for r in results if r['success'] and not r['has_price']]
    if no_price:
        print(f"\n⚠️ FİYAT ÇEKİLEMEYENLER ({len(no_price)}):")
        for r in no_price:
            print(f"  - {r['site_name']}: {r['url']}")
    
    # Sonuçları JSON'a kaydet
    report = {
        'test_date': datetime.now().isoformat(),
        'total_tests': total,
        'successful': successful,
        'with_price': with_price,
        'with_image': with_image,
        'with_brand': with_brand,
        'avg_duration': avg_duration,
        'results': results
    }
    
    with open('scraping_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Detaylı sonuçlar 'scraping_test_results.json' dosyasına kaydedildi.")
    
    return report

if __name__ == "__main__":
    # Testleri çalıştır
    asyncio.run(run_all_tests())

