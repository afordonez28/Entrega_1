import { showNotification } from './utils.js';

// Configuración global y tooltips
document.addEventListener('DOMContentLoaded', () => {
    window.addEventListener('unhandledrejection', function() {
        showNotification('Error de conexión con el servidor', 'error');
    });
});