# ============================================================================
# src/data/storage/repositories/token_repo.py
# ============================================================================
"""Token repository."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.core.models import Token, Network, TokenCreate, TokenResponse


class TokenRepository:
    """Repository for token operations."""
    
    async def create_token(self, db: AsyncSession, token_data: TokenCreate) -> Token:
        """Create a new token."""
        try:
            # Use PostgreSQL UPSERT to handle duplicates
            stmt = pg_insert(Token).values(
                address=token_data.address,
                network_id=token_data.network_id,
                symbol=token_data.symbol,
                name=token_data.name,
                decimals=token_data.decimals,
                total_supply=token_data.total_supply,
                is_verified=token_data.is_verified,
                metadata=token_data.metadata
            ).on_conflict_do_update(
                index_elements=['address', 'network_id'],
                set_=dict(
                    symbol=stmt.excluded.symbol,
                    name=stmt.excluded.name,
                    decimals=stmt.excluded.decimals,
                    total_supply=stmt.excluded.total_supply,
                    metadata=stmt.excluded.metadata,
                    updated_at=stmt.excluded.updated_at
                )
            ).returning(Token)
            
            result = await db.execute(stmt)
            token = result.scalar_one()
            await db.commit()
            return token
            
        except Exception as e:
            await db.rollback()
            raise
    
    async def get_token_by_address(
        self, 
        db: AsyncSession, 
        address: str, 
        network_id: int
    ) -> Optional[Token]:
        """Get token by address and network."""
        query = select(Token).where(
            and_(Token.address == address, Token.network_id == network_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_tokens_by_network(
        self, 
        db: AsyncSession, 
        network_id: int, 
        is_active: bool = True
    ) -> List[Token]:
        """Get all tokens for a network."""
        query = select(Token).where(
            and_(Token.network_id == network_id, Token.is_active == is_active)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def search_tokens(
        self, 
        db: AsyncSession, 
        search_term: str, 
        limit: int = 50
    ) -> List[Token]:
        """Search tokens by symbol or name."""
        query = select(Token).where(
            and_(
                Token.is_active == True,
                (Token.symbol.ilike(f"%{search_term}%") | 
                 Token.name.ilike(f"%{search_term}%"))
            )
        ).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())