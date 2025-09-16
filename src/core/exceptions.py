# ============================================================================
# src/core/exceptions.py
# ============================================================================
"""Custom exceptions for the trading system."""


class TradingAgentException(Exception):
    """Base exception for trading agent."""
    
    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class DataProviderException(TradingAgentException):
    """Exception raised by data providers."""
    pass


class ExchangeException(TradingAgentException):
    """Exception raised by exchange interactions."""
    pass


class StrategyException(TradingAgentException):
    """Exception raised by trading strategies."""
    pass


class RiskManagementException(TradingAgentException):
    """Exception raised by risk management system."""
    pass


class InsufficientFundsException(TradingAgentException):
    """Exception raised when insufficient funds for trade."""
    pass


class InvalidOrderException(TradingAgentException):
    """Exception raised for invalid orders."""
    pass


class RateLimitException(TradingAgentException):
    """Exception raised when API rate limit is exceeded."""
    pass


class NetworkException(TradingAgentException):
    """Exception raised for network-related errors."""
    pass


class ValidationException(TradingAgentException):
    """Exception raised for validation errors."""
    pass
