"""
Ratings Router - Handles store ratings and reviews.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
from backend.data_loader import data_loader

router = APIRouter()


class RatingCreate(BaseModel):
    rating: int
    review_text: str
    reviewer_name: str


@router.get("/store/{store_id}")
async def get_store_reviews(store_id: int):
    """Get all reviews for a specific store."""
    try:
        store = data_loader.stores[data_loader.stores['store_id'] == store_id]
        
        if store.empty:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Get ratings sorted by date descending
        ratings = data_loader.ratings[data_loader.ratings['store_id'] == store_id]
        ratings = ratings.sort_values('review_date', ascending=False)
        
        reviews = []
        for _, rating in ratings.iterrows():
            reviews.append({
                "rating_id": int(rating['rating_id']),
                "rating": int(rating['rating']),
                "review_text": rating['review_text'],
                "reviewer_name": rating['reviewer_name'],
                "review_date": rating['review_date']
            })
        
        return {
            "status": "success",
            "data": {
                "store_id": int(store_id),
                "store_name": store.iloc[0]['store_name'],
                "reviews": reviews,
                "total_reviews": len(reviews)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reviews: {str(e)}")


@router.post("/store/{store_id}")
async def create_review(store_id: int, rating_data: RatingCreate):
    """Create a new review for a store."""
    try:
        # Verify store exists
        store = data_loader.stores[data_loader.stores['store_id'] == store_id]
        
        if store.empty:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Validate rating
        if not (1 <= rating_data.rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Validate review text
        if len(rating_data.review_text.strip()) < 5:
            raise HTTPException(status_code=400, detail="Review must be at least 5 characters")
        
        # Generate rating_id
        if len(data_loader.ratings) > 0:
            next_rating_id = max(data_loader.ratings['rating_id']) + 1
        else:
            next_rating_id = 1
        
        review_date = datetime.now().strftime('%Y-%m-%d')
        
        # Add new rating
        new_rating = pd.DataFrame({
            'rating_id': [next_rating_id],
            'store_id': [store_id],
            'rating': [rating_data.rating],
            'review_text': [rating_data.review_text],
            'reviewer_name': [rating_data.reviewer_name],
            'review_date': [review_date]
        })
        
        data_loader.ratings = pd.concat(
            [data_loader.ratings, new_rating],
            ignore_index=True
        )
        
        data_loader.save_ratings()
        
        return {
            "status": "success",
            "data": {
                "rating_id": next_rating_id,
                "store_id": int(store_id),
                "store_name": store.iloc[0]['store_name'],
                "rating": rating_data.rating,
                "review_text": rating_data.review_text,
                "reviewer_name": rating_data.reviewer_name,
                "review_date": review_date
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating review: {str(e)}")


@router.get("/store/{store_id}/summary")
async def get_rating_summary(store_id: int):
    """Get rating summary for a store."""
    try:
        # Verify store exists
        store = data_loader.stores[data_loader.stores['store_id'] == store_id]
        
        if store.empty:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Get ratings
        ratings = data_loader.ratings[data_loader.ratings['store_id'] == store_id]
        
        if ratings.empty:
            return {
                "status": "success",
                "data": {
                    "store_id": int(store_id),
                    "store_name": store.iloc[0]['store_name'],
                    "average_rating": 0.0,
                    "total_reviews": 0,
                    "breakdown": {
                        "5": 0,
                        "4": 0,
                        "3": 0,
                        "2": 0,
                        "1": 0
                    }
                }
            }
        
        # Calculate average rating
        avg_rating = ratings['rating'].mean()
        avg_rating = round(avg_rating, 1)
        
        # Calculate breakdown
        breakdown = {}
        for i in range(5, 0, -1):
            count = len(ratings[ratings['rating'] == i])
            breakdown[str(i)] = count
        
        return {
            "status": "success",
            "data": {
                "store_id": int(store_id),
                "store_name": store.iloc[0]['store_name'],
                "average_rating": avg_rating,
                "total_reviews": len(ratings),
                "breakdown": breakdown
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching rating summary: {str(e)}")
