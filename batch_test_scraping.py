"""
50 Farklı Siteden Ürün Linklerini Toplu Test Et
Gerçek ürün linkleri ile test yapar ve sonuçları analiz eder
"""
import asyncio
import json
import sys
from datetime import datetime
from app_old import scrape_product

# 50 Farklı siteden gerçek ürün URL'leri
# Bu URL'ler gerçek ürün linkleri ile doldurulmalı
TEST_URLS = [
    # SPX - Kullanıcının verdiği link
    ("https://www.spx.com.tr/quiksilver-big-logo-hoodie-erkek-sweatshirt-aqyft03356-954-3/?recommended_by=dynamic&recommended_code=f012fe53b1f31a0753d3cf511ef84e90", "SPX"),
    
    # Buraya 49 tane daha gerçek ürün linki eklenebilir
    # Format: ("URL", "Site Adı")
]

async def test_single_url(url, site_name, index, total):
    """Tek bir URL'yi test et"""
    print(f"\n{'='*80}")
    print(f"[{index}/{total}] Test: {site_name}")
    print(f"URL: {url[:80]}...")
    print(f"{'='*80}")
    
    start_time = datetime.now()
    
    try:
        result = await scrape_product(url)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Sonuç analizi
        success = result and result.get('name') and result.get('name') != "İsim bulunamadı" and result.get('name') != "Scraping hatası - Lütfen URL'yi kontrol edin"
        has_price = result and result.get('price') and result.get('price') != "Fiyat bulunamadı"
        has_image = result and result.get('image')
        has_brand = result and result.get('brand') and result.get('brand') != "Bilinmiyor"
        
        # Fiyat format kontrolü
        price_valid = False
        if has_price:
            price_str = str(result.get('price', ''))
            # Fiyat formatı kontrolü (sayı içermeli)
            import re
            if re.search(r'\d', price_str):
                price_valid = True
        
        status = "✅ BAŞARILI" if success and has_price and price_valid else "❌ BAŞARISIZ"
        
        print(f"\n{status}")
        print(f"Süre: {duration:.2f} saniye")
        print(f"Başlık: {result.get('name', 'YOK')[:60] if result else 'HATA'}...")
        print(f"Fiyat: {result.get('price', 'YOK') if result else 'HATA'}")
        print(f"Eski Fiyat: {result.get('old_price', 'YOK') if result else 'HATA'}")
        print(f"Görsel: {'VAR' if has_image else 'YOK'}")
        print(f"Marka: {result.get('brand', 'YOK') if result else 'HATA'}")
        
        # Fiyat doğrulama
        if has_price and not price_valid:
            print(f"⚠️ UYARI: Fiyat formatı geçersiz: {result.get('price')}")
        
        return {
            'url': url,
            'site_name': site_name,
            'success': success,
            'has_price': has_price,
            'price_valid': price_valid,
            'has_image': has_image,
            'has_brand': has_brand,
            'duration': duration,
            'name': result.get('name') if result else None,
            'price': result.get('price') if result else None,
            'old_price': result.get('old_price') if result else None,
            'image': result.get('image') if result else None,
            'brand': result.get('brand') if result else None,
            'error': None
        }
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n❌ HATA")
        print(f"Süre: {duration:.2f} saniye")
        print(f"Hata: {str(e)[:100]}")
        
        return {
            'url': url,
            'site_name': site_name,
            'success': False,
            'has_price': False,
            'price_valid': False,
            'has_image': False,
            'has_brand': False,
            'duration': duration,
            'name': None,
            'price': None,
            'old_price': None,
            'image': None,
            'brand': None,
            'error': str(e)
        }

