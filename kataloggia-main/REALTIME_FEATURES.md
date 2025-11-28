# 🔴 Real-time Features - WebSocket Integration

## ✅ Tamamlanan İyileştirmeler

### 1. **Flask-SocketIO Integration**
- ✅ WebSocket server setup
- ✅ Real-time event handlers
- ✅ Room-based messaging
- ✅ User authentication

### 2. **Real-time Events**
- ✅ Price updates
- ✅ Price drop notifications
- ✅ Product added notifications
- ✅ General notifications

### 3. **Client-side Integration**
- ✅ SocketIO client JavaScript
- ✅ Auto-reconnect
- ✅ Event handlers
- ✅ Toast integration

## 🚀 Kullanım

### Server Setup

```bash
# Install dependencies
pip install flask-socketio eventlet

# Run with SocketIO
python run.py
```

### Client Setup

```html
<!-- Add SocketIO library -->
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>

<!-- Add client script -->
<script src="{{ url_for('static', filename='js/socketio-client.js') }}"></script>
```

### Custom Event Handlers

```javascript
// Override default handlers
socketClient.onPriceUpdate = function(data) {
    // Custom price update handling
    console.log('Price updated:', data);
    updateProductPrice(data.product_id, data.new_price);
};

socketClient.onPriceDrop = function(data) {
    // Custom price drop handling
    console.log('Price dropped!', data);
    showPriceDropNotification(data);
};

socketClient.onProductAdded = function(data) {
    // Custom product added handling
    console.log('Product added:', data);
    addProductToUI(data.product);
};
```

### Subscribe to Price Updates

```javascript
// Subscribe to specific product
socketClient.subscribeToPriceUpdates('product-id-123');

// Unsubscribe
socketClient.unsubscribeFromPriceUpdates('product-id-123');
```

## 📡 Real-time Events

### Server → Client

#### `price_update`
Fiyat güncellemesi bildirimi
```javascript
{
    product_id: 'uuid',
    old_price: '100 TL',
    new_price: '90 TL',
    change: { amount: -10, percentage: -10 },
    message: 'Fiyat değişti: 100 TL → 90 TL'
}
```

#### `price_drop`
Fiyat düşüşü bildirimi
```javascript
{
    product_id: 'uuid',
    old_price: '100 TL',
    new_price: '80 TL',
    discount: 20,
    message: 'Fiyat düştü! 20% indirim'
}
```

#### `product_added`
Ürün eklendi bildirimi
```javascript
{
    product: {
        id: 'uuid',
        name: 'Ürün Adı',
        price: '100 TL',
        brand: 'Marka'
    },
    message: 'Ürün Adı eklendi'
}
```

#### `notification`
Genel bildirim
```javascript
{
    type: 'info|success|warning|error',
    message: 'Bildirim mesajı',
    data: {},
    timestamp: '2025-01-01T00:00:00'
}
```

### Client → Server

#### `subscribe_price_updates`
Fiyat güncellemelerine abone ol
```javascript
socket.emit('subscribe_price_updates', {
    product_id: 'uuid'
});
```

#### `unsubscribe_price_updates`
Abonelikten çık
```javascript
socket.emit('unsubscribe_price_updates', {
    product_id: 'uuid'
});
```

#### `get_notifications`
Bildirimleri iste
```javascript
socket.emit('get_notifications');
```

## 🎯 Use Cases

### 1. Real-time Price Tracking
```javascript
// Subscribe when user enables tracking
function enablePriceTracking(productId) {
    socketClient.subscribeToPriceUpdates(productId);
}

// Handle price updates
socketClient.onPriceUpdate = function(data) {
    updateProductCard(data.product_id, {
        price: data.new_price,
        oldPrice: data.old_price
    });
    showPriceChangeIndicator(data.change);
};
```

### 2. Price Drop Alerts
```javascript
socketClient.onPriceDrop = function(data) {
    // Show prominent notification
    toast.success(`🎉 Fiyat düştü! ${data.discount}% indirim`, 'success', 10000);
    
    // Update UI
    highlightProduct(data.product_id);
    playNotificationSound();
};
```

### 3. Live Product Updates
```javascript
socketClient.onProductAdded = function(data) {
    // Add product to UI with animation
    addProductCard(data.product);
    ProductCardAnimations.add(newCard);
};
```

## 🔧 Configuration

### Environment Variables

```bash
# SocketIO async mode
export SOCKETIO_ASYNC_MODE=eventlet

# CORS settings (already configured)
# cors_allowed_origins="*"
```

### Server Configuration

```python
# In app/__init__.py
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet'
)
```

## 📊 Performance

### Connection Management
- Auto-reconnect on disconnect
- Max 5 reconnection attempts
- Exponential backoff

### Room-based Messaging
- User-specific rooms: `user_{user_id}`
- Product-specific rooms: `product_{product_id}`
- Efficient message routing

## 🔮 Future Improvements

1. **Presence System**: Show online users
2. **Typing Indicators**: Real-time typing status
3. **Live Chat**: User-to-user messaging
4. **Collaborative Features**: Real-time collaboration
5. **Analytics**: Real-time usage analytics

