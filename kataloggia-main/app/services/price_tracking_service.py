"""
Price Tracking Service
Background price checking service
"""
from app.models.price_tracking import PriceTracking
from app.services.scraping_service import ScrapingService

class PriceTrackingService:
    """Price tracking business logic"""
    
    def __init__(self):
        self.scraping_service = ScrapingService()

    def _parse_price(self, value):
        """Fiyat string'ini güvenli şekilde floata çevirir."""
        if value is None:
            return None

        import re

        # Her şeyi stringe çevir
        s = str(value)

        # Sadece sayı, nokta ve virgül kalsın
        s = re.sub(r"[^\d,\.]", "", s)

        # Hiç rakam yoksa boş say
        if not re.search(r"\d", s):
            return None

        # Örnek formatlar:
        #  - "1.299,99" (TR)
        #  - "1,299.99" (EN)
        #  - "1299,99"
        #  - "1299.99"
        #  - "1 299,99 TL" vs.

        if "," in s and "." in s:
            # İkisi de varsa: varsayılan Türk formatı: 1.299,99 -> 1299.99
            if s.rfind(",") > s.rfind("."):
                s = s.replace(".", "").replace(",", ".")
            else:
                # Çok istisnai durum, virgülleri at
                s = s.replace(",", "")
        elif "," in s and "." not in s:
            # Tek virgül: 1299,99 -> 1299.99 gibi
            s = s.replace(",", ".")
        else:
            # Sadece nokta veya düz sayı: 1,299.99 gibi durumlarda virgülü sil
            s = s.replace(",", "")

        try:
            return float(s)
        except ValueError:
            return None
    
    def check_all_prices(self):
        """Tüm takip edilen ürünlerin fiyatlarını kontrol et"""
        try:
            # Get all active tracking records
            trackings = PriceTracking.get_all_active()
            
            results = {
                'checked': 0,
                'updated': 0,
                'notifications': []
            }
            
            for tracking in trackings:
                try:
                    result = self.check_product_price(tracking.product_id)
                    results['checked'] += 1
                    
                    if result.get('price_changed'):
                        results['updated'] += 1
                        results['notifications'].append({
                            'product_id': tracking.product_id,
                            'old_price': result.get('old_price'),
                            'new_price': result.get('new_price'),
                            'change': result.get('price_change')
                        })
                except Exception as e:
                    print(f"Error checking price for product {tracking.product_id}: {e}")
                    continue
            
            return results
        except Exception as e:
            print(f"Error in check_all_prices: {e}")
            return {'checked': 0, 'updated': 0, 'notifications': []}
    
    def check_product_price(self, product_id):
        """Belirli bir ürünün fiyatını kontrol et"""
        try:
            from app.models.product import Product
            
            product = Product.get_by_id(product_id)
            if not product:
                return {'error': 'Product not found'}
            
            # Scrape current price
            scraped_data = self.scraping_service.scrape_product(product.url)
            
            if not scraped_data or not scraped_data.get('price'):
                return {'error': 'Could not scrape price'}
            
            new_price = scraped_data['price']
            old_price = product.current_price or product.price

            # Fiyat değişimini hesapla (numeric)
            change_info = self._calculate_price_change(old_price, new_price)
            change_amount = change_info.get('amount', 0)

            # Küçük oynamaları önemseme, en az 0.5 TL düşüş olsun
            price_changed = change_amount < -0.5
            
            if price_changed:
                # TODO: Ürün modelinde price update implement edilebilir
                tracking = PriceTracking.get_by_product_and_user(product_id, product.user_id)
                if tracking:
                    PriceTracking.update_price(tracking[0], new_price)
            
            return {
                'product_id': product_id,
                'old_price': old_price,
                'new_price': new_price,
                'price_changed': price_changed,
                'price_change': change_info
            }
        except Exception as e:
            print(f"Error in check_product_price: {e}")
            return {'error': str(e)}
    
    def _calculate_price_change(self, old_price, new_price):
        """Fiyat değişimini hesapla (daha dayanıklı parsing ile)."""
        try:
            old_num = self._parse_price(old_price)
            new_num = self._parse_price(new_price)

            # Parse edemediysek veya eski fiyat saçmaysa
            if old_num is None or new_num is None or old_num <= 0:
                return {'amount': 0, 'percentage': 0}

            change = new_num - old_num
            percentage = (change / old_num) * 100

            return {
                'amount': round(change, 2),
                'percentage': round(percentage, 2)
            }
        except Exception:
            return {'amount': 0, 'percentage': 0}

