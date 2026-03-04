# 🛒 Grocery Price Comparator

**Tagline:** "Shop Smarter. Spend Less."

A full-stack web application that allows users to compare grocery prices across multiple stores in real-time, plan budgets, view nearby stores with geolocation, and read community ratings.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Frontend Usage](#frontend-usage)
- [CSV Data Files](#csv-data-files)

---

## ✨ Features

### 🔍 **Search & Price Comparison**
- Search for grocery products by name
- Compare prices across 5+ stores
- View savings potential (cheapest vs. highest price)
- Sort by price, distance, or rating
- 30-day price history chart for each product

### 🗺️ **Nearby Stores**
- Google Maps integration with store pins
- Color-coded markers (in-stock = green, out-of-stock = red)
- Distance calculation using Haversine formula
- Store details popup on marker click
- Fallback list view if Maps API unavailable

### 💰 **Budget Planner**
- Set and track shopping budget
- Add items directly from search results
- Live total calculation with color-coded progress bar
- Budget alerts at 70% and 90% usage
- Remove items from shopping list
- Export shopping list as CSV

### ⭐ **Store Ratings & Reviews**
- View average ratings and review count
- Write and submit reviews with star ratings
- Latest 2 reviews preview on store cards
- Filter stores by rating or proximity
- Rating breakdown (1-5 star distribution)

### 📱 **Fully Responsive**
- Mobile-first design (320px+)
- Tablet layout optimization (768px+)
- Desktop grid layouts (1200px+)
- Touch-friendly buttons and inputs

---

## 🔧 Tech Stack

### **Backend**
- **Framework:** FastAPI (Python 3.11+)
- **Server:** Uvicorn ASGI
- **Data:** Pandas (CSV operations)
- **Validation:** Pydantic v2
- **CORS:** Enabled for frontend access

### **Frontend**
- **HTML5** - Semantic markup
- **CSS3** - Flexbox, CSS Grid, animations
- **Vanilla JavaScript** - No frameworks
- **Chart.js** - Price history visualizations
- **Google Maps API** - Store location mapping

### **Data Storage**
- **Format:** CSV files (no database required)
- **Files:** 8 CSV tables in `data/` folder
- **Operations:** Pandas read/write with pandas DataFrames

---

## 🗂️ Project Structure

```
grocery-price-comparator/
├── frontend/
│   ├── index.html              # Single-page app
│   ├── css/
│   │   └── style.css           # All styling (19KB)
│   └── js/
│       ├── app.js              # Global state & utilities
│       ├── search.js           # Product search logic
│       ├── budget.js           # Budget planner
│       ├── map.js              # Google Maps
│       └── ratings.js          # Store ratings & reviews
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── data_loader.py          # Singleton CSV manager
│   ├── routes/
│   │   ├── products.py         # Search & price comparison
│   │   ├── stores.py           # Store details & nearby
│   │   ├── budget.py           # Budget sessions & items
│   │   └── ratings.py          # Reviews & ratings
│   └── utils/
│       └── helpers.py          # Distance, formatting utilities
├── data/
│   ├── stores.csv              # 5 stores
│   ├── products.csv            # 20 products
│   ├── categories.csv          # 8 categories
│   ├── product_prices.csv      # 100 price records
│   ├── price_history.csv       # 3000 30-day history records
│   ├── store_ratings.csv       # 56 reviews
│   ├── budget_sessions.csv     # Budget sessions (populated at runtime)
│   └── budget_items.csv        # Shopping list items (populated at runtime)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image config
├── .env                        # Environment variables
└── README.md                   # This file

```

---

## 📦 Installation & Setup

### **Prerequisites**
- Python 3.11 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Google Maps API key (optional, map will gracefully degrade)

### **Step 1: Clone/Download Project**
```bash
cd grocery-price-comparator
```

### **Step 2: Install Python Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 3: (Optional) Configure Google Maps API**
Edit `.env` file:
```
GOOGLE_MAPS_API_KEY=your-actual-google-maps-api-key
```

Or update the `frontend/index.html` line:
```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&libraries=places"></script>
```

### **Step 4: Verify CSV Files Exist**
All 8 CSV files should be in `data/` folder. If missing, they'll be created on first API call.

---

## 🚀 Running the Application

### **Terminal 1: Start Backend API**
```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be available at:
- **Base URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs (Swagger UI)
- **ReDoc:** http://localhost:8000/redoc

### **Terminal 2: Open Frontend**

**Option A: Using Python's built-in server**
```bash
cd frontend
python -m http.server 8001
```
Then open: http://localhost:8001

**Option B: Using VS Code Live Server extension**
- Right-click `frontend/index.html` → "Open with Live Server"

**Option C: Direct file access**
- Simply double-click `frontend/index.html` to open in browser
- Note: Some features may not work due to CORS restrictions

### **Full Stack Test**
1. Open browser to frontend (http://localhost:8001)
2. Search for a product (e.g., "Milk")
3. View price comparison across stores
4. Set a budget and add items
5. Check store ratings and write reviews

---

## 🔌 API Endpoints

### **Products Router** (`/api/products/`)

#### `GET /search?q={query}&lat={lat}&lng={lng}&sort_by={price|distance|rating}`
Search for products with price comparison
```json
{
  "status": "success",
  "data": {
    "product": "Milk 1L",
    "product_id": 1,
    "results": [
      {
        "store_id": 1,
        "store_name": "FreshMart",
        "price": 45.00,
        "stock_status": "in_stock",
        "distance_km": 2.3,
        "rating": 4.2,
        "is_cheapest": true
      }
    ],
    "cheapest_price": 45.00,
    "highest_price": 58.00,
    "savings_potential": 13.00
  }
}
```

#### `GET /`
Get all products with cheapest prices

#### `GET /categories`
Get all product categories

#### `GET /{product_id}/price-history`
Get 30-day price history for charting

---

### **Stores Router** (`/api/stores/`)

#### `GET /`
Get all stores with ratings

#### `GET /nearby?lat={lat}&lng={lng}&radius={km}`
Get nearby stores within radius

#### `GET /{store_id}`
Get detailed store information

#### `GET /{store_id}/stock?category={category}`
Get store stock by category

---

### **Budget Router** (`/api/budget/`)

#### `POST /`
Create new budget session
```json
{
  "total_budget": 5000
}
```

#### `GET /{session_id}`
Get budget summary with items

#### `POST /{session_id}/items`
Add item to shopping list
```json
{
  "product_id": 1,
  "store_id": 2,
  "price_at_add": 45.00,
  "quantity": 2
}
```

#### `DELETE /{session_id}/items/{item_id}`
Remove item from budget

#### `GET /{session_id}/export`
Download shopping list as CSV

---

### **Ratings Router** (`/api/ratings/`)

#### `GET /store/{store_id}`
Get all reviews for a store

#### `POST /store/{store_id}`
Submit new review
```json
{
  "rating": 5,
  "review_text": "Great store with friendly staff!",
  "reviewer_name": "John Doe"
}
```

#### `GET /store/{store_id}/summary`
Get rating summary and breakdown

---

## 🎨 Frontend Usage

### **Search Products**
1. Enter product name in hero search bar
2. Click "Compare Prices" or press Enter
3. View results table with stores, prices, stock status, ratings
4. Sort by Price, Distance, or Rating
5. View 30-day price history chart
6. Click "Add" to add to budget

### **Budget Planner**
1. Scroll to "Budget Planner" section
2. Enter budget amount and click "Set Budget"
3. Add items from search results or manually
4. Watch progress bar update (green → orange → red)
5. Remove items as needed
6. Click "Export Shopping List" to download CSV

### **Nearby Stores Map**
1. Allows geolocation (for distance calculations)
2. Map shows all nearby stores as pins
3. Click pins to see store details
4. Sidebar lists stores sorted by distance
5. Click store in sidebar to pan map

### **Store Ratings**
1. Browse all stores in grid layout
2. See average rating, review count, latest reviews
3. Filter by "All Stores", "Top Rated", or "Nearby"
4. Click "Write a Review" to open modal
5. Enter name, select stars, write review
6. Submit and see live update

---

## 📊 CSV Data Files

### **stores.csv** (5 stores)
```
store_id, store_name, address, latitude, longitude, phone, opening_hours
```

### **products.csv** (20 products)
```
product_id, product_name, category
```

### **categories.csv** (8 categories)
```
category_id, category_name, description
```

### **product_prices.csv** (100 records)
```
price_id, product_id, store_id, price, stock_status, last_updated
stock_status: in_stock | low_stock | out_of_stock
```

### **price_history.csv** (3000 records)
30 days of price data per product per store
```
history_id, product_id, store_id, price, recorded_date
```

### **store_ratings.csv** (56 initial reviews)
```
rating_id, store_id, rating, review_text, reviewer_name, review_date
rating: 1-5 integer
```

### **budget_sessions.csv** (populated at runtime)
```
session_id, total_budget, created_at
session_id format: sess_YYYYMMDDHHmmss
```

### **budget_items.csv** (populated at runtime)
```
item_id, session_id, product_id, store_id, price_at_add, quantity
```

---

## 🎨 Color Scheme

| Element | Color | Hex |
|---------|-------|-----|
| Primary Green | Main branding | #2E860E |
| Secondary Dark Green | Accents, hover | #1A5C07 |
| Orange | Alerts, badges | #FFA500 |
| Red | Danger states | #CC3333 |
| Light Gray | Backgrounds | #F4F4F4 |

---

## 📱 Responsive Breakpoints

- **Mobile:** 320px - 768px (single column)
- **Tablet:** 768px - 1200px (two columns)
- **Desktop:** 1200px+ (three columns, grid layouts)

---

## 🐳 Docker Deployment

### Build Docker Image
```bash
docker build -t grocery-price-comparator .
```

### Run Container
```bash
docker run -p 8000:8000 grocery-price-comparator
```

---

## ⚙️ Environment Variables (.env)

```
GOOGLE_MAPS_API_KEY=your-key-here
DATA_DIR=data/
ALLOWED_ORIGINS=*
DEBUG=True
APP_NAME=Grocery Price Comparator
```

---

## 🔐 Notes

- **No Database:** All data stored in CSV files
- **No Authentication:** Public API, no login required
- **CORS Enabled:** Frontend can call API from any origin
- **CSV Auto-save:** Budget and ratings auto-save to CSV
- **Singleton Pattern:** DataLoader ensures single CSV instance

---

## 📝 Features Checklist

- ✅ Product search and price comparison
- ✅ Results sorted by price/distance/rating
- ✅ BEST DEAL badge highlighting
- ✅ 30-day price history chart
- ✅ Google Maps with store pins
- ✅ Haversine distance calculation
- ✅ Budget session management
- ✅ Shopping list with live totals
- ✅ Color-coded progress bar
- ✅ Budget alert toasts
- ✅ CSV export functionality
- ✅ Store ratings and reviews
- ✅ Star rating selector
- ✅ Fully responsive design
- ✅ Loading spinner overlay
- ✅ Toast notification system
- ✅ All data from CSV files

---

## 🆘 Troubleshooting

### API returns 500 error
- Check CSV files exist in `data/` folder
- Verify column names match expected schema
- Check terminal for detailed error messages

### Map not showing
- Add Google Maps API key to `.env` or `index.html`
- Check browser console for JavaScript errors
- Fallback list view will display if Maps API unavailable

### Budget items not saving
- Ensure `data/budget_items.csv` is writable
- Check API response for validation errors
- Verify session_id stored correctly in localStorage

### CORS errors
- Ensure FastAPI has `allow_origins=["*"]`
- Try accessing from `localhost` instead of IP address

---

## 📚 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Google Maps JavaScript API](https://developers.google.com/maps/documentation/javascript)
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)

---

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ using FastAPI, Python, and Vanilla JavaScript**
