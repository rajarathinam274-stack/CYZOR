"""
Products Router - Handles product search, filtering, and price comparison.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd
from backend.data_loader import data_loader
from backend.utils.helpers import haversine, calculate_savings_potential, round_price

router = APIRouter()


@router.get("/search")
async def search_products(
    q: str = Query(..., min_length=1, description="Product search query"),
    lat: Optional[float] = Query(
        None, description="User latitude for distance calculation"
    ),
    lng: Optional[float] = Query(
        None, description="User longitude for distance calculation"
    ),
    sort_by: str = Query("price", description="Sort by: price, distance, or rating"),
):
    """
    Search for products by name and compare prices across all stores.
    Returns list of stores with prices, stock status, distance, and ratings.
    """
    try:
        # Filter products by search query (case-insensitive)
        products_match = data_loader.products[
            data_loader.products["product_name"].str.lower().str.contains(q.lower())
        ]

        if products_match.empty:
            return {
                "status": "success",
                "data": {
                    "product": q,
                    "results": [],
                    "cheapest_price": None,
                    "highest_price": None,
                    "savings_potential": 0,
                },
            }

        product_id = products_match.iloc[0]["product_id"]
        product_name = products_match.iloc[0]["product_name"]

        # Join prices with stores
        product_prices = data_loader.prices[
            data_loader.prices["product_id"] == product_id
        ]

        results = []
        for _, row in product_prices.iterrows():
            store_info = data_loader.stores[
                data_loader.stores["store_id"] == row["store_id"]
            ]
            if store_info.empty:
                continue

            store = store_info.iloc[0]

            # Calculate distance if user location provided
            distance_km = None
            if lat is not None and lng is not None:
                distance_km = round(
                    haversine(lat, lng, store["latitude"], store["longitude"]), 1
                )

            # Get store rating
            store_ratings = data_loader.ratings[
                data_loader.ratings["store_id"] == row["store_id"]
            ]
            avg_rating = (
                store_ratings["rating"].mean() if not store_ratings.empty else 0.0
            )
            avg_rating = round(avg_rating, 1)

            result = {
                "store_id": int(row["store_id"]),
                "store_name": str(store["store_name"]),
                "price": float(round_price(float(row["price"]))),
                "stock_status": str(row["stock_status"]),
                "distance_km": float(distance_km) if distance_km is not None else None,
                "rating": float(avg_rating),
                "address": str(store["address"]),
                "phone": str(store["phone"]),
            }
            results.append(result)

        # Sort results
        if sort_by == "price":
            results = sorted(results, key=lambda x: x["price"])
        elif sort_by == "distance" and lat and lng:
            results = sorted(
                results,
                key=lambda x: x["distance_km"] if x["distance_km"] else float("inf"),
            )
        elif sort_by == "rating":
            results = sorted(results, key=lambda x: x["rating"], reverse=True)

        # Mark cheapest price
        if results:
            min_price = min(r["price"] for r in results)
            for r in results:
                r["is_cheapest"] = r["price"] == min_price

        # Calculate savings potential
        prices_list = [r["price"] for r in results]
        savings_info = calculate_savings_potential(prices_list)

        return {
            "status": "success",
            "data": {
                "product": product_name,
                "product_id": product_id,
                "results": results,
                "cheapest_price": savings_info["min"],
                "highest_price": savings_info["max"],
                "savings_potential": savings_info["savings"],
                "total_stores": len(results),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/categories")
async def get_categories():
    """Get all product categories with product counts, derived from the products table."""
    try:
        # Derive categories from actual product data (not categories.csv which may differ)
        cat_col = "category" if "category" in data_loader.products.columns else None
        if cat_col is None:
            return {"status": "success", "data": {"categories": [], "total": 0}}

        cat_counts = data_loader.products[cat_col].value_counts().reset_index()
        cat_counts.columns = ["category_name", "product_count"]
        cat_counts = cat_counts.sort_values("category_name")

        categories = [
            {
                "category_name": row["category_name"],
                "product_count": int(row["product_count"]),
            }
            for _, row in cat_counts.iterrows()
        ]

        return {
            "status": "success",
            "data": {"categories": categories, "total": len(categories)},
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching categories: {str(e)}"
        )


@router.get("/{product_id}/price-history")
async def get_price_history(product_id: int):
    """
    Get 30-day price history for a product across all stores.
    Returns price data grouped by store for chart rendering.
    """
    try:
        # Get product details
        product = data_loader.products[data_loader.products["product_id"] == product_id]
        if product.empty:
            raise HTTPException(status_code=404, detail="Product not found")

        product_name = product.iloc[0]["product_name"]

        # Get price history
        history = data_loader.price_history[
            data_loader.price_history["product_id"] == product_id
        ]

        if history.empty:
            return {
                "status": "success",
                "data": {
                    "product_id": product_id,
                    "product_name": product_name,
                    "history_by_store": {},
                },
            }

        # Group by store
        history_by_store = {}
        for store_id in history["store_id"].unique():
            store_history = history[history["store_id"] == store_id]
            store_info = data_loader.stores[data_loader.stores["store_id"] == store_id]

            if store_info.empty:
                continue

            store_name = store_info.iloc[0]["store_name"]

            # Sort by date and prepare for chart
            store_history = store_history.sort_values("recorded_date")

            history_by_store[int(store_id)] = {
                "store_name": store_name,
                "dates": store_history["recorded_date"].tolist(),
                "prices": [round_price(p) for p in store_history["price"].tolist()],
                "min_price": round_price(store_history["price"].min()),
                "max_price": round_price(store_history["price"].max()),
                "avg_price": round_price(store_history["price"].mean()),
            }

        return {
            "status": "success",
            "data": {
                "product_id": product_id,
                "product_name": product_name,
                "history_by_store": history_by_store,
                "total_stores": len(history_by_store),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching price history: {str(e)}"
        )


@router.get("")
async def get_all_products():
    """Get all products with their current lowest prices and stock status."""
    try:
        products_list = []

        for _, product in data_loader.products.iterrows():
            product_id = int(product["product_id"])

            # Get all price rows for this product
            product_prices = data_loader.prices[
                data_loader.prices["product_id"] == product_id
            ]

            if product_prices.empty:
                continue

            min_price = float(product_prices["price"].min())

            # Cheapest store
            cheapest_row = product_prices.loc[product_prices["price"].idxmin()]
            cheapest_store_info = data_loader.stores[
                data_loader.stores["store_id"] == int(cheapest_row["store_id"])
            ]
            cheapest_store_name = (
                str(cheapest_store_info.iloc[0]["store_name"])
                if not cheapest_store_info.empty
                else "N/A"
            )

            # Majority stock status across stores
            status_counts = product_prices["stock_status"].value_counts()
            majority_status = (
                str(status_counts.index[0])
                if not status_counts.empty
                else "out_of_stock"
            )

            products_list.append(
                {
                    "product_id": product_id,
                    "product_name": str(product["product_name"]),
                    "category": str(product["category"]),
                    "cheapest_price": round(min_price, 2),
                    "cheapest_store": cheapest_store_name,
                    "available_stores": int(len(product_prices)),
                    "stock_status": majority_status,
                }
            )

        return {
            "status": "success",
            "data": {"products": products_list, "total": len(products_list)},
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching products: {str(e)}"
        )
