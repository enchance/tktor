from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Relationship

from models.trade_models import TradeLogMod


if TYPE_CHECKING:
    from auth import Account


class TradeLog(TradeLogMod, SQLModel, table=True):
    __tablename__ = 'trade_log'
    account: 'Account' = Relationship(back_populates='trades')
