# ============================================================================
# src/core/constants.py
# ============================================================================
"""System constants and enums."""

from enum import Enum


class TimeFrame(str, Enum):
    """Trading timeframes."""
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"


class Network(str, Enum):
    """Supported blockchain networks."""
    ETHEREUM = "ethereum"
    BSC = "bsc"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"


class Exchange(str, Enum):
    """Supported exchanges."""
    UNISWAP_V2 = "uniswap_v2"
    UNISWAP_V3 = "uniswap_v3"
    PANCAKESWAP = "pancakeswap"
    SUSHISWAP = "sushiswap"
    ONE_INCH = "1inch"
    BINANCE = "binance"
    COINBASE = "coinbase"


class DataProvider(str, Enum):
    """Supported data providers."""
    DEXSCREENER = "dexscreener"
    MORALIS = "moralis"
    COINGECKO = "coingecko"
    THE_GRAPH = "the_graph"


# Common token addresses
COMMON_TOKENS = {
    "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "USDC": "0xA0b86a33E6441406E5f1a928f7C7f94F08a18b17",
    "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
}

# Gas limits for common operations
GAS_LIMITS = {
    "SWAP": 200000,
    "ADD_LIQUIDITY": 300000,
    "REMOVE_LIQUIDITY": 250000,
    "APPROVE": 50000,
}

# Risk management constants
RISK_LIMITS = {
    "MAX_POSITION_SIZE": 0.25,  # 25% of portfolio
    "MAX_DAILY_LOSS": 0.05,     # 5% daily loss
    "MAX_DRAWDOWN": 0.20,       # 20% maximum drawdown
    "MIN_LIQUIDITY": 10000,     # Minimum $10k liquidity
    "MAX_SLIPPAGE": 0.05,       # 5% maximum slippage
}