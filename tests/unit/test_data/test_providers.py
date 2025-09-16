# ============================================================================
# tests/unit/test_data/test_providers.py
# ============================================================================
"""Unit tests for data providers."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from decimal import Decimal

from src.data.providers.dexscreener import DexScreenerProvider
from src.core.exceptions import DataProviderException, RateLimitException


class TestDexScreenerProvider:
    """Test cases for DexScreener data provider."""
    
    @pytest_asyncio.fixture
    async def provider(self):
        """Create DexScreener provider instance."""
        return DexScreenerProvider()
    
    @pytest.mark.asyncio
    async def test_get_token_price_success(self, provider):
        """Test successful token price retrieval."""
        mock_response = {
            "pairs": [
                {
                    "priceUsd": "1234.56",
                    "liquidity": {"usd": "100000"}
                }
            ]
        }
        
        with patch.object(provider.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status = Mock()
            
            price = await provider.get_token_price("0x123")
            
            assert price == Decimal("1234.56")
            mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_token_price_no_pairs(self, provider):
        """Test token price retrieval with no pairs."""
        mock_response = {"pairs": []}
        
        with patch.object(provider.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status = Mock()
            
            price = await provider.get_token_price("0x123")
            
            assert price is None
    
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, provider):
        """Test rate limit handling."""
        # Set rate limit to 0 to trigger exception
        provider._request_count = provider.rate_limit
        
        with pytest.raises(RateLimitException):
            await provider.get_token_price("0x123")
    
    @pytest.mark.asyncio
    async def test_get_token_info_success(self, provider):
        """Test successful token info retrieval."""
        mock_response = {
            "pairs": [
                {
                    "baseToken": {
                        "symbol": "TEST",
                        "name": "Test Token"
                    },
                    "priceUsd": "100.50",
                    "volume": {"h24": "50000"},
                    "liquidity": {"usd": "200000"},
                    "priceChange": {"h24": "5.5"},
                    "marketCap": "1000000"
                }
            ]
        }
        
        with patch.object(provider.client, 'get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status = Mock()
            
            info = await provider.get_token_info("0x123")
            
            assert info["symbol"] == "TEST"
            assert info["name"] == "Test Token"
            assert info["price"] == Decimal("100.50")
