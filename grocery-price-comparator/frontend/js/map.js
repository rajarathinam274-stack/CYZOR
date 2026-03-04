/**
 * Leaflet.js Map Integration
 * Uses OpenStreetMap tiles — no API key required.
 */

let map = null;
let markers = [];
let nearbyStores = [];
let userMarker = null;

/**
 * Initialize Leaflet Map
 */
function initializeMap() {
    const mapElement = document.getElementById('map');
    if (!mapElement) return;

    // Check if Leaflet is loaded
    if (typeof L === 'undefined') {
        showMapFallback("Leaflet map library not loaded.");
        return;
    }

    // Fix default icon paths for Leaflet
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet/dist/images/marker-icon-2x.png',
        iconUrl: 'https://unpkg.com/leaflet/dist/images/marker-icon.png',
        shadowUrl: 'https://unpkg.com/leaflet/dist/images/marker-shadow.png',
    });

    map = L.map('map').setView([userLocation.lat, userLocation.lng], 13);

    // Add OpenStreetMap tile layer (free, no API key needed)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);

    // Add user location marker (green dot)
    const userIcon = L.divIcon({
        className: '',
        html: '<div style="width:16px;height:16px;background:#2E860E;border:3px solid #fff;border-radius:50%;box-shadow:0 0 6px rgba(0,0,0,0.4);"></div>',
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    });

    userMarker = L.marker([userLocation.lat, userLocation.lng], { icon: userIcon })
        .addTo(map)
        .bindPopup('<strong>📍 Your Location</strong>')
        .openPopup();

    // Load nearby stores from backend
    loadNearbyStores();
}

/**
 * Load nearby stores from backend REST API
 */
async function loadNearbyStores() {
    const params = new URLSearchParams({
        lat: userLocation.lat,
        lng: userLocation.lng,
        radius: 50   // larger radius — stores are in Chennai dataset
    });

    const data = await apiFetch(`/stores/nearby?${params}`);

    if (!data || data.status !== 'success') {
        // Fallback: load all stores if none found nearby
        const allData = await apiFetch('/stores');
        if (!allData || allData.status !== 'success') {
            showToast("Failed to load stores", "error");
            displayStoresList([]);
            return;
        }
        nearbyStores = allData.data.stores.map(s => ({ ...s, distance_km: null }));
    } else {
        nearbyStores = data.data.stores;
        // If none within radius, fall back to all stores
        if (nearbyStores.length === 0) {
            const allData = await apiFetch('/stores');
            if (allData && allData.status === 'success') {
                nearbyStores = allData.data.stores.map(s => ({ ...s, distance_km: null }));
            }
        }
    }

    displayStoresOnMap();
    displayStoresList();
}

/**
 * Display store markers on Leaflet map
 */
function displayStoresOnMap() {
    if (!map) return;

    // Clear existing markers
    markers.forEach(m => map.removeLayer(m));
    markers = [];

    const storeIcon = L.divIcon({
        className: '',
        html: '<div style="width:20px;height:20px;background:#FFA500;border:3px solid #fff;border-radius:50%;box-shadow:0 0 6px rgba(0,0,0,0.4);"></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
    });

    nearbyStores.forEach((store) => {
        if (!store.latitude || !store.longitude) return;

        const marker = L.marker([store.latitude, store.longitude], { icon: storeIcon })
            .addTo(map)
            .bindPopup(`
                <div style="font-family: Arial; min-width: 160px;">
                    <strong style="font-size:1rem;">🛒 ${store.store_name}</strong><br>
                    <span style="color:#555;">📍 ${store.address || ''}</span><br>
                    ${store.distance_km !== null && store.distance_km !== undefined
                    ? `<span>🚗 ${store.distance_km.toFixed(1)} km away</span><br>` : ''}
                    <span>⭐ ${store.rating ? store.rating.toFixed(1) : 'N/A'}/5
                        (${store.review_count || 0} reviews)</span><br>
                    <a href="https://www.openstreetmap.org/?mlat=${store.latitude}&mlon=${store.longitude}&zoom=16"
                       target="_blank" style="color:#2E860E;font-weight:bold;">Get Directions →</a>
                </div>
            `);

        // Highlight sidebar item on marker click
        marker.on('click', () => {
            const item = document.querySelector(`[data-store-id="${store.store_id}"]`);
            if (item) {
                item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                item.style.background = '#e8f5e9';
                setTimeout(() => item.style.background = '', 1500);
            }
        });

        markers.push(marker);
    });

    // Fit map to show all markers
    if (markers.length > 0) {
        const group = L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.2));
    }
}

/**
 * Display stores list in sidebar
 */
function displayStoresList() {
    const sidebar = document.getElementById('storesSidebar');
    if (!sidebar) return;
    sidebar.innerHTML = '';

    if (!nearbyStores || nearbyStores.length === 0) {
        sidebar.innerHTML = '<p style="padding:15px;color:#777;">No stores found.</p>';
        return;
    }

    nearbyStores.forEach((store) => {
        const storeItem = document.createElement('div');
        storeItem.className = 'store-item';
        storeItem.dataset.storeId = store.store_id;
        storeItem.innerHTML = `
            <div class="store-item-name">${store.store_name}</div>
            <div class="store-item-info">
                📍 ${store.address || 'Chennai'}<br>
                ${store.distance_km !== null && store.distance_km !== undefined
                ? `🚗 ${store.distance_km.toFixed(1)} km &nbsp;` : ''}
                ⭐ ${store.rating ? store.rating.toFixed(1) : 'N/A'}/5
                (${store.review_count || 0} reviews)
            </div>
        `;

        // Pan map to store on sidebar click
        storeItem.addEventListener('click', () => {
            if (map && store.latitude && store.longitude) {
                map.setView([store.latitude, store.longitude], 15);
                // Open the popup for this marker
                const marker = markers.find(m => {
                    const ll = m.getLatLng();
                    return Math.abs(ll.lat - store.latitude) < 0.0001 &&
                        Math.abs(ll.lng - store.longitude) < 0.0001;
                });
                if (marker) marker.openPopup();
            }
        });

        sidebar.appendChild(storeItem);
    });
}

/**
 * Show fallback message if map fails to load
 */
function showMapFallback(reason = '') {
    const mapElement = document.getElementById('map');
    if (!mapElement) return;

    mapElement.innerHTML = `
        <div style="
            padding: 40px 20px;
            text-align: center;
            background: #F4F4F4;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
        ">
            <div>
                <p style="font-size:2rem;">🗺️</p>
                <p style="color:#666;font-size:0.95rem;">
                    Map unavailable${reason ? ': ' + reason : '.'}<br>
                    Showing store list below.
                </p>
            </div>
        </div>
    `;

    // Still load stores into sidebar
    loadNearbyStores();
}

// Initialize map when page loads
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initializeMap, 500);
});
