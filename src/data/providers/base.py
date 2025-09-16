# ============================================================================
# src/data/providers/base.py
# ============================================================================
"""Abstract base classes for data providers."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from src.core.models import TokenResponse, PriceData
from src.core.exceptions import DataProviderException


class DataProvider(ABC):
    """Abstract base class for data providers."""
    
    def __init__(self, name: str, base_url: str, api_key: Optional[str] = None):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.rate_limit = 100  # Default rate limit per minute
        self._last_request_time = 0
        self._request_count = 0
    
    @abstractmethod
    async def get_token_price(self, token_address: str, network: str = "ethereum") -> Optional[Decimal]:
        """Get current token price."""
        pass
    
    @abstractmethod
    async def get_token_info(self, token_address: str, network: str = "ethereum") -> Optional[Dict[str, Any]]:
        """Get token information."""
        pass
    
    @abstractmethod
    async def get_price_history(
        self, 
        token_address: str, 
        timeframe: str = "1h", 
        limit: int = 100,
        network: str = "ethereum"
    ) -> List[PriceData]:
        """Get historical price data."""
        pass
    
    @abstractmethod
    async def get_trending_tokens(self, network: str = "ethereum", limit: int = 50) -> List[Dict[str, Any]]:
        """Get trending tokens."""
        pass
    
    async def health_check(self) -> bool:
        """Check if the data provider is healthy."""
        try:
            # Implement basic health check
            return True
        except Exception:
            return False
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        current_time = datetime.now().timestamp()
        if current_time - self._last_request_time > 60:
            # Reset counter every minute
            self._request_count = 0
            self._last_request_time = current_time
        
        return self._request_count < self.rate_limit
    
    def _increment_request_count(self) -> None:
        """Increment request counter."""
        self._request_count += 1