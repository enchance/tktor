from typing import TYPE_CHECKING
from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, Relationship, Field, Column as Col, DateTime, TEXT, text, String, SMALLINT, \
    UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from core import modstr, LitActiveAll
from core.models import UpdatedAtMixin, DTMixin, IntPkMixin
from exchange import services


if TYPE_CHECKING:
    from authentication import Account


class Order(SQLModel, table=True):
    __tablename__ = 'xch_order'
    id: str = Field(primary_key=True, unique=True, nullable=False)
    client_orderid: str | None = Field(sa_column=Col(String(199), default=None, server_default=None))
    symbol: str = Field(sa_column=Col(String(20), nullable=False))
    amount: str | None = Field(sa_column=Col(String(199), default=None, server_default=None))
    quote_amount: str | None = Field(sa_column=Col(String(199), default=None, server_default=None))
    executed_amount: str | None = Field(sa_column=Col(String(199), default=None, server_default=None))
    cum_quote_amount: str | None = Field(sa_column=Col(String(199), default=None, server_default=None))
    stop_limit: str | None = Field(sa_column=Col(String(20), default=None, server_default=None))
    stop_price: str | None = Field(sa_column=Col(String(20), default=None, server_default=None))
    status: str | None = Field(sa_column=Col(String(50), default=None, server_default=None))
    time_in_force: str | None = Field(sa_column=Col(String(20), default=None, server_default=None))
    type: str | None = Field(sa_column=Col(String(20), default=None, server_default=None))
    side: str = Field(sa_column=Col(String(20), nullable=False))
    iceberg_amount: str | None = Field(sa_column=Col(String(199), default='0.00000000', server_default='0.00000000'))
    exchange_id: int = Field(primary_key=True, foreign_key='xch_exchange.id', ondelete='CASCADE', nullable=False)
    account_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE', nullable=False)
    updated_at: datetime = Field(sa_column=Col(DateTime(timezone=True), nullable=False))
    created_at: datetime = Field(sa_column=Col(DateTime(timezone=True), nullable=False))  # time

    exchange: 'Exchange' = Relationship(back_populates='orders')
    trades: list['Trade'] = Relationship(back_populates='order')
    account: 'Account' = Relationship(back_populates='orders')


    def __str__(self):
        return modstr(self, 'symbol', 'status')


    # PLACEHOLDER: To follow
    async def get_all(self, orderids: list[str], account: 'Account', *, session: AsyncSession):
        pass


    # PLACEHOLDER: To follow
    async def add_all(self, orderids: list[str], account: 'Account', *, session: AsyncSession):
        pass


class Trade(UpdatedAtMixin, SQLModel, table=True):
    __tablename__ = 'xch_trade'
    id: str = Field(primary_key=True, unique=True, nullable=False)
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
    created_at: datetime = Field(sa_column=Col(DateTime(timezone=True), nullable=False))  # time

    order: 'Order' = Relationship(back_populates='trades')
    exchange: 'Exchange' = Relationship(back_populates='trades')
    account: 'Account' = Relationship(back_populates='trades')


    def __str__(self):
        return modstr(self, 'symbol')


    # PLACEHOLDER: To follow
    async def add_all(self, trades_dict: list[dict], account: 'Account', *, session: AsyncSession):
        ll = []
        for trade in trades_dict:
            pass

        # Verify order_ids


class Wallet(DTMixin, IntPkMixin, SQLModel, table=True):
    __tablename__ = 'xch_wallet'
    asset: str = Field(max_length=20, index=True)
    amount: str = Field(max_length=199)
    exchange_id: int = Field(foreign_key='xch_exchange.id', ondelete='CASCADE', nullable=False)
    meta: dict = Field(sa_column=Col(JSONB, server_default=text("'{}'::jsonb")), default_factory=dict)
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
    base_url: str = Field(max_length=199)
    description: str = Field(sa_column=Col(TEXT, default='', server_default=''))
    logo: str = Field(sa_column=Col(JSONB, server_default=text("'{}'::jsonb")), default_factory=dict)
    rating: int | None = Field(sa_column=Col(SMALLINT, default=None, server_default=None))
    meta: dict = Field(sa_column=Col(JSONB, server_default=text("'{}'::jsonb")), default_factory=dict)
    is_active: bool = Field(default=True)

    wallets: list['Wallet'] = Relationship(back_populates='exchange', cascade_delete=True)
    orders: list['Order'] = Relationship(back_populates='exchange', cascade_delete=True)
    trades: list['Trade'] = Relationship(back_populates='exchange', cascade_delete=True)
    apikeys: list['APIKeys'] = Relationship(back_populates='exchange', cascade_delete=True)


    def __str__(self):
        return modstr(self, 'name')


class APIKeys(DTMixin, IntPkMixin, SQLModel, table=True):
    __tablename__ = 'xch_apikeys'
    __table_args__ = (
        UniqueConstraint('name', 'apikeys', name='unique_keys'),
    )
    name: str = Field(max_length=191)
    apikeys: dict = Field(sa_column=Col(JSONB, server_default=text("'{}'::jsonb")), default_factory=dict)
    is_active: bool = Field(default=True, index=True)
    account_id: int = Field(foreign_key='auth_account.id', ondelete='CASCADE')
    exchange_id: int = Field(foreign_key='xch_exchange.id', ondelete='CASCADE')

    exchange: 'Exchange' = Relationship(back_populates='apikeys')
    account: 'Account' = Relationship(back_populates='apikeys')


    def __str__(self):
        return modstr(self, 'name', data=list(self.apikeys.keys()))


    @staticmethod
    async def get(account: 'Account', ident: str | int | None = None, *, active: LitActiveAll = 'ACTIVE',
                  session: AsyncSession, **kwargs) -> list['APIKeys']:
        return await services.ExchangeSvc.get_apikeys(account, ident, active=active, session=session, **kwargs)
