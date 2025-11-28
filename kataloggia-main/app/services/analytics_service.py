"""
Analytics Service
Usage analytics and metrics
"""
from datetime import datetime
import json
import os

class AnalyticsService:
    """Analytics service for tracking usage"""
    
    def __init__(self):
        self.events_file = 'logs/analytics.jsonl'
        self.ensure_logs_dir()
    
    def ensure_logs_dir(self):
        """Ensure logs directory exists"""
        if not os.path.exists('logs'):
            os.mkdir('logs')
    
    def track_event(self, event_type, user_id=None, **kwargs):
        """Track an event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            **kwargs
        }
        
        try:
            with open(self.events_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            print(f"Analytics tracking error: {e}")
    
    def track_product_added(self, user_id, product_id):
        """Track product addition"""
        self.track_event('product_added', user_id, product_id=product_id)
    
    def track_product_deleted(self, user_id, product_id):
        """Track product deletion"""
        self.track_event('product_deleted', user_id, product_id=product_id)
    
    def track_scraping(self, user_id, url, success):
        """Track scraping attempt"""
        self.track_event('scraping', user_id, url=url, success=success)
    
    def track_price_check(self, user_id, product_id, price_changed):
        """Track price check"""
        self.track_event('price_check', user_id, product_id=product_id, price_changed=price_changed)
    
    def track_api_call(self, endpoint, method, user_id=None, status_code=200):
        """Track API call"""
        self.track_event('api_call', user_id, 
                        endpoint=endpoint, 
                        method=method, 
                        status_code=status_code)

# Global analytics instance
analytics_service = AnalyticsService()