async def run_batch_tests():
    """Tüm testleri çalıştır"""
    print("\n" + "="*80)
    print("50 SİTE SCRAPING TESTİ BAŞLIYOR")
    print("="*80)
    print(f"Toplam Test: {len(TEST_URLS)}")
    print("="*80)
    
    if not TEST_URLS:
        print("⚠️ UYARI: Test URL'leri boş! Lütfen TEST_URLS listesine gerçek ürün linkleri ekleyin.")
        return None
    
    results = []
    
    for index, (url, site_name) in enumerate(TEST_URLS, 1):
        result = await test_single_url(url, site_name, index, len(TEST_URLS))
        results.append(result)
        
        # Her test arasında kısa bir bekleme (rate limiting)
        if index < len(TEST_URLS):
            await asyncio.sleep(3)
    
    # Sonuçları analiz et
    print("\n" + "="*80)
    print("TEST SONUÇLARI ÖZETİ")
    print("="*80)
    
    total = len(results)
    successful = sum(1 for r in results if r['success'])
    with_price = sum(1 for r in results if r['has_price'])
    price_valid = sum(1 for r in results if r['price_valid'])
    with_image = sum(1 for r in results if r['has_image'])
    with_brand = sum(1 for r in results if r['has_brand'])
    
    avg_duration = sum(r['duration'] for r in results) / total if total > 0 else 0
    total_duration = sum(r['duration'] for r in results)
    
    print(f"\n📊 GENEL İSTATİSTİKLER:")
    print(f"  Toplam Test: {total}")
    print(f"  Başarılı: {successful} ({successful/total*100:.1f}%)")
    print(f"  Fiyat Çekilen: {with_price} ({with_price/total*100:.1f}%)")
    print(f"  Geçerli Fiyat: {price_valid} ({price_valid/total*100:.1f}%)")
    print(f"  Görsel Çekilen: {with_image} ({with_image/total*100:.1f}%)")
    print(f"  Marka Tespit Edilen: {with_brand} ({with_brand/total*100:.1f}%)")
    print(f"  Ortalama Süre: {avg_duration:.2f} saniye")
    print(f"  Toplam Süre: {total_duration/60:.2f} dakika")
    
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
            print(f"  - {r['site_name']}: {r['url'][:60]}...")
    
    # Geçersiz fiyat formatı
    invalid_price = [r for r in results if r['has_price'] and not r['price_valid']]
    if invalid_price:
        print(f"\n⚠️ GEÇERSİZ FİYAT FORMATI ({len(invalid_price)}):")
        for r in invalid_price:
            print(f"  - {r['site_name']}: '{r['price']}'")
    
    # Site bazlı başarı oranları
    site_stats = {}
    for r in results:
        site = r['site_name']
        if site not in site_stats:
            site_stats[site] = {'total': 0, 'success': 0, 'with_price': 0}
        site_stats[site]['total'] += 1
        if r['success']:
            site_stats[site]['success'] += 1
        if r['has_price']:
            site_stats[site]['with_price'] += 1
    
    print(f"\n📈 SİTE BAZLI İSTATİSTİKLER:")
    for site, stats in sorted(site_stats.items()):
        success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
        price_rate = (stats['with_price'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  {site}: {stats['success']}/{stats['total']} başarılı ({success_rate:.1f}%), {stats['with_price']}/{stats['total']} fiyat ({price_rate:.1f}%)")
    
    # Sonuçları JSON'a kaydet
    report = {
        'test_date': datetime.now().isoformat(),
        'total_tests': total,
        'successful': successful,
        'with_price': with_price,
        'price_valid': price_valid,
        'with_image': with_image,
        'with_brand': with_brand,
        'avg_duration': avg_duration,
        'total_duration': total_duration,
        'site_stats': site_stats,
        'results': results
    }
    
    filename = f'scraping_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Detaylı sonuçlar '{filename}' dosyasına kaydedildi.")
    
    return report

if __name__ == "__main__":
    print("50 Site Scraping Test Aracı")
    print("="*80)
    print("\n⚠️ UYARI: Bu script gerçek web scraping yapar ve uzun sürebilir.")
    print("Test URL'lerini TEST_URLS listesine ekleyin.\n")
    
    if len(TEST_URLS) == 0:
        print("❌ HATA: TEST_URLS listesi boş!")
        print("Lütfen test_scraping.py dosyasındaki TEST_URLS listesine gerçek ürün linkleri ekleyin.")
        sys.exit(1)
    
    if len(TEST_URLS) < 50:
        print(f"⚠️ UYARI: Sadece {len(TEST_URLS)} URL bulundu. 50 URL önerilir.")
        response = input("Devam etmek istiyor musunuz? (e/h): ")
        if response.lower() != 'e':
            sys.exit(0)
    
    # Testleri çalıştır
    asyncio.run(run_batch_tests())

