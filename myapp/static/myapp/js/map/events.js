/**
 * Map Events Module — Utilities & Keyboard Shortcuts
 * fitToAll đã được khai báo trong sidebar.js
 */

// Phím tắt Ctrl+Shift+D bật/tắt debug panel
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        toggleDebug();
    }
    // Đóng sidebar khi nhấn Escape
    if (e.key === 'Escape' && MapApp.sidebar) {
        MapApp.sidebar.close();
    }
});

// Global error handler
window.addEventListener('error', (e) => {
    if (MapApp.debug) {
        MapApp.debug.log(`JS Error: ${e.message}`, 'error');
    }
});
