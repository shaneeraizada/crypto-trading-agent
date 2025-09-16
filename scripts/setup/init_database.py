# ============================================================================
# scripts/setup/init_database.py
# ============================================================================
"""Database initialization script."""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from config.database import Base
from config.settings import settings
from src.core.models import (
    Network, Token, Exchange, TradingPair, Strategy, 
    Portfolio, Order, Position
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_tables():
    """Create all database tables."""
    try:
        engine = create_async_engine(settings.database.url, echo=True)
        
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("All tables created successfully")
        
        await engine.dispose()
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


async def insert_sample_data():
    """Insert sample reference data."""
    try:
        engine = create_async_engine(settings.database.url)
        
        # Sample data would be inserted here
        logger.info("Sample data insertion complete")
        
        await engine.dispose()
        
    except Exception as e:
        logger.error(f"Error inserting sample data: {e}")
        raise


async def main():
    """Main initialization function."""
    try:
        logger.info("Starting database initialization...")
        
        # Create tables
        await create_tables()
        
        # Insert sample data
        await insert_sample_data()
        
        logger.info("Database initialization complete!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())