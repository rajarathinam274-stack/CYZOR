"""
Stores Router - Handles store listing, nearby store discovery, and details.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd
from backend.data_loader import data_loader
from backend.utils.helpers import haversine

router = APIRouter()


@router.get("")
async def get_all_stores():
    """Get all stores with their average ratings."""
    try:
        stores_list = []
        
        for _, store in data_loader.stores.iterrows():
            store_id = store['store_id']
            
            # Get average rating
            store_ratings = data_loader.ratings[data_loader.ratings['store_id'] == store_id]
            avg_rating = store_ratings['rating'].mean() if not store_ratings.empty else 0.0
            avg_rating = round(avg_rating, 1)
            review_count = len(store_ratings)
            
            stores_list.append({
                "store_id": int(store_id),
                "store_name": store['store_name'],
                "address": store['address'],
                "latitude": float(store['latitude']),
                "longitude": float(store['longitude']),
                "phone": store['phone'],
                "opening_hours": store['opening_hours'],
                "rating": avg_rating,
                "review_count": review_count
            })
        
        return {
            "status": "success",
            "data": {
                "stores": stores_list,
                "total": len(stores_list)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stores: {str(e)}")


@router.get("/nearby")
async def get_nearby_stores(
    lat: float = Query(..., description="User latitude"),
    lng: float = Query(..., description="User longitude"),
    radius: float = Query(10, description="Search radius in kilometers")
):
    """
    Get stores nearby the user's location.
    Returns stores sorted by distance, within given radius.
    """
    try:
        stores_list = []
        
        for _, store in data_loader.stores.iterrows():
            store_id = store['store_id']
            
            # Calculate distance using Haversine formula
            distance = haversine(lat, lng, store['latitude'], store['longitude'])
            
            # Filter by radius
            if distance > radius:
                continue
            
            # Get average rating
            store_ratings = data_loader.ratings[data_loader.ratings['store_id'] == store_id]
            avg_rating = store_ratings['rating'].mean() if not store_ratings.empty else 0.0
            avg_rating = round(avg_rating, 1)
            review_count = len(store_ratings)
            
            stores_list.append({
                "store_id": int(store_id),
                "store_name": store['store_name'],
                "address": store['address'],
                "latitude": float(store['latitude']),
                "longitude": float(store['longitude']),
                "phone": store['phone'],
                "opening_hours": store['opening_hours'],
                "distance_km": round(distance, 1),
                "rating": avg_rating,
                "review_count": review_count
            })
        
        # Sort by distance ascending
        stores_list = sorted(stores_list, key=lambda x: x['distance_km'])
        
        return {
            "status": "success",
            "data": {
                "user_location": {"latitude": lat, "longitude": lng},
                "search_radius_km": radius,
                "stores": stores_list,
                "total": len(stores_list)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching nearby stores: {str(e)}")


@router.get("/{store_id}")
async def get_store_details(store_id: int):
    """Get detailed information for a specific store."""
    try:
        store = data_loader.stores[data_loader.stores['store_id'] == store_id]
        
        if store.empty:
            raise HTTPException(status_code=404, detail="Store not found")
        
        store_data = store.iloc[0]
        
        # Get ratings
        store_ratings = data_loader.ratings[data_loader.ratings['store_id'] == store_id]
        avg_rating = store_ratings['rating'].mean() if not store_ratings.empty else 0.0
        avg_rating = round(avg_rating, 1)
        
        # Get rating breakdown (count of each star)
        rating_breakdown = {}
        for i in range(1, 6):
            rating_breakdown[str(i)] = int(len(store_ratings[store_ratings['rating'] == i]))
        
        # Get product stock info
        store_stock = data_loader.prices[data_loader.prices['store_id'] == store_id]
        in_stock_count = len(store_stock[store_stock['stock_status'] == 'in_stock'])
        low_stock_count = len(store_stock[store_stock['stock_status'] == 'low_stock'])
        out_of_stock_count = len(store_stock[store_stock['stock_status'] == 'out_of_stock'])
        
        # Get latest reviews (max 5)
        latest_reviews = (
            store_ratings.sort_values('review_date', ascending=False)
            .head(5)[['rating', 'review_text', 'reviewer_name', 'review_date']]
            .to_dict('records')
        )
        
        return {
            "status": "success",
            "data": {
                "store_id": int(store_id),
                "store_name": store_data['store_name'],
                "address": store_data['address'],
                "latitude": float(store_data['latitude']),
                "longitude": float(store_data['longitude']),
                "phone": store_data['phone'],
                "opening_hours": store_data['opening_hours'],
                "rating": avg_rating,
                "total_reviews": len(store_ratings),
                "rating_breakdown": rating_breakdown,
                "stock_status": {
                    "in_stock": in_stock_count,
                    "low_stock": low_stock_count,
                    "out_of_stock": out_of_stock_count,
                    "total_products": len(store_stock)
                },
                "latest_reviews": latest_reviews
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching store details: {str(e)}")


@router.get("/{store_id}/stock")
async def get_store_stock(
    store_id: int,
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Get stock information for a specific store, optionally filtered by category."""
    try:
        store = data_loader.stores[data_loader.stores['store_id'] == store_id]
        
        if store.empty:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Get store stock
        store_stock = data_loader.prices[data_loader.prices['store_id'] == store_id]
        
        # Join with product info
        stock_info = []
        for _, price_row in store_stock.iterrows():
            product = data_loader.products[data_loader.products['product_id'] == price_row['product_id']]
            
            if product.empty:
                continue
            
            product_data = product.iloc[0]
            
            # Filter by category if specified
            if category and product_data['category'].lower() != category.lower():
                continue
            
            stock_info.append({
                "product_id": int(price_row['product_id']),
                "product_name": product_data['product_name'],
                "category": product_data['category'],
                "price": float(price_row['price']),
                "stock_status": price_row['stock_status']
            })
        
        return {
            "status": "success",
            "data": {
                "store_id": int(store_id),
                "store_name": store.iloc[0]['store_name'],
                "category_filter": category,
                "items": stock_info,
                "total": len(stock_info)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching store stock: {str(e)}")
