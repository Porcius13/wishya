#!/usr/bin/env python3
"""
Site Spesifik Scraper Test Dosyası
Bu dosya verdiğiniz linkler için oluşturulan scraper'ları test eder.
"""

import asyncio
import json
import sys
import os
from site_specific_scrapers import SiteSpecificScrapers
from advanced_site_scrapers import AdvancedSiteScrapers

async def test_basic_scrapers():
    """Temel scraper'ları test eder"""
    print("=== TEMEL SCRAPER TEST ===")
    scraper = SiteSpecificScrapers()
    
    test_urls = [
        "https://www.beymen.com/tr/p_polo-ralph-lauren-beyaz-oxford-gomlek_1646218",
        "https://www.ellesse.com.tr/products/ellesse-erkek-polo-yaka-tisort-em460-bk",
        "https://www.beyyoglu.com/100-keten-oversize-gomlek-24ss53005006-27/",
        "https://www.ninewest.com.tr/urun/nine-west-margarita-5fx-siyah-kadin-topuklu-sandalet-101928976",
        "https://www.levis.com.tr/levis-511-slim-fit_117340",
        "https://www.dockers.com.tr/smart-360-flex-ultimate-chino-slim-fit-pantolon_2661",
        "https://sarar.com/sarar-loreto-kot-elbise-18167",
        "https://www.salomon.com.tr/acs-plus-unisex-sneaker-l47705300",
        "https://www.abercrombie.com/shop/wd/p/premium-polished-tee-57648335?categoryId=12204&faceout=model&seq=13",
        "https://www.loft.com.tr/p/loose-fit-erkek-tshirt-kkol-6931",
        "https://ucla.com.tr/canary-haki-bisiklet-yaka-gofre-baskili-modal-kumas-standard-fit-erkek-tshirt",
        "https://www.yargici.com/kahverengi-regular-fit-keten-gomlek-p-198901"
    ]
    
    results = []
    for i, url in enumerate(test_urls, 1):
        print(f"\n[{i}/{len(test_urls)}] Scraping: {url}")
        try:
            result = await scraper.scrape_product(url)
            results.append(result)
            
            if "error" in result:
                print(f"❌ Hata: {result['error']}")
            else:
                print(f"✅ Başarılı:")
                print(f"   Site: {result.get('site', 'N/A')}")
                print(f"   Başlık: {result.get('title', 'N/A')[:50]}...")
                print(f"   Güncel Fiyat: {result.get('current_price', 'N/A')}")
                print(f"   Eski Fiyat: {result.get('original_price', 'N/A')}")
                print(f"   Resim: {result.get('image_url', 'N/A')[:50]}...")
            
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")
            results.append({"error": str(e), "url": url})
        
        await asyncio.sleep(1)  # Rate limiting
    
    # Sonuçları kaydet
    with open("basic_scraping_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 Temel scraper sonuçları basic_scraping_results.json dosyasına kaydedildi.")
    return results

async def test_advanced_scrapers():
    """Gelişmiş scraper'ları test eder"""
    print("\n=== GELİŞMİŞ SCRAPER TEST ===")
    scraper = AdvancedSiteScrapers()
    
    test_urls = [
        "https://www.beymen.com/tr/p_polo-ralph-lauren-beyaz-oxford-gomlek_1646218",
        "https://www.ellesse.com.tr/products/ellesse-erkek-polo-yaka-tisort-em460-bk",
        "https://www.beyyoglu.com/100-keten-oversize-gomlek-24ss53005006-27/",
        "https://www.ninewest.com.tr/urun/nine-west-margarita-5fx-siyah-kadin-topuklu-sandalet-101928976",
        "https://www.levis.com.tr/levis-511-slim-fit_117340",
        "https://www.dockers.com.tr/smart-360-flex-ultimate-chino-slim-fit-pantolon_2661",
        "https://sarar.com/sarar-loreto-kot-elbise-18167",
        "https://www.salomon.com.tr/acs-plus-unisex-sneaker-l47705300",
        "https://www.abercrombie.com/shop/wd/p/premium-polished-tee-57648335?categoryId=12204&faceout=model&seq=13",
        "https://www.loft.com.tr/p/loose-fit-erkek-tshirt-kkol-6931",
        "https://ucla.com.tr/canary-haki-bisiklet-yaka-gofre-baskili-modal-kumas-standard-fit-erkek-tshirt",
        "https://www.yargici.com/kahverengi-regular-fit-keten-gomlek-p-198901"
    ]
    
    results = []
    for i, url in enumerate(test_urls, 1):
        print(f"\n[{i}/{len(test_urls)}] Scraping: {url}")
        try:
            result = await scraper.scrape_product(url)
            results.append(result)
            
            if "error" in result:
                print(f"❌ Hata: {result['error']}")
            else:
                print(f"✅ Başarılı:")
                print(f"   Site: {result.get('site', 'N/A')}")
                print(f"   Başlık: {result.get('title', 'N/A')[:50]}...")
                print(f"   Güncel Fiyat: {result.get('current_price', 'N/A')}")
                print(f"   Eski Fiyat: {result.get('original_price', 'N/A')}")
                print(f"   Resim: {result.get('image_url', 'N/A')[:50]}...")
            
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")
            results.append({"error": str(e), "url": url})
        
        await asyncio.sleep(1)  # Rate limiting
    
    # Sonuçları kaydet
    with open("advanced_scraping_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 Gelişmiş scraper sonuçları advanced_scraping_results.json dosyasına kaydedildi.")
    return results

