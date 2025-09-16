# ============================================================================
# tests/conftest.py
# ============================================================================
"""Pytest configuration and fixtures."""

import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient

from src.api.app import app
from config.database import Base, get_db
from config.settings import settings


# Test database URL (SQLite for testing)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def client(test_session):
    """Create test HTTP client."""
    
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_token_data():
    """Sample token data for testing."""
    return {
        "address": "0x1234567890123456789012345678901234567890",
        "symbol": "TEST",
        "name": "Test Token",
        "decimals": 18,
        "network_id": 1
    }


@pytest.fixture
def sample_order_data():
    """Sample order data for testing."""
    return {
        "portfolio_id": 1,
        "trading_pair_id": 1,
        "exchange_id": 1,
        "order_type": "MARKET",
        "side": "BUY",
        "quantity": "100.0"
    }