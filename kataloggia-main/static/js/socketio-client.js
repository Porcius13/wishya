/**
 * SocketIO Client
 * Real-time communication client
 */

class SocketIOClient {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    connect() {
        // Check if SocketIO is available
        if (typeof io === 'undefined') {
            console.warn('[SocketIO] Socket.IO library not loaded');
            return;
        }

        try {
            this.socket = io();

            this.socket.on('connect', () => {
                this.connected = true;
                this.reconnectAttempts = 0;
                console.log('[SocketIO] Connected');
                this.onConnected();
            });

            this.socket.on('disconnect', () => {
                this.connected = false;
                console.log('[SocketIO] Disconnected');
                this.onDisconnected();
            });

            this.socket.on('connect_error', (error) => {
                console.error('[SocketIO] Connection error:', error);
                this.handleReconnect();
            });

            // Price update events
            this.socket.on('price_update', (data) => {
                console.log('[SocketIO] Price update:', data);
                this.onPriceUpdate(data);
            });

            this.socket.on('price_drop', (data) => {
                console.log('[SocketIO] Price drop:', data);
                this.onPriceDrop(data);
            });

            // Notification events
            this.socket.on('notification', (data) => {
                console.log('[SocketIO] Notification:', data);
                this.onNotification(data);
            });

            this.socket.on('notifications', (data) => {
                console.log('[SocketIO] Notifications:', data);
                this.onNotifications(data);
            });

            // Product events
            this.socket.on('product_added', (data) => {
                console.log('[SocketIO] Product added:', data);
                this.onProductAdded(data);
            });

            // Subscription events
            this.socket.on('subscribed', (data) => {
                console.log('[SocketIO] Subscribed:', data);
            });

            this.socket.on('unsubscribed', (data) => {
                console.log('[SocketIO] Unsubscribed:', data);
            });

        } catch (error) {
            console.error('[SocketIO] Connection failed:', error);
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.connected = false;
        }
    }

    subscribeToPriceUpdates(productId) {
        if (this.socket && this.connected) {
            this.socket.emit('subscribe_price_updates', {
                product_id: productId
            });
        }
    }

    unsubscribeFromPriceUpdates(productId) {
        if (this.socket && this.connected) {
            this.socket.emit('unsubscribe_price_updates', {
                product_id: productId
            });
        }
    }

    requestNotifications() {
        if (this.socket && this.connected) {
            this.socket.emit('get_notifications');
        }
    }

    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`[SocketIO] Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                this.connect();
            }, 2000 * this.reconnectAttempts);
        } else {
            console.error('[SocketIO] Max reconnection attempts reached');
        }
    }

    // Event handlers (can be overridden)
    onConnected() {
        // Override in your code
        if (window.toast) {
            toast.info('Real-time bağlantısı kuruldu');
        }
    }

    onDisconnected() {
        // Override in your code
        if (window.toast) {
            toast.warning('Real-time bağlantısı kesildi');
        }
    }

    onPriceUpdate(data) {
        // Override in your code
        if (window.toast) {
            toast.info(data.message || 'Fiyat güncellendi');
        }
    }

    onPriceDrop(data) {
        // Override in your code
        if (window.toast) {
            toast.success(data.message || 'Fiyat düştü!');
        }
    }

    onNotification(data) {
        // Override in your code
        if (window.toast) {
            toast.info(data.message);
        }
    }

    onNotifications(data) {
        // Override in your code
        // Update notification UI
    }

    onProductAdded(data) {
        // Override in your code
        if (window.toast) {
            toast.success(data.message || 'Ürün eklendi');
        }
    }
}

// Global instance
const socketClient = new SocketIOClient();

// Auto-connect on page load
document.addEventListener('DOMContentLoaded', () => {
    socketClient.connect();
});

// Export for global use
window.SocketIOClient = SocketIOClient;
window.socketClient = socketClient;

