"""
Notification Service
Real-time notification management
"""
from datetime import datetime
from flask_socketio import SocketIO

class NotificationService:
    """Notification service with SocketIO support"""
    
    def __init__(self, socketio=None):
        self.socketio = socketio
    
    def send_price_update(self, user_id, product_id, old_price, new_price, change):
        """Fiyat güncellemesi bildirimi gönder"""
        if self.socketio:
            # User-specific notification
            self.socketio.emit('price_update', {
                'product_id': product_id,
                'old_price': old_price,
                'new_price': new_price,
                'change': change,
                'message': f'Fiyat değişti: {old_price} → {new_price}'
            }, room=f"user_{user_id}")
            
            # Product-specific notification
            self.socketio.emit('price_update', {
                'product_id': product_id,
                'old_price': old_price,
                'new_price': new_price,
                'change': change
            }, room=f"product_{product_id}")
    
    def send_notification(self, user_id, notification_type, message, data=None):
        """Genel bildirim gönder"""
        if self.socketio:
            self.socketio.emit('notification', {
                'type': notification_type,
                'message': message,
                'data': data or {},
                'timestamp': str(datetime.now())
            }, room=f"user_{user_id}")
    
    def send_product_added(self, user_id, product):
        """Ürün eklendi bildirimi"""
        if self.socketio:
            self.socketio.emit('product_added', {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'brand': product.brand
                },
                'message': f'{product.name} eklendi'
            }, room=f"user_{user_id}")
    
    def broadcast_price_drop(self, product_id, old_price, new_price, discount):
        """Fiyat düşüşü broadcast (tüm takip edenlere)"""
        if self.socketio:
            self.socketio.emit('price_drop', {
                'product_id': product_id,
                'old_price': old_price,
                'new_price': new_price,
                'discount': discount,
                'message': f'Fiyat düştü! {discount}% indirim'
            }, room=f"product_{product_id}")