async def test_single_url(url: str):
    """Tek bir URL'yi test eder"""
    print(f"\n=== TEK URL TEST: {url} ===")
    
    # Temel scraper ile test
    print("\n--- Temel Scraper ---")
    basic_scraper = SiteSpecificScrapers()
    try:
        result = await basic_scraper.scrape_product(url)
        if "error" in result:
            print(f"❌ Temel scraper hatası: {result['error']}")
        else:
            print(f"✅ Temel scraper başarılı:")
            print(f"   Site: {result.get('site', 'N/A')}")
            print(f"   Başlık: {result.get('title', 'N/A')}")
            print(f"   Güncel Fiyat: {result.get('current_price', 'N/A')}")
            print(f"   Eski Fiyat: {result.get('original_price', 'N/A')}")
            print(f"   Resim: {result.get('image_url', 'N/A')}")
    except Exception as e:
        print(f"❌ Temel scraper beklenmeyen hata: {e}")
    
    # Gelişmiş scraper ile test
    print("\n--- Gelişmiş Scraper ---")
    advanced_scraper = AdvancedSiteScrapers()
    try:
        result = await advanced_scraper.scrape_product(url)
        if "error" in result:
            print(f"❌ Gelişmiş scraper hatası: {result['error']}")
        else:
            print(f"✅ Gelişmiş scraper başarılı:")
            print(f"   Site: {result.get('site', 'N/A')}")
            print(f"   Başlık: {result.get('title', 'N/A')}")
            print(f"   Güncel Fiyat: {result.get('current_price', 'N/A')}")
            print(f"   Eski Fiyat: {result.get('original_price', 'N/A')}")
            print(f"   Resim: {result.get('image_url', 'N/A')}")
    except Exception as e:
        print(f"❌ Gelişmiş scraper beklenmeyen hata: {e}")

def print_summary(basic_results, advanced_results):
    """Test sonuçlarının özetini yazdırır"""
    print("\n" + "="*50)
    print("TEST SONUÇLARI ÖZETİ")
    print("="*50)
    
    # Temel scraper sonuçları
    basic_success = sum(1 for r in basic_results if "error" not in r)
    basic_total = len(basic_results)
    print(f"\n📊 Temel Scraper:")
    print(f"   Başarılı: {basic_success}/{basic_total} ({basic_success/basic_total*100:.1f}%)")
    
    # Gelişmiş scraper sonuçları
    advanced_success = sum(1 for r in advanced_results if "error" not in r)
    advanced_total = len(advanced_results)
    print(f"\n📊 Gelişmiş Scraper:")
    print(f"   Başarılı: {advanced_success}/{advanced_total} ({advanced_success/advanced_total*100:.1f}%)")
    
    # Hata analizi
    print(f"\n🔍 Hata Analizi:")
    basic_errors = [r for r in basic_results if "error" in r]
    advanced_errors = [r for r in advanced_results if "error" in r]
    
    if basic_errors:
        print(f"   Temel scraper hataları: {len(basic_errors)}")
        for error in basic_errors[:3]:  # İlk 3 hatayı göster
            print(f"     - {error.get('error', 'Bilinmeyen hata')}")
    
    if advanced_errors:
        print(f"   Gelişmiş scraper hataları: {len(advanced_errors)}")
        for error in advanced_errors[:3]:  # İlk 3 hatayı göster
            print(f"     - {error.get('error', 'Bilinmeyen hata')}")

async def main():
    """Ana test fonksiyonu"""
    print("🚀 Site Spesifik Scraper Test Başlatılıyor...")
    
    # Komut satırı argümanlarını kontrol et
    if len(sys.argv) > 1:
        url = sys.argv[1]
        await test_single_url(url)
        return
    
    # Tüm testleri çalıştır
    try:
        basic_results = await test_basic_scrapers()
        advanced_results = await test_advanced_scrapers()
        print_summary(basic_results, advanced_results)
        
        print(f"\n🎉 Test tamamlandı!")
        print(f"📁 Sonuç dosyaları:")
        print(f"   - basic_scraping_results.json")
        print(f"   - advanced_scraping_results.json")
        
    except KeyboardInterrupt:
        print("\n⏹️ Test kullanıcı tarafından durduruldu.")
    except Exception as e:
        print(f"\n❌ Test sırasında hata oluştu: {e}")

if __name__ == "__main__":
    # Kullanım talimatları
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        print("""
Site Spesifik Scraper Test Aracı

Kullanım:
    python test_site_scrapers.py                    # Tüm testleri çalıştır
    python test_site_scrapers.py <URL>              # Tek URL test et
    
Örnek:
    python test_site_scrapers.py
    python test_site_scrapers.py "https://www.beymen.com/tr/p_polo-ralph-lauren-beyaz-oxford-gomlek_1646218"
        """)
        sys.exit(0)
    
    asyncio.run(main())
