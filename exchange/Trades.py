from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Relationship

from models import modstr
from models.trade_models import OrderMod, TradeMod, WalletMod, ExchangeMod


if TYPE_CHECKING:
    from authentication import Account


class Order(OrderMod, SQLModel, table=True):
    __tablename__ = 'xch_order'
    exchange: 'Exchange' = Relationship(back_populates='orders')
    trades: list['Trade'] = Relationship(back_populates='order')
    account: 'Account' = Relationship(back_populates='orders')


    def __repr__(self):
        return modstr(self)


class Trade(TradeMod, SQLModel, table=True):
    __tablename__ = 'xch_trade'
    order: 'Order' = Relationship(back_populates='trades')
    exchange: 'Exchange' = Relationship(back_populates='trades')
    account: 'Account' = Relationship(back_populates='trades')


    def __repr__(self):
        return modstr(self, 'symbol')


class Wallet(WalletMod, SQLModel, table=True):
    __tablename__ = 'xch_wallet'
    exchange: 'Exchange' = Relationship(back_populates='wallets')
    account: 'Account' = Relationship(back_populates='wallets')


    def __repr__(self):
        return modstr(self, 'asset')


class Exchange(ExchangeMod, SQLModel, table=True):
    __tablename__ = 'xch_exchange'
    wallets: list['Wallet'] = Relationship(back_populates='exchange')
    orders: list['Order'] = Relationship(back_populates='exchange')
    trades: list['Trade'] = Relationship(back_populates='exchange')
    account: 'Account' = Relationship(back_populates='exchanges')


    def __repr__(self):
        return modstr(self, 'name')
