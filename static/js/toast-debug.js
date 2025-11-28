/**
 * Toast Debug Helper
 * Test toast notifications
 */

// Test function - call from browser console
window.testToast = function() {
    if (typeof toast !== 'undefined') {
        toast.success('Test başarılı! Toast çalışıyor ✅');
        setTimeout(() => toast.error('Hata testi ❌'), 1000);
        setTimeout(() => toast.warning('Uyarı testi ⚠️'), 2000);
        setTimeout(() => toast.info('Bilgi testi ℹ️'), 3000);
    } else {
        alert('Toast manager yüklenmemiş!');
    }
};

console.log('Toast debug helper loaded. Call testToast() to test.');

