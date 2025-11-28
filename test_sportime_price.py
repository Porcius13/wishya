"""Sportime fiyat test - Debug çıktısı ile"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_old import scrape_product

URL = "https://sportime.com.tr/products/nike-air-max-1-gs-dz3307-112-cocuk-sneaker"

async def test():
    print("="*80)
    print("SPORTIME FIYAT TEST")
    print("="*80)
    print(f"URL: {URL}\n")
    
    result = await scrape_product(URL)
    
    if result:
        print("\n" + "="*80)
        print("SONUC:")
        print("="*80)
        print(f"Fiyat: {result.get('price', 'YOK')}")
        print(f"Eski Fiyat: {result.get('old_price', 'YOK')}")
        print(f"Gorsel: {result.get('image', 'YOK')[:80]}...")
        print("="*80)
    else:
        print("HATA: Sonuc alinamadi")

if __name__ == "__main__":
    asyncio.run(test())

