/**
 * Global App State and Utilities
 * Handles API calls, user location, and shared state
 */

const DEFAULT_API_PROTOCOL = window.location.protocol.startsWith("http")
    ? window.location.protocol
    : "http:";
const DEFAULT_API_HOST = window.location.hostname || "localhost";
const API_ORIGIN =
    localStorage.getItem("api_origin") || `${DEFAULT_API_PROTOCOL}//${DEFAULT_API_HOST}:8000`;
const API_BASE = `${API_ORIGIN}/api`;

let currentSessionId = localStorage.getItem("budget_session_id") || null;
let currentProduct = null;
let currentStoreId = null;
let userLocation = { lat: 13.0827, lng: 80.2707 }; // Default: Chennai center
let searchResults = [];
let priceChart = null;

// Get user geolocation on page load
document.addEventListener('DOMContentLoaded', () => {
    const statusBar = document.getElementById('api-status-bar');
    if (statusBar) {
        statusBar.textContent = "Cannot connect to backend API at " + API_ORIGIN + " - make sure the FastAPI server is running.";
    }
    initializeApp();
});

function initializeApp() {
    // Check backend connectivity first
    checkApiHealth();

    // Get user location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                console.log("User location obtained:", userLocation);
            },
            (error) => {
                console.log("Could not get user location, using default Chennai coordinates");
            }
        );
    }

    // Setup event listeners
    document.getElementById('searchBtn').addEventListener('click', performSearch);
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    document.getElementById('setBudgetBtn').addEventListener('click', setNewBudget);
    document.getElementById('exportBudgetBtn').addEventListener('click', exportBudget);

    // Load store ratings
    loadStoreRatings();

    // Hamburger menu
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('navLinks');
    if (hamburger) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    // Load existing budget if session exists
    if (currentSessionId) {
        loadBudget();
    }
}

/**
 * Check if the backend API is reachable and update the status indicator
 */
async function checkApiHealth() {
    const indicator = document.getElementById('api-indicator');
    const dot = document.getElementById('api-dot');
    const label = document.getElementById('api-label');
    const statusBar = document.getElementById('api-status-bar');

    try {
        const res = await fetch(`${API_ORIGIN}/health`, {
            signal: AbortSignal.timeout(4000)  // 4-second timeout
        });

        if (res.ok) {
            // âœ… Connected
            if (indicator) {
                indicator.style.background = '#e8f5e9';
                indicator.style.color = '#2e7d32';
                dot.textContent = 'â—';
                label.textContent = 'API Connected';
            }
            if (statusBar) statusBar.style.display = 'none';
        } else {
            throw new Error(`HTTP ${res.status}`);
        }
    } catch (err) {
        // âŒ Not reachable
        console.warn('Backend API not reachable:', err.message);
        if (indicator) {
            indicator.style.background = '#ffebee';
            indicator.style.color = '#c62828';
            dot.textContent = 'â—';
            label.textContent = 'API Offline';
        }
        if (statusBar) statusBar.style.display = 'block';
    }
}

/**
 * Universal fetch wrapper with loading spinner
 */
async function apiFetch(endpoint, options = {}) {
    showSpinner();
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, {
            headers: { "Content-Type": "application/json" },
            ...options
        });

        if (!res.ok) {
            throw new Error(`API error: ${res.status}`);
        }

        const data = await res.json();
        return data;
    } catch (err) {
        console.error("API Error:", err);
        showToast("Connection error. Please try again.", "error");
        return null;
    } finally {
        hideSpinner();
    }
}

/**
 * Show loading spinner
 */
function showSpinner() {
    document.getElementById('loadingSpinner').classList.remove('hidden');
}

/**
 * Hide loading spinner
 */
function hideSpinner() {
    document.getElementById('loadingSpinner').classList.add('hidden');
}

/**
 * Show toast notification
 */
function showToast(message, type = "success") {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    toastContainer.appendChild(toast);

    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Smooth scroll to section
 */
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
    // Close hamburger menu if open
    document.getElementById('navLinks').classList.remove('active');
}

/**
 * Format price with rupee symbol
 */
function formatPrice(price) {
    return `₹${parseFloat(price).toFixed(2)}`;
}

/**
 * Format rating stars
 */
function formatStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalf = (rating - fullStars) >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalf ? 1 : 0);

    let stars = "★".repeat(fullStars);
    if (hasHalf) stars += "½";
    stars += "☆".repeat(emptyStars);
    return stars;
}

/**
 * Get stock status display
 */
function getStockDisplay(status) {
    const statusMap = {
        'in_stock': { icon: 'â—', class: 'stock-in', label: 'In Stock' },
        'low_stock': { icon: 'â—', class: 'stock-low', label: 'Low Stock' },
        'out_of_stock': { icon: 'â—', class: 'stock-out', label: 'Out of Stock' }
    };
    const info = statusMap[status] || statusMap['out_of_stock'];
    return `<span class="stock-indicator ${info.class}"></span>${info.label}`;
}

/**
 * Convert distance to readable format
 */
function formatDistance(km) {
    if (km === null || km === undefined) return "â€”";
    if (km < 1) return `${(km * 1000).toFixed(0)}m`;
    return `${km.toFixed(1)}km`;
}






