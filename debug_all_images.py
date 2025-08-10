#!/usr/bin/env python3
"""
Tüm Görselleri Debug Et
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def debug_all_images():
    """Tüm img elementlerini debug et"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        url = "https://www.hepsiburada.com/gipta-pera-ciltli-deri-kapak-9x14-cizgisiz-defter-pm-HBC00002QG0EE"
        print(f"Sayfa yükleniyor: {url}")
        
        driver.get(url)
        time.sleep(8)  # Daha uzun bekle
        
        print("\n=== TÜM IMG ELEMENTLERİ ===")
        
        # Tüm img elementlerini bul
        img_elements = driver.find_elements(By.TAG_NAME, "img")
        print(f"Toplam img elementi sayısı: {len(img_elements)}")
        
        hepsiburada_images = []
        
        for i, img in enumerate(img_elements):
            try:
                src = img.get_attribute("src")
                alt = img.get_attribute("alt")
                class_attr = img.get_attribute("class")
                id_attr = img.get_attribute("id")
                
                print(f"\n--- Element {i+1} ---")
                print(f"src: {src}")
                print(f"alt: {alt}")
                print(f"class: {class_attr}")
                print(f"id: {id_attr}")
                
                # Hepsiburada görsellerini ayrı listele
                if src and "productimages.hepsiburada.net" in src:
                    hepsiburada_images.append({
                        'index': i+1,
                        'src': src,
                        'alt': alt,
                        'class': class_attr
                    })
                    print("✅ Hepsiburada görseli!")
                    
            except Exception as e:
                print(f"Element {i+1} hatası: {e}")
        
        print(f"\n=== HEPSIBURADA GÖRSELLERİ ({len(hepsiburada_images)}) ===")
        for img in hepsiburada_images:
            print(f"Element {img['index']}: {img['src']}")
            print(f"  Alt: {img['alt']}")
            print(f"  Class: {img['class']}")
        
        # Spesifik selector'ları test et
        print(f"\n=== SELECTOR TESTLERİ ===")
        
        selectors_to_test = [
            "img.i9jTSpEeoI29_M1mOKct.hb-HbImage-view__image",
            "img[class*='i9jTSpEeoI29_M1mOKct']",
            "img[class*='hb-HbImage-view__image']",
            "img[alt*='Pera']",
            "img[alt*='Ciltli']",
            "img[alt*='Defter']",
            "img[src*='productimages.hepsiburada.net']",
            "img[class*='product']",
            "img[class*='image']",
            "img[class*='view']"
        ]
        
        for selector in selectors_to_test:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"{selector}: {len(elements)} element bulundu")
                if len(elements) > 0:
                    for j, elem in enumerate(elements):
                        src = elem.get_attribute("src")
                        alt = elem.get_attribute("alt")
                        print(f"  Element {j+1}: src={src}, alt={alt}")
            except Exception as e:
                print(f"{selector}: HATA - {e}")
        
        # Sayfanın HTML'ini kaydet
        print(f"\n=== HTML KAYDET ===")
        html_content = driver.page_source
        with open("hepsiburada_page.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("HTML sayfa kaydedildi: hepsiburada_page.html")
        
    except Exception as e:
        print(f"Genel hata: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    debug_all_images()
