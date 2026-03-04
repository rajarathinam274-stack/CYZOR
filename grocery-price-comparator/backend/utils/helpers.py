"""
Helper functions for the Grocery Price Comparator backend.
Includes distance calculations, formatting, and utility functions.
"""

import math
from datetime import datetime


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    
    Returns distance in kilometers.
    """
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    R = 6371
    
    return R * c


def format_price(price: float) -> str:
    """Format price as Indian Rupees with proper formatting."""
    return f"₹{price:.2f}"


def calculate_average_rating(ratings_list: list) -> float:
    """Calculate average rating from a list of rating values."""
    if not ratings_list:
        return 0.0
    return round(sum(ratings_list) / len(ratings_list), 1)


def get_star_display(rating: float) -> str:
    """Convert numeric rating to star display (★☆ format)."""
    full_stars = int(rating)
    half_star = 1 if (rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    
    return "★" * full_stars + ("½" if half_star else "") + "☆" * empty_stars


def get_stock_status_color(status: str) -> str:
    """Return color code for stock status."""
    status_colors = {
        "in_stock": "#4CAF50",      # green
        "low_stock": "#FFA500",     # orange
        "out_of_stock": "#CC3333"   # red
    }
    return status_colors.get(status, "#999999")


def get_stock_status_label(status: str) -> str:
    """Return user-friendly stock status label."""
    status_labels = {
        "in_stock": "✓ In Stock",
        "low_stock": "⚠ Low Stock",
        "out_of_stock": "✗ Out of Stock"
    }
    return status_labels.get(status, "Unknown")


def generate_session_id() -> str:
    """Generate a unique session ID for budget tracking."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"sess_{timestamp}"


def format_datetime(dt_string: str) -> str:
    """Format datetime string to readable format."""
    try:
        dt = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d %b %Y, %I:%M %p")
    except:
        return dt_string


def round_price(price: float) -> float:
    """Round price to 2 decimal places."""
    return round(price, 2)


def calculate_savings_potential(prices: list) -> dict:
    """
    Calculate savings potential for a product across stores.
    Returns dict with min, max, and potential savings.
    """
    if not prices:
        return {"min": 0, "max": 0, "savings": 0}
    
    min_price = min(prices)
    max_price = max(prices)
    savings = max_price - min_price
    
    return {
        "min": round_price(min_price),
        "max": round_price(max_price),
        "savings": round_price(savings)
    }


def paginate_results(items: list, page: int = 1, per_page: int = 10) -> dict:
    """Paginate a list of items."""
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }
