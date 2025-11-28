import uuid
import time
import re
import traceback
from flask import Flask, render_template, request, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

app = Flask(__name__)
products = []

BRANDS = [
    ("koton.com", "Koton"),
    ("ltbjeans.com", "LTB Jeans"),
    ("colins.com.tr", "Colin's"),
    ("defacto.com.tr", "Defacto"),
    ("boyner.com.tr", "Boyner"),
    ("superstep.com.tr", "Superstep"),
    ("catiuniform.com", "Çatı Uniform"),
    ("oysho.com", "Oysho"),
    ("mango.com", "Mango"),
    ("zara.com", "Zara"),
    ("bershka.com", "Bershka"),
    ("stradivarius.com", "Stradivarius"),
    ("pullandbear.com", "Pull&Bear"),
    ("hm.com", "H&M"),
    ("lcwaikiki.com", "LC Waikiki"),
    ("trendyol.com", "Trendyol"),
    ("adidas.com.tr", "Adidas"),
    ("nike.com", "Nike"),
    ("penti.com", "Penti"),
    ("mavi.com", "Mavi"),
]

def setup_driver(headless=True):
    """Selenium driver'ı hazırla"""
    chrome_options = Options()
    
    # Temel ayarlar
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-javascript")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")
    chrome_options.add_argument("--disable-features=TranslateUI")
    chrome_options.add_argument("--disable-ipc-flooding-protection")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-sync")
    chrome_options.add_argument("--disable-translate")
    chrome_options.add_argument("--hide-scrollbars")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--no-pings")
    chrome_options.add_argument("--disable-prompt-on-repost")
    chrome_options.add_argument("--disable-hang-monitor")
    chrome_options.add_argument("--disable-client-side-phishing-detection")
    chrome_options.add_argument("--disable-component-update")
    chrome_options.add_argument("--disable-domain-reliability")
    chrome_options.add_argument("--disable-features=AudioServiceOutOfProcess")
    
    # User-Agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Window size
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Headless mod (görünmez)
    if headless:
        chrome_options.add_argument("--headless")
    
    # Diğer ayarlar
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Stealth script'ler
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR', 'tr', 'en-US', 'en']})")
    driver.execute_script("Object.defineProperty(navigator, 'permissions', {get: () => ({query: async () => ({ state: 'granted' })})})")
    driver.execute_script("window.chrome = {runtime: {}}")
    
    return driver

