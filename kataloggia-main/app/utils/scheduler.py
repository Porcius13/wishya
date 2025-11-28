"""
Task Scheduler
Periodic task scheduling (Celery Beat)
"""
import os

# Try to import Celery Beat
try:
    from celery.schedules import crontab
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

if CELERY_AVAILABLE:
    from app.tasks.scraping_tasks import celery_app
    
    # Configure periodic tasks
    celery_app.conf.beat_schedule = {
        # Her saat başı fiyat kontrolü
        'check-prices-hourly': {
            'task': 'price_tracking.check_prices',
            'schedule': crontab(minute=0),  # Her saat başı
        },
        # Her gün gece 2'de temizlik
        'cleanup-old-data': {
            'task': 'maintenance.cleanup_old_data',
            'schedule': crontab(hour=2, minute=0),  # Her gece 02:00
        },
        # Her 6 saatte bir cache temizliği
        'clear-old-cache': {
            'task': 'maintenance.clear_old_cache',
            'schedule': crontab(minute=0, hour='*/6'),  # Her 6 saatte bir
        },
    }
    
    print("[INFO] Celery Beat schedule configured")
else:
    print("[INFO] Celery not available, scheduled tasks disabled")

