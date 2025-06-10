import { showNotification, toggleForm, getBase64 } from './utils.js';

let currentEditIdx = null;

async function createOrUpdatePlayer(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const imageFile = formData.get('image');
    try {
        let imageBase64;
        if (imageFile && imageFile.size > 0) {
            imageBase64 = await getBase64(imageFile);
        } else if (currentEditIdx !== null) {
            // Mantener la imagen anterior si no cambió
            const players = await fetch('/api/players/').then(r => r.json());
            imageBase64 = players[currentEditIdx].image;
        } else {
            throw new Error('La imagen es requerida');
        }
        const playerData = {
            name: formData.get('name'),
            health: parseInt(formData.get('health')),
            regenerate_health: parseInt(formData.get('regenerate_health')),
            speed: parseFloat(formData.get('speed')),
            jump: parseFloat(formData.get('jump')),
            is_dead: false,
            armor: parseInt(formData.get('armor')),
            hit_speed: parseInt(formData.get('hit_speed')),
            image: imageBase64
        };
        if (currentEditIdx !== null) {
            const response = await fetch(`/api/players/${currentEditIdx}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(playerData)
            });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Error al actualizar jugador');
            }
            showNotification('Jugador actualizado exitosamente');
        } else {
            const response = await fetch('/api/players/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(playerData)
            });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Error al crear jugador');
            }
            showNotification('Jugador creado exitosamente');
        }
        event.target.reset();
        document.getElementById('imagePreview').style.backgroundImage = '';
        toggleForm('playerForm');
        loadPlayers();
        currentEditIdx = null;
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function deleteAllPlayers() {
    if (!confirm('¿Seguro que quieres eliminar todos los jugadores?')) return;
    try {
        const response = await fetch('/api/players/', { method: 'DELETE' });
        if (!response.ok) throw new Error('Error al eliminar jugadores');
        showNotification('Todos los jugadores eliminados');
        loadPlayers();
        loadDeletedPlayers();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

async function loadPlayers() {
    const list = document.getElementById('playersList');
    list.innerHTML = '';
    try {
        const response = await fetch('/api/players/');
        const players = await response.json();
        if (!players.length) {
            list.innerHTML = '<p>No hay jugadores registrados.</p>';
            return;
        }
        players.forEach((player, idx) => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <div class="card-image" style="background-image:url('${player.image}')"></div>
                <h3>${player.name}</h3>
                <p><b>Salud:</b> ${player.health}</p>
                <p><b>Regeneración:</b> ${player.regenerate_health}</p>
                <p><b>Velocidad:</b> ${player.speed}</p>
                <p><b>Salto:</b> ${player.jump}</p>
                <p><b>Armadura:</b> ${player.armor}</p>
                <p><b>Vel. golpe:</b> ${player.hit_speed}</p>
                <button class="btn-warning" data-idx="${idx}">Editar</button>
            `;
            card.querySelector('.btn-warning').onclick = () => editPlayer(idx);
            list.appendChild(card);
        });
    } catch (error) {
        list.innerHTML = '<p>Error al cargar jugadores.</p>';
    }
}

async function loadDeletedPlayers() {
    const list = document.getElementById('deletedPlayersList');
    list.innerHTML = '';
    const response = await fetch('/api/players/history/');
    const deleted = await response.json();
    if (!deleted.length) {
        list.innerHTML = '<li>No hay histórico.</li>';
        return;
    }
    deleted.forEach(player => {
        const li = document.createElement('li');
        li.innerText = `${player.name} (Salud: ${player.health}, Vel: ${player.speed})`;
        list.appendChild(li);
    });
}

function editPlayer(idx) {
    fetch('/api/players/').then(r => r.json()).then(players => {
        const player = players[idx];
        const form = document.getElementById('playerForm');
        form.name.value = player.name;
        form.health.value = player.health;
        form.regenerate_health.value = player.regenerate_health;
        form.speed.value = player.speed;
        form.jump.value = player.jump;
        form.armor.value = player.armor;
        form.hit_speed.value = player.hit_speed;
        document.getElementById('imagePreview').style.backgroundImage = `url('${player.image}')`;
        toggleForm('playerForm');
        currentEditIdx = idx;
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('togglePlayerFormBtn').addEventListener('click', () => {
        toggleForm('playerForm');
        currentEditIdx = null;
    });
    document.getElementById('playerForm').addEventListener('submit', createOrUpdatePlayer);
    document.getElementById('deleteAllPlayers').addEventListener('click', deleteAllPlayers);
    document.getElementById('cancelPlayerForm').addEventListener('click', () => {
        toggleForm('playerForm');
        currentEditIdx = null;
    });
    loadPlayers();
    loadDeletedPlayers();
});