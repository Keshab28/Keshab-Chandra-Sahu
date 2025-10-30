let lastUpdateTime = new Date();
let refreshInterval;

// Toggle mobile menu
function toggleMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    mobileMenu.classList.toggle('active');
}

// Format time ago
function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000); // difference in seconds
    
    if (diff < 60) return `${diff} seconds ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
    return `${Math.floor(diff / 86400)} days ago`;
}

// Get status color class
function getStatusClass(status) {
    switch(status.toLowerCase()) {
        case 'open': return 'open';
        case 'closed': return 'closed';
        case 'busy': return 'busy';
        case 'empty': return 'empty';
        default: return '';
    }
}

// Create area card HTML
function createAreaCard(area) {
    const statusClass = getStatusClass(area.status);
    const outdatedWarning = area.is_outdated ? 
        '<span class="outdated-warning">⚠ Data might be outdated</span>' : '';
    
    return `
        <div class="area-card" data-area-id="${area.id}">
            <div class="area-header">
                <h3 class="area-name">${area.name}</h3>
                <span class="status-badge ${statusClass}">${area.status}</span>
            </div>
            <div class="area-details">
                <div class="detail-item">
                    <div class="detail-label">People Count</div>
                    <div class="detail-value">${area.people_count}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Capacity</div>
                    <div class="detail-value">${getCapacity(area.status)}</div>
                </div>
            </div>
            <div class="area-footer">
                <span class="update-time">Updated ${area.time_ago}</span>
                ${outdatedWarning}
            </div>
        </div>
    `;
}

// Get capacity based on status
function getCapacity(status) {
    switch(status.toLowerCase()) {
        case 'empty': return '0%';
        case 'open': return '< 30%';
        case 'busy': return '30-75%';
        case 'closed': return '> 75%';
        default: return 'N/A';
    }
}

// Fetch and update areas
async function fetchAndUpdateAreas() {
    try {
        const response = await fetch('/areas');
        const areas = await response.json();
        
        const areasGrid = document.getElementById('areasGrid');
        if (areasGrid) {
            areasGrid.innerHTML = areas.map(area => createAreaCard(area)).join('');
        }
        
        // Update refresh time
        lastUpdateTime = new Date();
        updateRefreshTime();
        
    } catch (error) {
        console.error('Error fetching areas:', error);
    }
}

// Update refresh time display
function updateRefreshTime() {
    const refreshTimeElement = document.getElementById('refreshTime');
    if (refreshTimeElement) {
        const secondsAgo = Math.floor((new Date() - lastUpdateTime) / 1000);
        if (secondsAgo <= 5) {
            refreshTimeElement.textContent = 'Last updated: Just now';
        } else {
            refreshTimeElement.textContent = `Last updated: ${secondsAgo} seconds ago`;
        }
    }
}

// Initialize dashboard
function initDashboard() {
    // Initial fetch
    fetchAndUpdateAreas();
    
    // Set up auto-refresh every 10 seconds
    refreshInterval = setInterval(fetchAndUpdateAreas, 10000);
    // refreshInterval = setInterval(fetchAndUpdateAreas, 10000);
    
    // Update refresh time display every second
    setInterval(updateRefreshTime, 1000);
}

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}