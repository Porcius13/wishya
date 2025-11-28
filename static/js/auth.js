/**
 * Client-side Authentication Check
 * localStorage tabanlı kimlik doğrulama
 */

// Check if user is logged in
function checkAuth() {
    const user = StorageManager.getCurrentUser();
    return user !== null && user.isLoggedIn === true;
}

// Get current user
function getCurrentUser() {
    return StorageManager.getCurrentUser();
}

// Require auth - redirect to login if not authenticated
function requireAuth() {
    if (!checkAuth()) {
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Logout
function logout() {
    StorageManager.logout();
    window.location.href = '/';
}

// Initialize auth check on page load
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a protected page
    const protectedPages = ['/dashboard', '/profile', '/collections'];
    const currentPath = window.location.pathname;
    
    if (protectedPages.some(page => currentPath.startsWith(page))) {
        if (!checkAuth()) {
            window.location.href = '/login?redirect=' + encodeURIComponent(currentPath);
        }
    }
    
    // Update UI based on auth status
    const user = getCurrentUser();
    if (user) {
        // Update header with user info
        const userElements = document.querySelectorAll('[data-user-name]');
        userElements.forEach(el => {
            el.textContent = user.username;
        });
        
        // Show logged-in UI elements
        const loggedInElements = document.querySelectorAll('[data-logged-in]');
        loggedInElements.forEach(el => {
            el.style.display = '';
        });
        
        // Hide logged-out UI elements
        const loggedOutElements = document.querySelectorAll('[data-logged-out]');
        loggedOutElements.forEach(el => {
            el.style.display = 'none';
        });
    } else {
        // Show logged-out UI elements
        const loggedOutElements = document.querySelectorAll('[data-logged-out]');
        loggedOutElements.forEach(el => {
            el.style.display = '';
        });
        
        // Hide logged-in UI elements
        const loggedInElements = document.querySelectorAll('[data-logged-in]');
        loggedInElements.forEach(el => {
            el.style.display = 'none';
        });
    }
});

// Export for use in other scripts
if (typeof window !== 'undefined') {
    window.checkAuth = checkAuth;
    window.getCurrentUser = getCurrentUser;
    window.requireAuth = requireAuth;
    window.logout = logout;
}

