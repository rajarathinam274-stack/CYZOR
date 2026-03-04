/**
 * Search and Results Logic
 */

let currentSortMethod = 'price';

/**
 * Perform product search
 */
async function performSearch() {
    const query = document.getElementById('searchInput').value.trim();
    
    if (!query) {
        showToast("Please enter a product name", "warning");
        return;
    }

    const params = new URLSearchParams({
        q: query,
        lat: userLocation.lat,
        lng: userLocation.lng,
        sort_by: currentSortMethod
    });

    const data = await apiFetch(`/products/search?${params}`);
    
    if (!data || data.status !== 'success') {
        showToast("Search failed. Please try again.", "error");
        return;
    }

    currentProduct = data.data;
    displaySearchResults();
    loadPriceHistory();
    scrollToSection('search-results');
}

/**
 * Display search results in table
 */
function displaySearchResults() {
    const resultsSection = document.getElementById('search-results');
    const resultsSummary = document.getElementById('resultsSummary');
    const resultsBody = document.getElementById('resultsBody');

    // Show results section
    resultsSection.classList.remove('hidden');

    // Display summary
    const { product, cheapest_price, highest_price, savings_potential, results } = currentProduct;
    
    resultsSummary.innerHTML = `
        <h3>Found ${results.length} store(s) for "${product}"</h3>
        <p><strong>Cheapest Price:</strong> ${formatPrice(cheapest_price)}</p>
        <p><strong>Highest Price:</strong> ${formatPrice(highest_price)}</p>
        <p><strong>You can save:</strong> <span style="color: #4CAF50; font-weight: bold;">${formatPrice(savings_potential)}</span></p>
    `;

    // Clear table
    resultsBody.innerHTML = '';

    // Populate results
    results.forEach((result) => {
        const row = document.createElement('tr');
        row.className = result.is_cheapest ? 'cheapest' : '';

        const distanceText = result.distance_km !== null 
            ? `${result.distance_km.toFixed(1)}km` 
            : 'â€”';

        const badgeHTML = result.is_cheapest 
            ? '<span class="best-deal-badge">BEST DEAL</span>' 
            : '';

        row.innerHTML = `
            <td><strong>${result.store_name}</strong></td>
            <td><span class="price">${formatPrice(result.price)}</span>${badgeHTML}</td>
            <td>${distanceText}</td>
            <td>${getStockDisplay(result.stock_status)}</td>
            <td><span class="rating">${formatStars(result.rating)}</span> ${result.rating.toFixed(1)}/5</td>
            <td>
                <button class="btn btn-primary" onclick="addToBudget(
                    ${result.store_id},
                    ${currentProduct.product_id},
                    '${currentProduct.product}',
                    '${result.store_name}',
                    ${result.price}
                )">Add</button>
            </td>
        `;
        resultsBody.appendChild(row);
    });
}

/**
 * Load and display price history chart
 */
async function loadPriceHistory() {
    if (!currentProduct || !currentProduct.product_id) return;

    const data = await apiFetch(`/products/${currentProduct.product_id}/price-history`);
    
    if (!data || data.status !== 'success' || !data.data.history_by_store) {
        return;
    }

    const historyData = data.data.history_by_store;
    
    // Prepare chart data
    const chartCtx = document.getElementById('priceChart').getContext('2d');
    
    // Destroy existing chart if any
    if (priceChart) {
        priceChart.destroy();
    }

    const datasets = [];
    const colors = ['#2E860E', '#FF9800', '#2196F3', '#E91E63', '#4CAF50'];
    
    let dateLabels = [];

    Object.entries(historyData).forEach(([storeId, storeData], index) => {
        if (index === 0) {
            dateLabels = storeData.dates;
        }

        datasets.push({
            label: storeData.store_name,
            data: storeData.prices,
            borderColor: colors[index % colors.length],
            backgroundColor: colors[index % colors.length] + '20',
            borderWidth: 2,
            fill: false,
            tension: 0.3,
            pointRadius: 4,
            pointBackgroundColor: colors[index % colors.length],
            pointBorderWidth: 0
        });
    });

    priceChart = new Chart(chartCtx, {
        type: 'line',
        data: {
            labels: dateLabels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Price (₹)'
                    }
                }
            }
        }
    });
}

/**
 * Sort search results
 */
function sortResults(method, buttonElement) {
    currentSortMethod = method;

    // Update active button
    document.querySelectorAll('.sort-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    if (buttonElement) {
        buttonElement.classList.add('active');
    }

    // Re-fetch and display
    performSearch();
}

/**
 * Add product to budget
 */
function addToBudget(storeId, productId, productName, storeName, price) {
    if (!currentSessionId) {
        showToast("Please set a budget first", "warning");
        scrollToSection('budget-section');
        return;
    }

    // Prompt for quantity
    const quantity = prompt(`How many of "${productName}" from ${storeName}?`, "1");
    
    if (quantity === null || quantity === "") return;

    const qty = parseInt(quantity);
    if (isNaN(qty) || qty < 1) {
        showToast("Please enter a valid quantity", "error");
        return;
    }

    addItemToBudget(productId, storeId, price, qty);
}

/**
 * Add item to budget via API
 */
async function addItemToBudget(productId, storeId, price, quantity) {
    const payload = {
        product_id: productId,
        store_id: storeId,
        price_at_add: price,
        quantity: quantity
    };

    const data = await apiFetch(`/budget/${currentSessionId}/items`, {
        method: 'POST',
        body: JSON.stringify(payload)
    });

    if (!data || data.status !== 'success') {
        showToast("Failed to add item to budget", "error");
        return;
    }

    showToast(`Added ${quantity}x ${data.data.product_name} to budget`, "success");
    loadBudget();
}

