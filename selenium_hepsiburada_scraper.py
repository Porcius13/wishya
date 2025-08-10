#!/usr/bin/env python3
"""
Selenium ile Hepsiburada Scraper
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def setup_driver():
    """Chrome driver'ı ayarla"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def scrape_hepsiburada_selenium(url):
    """Selenium ile Hepsiburada'dan veri çekme"""
    driver = None
    try:
        print(f"Sayfa yükleniyor: {url}")
        driver = setup_driver()
        driver.get(url)
        
        # Sayfanın yüklenmesini bekle
        time.sleep(5)
        
        # Başlık çekme
        title = ""
        try:
            # H1 elementlerini dene
            h1_elements = driver.find_elements(By.TAG_NAME, "h1")
            for h1 in h1_elements:
                text = h1.text.strip()
                if text and len(text) > 5:
                    title = text
                    break
            
            # H1 bulunamazsa diğer başlık elementlerini dene
            if not title:
                title_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='title'], [class*='product-name'], [data-testid*='product']")
                for element in title_elements:
                    text = element.text.strip()
                    if text and len(text) > 5:
                        title = text
                        break
        except Exception as e:
            print(f"Başlık çekme hatası: {e}")

        # Fiyat çekme
        current_price = ""
        original_price = ""
        
        try:
            # Daha spesifik fiyat selector'ları dene
            price_selectors = [
                "div[class*='price'] span",
                "span[class*='price']",
                "[data-test-id='price-current']",
                ".price-current",
                "div[class*='z7kokklsVwh0K5zFWjIO'] span",
                "div[class*='ETYrVpXSa3c1UlXVAjTK'] span"
            ]
            
            prices_found = []
            
            for selector in price_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and ("₺" in text or "TL" in text) and any(char.isdigit() for char in text):
                            # Fiyat temizleme
                            price_clean = re.sub(r'[^\d.,]', '', text)
                            if price_clean and len(price_clean) > 2 and price_clean not in prices_found:
                                # Sadece geçerli fiyatları al (çok uzun olmayan)
                                if len(price_clean) < 20:
                                    prices_found.append(price_clean)
                except:
                    continue
            
            # Fiyatları sırala (en düşük fiyat mevcut fiyat, en yüksek indirimsiz fiyat)
            if prices_found:
                # Sadece sayısal değerleri al
                valid_prices = []
                for price in prices_found:
                    try:
                        # Virgülü noktaya çevir ve float'a çevir
                        price_float = float(price.replace(',', '.'))
                        if 1 <= price_float <= 100000:  # Makul fiyat aralığı
                            valid_prices.append((price_float, price))
                    except:
                        continue
                
                if valid_prices:
                    valid_prices.sort(key=lambda x: x[0])
                    current_price = f"{valid_prices[0][0]} TL"
                    if len(valid_prices) > 1:
                        original_price = f"{valid_prices[-1][0]} TL"
                    
        except Exception as e:
            print(f"Fiyat çekme hatası: {e}")

        # Görsel çekme
        image = ""
        try:
            # En basit yöntem: Tüm img elementlerini bul ve Hepsiburada görsellerini ara
            img_elements = driver.find_elements(By.TAG_NAME, "img")
            print(f"Toplam {len(img_elements)} img elementi bulundu")
            
            for img in img_elements:
                try:
                    src = img.get_attribute("src")
                    if src and "productimages.hepsiburada.net" in src:
                        # Orijinal boyut için parametreleri kaldır
                        base_url = src.split('?')[0] if '?' in src else src
                        image = base_url
                        print(f"✅ Görsel bulundu: {src}")
                        break
                except:
                    continue
                        
        except Exception as e:
            print(f"Görsel çekme hatası: {e}")

        # Marka tespiti
        brand = "Hepsiburada"
        if title:
            common_brands = ["GIPTA", "MOLESKINE", "LEUCHTTURM", "RHODIA", "CLAIREFONTAINE", "EXACOMPTA", "OXFORD", "PAPERBLANKS", "PETER PAUPER", "QUO VADIS", "SILVER POINT", "STAPLES", "TARGET", "WALMART", "AMAZON", "ALIEXPRESS", "BANGGOOD", "GEARBEST", "LIGHTINTHEBOX", "SHEIN", "WISH", "TEMU", "APPLE", "SAMSUNG", "XIAOMI", "HUAWEI", "OPPO", "VIVO", "REALME", "ONEPLUS", "GOOGLE", "NOKIA", "SONY", "LG", "ASUS", "ACER", "LENOVO", "DELL", "HP", "MSI", "RAZER", "LOGITECH", "STEELSERIES", "CORSAIR", "KINGSTON", "SANDISK", "WESTERN DIGITAL", "SEAGATE", "TOSHIBA", "INTEL", "AMD", "NVIDIA", "GIGABYTE", "ASROCK", "MSI", "EVGA", "THERMALTAKE", "COOLER MASTER", "NOCTUA", "BE QUIET", "SEASONIC"]
            for brand_name in common_brands:
                if brand_name in title.upper():
                    brand = brand_name
                    break

        result = {
            "title": title,
            "current_price": current_price,
            "original_price": original_price,
            "image": image,
            "brand": brand,
            "url": url,
            "site": "hepsiburada.com"
        }

        print(f"✅ Başarılı! Başlık: {title}")
        return result

    except Exception as e:
        print(f"❌ Hata: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def scrape_hepsiburada_product(url):
    """3 deneme ile Hepsiburada ürün verisi çekme"""
    for i in range(3):
        try:
            print(f"Deneme {i+1}/3...")
            result = scrape_hepsiburada_selenium(url)
            if result and result.get("title"):
                return result
        except Exception as e:
            print(f"Hata {i+1}: {e}")
    
    print("Tüm denemeler başarısız!")
    return None

# Test
if __name__ == "__main__":
    test_url = "https://www.hepsiburada.com/gipta-pera-ciltli-deri-kapak-9x14-cizgisiz-defter-pm-HBC00002QG0EE"
    result = scrape_hepsiburada_product(test_url)
    print("\n=== SONUÇ ===")
    print(result)
