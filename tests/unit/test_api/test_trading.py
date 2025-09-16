# ============================================================================
# tests/unit/test_api/test_trading.py
# ============================================================================
"""Unit tests for trading API endpoints."""

import pytest
from httpx import AsyncClient


class TestTradingAPI:
    """Test cases for trading API endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_order_success(self, client: AsyncClient, sample_order_data):
        """Test successful order creation."""
        response = await client.post("/api/v1/trading/orders", json=sample_order_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["side"] == "BUY"
        assert data["order_type"] == "MARKET"
        assert data["status"] == "PENDING"
    
    @pytest.mark.asyncio
    async def test_create_order_invalid_quantity(self, client: AsyncClient, sample_order_data):
        """Test order creation with invalid quantity."""
        sample_order_data["quantity"] = "0"
        
        response = await client.post("/api/v1/trading/orders", json=sample_order_data)
        
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_orders_empty(self, client: AsyncClient):
        """Test getting orders when none exist."""
        response = await client.get("/api/v1/trading/orders")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_get_order_not_found(self, client: AsyncClient):
        """Test getting non-existent order."""
        response = await client.get("/api/v1/trading/orders/non-existent-id")
        
        assert response.status_code == 404