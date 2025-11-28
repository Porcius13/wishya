#!/usr/bin/env python3
"""
Hızlı test için basit scraper testi
"""

import asyncio
from site_specific_scrapers import SiteSpecificScrapers

async def quick_test():
    scraper = SiteSpecificScrapers()
    
    # Sadece 3 URL test et
    test_urls = [
        "https://www.beymen.com/tr/p_polo-ralph-lauren-beyaz-oxford-gomlek_1646218",
        "https://www.ellesse.com.tr/products/ellesse-erkek-polo-yaka-tisort-em460-bk",
        "https://www.beyyoglu.com/100-keten-oversize-gomlek-24ss53005006-27/"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n[{i}/{len(test_urls)}] Testing: {url}")
        try:
            result = await scraper.scrape_product(url)
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
        
        await asyncio.sleep(2)  # Rate limiting

if __name__ == "__main__":
    print("🚀 Quick Test Starting...")
    asyncio.run(quick_test())
    print("\n✅ Quick test completed!")
