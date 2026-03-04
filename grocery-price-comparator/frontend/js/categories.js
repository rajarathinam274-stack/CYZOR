/**
 * Categories Nav Bar & Products Browser
 * Fetches categories and products from the backend REST API,
 * renders a scrollable category nav bar and a filterable product grid.
 */

// ─── Category icon & colour map ────────────────────────────────────────────
const CATEGORY_META = {
    'Dairy':         { icon: '🥛', color: '#e3f2fd', accent: '#1565c0' },
    'Vegetables':    { icon: '🥦', color: '#e8f5e9', accent: '#2e7d32' },
    'Fruits':        { icon: '🍎', color: '#fce4ec', accent: '#c62828' },
    'Grains':        { icon: '🌾', color: '#fff8e1', accent: '#f57f17' },
    'Snacks':        { icon: '🍿', color: '#fff3e0', accent: '#e65100' },
    'Beverages':     { icon: '🥤', color: '#e8eaf6', accent: '#283593' },
    'Cleaning':      { icon: '🧹', color: '#f3e5f5', accent: '#6a1b9a' },
    'Personal Care': { icon: '🧴', color: '#fbe9e7', accent: '#bf360c' },
    'Groceries':     { icon: '🛒', color: '#e0f2f1', accent: '#00695c' },
};

// State
let allProducts   = [];
let activeCategory = 'All';
let productSearch  = '';

// ─── Bootstrap on DOM ready ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    buildCategoryNavBar();
    loadProductsForBrowser();
});

// ─── Build the sticky category nav bar ──────────────────────────────────────
async function buildCategoryNavBar() {
    const rail = document.getElementById('categoryRail');
    if (!rail) return;

    // "All" pill first
    rail.innerHTML = '';
    const allPill = makeCategoryPill('All', '🏪', true);
    rail.appendChild(allPill);

    // Fetch categories from backend
    const data = await apiFetch('/products/categories');
    const cats = (data && data.status === 'success')
        ? data.data.categories.map(c => c.category_name || c.name || c)
        : Object.keys(CATEGORY_META);

    // Remove duplicates & build pills
    [...new Set(cats)].forEach(cat => {
        const meta = CATEGORY_META[cat] || { icon: '📦', color: '#f5f5f5', accent: '#555' };
        const pill = makeCategoryPill(cat, meta.icon, false);
        rail.appendChild(pill);
    });
}

function makeCategoryPill(label, icon, active) {
    const btn = document.createElement('button');
    btn.className = 'cat-pill' + (active ? ' active' : '');
    btn.dataset.category = label;
    btn.innerHTML = `<span class="cat-icon">${icon}</span><span class="cat-label">${label}</span>`;
    btn.addEventListener('click', () => selectCategory(label));
    return btn;
}

// ─── Load all products (uses /api/products endpoint) ─────────────────────────
async function loadProductsForBrowser() {
    const grid = document.getElementById('productGrid');
    const countEl = document.getElementById('productCount');
    if (!grid) return;

    grid.innerHTML = '<div class="prod-loading">Loading products…</div>';

    const data = await apiFetch('/products');
    if (!data || data.status !== 'success') {
        grid.innerHTML = '<p class="prod-error">Could not load products. Is the backend running?</p>';
        return;
    }

    allProducts = data.data.products || [];
    if (countEl) countEl.textContent = allProducts.length;
    renderProductGrid();
}

// ─── Category filter ─────────────────────────────────────────────────────────
function selectCategory(cat) {
    activeCategory = cat;
    productSearch = '';

    // Update pill active state
    document.querySelectorAll('.cat-pill').forEach(p => {
        p.classList.toggle('active', p.dataset.category === cat);
    });

    // Clear search box
    const searchBox = document.getElementById('productSearchBox');
    if (searchBox) searchBox.value = '';

    renderProductGrid();

    // Smooth-scroll to products section
    const section = document.getElementById('products-section');
    if (section) section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ─── Product search inside the browser ───────────────────────────────────────
function filterProductsBySearch(query) {
    productSearch = query.toLowerCase().trim();
    renderProductGrid();
}

// ─── Render the product grid ──────────────────────────────────────────────────
function renderProductGrid() {
    const grid = document.getElementById('productGrid');
    const countEl = document.getElementById('productCount');
    if (!grid) return;

    let filtered = allProducts;

    // Filter by category
    if (activeCategory !== 'All') {
        filtered = filtered.filter(p =>
            (p.category || '').toLowerCase() === activeCategory.toLowerCase()
        );
    }

    // Filter by search text
    if (productSearch) {
        filtered = filtered.filter(p =>
            (p.product_name || '').toLowerCase().includes(productSearch)
        );
    }

    if (countEl) countEl.textContent = filtered.length;

    if (filtered.length === 0) {
        grid.innerHTML = `
            <div class="prod-empty">
                <span>🔍</span>
                <p>No products found${activeCategory !== 'All' ? ` in <strong>${activeCategory}</strong>` : ''}${productSearch ? ` matching "<strong>${productSearch}</strong>"` : ''}.</p>
            </div>`;
        return;
    }

    grid.innerHTML = '';
    filtered.forEach(p => {
        const meta = CATEGORY_META[p.category] || { icon: '📦', color: '#f5f5f5', accent: '#555' };
        const card = document.createElement('div');
        card.className = 'prod-card';
        card.style.setProperty('--cat-color', meta.color);
        card.style.setProperty('--cat-accent', meta.accent);

        // Stock badge
        const stockClass = p.stock_status === 'in_stock' ? 'in-stock'
                         : p.stock_status === 'low_stock' ? 'low-stock'
                         : 'out-stock';
        const stockLabel = p.stock_status === 'in_stock' ? '● In Stock'
                         : p.stock_status === 'low_stock' ? '● Low Stock'
                         : '● Out of Stock';

        card.innerHTML = `
            <div class="prod-card-icon">${meta.icon}</div>
            <div class="prod-card-body">
                <div class="prod-card-category" style="color:${meta.accent};">${p.category || 'General'}</div>
                <div class="prod-card-name">${p.product_name || `Product #${p.product_id}`}</div>
                <div class="prod-card-price">₹${(p.cheapest_price || 0).toFixed(2)}
                    <span class="prod-cheapest-store">@ ${p.cheapest_store || '—'}</span>
                </div>
                <div class="prod-card-footer">
                    <span class="stock-tag ${stockClass}">${stockLabel}</span>
                    <button class="prod-search-btn" onclick="quickSearchProduct('${(p.product_name || '').replace(/'/g, "\\'")}')">
                        Compare →
                    </button>
                </div>
            </div>`;
        grid.appendChild(card);
    });
}

// ─── Quick-search a product from its card ────────────────────────────────────
function quickSearchProduct(name) {
    const input = document.getElementById('searchInput');
    if (input) {
        input.value = name;
        scrollToSection('hero');
        // slight delay so scroll finishes, then trigger search
        setTimeout(() => performSearch(), 400);
    }
}
