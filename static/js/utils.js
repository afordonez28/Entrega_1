// Función para mostrar notificaciones
export function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// Función para mostrar/ocultar formularios
export function toggleForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
        if (form.style.display === 'none') {
            form.reset();
            const preview = form.querySelector('.image-preview');
            if (preview) preview.style.backgroundImage = '';
        }
    }
}

// Función para convertir imagen a Base64
export function getBase64(file) {
    return new Promise((resolve, reject) => {
        if (!file) {
            reject(new Error('No se ha seleccionado ningún archivo'));
            return;
        }
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

// Función para previsualizar imagen
export function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    const file = input.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.style.backgroundImage = `url(${e.target.result})`;
        };
        reader.readAsDataURL(file);
    } else {
        preview.style.backgroundImage = '';
    }
}

// Previsualización de imágenes para input file
document.addEventListener('DOMContentLoaded', function() {
    const playerImage = document.getElementById('playerImage');
    const enemyImage = document.getElementById('enemyImage');
    if (playerImage) {
        playerImage.addEventListener('change', function() {
            previewImage(this, 'imagePreview');
        });
    }
    if (enemyImage) {
        enemyImage.addEventListener('change', function() {
            previewImage(this, 'imagePreview');
        });
    }
});