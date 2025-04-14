import pandas as pd
from typing import Union, TYPE_CHECKING
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core import NotFoundException
from .Trades import Exchange, APIKeys


if TYPE_CHECKING:
    from authentication import Account


class ExchangeSvc:
    @staticmethod
    async def get_exchange(name: str, *, session: AsyncSession) -> Union[Exchange, None]:
        try:
            stmt = select(Exchange).where(Exchange.name == name)  # noqa
            exec_ = await session.exec(stmt)  # noqa
            return exec_.one_or_none()
        except Exception as e:
            raise


    @staticmethod
    async def get_apikeys(account: 'Account', ident: str | int | None = None, *, only_active: bool | None = True,
                          session: AsyncSession, **kwargs) -> Union['APIKeys', list['APIKeys'],
    None]:
        """
        Get the account's API keys for an exchange.
        For more specific
        :param account:         Account
        :param ident:           APIkey name or id
        :param only_active:     Active apikeys
        :param session:         AsyncSession
        :param kwargs:          limit, offset
        :return:                APIKeys, list, None
        """
        limit = kwargs.pop('limit', account.options.items_per_page)
        offset = kwargs.pop('offset', 0)

        try:
            stmt = select(APIKeys).where(APIKeys.account == account)
            if only_active is None:
                # Do nothing
                pass
            elif only_active:
                stmt = stmt.where(APIKeys.is_active)
            else:
                stmt = stmt.where(~APIKeys.is_active)

            if ident:
                if isinstance(ident, int):
                    return await session.get(APIKeys, ident)
                else:
                    stmt = stmt.where(APIKeys.name == ident)

            stmt = stmt.offset(offset).limit(limit)
            exec_ = await session.exec(stmt)  # noqa
            return exec_.all()

        except Exception as e:
            raise


# PLACEHOLDER: To follow
@staticmethod
async def get_orders(account: 'Account', *, apikey: str, start_time: int, session: AsyncSession):
    def _clean_orders(df_: pd.DataFrame):
        df_['time'] = pd.to_datetime(df_['time'], unit='ms')
        df_['updateTime'] = pd.to_datetime(df_['updateTime'], unit='ms')
        df_ = df_.drop(columns=['workingTime', 'selfTradePreventionMode', 'isWorking', 'orderListId'])
        df_ = df_.rename(columns={
            'orderId': 'exchange_orderid',
            'clientOrderId': 'client_orderid',
            'price': 'stop_limit',
            'origQty': 'amount',
            'executedQty': 'executed_amount',
            'cummulativeQuoteQty': 'cum_quote_amount',
            'timeInForce': 'time_in_force',
            'stopPrice': 'stop_price',
            'icebergQty': 'iceberg_amount',
            'origQuoteOrderQty': 'quote_amount',
            'time': 'created_at',
            'updateTime': 'updated_at',
        })
        return df_


    try:
        pass
    except Exception as e:
        raise


# PLACEHOLDER: To follow
@staticmethod
async def get_trades():
    pass


# PLACEHOLDER: To follow
@staticmethod
async def update_pointer():
    pass
