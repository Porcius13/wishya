"""
SocketIO Events
Real-time event handlers
"""
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room

def register_socketio_events(socketio):
    """Register all SocketIO events"""
    
    @socketio.on('connect')
    def handle_connect(auth):
        """Client bağlandığında"""
        if current_user.is_authenticated:
            user_room = f"user_{current_user.id}"
            join_room(user_room)
            emit('connected', {
                'status': 'connected',
                'user_id': current_user.id,
                'username': current_user.username
            })
            print(f"[SOCKETIO] User {current_user.username} connected")
        else:
            emit('error', {'message': 'Authentication required'})
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Client bağlantısı kesildiğinde"""
        if current_user.is_authenticated:
            user_room = f"user_{current_user.id}"
            leave_room(user_room)
            print(f"[SOCKETIO] User {current_user.username} disconnected")
    
    @socketio.on('subscribe_price_updates')
    def handle_subscribe_price_updates(data):
        """Fiyat güncellemelerine abone ol"""
        if current_user.is_authenticated:
            product_id = data.get('product_id')
            if product_id:
                room = f"product_{product_id}"
                join_room(room)
                emit('subscribed', {
                    'room': room,
                    'product_id': product_id
                })
                print(f"[SOCKETIO] User {current_user.username} subscribed to product {product_id}")
    
    @socketio.on('unsubscribe_price_updates')
    def handle_unsubscribe_price_updates(data):
        """Fiyat güncellemelerinden abonelikten çık"""
        if current_user.is_authenticated:
            product_id = data.get('product_id')
            if product_id:
                room = f"product_{product_id}"
                leave_room(room)
                emit('unsubscribed', {
                    'room': room,
                    'product_id': product_id
                })
    
    @socketio.on('get_notifications')
    def handle_get_notifications():
        """Bildirimleri iste"""
        if current_user.is_authenticated:
            # TODO: Get notifications from database
            emit('notifications', {
                'notifications': [],
                'unread_count': 0
            })

