# ============================================================================
# src/api/v1/schemas/trading.py
# ============================================================================
"""Trading-related API schemas."""

from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.core.models import OrderType, OrderSide, OrderStatus


class OrderCreateRequest(BaseModel):
    """Request schema for creating orders."""
    portfolio_id: int = Field(..., description="Portfolio ID")
    trading_pair_id: int = Field(..., description="Trading pair ID")
    exchange_id: int = Field(..., description="Exchange ID")
    strategy_id: Optional[int] = Field(None, description="Strategy ID")
    order_type: OrderType = Field(..., description="Order type")
    side: OrderSide = Field(..., description="Order side (BUY/SELL)")
    quantity: Decimal = Field(..., gt=0, description="Order quantity")
    price: Optional[Decimal] = Field(None, gt=0, description="Order price (for limit orders)")
    stop_price: Optional[Decimal] = Field(None, gt=0, description="Stop price (for stop orders)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class OrderResponse(BaseModel):
    """Response schema for orders."""
    id: str
    portfolio_id: int
    trading_pair_id: int
    exchange_id: int
    strategy_id: Optional[int]
    order_type: OrderType
    side: OrderSide
    quantity: Decimal
    price: Optional[Decimal]
    stop_price: Optional[Decimal]
    filled_quantity: Decimal
    average_fill_price: Optional[Decimal]
    status: OrderStatus
    external_order_id: Optional[str]
    fees: Decimal
    created_at: datetime
    updated_at: datetime


class OrderStatusUpdate(BaseModel):
    """Schema for order status updates."""
    status: OrderStatus
    filled_quantity: Optional[Decimal] = None
    average_fill_price: Optional[Decimal] = None
    fees: Optional[Decimal] = None
