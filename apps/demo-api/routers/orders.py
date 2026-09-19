from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import models
from database import get_db

router = APIRouter(prefix="/api/orders", tags=["Orders"])

class Order(BaseModel):
    id: int
    item: str
    price: float

# VULNERABILITY: Broken Authentication. This endpoint returns sensitive order data but doesn't require authentication!
@router.get("/{order_id}", response_model=Order)
def read_order(order_id: int):
    # Mocking order data for demo
    if order_id > 100:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(id=order_id, item="Premium Widget", price=99.99)
