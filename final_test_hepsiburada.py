#!/usr/bin/env python3
"""
Hepsiburada Scraper Final Test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium_hepsiburada_scraper import scrape_hepsiburada_product
from scraper import scrape_product

def test_hepsiburada_final():
    """Hepsiburada scraper final test"""
    print("=== Hepsiburada Scraper Final Test ===")
    
    # Test URL'i
    test_url = "https://www.hepsiburada.com/gipta-pera-ciltli-deri-kapak-9x14-cizgisiz-defter-pm-HBC00002QG0EE"
    
    print(f"Test URL: {test_url}")
    print("\n1. Selenium Hepsiburada Scraper Test:")
    print("-" * 50)
    
    # Selenium scraper test
    result1 = scrape_hepsiburada_product(test_url)
    if result1:
        print("✅ Başarılı!")
        print(f"Başlık: {result1.get('title', 'N/A')}")
        print(f"Mevcut Fiyat: {result1.get('current_price', 'N/A')} TL")
        print(f"İndirimsiz Fiyat: {result1.get('original_price', 'N/A')} TL")
        print(f"Marka: {result1.get('brand', 'N/A')}")
        print(f"Görsel: {result1.get('image', 'N/A')}")
        print(f"Site: {result1.get('site', 'N/A')}")
    else:
        print("❌ Başarısız!")
    
    print("\n2. Genel Scraper Test (Hepsiburada için Selenium kullanacak):")
    print("-" * 50)
    
    # Genel scraper test
    result2 = scrape_product(test_url)
    if result2:
        print("✅ Başarılı!")
        print(f"Başlık: {result2.get('title', 'N/A')}")
        print(f"Fiyat: {result2.get('price', 'N/A')}")
        print(f"İndirimsiz Fiyat: {result2.get('original_price', 'N/A')}")
        print(f"Marka: {result2.get('brand', 'N/A')}")
        print(f"Görsel: {result2.get('image', 'N/A')}")
        print(f"Site: {result2.get('site', 'N/A')}")
    else:
        print("❌ Başarısız!")
    
    print("\n=== Test Tamamlandı ===")
    
    # Sonuç karşılaştırması
    if result1 and result2:
        print("\n=== KARŞILAŞTIRMA ===")
        print(f"Başlık Eşleşmesi: {'✅' if result1.get('title') == result2.get('title') else '❌'}")
        print(f"Fiyat Eşleşmesi: {'✅' if result1.get('current_price') == result2.get('price') else '❌'}")
        print(f"Marka Eşleşmesi: {'✅' if result1.get('brand') == result2.get('brand') else '❌'}")
        print(f"Görsel Eşleşmesi: {'✅' if result1.get('image') == result2.get('image') else '❌'}")

if __name__ == "__main__":
    test_hepsiburada_final()
