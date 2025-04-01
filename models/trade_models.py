from abc import ABC
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime, func, text, TEXT
from sqlalchemy.dialects.postgresql import JSONB

from .common_models import IntPkMixin, DTMixin, UpdatedAtMixin


class TradeLogMod(UpdatedAtMixin, ABC):
    id: int = Field(primary_key=True)
    orderid: int = Field(unique=True)
    orderlistid: int = Field()
    symbol: str = Field(max_length=20, index=True)
    price: str = Field(max_length=199)
    qty: str = Field(max_length=199)
    quote_qty: str = Field(max_length=199)
    commission: str = Field(max_length=199)
    commission_asset: str = Field(max_length=10)
    exchange: str = Field(max_length=199, default='binance', index=True)
    is_buyer: bool = Field()
    is_maker: bool = Field()
    is_best_match: bool = Field()
    owner_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE')
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))


class WalletMod(DTMixin, IntPkMixin, ABC):
    exchange: str = Field(max_length=199, index=True)
    symbol: str = Field(max_length=20, index=True)
    balance: str = Field(max_length=199)
    meta: dict = Field(sa_column=Column(JSONB, server_default=text("'{}'::jsonb")), default_factory=dict)
    owner_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE')


class SymbolMod(DTMixin, IntPkMixin, SQLModel, table=True):
    __tablename__ = 'trade_symbol'
    symbol: str = Field(max_length=20, unique=True)
    name: str = Field(max_length=20, unique=True)
    description: str = Field(sa_column=Column(TEXT, default='', server_default=''))
