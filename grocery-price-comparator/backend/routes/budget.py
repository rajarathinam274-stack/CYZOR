"""
Budget Router - Handles budget planning, session management, and budget item tracking.
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import pandas as pd
from io import StringIO
from datetime import datetime
from backend.data_loader import data_loader
from backend.utils.helpers import generate_session_id, round_price
from pydantic import BaseModel

router = APIRouter()


class BudgetCreate(BaseModel):
    total_budget: float


class BudgetItemCreate(BaseModel):
    product_id: int
    store_id: int
    price_at_add: float
    quantity: int


@router.post("")
async def create_budget(budget: BudgetCreate):
    """Create a new budget session."""
    try:
        session_id = generate_session_id()
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Add new row to budget_sessions
        new_session = pd.DataFrame({
            'session_id': [session_id],
            'total_budget': [budget.total_budget],
            'created_at': [created_at]
        })
        
        data_loader.budget_sessions = pd.concat(
            [data_loader.budget_sessions, new_session],
            ignore_index=True
        )
        
        data_loader.save_budget_sessions()
        
        return {
            "status": "success",
            "data": {
                "session_id": session_id,
                "total_budget": budget.total_budget,
                "created_at": created_at
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating budget: {str(e)}")


@router.get("/{session_id}")
async def get_budget(session_id: str):
    """Get budget summary for a session."""
    try:
        # Get session
        session = data_loader.budget_sessions[
            data_loader.budget_sessions['session_id'] == session_id
        ]
        
        if session.empty:
            raise HTTPException(status_code=404, detail="Budget session not found")
        
        session_data = session.iloc[0]
        total_budget = float(session_data['total_budget'])
        
        # Get items for this session
        items = data_loader.budget_items[
            data_loader.budget_items['session_id'] == session_id
        ]
        
        items_list = []
        total_spent = 0.0
        
        for _, item in items.iterrows():
            product = data_loader.products[
                data_loader.products['product_id'] == item['product_id']
            ]
            store = data_loader.stores[
                data_loader.stores['store_id'] == item['store_id']
            ]
            
            if product.empty or store.empty:
                continue
            
            quantity = int(item['quantity'])
            price = float(item['price_at_add'])
            item_total = price * quantity
            total_spent += item_total
            
            items_list.append({
                "item_id": int(item['item_id']),
                "product_id": int(item['product_id']),
                "product_name": product.iloc[0]['product_name'],
                "store_id": int(item['store_id']),
                "store_name": store.iloc[0]['store_name'],
                "price": round_price(price),
                "quantity": quantity,
                "total": round_price(item_total)
            })
        
        total_spent = round_price(total_spent)
        remaining = round_price(total_budget - total_spent)
        percentage_used = round((total_spent / total_budget * 100), 1) if total_budget > 0 else 0
        
        return {
            "status": "success",
            "data": {
                "session_id": session_id,
                "total_budget": total_budget,
                "total_spent": total_spent,
                "remaining_budget": remaining,
                "percentage_used": percentage_used,
                "budget_status": "over" if remaining < 0 else ("warning" if percentage_used > 70 else "ok"),
                "items": items_list,
                "total_items": len(items_list),
                "created_at": session_data['created_at']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching budget: {str(e)}")


@router.post("/{session_id}/items")
async def add_budget_item(session_id: str, item: BudgetItemCreate):
    """Add an item to a budget session."""
    try:
        # Verify session exists
        session = data_loader.budget_sessions[
            data_loader.budget_sessions['session_id'] == session_id
        ]
        
        if session.empty:
            raise HTTPException(status_code=404, detail="Budget session not found")
        
        # Verify product and store exist
        product = data_loader.products[
            data_loader.products['product_id'] == item.product_id
        ]
        store = data_loader.stores[
            data_loader.stores['store_id'] == item.store_id
        ]
        
        if product.empty:
            raise HTTPException(status_code=404, detail="Product not found")
        if store.empty:
            raise HTTPException(status_code=404, detail="Store not found")
        
        # Generate item_id
        if len(data_loader.budget_items) > 0:
            next_item_id = max(data_loader.budget_items['item_id']) + 1
        else:
            next_item_id = 1
        
        # Add item
        new_item = pd.DataFrame({
            'item_id': [next_item_id],
            'session_id': [session_id],
            'product_id': [item.product_id],
            'store_id': [item.store_id],
            'price_at_add': [item.price_at_add],
            'quantity': [item.quantity]
        })
        
        data_loader.budget_items = pd.concat(
            [data_loader.budget_items, new_item],
            ignore_index=True
        )
        
        data_loader.save_budget_items()
        
        return {
            "status": "success",
            "data": {
                "item_id": next_item_id,
                "product_name": product.iloc[0]['product_name'],
                "store_name": store.iloc[0]['store_name'],
                "price": item.price_at_add,
                "quantity": item.quantity,
                "total": round_price(item.price_at_add * item.quantity)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding item to budget: {str(e)}")


@router.delete("/{session_id}/items/{item_id}")
async def remove_budget_item(session_id: str, item_id: int):
    """Remove an item from a budget session."""
    try:
        # Verify item exists
        item = data_loader.budget_items[
            (data_loader.budget_items['session_id'] == session_id) &
            (data_loader.budget_items['item_id'] == item_id)
        ]
        
        if item.empty:
            raise HTTPException(status_code=404, detail="Budget item not found")
        
        # Remove item
        data_loader.budget_items = data_loader.budget_items[
            ~((data_loader.budget_items['session_id'] == session_id) &
              (data_loader.budget_items['item_id'] == item_id))
        ].reset_index(drop=True)
        
        data_loader.save_budget_items()
        
        return {
            "status": "success",
            "message": "Item removed from budget"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing item: {str(e)}")


@router.get("/{session_id}/export")
async def export_budget(session_id: str):
    """Export budget items as CSV file."""
    try:
        # Get budget
        budget = data_loader.budget_sessions[
            data_loader.budget_sessions['session_id'] == session_id
        ]
        
        if budget.empty:
            raise HTTPException(status_code=404, detail="Budget session not found")
        
        # Get items
        items = data_loader.budget_items[
            data_loader.budget_items['session_id'] == session_id
        ]
        
        if items.empty:
            # Return empty CSV with headers
            csv_data = "Product,Store,Price,Quantity,Total\n"
        else:
            # Build export data
            export_rows = []
            for _, item in items.iterrows():
                product = data_loader.products[
                    data_loader.products['product_id'] == item['product_id']
                ]
                store = data_loader.stores[
                    data_loader.stores['store_id'] == item['store_id']
                ]
                
                if product.empty or store.empty:
                    continue
                
                quantity = int(item['quantity'])
                price = float(item['price_at_add'])
                total = price * quantity
                
                export_rows.append({
                    'Product': product.iloc[0]['product_name'],
                    'Store': store.iloc[0]['store_name'],
                    'Price': f"₹{price:.2f}",
                    'Quantity': quantity,
                    'Total': f"₹{total:.2f}"
                })
            
            export_df = pd.DataFrame(export_rows)
            csv_data = export_df.to_csv(index=False)
        
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=budget_{session_id}.csv"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting budget: {str(e)}")