def scrape_product(url, headless=True):
    print(f"[DEBUG] Scraping başlıyor: {url}")
    
    # Marka tespiti
    brand = "Bilinmiyor"
    try:
        for domain, brand_name in BRANDS:
            if domain in url:
                brand = brand_name
                break
    except:
        pass
    
    driver = None
    try:
        driver = setup_driver(headless=headless)
        
        # Önce ana sayfaya git (bot korumasını aşmak için)
        try:
            if "mango.com" in url:
                driver.get("https://shop.mango.com/tr")
                time.sleep(3)
            elif "zara.com" in url:
                driver.get("https://www.zara.com/tr/")
                time.sleep(3)
            elif "bershka.com" in url:
                driver.get("https://www.bershka.com/tr/")
                time.sleep(3)
        except:
            pass
        
        # Ürün sayfasına git
        driver.get(url)
        time.sleep(5)
        
        # Başlık çek
        title = None
        try:
            title_selectors = [
                'h1[data-testid="product-detail-name"]',
                'h1.product-name',
                'h1.product-title',
                'h1.title',
                'h1',
                'title'
            ]
            
            for selector in title_selectors:
                try:
                    if selector == 'title':
                        title = driver.title
                    else:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                        title = element.text
                    
                    if title and title.strip():
                        title = title.strip().upper()
                        title = re.sub(r'[^\w\s\-\.]', '', title)
                        title = re.sub(r'\s+', ' ', title).strip()
                        break
                except:
                    continue
            
            if not title:
                title = "Başlık bulunamadı"
                
        except Exception as e:
            print(f"[HATA] Başlık çekilemedi: {e}")
            title = "Başlık bulunamadı"

        # Görsel çek
        image = None
        try:
            img_selectors = [
                'img[data-testid="product-detail-image"]',
                'img.image-viewer-image',
                'img.product-gallery-image',
                'img.product-image',
                'img.main-image',
                'img[src*=".jpg"]',
                'img[src*=".jpeg"]',
                'img[src*=".webp"]',
                'img[src*=".png"]'
            ]
            
            for selector in img_selectors:
                try:
                    img_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for img in img_elements:
                        src = img.get_attribute('src')
                        srcset = img.get_attribute('srcset')
                        
                        # src'yi kontrol et
                        if src:
                            if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png']):
                                image = src
                                break
                        
                        # srcset'i kontrol et
                        if srcset and not image:
                            srcset_urls = srcset.split(',')
                            for srcset_url in srcset_urls:
                                url_part = srcset_url.strip().split(' ')[0]
                                if any(ext in url_part.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png']):
                                    image = url_part
                                    break
                        
                        if image:
                            break
                    
                    if image:
                        break
                except:
                    continue
            
            # Regex fallback
            if not image:
                page_source = driver.page_source
                img_pattern = re.compile(r'src=["\']([^"\']*\.(?:jpg|jpeg|webp|png)[^"\']*)["\']')
                match = img_pattern.search(page_source)
                if match:
                    image = match.group(1)
                    
        except Exception as e:
            print(f"[HATA] Görsel çekilemedi: {e}")
            image = None

        # Fiyat çek
        price = None
        try:
            price_selectors = [
                '.product-sale',
                '.product-price',
                '.price',
                'span.price',
                'div.price',
                'p.price',
                '[data-testid="product-price"]',
                '[class*="price"]',
                'span',
                'div',
                'p'
            ]
            
            for selector in price_selectors:
                try:
                    price_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in price_elements:
                        text = element.text
                        if text and ('₺' in text or 'TL' in text):
                            # Fiyat regex'i
                            price_pattern = re.compile(r'([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}\s*(?:₺|TL)|[0-9]{1,3}(?:\.[0-9]{3})*\s*(?:₺|TL)|[0-9]+(?:\.[0-9]{2})?\s*(?:₺|TL))')
                            match = price_pattern.search(text)
                            if match:
                                price = match.group(1)
                                break
                    
                    if price:
                        break
                except:
                    continue
            
            # Regex fallback
            if not price:
                page_text = driver.page_source
                price_pattern = re.compile(r'([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}\s*(?:₺|TL)|[0-9]{1,3}(?:\.[0-9]{3})*\s*(?:₺|TL)|[0-9]+(?:\.[0-9]{2})?\s*(?:₺|TL))')
                match = price_pattern.search(page_text)
                if match:
                    price = match.group(1)
                else:
                    price = "Fiyat bulunamadı"
                    
        except Exception as e:
            print(f"[HATA] Fiyat çekilemedi: {e}")
            price = "Fiyat bulunamadı"

        print(f"[DEBUG] Çekilen başlık: {title}")
        print(f"[DEBUG] Çekilen fiyat: {price}")
        print(f"[DEBUG] Çekilen marka: {brand}")
        
        return {
            "id": str(uuid.uuid4()),
            "url": url,
            "name": title.strip() if title else "İsim bulunamadı",
            "price": price,
            "image": image,
            "brand": brand,
            "sizes": []
        }
        
    except Exception as e:
        print(f"[HATA] Scraping başarısız: {e}")
        traceback.print_exc()
        return {
            "id": str(uuid.uuid4()),
            "url": url,
            "name": "Scraping hatası",
            "price": "Fiyat bulunamadı",
            "image": None,
            "brand": brand,
            "sizes": []
        }
    finally:
        if driver:
            driver.quit()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        product_url = request.form.get("product_url")
        if product_url:
            try:
                product = scrape_product(product_url)
                if product:
                    products.append(product)
            except Exception as e:
                print(f"[HATA] Ürün eklenirken hata: {e}")
                traceback.print_exc()
        return redirect(url_for("index"))
    return render_template("index.html", products=products)

@app.route("/delete/<id>", methods=["POST"])
def delete_product(id):
    global products
    products = [p for p in products if p.get("id") != id]
    return redirect(url_for("index"))

@app.errorhandler(405)
def method_not_allowed(e):
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True) 