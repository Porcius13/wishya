"""Hızlı Sportime test - Fiyat ve görsel çekme"""
import asyncio
import sys
import os

# Dizin ayarı
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_old import scrape_product

URL = "https://sportime.com.tr/products/nike-air-max-1-gs-dz3307-112-cocuk-sneaker"

async def get_product_info():
    print("="*80)
    print("SPORTIME ÜRÜN BİLGİLERİ")
    print("="*80)
    print(f"URL: {URL}\n")
    
    try:
        result = await scrape_product(URL)
        
        if result:
            print("\n" + "="*80)
            print("SONUÇLAR:")
            print("="*80)
            
            print(f"\n📦 BAŞLIK:")
            print(f"   {result.get('name', 'Bulunamadı')}")
            
            print(f"\n💰 FİYAT:")
            price = result.get('price', 'Bulunamadı')
            print(f"   {price}")
            old_price = result.get('old_price')
            if old_price:
                print(f"   Eski Fiyat: {old_price}")
            
            print(f"\n🖼️ GÖRSEL:")
            image = result.get('image', 'Bulunamadı')
            if image:
                print(f"   {image}")
            else:
                print(f"   Bulunamadı")
            
            print(f"\n🏷️ MARKA:")
            print(f"   {result.get('brand', 'Bulunamadı')}")
            
            print("\n" + "="*80)
            
            # Kullanıcı için özet
            print("\n📋 ÖZET:")
            print(f"   Fiyat: {price}")
            print(f"   Görsel: {image[:80] + '...' if image and len(image) > 80 else image}")
            
        else:
            print("\n❌ Ürün bilgileri çekilemedi!")
            
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(get_product_info())

