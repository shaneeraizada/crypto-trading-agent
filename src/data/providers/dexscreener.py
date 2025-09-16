# ============================================================================
# src/data/providers/dexscreener.py
# ============================================================================
"""DexScreener data provider implementation."""

import asyncio
import httpx
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from .base import DataProvider
from src.core.models import PriceData
from src.core.exceptions import DataProviderException, RateLimitException
from config.settings import settings


class DexScreenerProvider(DataProvider):
    """DexScreener API data provider."""
    
    def __init__(self):
        super().__init__(
            name="DexScreener",
            base_url="https://api.dexscreener.com/latest",
            api_key=None  # DexScreener doesn't require API key
        )
        self.rate_limit = settings.apis.dexscreener_rate_limit
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def get_token_price(self, token_address: str, network: str = "ethereum") -> Optional[Decimal]:
        """Get current token price from DexScreener."""
        try:
            if not self._check_rate_limit():
                raise RateLimitException("Rate limit exceeded for DexScreener")
            
            url = f"{self.base_url}/dex/tokens/{token_address}"
            response = await self.client.get(url)
            response.raise_for_status()
            
            self._increment_request_count()
            
            data = response.json()
            if data.get("pairs"):
                # Get the most liquid pair
                best_pair = max(data["pairs"], key=lambda p: float(p.get("liquidity", {}).get("usd", 0)))
                return Decimal(str(best_pair.get("priceUsd", 0)))
            
            return None
            
        except httpx.HTTPError as e:
            raise DataProviderException(f"HTTP error from DexScreener: {e}")
        except Exception as e:
            raise DataProviderException(f"Error getting token price: {e}")
    
    async def get_token_info(self, token_address: str, network: str = "ethereum") -> Optional[Dict[str, Any]]:
        """Get token information from DexScreener."""
        try:
            if not self._check_rate_limit():
                raise RateLimitException("Rate limit exceeded for DexScreener")
            
            url = f"{self.base_url}/dex/tokens/{token_address}"
            response = await self.client.get(url)
            response.raise_for_status()
            
            self._increment_request_count()
            
            data = response.json()
            if data.get("pairs"):
                pair = data["pairs"][0]
                token_info = pair.get("baseToken", {})
                
                return {
                    "address": token_address,
                    "symbol": token_info.get("symbol"),
                    "name": token_info.get("name"),
                    "price": Decimal(str(pair.get("priceUsd", 0))),
                    "volume_24h": Decimal(str(pair.get("volume", {}).get("h24", 0))),
                    "liquidity": Decimal(str(pair.get("liquidity", {}).get("usd", 0))),
                    "price_change_24h": float(pair.get("priceChange", {}).get("h24", 0)),
                    "market_cap": Decimal(str(pair.get("marketCap", 0))),
                    "fdv": Decimal(str(pair.get("fdv", 0))),
                }
            
            return None
            
        except Exception as e:
            raise DataProviderException(f"Error getting token info: {e}")
    
    async def get_price_history(
        self, 
        token_address: str, 
        timeframe: str = "1h", 
        limit: int = 100,
        network: str = "ethereum"
    ) -> List[PriceData]:
        """Get historical price data (Note: DexScreener has limited historical data)."""
        # DexScreener doesn't provide historical OHLCV data via public API
        # This would need to be implemented using their premium API or alternative sources
        return []
    
    async def get_trending_tokens(self, network: str = "ethereum", limit: int = 50) -> List[Dict[str, Any]]:
        """Get trending tokens from DexScreener."""
        try:
            if not self._check_rate_limit():
                raise RateLimitException("Rate limit exceeded for DexScreener")
            
            # DexScreener doesn't have a direct trending endpoint
            # We'll search for tokens with high volume
            url = f"{self.base_url}/dex/search/?q={network}"
            response = await self.client.get(url)
            response.raise_for_status()
            
            self._increment_request_count()
            
            data = response.json()
            tokens = []
            
            for pair in data.get("pairs", [])[:limit]:
                if pair.get("baseToken"):
                    base_token = pair["baseToken"]
                    tokens.append({
                        "address": base_token.get("address"),
                        "symbol": base_token.get("symbol"),
                        "name": base_token.get("name"),
                        "price": Decimal(str(pair.get("priceUsd", 0))),
                        "volume_24h": Decimal(str(pair.get("volume", {}).get("h24", 0))),
                        "liquidity": Decimal(str(pair.get("liquidity", {}).get("usd", 0))),
                        "price_change_24h": float(pair.get("priceChange", {}).get("h24", 0)),
                        "market_cap": Decimal(str(pair.get("marketCap", 0))),
                    })
            
            # Sort by volume descending
            tokens.sort(key=lambda x: x["volume_24h"], reverse=True)
            return tokens[:limit]
            
        except Exception as e:
            raise DataProviderException(f"Error getting trending tokens: {e}")