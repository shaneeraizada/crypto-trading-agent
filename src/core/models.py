# ============================================================================
# src/core/models.py
# ============================================================================
"""Core Pydantic models and SQLAlchemy models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, 
    Numeric, ForeignKey, JSON, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config.database import Base


# ============================================================================
# ENUMS
# ============================================================================

class OrderType(str, Enum):
    """Order types."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderSide(str, Enum):
    """Order sides."""
    BUY = "BUY"
    SELL = "SELL"


class OrderStatus(str, Enum):
    """Order status."""
    PENDING = "PENDING"
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class ExchangeType(str, Enum):
    """Exchange types."""
    DEX = "DEX"
    CEX = "CEX"


class StrategyType(str, Enum):
    """Strategy types."""
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    ML = "ml"
    HYBRID = "hybrid"


# ============================================================================
# PYDANTIC MODELS (API Schemas)
# ============================================================================

class TokenBase(BaseModel):
    """Base token model."""
    model_config = ConfigDict(from_attributes=True)
    
    address: str = Field(..., description="Token contract address")
    symbol: str = Field(..., max_length=20, description="Token symbol")
    name: str = Field(..., max_length=100, description="Token name")
    decimals: int = Field(default=18, ge=0, le=30, description="Token decimals")


class TokenCreate(TokenBase):
    """Token creation model."""
    network_id: int = Field(..., description="Network ID")
    total_supply: Optional[Decimal] = None
    is_verified: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TokenResponse(TokenBase):
    """Token response model."""
    id: int
    network_id: int
    total_supply: Optional[Decimal] = None
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PriceData(BaseModel):
    """Price data model."""
    model_config = ConfigDict(from_attributes=True)
    
    time: datetime
    trading_pair_id: int
    timeframe: str = Field(..., pattern=r'^(1m|5m|15m|1h|4h|1d)$')
    open_price: Decimal = Field(..., gt=0)
    high_price: Decimal = Field(..., gt=0)
    low_price: Decimal = Field(..., gt=0)
    close_price: Decimal = Field(..., gt=0)
    volume: Decimal = Field(..., ge=0)
    quote_volume: Decimal = Field(..., ge=0)
    trade_count: int = Field(default=0, ge=0)


class OrderCreate(BaseModel):
    """Order creation model."""
    model_config = ConfigDict(from_attributes=True)
    
    portfolio_id: int
    trading_pair_id: int
    exchange_id: int
    strategy_id: Optional[int] = None
    order_type: OrderType
    side: OrderSide
    quantity: Decimal = Field(..., gt=0)
    price: Optional[Decimal] = Field(None, gt=0)
    stop_price: Optional[Decimal] = Field(None, gt=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OrderResponse(BaseModel):
    """Order response model."""
    model_config = ConfigDict(from_attributes=True)
    
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


class StrategyCreate(BaseModel):
    """Strategy creation model."""
    name: str = Field(..., max_length=100)
    type: StrategyType
    class_name: str = Field(..., max_length=100)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    created_by: Optional[str] = Field(None, max_length=50)


class StrategyResponse(BaseModel):
    """Strategy response model."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    type: StrategyType
    class_name: str
    parameters: Dict[str, Any]
    is_active: bool
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime


class PortfolioCreate(BaseModel):
    """Portfolio creation model."""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    base_currency: str = Field(default="USD", max_length=10)
    initial_balance: Decimal = Field(..., gt=0)
    strategy_id: Optional[int] = None
    risk_profile: Dict[str, Any] = Field(default_factory=dict)


class PortfolioResponse(BaseModel):
    """Portfolio response model."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str]
    base_currency: str
    initial_balance: Decimal
    current_balance: Decimal
    strategy_id: Optional[int]
    risk_profile: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ============================================================================
# SQLALCHEMY MODELS (Database Tables)
# ============================================================================

class Network(Base):
    """Blockchain networks table."""
    __tablename__ = "networks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    chain_id = Column(Integer, unique=True)
    symbol = Column(String(10), nullable=False)
    rpc_url = Column(Text)
    explorer_url = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tokens = relationship("Token", back_populates="network")
    exchanges = relationship("Exchange", back_populates="network")


class Token(Base):
    """Tokens table."""
    __tablename__ = "tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(42), nullable=False)
    network_id = Column(Integer, ForeignKey("networks.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    decimals = Column(Integer, nullable=False, default=18)
    total_supply = Column(Numeric(36, 0))
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('address', 'network_id'),
        Index('idx_tokens_active', 'network_id', 'symbol', postgresql_where=Column('is_active') == True),
    )
    
    # Relationships
    network = relationship("Network", back_populates="tokens")
    base_pairs = relationship("TradingPair", foreign_keys="TradingPair.base_token_id", back_populates="base_token")
    quote_pairs = relationship("TradingPair", foreign_keys="TradingPair.quote_token_id", back_populates="quote_token")


class Exchange(Base):
    """Exchanges table."""
    __tablename__ = "exchanges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    type = Column(String(20), nullable=False)  # DEX or CEX
    network_id = Column(Integer, ForeignKey("networks.id"))
    router_address = Column(String(42))
    factory_address = Column(String(42))
    api_endpoint = Column(Text)
    fee_rate = Column(Numeric(5, 4), default=0.003)
    is_active = Column(Boolean, default=True)
    configuration = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    network = relationship("Network", back_populates="exchanges")
    trading_pairs = relationship("TradingPair", back_populates="exchange")
    orders = relationship("Order", back_populates="exchange")


class TradingPair(Base):
    """Trading pairs table."""
    __tablename__ = "trading_pairs"
    
    id = Column(Integer, primary_key=True, index=True)
    exchange_id = Column(Integer, ForeignKey("exchanges.id"), nullable=False)
    base_token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    quote_token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    pair_address = Column(String(42))
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('exchange_id', 'base_token_id', 'quote_token_id'),
    )
    
    # Relationships
    exchange = relationship("Exchange", back_populates="trading_pairs")
    base_token = relationship("Token", foreign_keys=[base_token_id], back_populates="base_pairs")
    quote_token = relationship("Token", foreign_keys=[quote_token_id], back_populates="quote_pairs")
    orders = relationship("Order", back_populates="trading_pair")


class Strategy(Base):
    """Strategies table."""
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(String(50), nullable=False)
    class_name = Column(String(100), nullable=False)
    parameters = Column(JSON, nullable=False, default={})
    is_active = Column(Boolean, default=True)
    created_by = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="strategy")
    orders = relationship("Order", back_populates="strategy")


