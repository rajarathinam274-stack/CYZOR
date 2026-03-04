/**
 * Budget Planner Logic
 */

/**
 * Set a new budget
 */
async function setNewBudget() {
    const budgetInput = document.getElementById('budgetInput').value;
    const budget = parseFloat(budgetInput);

    if (!budgetInput || isNaN(budget) || budget <= 0) {
        showToast("Please enter a valid budget amount", "error");
        return;
    }

    const payload = { total_budget: budget };

    const data = await apiFetch('/budget', {
        method: 'POST',
        body: JSON.stringify(payload)
    });

    if (!data || data.status !== 'success') {
        showToast("Failed to create budget", "error");
        return;
    }

    currentSessionId = data.data.session_id;
    localStorage.setItem("budget_session_id", currentSessionId);

    showToast(`Budget set to ${formatPrice(budget)}`, "success");
    loadBudget();
}

/**
 * Load and display budget
 */
async function loadBudget() {
    if (!currentSessionId) {
        document.getElementById('budgetStatus').style.display = 'none';
        return;
    }

    const data = await apiFetch(`/budget/${currentSessionId}`);

    if (!data || data.status !== 'success') {
        showToast("Failed to load budget", "error");
        return;
    }

    const budget = data.data;
    document.getElementById('budgetStatus').style.display = 'block';

    // Update summary
    document.getElementById('budgetAmount').textContent = formatPrice(budget.total_budget);
    document.getElementById('totalItems').textContent = budget.total_items;
    document.getElementById('totalCost').textContent = formatPrice(budget.total_spent);
    document.getElementById('remainingBudget').textContent = formatPrice(budget.remaining_budget);

    // Update budget input
    document.getElementById('budgetInput').value = budget.total_budget;

    // Update progress bar
    updateProgressBar(budget.percentage_used, budget.budget_status);

    // Populate shopping list
    const shoppingListBody = document.getElementById('shoppingListBody');
    shoppingListBody.innerHTML = '';

    budget.items.forEach((item) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.product_name}</td>
            <td>${item.store_name}</td>
            <td>${formatPrice(item.price)}</td>
            <td>${item.quantity}</td>
            <td>${formatPrice(item.total)}</td>
            <td>
                <button class="remove-btn" onclick="removeFromBudget(${item.item_id})">Remove</button>
            </td>
        `;
        shoppingListBody.appendChild(row);
    });
}

/**
 * Update progress bar appearance
 */
function updateProgressBar(percentage, status) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');

    progressFill.style.width = Math.min(percentage, 100) + '%';
    progressText.textContent = Math.min(percentage, 100).toFixed(1) + '%';

    // Remove previous status classes
    progressFill.classList.remove('warning', 'danger');

    // Add warning toast at 70%
    if (percentage >= 70 && percentage < 90) {
        progressFill.classList.add('warning');
        if (!progressText.dataset.warned70) {
            showToast("⚠ You're using 70% of your budget!", "warning");
            progressText.dataset.warned70 = 'true';
        }
    }

    // Add danger state at 90%+
    if (percentage >= 90) {
        progressFill.classList.add('danger');
        if (!progressText.dataset.warned90) {
            showToast("🚨 You're approaching your budget limit!", "error");
            progressText.dataset.warned90 = 'true';
        }
    }
}

/**
 * Remove item from budget
 */
async function removeFromBudget(itemId) {
    if (!currentSessionId) return;

    const confirmed = confirm("Are you sure you want to remove this item?");
    if (!confirmed) return;

    const data = await apiFetch(`/budget/${currentSessionId}/items/${itemId}`, {
        method: 'DELETE'
    });

    if (!data || data.status !== 'success') {
        showToast("Failed to remove item", "error");
        return;
    }

    showToast("Item removed from budget", "success");
    loadBudget();
}

/**
 * Export budget as CSV
 */
async function exportBudget() {
    if (!currentSessionId) {
        showToast("No budget to export", "warning");
        return;
    }

    try {
        showSpinner();
        const response = await fetch(`${API_BASE}/budget/${currentSessionId}/export`);
        
        if (!response.ok) {
            showToast("Failed to export budget", "error");
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `budget_${currentSessionId}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showToast("Budget exported successfully!", "success");
    } catch (err) {
        showToast("Export failed", "error");
    } finally {
        hideSpinner();
    }
}
