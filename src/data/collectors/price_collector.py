# ============================================================================
# src/data/collectors/price_collector.py
# ============================================================================
"""Price data collection service."""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from src.data.providers.dexscreener import DexScreenerProvider
from src.data.storage.repositories.price_repo import PriceRepository
from src.core.events import event_bus, PriceUpdateEvent
from src.core.exceptions import DataProviderException
from config.database import get_db

logger = logging.getLogger(__name__)


class PriceCollector:
    """Collects and stores price data from multiple sources."""
    
    def __init__(self):
        self.providers = {
            "dexscreener": DexScreenerProvider(),
        }
        self.price_repo = PriceRepository()
        self.watchlist: List[str] = []
        self.collection_interval = 60  # seconds
        self.is_running = False
    
    def add_token_to_watchlist(self, token_address: str) -> None:
        """Add token to price collection watchlist."""
        if token_address not in self.watchlist:
            self.watchlist.append(token_address)
            logger.info(f"Added {token_address} to price collection watchlist")
    
    def remove_token_from_watchlist(self, token_address: str) -> None:
        """Remove token from price collection watchlist."""
        if token_address in self.watchlist:
            self.watchlist.remove(token_address)
            logger.info(f"Removed {token_address} from price collection watchlist")
    
    async def collect_price_data(self, token_addresses: List[str]) -> Dict[str, Any]:
        """Collect price data for given token addresses."""
        results = {}
        
        for token_address in token_addresses:
            try:
                # Try each provider until we get data
                for provider_name, provider in self.providers.items():
                    try:
                        price_data = await provider.get_token_info(token_address)
                        if price_data:
                            results[token_address] = {
                                "data": price_data,
                                "source": provider_name,
                                "timestamp": datetime.utcnow()
                            }
                            
                            # Publish price update event
                            await event_bus.publish(PriceUpdateEvent(
                                source="price_collector",
                                data={
                                    "token_address": token_address,
                                    "price": float(price_data["price"]),
                                    "volume_24h": float(price_data["volume_24h"]),
                                    "price_change_24h": price_data["price_change_24h"],
                                    "source": provider_name
                                }
                            ))
                            break
                            
                    except DataProviderException as e:
                        logger.warning(f"Provider {provider_name} failed for {token_address}: {e}")
                        continue
                
                if token_address not in results:
                    logger.error(f"Failed to collect data for {token_address} from all providers")
                    
            except Exception as e:
                logger.error(f"Unexpected error collecting data for {token_address}: {e}")
        
        return results
    
    async def start_collection(self) -> None:
        """Start the price collection loop."""
        self.is_running = True
        logger.info("Started price collection service")
        
        while self.is_running:
            try:
                if self.watchlist:
                    logger.debug(f"Collecting price data for {len(self.watchlist)} tokens")
                    results = await self.collect_price_data(self.watchlist)
                    
                    # Store results in database
                    for token_address, result in results.items():
                        try:
                            async with get_db() as db:
                                await self.price_repo.store_price_tick(
                                    db=db,
                                    token_address=token_address,
                                    price_data=result["data"]
                                )
                        except Exception as e:
                            logger.error(f"Failed to store price data for {token_address}: {e}")
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in price collection loop: {e}")
                await asyncio.sleep(self.collection_interval)
    
    async def stop_collection(self) -> None:
        """Stop the price collection loop."""
        self.is_running = False
        logger.info("Stopped price collection service")
    
    async def get_latest_price(self, token_address: str) -> Optional[Decimal]:
        """Get the latest price for a token."""
        try:
            async with get_db() as db:
                return await self.price_repo.get_latest_price(db, token_address)
        except Exception as e:
            logger.error(f"Error getting latest price for {token_address}: {e}")
            return None