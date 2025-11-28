/**
 * localStorage Utility for Wishya
 * Tüm kullanıcı verilerini localStorage'da saklar
 */

const StorageManager = {
    // Storage keys
    KEYS: {
        USER: 'wishya_user',
        USERS: 'wishya_users', // All registered users
        PRODUCTS: 'wishya_products',
        COLLECTIONS: 'wishya_collections',
        PRICE_TRACKING: 'wishya_price_tracking',
        SETTINGS: 'wishya_settings'
    },

    // User Management
    saveUser(user) {
        try {
            const userData = {
                id: user.id || this.generateId(),
                username: user.username,
                email: user.email,
                profile_url: user.profile_url || `user_${this.generateId().substring(0, 8)}`,
                created_at: user.created_at || new Date().toISOString(),
                isLoggedIn: true
            };
            localStorage.setItem(this.KEYS.USER, JSON.stringify(userData));
            return userData;
        } catch (e) {
            console.error('User kaydetme hatası:', e);
            return null;
        }
    },

    getCurrentUser() {
        try {
            const userStr = localStorage.getItem(this.KEYS.USER);
            if (!userStr) return null;
            const user = JSON.parse(userStr);
            return user.isLoggedIn ? user : null;
        } catch (e) {
            console.error('User okuma hatası:', e);
            return null;
        }
    },

    logout() {
        try {
            const user = this.getCurrentUser();
            if (user) {
                user.isLoggedIn = false;
                localStorage.setItem(this.KEYS.USER, JSON.stringify(user));
            }
        } catch (e) {
            console.error('Logout hatası:', e);
        }
    },

    // Products Management
    saveProduct(product) {
        try {
            const user = this.getCurrentUser();
            if (!user) {
                throw new Error('Kullanıcı giriş yapmamış');
            }

            const products = this.getProducts();
            const productData = {
                id: product.id || this.generateId(),
                user_id: user.id,
                name: product.name,
                price: product.price,
                image: product.image,
                brand: product.brand,
                url: product.url,
                old_price: product.old_price || null,
                current_price: product.current_price || product.price,
                discount_percentage: product.discount_percentage || null,
                images: product.images || (product.image ? [product.image] : []),
                discount_info: product.discount_info || null,
                created_at: product.created_at || new Date().toISOString()
            };

            // Check if product already exists
            const existingIndex = products.findIndex(p => p.id === productData.id);
            if (existingIndex >= 0) {
                products[existingIndex] = productData;
            } else {
                products.push(productData);
            }

            localStorage.setItem(this.KEYS.PRODUCTS, JSON.stringify(products));
            return productData;
        } catch (e) {
            console.error('Ürün kaydetme hatası:', e);
            throw e;
        }
    },

    getProducts(userId = null) {
        try {
            const productsStr = localStorage.getItem(this.KEYS.PRODUCTS);
            if (!productsStr) return [];
            
            const products = JSON.parse(productsStr);
            if (userId) {
                return products.filter(p => p.user_id === userId);
            }
            return products;
        } catch (e) {
            console.error('Ürün okuma hatası:', e);
            return [];
        }
    },

    getProductById(productId) {
        const products = this.getProducts();
        return products.find(p => p.id === productId) || null;
    },

    deleteProduct(productId) {
        try {
            const user = this.getCurrentUser();
            if (!user) {
                throw new Error('Kullanıcı giriş yapmamış');
            }

            const products = this.getProducts();
            const filtered = products.filter(p => !(p.id === productId && p.user_id === user.id));
            localStorage.setItem(this.KEYS.PRODUCTS, JSON.stringify(filtered));
            
            // Also remove from collections
            const collections = this.getCollections();
            collections.forEach(collection => {
                if (collection.products && collection.products.includes(productId)) {
                    collection.products = collection.products.filter(id => id !== productId);
                }
            });
            localStorage.setItem(this.KEYS.COLLECTIONS, JSON.stringify(collections));
            
            return true;
        } catch (e) {
            console.error('Ürün silme hatası:', e);
            return false;
        }
    },

    // Collections Management
    saveCollection(collection) {
        try {
            const user = this.getCurrentUser();
            if (!user) {
                throw new Error('Kullanıcı giriş yapmamış');
            }

            const collections = this.getCollections();
            const collectionData = {
                id: collection.id || this.generateId(),
                user_id: user.id,
                name: collection.name,
                description: collection.description || '',
                type: collection.type || 'favorites',
                is_public: collection.is_public !== undefined ? collection.is_public : true,
                share_url: collection.share_url || `collection_${this.generateId().substring(0, 8)}`,
                products: collection.products || [],
                created_at: collection.created_at || new Date().toISOString()
            };

            const existingIndex = collections.findIndex(c => c.id === collectionData.id);
            if (existingIndex >= 0) {
                collections[existingIndex] = collectionData;
            } else {
                collections.push(collectionData);
            }

            localStorage.setItem(this.KEYS.COLLECTIONS, JSON.stringify(collections));
            return collectionData;
        } catch (e) {
            console.error('Koleksiyon kaydetme hatası:', e);
            throw e;
        }
    },

    getCollections(userId = null) {
        try {
            const collectionsStr = localStorage.getItem(this.KEYS.COLLECTIONS);
            if (!collectionsStr) return [];
            
            const collections = JSON.parse(collectionsStr);
            if (userId) {
                return collections.filter(c => c.user_id === userId);
            }
            return collections;
        } catch (e) {
            console.error('Koleksiyon okuma hatası:', e);
            return [];
        }
    },

    getCollectionById(collectionId) {
        const collections = this.getCollections();
        return collections.find(c => c.id === collectionId) || null;
    },

    addProductToCollection(collectionId, productId) {
        try {
            const collection = this.getCollectionById(collectionId);
            if (!collection) {
                throw new Error('Koleksiyon bulunamadı');
            }

            if (!collection.products) {
                collection.products = [];
            }

            if (!collection.products.includes(productId)) {
                collection.products.push(productId);
                this.saveCollection(collection);
            }

            return true;
        } catch (e) {
            console.error('Koleksiyona ürün ekleme hatası:', e);
            return false;
        }
    },

    removeProductFromCollection(collectionId, productId) {
        try {
            const collection = this.getCollectionById(collectionId);
            if (!collection) {
                throw new Error('Koleksiyon bulunamadı');
            }

            if (collection.products) {
                collection.products = collection.products.filter(id => id !== productId);
                this.saveCollection(collection);
            }

            return true;
        } catch (e) {
            console.error('Koleksiyondan ürün çıkarma hatası:', e);
            return false;
        }
    },

    deleteCollection(collectionId) {
        try {
            const collections = this.getCollections();
            const filtered = collections.filter(c => c.id !== collectionId);
            localStorage.setItem(this.KEYS.COLLECTIONS, JSON.stringify(filtered));
            return true;
        } catch (e) {
            console.error('Koleksiyon silme hatası:', e);
            return false;
        }
    },

    // Price Tracking
    savePriceTracking(tracking) {
        try {
            const user = this.getCurrentUser();
            if (!user) {
                throw new Error('Kullanıcı giriş yapmamış');
            }

            const trackings = this.getPriceTrackings();
            const trackingData = {
                id: tracking.id || this.generateId(),
                product_id: tracking.product_id,
                user_id: user.id,
                current_price: tracking.current_price,
                original_price: tracking.original_price || tracking.current_price,
                price_change: tracking.price_change || '0',
                is_active: tracking.is_active !== undefined ? tracking.is_active : true,
                alert_price: tracking.alert_price || null,
                created_at: tracking.created_at || new Date().toISOString(),
                last_checked: tracking.last_checked || new Date().toISOString()
            };

            const existingIndex = trackings.findIndex(t => t.id === trackingData.id);
            if (existingIndex >= 0) {
                trackings[existingIndex] = trackingData;
            } else {
                trackings.push(trackingData);
            }

            localStorage.setItem(this.KEYS.PRICE_TRACKING, JSON.stringify(trackings));
            return trackingData;
        } catch (e) {
            console.error('Fiyat takibi kaydetme hatası:', e);
            throw e;
        }
    },

    getPriceTrackings(userId = null) {
        try {
            const trackingsStr = localStorage.getItem(this.KEYS.PRICE_TRACKING);
            if (!trackingsStr) return [];
            
            const trackings = JSON.parse(trackingsStr);
            if (userId) {
                return trackings.filter(t => t.user_id === userId && t.is_active);
            }
            return trackings.filter(t => t.is_active);
        } catch (e) {
            console.error('Fiyat takibi okuma hatası:', e);
            return [];
        }
    },

    getPriceTrackingByProduct(productId) {
        const user = this.getCurrentUser();
        if (!user) return null;

        const trackings = this.getPriceTrackings(user.id);
        return trackings.find(t => t.product_id === productId) || null;
    },

    removePriceTracking(trackingId) {
        try {
            const trackings = this.getPriceTrackings();
            const tracking = trackings.find(t => t.id === trackingId);
            if (tracking) {
                tracking.is_active = false;
                const allTrackings = JSON.parse(localStorage.getItem(this.KEYS.PRICE_TRACKING) || '[]');
                const index = allTrackings.findIndex(t => t.id === trackingId);
                if (index >= 0) {
                    allTrackings[index] = tracking;
                    localStorage.setItem(this.KEYS.PRICE_TRACKING, JSON.stringify(allTrackings));
                }
            }
            return true;
        } catch (e) {
            console.error('Fiyat takibi kaldırma hatası:', e);
            return false;
        }
    },

    // Settings
    saveSettings(settings) {
        try {
            const currentSettings = this.getSettings();
            const newSettings = { ...currentSettings, ...settings };
            localStorage.setItem(this.KEYS.SETTINGS, JSON.stringify(newSettings));
            return newSettings;
        } catch (e) {
            console.error('Ayarlar kaydetme hatası:', e);
            return null;
        }
    },

    getSettings() {
        try {
            const settingsStr = localStorage.getItem(this.KEYS.SETTINGS);
            return settingsStr ? JSON.parse(settingsStr) : {};
        } catch (e) {
            console.error('Ayarlar okuma hatası:', e);
            return {};
        }
    },

    // Utility
    generateId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    },

    // Clear all data (for testing/logout)
    clearAll() {
        try {
            Object.values(this.KEYS).forEach(key => {
                localStorage.removeItem(key);
            });
            return true;
        } catch (e) {
            console.error('Veri temizleme hatası:', e);
            return false;
        }
    }
};

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.StorageManager = StorageManager;
}

