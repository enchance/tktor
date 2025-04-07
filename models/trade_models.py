from abc import ABC
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, DateTime, func, text, TEXT
from sqlalchemy.dialects.postgresql import JSONB

from core import ic
from .common_models import IntPkMixin, DTMixin, UpdatedAtMixin


class OrderMod(UpdatedAtMixin, ABC):
    id: int | None = Field(primary_key=True, nullable=False)
    exchange_orderid: str = Field(max_length=199, unique=True, nullable=False)
    client_orderid: str = Field(max_length=199, nullable=False)
    symbol: str = Field(max_length=20, nullable=False)
    amount: str = Field(max_length=199, nullable=False)
    quote_amount: str = Field(max_length=199, nullable=False)
    executed_amount: str = Field(max_length=199, nullable=False)
    cum_quote_amount: str = Field(max_length=199, nullable=False)
    stop_limit: str = Field(max_length=199, nullable=False)
    stop_price: str = Field(max_length=199, nullable=False)
    status: str = Field(max_length=199, nullable=False)
    time_in_force: str = Field(max_length=10, nullable=False)
    type: str = Field(max_length=20, nullable=False)
    side: str = Field(max_length=20, nullable=False)
    iceberg_amount: str = Field(max_length=199, nullable=False)
    exchange_id: int = Field(foreign_key='xch_exchange.id', ondelete='CASCADE', nullable=False)
    account_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE', nullable=False)
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))  # time
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))  # time


class TradeMod(ABC):
    id: int = Field(primary_key=True, nullable=False)
    symbol: str = Field(max_length=20, nullable=False)
    price: str = Field(max_length=199, nullable=False)
    amount: str = Field(max_length=199, nullable=False)  # quantity
    total: str = Field(max_length=199, nullable=False)  # quoteQty
    commission: str = Field(max_length=199, nullable=False)
    asset: str = Field(max_length=199, nullable=False)  # commissionAsset
    pair: str = Field(max_length=20, nullable=False)
    is_buyer: bool = Field(nullable=False)
    is_maker: bool = Field(nullable=False)
    is_best_match: bool = Field(nullable=False)
    order_id: int = Field(foreign_key='xch_order.id', ondelete='CASCADE', nullable=False)
    exchange_id: int = Field(foreign_key='xch_exchange.id', ondelete='CASCADE', nullable=False)
    account_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE', nullable=False)
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))  # time


class WalletMod(DTMixin, IntPkMixin, ABC):
    asset: str = Field(max_length=20, index=True)
    amount: str = Field(max_length=199)
    exchange_id: int = Field(foreign_key='xch_exchange.id', ondelete='CASCADE', nullable=False)
    meta: dict = Field(sa_column=Column(JSONB, server_default=text("'{}'::jsonb")), default_factory=dict)
    account_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE')


class ExchangeMod(DTMixin, IntPkMixin, ABC):
    name: str = Field(max_length=199)
    display: str = Field(max_length=199)
    website: str = Field(max_length=199)
    description: str = Field(sa_column=Column(TEXT, default='', server_default=''))
    # account_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE')
    meta: dict = Field(sa_column=Column(JSONB, server_default=text("'{}'::jsonb")), default_factory=dict)
