#!/usr/bin/env python3
"""
E-Ticaret Ürün Kataloğu - API Kullanım Örnekleri
"""

import requests
import json
import time

# API Base URL
BASE_URL = "http://localhost:5000"

def scrape_product(url):
    """Tek ürün çekme"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/scrape",
            json={"url": url},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Başarılı: {result['product']['name']}")
            return result['product']
        else:
            print(f"❌ Hata: {response.json().get('error', 'Bilinmeyen hata')}")
            return None
            
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return None

def get_all_products():
    """Tüm ürünleri listeleme"""
    try:
        response = requests.get(f"{BASE_URL}/api/products")
        
        if response.status_code == 200:
            products = response.json()['products']
            print(f"📦 Toplam {len(products)} ürün bulundu:")
            
            for i, product in enumerate(products, 1):
                print(f"{i}. {product['brand']} - {product['name']} - {product['price']}")
            
            return products
        else:
            print(f"❌ Hata: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return []

def clear_all_products():
    """Tüm ürünleri silme"""
    try:
        response = requests.post(f"{BASE_URL}/api/clear")
        
        if response.status_code == 200:
            print("🗑️ Tüm ürünler silindi")
            return True
        else:
            print(f"❌ Hata: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return False

def bulk_scrape(urls):
    """Toplu ürün çekme"""
    print(f"🚀 {len(urls)} ürün çekiliyor...")
    
    successful = 0
    failed = 0
    
    for i, url in enumerate(urls, 1):
        print(f"\n📥 {i}/{len(urls)}: {url}")
        
        product = scrape_product(url)
        if product:
            successful += 1
        else:
            failed += 1
        
        # Rate limiting - her istek arasında 2 saniye bekle
        time.sleep(2)
    
    print(f"\n📊 Sonuç: {successful} başarılı, {failed} başarısız")

def main():
    """Ana fonksiyon - örnek kullanım"""
    
    print("🛍️ E-Ticaret Ürün Kataloğu - API Örnekleri")
    print("=" * 50)
    
    # Örnek URL'ler
    sample_urls = [
        "https://www.zara.com/tr/kadin/elbiseler-c106",
        "https://www.mango.com/tr/kadin/elbiseler",
        "https://www.bershka.com/tr/kadin/elbiseler",
        "https://www.boyner.com.tr/kadin/elbiseler",
        "https://www.koton.com/kadin/elbiseler"
    ]
    
    while True:
        print("\n📋 Menü:")
        print("1. Tek ürün çek")
        print("2. Toplu ürün çek")
        print("3. Tüm ürünleri listele")
        print("4. Tüm ürünleri sil")
        print("5. Örnek URL'lerle test et")
        print("0. Çıkış")
        
        choice = input("\nSeçiminiz (0-5): ").strip()
        
        if choice == "1":
            url = input("Ürün URL'si: ").strip()
            if url:
                scrape_product(url)
        
        elif choice == "2":
            print("URL'leri her satıra bir tane gelecek şekilde yazın (boş satır ile bitirin):")
            urls = []
            while True:
                url = input().strip()
                if not url:
                    break
                urls.append(url)
            
            if urls:
                bulk_scrape(urls)
        
        elif choice == "3":
            get_all_products()
        
        elif choice == "4":
            confirm = input("Tüm ürünleri silmek istediğinizden emin misiniz? (y/N): ")
            if confirm.lower() == 'y':
                clear_all_products()
        
        elif choice == "5":
            print("🧪 Örnek URL'lerle test ediliyor...")
            bulk_scrape(sample_urls)
        
        elif choice == "0":
            print("👋 Görüşürüz!")
            break
        
        else:
            print("❌ Geçersiz seçim!")

if __name__ == "__main__":
    main() 