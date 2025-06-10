import { showNotification } from './utils.js';

document.addEventListener('DOMContentLoaded', function() {
    updateStats();
});

async function updateStats() {
    try {
        const response = await fetch('/api/stats/');
        const stats = await response.json();
        displayStats(stats);
    } catch (error) {
        showNotification('Error al cargar estadísticas', 'error');
    }
}

function displayStats(stats) {
    document.getElementById('totalPlayers').textContent = stats.total_players;
    document.getElementById('totalEnemies').textContent = stats.total_enemies;
}