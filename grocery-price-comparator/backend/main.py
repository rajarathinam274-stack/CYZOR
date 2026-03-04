"""
FastAPI main application file.
Sets up routes, middleware, and CORS configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import json
import numpy as np

# Import routers
from backend.routes import products, stores, budget, ratings
from backend.data_loader import DataLoader, data_loader


class NumpySafeEncoder(json.JSONEncoder):
    """JSON encoder that converts numpy types to native Python types."""

    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


class NumpySafeJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(content, cls=NumpySafeEncoder, ensure_ascii=False).encode(
            "utf-8"
        )


# Initialize FastAPI app
app = FastAPI(
    title="Grocery Price Comparator API",
    description="Compare grocery prices across stores in Chennai",
    version="1.0.0",
    debug=True,
    default_response_class=NumpySafeJSONResponse,
)

# Patch FastAPI's internal jsonable_encoder to handle numpy types globally
import fastapi.encoders as _fe

_orig_encoder = _fe.jsonable_encoder


def _numpy_safe_encoder(obj, *args, **kwargs):
    import numpy as np

    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return _orig_encoder(obj, *args, **kwargs)


_fe.jsonable_encoder = _numpy_safe_encoder

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(stores.router, prefix="/api/stores", tags=["Stores"])
app.include_router(budget.router, prefix="/api/budget", tags=["Budget"])
app.include_router(ratings.router, prefix="/api/ratings", tags=["Ratings"])


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "status": "success",
        "message": "Grocery Price Comparator API is running",
        "version": "1.0.0",
        "endpoints": {
            "products": "/api/products",
            "stores": "/api/stores",
            "budget": "/api/budget",
            "ratings": "/api/ratings",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }


@app.on_event("startup")
async def startup_event():
    """Force reload CSV data on every server start."""
    data_loader.reload_all()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    products_count = (
        len(data_loader.products) if hasattr(data_loader, "products") else 0
    )
    return {
        "status": "ok",
        "message": "API is healthy",
        "products_loaded": products_count,
    }


@app.get("/api/reload")
async def reload_data():
    """Force reload all CSV data from disk. Call this after updating CSV files."""
    data_loader.reload_all()
    return {
        "status": "success",
        "message": "Data reloaded from CSV files",
        "counts": {
            "products": len(data_loader.products),
            "prices": len(data_loader.prices),
            "stores": len(data_loader.stores),
            "ratings": len(data_loader.ratings),
            "price_history": len(data_loader.price_history),
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

