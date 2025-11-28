#!/usr/bin/env python3
"""
Tüm URL'leri test etmek için güvenli test dosyası
"""

import asyncio
import json
from site_specific_scrapers import SiteSpecificScrapers
from advanced_site_scrapers import AdvancedSiteScrapers

async def full_test():
    # Tüm test URL'leri
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
    
    # Temel scraper test
    print("=== TEMEL SCRAPER TEST ===")
    basic_scraper = SiteSpecificScrapers()
    basic_results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n[{i}/{len(test_urls)}] Testing: {url}")
        try:
            result = await basic_scraper.scrape_product(url)
            basic_results.append(result)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Success:")
                print(f"   Site: {result.get('site', 'N/A')}")
                print(f"   Title: {result.get('title', 'N/A')[:50]}...")
                print(f"   Current Price: {result.get('current_price', 'N/A')}")
                print(f"   Original Price: {result.get('original_price', 'N/A')}")
                print(f"   Image: {result.get('image_url', 'N/A')[:50]}...")
        except Exception as e:
            print(f"❌ Exception: {e}")
            basic_results.append({"error": str(e), "url": url})
        
        await asyncio.sleep(3)  # Daha uzun bekleme süresi
    
    # Gelişmiş scraper test
    print("\n=== GELİŞMİŞ SCRAPER TEST ===")
    advanced_scraper = AdvancedSiteScrapers()
    advanced_results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n[{i}/{len(test_urls)}] Testing: {url}")
        try:
            result = await advanced_scraper.scrape_product(url)
            advanced_results.append(result)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Success:")
                print(f"   Site: {result.get('site', 'N/A')}")
                print(f"   Title: {result.get('title', 'N/A')[:50]}...")
                print(f"   Current Price: {result.get('current_price', 'N/A')}")
                print(f"   Original Price: {result.get('original_price', 'N/A')}")
                print(f"   Image: {result.get('image_url', 'N/A')[:50]}...")
        except Exception as e:
            print(f"❌ Exception: {e}")
            advanced_results.append({"error": str(e), "url": url})
        
        await asyncio.sleep(3)  # Daha uzun bekleme süresi
    
    # Sonuçları analiz et
    print("\n" + "="*50)
    print("TEST SONUÇLARI ÖZETİ")
    print("="*50)
    
    basic_success = sum(1 for r in basic_results if "error" not in r)
    advanced_success = sum(1 for r in advanced_results if "error" not in r)
    
    print(f"\n📊 Temel Scraper:")
    print(f"   Başarılı: {basic_success}/{len(test_urls)} ({basic_success/len(test_urls)*100:.1f}%)")
    
    print(f"\n📊 Gelişmiş Scraper:")
    print(f"   Başarılı: {advanced_success}/{len(test_urls)} ({advanced_success/len(test_urls)*100:.1f}%)")
    
    # Başarılı olanları listele
    print(f"\n✅ Başarılı Scraping'ler:")
    for i, (basic, advanced) in enumerate(zip(basic_results, advanced_results)):
        if "error" not in basic:
            print(f"   {i+1}. {basic.get('site', 'N/A')} - {basic.get('title', 'N/A')[:30]}...")
    
    # Sonuçları kaydet
    with open("full_test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "basic_results": basic_results,
            "advanced_results": advanced_results,
            "summary": {
                "basic_success": basic_success,
                "advanced_success": advanced_success,
                "total_urls": len(test_urls)
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 Sonuçlar full_test_results.json dosyasına kaydedildi.")

if __name__ == "__main__":
    print("🚀 Full Test Starting...")
    asyncio.run(full_test())
    print("\n✅ Full test completed!")
