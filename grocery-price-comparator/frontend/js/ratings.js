/**
 * Store Ratings and Reviews Logic
 */

let allStores = [];
let currentReviewStoreId = null;
let selectedRating = 0;

/**
 * Load all stores and their ratings
 */
async function loadStoreRatings() {
    const data = await apiFetch('/stores');

    if (!data || data.status !== 'success') {
        showToast("Failed to load stores", "error");
        return;
    }

    allStores = data.data.stores;
    displayStoreCards('all');
}

/**
 * Display store cards
 */
async function displayStoreCards(filter) {
    const storesGrid = document.getElementById('storesGrid');
    storesGrid.innerHTML = '';

    let storesList = [...allStores];

    // Apply filter
    if (filter === 'top') {
        storesList = storesList.filter((s) => s.rating >= 4);
    } else if (filter === 'nearby') {
        storesList = storesList.sort((a, b) => {
            const distA = Math.sqrt(
                Math.pow(a.latitude - userLocation.lat, 2) +
                Math.pow(a.longitude - userLocation.lng, 2)
            );
            const distB = Math.sqrt(
                Math.pow(b.latitude - userLocation.lat, 2) +
                Math.pow(b.longitude - userLocation.lng, 2)
            );
            return distA - distB;
        });
    }

    // Create cards
    for (const store of storesList) {
        // Keep summary call for API compatibility; card uses store-level rating/count.
        const ratingsData = await apiFetch(`/ratings/store/${store.store_id}/summary`);
        if (!ratingsData || ratingsData.status !== 'success') {
            continue;
        }

        const reviews = await getStoreReviews(store.store_id);

        const card = document.createElement('div');
        card.className = 'store-card';
        card.innerHTML = `
            <div class="store-card-header">
                <h3>${store.store_name}</h3>
                <div class="store-card-address">${store.address}</div>
            </div>

            <div class="store-card-rating">
                <span class="stars">${formatStars(store.rating)}</span>
                <span class="rating-score">${store.rating.toFixed(1)}/5</span>
                <span class="review-count">(${store.review_count} reviews)</span>
            </div>

            <div class="store-card-reviews" id="reviews-${store.store_id}">
                ${reviews.length > 0
                    ? reviews.slice(0, 2).map((r) => `
                        <div class="review-item">
                            <div class="review-stars">${formatStars(r.rating)}</div>
                            <div class="review-text">"${r.review_text.substring(0, 80)}..."</div>
                        </div>
                    `).join('')
                    : '<div style="color: #999; text-align: center; padding: 20px;">No reviews yet</div>'
                }
            </div>

            <button class="write-review-btn" onclick='openReviewModal(${store.store_id}, ${JSON.stringify(store.store_name)})'>
                Write a Review
            </button>
        `;

        storesGrid.appendChild(card);
    }
}

/**
 * Get store reviews
 */
async function getStoreReviews(storeId) {
    const data = await apiFetch(`/ratings/store/${storeId}`);

    if (!data || data.status !== 'success') {
        return [];
    }

    return data.data.reviews;
}

/**
 * Filter stores
 */
function filterStores(filter, buttonElement) {
    // Update active button
    document.querySelectorAll('.filter-btn').forEach((btn) => {
        btn.classList.remove('active');
    });
    if (buttonElement) {
        buttonElement.classList.add('active');
    }

    // Display filtered stores
    displayStoreCards(filter);
}

/**
 * Open review modal
 */
function openReviewModal(storeId, storeName) {
    currentReviewStoreId = storeId;
    selectedRating = 0;

    document.getElementById('modalStoreTitle').textContent = `Review: ${storeName}`;
    document.getElementById('reviewerName').value = '';
    document.getElementById('reviewText').value = '';
    document.getElementById('selectedRating').textContent = 'Select rating';

    // Reset stars
    document.querySelectorAll('.star').forEach((star) => {
        star.classList.remove('selected');
    });

    document.getElementById('reviewModal').classList.remove('hidden');
}

/**
 * Close review modal
 */
function closeReviewModal() {
    document.getElementById('reviewModal').classList.add('hidden');
    currentReviewStoreId = null;
    selectedRating = 0;
}

/**
 * Select star rating
 */
function selectStar(rating) {
    selectedRating = rating;
    document.getElementById('selectedRating').textContent = `${rating} star${rating !== 1 ? 's' : ''} selected`;

    // Update visual
    document.querySelectorAll('.star').forEach((star, index) => {
        if (index < rating) {
            star.classList.add('selected');
        } else {
            star.classList.remove('selected');
        }
    });
}

/**
 * Submit review
 */
async function submitReview(event) {
    event.preventDefault();

    const reviewerName = document.getElementById('reviewerName').value.trim();
    const reviewText = document.getElementById('reviewText').value.trim();

    if (!reviewerName) {
        showToast("Please enter your name", "error");
        return;
    }

    if (selectedRating === 0) {
        showToast("Please select a rating", "error");
        return;
    }

    if (reviewText.length < 10) {
        showToast("Review must be at least 10 characters", "error");
        return;
    }

    const payload = {
        rating: selectedRating,
        review_text: reviewText,
        reviewer_name: reviewerName
    };

    const data = await apiFetch(`/ratings/store/${currentReviewStoreId}`, {
        method: 'POST',
        body: JSON.stringify(payload)
    });

    if (!data || data.status !== 'success') {
        showToast("Failed to submit review", "error");
        return;
    }

    showToast("Review submitted successfully!", "success");
    closeReviewModal();
    loadStoreRatings();
}

// Close modal when clicking overlay
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('reviewModal');
    if (modal) {
        const overlay = modal.querySelector('.modal-overlay');
        overlay.addEventListener('click', closeReviewModal);
    }
});
