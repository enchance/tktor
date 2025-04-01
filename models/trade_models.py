from abc import ABC
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime, func

from .common_models import IntPkMixin


class TradeLogMod(ABC):
    id: int = Field(primary_key=True)
    orderid: int = Field(unique=True)
    orderlistid: int = Field()
    symbol: str = Field(max_length=20, index=True)
    price: str = Field(max_length=199)
    qty: str = Field(max_length=199)
    quote_qty: str = Field(max_length=199)
    commission: str = Field(max_length=199)
    commission_asset: str = Field(max_length=10)
    transacted_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    exchange: str = Field(max_length=199, default='binance', index=True)
    is_buyer: bool = Field()
    is_maker: bool = Field()
    is_best_match: bool = Field()
    owner_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE')
