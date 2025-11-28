"""
Universal Scraper - Tüm siteler için otomatik ürün verisi çekme modülü
Başarılı scraping yaklaşımlarını birleştirerek yeni siteler için otomatik çalışır
"""

import re
import json
from urllib.parse import urlparse
from typing import Dict, List, Optional, Tuple


class UniversalScraper:
    """Evrensel ürün scraping sınıfı"""
    
    def __init__(self):
        # Skip edilecek keyword'ler (logo, banner, vb.)
        self.skip_keywords = ['logo', 'banner', 'icon', 'header', 'footer', 'ad', 'promo', 'campaign', 'ads']
        
        # Genel selector'lar (öncelik sırasına göre)
        self.title_selectors = [
            'h1[data-testid="product-detail-name"]',
            'h1[data-testid="product-title"]',
            'h1.product-name',
            'h1.product-title',
            'h1.title',
            '.product-name',
            '.product-title',
            '.product-detail-name',
            '[data-testid="product-title"]',
            'h1',
            'title'
        ]
        
        self.price_selectors = [
            '[itemprop="price"]',
            '[data-price]',
            '.product-price',
            '.product__price',
            '.price',
            'span.price',
            'div.price',
            '[class*="price"]',
            '[class*="Price"]',
            '.current-price',
            '.sale-price',
            '.final-price'
        ]
        
        self.image_selectors = [
            'img[data-testid="product-detail-image"]',
            'img[data-testid="product-image"]',
            'img.product-image',
            'img.product__image',
            'img[class*="product-image"]',
            'img[class*="product__image"]',
            'img[alt*="product"]',
            'img[alt*="ürün"]',
            'img[alt*="resmi"]',
            'img[src*=".jpg"]',
            'img[src*=".jpeg"]',
            'img[src*=".webp"]',
            'img[src*=".png"]'
        ]
    
    async def extract_title(self, page) -> Optional[str]:
        """Başlık çekme - Öncelik sırası: JSON-LD > Meta Tags > DOM Selectors"""
        title = None
        
        try:
            # 1. JSON-LD structured data'dan çek
            title = await self._extract_title_from_jsonld(page)
            if title:
                print(f"[DEBUG] Başlık JSON-LD'den bulundu: {title}")
                return self._clean_title(title)
            
            # 2. Meta tags'den çek
            title = await self._extract_title_from_meta(page)
            if title:
                print(f"[DEBUG] Başlık meta tag'den bulundu: {title}")
                return self._clean_title(title)
            
            # 3. DOM selector'larından çek
            for selector in self.title_selectors:
                try:
                    if selector == 'title':
                        element = await page.query_selector('title')
                    else:
                        element = await page.query_selector(selector)
                    
                    if element:
                        title_text = await element.text_content()
                        if title_text and title_text.strip():
                            title = title_text.strip()
                            print(f"[DEBUG] Başlık DOM'dan bulundu ({selector}): {title}")
                            return self._clean_title(title)
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"[DEBUG] Başlık çekme hatası: {e}")
        
        return None
    
    async def extract_price(self, page, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fiyat çekme - Current ve old price
        Öncelik sırası: JSON-LD > Meta Tags > DOM Selectors > Regex
        """
        price = None
        old_price = None
        
        try:
            # 1. JSON-LD structured data'dan çek
            price_data = await self._extract_price_from_jsonld(page)
            if price_data:
                price = price_data.get('current')
                old_price = price_data.get('old')
                if price:
                    print(f"[DEBUG] Fiyat JSON-LD'den bulundu: {price}")
                    if old_price:
                        print(f"[DEBUG] Eski fiyat JSON-LD'den bulundu: {old_price}")
                    return price, old_price
            
            # 2. Meta tags'den çek
            price_data = await self._extract_price_from_meta(page)
            if price_data:
                price = price_data.get('current')
                old_price = price_data.get('old')
                if price:
                    print(f"[DEBUG] Fiyat meta tag'den bulundu: {price}")
                    return price, old_price
            
            # 3. DOM selector'larından çek
            price_data = await self._extract_price_from_dom(page, url)
            if price_data:
                price = price_data.get('current')
                old_price = price_data.get('old')
                if price:
                    print(f"[DEBUG] Fiyat DOM'dan bulundu: {price}")
                    return price, old_price
            
            # 4. Regex ile sayfadan çek (son çare)
            price_data = await self._extract_price_with_regex(page)
            if price_data:
                price = price_data.get('current')
                old_price = price_data.get('old')
                if price:
                    print(f"[DEBUG] Fiyat regex ile bulundu: {price}")
                    return price, old_price
            
        except Exception as e:
            print(f"[DEBUG] Fiyat çekme hatası: {e}")
        
        return None, None
    
    async def extract_image(self, page, url: str) -> Tuple[Optional[str], List[str]]:
        """
        Görsel çekme - Ana görsel ve tüm görseller
        Öncelik sırası: JSON-LD > Meta Tags > DOM Selectors > Fallback
        """
        image = None
        images = []
        
        try:
            # 1. JSON-LD structured data'dan çek
            image_data = await self._extract_image_from_jsonld(page)
            if image_data:
                image = image_data.get('primary')
                images = image_data.get('all', [])
                if image:
                    print(f"[DEBUG] Görsel JSON-LD'den bulundu: {image}")
                    return image, images
            
            # 2. Meta tags'den çek
            image_data = await self._extract_image_from_meta(page)
            if image_data:
                image = image_data.get('primary')
                images = image_data.get('all', [])
                if image:
                    print(f"[DEBUG] Görsel meta tag'den bulundu: {image}")
                    return image, images
            
            # 3. DOM selector'larından çek
            image_data = await self._extract_image_from_dom(page, url)
            if image_data:
                image = image_data.get('primary')
                images = image_data.get('all', [])
                if image:
                    print(f"[DEBUG] Görsel DOM'dan bulundu: {image}")
                    return image, images
            
            # 4. Fallback: Tüm görselleri tara
            image_data = await self._extract_image_fallback(page, url)
            if image_data:
                image = image_data.get('primary')
                images = image_data.get('all', [])
                if image:
                    print(f"[DEBUG] Görsel fallback ile bulundu: {image}")
                    return image, images
                
        except Exception as e:
            print(f"[DEBUG] Görsel çekme hatası: {e}")
        
        return None, []
    
    # ========== Helper Methods ==========
    
    async def _extract_title_from_jsonld(self, page) -> Optional[str]:
        """JSON-LD structured data'dan başlık çek"""
        try:
            scripts = await page.query_selector_all('script[type="application/ld+json"]')
            for script in scripts:
                try:
                    content = await script.text_content()
                    if not content:
                        continue
                    
                    data = json.loads(content)
                    
                    # Product schema kontrolü
                    if isinstance(data, dict):
                        if data.get('@type') == 'Product' or 'Product' in str(data.get('@type', '')):
                            title = data.get('name') or data.get('title')
                            if title:
                                return title
                    
                    # Array içinde Product arama
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and (item.get('@type') == 'Product' or 'Product' in str(item.get('@type', ''))):
                                title = item.get('name') or item.get('title')
                                if title:
                                    return title
                    
                    # Nested structure kontrolü
                    if isinstance(data, dict) and '@graph' in data:
                        for item in data.get('@graph', []):
                            if isinstance(item, dict) and (item.get('@type') == 'Product' or 'Product' in str(item.get('@type', ''))):
                                title = item.get('name') or item.get('title')
                                if title:
                                    return title
                except json.JSONDecodeError:
                    continue
                except Exception:
                    continue
        except Exception:
            pass
        
        return None
    
    async def _extract_title_from_meta(self, page) -> Optional[str]:
        """Meta tags'den başlık çek"""
        try:
            meta_selectors = [
                'meta[property="og:title"]',
                'meta[name="twitter:title"]',
                'meta[property="product:title"]',
                'meta[name="title"]'
            ]
            
            for selector in meta_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        title = await element.get_attribute('content')
                        if title and title.strip():
                            return title.strip()
                except:
                    continue
        except Exception:
            pass
        
        return None
    
    async def _extract_price_from_jsonld(self, page) -> Optional[Dict[str, str]]:
        """JSON-LD structured data'dan fiyat çek"""
        try:
            scripts = await page.query_selector_all('script[type="application/ld+json"]')
            for script in scripts:
                try:
                    content = await script.text_content()
                    if not content:
                        continue
                    
                    data = json.loads(content)
                    
                    # Product schema kontrolü
                    product_data = None
                    if isinstance(data, dict):
                        if data.get('@type') == 'Product' or 'Product' in str(data.get('@type', '')):
                            product_data = data
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and (item.get('@type') == 'Product' or 'Product' in str(item.get('@type', ''))):
                                product_data = item
                                break
                    
                    if product_data and 'offers' in product_data:
                        offers = product_data['offers']
                        
                        # Single offer
                        if isinstance(offers, dict):
                            price_value = offers.get('price') or offers.get('priceCurrency')
                            if price_value:
                                price_str = self._format_price(price_value)
                                return {'current': price_str, 'old': None}
                        
                        # Multiple offers
                        elif isinstance(offers, list) and len(offers) > 0:
                            prices = []
                            for offer in offers:
                                if isinstance(offer, dict):
                                    price_value = offer.get('price')
                                    if price_value:
                                        prices.append(float(str(price_value).replace(',', '.')))
                            
                            if prices:
                                prices.sort()
                                current = self._format_price(prices[0])
                                old = self._format_price(prices[-1]) if len(prices) > 1 and prices[-1] != prices[0] else None
                                return {'current': current, 'old': old}
                
                except json.JSONDecodeError:
                    continue
                except Exception:
                    continue
        except Exception:
            pass
        
        return None
    
    async def _extract_price_from_meta(self, page) -> Optional[Dict[str, str]]:
        """Meta tags'den fiyat çek"""
        try:
            meta_selectors = [
                ('meta[property="product:price:amount"]', 'current'),
                ('meta[name="price"]', 'current'),
                ('meta[itemprop="price"]', 'current')
            ]
            
            price = None
            for selector, _ in meta_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        price_value = await element.get_attribute('content')
                        if price_value:
                            price = self._format_price(price_value)
                            break
                except:
                    continue
            
            if price:
                return {'current': price, 'old': None}
        except Exception:
            pass
        
        return None
    
    async def _extract_price_from_dom(self, page, url: str) -> Optional[Dict[str, str]]:
        """DOM selector'larından fiyat çek"""
        try:
            all_prices = []
            
            for selector in self.price_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        price_text = await element.text_content()
                        if price_text and price_text.strip():
                            # Fiyat formatlarını parse et
                            prices = self._parse_price_text(price_text)
                            for p in prices:
                                if p and p not in all_prices:
                                    all_prices.append(p)
                except:
                    continue
            
            if all_prices:
                # Fiyatları sayısal değere çevir ve sırala
                price_nums = []
                for p in all_prices:
                    try:
                        num = self._price_to_float(p)
                        if 10 <= num <= 100000:  # Mantıklı fiyat aralığı
                            price_nums.append({'value': num, 'text': p})
                    except:
                        continue
                
                if price_nums:
                    price_nums.sort(key=lambda x: x['value'])
                    current = price_nums[0]['text']
                    old = price_nums[-1]['text'] if len(price_nums) > 1 and price_nums[-1]['value'] != price_nums[0]['value'] else None
                    return {'current': current, 'old': old}
        except Exception as e:
            print(f"[DEBUG] DOM fiyat çekme hatası: {e}")
        
        return None
    
    async def _extract_price_with_regex(self, page) -> Optional[Dict[str, str]]:
        """Regex ile sayfadan fiyat çek (son çare)"""
        try:
            page_text = await page.text_content()
            if not page_text:
                return None
            
            # Türkçe format: 1.299,99 veya 1.299,99 TL
            price_patterns = [
                r'([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})\s*(?:₺|TL|tl)?',
                r'([0-9]{1,3}(?:\.[0-9]{3})*\.[0-9]{2})\s*(?:₺|TL|tl)?',  # İngilizce format
                r'([0-9]+(?:\.[0-9]{2})?)\s*(?:₺|TL|tl)'
            ]
            
            all_prices = []
            for pattern in price_patterns:
                matches = re.findall(pattern, page_text)
                for match in matches:
                    try:
                        num = self._price_to_float(match)
                        if 10 <= num <= 100000:
                            formatted = self._format_price(match)
                            if formatted not in all_prices:
                                all_prices.append({'value': num, 'text': formatted})
                    except:
                        continue
            
            if all_prices:
                all_prices.sort(key=lambda x: x['value'])
                current = all_prices[0]['text']
                old = all_prices[-1]['text'] if len(all_prices) > 1 and all_prices[-1]['value'] != all_prices[0]['value'] else None
                return {'current': current, 'old': old}
        except Exception:
            pass
        
        return None
    
    async def _extract_image_from_jsonld(self, page) -> Optional[Dict[str, any]]:
        """JSON-LD structured data'dan görsel çek"""
        try:
            scripts = await page.query_selector_all('script[type="application/ld+json"]')
            for script in scripts:
                try:
                    content = await script.text_content()
                    if not content:
                        continue
                    
                    data = json.loads(content)
                    
                    # Product schema kontrolü
                    product_data = None
                    if isinstance(data, dict):
                        if data.get('@type') == 'Product' or 'Product' in str(data.get('@type', '')):
                            product_data = data
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and (item.get('@type') == 'Product' or 'Product' in str(item.get('@type', ''))):
                                product_data = item
                                break
                    
                    if product_data:
                        images = []
                        
                        # image field
                        if 'image' in product_data:
                            img = product_data['image']
                            if isinstance(img, str):
                                images.append(img)
                            elif isinstance(img, list):
                                images.extend([i for i in img if isinstance(i, str)])
                            elif isinstance(img, dict) and 'url' in img:
                                images.append(img['url'])
                        
                        # images field
                        if 'images' in product_data:
                            imgs = product_data['images']
                            if isinstance(imgs, list):
                                for img in imgs:
                                    if isinstance(img, str):
                                        images.append(img)
                                    elif isinstance(img, dict) and 'url' in img:
                                        images.append(img['url'])
                        
                        if images:
                            # İlk görseli ana görsel olarak seç
                            primary = self._normalize_image_url(images[0], page.url)
                            all_images = [self._normalize_image_url(img, page.url) for img in images]
                            return {'primary': primary, 'all': all_images}
                
                except json.JSONDecodeError:
                    continue
                except Exception:
                    continue
        except Exception:
            pass
        
        return None
    
    async def _extract_image_from_meta(self, page) -> Optional[Dict[str, any]]:
        """Meta tags'den görsel çek"""
        try:
            meta_selectors = [
                'meta[property="og:image"]',
                'meta[name="twitter:image"]',
                'meta[property="product:image"]',
                'meta[itemprop="image"]'
            ]
            
            images = []
            for selector in meta_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        img_url = await element.get_attribute('content')
                        if img_url and img_url not in images:
                            images.append(img_url)
                except:
                    continue
            
            if images:
                primary = self._normalize_image_url(images[0], page.url)
                all_images = [self._normalize_image_url(img, page.url) for img in images]
                return {'primary': primary, 'all': all_images}
        except Exception:
            pass
        
        return None
    
    async def _extract_image_from_dom(self, page, url: str) -> Optional[Dict[str, any]]:
        """DOM selector'larından görsel çek"""
        try:
            all_product_images = []
            
            for selector in self.image_selectors:
                try:
                    img_elements = await page.query_selector_all(selector)
                    for img_element in img_elements:
                        # srcset kontrolü
                        srcset = await img_element.get_attribute('srcset')
                        src = await img_element.get_attribute('src')
                        data_src = await img_element.get_attribute('data-src')
                        data_lazy_src = await img_element.get_attribute('data-lazy-src')
                        alt_text = await img_element.get_attribute('alt') or ''
                        
                        # srcset'ten en yüksek kaliteli görseli al
                        if srcset:
                            srcset_parts = srcset.split(',')
                            highest_res = None
                            max_width = 0
                            
                            for part in srcset_parts:
                                part = part.strip()
                                if ' ' in part:
                                    url_part, size_part = part.rsplit(' ', 1)
                                    if 'w' in size_part:
                                        try:
                                            width = int(size_part.replace('w', ''))
                                            if width > max_width:
                                                max_width = width
                                                highest_res = url_part.strip()
                                        except ValueError:
                                            continue
                            
                            if highest_res:
                                src = highest_res
                        
                        # data-src ve data-lazy-src kontrolü (lazy loading)
                        if data_lazy_src and not src:
                            src = data_lazy_src
                        if data_src and not src:
                            src = data_src
                        
                        if src:
                            # Relative URL'yi absolute yap
                            src = self._normalize_image_url(src, url)
                            
                            # Skip keyword kontrolü
                            src_lower = src.lower()
                            if any(keyword in src_lower for keyword in self.skip_keywords):
                                continue
                            
                            # Görsel formatı kontrolü
                            if any(ext in src_lower for ext in ['.jpg', '.jpeg', '.webp', '.png']):
                                # Priority score hesapla
                                priority_score = 0
                                alt_lower = alt_text.lower()
                                
                                if 'product' in alt_lower or 'ürün' in alt_lower or 'resmi' in alt_lower:
                                    priority_score += 100
                                if max_width > 0:
                                    priority_score += max_width / 10
                                
                                all_product_images.append({
                                    'url': src,
                                    'width': max_width if max_width > 0 else 0,
                                    'priority': priority_score,
                                    'alt': alt_text
                                })
                except Exception as e:
                    continue
            
            if all_product_images:
                # Priority score'a göre sırala
                all_product_images.sort(key=lambda x: x.get('priority', 0), reverse=True)
                
                # En yüksek öncelikli görseli seç
                selected = all_product_images[0]
                primary = selected['url']
                
                # Tüm görselleri topla (tekrar yoksa)
                all_images = [img['url'] for img in all_product_images if img['url'] not in [primary]]
                all_images.insert(0, primary)
                
                return {'primary': primary, 'all': all_images}
        except Exception as e:
            print(f"[DEBUG] DOM görsel çekme hatası: {e}")
        
        return None
    
    async def _extract_image_fallback(self, page, url: str) -> Optional[Dict[str, any]]:
        """Fallback: Tüm görselleri tara"""
        try:
            all_imgs = await page.query_selector_all('img')
            candidate_images = []
            
            for img in all_imgs:
                try:
                    src = await img.get_attribute('src')
                    if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.webp', '.png']):
                        # Skip keyword kontrolü
                        if not any(keyword in src.lower() for keyword in self.skip_keywords):
                            # Boyut kontrolü
                            try:
                                size = await img.bounding_box()
                                if size and size['width'] > 150 and size['height'] > 150:
                                    src = self._normalize_image_url(src, url)
                                    if src not in candidate_images:
                                        candidate_images.append(src)
                            except:
                                src = self._normalize_image_url(src, url)
                                if src not in candidate_images:
                                    candidate_images.append(src)
                except:
                    continue
                    
            if candidate_images:
                return {'primary': candidate_images[0], 'all': candidate_images}
        except Exception:
            pass
        
        return None

    # ========== Utility Methods ==========
    
    def _clean_title(self, title: str) -> str:
        """Başlığı temizle ve formatla"""
        if not title:
            return None
        
        title = title.strip().upper()
        title = re.sub(r'[^\w\s\-\.]', '', title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title
    
    def _format_price(self, price_value) -> str:
        """Fiyatı formatla (TL ekle)"""
        if not price_value:
            return None
        
        price_str = str(price_value).strip()
        
        # Sayısal değeri float'a çevir
        try:
            price_float = self._price_to_float(price_str)
            
            # Türkçe formatına çevir
            if price_float >= 1000:
                formatted = f"{price_float:,.2f} TL".replace(',', 'X').replace('.', ',').replace('X', '.')
            else:
                formatted = f"{price_float:.2f} TL".replace('.', ',')
            
            return formatted
        except:
            # Eğer parse edilemezse, direkt TL ekle
            if 'TL' not in price_str.upper() and '₺' not in price_str:
                return f"{price_str} TL"
            return price_str
    
    def _price_to_float(self, price_str: str) -> float:
        """Fiyat string'ini float'a çevir"""
        if not price_str:
            return 0.0
        
        # Temizle
        price_clean = re.sub(r'[^\d,\.]', '', str(price_str))
        
        # Türkçe format: 1.299,99
        if ',' in price_clean and '.' in price_clean:
            # Nokta binlik, virgül ondalık
            price_clean = price_clean.replace('.', '').replace(',', '.')
        # İngilizce format: 1,299.99 veya 1299.99
        elif ',' in price_clean:
            price_clean = price_clean.replace(',', '')
        # Sadece nokta: 1299.99
        elif '.' in price_clean:
            # Son 2 haneyi ondalık olarak ayır
            parts = price_clean.split('.')
            if len(parts) == 2 and len(parts[1]) == 2:
                price_clean = price_clean
            else:
                price_clean = price_clean.replace('.', '')
        
        try:
            return float(price_clean)
        except:
            return 0.0
    
    def _parse_price_text(self, text: str) -> List[str]:
        """Fiyat metninden fiyatları parse et"""
        if not text:
            return []
        
        prices = []
        
        # Türkçe format: 1.299,99 veya 1.299,99 TL
        pattern1 = r'([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2})'
        matches1 = re.findall(pattern1, text)
        prices.extend(matches1)
        
        # İngilizce format: 1,299.99 veya 1299.99
        pattern2 = r'([0-9]{1,3}(?:\.[0-9]{3})*\.[0-9]{2})'
        matches2 = re.findall(pattern2, text)
        prices.extend(matches2)
        
        # Basit format: 199.99 veya 199 TL
        pattern3 = r'([0-9]+(?:\.[0-9]{2})?)'
        matches3 = re.findall(pattern3, text)
        prices.extend(matches3)
        
        return list(set(prices))  # Duplicate'leri kaldır
    
    def _normalize_image_url(self, img_url: str, base_url: str) -> str:
        """Görsel URL'sini normalize et (relative -> absolute)"""
        if not img_url:
            return None
        
        # Zaten absolute URL ise
        if img_url.startswith('http://') or img_url.startswith('https://'):
            return img_url
        
        # Protocol-relative URL
        if img_url.startswith('//'):
            return 'https:' + img_url
        
        # Relative URL
        if img_url.startswith('/'):
            parsed = urlparse(base_url)
            return f"{parsed.scheme}://{parsed.netloc}{img_url}"
        
        # Diğer durumlar için base URL ile birleştir
        parsed = urlparse(base_url)
        return f"{parsed.scheme}://{parsed.netloc}/{img_url.lstrip('/')}"


# Global instance
universal_scraper = UniversalScraper()
