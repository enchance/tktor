from typing import TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Relationship, Field, Column, DateTime, TEXT, text
from sqlalchemy.dialects.postgresql import JSONB

from core import modstr
from core.models import UpdatedAtMixin, DTMixin, IntPkMixin


if TYPE_CHECKING:
    from authentication import Account


class Order(SQLModel, table=True):
    __tablename__ = 'xch_order'
    id: str = Field(primary_key=True, unique=True, nullable=False)
    # exchange_orderid: str = Field(max_length=199, nullable=False)
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
    exchange_id: int = Field(primary_key=True, foreign_key='xch_exchange.id', ondelete='CASCADE')
    account_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE', nullable=False)
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))  # time

    exchange: 'Exchange' = Relationship(back_populates='orders')
    trades: list['Trade'] = Relationship(back_populates='order')
    account: 'Account' = Relationship(back_populates='orders')


    def __str__(self):
        return modstr(self, 'symbol')


class Trade(UpdatedAtMixin, SQLModel, table=True):
    __tablename__ = 'xch_trade'
    id: str = Field(primary_key=True, unique=True, nullable=False)
    # exchange_orderid: str = Field(nullable=True)
    asset: str = Field(max_length=20, nullable=False)
    symbol: str = Field(max_length=20, nullable=False)
    price: str = Field(max_length=199, nullable=False)
    amount: str = Field(max_length=199, nullable=False)  # quantity
    total: str = Field(max_length=199, nullable=False)  # quoteQty
    commission: str = Field(max_length=199, nullable=False)
    is_buyer: bool = Field(nullable=False)
    is_maker: bool = Field(nullable=False)
    is_best_match: bool = Field(nullable=False)
    order_id: str = Field(max_length=199, foreign_key='xch_order.id', ondelete='CASCADE')
    exchange_id: int = Field(primary_key=True, foreign_key='xch_exchange.id', ondelete='CASCADE')
    account_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE')
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))  # time

    order: 'Order' = Relationship(back_populates='trades')
    exchange: 'Exchange' = Relationship(back_populates='trades')
    account: 'Account' = Relationship(back_populates='trades')


    def __str__(self):
        return modstr(self, 'symbol')


class Wallet(DTMixin, IntPkMixin, SQLModel, table=True):
    __tablename__ = 'xch_wallet'
    asset: str = Field(max_length=20, index=True)
    amount: str = Field(max_length=199)
    exchange_id: int = Field(foreign_key='xch_exchange.id', ondelete='CASCADE', nullable=False)
    meta: dict = Field(sa_column=Column(JSONB, server_default=text("'{}'::jsonb")), default_factory=dict)
    account_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE')

    exchange: 'Exchange' = Relationship(back_populates='wallets')
    account: 'Account' = Relationship(back_populates='wallets')


    def __str__(self):
        return modstr(self, 'asset')


class Exchange(DTMixin, IntPkMixin, SQLModel, table=True):
    __tablename__ = 'xch_exchange'
    name: str = Field(max_length=199)
    prefix: str = Field(max_length=199)
    display: str = Field(max_length=199)
    website: str = Field(max_length=199)
    description: str = Field(sa_column=Column(TEXT, default='', server_default=''))
    # account_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE')
    meta: dict = Field(sa_column=Column(JSONB, server_default=text("'{}'::jsonb")), default_factory=dict)

    wallets: list['Wallet'] = Relationship(back_populates='exchange')
    orders: list['Order'] = Relationship(back_populates='exchange')
    trades: list['Trade'] = Relationship(back_populates='exchange')


    def __str__(self):
        return modstr(self, 'name')