class Portfolio(Base):
    """Portfolios table."""
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    base_currency = Column(String(10), nullable=False, default='USD')
    initial_balance = Column(Numeric(18, 2), nullable=False)
    current_balance = Column(Numeric(18, 2), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    risk_profile = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    strategy = relationship("Strategy", back_populates="portfolios")
    orders = relationship("Order", back_populates="portfolio")
    positions = relationship("Position", back_populates="portfolio")
    allocations = relationship("PortfolioAllocation", back_populates="portfolio")


class PortfolioAllocation(Base):
    """Portfolio allocations table."""
    __tablename__ = "portfolio_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    target_weight = Column(Numeric(5, 4), nullable=False)
    current_weight = Column(Numeric(5, 4), default=0)
    min_weight = Column(Numeric(5, 4), default=0)
    max_weight = Column(Numeric(5, 4), default=1)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('portfolio_id', 'token_id'),
    )
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="allocations")
    token = relationship("Token")


class Order(Base):
    """Orders table."""
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    trading_pair_id = Column(Integer, ForeignKey("trading_pairs.id"), nullable=False)
    exchange_id = Column(Integer, ForeignKey("exchanges.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"))
    order_type = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    quantity = Column(Numeric(36, 18), nullable=False)
    price = Column(Numeric(36, 18))
    stop_price = Column(Numeric(36, 18))
    filled_quantity = Column(Numeric(36, 18), default=0)
    average_fill_price = Column(Numeric(36, 18))
    status = Column(String(20), default='PENDING')
    external_order_id = Column(String(100))
    fees = Column(Numeric(36, 18), default=0)
    gas_used = Column(Numeric(36, 18))
    gas_price = Column(Numeric(36, 18))
    slippage = Column(Numeric(5, 4))
    execution_time = Column(DateTime(timezone=True))
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_orders_portfolio_created', 'portfolio_id', 'created_at'),
        Index('idx_orders_status_created', 'status', 'created_at'),
        Index('idx_orders_external_id', 'external_order_id'),
    )
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="orders")
    trading_pair = relationship("TradingPair", back_populates="orders")
    exchange = relationship("Exchange", back_populates="orders")
    strategy = relationship("Strategy", back_populates="orders")
    fills = relationship("OrderFill", back_populates="order")


class OrderFill(Base):
    """Order fills table."""
    __tablename__ = "order_fills"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    fill_time = Column(DateTime(timezone=True), nullable=False)
    quantity = Column(Numeric(36, 18), nullable=False)
    price = Column(Numeric(36, 18), nullable=False)
    fee = Column(Numeric(36, 18), default=0)
    gas_used = Column(Numeric(36, 18))
    transaction_hash = Column(String(66))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_order_fills_order_time', 'order_id', 'fill_time'),
    )
    
    # Relationships
    order = relationship("Order", back_populates="fills")


class Position(Base):
    """Positions table."""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    token_id = Column(Integer, ForeignKey("tokens.id"), nullable=False)
    quantity = Column(Numeric(36, 18), nullable=False, default=0)
    average_cost = Column(Numeric(36, 18), nullable=False, default=0)
    realized_pnl = Column(Numeric(18, 2), default=0)
    unrealized_pnl = Column(Numeric(18, 2), default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('portfolio_id', 'token_id'),
        Index('idx_positions_portfolio', 'portfolio_id'),
    )
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")
    token = relationship("Token")