/**
 * 🎨 Modern UI JavaScript - Görünür İyileştirmeler
 * Toast notifications, loading states, animations
 */

// ============================================
// TOAST NOTIFICATION SYSTEM
// ============================================
class ToastManager {
    constructor() {
        this.container = this.createContainer();
        this.toasts = [];
    }

    createContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', duration = 5000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        toast.innerHTML = `
            <div class="toast-icon">${icons[type] || icons.info}</div>
            <div class="toast-content">
                <div class="toast-title">${this.getTitle(type)}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
            <div class="toast-progress"></div>
        `;

        this.container.appendChild(toast);
        this.toasts.push(toast);

        // Force reflow and trigger animation
        void toast.offsetWidth; // Force reflow
        
        // Trigger animation
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        // Auto remove
        setTimeout(() => {
            this.remove(toast);
        }, duration);

        return toast;
    }

    getTitle(type) {
        const titles = {
            success: 'Başarılı',
            error: 'Hata',
            warning: 'Uyarı',
            info: 'Bilgi'
        };
        return titles[type] || titles.info;
    }

    remove(toast) {
        toast.classList.add('hiding');
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
            this.toasts = this.toasts.filter(t => t !== toast);
        }, 300);
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Global toast instance
let toast;
try {
    // Initialize toast manager
    toast = new ToastManager();
    
    // Make sure it's available globally
    window.toast = toast;
    
    console.log('[Toast] ✅ Toast manager initialized successfully');
    
    // Test toast (optional - uncomment to test on load)
    // setTimeout(() => {
    //     toast.success('Toast sistemi çalışıyor!');
    // }, 1000);
} catch (error) {
    console.error('[Toast] ❌ Error initializing toast manager:', error);
    // Fallback to alert
    toast = {
        success: (msg) => { console.log('Success:', msg); alert('Success: ' + msg); },
        error: (msg) => { console.log('Error:', msg); alert('Error: ' + msg); },
        warning: (msg) => { console.log('Warning:', msg); alert('Warning: ' + msg); },
        info: (msg) => { console.log('Info:', msg); alert('Info: ' + msg); }
    };
    window.toast = toast;
}

// ============================================
// LOADING STATE MANAGER
// ============================================
class LoadingManager {
    static showButton(button) {
        if (!button) return;
        
        button.classList.add('btn-loading');
        button.disabled = true;
        const originalText = button.textContent;
        button.dataset.originalText = originalText;
    }

    static hideButton(button) {
        if (!button) return;
        
        button.classList.remove('btn-loading');
        button.disabled = false;
        if (button.dataset.originalText) {
            button.textContent = button.dataset.originalText;
        }
    }

    static showSpinner(container) {
        const spinner = document.createElement('div');
        spinner.className = 'spinner spinner-large';
        spinner.id = 'loading-spinner';
        container.appendChild(spinner);
        return spinner;
    }

    static hideSpinner() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }
}

// ============================================
// SKELETON LOADING
// ============================================
class SkeletonLoader {
    static createCard() {
        return `
            <div class="skeleton-card">
                <div class="skeleton-image"></div>
                <div class="skeleton-content">
                    <div class="skeleton-line short"></div>
                    <div class="skeleton-line medium"></div>
                    <div class="skeleton-line long"></div>
                    <div class="skeleton-line long" style="margin-top: 20px;"></div>
                </div>
            </div>
        `;
    }

    static show(container, count = 6) {
        container.innerHTML = '';
        for (let i = 0; i < count; i++) {
            container.insertAdjacentHTML('beforeend', this.createCard());
        }
    }

    static hide(container) {
        const skeletons = container.querySelectorAll('.skeleton-card');
        skeletons.forEach(skeleton => {
            skeleton.style.opacity = '0';
            setTimeout(() => skeleton.remove(), 300);
        });
    }
}

// ============================================
// CONFIRMATION DIALOG
// ============================================
class ConfirmDialog {
    static show(message, title = 'Onay Gerekli') {
        return new Promise((resolve) => {
            const overlay = document.createElement('div');
            overlay.className = 'confirm-overlay';
            
            overlay.innerHTML = `
                <div class="confirm-dialog">
                    <div class="confirm-title">${title}</div>
                    <div class="confirm-message">${message}</div>
                    <div class="confirm-actions">
                        <button class="confirm-btn confirm-btn-cancel">İptal</button>
                        <button class="confirm-btn confirm-btn-confirm">Onayla</button>
                    </div>
                </div>
            `;

            document.body.appendChild(overlay);

            const cancelBtn = overlay.querySelector('.confirm-btn-cancel');
            const confirmBtn = overlay.querySelector('.confirm-btn-confirm');

            const close = (result) => {
                overlay.style.opacity = '0';
                setTimeout(() => {
                    overlay.remove();
                    resolve(result);
                }, 200);
            };

            cancelBtn.addEventListener('click', () => close(false));
            confirmBtn.addEventListener('click', () => close(true));
            
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    close(false);
                }
            });
        });
    }
}

// ============================================
// PRODUCT CARD ANIMATIONS
// ============================================
class ProductCardAnimations {
    static add(card) {
        card.classList.add('adding');
        setTimeout(() => {
            card.classList.remove('adding');
        }, 500);
    }

    static remove(card, callback) {
        card.classList.add('removing');
        setTimeout(() => {
            if (callback) callback();
        }, 300);
    }

    static highlight(card) {
        card.style.transform = 'scale(1.05)';
        card.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.2)';
        setTimeout(() => {
            card.style.transform = '';
            card.style.boxShadow = '';
        }, 500);
    }
}

// ============================================
// IMAGE LOADING HANDLER
// ============================================
class ImageLoader {
    static handle(img) {
        img.classList.add('loading');
        
        const handleLoad = () => {
            img.classList.remove('loading');
            img.style.opacity = '0';
            setTimeout(() => {
                img.style.opacity = '1';
            }, 50);
        };

        if (img.complete) {
            handleLoad();
        } else {
            img.addEventListener('load', handleLoad);
            img.addEventListener('error', () => {
                img.classList.remove('loading');
            });
        }
    }
}

// ============================================
// FORM ENHANCEMENTS
// ============================================
class FormEnhancer {
    static enhance(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            form.addEventListener('submit', (e) => {
                LoadingManager.showButton(submitBtn);
            });
        }

        // Add ripple effect to buttons
        form.querySelectorAll('button').forEach(btn => {
            btn.classList.add('btn-ripple');
        });
    }
}

// ============================================
// AUTO-INITIALIZE
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    // Enhance all forms
    document.querySelectorAll('form').forEach(form => {
        FormEnhancer.enhance(form);
    });

    // Handle image loading
    document.querySelectorAll('.product-image').forEach(img => {
        ImageLoader.handle(img);
    });

    // Add fade-in animation to product cards
    document.querySelectorAll('.product-card').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
});

// ============================================
// EXPORT FOR GLOBAL USE
// ============================================
window.ToastManager = ToastManager;
window.toast = toast;
window.LoadingManager = LoadingManager;
window.SkeletonLoader = SkeletonLoader;
window.ConfirmDialog = ConfirmDialog;
window.ProductCardAnimations = ProductCardAnimations;
window.ImageLoader = ImageLoader;
window.FormEnhancer = FormEnhancer;

