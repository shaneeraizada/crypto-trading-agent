# ============================================================================
# src/data/storage/cache/redis_cache.py
# ============================================================================
"""Redis cache implementation."""

import json
import pickle
from typing import Any, Optional, Union
from datetime import timedelta
import redis.asyncio as redis
from decimal import Decimal

from config.database import redis_client
from src.core.exceptions import TradingAgentException


class RedisCache:
    """Redis cache manager."""
    
    def __init__(self, redis_client: redis.Redis = redis_client):
        self.redis = redis_client
        self.default_ttl = 300  # 5 minutes
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        try:
            value = await self.redis.get(key)
            if value is None:
                return default
            
            # Try to deserialize as JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return pickle.loads(value)
                
        except Exception as e:
            raise TradingAgentException(f"Error getting cache key {key}: {e}")
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """Set value in cache."""
        try:
            # Convert timedelta to seconds
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            elif ttl is None:
                ttl = self.default_ttl
            
            # Serialize value
            try:
                # Try JSON first (faster and more readable)
                serialized_value = json.dumps(value, default=str)
            except (TypeError, ValueError):
                # Fall back to pickle for complex objects
                serialized_value = pickle.dumps(value)
            
            return await self.redis.setex(key, ttl, serialized_value)
            
        except Exception as e:
            raise TradingAgentException(f"Error setting cache key {key}: {e}")
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            raise TradingAgentException(f"Error deleting cache key {key}: {e}")
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return bool(await self.redis.exists(key))
        except Exception as e:
            raise TradingAgentException(f"Error checking cache key {key}: {e}")
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment numeric value."""
        try:
            return await self.redis.incr(key, amount)
        except Exception as e:
            raise TradingAgentException(f"Error incrementing cache key {key}: {e}")
    
    async def expire(self, key: str, ttl: Union[int, timedelta]) -> bool:
        """Set expiration for existing key."""
        try:
            if isinstance(ttl, timedelta):
                ttl = int(ttl.total_seconds())
            return await self.redis.expire(key, ttl)
        except Exception as e:
            raise TradingAgentException(f"Error setting expiration for {key}: {e}")
    
    async def flush_all(self) -> bool:
        """Flush all cache data (use with caution)."""
        try:
            return await self.redis.flushdb()
        except Exception as e:
            raise TradingAgentException(f"Error flushing cache: {e}")
    
    # Utility methods for common patterns
    
    async def get_price(self, token_address: str) -> Optional[Decimal]:
        """Get cached price for a token."""
        key = f"price:{token_address}"
        price_str = await self.get(key)
        return Decimal(price_str) if price_str else None
    
    async def set_price(
        self, 
        token_address: str, 
        price: Decimal, 
        ttl: int = 60
    ) -> bool:
        """Cache price for a token."""
        key = f"price:{token_address}"
        return await self.set(key, str(price), ttl)
    
    async def get_rate_limit_count(self, provider: str, endpoint: str) -> int:
        """Get current rate limit count."""
        key = f"rate_limit:{provider}:{endpoint}"
        count = await self.get(key, 0)
        return int(count)
    
    async def incr_rate_limit(self, provider: str, endpoint: str, ttl: int = 60) -> int:
        """Increment rate limit counter."""
        key = f"rate_limit:{provider}:{endpoint}"
        count = await self.incr(key)
        if count == 1:  # First increment, set TTL
            await self.expire(key, ttl)
        return count


# Global cache instance
cache = RedisCache()