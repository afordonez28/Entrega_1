import { showNotification, toggleForm, getBase64 } from './utils.js';

let currentEditIdx = null;

async function createOrUpdateEnemy(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const imageFile = formData.get('image');
    try {
        let imageBase64;
        if (imageFile && imageFile.size > 0) {
            imageBase64 = await getBase64(imageFile);
        } else if (currentEditIdx !== null) {
            const enemies = await fetch('/api/enemies/').then(r => r.json());
            imageBase64 = enemies[currentEditIdx].image;
        } else {
            throw new Error('La imagen es requerida');
        }
        const enemyData = {
            name: formData.get('name'),
            speed: parseFloat(formData.get('speed')),
            jump: parseFloat(formData.get('jump')),
            hit_speed: parseInt(formData.get('hit_speed')),
            health: parseInt(formData.get('health')),
            type: formData.get('type'),
            spawn: parseFloat(formData.get('spawn')),
            probability_spawn: parseFloat(formData.get('probability_spawn')),
            image: imageBase64
        };
        if (currentEditIdx !== null) {
            const response = await fetch(`/api/enemies/${currentEditIdx}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(enemyData)
            });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Error al actualizar enemigo');
            }
            showNotification('Enemigo actualizado exitosamente');
        } else {
            const response = await fetch('/api/enemies/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(enemyData)
            });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Error al crear enemigo');
            }
            showNotification('Enemigo creado exitosamente');
        }
        event.target.reset();
        document.getElementById('imagePreview').style.backgroundImage = '';
        toggleForm('enemyForm');
        loadEnemies();
        currentEditIdx = null;
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function deleteAllEnemies() {
    if (!confirm('¿Seguro que quieres eliminar todos los enemigos?')) return;
    try {
        const response = await fetch('/api/enemies/', { method: 'DELETE' });
        if (!response.ok) throw new Error('Error al eliminar enemigos');
        showNotification('Todos los enemigos eliminados');
        loadEnemies();
        loadDeletedEnemies();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function loadEnemies() {
    const list = document.getElementById('enemiesList');
    list.innerHTML = '';
    try {
        const response = await fetch('/api/enemies/');
        const enemies = await response.json();
        if (!enemies.length) {
            list.innerHTML = '<p>No hay enemigos registrados.</p>';
            return;
        }
        enemies.forEach((enemy, idx) => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <div class="card-image" style="background-image:url('${enemy.image}')"></div>
                <h3>${enemy.name}</h3>
                <p><b>Tipo:</b> ${enemy.type}</p>
                <p><b>Salud:</b> ${enemy.health}</p>
                <p><b>Velocidad:</b> ${enemy.speed}</p>
                <p><b>Salto:</b> ${enemy.jump}</p>
                <p><b>Vel. golpe:</b> ${enemy.hit_speed}</p>
                <p><b>Spawn:</b> ${enemy.spawn}</p>
                <p><b>Prob. Spawn:</b> ${enemy.probability_spawn}</p>
                <button class="btn-warning" data-idx="${idx}">Editar</button>
            `;
            card.querySelector('.btn-warning').onclick = () => editEnemy(idx);
            list.appendChild(card);
        });
    } catch (error) {
        list.innerHTML = '<p>Error al cargar enemigos.</p>';
    }
}

async function loadDeletedEnemies() {
    const list = document.getElementById('deletedEnemiesList');
    list.innerHTML = '';
    const response = await fetch('/api/enemies/history/');
    const deleted = await response.json();
    if (!deleted.length) {
        list.innerHTML = '<li>No hay histórico.</li>';
        return;
    }
    deleted.forEach(enemy => {
        const li = document.createElement('li');
        li.innerText = `${enemy.name} (Tipo: ${enemy.type}, Salud: ${enemy.health})`;
        list.appendChild(li);
    });
}

function editEnemy(idx) {
    fetch('/api/enemies/').then(r => r.json()).then(enemies => {
        const enemy = enemies[idx];
        const form = document.getElementById('enemyForm');
        form.name.value = enemy.name;
        form.speed.value = enemy.speed;
        form.jump.value = enemy.jump;
        form.hit_speed.value = enemy.hit_speed;
        form.health.value = enemy.health;
        form.type.value = enemy.type;
        form.spawn.value = enemy.spawn;
        form.probability_spawn.value = enemy.probability_spawn;
        document.getElementById('imagePreview').style.backgroundImage = `url('${enemy.image}')`;
        toggleForm('enemyForm');
        currentEditIdx = idx;
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('toggleEnemyFormBtn').addEventListener('click', () => {
        toggleForm('enemyForm');
        currentEditIdx = null;
    });
    document.getElementById('enemyForm').addEventListener('submit', createOrUpdateEnemy);
    document.getElementById('deleteAllEnemies').addEventListener('click', deleteAllEnemies);
    document.getElementById('cancelEnemyForm').addEventListener('click', () => {
        toggleForm('enemyForm');
        currentEditIdx = null;
    });
    loadEnemies();
    loadDeletedEnemies();
});