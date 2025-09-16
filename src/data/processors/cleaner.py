# ============================================================================
# src/data/processors/cleaner.py
# ============================================================================
"""Data cleaning and validation utilities."""

from typing import Dict, Any, Optional, List
from decimal import Decimal, InvalidOperation
from datetime import datetime
import re

from src.core.exceptions import ValidationException


class DataCleaner:
    """Utility class for cleaning and validating market data."""
    
    @staticmethod
    def clean_price_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate price data."""
        try:
            cleaned_data = {}
            
            # Clean price fields
            price_fields = ['price', 'open_price', 'high_price', 'low_price', 'close_price']
            for field in price_fields:
                if field in raw_data:
                    cleaned_data[field] = DataCleaner._clean_decimal(raw_data[field])
            
            # Clean volume fields
            volume_fields = ['volume', 'volume_24h', 'quote_volume', 'liquidity']
            for field in volume_fields:
                if field in raw_data:
                    cleaned_data[field] = DataCleaner._clean_decimal(raw_data[field])
            
            # Clean percentage fields
            percentage_fields = ['price_change_24h', 'price_change_1h']
            for field in percentage_fields:
                if field in raw_data:
                    cleaned_data[field] = DataCleaner._clean_percentage(raw_data[field])
            
            # Clean integer fields
            int_fields = ['trade_count', 'holders']
            for field in int_fields:
                if field in raw_data:
                    cleaned_data[field] = DataCleaner._clean_integer(raw_data[field])
            
            # Clean string fields
            string_fields = ['symbol', 'name']
            for field in string_fields:
                if field in raw_data:
                    cleaned_data[field] = DataCleaner._clean_string(raw_data[field])
            
            # Clean address field
            if 'address' in raw_data:
                cleaned_data['address'] = DataCleaner._clean_address(raw_data['address'])
            
            # Add timestamp
            cleaned_data['timestamp'] = datetime.utcnow()
            
            return cleaned_data
            
        except Exception as e:
            raise ValidationException(f"Error cleaning price data: {e}")
    
    @staticmethod
    def _clean_decimal(value: Any) -> Optional[Decimal]:
        """Clean and convert value to Decimal."""
        if value is None or value == '':
            return None
        
        try:
            if isinstance(value, str):
                # Remove any non-numeric characters except decimal point and minus
                cleaned = re.sub(r'[^\d.-]', '', value)
                if not cleaned:
                    return None
                return Decimal(cleaned)
            
            return Decimal(str(value))
            
        except (InvalidOperation, ValueError, TypeError):
            return None
    
    @staticmethod
    def _clean_percentage(value: Any) -> Optional[float]:
        """Clean and convert percentage value."""
        if value is None or value == '':
            return None
        
        try:
            if isinstance(value, str):
                # Remove percentage sign and other characters
                cleaned = re.sub(r'[^\d.-]', '', value)
                if not cleaned:
                    return None
                return float(cleaned)
            
            return float(value)
            
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _clean_integer(value: Any) -> Optional[int]:
        """Clean and convert integer value."""
        if value is None or value == '':
            return None
        
        try:
            if isinstance(value, str):
                cleaned = re.sub(r'[^\d]', '', value)
                if not cleaned:
                    return None
                return int(cleaned)
            
            return int(value)
            
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def _clean_string(value: Any) -> Optional[str]:
        """Clean string value."""
        if value is None:
            return None
        
        try:
            cleaned = str(value).strip()
            return cleaned if cleaned else None
        except:
            return None
    
    @staticmethod
    def _clean_address(value: Any) -> Optional[str]:
        """Clean and validate Ethereum address."""
        if value is None:
            return None
        
        try:
            address = str(value).strip().lower()
            
            # Basic Ethereum address validation
            if not address.startswith('0x') or len(address) != 42:
                return None
            
            # Check if it contains only valid hex characters
            if not re.match(r'^0x[a-f0-9]{40}', address):
                return None
            
            return address
            
        except:
            return None
    
    @staticmethod
    def validate_price_data(data: Dict[str, Any]) -> bool:
        """Validate price data integrity."""
        try:
            # Check required fields
            required_fields = ['price']
            for field in required_fields:
                if field not in data or data[field] is None:
                    return False
            
            # Validate price is positive
            if data['price'] <= 0:
                return False
            
            # Validate OHLC data if present
            if all(field in data for field in ['open_price', 'high_price', 'low_price', 'close_price']):
                ohlc = [data['open_price'], data['high_price'], data['low_price'], data['close_price']]
                
                # High should be >= all other prices
                if not (data['high_price'] >= max(data['open_price'], data['close_price']) and
                        data['high_price'] >= data['low_price']):
                    return False
                
                # Low should be <= all other prices
                if not (data['low_price'] <= min(data['open_price'], data['close_price']) and
                        data['low_price'] <= data['high_price']):
                    return False
            
            # Validate volume is non-negative
            if 'volume' in data and data['volume'] is not None and data['volume'] < 0:
                return False
            
            return True
            
        except Exception:
            return False


# Global data cleaner instance
data_cleaner = DataCleaner()