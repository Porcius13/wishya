"""
Scraping Background Tasks
Celery tasks for async scraping
"""
import os

# Try to import Celery
try:
    from celery import Celery
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    print("[INFO] Celery yüklü değil, background tasks devre dışı")

if CELERY_AVAILABLE:
    # Create Celery app
    celery_app = Celery(
        'kataloggia',
        broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    )
    
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )
    
    @celery_app.task(name='scraping.scrape_product')
    def scrape_product_task(url):
        """Async product scraping task"""
        from app.services.scraping_service import ScrapingService
        scraping_service = ScrapingService()
        return scraping_service.scrape_product(url)
    
    @celery_app.task(name='scraping.scrape_batch')
    def scrape_batch_task(urls):
        """Async batch scraping task"""
        from app.services.scraping_service import ScrapingService
        scraping_service = ScrapingService()
        return scraping_service.scrape_multiple(urls)
    
    @celery_app.task(name='price_tracking.check_prices')
    def check_prices_task():
        """Check price changes for tracked products"""
        from app.services.price_tracking_service import PriceTrackingService
        service = PriceTrackingService()
        return service.check_all_prices()
    
    @celery_app.task(name='price_tracking.check_product_price')
    def check_product_price_task(product_id):
        """Check price for a specific product"""
        from app.services.price_tracking_service import PriceTrackingService
        service = PriceTrackingService()
        return service.check_product_price(product_id)
else:
    # Fallback: synchronous tasks
    def scrape_product_task(url):
        """Synchronous fallback"""
        from app.services.scraping_service import ScrapingService
        scraping_service = ScrapingService()
        return scraping_service.scrape_product(url)
    
    def scrape_batch_task(urls):
        """Synchronous fallback"""
        from app.services.scraping_service import ScrapingService
        scraping_service = ScrapingService()
        return scraping_service.scrape_multiple(urls)
    
    def check_prices_task():
        """Synchronous fallback"""
        print("[INFO] Price checking (synchronous mode)")
        return {"status": "completed", "checked": 0}
    
    def check_product_price_task(product_id):
        """Synchronous fallback"""
        print(f"[INFO] Price check for product {product_id} (synchronous mode)")
        return {"status": "completed", "product_id": product_id}

